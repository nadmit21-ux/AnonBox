from pathlib import Path

INDEX = Path('web/index.html')
SW = Path('web/sw.js')
html = INDEX.read_text(encoding='utf-8')

MARKER = '/* anonbox-premium-ui-v1 */'

if MARKER not in html:
    css = r'''
    /* anonbox-premium-ui-v1 */
    :root{
      --bg:#0a1019;
      --panel:#111a27;
      --panel2:#0e1723;
      --text:#f4f7fb;
      --muted:#8e9bad;
      --line:rgba(148,163,184,.14);
      --brand:#7c5cff;
      --brand2:#31b6d8;
      --ok:#42d3a2;
      --bad:#ff758f;
      --composer:82px;
      --surface-soft:rgba(17,26,39,.78);
      --surface-raised:rgba(20,30,45,.94);
      --shadow-soft:0 10px 30px rgba(0,0,0,.16);
    }

    html,body{background:#0a1019}
    body{
      background:
        radial-gradient(circle at 18% -10%,rgba(124,92,255,.10),transparent 34%),
        radial-gradient(circle at 92% 0,rgba(49,182,216,.065),transparent 30%),
        #0a1019;
      color:var(--text);
      -webkit-font-smoothing:antialiased;
      text-rendering:optimizeLegibility;
      overscroll-behavior-y:none;
    }
    button,input,textarea{font-family:inherit}
    button{transition:transform .16s ease,background-color .16s ease,border-color .16s ease,opacity .16s ease}
    button:active{transform:scale(.97)}
    .shell{width:min(100%,760px);padding:18px 14px 108px}
    .brand{font-size:15px;letter-spacing:.1px;color:#dcd7ff}
    .brand i{width:9px;height:9px;box-shadow:0 0 16px rgba(124,92,255,.52)}

    .card{
      border:1px solid rgba(148,163,184,.11);
      background:linear-gradient(180deg,rgba(18,27,41,.88),rgba(13,21,33,.88));
      border-radius:20px;
      box-shadow:var(--shadow-soft);
    }
    input,textarea{
      border:1px solid rgba(148,163,184,.15);
      background:rgba(9,15,24,.82);
      border-radius:16px;
      color:#f6f8fb;
    }
    input:focus,textarea:focus{border-color:rgba(124,92,255,.62);box-shadow:0 0 0 3px rgba(124,92,255,.08)}

    /* App header */
    .messengerTop{
      margin:-18px -14px 18px;
      padding:calc(12px + env(safe-area-inset-top)) 16px 12px;
      background:linear-gradient(180deg,rgba(10,16,25,.985),rgba(10,16,25,.91));
      border-bottom:1px solid rgba(148,163,184,.08);
      backdrop-filter:blur(18px);
    }
    .topAvatar{
      width:42px;height:42px;
      background:linear-gradient(145deg,#6550d8,#147b94);
      border:1px solid rgba(255,255,255,.10);
      box-shadow:0 5px 16px rgba(0,0,0,.20);
    }
    .pageTitle{font-size:21px;font-weight:780;letter-spacing:-.45px}
    .topUserLine{font-size:11px;color:#7f8da0;max-width:220px}
    .iconButton{
      width:40px;height:40px;
      background:rgba(255,255,255,.045);
      border:1px solid rgba(148,163,184,.10);
      color:#c8d2df;
      box-shadow:none;
    }

    /* Discussion list */
    .sectionTitle{margin:2px 2px 14px;align-items:center}
    .sectionTitle h2{font-size:27px;font-weight:760;letter-spacing:-.75px}
    .sectionTitle p{font-size:12px;color:#7f8da0;margin-top:3px}
    .discussionTools,.libraryTools{gap:9px;margin:7px 0 13px}
    .searchBox{
      height:45px;
      border:1px solid rgba(148,163,184,.10);
      background:rgba(255,255,255,.045);
      border-radius:15px;
      padding:0 13px;
      box-shadow:none;
    }
    .searchBox span{font-size:18px;color:#7e8ca0}
    .searchBox input{height:43px;color:#e9eef5;font-size:14px}
    .filterChips{gap:6px;padding:1px 1px 3px}
    .filterChip{
      padding:7px 12px;
      border-radius:999px;
      background:rgba(255,255,255,.035);
      border:1px solid rgba(148,163,184,.10);
      color:#8795a8;
      font-size:11px;
      font-weight:650;
    }
    .filterChip.active{
      background:rgba(124,92,255,.14);
      border-color:rgba(124,92,255,.34);
      color:#ddd8ff;
      box-shadow:inset 0 0 0 1px rgba(124,92,255,.04);
    }
    .messengerList{
      border:0;
      border-radius:18px;
      overflow:hidden;
      background:rgba(14,22,34,.58);
      box-shadow:inset 0 0 0 1px rgba(148,163,184,.07);
    }
    .messengerList .conversationList{background:transparent}
    .messengerList .conversationList:not(:last-child){border-bottom:1px solid rgba(148,163,184,.075)}
    .conversationList{border:0;border-radius:0;background:transparent;overflow:visible}
    .conversationList+.conversationList{margin-top:0}
    .chatRow{
      min-height:72px;
      gap:12px;
      padding:11px 13px;
      background:transparent;
    }
    .chatRow:hover{background:rgba(255,255,255,.025)}
    .chatRow:active{background:rgba(255,255,255,.052)}
    .chatRow.unread{background:linear-gradient(90deg,rgba(124,92,255,.075),transparent 70%)}
    .msgAvatar{
      width:50px;height:50px;
      border-radius:50%;
      background:linear-gradient(145deg,#28364a,#1b2636);
      border:1px solid rgba(255,255,255,.07);
      box-shadow:0 4px 14px rgba(0,0,0,.16);
      font-size:13px;
    }
    .chatRowTop{margin-bottom:5px;gap:8px}
    .chatRowName{font-size:15px;font-weight:760;letter-spacing:-.18px;color:#eef2f7}
    .chatRowTime{font-size:10.5px;color:#6f7c8d}
    .chatRow.unread .chatRowTime{color:#a99cff;font-weight:700}
    .chatRowBottom{gap:7px}
    .chatPreview{font-size:13px;color:#7f8da0;line-height:1.25}
    .chatRow.unread .chatPreview{color:#aeb9c7;font-weight:560}
    .chatMode{
      font-size:9.5px;
      color:#758296;
      background:rgba(255,255,255,.035);
      padding:3px 6px;
      border-radius:999px;
    }
    .chevron{display:none}
    .unreadBadge{
      min-width:20px;height:20px;padding:0 6px;
      background:#7259e8;
      box-shadow:0 2px 8px rgba(114,89,232,.30);
      font-size:10px;
    }

    /* Home cards */
    .stats{gap:8px}
    .stat{
      padding:13px 12px;
      border:1px solid rgba(148,163,184,.09);
      border-radius:17px;
      background:rgba(255,255,255,.032);
      box-shadow:none;
    }
    .stat b{font-size:24px;font-weight:760;letter-spacing:-.6px;margin-top:3px}
    #homeTab>div>h3{font-size:15px;font-weight:720;color:#d9e0ea;margin:5px 2px 10px}

    /* Bottom navigation */
    #dashboard{padding-bottom:88px}
    .nav{
      position:fixed;
      left:50%;
      transform:translateX(-50%);
      bottom:max(8px,env(safe-area-inset-bottom));
      width:min(calc(100% - 18px),730px);
      margin:0;
      padding:6px 7px;
      gap:3px;
      border:1px solid rgba(148,163,184,.12);
      background:rgba(13,21,32,.94);
      backdrop-filter:blur(22px);
      border-radius:24px;
      box-shadow:0 14px 40px rgba(0,0,0,.32);
      z-index:60;
    }
    .nav button{
      position:relative;
      min-height:50px;
      padding:5px 4px 4px;
      border-radius:18px;
      color:#718095;
      display:flex;
      flex-direction:column;
      align-items:center;
      justify-content:center;
      gap:2px;
      font-weight:600;
    }
    .nav button.active{
      background:rgba(124,92,255,.12);
      color:#d8d2ff;
      box-shadow:inset 0 0 0 1px rgba(124,92,255,.10);
    }
    .navIcon{font-size:18px;line-height:20px;filter:saturate(.72)}
    .navLabel{font-size:9.5px;letter-spacing:.02em}
    .navBadge{top:3px;right:20%;box-shadow:0 0 0 2px #101923}

    /* Full chat */
    .chatScreenShell{width:min(100%,760px);background:#0a1019;padding-bottom:calc(var(--composer) + 28px)}
    .chatScreenHeader{
      min-height:64px;
      padding:9px 10px;
      background:rgba(10,16,25,.94);
      border-bottom:1px solid rgba(148,163,184,.075);
      backdrop-filter:blur(20px);
    }
    .backBtn,.headerAction{
      width:40px;height:40px;
      background:transparent;
      border:0;
      color:#c9d3df;
      box-shadow:none;
    }
    .backBtn{font-size:29px;font-weight:300}
    .chatHeaderIdentity{gap:9px}
    .chatHeaderIdentity .msgAvatar{width:40px;height:40px}
    .chatHeaderName{font-size:15px;font-weight:740;letter-spacing:-.15px}
    .chatHeaderSub{font-size:10.5px;color:#778598;margin-top:1px}
    .chatScreenBody{
      gap:5px;
      padding:15px 11px 24px;
      background:
        radial-gradient(circle at 18% 8%,rgba(124,92,255,.045),transparent 25%),
        radial-gradient(circle at 88% 80%,rgba(49,182,216,.035),transparent 28%),
        #0a1019;
    }
    .dayPill{
      margin:5px 0 8px;
      padding:5px 9px;
      border:0;
      background:rgba(255,255,255,.045);
      color:#738195;
      font-size:9.5px;
      box-shadow:none;
    }
    .bubble{
      max-width:79%;
      padding:8px 10px 6px;
      border-radius:18px;
      line-height:1.39;
      font-size:14px;
      box-shadow:0 3px 9px rgba(0,0,0,.12);
      border:0;
    }
    .bubble.left{
      background:#172131;
      border:0;
      border-bottom-left-radius:6px;
    }
    .bubble.right{
      background:linear-gradient(135deg,#6652d5,#4c56b8 70%,#3e6d99);
      border:0;
      border-bottom-right-radius:6px;
    }
    .bubbleMeta{margin-top:3px;font-size:8.5px;color:rgba(210,220,232,.63)}
    .bubble.left .bubbleMeta{color:#718095}
    .readMark{color:#8fe4f5}
    .replyQuote{
      margin:0 0 6px;
      padding:6px 8px;
      border-left:2px solid rgba(196,181,253,.78);
      border-radius:8px;
      background:rgba(6,10,17,.22);
      color:#c3ccda;
      font-size:10.5px;
    }
    .reactionStrip{gap:4px;margin-top:5px}
    .reactionPill{
      padding:2px 6px;
      border:1px solid rgba(255,255,255,.09);
      background:rgba(7,12,20,.28);
      font-size:10.5px;
    }
    .attachmentCard{
      margin-top:5px;
      border:1px solid rgba(255,255,255,.08);
      background:rgba(6,10,17,.23);
      border-radius:13px;
      box-shadow:none;
    }

    /* Composer */
    .chatComposer{
      width:min(100%,760px);
      gap:7px;
      padding:8px 9px calc(8px + env(safe-area-inset-bottom));
      background:linear-gradient(180deg,rgba(10,16,25,0),rgba(10,16,25,.95) 22%,rgba(10,16,25,.995));
      border-top:0;
      backdrop-filter:none;
    }
    .chatComposer textarea{
      min-height:46px;
      border-radius:23px;
      padding:12px 15px;
      background:#151f2d;
      border:1px solid rgba(148,163,184,.10);
      box-shadow:0 4px 16px rgba(0,0,0,.14);
      font-size:14px;
    }
    .attachButton,.sendCircle{
      width:44px;height:44px;flex:0 0 44px;
      border-radius:50%;
      border:1px solid rgba(148,163,184,.10);
      box-shadow:0 4px 14px rgba(0,0,0,.16);
    }
    .attachButton{background:#151f2d;color:#aeb9c8;font-size:18px}
    .sendCircle{background:#7158e8;color:white;font-size:19px}
    .replyComposerBar{
      padding:7px 10px;
      border-left:2px solid #8e7cff;
      border-radius:12px;
      background:rgba(21,31,45,.96);
    }

    /* Action sheet */
    .actionBackdrop{background:rgba(3,7,12,.58);backdrop-filter:blur(4px)}
    .actionSheet{
      background:#111a27;
      border:1px solid rgba(148,163,184,.12);
      border-radius:26px 26px 20px 20px;
      padding:12px 12px 14px;
      box-shadow:0 -20px 55px rgba(0,0,0,.38);
    }
    .actionPreview{background:rgba(255,255,255,.035);border-radius:13px;color:#aab6c5}
    .reactionPicker button,.actionGrid button,.forwardTarget{
      background:rgba(255,255,255,.04);
      border:1px solid rgba(148,163,184,.09);
    }

    /* Visitor library */
    .libraryTop{margin:10px 2px 13px;align-items:center}
    .libraryTop h1{font-size:25px;font-weight:760;letter-spacing:-.6px}
    #libraryRefresh{width:40px;height:40px;padding:0;border-radius:50%;font-size:18px}
    .librarySummary{padding:0 3px;color:#718095}

    /* Subtle motion */
    .tabPage:not(.hidden){animation:anonboxPageIn .18s ease-out}
    .chatRow{animation:anonboxRowIn .20s ease-out both}
    .bubble{animation:anonboxBubbleIn .14s ease-out both}
    @keyframes anonboxPageIn{from{opacity:.35;transform:translateY(3px)}to{opacity:1;transform:none}}
    @keyframes anonboxRowIn{from{opacity:.25;transform:translateY(2px)}to{opacity:1;transform:none}}
    @keyframes anonboxBubbleIn{from{opacity:.25;transform:translateY(2px) scale(.99)}to{opacity:1;transform:none}}
    @media (prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}

    @media (max-width:520px){
      .shell{padding-left:10px;padding-right:10px}
      .messengerTop{margin-left:-10px;margin-right:-10px}
      .sectionTitle h2{font-size:25px}
      .chatRow{padding-left:10px;padding-right:10px}
      .msgAvatar{width:48px;height:48px}
      .chatMode{display:none}
      .bubble{max-width:84%;font-size:13.8px}
      .nav{width:calc(100% - 12px)}
    }
    '''
    if '</style>' not in html:
        raise SystemExit('style closing tag not found')
    html = html.replace('</style>', css + '\n  </style>', 1)

# Softer system chrome and concise mobile affordances.
html = html.replace('<meta name="theme-color" content="#070a12">', '<meta name="theme-color" content="#0a1019">', 1)
html = html.replace('<button id="libraryRefresh" class="secondary">Actualiser</button>', '<button id="libraryRefresh" class="secondary" aria-label="Actualiser">↻</button>', 1)
html = html.replace('<button id="chatSendBtn" class="sendCircle" aria-label="Envoyer">➤</button>', '<button id="chatSendBtn" class="sendCircle" aria-label="Envoyer">↑</button>', 1)

INDEX.write_text(html, encoding='utf-8')

sw = SW.read_text(encoding='utf-8')
if "const CACHE='anonbox-v8';" in sw:
    sw = sw.replace("const CACHE='anonbox-v8';", "const CACHE='anonbox-v9';", 1)
elif "const CACHE='anonbox-v9';" not in sw:
    raise SystemExit('unexpected service worker cache version')
SW.write_text(sw, encoding='utf-8')

print('AnonBox premium UI refactor v1 applied')
