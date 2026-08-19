from pathlib import Path

INDEX = Path('web/index.html')
SW = Path('web/sw.js')
s = INDEX.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    s = s.replace(old, new, 1)


replace_once(
    "realtimeTimer=null,libraryPollTimer=null;",
    "realtimeTimer=null,libraryPollTimer=null,libraryRealtimeChannels=[],activeChatChannel=null,activeChatTopic=null,activeChatViewer=null,activeChatBaseSub='',remoteTypingTimer=null,typingStopTimer=null,typingThrottleTimer=null,libraryReloadTimer=null;",
    'state variables',
)

replace_once(
    "function renderHeader(name,sub,avatar,anonymous){$('chatHeaderIdentity')",
    "function renderHeader(name,sub,avatar,anonymous){activeChatBaseSub=sub||'';$('chatHeaderIdentity')",
    'renderHeader state',
)

replace_once(
    "function renderMessageBubble(m,viewer){var right=viewer==='owner'?m.direction==='owner':m.direction==='visitor',readState='';if(right){if(viewer==='owner')readState=m.read_at?'<span class=\"readMark\">✓✓</span>':'<span class=\"sentMark\">✓</span>';else readState='<span class=\"sentMark\">✓</span>'}return '<div class=\"bubble '+(right?'right':'left')+'\">'+esc(m.body)+'<span class=\"bubbleMeta\"><span>'+esc(clockLabel(m.created_at))+'</span>'+readState+'</span></div>'}",
    "function renderMessageBubble(m,viewer){var right=viewer==='owner'?m.direction==='owner':m.direction==='visitor',readState='';if(right)readState=m.read_at?'<span class=\"readMark\" title=\"Lu\">✓✓</span>':'<span class=\"sentMark\" title=\"Envoyé\">✓</span>';return '<div class=\"bubble '+(right?'right':'left')+'\">'+esc(m.body)+'<span class=\"bubbleMeta\"><span>'+esc(clockLabel(m.created_at))+'</span>'+readState+'</span></div>'}",
    'read receipts',
)

marker = "function stopLibraryAutoRefresh(){if(libraryPollTimer){clearInterval(libraryPollTimer);libraryPollTimer=null}}async function rpc"
insert = r"""function stopLibraryAutoRefresh(){if(libraryPollTimer){clearInterval(libraryPollTimer);libraryPollTimer=null}}
function stopLibraryRealtime(){libraryRealtimeChannels.forEach(function(ch){try{sb.removeChannel(ch)}catch(e){}});libraryRealtimeChannels=[]}
function scheduleLibraryReload(){if(libraryReloadTimer)clearTimeout(libraryReloadTimer);libraryReloadTimer=setTimeout(function(){libraryReloadTimer=null;if(mode==='library'&&document.visibilityState!=='hidden')loadLibrary(true)},120)}
function startLibraryRealtime(){stopLibraryRealtime();if(mode!=='library'||chatId||!sb||!sb.channel)return;libraryConversations.slice(0,50).forEach(function(c){if(!c.realtime_topic)return;var ch=sb.channel(c.realtime_topic).on('broadcast',{event:'message'},function(){scheduleLibraryReload()}).on('broadcast',{event:'read'},function(){scheduleLibraryReload()}).subscribe();libraryRealtimeChannels.push(ch)})}
function resetRemoteTyping(){if(remoteTypingTimer){clearTimeout(remoteTypingTimer);remoteTypingTimer=null}var el=document.querySelector('.chatHeaderSub');if(el)el.textContent=activeChatBaseSub||''}
function stopActiveChatRealtime(){resetRemoteTyping();if(activeChatChannel){try{sb.removeChannel(activeChatChannel)}catch(e){}activeChatChannel=null}activeChatTopic=null;activeChatViewer=null}
function showRemoteTyping(evt){var payload=evt&&evt.payload?evt.payload:evt;if(!payload||!activeChatViewer||payload.actor===activeChatViewer)return;var el=document.querySelector('.chatHeaderSub');if(!el)return;if(payload.typing){el.textContent='écrit…';if(remoteTypingTimer)clearTimeout(remoteTypingTimer);remoteTypingTimer=setTimeout(resetRemoteTyping,1900)}else resetRemoteTyping()}
function activeChatReload(){if(activeChatViewer==='owner')scheduleRealtimeReload();else scheduleLibraryReload()}
function startActiveChatRealtime(topic,viewer){if(!topic||!sb||!sb.channel)return;if(activeChatChannel&&activeChatTopic===topic&&activeChatViewer===viewer)return;stopActiveChatRealtime();activeChatTopic=topic;activeChatViewer=viewer;activeChatChannel=sb.channel(topic).on('broadcast',{event:'message'},function(){activeChatReload()}).on('broadcast',{event:'read'},function(){activeChatReload()}).on('broadcast',{event:'typing'},showRemoteTyping).subscribe()}
async function sendTypingState(value){if(!chatId)return;try{await rpc('anonbox_set_typing',{p_conversation_id:chatId,p_device_id:deviceId(),p_typing:!!value})}catch(e){}}
function handleComposerTyping(){autoGrowComposer();if(!chatId)return;if(!typingThrottleTimer){sendTypingState(true);typingThrottleTimer=setTimeout(function(){typingThrottleTimer=null},650)}if(typingStopTimer)clearTimeout(typingStopTimer);typingStopTimer=setTimeout(function(){typingStopTimer=null;sendTypingState(false)},1350)}
async function rpc"""
replace_once(marker, insert, 'realtime helpers')

replace_once(
    "$('chatInput').addEventListener('input',autoGrowComposer);",
    "$('chatInput').addEventListener('input',handleComposerTyping);$('chatInput').addEventListener('blur',function(){sendTypingState(false)});",
    'composer typing binding',
)

replace_once(
    "libraryConversations=Array.isArray(list)?list:[];if(chatId)renderVisitorChat();else renderLibraryList()",
    "libraryConversations=Array.isArray(list)?list:[];if(chatId)renderVisitorChat();else{renderLibraryList();startLibraryRealtime()}",
    'library realtime subscription',
)

replace_once(
    "renderHeader(owner.pseudonym||c.title||'Boîte',threadMode==='profile'?'Conversation avec mon profil':'Conversation anonyme',owner.avatar_url,false);",
    "renderHeader(owner.pseudonym||c.title||'Boîte',threadMode==='profile'?'Conversation avec mon profil':'Conversation anonyme',owner.avatar_url,false);startActiveChatRealtime(c.realtime_topic,'visitor');",
    'visitor chat realtime',
)

replace_once(
    "renderHeader(info.name,info.profile?'Profil visible':'Conversation anonyme',info.avatar,!info.profile);",
    "renderHeader(info.name,info.profile?'Profil visible':'Conversation anonyme',info.avatar,!info.profile);var ownerTopic=null;try{ownerTopic=await rpc('anonbox_get_realtime_topic',{p_conversation_id:chatId,p_device_id:deviceId()})}catch(e){}startActiveChatRealtime(ownerTopic,'owner');",
    'owner chat realtime',
)

replace_once(
    "$('chatInput').value='';autoGrowComposer();await loadLibrary()",
    "$('chatInput').value='';autoGrowComposer();sendTypingState(false);await loadLibrary()",
    'visitor stop typing on send',
)

replace_once(
    "$('chatInput').value='';autoGrowComposer();await loadAll()",
    "$('chatInput').value='';autoGrowComposer();sendTypingState(false);await loadAll()",
    'owner stop typing on send',
)

replace_once(
    "window.addEventListener('beforeunload',function(){stopLibraryAutoRefresh()});",
    "window.addEventListener('beforeunload',function(){stopLibraryAutoRefresh();stopLibraryRealtime();stopActiveChatRealtime()});",
    'realtime cleanup',
)

INDEX.write_text(s, encoding='utf-8')

sw = SW.read_text(encoding='utf-8')
if "const CACHE='anonbox-v5';" not in sw:
    raise SystemExit('service worker cache marker not found')
sw = sw.replace("const CACHE='anonbox-v5';", "const CACHE='anonbox-v6';", 1)
SW.write_text(sw, encoding='utf-8')

print('Realtime chat frontend patch applied successfully')
