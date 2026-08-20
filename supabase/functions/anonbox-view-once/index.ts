import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL") || "";
const legacyServiceRole = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || "";
const secretMapRaw = Deno.env.get("SUPABASE_SECRET_KEYS") || "";
let mappedServiceRole = "";
try { mappedServiceRole = secretMapRaw ? String(JSON.parse(secretMapRaw)?.default || "") : ""; } catch { mappedServiceRole = ""; }
const ADMIN_KEY = legacyServiceRole || mappedServiceRole;
if (!SUPABASE_URL || !ADMIN_KEY) throw new Error("Supabase admin environment unavailable");
const admin = createClient(SUPABASE_URL, ADMIN_KEY, { auth: { persistSession:false } });
const BUCKET = "anonbox-attachments";

function cors(req: Request) {
  const origin = req.headers.get("origin") || "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Headers": "authorization, apikey, content-type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Vary":"Origin",
  };
}
function json(req: Request, data: unknown, status=200) {
  return new Response(JSON.stringify(data),{status,headers:{...cors(req),"Content-Type":"application/json; charset=utf-8","Cache-Control":"no-store, no-cache, must-revalidate"}});
}
async function requestUser(req: Request): Promise<string | null> {
  const auth = req.headers.get("authorization") || "";
  const m = auth.match(/^Bearer\s+(.+)$/i);
  if (!m) return null;
  const { data, error } = await admin.auth.getUser(m[1].trim());
  return error || !data.user ? null : data.user.id;
}
async function sha256Hex(value: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256",new TextEncoder().encode(value));
  return Array.from(new Uint8Array(digest)).map(b=>b.toString(16).padStart(2,"0")).join("");
}
async function recipientAllowed(msg: any, deviceId: string, userId: string | null): Promise<{ok:boolean,actor:string}> {
  const { data: box } = await admin.from("anonbox_boxes").select("owner_id").eq("id",msg.box_id).maybeSingle();
  if (!box) return {ok:false,actor:""};
  const ownerId = String(box.owner_id);
  if (msg.direction === "visitor") {
    return userId && userId === ownerId ? {ok:true,actor:`owner:${ownerId}`} : {ok:false,actor:""};
  }
  if (msg.direction !== "owner") return {ok:false,actor:""};
  if (userId) {
    const { data: profileRows } = await admin.from("anonbox_messages_v2").select("id").eq("conversation_id",msg.conversation_id).eq("direction","visitor").eq("sender_mode","profile").eq("sender_user_id",userId).limit(1);
    if (profileRows?.length) return {ok:true,actor:`profile:${userId}`};
  }
  if (deviceId.length >= 8 && deviceId.length <= 200) {
    const fp = await sha256Hex(`${msg.box_id}:${deviceId}`);
    const { data: anonRows } = await admin.from("anonbox_messages_v2").select("id").eq("conversation_id",msg.conversation_id).eq("direction","visitor").eq("sender_mode","anonymous").eq("sender_fingerprint",fp).limit(1);
    if (anonRows?.length) return {ok:true,actor:`anon:${fp}`};
  }
  return {ok:false,actor:""};
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response(null,{status:204,headers:cors(req)});
  if (req.method !== "POST") return json(req,{error:"Method not allowed"},405);
  let body: any;
  try { body = await req.json(); } catch { return json(req,{error:"JSON invalide."},400); }
  const messageId = String(body?.message_id || "").trim();
  const deviceId = String(body?.device_id || "");
  if (!/^\d{1,20}$/.test(messageId)) return json(req,{error:"Message invalide."},400);
  const { data: msg } = await admin.from("anonbox_messages_v2")
    .select("id,box_id,conversation_id,direction,view_once,view_once_opened_at,deleted_at")
    .eq("id",messageId).maybeSingle();
  if (!msg || msg.deleted_at || !msg.view_once) return json(req,{error:"Message à vue unique introuvable."},404);
  if (msg.view_once_opened_at) return json(req,{ok:false,opened:true,error:"Ce message a déjà été ouvert."},410);
  const userId = await requestUser(req);
  const allowed = await recipientAllowed(msg,deviceId,userId);
  if (!allowed.ok) return json(req,{error:"Seul le destinataire peut ouvrir ce message."},403);

  const { data: payload } = await admin.from("anonbox_view_once_payloads").select("message_id,body,attachment_id,attachment_name,attachment_mime,attachment_size,attachment_path,voice_duration_ms,opened_at").eq("message_id",messageId).maybeSingle();
  if (!payload) return json(req,{error:"Contenu indisponible."},404);
  if (payload.opened_at) return json(req,{ok:false,opened:true,error:"Ce message a déjà été ouvert."},410);

  const now = new Date().toISOString();
  const { data: claimed, error: claimError } = await admin.from("anonbox_view_once_payloads")
    .update({opened_at:now,opened_by:allowed.actor}).eq("message_id",messageId).is("opened_at",null).select("message_id").maybeSingle();
  if (claimError || !claimed) return json(req,{ok:false,opened:true,error:"Ce message a déjà été ouvert."},410);

  await admin.from("anonbox_messages_v2").update({view_once_opened_at:now,read_at:now}).eq("id",messageId);

  let signedUrl: string | null = null;
  if (payload.attachment_path) {
    const { data: signed } = await admin.storage.from(BUCKET).createSignedUrl(String(payload.attachment_path),300,{download:false});
    signedUrl = signed?.signedUrl || null;
  }

  return json(req,{
    ok:true,
    opened_at:now,
    body:payload.body || "",
    attachment:payload.attachment_path ? {
      id:payload.attachment_id,
      name:payload.attachment_name,
      mime:payload.attachment_mime,
      size:payload.attachment_size,
      signed_url:signedUrl,
      expires_in:300,
      voice_duration_ms:payload.voice_duration_ms
    } : null
  });
});
