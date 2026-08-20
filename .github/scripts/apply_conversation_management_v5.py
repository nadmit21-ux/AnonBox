from pathlib import Path

INDEX = Path('web/index.html')
SW = Path('web/sw.js')
VERSION = Path('web/version.txt')
html = INDEX.read_text(encoding='utf-8')
marker = '/* conversation-management-v5 */'

if marker in html:
    print('Conversation management v5 already present')
    raise SystemExit(0)


def replace_once(old, new, label):
    global html
    count = html.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    html = html.replace(old, new, 1)

css = r'''
    /* conversation-management-v5 */
    .conversationFlags{display:inline-flex;align-items:center;gap:3px;font-size:10px;color:#8e9bad;white-space:nowrap}.conversationMenuInfo{padding:10px 12px;margin-bottom:10px;border-radius:14px;background:rgba(255,255,255,.035);border:1px solid rgba(148,163,184,.09)}.conversationMenuInfo b{display:block;font-size:13px;color:#edf2f7}.conversationMenuInfo span{display:block;margin-top:3px;font-size:10px;color:#7e8ca0}.conversationMenuState{display:inline-flex;gap:5px;flex-wrap:wrap;margin-top:7px}.conversationStatePill{padding:4px 7px;border-radius:999px;background:rgba(124,92,255,.10);border:1px solid rgba(124,92,255,.17);font-size:9px;color:#bbb2ff}.filterChip[data-filter="archived"]{margin-right:2px}
'''
replace_once('</style>', css + '\n  </style>', 'append conversation management styles')

replace_once(
    "conversationSearch='',conversationFilter='all',librarySearch='',",
    "conversationSearch='',conversationFilter='all',conversationPrefs={},librarySearch='',",
    'conversation preference state',
)

replace_once(
    '<button class="filterChip" data-filter="anonymous">Anonymes</button>',
    '<button class="filterChip" data-filter="anonymous">Anonymes</button><button class="filterChip" data-filter="archived">Archivées</button>',
    'archived filter chip',
)

old_match = "function ownerConversationMatches(c){var info=conversationIdentity(c);if(conversationFilter==='unread'&&!info.unread)return false;if(conversationFilter==='profiles'&&!info.profile)return false;if(conversationFilter==='anonymous'&&info.profile)return false;var q=normaliseText(conversationSearch.trim());if(!q)return true;var text=info.name+' '+c.messages.map(function(m){return m.body||''}).join(' ');return normaliseText(text).indexOf(q)>=0}"
new_match = "function ownerConversationMatches(c){var info=conversationIdentity(c),pref=prefFor(c.id),archived=!!pref.archived_at;if(conversationFilter==='archived'){if(!archived)return false}else if(archived)return false;if(conversationFilter==='unread'&&!info.unread)return false;if(conversationFilter==='profiles'&&!info.profile)return false;if(conversationFilter==='anonymous'&&info.profile)return false;var q=normaliseText(conversationSearch.trim());if(!q)return true;var text=info.name+' '+c.messages.map(function(m){return m.body||''}).join(' ');return normaliseText(text).indexOf(q)>=0}"
replace_once(old_match, new_match, 'archive-aware conversation matching')

helpers_marker = "function libraryConversationMatches(c){"
helpers = r'''function prefFor(id){return conversationPrefs[String(id)]||{}}
function isPrefMuted(pref){if(!pref||!pref.muted_until)return false;return new Date(pref.muted_until).getTime()>Date.now()}
function conversationFlagsHtml(id){var p=prefFor(id),out='';if(p.pinned_at)out+='📌';if(isPrefMuted(p))out+=(out?' ':'')+'🔕';return out?'<span class="conversationFlags">'+out+'</span>':''}
async function saveConversationPref(id,changes){if(!session||!session.user)throw new Error('Session requise.');var current=prefFor(id),row={owner_id:session.user.id,conversation_id:id,pinned_at:current.pinned_at||null,archived_at:current.archived_at||null,muted_until:current.muted_until||null,updated_at:new Date().toISOString()};Object.keys(changes||{}).forEach(function(k){row[k]=changes[k]});var r=await sb.from('anonbox_conversation_preferences').upsert(row,{onConflict:'owner_id,conversation_id'}).select('conversation_id,pinned_at,archived_at,muted_until,updated_at').single();if(r.error)throw r.error;conversationPrefs[String(id)]=r.data||row;return conversationPrefs[String(id)]}
function ensureConversationMenu(){if($('conversationSettingsBackdrop'))return;var d=document.createElement('div');d.id='conversationSettingsBackdrop';d.className='actionBackdrop hidden';d.innerHTML='<div class="actionSheet" role="dialog" aria-modal="true"><div class="actionHandle"></div><div id="conversationMenuInfo" class="conversationMenuInfo"></div><div class="actionGrid"><button id="conversationPinAction" type="button"></button><button id="conversationMuteAction" type="button"></button><button id="conversationArchiveAction" type="button"></button><button id="conversationCloseAction" type="button">Fermer</button></div></div>';document.body.appendChild(d);d.onclick=function(e){if(e.target===d)closeConversationSettings()};$('conversationCloseAction').onclick=closeConversationSettings}
function closeConversationSettings(){var d=$('conversationSettingsBackdrop');if(d)d.classList.add('hidden')}
function openConversationSettings(id,info){ensureConversationMenu();var p=prefFor(id),muted=isPrefMuted(p),states=[];if(p.pinned_at)states.push('Épinglée');if(muted)states.push('Silencieuse');if(p.archived_at)states.push('Archivée');$('conversationMenuInfo').innerHTML='<b>'+esc((info&&info.name)||'Conversation')+'</b><span>Gère cette discussion sans révéler l’identité d’un expéditeur anonyme.</span>'+(states.length?'<div class="conversationMenuState">'+states.map(function(s){return '<span class="conversationStatePill">'+esc(s)+'</span>'}).join('')+'</div>':'');$('conversationPinAction').textContent=p.pinned_at?'📌 Désépingler':'📌 Épingler';$('conversationMuteAction').textContent=muted?'🔔 Réactiver les notifications':'🔕 Mettre en sourdine';$('conversationArchiveAction').textContent=p.archived_at?'↩ Restaurer':'🗄 Archiver';$('conversationPinAction').onclick=async function(){try{await saveConversationPref(id,{pinned_at:p.pinned_at?null:new Date().toISOString()});closeConversationSettings();showToast(p.pinned_at?'Conversation désépinglée':'Conversation épinglée ✓','ok')}catch(e){showToast(e.message||'Modification impossible.','err')}};$('conversationMuteAction').onclick=async function(){try{await saveConversationPref(id,{muted_until:muted?null:'2100-01-01T00:00:00.000Z'});closeConversationSettings();showToast(muted?'Notifications réactivées ✓':'Conversation mise en sourdine ✓','ok')}catch(e){showToast(e.message||'Modification impossible.','err')}};$('conversationArchiveAction').onclick=async function(){try{var archiving=!p.archived_at;await saveConversationPref(id,{archived_at:archiving?new Date().toISOString():null});closeConversationSettings();showToast(archiving?'Conversation archivée ✓':'Conversation restaurée ✓','ok');if(archiving)setTimeout(function(){goto(BASE+'?app=1&tab=messages')},350)}catch(e){showToast(e.message||'Modification impossible.','err')}};$('conversationSettingsBackdrop').classList.remove('hidden')}
'''
replace_once(helpers_marker, helpers + helpers_marker, 'insert preference helpers')

old_load = "async function loadAll(){var uid=session.user.id,p=await sb.from('anonbox_profiles').select('user_id,display_name,pseudonym,handle,avatar_path,bio').eq('user_id',uid).maybeSingle(),b=await sb.from('anonbox_boxes').select('id,slug,title,welcome_message,is_open,allow_anonymous,allow_profile_messages').eq('owner_id',uid).maybeSingle(),m=await sb.from('anonbox_messages_v2').select('id,conversation_id,direction,body,sender_mode,sender_user_id,sender_pseudonym_snapshot,sender_avatar_path_snapshot,created_at,read_at,deleted_at,reply_to_id,reaction_summary,attachment_id,attachment_name,attachment_mime,attachment_size').is('deleted_at',null).order('created_at',{ascending:true}).limit(500);if(p.error||b.error||m.error||!p.data||!b.data){"
new_load = "async function loadAll(){var uid=session.user.id,p=await sb.from('anonbox_profiles').select('user_id,display_name,pseudonym,handle,avatar_path,bio').eq('user_id',uid).maybeSingle(),b=await sb.from('anonbox_boxes').select('id,slug,title,welcome_message,is_open,allow_anonymous,allow_profile_messages').eq('owner_id',uid).maybeSingle(),m=await sb.from('anonbox_messages_v2').select('id,conversation_id,direction,body,sender_mode,sender_user_id,sender_pseudonym_snapshot,sender_avatar_path_snapshot,created_at,read_at,deleted_at,reply_to_id,reaction_summary,attachment_id,attachment_name,attachment_mime,attachment_size').is('deleted_at',null).order('created_at',{ascending:true}).limit(500),pr=await sb.from('anonbox_conversation_preferences').select('conversation_id,pinned_at,archived_at,muted_until,updated_at').eq('owner_id',uid);if(p.error||b.error||m.error||!p.data||!b.data){"
replace_once(old_load, new_load, 'load owner conversation preferences')

replace_once(
    "profile=p.data;box=b.data;messages=m.data||[];startOwnerRealtime();",
    "profile=p.data;box=b.data;messages=m.data||[];conversationPrefs={};if(!pr.error)(pr.data||[]).forEach(function(x){conversationPrefs[String(x.conversation_id)]=x});startOwnerRealtime();",
    'store owner preferences',
)

replace_once(
    "return Object.keys(map).map(function(k){return map[k]}).sort(function(a,b){return new Date(b.lastAt)-new Date(a.lastAt)})",
    "return Object.keys(map).map(function(k){return map[k]}).sort(function(a,b){var pa=prefFor(a.id),pb=prefFor(b.id),ap=!!pa.pinned_at,bp=!!pb.pinned_at;if(ap!==bp)return ap?-1:1;return new Date(b.lastAt)-new Date(a.lastAt)})",
    'sort pinned conversations first',
)

old_render = "function renderOwnerConversation(c){var info=conversationIdentity(c),last=c.messages[c.messages.length-1],preview=(last&&last.direction==='owner'?'Vous : ':'')+previewText(last&&last.body||'Aucun message');return '<article class=\"conversationList\"><button class=\"chatRow ownerConversationRow '+(info.unread?'unread':'')+'\" data-id=\"'+esc(c.id)+'\"><div>'+(info.avatar?'<img class=\"msgAvatar\" src=\"'+esc(info.avatar)+'\" alt=\"\">':'<div class=\"msgAvatar\">'+(info.profile?esc(info.name.slice(0,2).toUpperCase()):'🕶️')+'</div>')+'</div><div class=\"chatRowMain\"><div class=\"chatRowTop\"><span class=\"chatRowName\">'+esc(info.name)+'</span><span class=\"chatRowTime\">'+esc(timeLabel(c.lastAt))+'</span></div><div class=\"chatRowBottom\"><span class=\"chatPreview\">'+esc(preview)+'</span><span class=\"chatMode\">'+(info.profile?'👤 Profil':'🕶️ Anonyme')+'</span>'+(info.unreadCount?'<span class=\"unreadBadge\">'+info.unreadCount+'</span>':'')+'<span class=\"chevron\">›</span></div></div></button></article>'}"
new_render = "function renderOwnerConversation(c){var info=conversationIdentity(c),last=c.messages[c.messages.length-1],preview=(last&&last.direction==='owner'?'Vous : ':'')+previewText(last&&last.body||'Aucun message'),flags=conversationFlagsHtml(c.id);return '<article class=\"conversationList\"><button class=\"chatRow ownerConversationRow '+(info.unread?'unread':'')+'\" data-id=\"'+esc(c.id)+'\"><div>'+(info.avatar?'<img class=\"msgAvatar\" src=\"'+esc(info.avatar)+'\" alt=\"\">':'<div class=\"msgAvatar\">'+(info.profile?esc(info.name.slice(0,2).toUpperCase()):'🕶️')+'</div>')+'</div><div class=\"chatRowMain\"><div class=\"chatRowTop\"><span class=\"chatRowName\">'+esc(info.name)+'</span>'+flags+'<span class=\"chatRowTime\">'+esc(timeLabel(c.lastAt))+'</span></div><div class=\"chatRowBottom\"><span class=\"chatPreview\">'+esc(preview)+'</span><span class=\"chatMode\">'+(info.profile?'👤 Profil':'🕶️ Anonyme')+'</span>'+(info.unreadCount?'<span class=\"unreadBadge\">'+info.unreadCount+'</span>':'')+'<span class=\"chevron\">›</span></div></div></button></article>'}"
replace_once(old_render, new_render, 'show pin and mute flags')

old_dashboard_start = "function renderDashboard(){var visitorMessages=messages.filter(function(x){return x.direction==='visitor'}),convs=groupConversations(),unreadTotal=visitorMessages.filter(function(x){return !x.read_at}).length;"
new_dashboard_start = "function renderDashboard(){var visitorMessages=messages.filter(function(x){return x.direction==='visitor'}),convs=groupConversations(),unreadTotal=convs.filter(function(c){return !prefFor(c.id).archived_at}).reduce(function(n,c){return n+conversationIdentity(c).unreadCount},0);"
replace_once(old_dashboard_start, new_dashboard_start, 'exclude archived from primary unread count')

replace_once(
    "var newConvs=convs.filter(function(c){return conversationIdentity(c).unread}),filteredConvs=convs.filter(ownerConversationMatches);",
    "var newConvs=convs.filter(function(c){return conversationIdentity(c).unread&&!prefFor(c.id).archived_at}),filteredConvs=convs.filter(ownerConversationMatches);",
    'hide archived conversations from home new list',
)

replace_once(
    "$('chatHeaderAction').onclick=function(){goto(BASE+'?app=1&tab=messages')};$('chatSendBtn').onclick=async function(){",
    "$('chatHeaderAction').onclick=function(){openConversationSettings(chatId,info)};$('chatSendBtn').onclick=async function(){",
    'real owner conversation menu',
)

INDEX.write_text(html, encoding='utf-8')
sw = SW.read_text(encoding='utf-8')
if "const CACHE='anonbox-v12';" not in sw:
    raise SystemExit('service worker v12 marker not found')
SW.write_text(sw.replace("const CACHE='anonbox-v12';", "const CACHE='anonbox-v13';", 1), encoding='utf-8')
VERSION.write_text('AnonBox web UI v5\nConversation management: pin, mute and archive\nMuted conversations skip Android push enqueue\nIncludes UX v4 scroll, unread, swipe-to-reply and in-app feedback\nCache: anonbox-v13\n', encoding='utf-8')
print('Conversation management v5 applied')
