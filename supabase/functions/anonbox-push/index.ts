import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

type ServiceAccount = {
  project_id: string;
  client_email: string;
  private_key: string;
};

type PushConfig = {
  hook_secret?: string | null;
  firebase_service_account?: string | null;
};

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const secretMapRaw = Deno.env.get("SUPABASE_SECRET_KEYS");
const legacyServiceRole = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
const adminKey = secretMapRaw ? JSON.parse(secretMapRaw)["default"] : legacyServiceRole;
if (!SUPABASE_URL || !adminKey) throw new Error("Supabase admin environment is unavailable");

const admin = createClient(SUPABASE_URL, adminKey, {
  auth: { persistSession: false },
});

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}

function safeEqual(a: string, b: string): boolean {
  if (!a || !b || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

function base64Url(input: Uint8Array | string): string {
  const bytes = typeof input === "string" ? new TextEncoder().encode(input) : input;
  let binary = "";
  for (const b of bytes) binary += String.fromCharCode(b);
  return btoa(binary)
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/g, "");
}

function pemToDer(pem: string): Uint8Array {
  const clean = pem
    .replace(/-----BEGIN PRIVATE KEY-----/g, "")
    .replace(/-----END PRIVATE KEY-----/g, "")
    .replace(/\s+/g, "");
  const binary = atob(clean);
  const out = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) out[i] = binary.charCodeAt(i);
  return out;
}

async function firebaseAccessToken(sa: ServiceAccount): Promise<string> {
  const now = Math.floor(Date.now() / 1000);
  const header = base64Url(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const payload = base64Url(
    JSON.stringify({
      iss: sa.client_email,
      scope: "https://www.googleapis.com/auth/firebase.messaging",
      aud: "https://oauth2.googleapis.com/token",
      iat: now,
      exp: now + 3600,
    }),
  );
  const unsigned = `${header}.${payload}`;
  const key = await crypto.subtle.importKey(
    "pkcs8",
    pemToDer(sa.private_key),
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = new Uint8Array(
    await crypto.subtle.sign(
      "RSASSA-PKCS1-v1_5",
      key,
      new TextEncoder().encode(unsigned),
    ),
  );
  const assertion = `${unsigned}.${base64Url(signature)}`;
  const tokenResponse = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
      assertion,
    }),
  });
  const tokenData = await tokenResponse.json();
  if (!tokenResponse.ok || !tokenData.access_token) {
    throw new Error(`OAuth Firebase refusé (${tokenResponse.status})`);
  }
  return tokenData.access_token;
}

async function loadPushConfig(): Promise<PushConfig> {
  const { data, error } = await admin.rpc("anonbox_internal_push_config");
  if (error) throw new Error("Push configuration unavailable");
  return (data || {}) as PushConfig;
}

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") return json({ error: "Method not allowed" }, 405);

  let config: PushConfig;
  try {
    config = await loadPushConfig();
  } catch {
    return json({ error: "Push configuration unavailable" }, 503);
  }

  const suppliedHook = req.headers.get("x-anonbox-hook-secret") || "";
  const expectedHook = String(config.hook_secret || "");
  if (!safeEqual(suppliedHook, expectedHook)) {
    return json({ error: "Unauthorized" }, 401);
  }

  let body: any;
  try {
    body = await req.json();
  } catch {
    return json({ error: "Invalid JSON" }, 400);
  }

  const messageId = String(body?.message_id || "").trim();
  if (!/^\d{1,20}$/.test(messageId)) {
    return json({ error: "Invalid message id" }, 400);
  }

  const rawSa = String(config.firebase_service_account || "");
  if (!rawSa) {
    return json({ error: "Firebase server credentials not configured" }, 503);
  }

  let sa: ServiceAccount;
  try {
    sa = JSON.parse(rawSa);
    if (!sa.project_id || !sa.client_email || !sa.private_key) {
      throw new Error("missing fields");
    }
  } catch {
    return json({ error: "Invalid Firebase server credentials" }, 503);
  }

  const { data: msg, error: msgError } = await admin
    .from("anonbox_messages_v2")
    .select("id,box_id,conversation_id,direction,sender_mode,created_at")
    .eq("id", messageId)
    .maybeSingle();

  if (msgError || !msg) return json({ error: "Message not found" }, 404);
  if (msg.direction !== "visitor") {
    return json({ ok: true, skipped: "not_visitor" });
  }
  if (Date.now() - new Date(msg.created_at).getTime() > 10 * 60 * 1000) {
    return json({ ok: true, skipped: "too_old" });
  }

  const { data: box, error: boxError } = await admin
    .from("anonbox_boxes")
    .select("owner_id")
    .eq("id", msg.box_id)
    .single();

  if (boxError || !box) return json({ error: "Owner not found" }, 404);

  const { data: devices, error: deviceError } = await admin
    .from("anonbox_push_tokens")
    .select("id,token")
    .eq("user_id", box.owner_id)
    .eq("enabled", true)
    .eq("platform", "android");

  if (deviceError) return json({ error: "Push devices unavailable" }, 500);
  if (!devices?.length) return json({ ok: true, skipped: "no_devices" });

  const { error: claimError } = await admin
    .from("anonbox_push_deliveries")
    .insert({ message_id: messageId });

  if (claimError) {
    if (claimError.code === "23505") {
      return json({ ok: true, skipped: "already_processed" });
    }
    return json({ error: "Unable to claim notification" }, 500);
  }

  try {
    const accessToken = await firebaseAccessToken(sa);
    let sent = 0;
    const invalidTokenIds: string[] = [];
    const failures: string[] = [];

    for (const device of devices) {
      const fcm = await fetch(
        `https://fcm.googleapis.com/v1/projects/${encodeURIComponent(sa.project_id)}/messages:send`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: {
              token: device.token,
              notification: {
                title: "Nouveau message AnonBox",
                body: "Tu as reçu un nouveau message.",
              },
              data: {
                conversation_id: String(msg.conversation_id),
                message_id: String(msg.id),
              },
              android: {
                priority: "high",
                notification: {
                  channel_id: "anonbox_messages",
                  sound: "default",
                },
              },
            },
          }),
        },
      );

      if (fcm.ok) {
        sent++;
        continue;
      }

      const err = await fcm.text();
      failures.push(`${fcm.status}:${err.slice(0, 300)}`);
      if (
        fcm.status === 404 ||
        err.includes("UNREGISTERED") ||
        err.includes("registration-token-not-registered")
      ) {
        invalidTokenIds.push(String(device.id));
      }
    }

    if (invalidTokenIds.length) {
      await admin
        .from("anonbox_push_tokens")
        .update({ enabled: false })
        .in("id", invalidTokenIds);
    }

    await admin
      .from("anonbox_push_deliveries")
      .update({
        sent_at: sent > 0 ? new Date().toISOString() : null,
        delivered_count: sent,
        last_error: failures.length ? failures.join(" | ").slice(0, 2000) : null,
      })
      .eq("message_id", messageId);

    if (sent === 0 && failures.length) {
      await admin
        .from("anonbox_push_deliveries")
        .delete()
        .eq("message_id", messageId);
      return json({ error: "FCM delivery failed", failures: failures.length }, 502);
    }

    return json({ ok: true, sent, disabled_tokens: invalidTokenIds.length });
  } catch (e) {
    await admin
      .from("anonbox_push_deliveries")
      .delete()
      .eq("message_id", messageId);
    return json({ error: e instanceof Error ? e.message : "Push failed" }, 502);
  }
});
