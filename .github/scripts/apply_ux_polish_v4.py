from pathlib import Path

INDEX = Path('web/index.html')
SW = Path('web/sw.js')
VERSION = Path('web/version.txt')
html = INDEX.read_text(encoding='utf-8')
marker = '/* anonbox-ux-polish-v4 */'

if marker in html:
    print('UX polish v4 already present')
    raise SystemExit(0)


def replace_once(old, new, label):
    global html
    count = html.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    html = html.replace(old, new, 1)

css = r'''
    /* anonbox-ux-polish-v4 */
    .scrollToBottom{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(var(--composer) + 24px + env(safe-area-inset-bottom));z-index:38;min-width:42px;height:42px;padding:0 11px;border-radius:999px;background:rgba(20,30,45,.96);border:1px solid rgba(148,163,184,.16);box-shadow:0 8px 26px rgba(0,0,0,.34);display:flex;align-items:center;justify-content:center;gap:6px;color:#d8e0ea;font-size:18px;backdrop-filter:blur(14px)}
    .scrollToBottom .scrollUnread{min-width:18px;height:18px;padding:0 5px;border-radius:999px;background:#755de9;display:grid;place-items:center;font-size:9px;font-weight:800;color:white}
    .unreadDivider{display:flex;align-items:center;gap:9px;margin:10px 0 8px;color:#9d91f7;font-size:10px;font-weight:750;letter-spacing:.02em}.unreadDivider:before,.unreadDivider:after{content:"";height:1px;flex:1;background:linear-gradient(90deg,transparent,rgba(124,92,255,.28))}.unreadDivider:after{background:linear-gradient(90deg,rgba(124,92,255,.28),transparent)}
    .messageBubble{transition:transform .14s ease,filter .14s ease,box-shadow .18s ease;touch-action:pan-y}.messageBubble.replySwipe{transform:translateX(18px)}.messageBubble.messageFlash{animation:messageFlash .75s ease}
    @keyframes messageFlash{0%,100%{box-shadow:0 3px 9px rgba(0,0,0,.12)}45%{box-shadow:0 0 0 3px rgba(124,92,255,.28),0 4px 18px rgba(0,0,0,.18)}}
    .replyQuote[data-reply-id]{cursor:pointer}.replyQuote[data-reply-id]:active{opacity:.78}
    .composerCounter{position:absolute;right:62px;bottom:2px;font-size:9px;color:#738195;pointer-events:none}.composerCounter.warn{color:#e5ad66}.composerCounter.limit{color:#ff8297}
    .toastStack{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(86px + env(safe-area-inset-bottom));z-index:120;width:min(calc(100% - 24px),520px);display:grid;gap:7px;pointer-events:none}
    .appToast{padding:11px 13px;border-radius:15px;background:rgba(20,30,44,.97);border:1px solid rgba(148,163,184,.14);box-shadow:0 12px 34px rgba(0,0,0,.34);color:#dbe4ee;font-size:12px;line-height:1.4;opacity:0;transform:translateY(10px) scale(.98);animation:toastIn .18s ease forwards}.appToast.ok{border-color:rgba(66,211,162,.23)}.appToast.err{border-color:rgba(255,117,143,.28);color:#ffd3db}@keyframes toastIn{to{opacity:1;transform:none}}
    .confirmBackdrop{position:fixed;inset:0;z-index:125;display:grid;place-items:center;padding:20px;background:rgba(2,6,12,.64);backdrop-filter:blur(5px)}.confirmCard{width:min(100%,390px);padding:18px;border-radius:22px;background:#111a27;border:1px solid rgba(148,163,184,.14);box-shadow:0 22px 70px rgba(0,0,0,.46)}.confirmCard h3{margin:0 0 7px;font-size:17px}.confirmCard p{margin:0 0 16px;color:#8e9bad;font-size:12px;line-height:1.5}.confirmActions{display:grid;grid-template-columns:1fr 1fr;gap:8px}.confirmActions button{border-radius:14px}.confirmCancel{background:rgba(255,255,255,.045);border:1px solid rgba(148,163,184,.12);color:#c5cfdb}.confirmDanger{background:#51212c;border:1px solid rgba(255,117,143,.28);color:#ffd3db}
    @media(max-width:560px){.scrollToBottom{bottom:calc(var(--composer) + 18px + env(safe-area-inset-bottom))}.toastStack{bottom:calc(78px + env(safe-area-inset-bottom))}}
'''
replace_once('</style>', css + '\n  </style>', 'append UX polish styles')

replace_once(
    "attachmentBusy=false,attachmentUrlCache={};",
    "attachmentBusy=false,attachmentUrlCache={},chatRenderInitialized=false,chatRenderedCount=0,chatFirstUnreadId=null,chatUnreadWhileAway=0,chatScrollButton=null,chatScrollBound=false,composerCounter=null;",
    'extend UX state',
)

helpers_marker = "function activeViewerMessages(){"
helpers = r'''function isChatNearBottom(){return (document.documentElement.scrollHeight-(window.scrollY+window.innerHeight))<190}
function ensureChatScrollButton(){if(chatScrollButton&&document.body.contains(chatScrollButton))return chatScrollButton;var b=document.createElement('button');b.type='button';b.className='scrollToBottom hidden';b.setAttribute('aria-label','Aller aux messages récents');b.innerHTML='<span>↓</span><span class="scrollUnread hidden"></span>';b.onclick=function(){scrollChatBottom(true)};document.body.appendChild(b);chatScrollButton=b;return b}
function updateChatScrollButton(){var b=ensureChatScrollButton(),near=isChatNearBottom(),badge=b.querySelector('.scrollUnread');if(near){chatUnreadWhileAway=0;b.classList.add('hidden')}else b.classList.remove('hidden');if(chatUnreadWhileAway>0){badge.textContent=chatUnreadWhileAway>99?'99+':String(chatUnreadWhileAway);badge.classList.remove('hidden')}else badge.classList.add('hidden')}
function scrollChatBottom(smooth){chatUnreadWhileAway=0;window.scrollTo({top:document.documentElement.scrollHeight,behavior:smooth?'smooth':'auto'});setTimeout(updateChatScrollButton,80)}
function bindChatScrollTracking(){if(chatScrollBound)return;chatScrollBound=true;window.addEventListener('scroll',function(){if(!chatId)return;updateChatScrollButton()},{passive:true})}
function haptic(ms){try{if(navigator.vibrate)navigator.vibrate(ms||12)}catch(e){}}
function showToast(message,type){var stack=$('anonboxToastStack');if(!stack){stack=document.createElement('div');stack.id='anonboxToastStack';stack.className='toastStack';document.body.appendChild(stack)}var t=document.createElement('div');t.className='appToast '+(type||'');t.textContent=String(message||'');stack.appendChild(t);setTimeout(function(){t.style.opacity='0';t.style.transform='translateY(8px) scale(.98)';setTimeout(function(){t.remove()},180)},2600)}
function toastType(message){var s=String(message||'').toLowerCase();if(s.indexOf('impossible')>=0||s.indexOf('erreur')>=0||s.indexOf('invalide')>=0||s.indexOf('trop ')>=0||s.indexOf('refus')>=0||s.indexOf('format')>=0)return 'err';if(s.indexOf('✓')>=0||s.indexOf('envoy')>=0||s.indexOf('enregistr')>=0||s.indexOf('copi')>=0)return 'ok';return ''}
window.alert=function(message){showToast(message,toastType(message))}
function confirmAction(title,message,dangerLabel){return new Promise(function(resolve){var d=document.createElement('div');d.className='confirmBackdrop';d.innerHTML='<div class="confirmCard" role="dialog" aria-modal="true"><h3>'+esc(title)+'</h3><p>'+esc(message)+'</p><div class="confirmActions"><button type="button" class="confirmCancel">Annuler</button><button type="button" class="confirmDanger">'+esc(dangerLabel||'Confirmer')+'</button></div></div>';document.body.appendChild(d);function done(v){d.remove();resolve(v)}d.querySelector('.confirmCancel').onclick=function(){done(false)};d.querySelector('.confirmDanger').onclick=function(){done(true)};d.onclick=function(e){if(e.target===d)done(false)}})}
function ensureComposerCounter(){if(composerCounter&&document.body.contains(composerCounter))return composerCounter;var composer=$('chatComposer');if(!composer)return null;var c=document.createElement('span');c.id='composerCounter';c.className='composerCounter hidden';composer.appendChild(c);composerCounter=c;return c}
function updateComposerState(){var input=$('chatInput'),send=$('chatSendBtn');if(!input||!send)return;var len=input.value.length;if(!send.dataset.sending)send.disabled=!input.value.trim();var c=ensureComposerCounter();if(c){c.textContent=len+'/1500';c.className='composerCounter '+(len>=1450?'limit':(len>=1200?'warn':'hidden'));if(len>=1200)c.classList.remove('hidden')}}
function flashQuotedMessage(id){var el=document.querySelector('.messageBubble[data-message-id="'+String(id).replace(/"/g,'')+'"]');if(!el)return;el.scrollIntoView({behavior:'smooth',block:'center'});el.classList.remove('messageFlash');void el.offsetWidth;el.classList.add('messageFlash');setTimeout(function(){el.classList.remove('messageFlash')},800)}
function bindReplyQuoteLinks(){document.querySelectorAll('.replyQuote[data-reply-id]').forEach(function(q){q.onclick=function(e){e.stopPropagation();flashQuotedMessage(q.getAttribute('data-reply-id'))}})}
function bindSwipeReply(viewer){document.querySelectorAll('.messageBubble').forEach(function(el){if(el.dataset.swipeBound==='1')return;el.dataset.swipeBound='1';var sx=0,sy=0,dx=0,dy=0,moved=false;el.addEventListener('touchstart',function(e){var t=e.touches&&e.touches[0];if(!t)return;sx=t.clientX;sy=t.clientY;dx=dy=0;moved=false},{passive:true});el.addEventListener('touchmove',function(e){var t=e.touches&&e.touches[0];if(!t)return;dx=t.clientX-sx;dy=t.clientY-sy;if(dx>8&&Math.abs(dy)<40){moved=true;el.classList.toggle('replySwipe',dx>26)}},{passive:true});el.addEventListener('touchend',function(){el.classList.remove('replySwipe');if(moved&&dx>55&&Math.abs(dy)<42){var m=findActiveMessage(el.getAttribute('data-message-id'));if(m){el.dataset.justSwiped='1';haptic(16);setReplyMessage(m);setTimeout(function(){delete el.dataset.justSwiped},220)}}},{passive:true})})}
'''
replace_once(helpers_marker, helpers + helpers_marker, 'insert UX helpers')

old_delete = "async function deleteActiveMessage(m,viewer){if(!ownMessage(m,viewer))return;if(!confirm('Supprimer ce message pour cette conversation ?'))return;try{"
new_delete = "async function deleteActiveMessage(m,viewer){if(!ownMessage(m,viewer))return;if(!await confirmAction('Supprimer le message','Ce message sera retiré de cette conversation.','Supprimer'))return;try{"
replace_once(old_delete, new_delete, 'replace destructive confirm')

old_bind = "function bindMessageActions(viewer){document.querySelectorAll('.messageBubble').forEach(function(el){el.onclick=function(){var m=findActiveMessage(el.getAttribute('data-message-id'));if(m)openMessageActions(m,viewer)};el.oncontextmenu=function(e){e.preventDefault();var m=findActiveMessage(el.getAttribute('data-message-id'));if(m)openMessageActions(m,viewer)}})}"
new_bind = "function bindMessageActions(viewer){document.querySelectorAll('.messageBubble').forEach(function(el){el.onclick=function(){if(el.dataset.justSwiped==='1')return;var m=findActiveMessage(el.getAttribute('data-message-id'));if(m)openMessageActions(m,viewer)};el.oncontextmenu=function(e){e.preventDefault();var m=findActiveMessage(el.getAttribute('data-message-id'));if(m)openMessageActions(m,viewer)}});bindSwipeReply(viewer)}"
replace_once(old_bind, new_bind, 'add swipe reply')

old_quote = "quote=m.reply_to_id?'<div class=\"replyQuote\">↪ '+esc(src?previewText(src.body):'Message indisponible')+'</div>':'',"
new_quote = "quote=m.reply_to_id?'<div class=\"replyQuote\" data-reply-id=\"'+esc(m.reply_to_id)+'\">↪ '+esc(src?previewText(src.body):'Message indisponible')+'</div>':'',"
replace_once(old_quote, new_quote, 'make reply quote interactive')

old_stream = "function renderMessageStream(msgs,viewer){var lastDay='',out='';msgs.forEach(function(m){var day=dayLabel(m.created_at);if(day!==lastDay){out+='<div class=\"dayPill\">'+esc(day)+'</div>';lastDay=day}out+=renderMessageBubble(m,viewer)});$('chatScreenBody').innerHTML=out||'<div class=\"empty\">Aucun message.</div>';ensureReplyBar();ensureAttachmentControls();bindMessageActions(viewer);bindAttachmentCards();setTimeout(function(){window.scrollTo({top:document.body.scrollHeight,behavior:'auto'})},30)}"
new_stream = "function renderMessageStream(msgs,viewer){var first=!chatRenderInitialized,wasNear=first||isChatNearBottom(),oldCount=chatRenderedCount,lastDay='',out='';msgs.forEach(function(m){var day=dayLabel(m.created_at);if(day!==lastDay){out+='<div class=\"dayPill\">'+esc(day)+'</div>';lastDay=day}if(chatFirstUnreadId&&String(m.id)===String(chatFirstUnreadId))out+='<div class=\"unreadDivider\">Nouveaux messages</div>';out+=renderMessageBubble(m,viewer)});$('chatScreenBody').innerHTML=out||'<div class=\"empty\">Aucun message.</div>';ensureReplyBar();ensureAttachmentControls();ensureComposerCounter();bindMessageActions(viewer);bindReplyQuoteLinks();bindAttachmentCards();bindChatScrollTracking();chatRenderedCount=msgs.length;chatRenderInitialized=true;var added=Math.max(0,msgs.length-oldCount);if(first){setTimeout(function(){var unread=chatFirstUnreadId&&document.querySelector('.messageBubble[data-message-id=\"'+chatFirstUnreadId+'\"]');if(unread)unread.scrollIntoView({block:'center',behavior:'auto'});else scrollChatBottom(false);updateChatScrollButton()},40)}else if(wasNear){setTimeout(function(){scrollChatBottom(false)},30)}else if(added>0){chatUnreadWhileAway+=added;var last=msgs[msgs.length-1],incoming=last&&(viewer==='owner'?last.direction==='visitor':last.direction==='owner');if(incoming)haptic(12);setTimeout(updateChatScrollButton,30)}else setTimeout(updateChatScrollButton,30);updateComposerState()}"
replace_once(old_stream, new_stream, 'preserve chat scroll and unread marker')

old_input = "function handleComposerTyping(){autoGrowComposer();if(!chatId)return;"
new_input = "function handleComposerTyping(){autoGrowComposer();updateComposerState();if(!chatId)return;"
replace_once(old_input, new_input, 'composer state on input')

old_listener = "$('chatInput').addEventListener('input',handleComposerTyping);$('chatInput').addEventListener('blur',function(){sendTypingState(false)});"
new_listener = "$('chatInput').addEventListener('input',handleComposerTyping);$('chatInput').addEventListener('blur',function(){sendTypingState(false)});$('chatInput').addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey&&window.matchMedia&&window.matchMedia('(pointer:fine)').matches){e.preventDefault();if(!$('chatSendBtn').disabled)$('chatSendBtn').click()}});document.addEventListener('keydown',function(e){if(e.key==='Escape'){if(replyTarget)clearReplyTarget();closeMessageActions()}});"
replace_once(old_listener, new_listener, 'keyboard comfort')

# Capture the first unread message before marking the thread read.
old_visitor = "async function renderVisitorChat(){var c=visitorConversation();if(!c){"
new_visitor = "async function renderVisitorChat(){var c=visitorConversation();if(!c){"
# Keep prefix, inject immediately after the missing-conversation guard via a stable longer match.
old_visitor_guard = "$('chatBackBtn').onclick=function(){goto(BASE+'?library=1')};return}try{var readOut=await rpc('anonbox_mark_library_read'"
new_visitor_guard = "$('chatBackBtn').onclick=function(){goto(BASE+'?library=1')};return}if(!chatRenderInitialized){var firstUnreadVisitor=(c.messages||[]).find(function(mm){return mm.direction==='owner'&&!mm.read_at});chatFirstUnreadId=firstUnreadVisitor?firstUnreadVisitor.id:null}try{var readOut=await rpc('anonbox_mark_library_read'"
replace_once(old_visitor_guard, new_visitor_guard, 'visitor first unread marker')

old_owner = "async function renderOwnerChat(){var c=groupConversations().find(function(x){return x.id===chatId});if(!c){showChatError('Conversation introuvable.');$('chatBackBtn').onclick=function(){goto(BASE+'?app=1&tab=messages')};return}await markConversationRead(chatId);"
new_owner = "async function renderOwnerChat(){var c=groupConversations().find(function(x){return x.id===chatId});if(!c){showChatError('Conversation introuvable.');$('chatBackBtn').onclick=function(){goto(BASE+'?app=1&tab=messages')};return}if(!chatRenderInitialized){var firstUnreadOwner=(c.messages||[]).find(function(mm){return mm.direction==='visitor'&&!mm.read_at});chatFirstUnreadId=firstUnreadOwner?firstUnreadOwner.id:null}await markConversationRead(chatId);"
replace_once(old_owner, new_owner, 'owner first unread marker')

# Track async send state without letting composer input re-enable button mid-flight.
html = html.replace("$('chatSendBtn').disabled=true;try{", "$('chatSendBtn').dataset.sending='1';$('chatSendBtn').disabled=true;try{", 2)
html = html.replace("$('chatSendBtn').disabled=false}};", "delete $('chatSendBtn').dataset.sending;updateComposerState()}};", 2)

# Update composer after clearing message text in the two chat send flows and attachment flow.
html = html.replace("$('chatInput').value='';autoGrowComposer();sendTypingState(false);clearReplyTarget();", "$('chatInput').value='';autoGrowComposer();updateComposerState();sendTypingState(false);clearReplyTarget();")
html = html.replace("$('chatInput').value='';autoGrowComposer();clearReplyTarget();status($('chatScreenStatus'),'Fichier envoyé ✓',true);", "$('chatInput').value='';autoGrowComposer();updateComposerState();clearReplyTarget();status($('chatScreenStatus'),'Fichier envoyé ✓',true);", 1)

INDEX.write_text(html, encoding='utf-8')

sw = SW.read_text(encoding='utf-8')
if "const CACHE='anonbox-v11';" not in sw:
    raise SystemExit('service worker cache v11 marker not found')
SW.write_text(sw.replace("const CACHE='anonbox-v11';", "const CACHE='anonbox-v12';", 1), encoding='utf-8')
VERSION.write_text('AnonBox web UI v4\nPremium messaging UX polish\nScroll preservation, unread divider, swipe-to-reply, in-app toasts, keyboard and composer polish\nCache: anonbox-v12\n', encoding='utf-8')
print('AnonBox UX polish v4 applied')
