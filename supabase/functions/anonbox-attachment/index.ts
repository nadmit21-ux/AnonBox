import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") || "";
const legacyServiceRole = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
const secretMapRaw = Deno.env.get("SUPABASE_SECRET_KEYS") || "";
let mappedServiceRole = "";
try {
  mappedServiceRole = secretMapRaw ? String(JSON.parse(secretMapRaw)?.default || "") : "";
} catch {
  mappedServiceRole = "";
}
const ADMIN_KEY = legacyServiceRole || mappedServiceRole;
if (!SUPABASE_URL || !ADMIN_KEY) throw new Error("Supabase admin environment unavailable");

const admin = createClient(SUPABASE_URL, ADMIN_KEY, { auth: { persistSession: false } });
const BUCKET = "anonbox-attachments";
const MAX_BYTES = 10 * 1024 * 1024;
const ALLOWED = new Set([
  "image/jpeg", "image/png", "image/webp", "image/gif",
  "application/pdf", "text/plain", "application/zip",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  "audio/mpeg", "audio/mp4", "video/mp4",
]);

function cors(req: Request) {
  const origin = req.headers.get("origin") || "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Headers": "authorization, apikey, content-type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Vary": "Origin",
  };
}

function json(req: Request, data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...cors(req), "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" },
  });
}

async function requestUser(req: Request): Promise<string | null> {
  const auth = req.headers.get("authorization") || "";
  const m = auth.match(/^Bearer\s+(.+)$/i);
  if (!m) return null;
  const token = m[1].trim();
  if (!token) return null;
  const { data, error } = await admin.auth.getUser(token);
  if (error || !data.user) return null;
  return data.user.id;
}

async function sha256Hex(value: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return Array.from(new Uint8Array(digest)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

function safeFileName(name: string) {
  const cleaned = name.normalize("NFKC").replace(/[\\/\0\r\n]+/g, "-").replace(/\s+/g, " ").trim();
  return (cleaned || "fichier").slice(0, 180);
}

function storageFileName(name: string) {
  return safeFileName(name).replace(/[^a-zA-Z0-9._-]+/g, "-").replace(/-+/g, "-").slice(0, 100) || "file";
}

type Participant = {
  actor: "owner" | "visitor";
  mode: "owner" | "profile" | "anonymous";
  boxId: string;
  ownerId: string;
  userId: string | null;
  fingerprint: string;
  pseudonym: string | null;
  avatarPath: string | null;
};

async function participant(conversationId: string, deviceId: string, userId: string | null): Promise<Participant | null> {
  const { data: rows, error } = await admin
    .from("anonbox_messages_v2")
    .select("id,box_id,direction,sender_mode,sender_user_id,sender_fingerprint,sender_pseudonym_snapshot,sender_avatar_path_snapshot")
    .eq("conversation_id", conversationId)
    .is("deleted_at", null)
    .order("created_at", { ascending: true })
    .limit(500);
  if (error || !rows?.length) return null;

  const boxId = String(rows[0].box_id);
  const { data: box, error: boxError } = await admin.from("anonbox_boxes").select("owner_id").eq("id", boxId).maybeSingle();
  if (boxError || !box) return null;
  const ownerId = String(box.owner_id);

  if (userId && userId === ownerId) {
    const { data: p } = await admin.from("anonbox_profiles").select("pseudonym,avatar_path").eq("user_id", userId).maybeSingle();
    const firstVisitor = rows.find((r: any) => r.direction === "visitor");
    return { actor: "owner", mode: "owner", boxId, ownerId, userId,
      fingerprint: String(firstVisitor?.sender_fingerprint || await sha256Hex(`owner:${boxId}:${conversationId}`)),
      pseudonym: p?.pseudonym || "Propriétaire", avatarPath: p?.avatar_path || null };
  }

  if (userId) {
    const profileRow = rows.find((r: any) => r.direction === "visitor" && r.sender_mode === "profile" && String(r.sender_user_id || "") === userId);
    if (profileRow) {
      const { data: p } = await admin.from("anonbox_profiles").select("pseudonym,avatar_path").eq("user_id", userId).maybeSingle();
      return { actor: "visitor", mode: "profile", boxId, ownerId, userId,
        fingerprint: String(profileRow.sender_fingerprint), pseudonym: p?.pseudonym || "Profil", avatarPath: p?.avatar_path || null };
    }
  }

  if (deviceId.length >= 8 && deviceId.length <= 200) {
    const fp = await sha256Hex(`${boxId}:${deviceId}`);
    const anonRow = [...rows].reverse().find((r: any) => r.direction === "visitor" && r.sender_mode === "anonymous" && r.sender_fingerprint === fp);
    if (anonRow) return {
      actor: "visitor", mode: "anonymous", boxId, ownerId, userId: null, fingerprint: fp,
      pseudonym: anonRow.sender_pseudonym_snapshot || null,
      avatarPath: anonRow.sender_avatar_path_snapshot || null,
    };
  }
  return null;
}

async function rateLimited(p: Participant, conversationId: string) {
  const since = new Date(Date.now() - 10 * 60 * 1000).toISOString();
  let q = admin.from("anonbox_messages_v2").select("id", { count: "exact", head: true }).eq("conversation_id", conversationId).gte("created_at", since);
  if (p.actor === "owner") q = q.eq("direction", "owner");
  else q = q.eq("direction", "visitor").eq("sender_fingerprint", p.fingerprint);
  const { count, error } = await q;
  if (error) return true;
  return (count || 0) >= (p.actor === "owner" ? 30 : 5);
}

async function upload(req: Request) {
  let form: FormData;
  try { form = await req.formData(); } catch { return json(req, { error: "Formulaire invalide." }, 400); }
  const conversationId = String(form.get("conversation_id") || "").trim();
  const deviceId = String(form.get("device_id") || "");
  const caption = String(form.get("caption") || "").trim();
  const replyRaw = String(form.get("reply_to_id") || "").trim();
  const anonPseudonym = String(form.get("anon_pseudonym") || "").trim();
  const anonAvatarPath = String(form.get("anon_avatar_path") || "").trim();
  const file = form.get("file");
  if (!/^[0-9a-f-]{36}$/i.test(conversationId)) return json(req, { error: "Conversation invalide." }, 400);
  if (!(file instanceof File)) return json(req, { error: "Fichier manquant." }, 400);
  if (file.size < 1 || file.size > MAX_BYTES) return json(req, { error: "Fichier trop volumineux (10 Mo maximum)." }, 400);
  const mime = String(file.type || "").toLowerCase();
  if (!ALLOWED.has(mime)) return json(req, { error: "Type de fichier non pris en charge." }, 400);
  if (caption.length > 1500) return json(req, { error: "Légende trop longue." }, 400);

  const userId = await requestUser(req);
  const p = await participant(conversationId, deviceId, userId);
  if (!p) return json(req, { error: "Conversation introuvable." }, 403);

  if (p.mode === "anonymous") {
    if (anonPseudonym) {
      if (anonPseudonym.length < 2 || anonPseudonym.length > 32) return json(req, { error: "Nom de profil anonyme invalide." }, 400);
      p.pseudonym = anonPseudonym;
    }
    if (anonAvatarPath) {
      const deviceHash = await sha256Hex(deviceId);
      if (!anonAvatarPath.startsWith(`anonymous/${deviceHash}/`)) return json(req, { error: "Avatar anonyme invalide." }, 400);
      p.avatarPath = anonAvatarPath;
    }
  }

  if (await rateLimited(p, conversationId)) return json(req, { error: "Trop de messages envoyés. Réessaie un peu plus tard." }, 429);

  let replyTo: number | null = null;
  if (replyRaw) {
    if (!/^\d{1,20}$/.test(replyRaw)) return json(req, { error: "Réponse citée invalide." }, 400);
    const { data: quoted } = await admin.from("anonbox_messages_v2").select("id,conversation_id").eq("id", replyRaw).is("deleted_at", null).maybeSingle();
    if (!quoted || String(quoted.conversation_id) !== conversationId) return json(req, { error: "Le message cité est invalide." }, 400);
    replyTo = Number(replyRaw);
  }

  const originalName = safeFileName(file.name || "fichier");
  const id = crypto.randomUUID();
  const path = `${p.boxId}/${conversationId}/${id}-${storageFileName(originalName)}`;
  const { error: storageError } = await admin.storage.from(BUCKET).upload(path, file, { contentType: mime, upsert: false, cacheControl: "3600" });
  if (storageError) return json(req, { error: "Échec de l’envoi du fichier." }, 500);

  const body = caption || `📎 ${originalName}`;
  const row = {
    box_id: p.boxId, conversation_id: conversationId, direction: p.actor === "owner" ? "owner" : "visitor", body,
    sender_mode: p.mode, sender_user_id: p.userId, sender_pseudonym_snapshot: p.pseudonym,
    sender_avatar_path_snapshot: p.avatarPath, sender_fingerprint: p.fingerprint, read_at: null, reply_to_id: replyTo,
    attachment_id: id, attachment_name: originalName, attachment_mime: mime, attachment_size: file.size, attachment_path: path,
  };
  const { data: inserted, error: insertError } = await admin.from("anonbox_messages_v2").insert(row).select("id").single();
  if (insertError || !inserted) {
    await admin.storage.from(BUCKET).remove([path]);
    return json(req, { error: "Échec de création du message." }, 500);
  }
  return json(req, { ok: true, message_id: inserted.id, attachment_id: id }, 201);
}

async function sign(req: Request, body: any) {
  const messageId = String(body?.message_id || "").trim();
  const deviceId = String(body?.device_id || "");
  if (!/^\d{1,20}$/.test(messageId)) return json(req, { error: "Message invalide." }, 400);
  const { data: msg, error } = await admin.from("anonbox_messages_v2")
    .select("id,conversation_id,attachment_path,attachment_name,attachment_mime")
    .eq("id", messageId).is("deleted_at", null).maybeSingle();
  if (error || !msg || !msg.attachment_path) return json(req, { error: "Pièce jointe introuvable." }, 404);
  const userId = await requestUser(req);
  const p = await participant(String(msg.conversation_id), deviceId, userId);
  if (!p) return json(req, { error: "Accès refusé." }, 403);
  const { data, error: signedError } = await admin.storage.from(BUCKET).createSignedUrl(String(msg.attachment_path), 300, { download: false });
  if (signedError || !data?.signedUrl) return json(req, { error: "Lien temporaire indisponible." }, 500);
  return json(req, { ok: true, signed_url: data.signedUrl, file_name: msg.attachment_name, mime_type: msg.attachment_mime, expires_in: 300 });
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(req) });
  if (req.method !== "POST") return json(req, { error: "Method not allowed" }, 405);
  const contentType = req.headers.get("content-type") || "";
  if (contentType.includes("multipart/form-data")) return await upload(req);
  let body: any;
  try { body = await req.json(); } catch { return json(req, { error: "JSON invalide." }, 400); }
  if (body?.action === "sign") return await sign(req, body);
  return json(req, { error: "Action inconnue." }, 400);
});
