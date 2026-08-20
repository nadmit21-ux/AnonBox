import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") || "";
const legacyServiceRole = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
const secretMapRaw = Deno.env.get("SUPABASE_SECRET_KEYS") || "";
let mappedServiceRole = "";
try { mappedServiceRole = secretMapRaw ? String(JSON.parse(secretMapRaw)?.default || "") : ""; } catch { mappedServiceRole = ""; }
const ADMIN_KEY = legacyServiceRole || mappedServiceRole;
if (!SUPABASE_URL || !ADMIN_KEY) throw new Error("Supabase admin environment unavailable");

const admin = createClient(SUPABASE_URL, ADMIN_KEY, { auth: { persistSession: false } });
const BUCKET = "anonbox-avatars";
const MAX_BYTES = 3 * 1024 * 1024;
const ALLOWED = new Set(["image/jpeg", "image/png", "image/webp"]);

function cors(req: Request) {
  const origin = req.headers.get("origin") || "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Headers": "content-type, apikey, authorization",
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

async function sha256Hex(value: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return Array.from(new Uint8Array(digest)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

function extensionFor(mime: string) {
  if (mime === "image/png") return "png";
  if (mime === "image/webp") return "webp";
  return "jpg";
}

function validMagic(bytes: Uint8Array, mime: string): boolean {
  if (mime === "image/jpeg") return bytes.length >= 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff;
  if (mime === "image/png") return bytes.length >= 8 && bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4e && bytes[3] === 0x47 && bytes[4] === 0x0d && bytes[5] === 0x0a && bytes[6] === 0x1a && bytes[7] === 0x0a;
  if (mime === "image/webp") return bytes.length >= 12 && String.fromCharCode(...bytes.slice(0, 4)) === "RIFF" && String.fromCharCode(...bytes.slice(8, 12)) === "WEBP";
  return false;
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(req) });
  if (req.method !== "POST") return json(req, { error: "Method not allowed" }, 405);

  let form: FormData;
  try { form = await req.formData(); } catch { return json(req, { error: "Formulaire invalide." }, 400); }

  const deviceId = String(form.get("device_id") || "");
  const file = form.get("file");
  if (deviceId.length < 8 || deviceId.length > 200) return json(req, { error: "Navigateur non reconnu." }, 400);
  if (!(file instanceof File)) return json(req, { error: "Image manquante." }, 400);
  if (file.size < 1 || file.size > MAX_BYTES) return json(req, { error: "Image trop lourde : 3 Mo maximum." }, 400);

  const mime = String(file.type || "").toLowerCase();
  if (!ALLOWED.has(mime)) return json(req, { error: "Format accepté : JPG, PNG ou WebP." }, 400);

  const bytes = new Uint8Array(await file.arrayBuffer());
  if (!validMagic(bytes, mime)) return json(req, { error: "Le fichier ne semble pas être une image valide." }, 400);

  const hash = await sha256Hex(deviceId);
  const folder = `anonymous/${hash}`;
  const ext = extensionFor(mime);
  const path = `${folder}/avatar-${Date.now()}.${ext}`;

  try {
    const { data: oldFiles } = await admin.storage.from(BUCKET).list(folder, { limit: 50 });
    const oldPaths = (oldFiles || []).filter((f: any) => f?.name).map((f: any) => `${folder}/${f.name}`);
    if (oldPaths.length) await admin.storage.from(BUCKET).remove(oldPaths);
  } catch { /* best effort cleanup */ }

  const blob = new Blob([bytes], { type: mime });
  const { error } = await admin.storage.from(BUCKET).upload(path, blob, { contentType: mime, upsert: false, cacheControl: "3600" });
  if (error) return json(req, { error: "Impossible d’enregistrer l’avatar." }, 500);

  const { data } = admin.storage.from(BUCKET).getPublicUrl(path);
  return json(req, { ok: true, path, public_url: data.publicUrl }, 201);
});
