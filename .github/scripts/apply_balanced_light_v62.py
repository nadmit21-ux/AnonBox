from pathlib import Path

INDEX=Path('web/index.html')
SW=Path('web/sw.js')
VERSION=Path('web/version.txt')
html=INDEX.read_text(encoding='utf-8')
MARK='/* anonbox-balanced-light-v62 */'
if MARK in html:
    raise SystemExit(0)

html=html.replace('<meta name="theme-color" content="#f6f8fc">','<meta name="theme-color" content="#e9eef5">',1)

css=r'''
    /* anonbox-balanced-light-v62 */
    :root{--bg:#e9eef5;--panel:#f5f7fa;--panel2:#edf1f6;--surface-soft:#eef2f7;--surface-raised:#f8fafc;--line:rgba(41,55,76,.14);--text:#1f2a3b;--muted:#68778a;--shadow-soft:0 10px 28px rgba(44,58,80,.10)}
    html{background:#e9eef5!important}
    body{background:radial-gradient(circle at 8% -8%,rgba(111,92,232,.13),transparent 31%),radial-gradient(circle at 100% 4%,rgba(51,153,191,.10),transparent 27%),#e9eef5!important}
    .shell{background:transparent}
    .card{background:#f5f7fa!important;border-color:rgba(41,55,76,.12)!important;box-shadow:0 10px 26px rgba(44,58,80,.08)!important}
    .tag{background:#f1f4f8!important}
    input,textarea{background:#eef2f6!important;border-color:rgba(41,55,76,.13)!important}
    button.ghost{background:#f3f5f8!important}button.secondary{background:#e7e9fb!important}
    .tabs{background:#e4e9f0!important}.tabs button.active{background:#f7f8fb!important}
    #publicView .hero,#authView .hero{background:linear-gradient(145deg,#f3f1fb,#eaf0f6)!important;border-color:rgba(92,75,187,.13)!important;box-shadow:0 13px 30px rgba(44,58,80,.08)!important}
    #publicBox>.card:not(.stack),#publicLibrary{background:#f2f5f8!important}
    #messageBody{background:#eef2f6!important}
    .anonIdentityPanel{background:linear-gradient(145deg,#eeebfa,#eaf1f6)!important;border-color:rgba(103,88,232,.16)!important}
    .anonProfileAvatar{background:#e2def8!important}.anonProfileEditor input[type=file]{background:#eef2f6!important}
    .messengerTop{background:rgba(239,243,248,.96)!important;border-bottom-color:rgba(41,55,76,.10)!important;box-shadow:0 5px 18px rgba(44,58,80,.07)!important}
    .iconButton{background:#e5eaf0!important}.searchBox{background:#f3f5f8!important}.filterChip{background:#edf1f5!important}.filterChip.active{background:#e3defa!important}
    .messengerList{background:#f3f5f8!important;box-shadow:inset 0 0 0 1px rgba(41,55,76,.08)!important}
    .chatRow:hover,.chatRow:active{background:#e9edf3!important}.chatRow.unread{background:linear-gradient(90deg,rgba(103,88,232,.10),rgba(239,243,248,.72) 70%)!important}
    .stat,.contact{background:#f2f5f8!important;border-color:rgba(41,55,76,.11)!important}
    .logoPreview{background:#e8edf3!important}
    .nav{background:rgba(237,241,246,.97)!important;border-color:rgba(41,55,76,.13)!important;box-shadow:0 12px 30px rgba(44,58,80,.13)!important}.nav button.active{background:#e2def8!important}.navBadge{box-shadow:0 0 0 2px #edf1f6!important}
    .chatScreenShell{background:#e9eef5!important}.chatScreenHeader{background:rgba(239,243,248,.97)!important;border-bottom-color:rgba(41,55,76,.10)!important}.headerAction{background:#e4e9ef!important}.msgAvatar{background:linear-gradient(145deg,#e7ebf1,#dde3eb)!important}
    .chatScreenBody{background:radial-gradient(circle at 12% 2%,rgba(103,88,232,.08),transparent 25%),radial-gradient(circle at 90% 90%,rgba(45,156,194,.06),transparent 28%),#e7ecf3!important}
    .dayPill{background:#edf1f5!important}.bubble.left{background:#f3f5f8!important;border-color:rgba(41,55,76,.10)!important;box-shadow:0 4px 13px rgba(44,58,80,.07)!important}.bubble.right{background:#ded9f8!important;border-color:#cfc8f3!important;box-shadow:0 4px 13px rgba(90,78,170,.10)!important}
    .replyQuote{background:rgba(239,243,248,.78)!important}.reactionPill{background:#edf1f5!important}
    .chatComposer{background:linear-gradient(180deg,rgba(231,236,243,0),rgba(231,236,243,.94) 22%,#e7ecf3)!important}.chatComposer textarea{background:#f2f5f8!important}.attachButton{background:#edf1f5!important}.replyComposerBar{background:#edf1f5!important}
    .actionSheet{background:#eef2f6!important}.actionPreview,.reactionPicker button,.actionGrid button,.forwardTarget{background:#e5eaf0!important}.conversationMenuInfo{background:#e7ebf0!important}.attachmentCard{background:rgba(238,242,246,.92)!important}
    .chatScrollToBottom{background:#eef2f6!important}
    @media(max-width:520px){body{background:#e9eef5!important}.shell{padding-left:12px;padding-right:12px}.card{box-shadow:0 7px 20px rgba(44,58,80,.07)!important}}
'''
html=html.replace('</style>',css+'\n  </style>',1)
INDEX.write_text(html,encoding='utf-8')

sw=SW.read_text(encoding='utf-8').replace("const CACHE='anonbox-v15';","const CACHE='anonbox-v16';")
SW.write_text(sw,encoding='utf-8')
VERSION.write_text('AnonBox web UI v6.2\nBalanced light interface: blue-gray background, off-white surfaces, softer contrast\nAnonymous profile features unchanged\nCache: anonbox-v16\n',encoding='utf-8')
