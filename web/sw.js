const CACHE='anonbox-v22';
const SUPABASE_URL='https://ugyrgvbfwvmuhsjmjtue.supabase.co';
const SUPABASE_KEY='sb_publishable_qHIobQFTgOOrzBttJazZQA_e5-MvmLK';
const LEGACY_API=SUPABASE_URL+'/functions/v1/anonbox-api';

const CHAT_HOTFIX=`
<style id="anonbox-v83-hotfix">
html{scroll-behavior:auto!important}
.chatNotice{display:none!important}
.chatScreenShell{padding-bottom:calc(var(--composer) + 14px)!important}
.chatComposer{gap:4px!important;padding:6px 7px calc(6px + env(safe-area-inset-bottom))!important;align-items:center!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important;box-shadow:none!important}
#chatAttachmentBtn,#chatVoiceBtn,#chatViewOnceBtn{width:32px!important;height:32px!important;min-width:32px!important;min-height:32px!important;flex:0 0 32px!important;padding:0!important;border-radius:50%!important;font-size:15px!important;line-height:1!important;display:grid!important;place-items:center!important;background:rgba(72,91,100,.14)!important;border:1px solid rgba(70,90,100,.22)!important;color:var(--text)!important;box-shadow:none!important;transition:none!important}
#chatViewOnceBtn.active{background:#6557d9!important;border-color:#7669e6!important;color:#fff!important}
#chatSendBtn{width:38px!important;height:38px!important;min-width:38px!important;min-height:38px!important;flex:0 0 38px!important;font-size:16px!important;box-shadow:none!important;transition:none!important}
#chatInput{flex:1 1 auto!important;min-width:110px!important;min-height:38px!important;height:38px;padding:8px 11px!important;border-radius:19px!important;font-size:14px!important;box-shadow:none!important}
.chatScreenHeader,.messengerTop,.nav,.actionSheet{backdrop-filter:none!important;-webkit-backdrop-filter:none!important}
.chatScreenHeader,.chatComposer,.nav,.actionSheet,.messengerList,.searchBox,.card,.bubble,.chatScrollToBottom{box-shadow:none!important}
.messageBubble,.chatRow,.nav button,.iconButton,.headerAction,.attachButton,.sendCircle,.filterChip,.reactionPill{transition:none!important;will-change:auto!important}
.messageBubble{contain:layout paint}
.chatHeaderName{color:var(--text)!important;opacity:1!important}.chatHeaderSub{color:var(--muted)!important;opacity:1!important}.bubbleText{color:inherit!important;opacity:1!important}.bubbleMeta{opacity:.9!important}
html[data-anon-theme="night"]{--text:#f4f9f9!important;--muted:#c1ced1!important;--line:#3d5862!important}
html[data-anon-theme="night"] .chatHeaderName{color:#fff!important}html[data-anon-theme="night"] .chatHeaderSub{color:#cbd7d9!important}
html[data-anon-theme="night"] .bubble.left{background:#2b414a!important;border-color:#3d5963!important;color:#fff!important}html[data-anon-theme="night"] .bubble.right{background:linear-gradient(135deg,#35675f,#3d7166)!important;border-color:#54867a!important;color:#fff!important}html[data-anon-theme="night"] .bubbleMeta{color:#d0dadd!important}
html[data-anon-theme="night"] .chatComposer{background:#1b2e36!important;border-top-color:#35505a!important}html[data-anon-theme="night"] #chatInput{background:#263d46!important;border-color:#45636d!important;color:#fff!important}html[data-anon-theme="night"] #chatInput::placeholder{color:#b4c2c5!important;opacity:1!important}
html[data-anon-theme="night"] #chatAttachmentBtn,html[data-anon-theme="night"] #chatVoiceBtn,html[data-anon-theme="night"] #chatViewOnceBtn{background:#263d46!important;border-color:#405d67!important;color:#f2f8f8!important}html[data-anon-theme="night"] #chatViewOnceBtn.active{background:#6557d9!important;border-color:#8174ec!important;color:#fff!important}html[data-anon-theme="night"] #chatSendBtn{background:#6557d9!important;color:#fff!important;box-shadow:none!important}
@media(max-width:380px){.chatComposer{gap:3px!important;padding-left:5px!important;padding-right:5px!important}#chatAttachmentBtn,#chatVoiceBtn,#chatViewOnceBtn{width:30px!important;height:30px!important;min-width:30px!important;min-height:30px!important;flex-basis:30px!important;font-size:14px!important}#chatSendBtn{width:36px!important;height:36px!important;min-width:36px!important;min-height:36px!important;flex-basis:36px!important}#chatInput{min-width:92px!important;padding-left:9px!important;padding-right:9px!important}}
</style>
<meta name="anonbox-ui-build" content="8.3">
`;

self.addEventListener('install',event=>{
  self.skipWaiting();
  event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(['./'])));
});

self.addEventListener('activate',event=>{
  event.waitUntil((async()=>{
    const keys=await caches.keys();
    await Promise.all(keys.filter(k=>k!==CACHE&&k.startsWith('anonbox-')).map(k=>caches.delete(k)));
    await self.clients.claim();
    const clients=await self.clients.matchAll({type:'window',includeUncontrolled:true});
    for(const client of clients){
      try{
        const u=new URL(client.url);
        if(u.searchParams.get('_abv')!=='22'){
          u.searchParams.set('_abv','22');
          await client.navigate(u.toString());
        }
      }catch(e){}
    }
  })());
});

function jsonResponse(data,status=200){
  return new Response(JSON.stringify(data),{
    status,
    headers:{
      'Content-Type':'application/json; charset=utf-8',
      'Cache-Control':'no-store',
      'Access-Control-Allow-Origin':'*'
    }
  });
}

async function rpc(name,args,accessToken){
  const headers={
    'Content-Type':'application/json',
    'Accept':'application/json',
    'apikey':SUPABASE_KEY
  };
  if(accessToken) headers['Authorization']='Bearer '+accessToken;
  const res=await fetch(SUPABASE_URL+'/rest/v1/rpc/'+name,{
    method:'POST',
    headers,
    body:JSON.stringify(args)
  });
  let data=null;
  try{data=await res.json()}catch(e){}
  if(!res.ok){
    const message=(data&&(data.message||data.error||data.hint))||'Une erreur est survenue.';
    throw new Error(message);
  }
  return data;
}

async function handleLegacyApi(request){
  let payload={};
  try{payload=await request.clone().json()}catch(e){return jsonResponse({error:'Requête invalide.'},400)}

  if(payload.action==='public-box'){
    try{
      const data=await rpc('anonbox_get_public_box',{p_slug:String(payload.slug||'')},null);
      if(!data) return jsonResponse({error:'Boîte introuvable.'},404);
      return jsonResponse(data,200);
    }catch(e){
      return jsonResponse({error:e.message||'Impossible de charger la boîte.'},500);
    }
  }

  if(payload.action==='submit'){
    try{
      const data=await rpc('anonbox_submit_message',{
        p_slug:String(payload.slug||''),
        p_body:String(payload.body||''),
        p_mode:payload.mode==='profile'?'profile':'anonymous',
        p_device_id:String(payload.deviceId||'')
      },payload.accessToken||null);
      if(!data||data.ok===false) return jsonResponse({error:(data&&data.error)||'Impossible d’envoyer le message.'},400);
      return jsonResponse(data,201);
    }catch(e){
      return jsonResponse({error:e.message||'Impossible d’envoyer le message.'},500);
    }
  }

  return jsonResponse({error:'Action inconnue.'},400);
}

async function injectUiHotfix(response){
  if(!response) return response;
  const type=response.headers.get('content-type')||'';
  if(!type.includes('text/html')) return response;
  try{
    let html=await response.text();
    html=html.replace("function scheduleRealtimeReload(){if(realtimeTimer)clearTimeout(realtimeTimer);realtimeTimer=setTimeout(function(){realtimeTimer=null;if(session&&box&&document.visibilityState!=='hidden')loadAll()},180)}","function scheduleRealtimeReload(){if(realtimeTimer)clearTimeout(realtimeTimer);realtimeTimer=setTimeout(function(){realtimeTimer=null;if(session&&box&&document.visibilityState!=='hidden')loadAll()},360)}");
    html=html.replace("function scheduleLibraryReload(){if(libraryReloadTimer)clearTimeout(libraryReloadTimer);libraryReloadTimer=setTimeout(function(){libraryReloadTimer=null;if(mode==='library'&&document.visibilityState!=='hidden')loadLibrary(true)},120)}","function scheduleLibraryReload(){if(libraryReloadTimer)clearTimeout(libraryReloadTimer);libraryReloadTimer=setTimeout(function(){libraryReloadTimer=null;if(mode==='library'&&document.visibilityState!=='hidden')loadLibrary(true)},280)}");
    html=html.replace("startLibraryAutoRefresh(){if(libraryPollTimer)return;libraryPollTimer=setInterval(function(){if(mode==='library'&&document.visibilityState!=='hidden')loadLibrary(true)},6000)}","startLibraryAutoRefresh(){if(libraryPollTimer)return;libraryPollTimer=setInterval(function(){if(mode==='library'&&document.visibilityState!=='hidden')loadLibrary(true)},12000)}");
    html=html.replace("voiceTimer=setInterval(updateVoiceTimer,250)","voiceTimer=setInterval(updateVoiceTimer,500)");
    html=html.replace("voiceRecorder.start(250)","voiceRecorder.start(500)");
    html=html.replace("scrollIntoView({behavior:'smooth',block:'center'})","scrollIntoView({behavior:'auto',block:'center'})");
    html=html.replace(/<style id="anonbox-v82-hotfix">[\s\S]*?<meta name="anonbox-ui-build" content="8\.2">/g,'');
    if(!html.includes('anonbox-v83-hotfix')) html=html.replace('</head>',CHAT_HOTFIX+'</head>');
    const headers=new Headers(response.headers);
    headers.set('Cache-Control','no-store, max-age=0');
    headers.delete('Content-Length');
    return new Response(html,{status:response.status,statusText:response.statusText,headers});
  }catch(e){
    return response;
  }
}

self.addEventListener('fetch',event=>{
  const req=event.request;
  if(req.method==='POST'&&req.url===LEGACY_API){
    event.respondWith(handleLegacyApi(req));
    return;
  }
  if(req.method!=='GET') return;
  if(req.mode==='navigate'){
    event.respondWith((async()=>{
      try{return await injectUiHotfix(await fetch(req,{cache:'no-store'}));}
      catch(e){return await injectUiHotfix(await caches.match('./'));}
    })());
    return;
  }
  event.respondWith(fetch(req).catch(()=>caches.match(req)));
});
