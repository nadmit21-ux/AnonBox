from pathlib import Path

INDEX=Path('web/index.html')
SW=Path('web/sw.js')
s=INDEX.read_text(encoding='utf-8')

if 'private-attachments-v1' in s:
    sw=SW.read_text(encoding='utf-8')
    if "const CACHE='anonbox-v7';" in sw:
        SW.write_text(sw.replace("const CACHE='anonbox-v7';","const CACHE='anonbox-v8';",1),encoding='utf-8')
    print('Private attachments patch already present')
    raise SystemExit(0)

def replace_once(old,new,label):
    global s
    c=s.count(old)
    if c!=1: raise SystemExit(f'{label}: expected 1 match, found {c}')
    s=s.replace(old,new,1)

replace_once(
    "SUPABASE_KEY='sb_publishable_qHIobQFTgOOrzBttJazZQA_e5-MvmLK',BASE=",
    "SUPABASE_KEY='sb_publishable_qHIobQFTgOOrzBttJazZQA_e5-MvmLK',ATTACHMENT_API=SUPABASE_URL+'/functions/v1/anonbox-attachment',BASE=",
    'attachment api constant'
)

replace_once(
    "replyTarget=null,actionMessage=null,actionViewer=null;",
    "replyTarget=null,actionMessage=null,actionViewer=null,attachmentBusy=false,attachmentUrlCache={};",
    'attachment state'
)

replace_once(
    ".forwardBack{margin-top:9px;width:100%;background:transparent;border:1px solid var(--line);color:#cbd5e1}",
    ".forwardBack{margin-top:9px;width:100%;background:transparent;border:1px solid var(--line);color:#cbd5e1}\n"
    "    /* private-attachments-v1 */\n"
    "    .attachButton{width:46px;height:46px;flex:0 0 46px;padding:0;border-radius:50%;display:grid;place-items:center;background:#111827;border:1px solid var(--line);font-size:20px}.attachButton:disabled{opacity:.45}.attachmentCard{width:100%;margin-top:7px;padding:8px;display:flex;align-items:center;gap:9px;text-align:left;border-radius:13px;background:rgba(2,6,23,.38);border:1px solid rgba(148,163,184,.2);color:#e2e8f0}.attachmentThumb{width:58px;height:58px;flex:0 0 58px;border-radius:10px;display:grid;place-items:center;background:#111827;overflow:hidden;font-size:24px}.attachmentThumb img{width:100%;height:100%;object-fit:cover}.attachmentInfo{min-width:0;flex:1}.attachmentName{display:block;font-size:12px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.attachmentMeta{display:block;margin-top:3px;font-size:10px;color:#94a3b8}",
    'attachment styles'
)

marker="async function rpc(name,args){var r=await sb.rpc(name,args);if(r.error)throw r.error;return r.data}"
helpers=r'''function attachmentSize(n){n=Number(n||0);if(n<1024)return n+' o';if(n<1048576)return (n/1024).toFixed(1)+' Ko';return (n/1048576).toFixed(1)+' Mo'}
function attachmentIcon(mime){mime=String(mime||'');if(mime.indexOf('pdf')>=0)return '📕';if(mime.indexOf('zip')>=0)return '🗜️';if(mime.indexOf('audio/')===0)return '🎵';if(mime.indexOf('video/')===0)return '🎬';if(mime.indexOf('sheet')>=0)return '📊';if(mime.indexOf('presentation')>=0)return '📽️';if(mime.indexOf('word')>=0)return '📘';return '📎'}
function attachmentHtml(m){if(!m||!m.attachment_id)return '';var image=String(m.attachment_mime||'').indexOf('image/')===0,visual=image?'<span class="attachmentThumb" data-attachment-thumb="'+esc(m.id)+'">🖼️</span>':'<span class="attachmentThumb">'+attachmentIcon(m.attachment_mime)+'</span>';return '<button type="button" class="attachmentCard attachmentOpen" data-attachment-message="'+esc(m.id)+'">'+visual+'<span class="attachmentInfo"><span class="attachmentName">'+esc(m.attachment_name||'Fichier')+'</span><span class="attachmentMeta">'+esc(attachmentSize(m.attachment_size))+' · ouvrir</span></span></button>'}
function attachmentHeaders(jsonMode){var h={'apikey':SUPABASE_KEY};if(session&&session.access_token)h['Authorization']='Bearer '+session.access_token;if(jsonMode)h['Content-Type']='application/json';return h}
function ensureAttachmentControls(){var composer=$('chatComposer');if(!composer||$('chatAttachmentBtn'))return;var btn=document.createElement('button');btn.id='chatAttachmentBtn';btn.type='button';btn.className='attachButton';btn.textContent='📎';btn.title='Joindre un fichier';var input=document.createElement('input');input.id='chatAttachmentInput';input.type='file';input.className='hidden';input.accept='image/jpeg,image/png,image/webp,image/gif,application/pdf,text/plain,application/zip,.docx,.xlsx,.pptx,audio/mpeg,audio/mp4,video/mp4';composer.insertBefore(btn,$('chatInput'));composer.appendChild(input);btn.onclick=function(){if(!attachmentBusy)input.click()};input.onchange=function(){var f=input.files&&input.files[0];if(f)uploadAttachment(f);input.value=''}}
async function uploadAttachment(file){if(attachmentBusy||!chatId)return;if(file.size>10485760){alert('Fichier trop volumineux : 10 Mo maximum.');return}attachmentBusy=true;var btn=$('chatAttachmentBtn');if(btn)btn.disabled=true;status($('chatScreenStatus'),'Envoi du fichier…',true);try{var fd=new FormData();fd.append('conversation_id',chatId);fd.append('device_id',deviceId());fd.append('caption',$('chatInput').value.trim());if(replyTarget)fd.append('reply_to_id',String(replyTarget.id));fd.append('file',file,file.name);var res=await fetch(ATTACHMENT_API,{method:'POST',headers:attachmentHeaders(false),body:fd});var out=null;try{out=await res.json()}catch(e){}if(!res.ok||!out||out.ok===false)throw new Error((out&&out.error)||'Envoi du fichier impossible.');$('chatInput').value='';autoGrowComposer();clearReplyTarget();status($('chatScreenStatus'),'Fichier envoyé ✓',true);setTimeout(function(){clearStatus($('chatScreenStatus'))},1800);if(activeChatViewer==='owner')await loadAll();else await loadLibrary(true)}catch(e){status($('chatScreenStatus'),e.message||'Envoi du fichier impossible.',false)}attachmentBusy=false;if(btn)btn.disabled=false}
async function signedAttachmentUrl(messageId){var key=String(messageId),cached=attachmentUrlCache[key];if(cached&&cached.expires>Date.now())return cached.url;var res=await fetch(ATTACHMENT_API,{method:'POST',headers:attachmentHeaders(true),body:JSON.stringify({action:'sign',message_id:key,device_id:deviceId()})});var out=null;try{out=await res.json()}catch(e){}if(!res.ok||!out||!out.signed_url)throw new Error((out&&out.error)||'Pièce jointe indisponible.');attachmentUrlCache[key]={url:out.signed_url,expires:Date.now()+240000};return out.signed_url}
async function openAttachment(messageId){try{var url=await signedAttachmentUrl(messageId);location.href=url}catch(e){alert(e.message||'Pièce jointe indisponible.')}}
function bindAttachmentCards(){document.querySelectorAll('.attachmentOpen').forEach(function(el){el.onclick=function(e){e.stopPropagation();openAttachment(el.getAttribute('data-attachment-message'))}});document.querySelectorAll('[data-attachment-thumb]').forEach(function(el){var id=el.getAttribute('data-attachment-thumb');signedAttachmentUrl(id).then(function(url){if(document.body.contains(el))el.innerHTML='<img src="'+esc(url)+'" alt="">'}).catch(function(){})})}
''' + marker
replace_once(marker,helpers,'attachment helpers')

old="reactions=reactionHtml(m.reaction_summary);if(right)readState=m.read_at?'<span class=\"readMark\" title=\"Lu\">✓✓</span>':'<span class=\"sentMark\" title=\"Envoyé\">✓</span>';return '<div class=\"bubble messageBubble '+(right?'right':'left')+'\" data-message-id=\"'+esc(m.id)+'\">'+quote+'<div class=\"bubbleText\">'+esc(m.body)+'</div>'+(reactions?'<div class=\"reactionStrip\">'+reactions+'</div>':'')+'<span class=\"bubbleMeta\"><span>'+esc(clockLabel(m.created_at))+'</span>'+readState+'</span></div>'}"
new="reactions=reactionHtml(m.reaction_summary),attachment=attachmentHtml(m),hideFallback=!!(m.attachment_id&&String(m.body||'')==='📎 '+String(m.attachment_name||'')),bodyPart=hideFallback?'':'<div class=\"bubbleText\">'+esc(m.body)+'</div>';if(right)readState=m.read_at?'<span class=\"readMark\" title=\"Lu\">✓✓</span>':'<span class=\"sentMark\" title=\"Envoyé\">✓</span>';return '<div class=\"bubble messageBubble '+(right?'right':'left')+'\" data-message-id=\"'+esc(m.id)+'\">'+quote+bodyPart+attachment+(reactions?'<div class=\"reactionStrip\">'+reactions+'</div>':'')+'<span class=\"bubbleMeta\"><span>'+esc(clockLabel(m.created_at))+'</span>'+readState+'</span></div>'}"
replace_once(old,new,'attachment bubble rendering')

replace_once(
    "ensureReplyBar();bindMessageActions(viewer);setTimeout(function(){window.scrollTo({top:document.body.scrollHeight,behavior:'auto'})},30)",
    "ensureReplyBar();ensureAttachmentControls();bindMessageActions(viewer);bindAttachmentCards();setTimeout(function(){window.scrollTo({top:document.body.scrollHeight,behavior:'auto'})},30)",
    'attachment bindings'
)

replace_once(
    "created_at,read_at,deleted_at,reply_to_id,reaction_summary')",
    "created_at,read_at,deleted_at,reply_to_id,reaction_summary,attachment_id,attachment_name,attachment_mime,attachment_size')",
    'owner attachment metadata query'
)

INDEX.write_text(s,encoding='utf-8')
sw=SW.read_text(encoding='utf-8')
if "const CACHE='anonbox-v7';" in sw:
    SW.write_text(sw.replace("const CACHE='anonbox-v7';","const CACHE='anonbox-v8';",1),encoding='utf-8')
elif "const CACHE='anonbox-v8';" not in sw:
    raise SystemExit('service worker cache marker not found')
print('Private attachment frontend patch applied successfully')
