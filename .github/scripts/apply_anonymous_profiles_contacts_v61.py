from pathlib import Path

INDEX=Path('web/index.html')
SW=Path('web/sw.js')
VERSION=Path('web/version.txt')
html=INDEX.read_text(encoding='utf-8')
MARK='/* anonymous-profiles-contacts-v61 */'
if MARK in html:
    raise SystemExit(0)

html=html.replace(
'''<div id="contactsTab" class="tabPage hidden"><h2>Contacts</h2><p class="muted">Seuls ceux qui ont volontairement choisi « Mon profil » apparaissent ici. Les anonymes restent anonymes.</p><div id="contacts" class="stack"></div></div>''',
'''<div id="contactsTab" class="tabPage hidden"><h2>Profils</h2><p class="muted">Retrouve les profils visibles dans tes conversations. Un profil anonyme n’affiche qu’un pseudonyme et une image choisis pour AnonBox : son identité réelle reste masquée.</p><div id="contacts" class="stack"></div></div>''',1)

html=html.replace(
"if(conversationFilter==='profiles'&&!info.profile)return false;",
"if(conversationFilter==='profiles'&&!(info.profile||info.anonymousProfile))return false;",1)

html=html.replace(
"sender_mode,sender_user_id,sender_pseudonym_snapshot,sender_avatar_path_snapshot,created_at",
"sender_mode,sender_user_id,sender_pseudonym_snapshot,sender_avatar_path_snapshot,sender_fingerprint,created_at",1)

old="var contactMap={};visitorMessages.filter(function(x){return x.sender_mode==='profile'&&x.sender_user_id}).forEach(function(x){contactMap[x.sender_user_id]=x});var contacts=Object.keys(contactMap).map(function(k){return contactMap[k]});$('profileCount').textContent=String(contacts.length);"
new="var contactMap={};visitorMessages.forEach(function(x){if(x.sender_mode==='profile'&&x.sender_user_id)contactMap['account:'+x.sender_user_id]={message:x,anonymous:false};else if(x.sender_mode==='anonymous'&&x.sender_pseudonym_snapshot&&x.sender_fingerprint)contactMap['anon:'+x.sender_fingerprint]={message:x,anonymous:true}});var contacts=Object.keys(contactMap).map(function(k){return contactMap[k]});$('profileCount').textContent=String(contacts.length);"
if old not in html: raise SystemExit('contact map anchor missing')
html=html.replace(old,new,1)

old2="$('contacts').innerHTML=contacts.length?contacts.map(function(c){var av=avatarUrl(c.sender_avatar_path_snapshot);return '<div class=\"contact\">'+(av?'<img class=\"msgAvatar\" src=\"'+esc(av)+'\" alt=\"\">':'<div class=\"msgAvatar\">'+esc((c.sender_pseudonym_snapshot||'?').slice(0,2).toUpperCase())+'</div>')+'<div><b>'+esc(c.sender_pseudonym_snapshot||'Profil')+'</b><div class=\"small muted\">A choisi volontairement « Mon profil »</div></div></div>'}).join(''):'<div class=\"card muted\">Aucun expéditeur avec profil pour le moment.</div>';"
new2="$('contacts').innerHTML=contacts.length?contacts.map(function(item){var c=item.message,av=avatarUrl(c.sender_avatar_path_snapshot),label=item.anonymous?'🕶️ Profil anonyme · identité réelle masquée':'👤 Profil de compte';return '<div class=\"contact\">'+(av?'<img class=\"msgAvatar\" src=\"'+esc(av)+'\" alt=\"\">':'<div class=\"msgAvatar\">'+(item.anonymous?'🕶️':esc((c.sender_pseudonym_snapshot||'?').slice(0,2).toUpperCase()))+'</div>')+'<div><b>'+esc(c.sender_pseudonym_snapshot||'Profil')+'</b><div class=\"small muted\">'+label+'</div></div></div>'}).join(''):'<div class=\"card muted\">Aucun profil visible pour le moment.</div>';"
if old2 not in html: raise SystemExit('contacts render anchor missing')
html=html.replace(old2,new2,1)

html=html.replace('</style>', '''
    /* anonymous-profiles-contacts-v61 */
    #contacts .contact{align-items:center;padding:13px 14px;border-radius:17px}
    #contacts .contact>div:last-child{min-width:0;display:grid;gap:3px}
    #contacts .contact b{font-size:14px;color:#263245;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    #contacts .contact .small{font-size:10.5px;line-height:1.35}
  </style>''',1)

INDEX.write_text(html,encoding='utf-8')
sw=SW.read_text(encoding='utf-8').replace("const CACHE='anonbox-v14';","const CACHE='anonbox-v15';")
SW.write_text(sw,encoding='utf-8')
VERSION.write_text('AnonBox web UI v6.1\nLight interface by default\nAnonymous visitors: no profile, custom local anonymous profile, or generated anonymous profile with image\nAnonymous profiles are visible in the Profiles tab while real account identity remains hidden\nCache: anonbox-v15\n',encoding='utf-8')
