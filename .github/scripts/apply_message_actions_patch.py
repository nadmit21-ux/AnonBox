from pathlib import Path

INDEX = Path('web/index.html')
SW = Path('web/sw.js')
s = INDEX.read_text(encoding='utf-8')

if 'message-actions-v1' in s:
    sw = SW.read_text(encoding='utf-8')
    if "const CACHE='anonbox-v6';" in sw:
        SW.write_text(sw.replace("const CACHE='anonbox-v6';", "const CACHE='anonbox-v7';", 1), encoding='utf-8')
    print('Message actions patch already present')
    raise SystemExit(0)


def replace_once(old: str, new: str, label: str):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    s = s.replace(old, new, 1)

replace_once(
    ".chatError{margin:20px}",
    ".chatError{margin:20px}\n"
    "    /* message-actions-v1 */\n"
    "    .messageBubble{position:relative;cursor:pointer}.messageBubble:active{filter:brightness(1.08)}.bubbleText{white-space:pre-wrap}.replyQuote{margin:-2px 0 7px;padding:7px 9px;border-left:3px solid #8b5cf6;border-radius:9px;background:rgba(2,6,23,.34);font-size:11px;color:#cbd5e1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.reactionStrip{display:flex;flex-wrap:wrap;gap:5px;margin-top:7px}.reactionPill{display:inline-flex;align-items:center;gap:3px;padding:2px 7px;border-radius:999px;background:rgba(15,23,42,.78);border:1px solid rgba(148,163,184,.2);font-size:11px}.chatComposer{flex-wrap:wrap}.replyComposerBar{flex:0 0 100%;display:flex;align-items:center;gap:9px;padding:7px 10px;border-radius:13px;background:#111827;border-left:3px solid #8b5cf6}.replyComposerText{min-width:0;flex:1}.replyComposerText b{display:block;font-size:11px;color:#c4b5fd}.replyComposerText span{display:block;font-size:11px;color:#94a3b8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.replyComposerClose{width:30px;height:30px;padding:0;border-radius:50%;background:transparent;border:1px solid var(--line);color:#cbd5e1}.actionBackdrop{position:fixed;inset:0;z-index:80;background:rgba(0,0,0,.52);display:flex;align-items:flex-end;justify-content:center;padding:12px}.actionSheet{width:min(100%,600px);background:#0d1421;border:1px solid var(--line);border-radius:24px;padding:14px;box-shadow:0 -20px 60px rgba(0,0,0,.42)}.actionHandle{width:44px;height:4px;border-radius:999px;background:#475569;margin:0 auto 12px}.actionPreview{padding:10px 12px;border-radius:14px;background:#111827;color:#cbd5e1;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:10px}.reactionPicker{display:flex;justify-content:space-between;gap:5px;padding:8px 2px 12px}.reactionPicker button{width:42px;height:42px;padding:0;border-radius:50%;background:#111827;border:1px solid var(--line);font-size:20px}.actionGrid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}.actionGrid button{background:#111827;border:1px solid var(--line);color:#e2e8f0}.actionGrid button.danger{background:#35141d;color:#fecdd3;border-color:#6b2638}.forwardTargets{display:grid;gap:7px;max-height:45vh;overflow:auto;margin-top:10px}.forwardTarget{display:flex;align-items:center;justify-content:space-between;gap:10px;text-align:left;background:#111827;border:1px solid var(--line)}.forwardBack{margin-top:9px;width:100%;background:transparent;border:1px solid var(--line);color:#cbd5e1}",
    'message action styles',
)

replace_once(
    "remoteTypingTimer=null,typingStopTimer=null,typingThrottleTimer=null,libraryReloadTimer=null;",
    "remoteTypingTimer=null,typingStopTimer=null,typingThrottleTimer=null,libraryReloadTimer=null,replyTarget=null,actionMessage=null,actionViewer=null;",
    'message action state',
)

marker = "async function rpc(name,args){var r=await sb.rpc(name,args);if(r.error)throw r.error;return r.data}"
helpers = r'''function activeViewerMessages(){if(actionViewer==='owner'||activeChatViewer==='owner')return messages||[];var c=visitorConversation();return c&&c.messages?c.messages:[]}
function findActiveMessage(id){var list=activeViewerMessages(),sid=String(id);return list.find(function(m){return String(m.id)===sid})||null}
function ownMessage(m,viewer){return viewer==='owner'?m.direction==='owner':m.direction==='visitor'}
function reactionHtml(summary){var obj=summary&&typeof summary==='object'?summary:{};return Object.keys(obj).filter(function(k){return Number(obj[k])>0}).map(function(k){return '<span class="reactionPill">'+esc(k)+' <b>'+esc(obj[k])+'</b></span>'}).join('')}
function ensureReplyBar(){var composer=$('chatComposer');if(!composer||$('replyComposerBar'))return;var bar=document.createElement('div');bar.id='replyComposerBar';bar.className='replyComposerBar hidden';bar.innerHTML='<div class="replyComposerText"><b>Réponse</b><span id="replyComposerPreview"></span></div><button id="replyComposerClose" class="replyComposerClose" type="button">×</button>';composer.insertBefore(bar,$('chatInput'));$('replyComposerClose').onclick=function(){clearReplyTarget()}}
function clearReplyTarget(){replyTarget=null;var bar=$('replyComposerBar');if(bar)bar.classList.add('hidden')}
function setReplyMessage(m){replyTarget=m;ensureReplyBar();var bar=$('replyComposerBar'),p=$('replyComposerPreview');if(p)p.textContent=previewText(m&&m.body||'Message');if(bar)bar.classList.remove('hidden');closeMessageActions();setTimeout(function(){$('chatInput').focus()},40)}
function ensureActionSheet(){if($('messageActionBackdrop'))return;var d=document.createElement('div');d.id='messageActionBackdrop';d.className='actionBackdrop hidden';d.innerHTML='<div class="actionSheet" role="dialog" aria-modal="true"><div class="actionHandle"></div><div id="messageActionMain"><div id="messageActionPreview" class="actionPreview"></div><div class="reactionPicker">'+['❤️','😂','😮','😢','👍','👎'].map(function(e){return '<button type="button" class="reactionChoice" data-emoji="'+e+'">'+e+'</button>'}).join('')+'</div><div class="actionGrid"><button type="button" id="messageReplyAction">↩ Répondre</button><button type="button" id="messageCopyAction">⧉ Copier</button><button type="button" id="messageForwardAction">↗ Transférer</button><button type="button" id="messageDeleteAction" class="danger">🗑 Supprimer</button></div></div><div id="messageForwardPanel" class="hidden"><b>Transférer vers…</b><div id="messageForwardTargets" class="forwardTargets"></div><button id="messageForwardBack" class="forwardBack" type="button">Retour</button></div></div>';document.body.appendChild(d);d.onclick=function(e){if(e.target===d)closeMessageActions()};$('messageReplyAction').onclick=function(){if(actionMessage)setReplyMessage(actionMessage)};$('messageCopyAction').onclick=function(){if(actionMessage)copyMessageText(actionMessage.body)};$('messageForwardAction').onclick=function(){if(actionMessage)showForwardTargets(actionMessage,actionViewer)};$('messageDeleteAction').onclick=function(){if(actionMessage)deleteActiveMessage(actionMessage,actionViewer)};$('messageForwardBack').onclick=function(){showActionMain()};document.querySelectorAll('.reactionChoice').forEach(function(b){b.onclick=function(){if(actionMessage)toggleMessageReaction(actionMessage,b.getAttribute('data-emoji'))}})}
function closeMessageActions(){var d=$('messageActionBackdrop');if(d)d.classList.add('hidden');actionMessage=null;actionViewer=null;showActionMain()}
function showActionMain(){var a=$('messageActionMain'),f=$('messageForwardPanel');if(a)a.classList.remove('hidden');if(f)f.classList.add('hidden')}
function openMessageActions(m,viewer){actionMessage=m;actionViewer=viewer;ensureActionSheet();$('messageActionPreview').textContent=previewText(m.body||'Message');$('messageDeleteAction').classList.toggle('hidden',!ownMessage(m,viewer));showActionMain();$('messageActionBackdrop').classList.remove('hidden')}
async function copyMessageText(text){try{await navigator.clipboard.writeText(String(text||''))}catch(e){var t=document.createElement('textarea');t.value=String(text||'');document.body.appendChild(t);t.select();document.execCommand('copy');t.remove()}closeMessageActions()}
async function toggleMessageReaction(m,emoji){try{var out=await rpc('anonbox_toggle_reaction',{p_message_id:m.id,p_emoji:emoji,p_device_id:deviceId()});if(!out||out.ok===false)throw new Error((out&&out.error)||'Réaction impossible.');closeMessageActions();if(actionViewer==='owner'||activeChatViewer==='owner')await loadAll();else await loadLibrary(true)}catch(e){alert(e.message||'Réaction impossible.')}}
async function deleteActiveMessage(m,viewer){if(!ownMessage(m,viewer))return;if(!confirm('Supprimer ce message pour cette conversation ?'))return;try{var out=await rpc('anonbox_delete_message',{p_message_id:m.id,p_device_id:deviceId()});if(!out||out.ok===false)throw new Error((out&&out.error)||'Suppression impossible.');closeMessageActions();clearReplyTarget();if(viewer==='owner')await loadAll();else await loadLibrary(true)}catch(e){alert(e.message||'Suppression impossible.')}}
function showForwardTargets(m,viewer){var targets=[];if(viewer==='owner'){targets=groupConversations().filter(function(c){return c.id!==chatId}).map(function(c){return {id:c.id,label:conversationIdentity(c).name,kind:'owner'}})}else{targets=libraryConversations.filter(function(c){return c.conversation_id!==chatId}).map(function(c){return {id:c.conversation_id,label:(c.owner&&c.owner.pseudonym)||c.title||'Conversation',kind:'visitor',conversation:c}})}$('messageActionMain').classList.add('hidden');$('messageForwardPanel').classList.remove('hidden');var el=$('messageForwardTargets');if(!targets.length){el.innerHTML='<div class="empty">Aucune autre conversation disponible.</div>';return}el.innerHTML=targets.map(function(t){return '<button type="button" class="forwardTarget" data-id="'+esc(t.id)+'"><span>'+esc(t.label)+'</span><span>›</span></button>'}).join('');el.querySelectorAll('.forwardTarget').forEach(function(b){b.onclick=function(){var id=b.getAttribute('data-id'),t=targets.find(function(x){return String(x.id)===String(id)});if(t)forwardMessage(m,viewer,t)}})}
async function forwardMessage(m,viewer,target){try{if(viewer==='owner'){var out=await rpc('anonbox_reply',{p_conversation_id:target.id,p_body:m.body,p_reply_to_id:null});if(!out||out.ok===false)throw new Error((out&&out.error)||'Transfert impossible.')}else{var c=target.conversation,vm=(c.messages||[]).filter(function(x){return x.direction==='visitor'}),threadMode=vm.length?(vm[0].sender_mode||'anonymous'):'anonymous',out2=await rpc('anonbox_submit_message',{p_slug:c.slug,p_body:m.body,p_mode:threadMode,p_device_id:deviceId(),p_reply_to_id:null});if(!out2||out2.ok===false)throw new Error((out2&&out2.error)||'Transfert impossible.')}closeMessageActions();alert('Message transféré ✓')}catch(e){alert(e.message||'Transfert impossible.')}}
function bindMessageActions(viewer){document.querySelectorAll('.messageBubble').forEach(function(el){el.onclick=function(){var m=findActiveMessage(el.getAttribute('data-message-id'));if(m)openMessageActions(m,viewer)};el.oncontextmenu=function(e){e.preventDefault();var m=findActiveMessage(el.getAttribute('data-message-id'));if(m)openMessageActions(m,viewer)}})}
''' + marker
replace_once(marker, helpers, 'message action helpers')

old_bubble = "function renderMessageBubble(m,viewer){var right=viewer==='owner'?m.direction==='owner':m.direction==='visitor',readState='';if(right)readState=m.read_at?'<span class=\"readMark\" title=\"Lu\">✓✓</span>':'<span class=\"sentMark\" title=\"Envoyé\">✓</span>';return '<div class=\"bubble '+(right?'right':'left')+'\">'+esc(m.body)+'<span class=\"bubbleMeta\"><span>'+esc(clockLabel(m.created_at))+'</span>'+readState+'</span></div>'}"
new_bubble = "function renderMessageBubble(m,viewer){var right=viewer==='owner'?m.direction==='owner':m.direction==='visitor',readState='',src=m.reply_to_id?findActiveMessage(m.reply_to_id):null,quote=m.reply_to_id?'<div class=\"replyQuote\">↪ '+esc(src?previewText(src.body):'Message indisponible')+'</div>':'',reactions=reactionHtml(m.reaction_summary);if(right)readState=m.read_at?'<span class=\"readMark\" title=\"Lu\">✓✓</span>':'<span class=\"sentMark\" title=\"Envoyé\">✓</span>';return '<div class=\"bubble messageBubble '+(right?'right':'left')+'\" data-message-id=\"'+esc(m.id)+'\">'+quote+'<div class=\"bubbleText\">'+esc(m.body)+'</div>'+(reactions?'<div class=\"reactionStrip\">'+reactions+'</div>':'')+'<span class=\"bubbleMeta\"><span>'+esc(clockLabel(m.created_at))+'</span>'+readState+'</span></div>'}"
replace_once(old_bubble, new_bubble, 'bubble actions and metadata')

replace_once(
    "$('chatScreenBody').innerHTML=out||'<div class=\"empty\">Aucun message.</div>';setTimeout(function(){window.scrollTo({top:document.body.scrollHeight,behavior:'auto'})},30)}",
    "$('chatScreenBody').innerHTML=out||'<div class=\"empty\">Aucun message.</div>';ensureReplyBar();bindMessageActions(viewer);setTimeout(function(){window.scrollTo({top:document.body.scrollHeight,behavior:'auto'})},30)}",
    'bind bubble actions',
)

replace_once(
    ".on('broadcast',{event:'read'},function(){scheduleLibraryReload()}).subscribe();",
    ".on('broadcast',{event:'read'},function(){scheduleLibraryReload()}).on('broadcast',{event:'reaction'},function(){scheduleLibraryReload()}).subscribe();",
    'library reaction realtime',
)

replace_once(
    ".on('broadcast',{event:'read'},function(){activeChatReload()}).on('broadcast',{event:'typing'},showRemoteTyping).subscribe()",
    ".on('broadcast',{event:'read'},function(){activeChatReload()}).on('broadcast',{event:'reaction'},function(){activeChatReload()}).on('broadcast',{event:'typing'},showRemoteTyping).subscribe()",
    'active chat reaction realtime',
)

replace_once(
    ".select('id,conversation_id,direction,body,sender_mode,sender_user_id,sender_pseudonym_snapshot,sender_avatar_path_snapshot,created_at,read_at,deleted_at')",
    ".select('id,conversation_id,direction,body,sender_mode,sender_user_id,sender_pseudonym_snapshot,sender_avatar_path_snapshot,created_at,read_at,deleted_at,reply_to_id,reaction_summary')",
    'owner message metadata query',
)

replace_once(
    "rpc('anonbox_submit_message',{p_slug:c.slug,p_body:text,p_mode:threadMode,p_device_id:deviceId()})",
    "rpc('anonbox_submit_message',{p_slug:c.slug,p_body:text,p_mode:threadMode,p_device_id:deviceId(),p_reply_to_id:replyTarget?replyTarget.id:null})",
    'visitor reply target send',
)
replace_once(
    "$('chatInput').value='';autoGrowComposer();sendTypingState(false);await loadLibrary()",
    "$('chatInput').value='';autoGrowComposer();sendTypingState(false);clearReplyTarget();await loadLibrary()",
    'visitor clear reply',
)
replace_once(
    "rpc('anonbox_reply',{p_conversation_id:chatId,p_body:text})",
    "rpc('anonbox_reply',{p_conversation_id:chatId,p_body:text,p_reply_to_id:replyTarget?replyTarget.id:null})",
    'owner reply target send',
)
replace_once(
    "$('chatInput').value='';autoGrowComposer();sendTypingState(false);await loadAll()",
    "$('chatInput').value='';autoGrowComposer();sendTypingState(false);clearReplyTarget();await loadAll()",
    'owner clear reply',
)

INDEX.write_text(s, encoding='utf-8')

sw = SW.read_text(encoding='utf-8')
if "const CACHE='anonbox-v6';" not in sw:
    if "const CACHE='anonbox-v7';" not in sw:
        raise SystemExit('service worker cache marker not found')
else:
    SW.write_text(sw.replace("const CACHE='anonbox-v6';", "const CACHE='anonbox-v7';", 1), encoding='utf-8')

print('Message actions frontend patch applied successfully')
