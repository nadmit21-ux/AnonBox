from pathlib import Path

INDEX=Path('web/index.html')
SW=Path('web/sw.js')
html=INDEX.read_text(encoding='utf-8')
MARK='/* anonbox-premium-ui-v3 */'

if MARK not in html:
    css=r'''
    /* anonbox-premium-ui-v3 */
    /* Library */
    #libraryView{max-width:720px;margin:0 auto;padding-bottom:30px}
    .libraryTop{margin:16px 0 12px;align-items:center}
    .libraryTop>div{min-width:0}
    .libraryTop .tag{padding:5px 9px;font-size:10px;background:rgba(124,92,255,.07);border-color:rgba(124,92,255,.14);color:#c8c2ff}
    .libraryTop h1{font-size:28px;letter-spacing:-1px;font-weight:760;margin-top:6px}
    #libraryRefresh{width:42px;height:42px;min-width:42px;padding:0;border-radius:50%;font-size:0;background:rgba(255,255,255,.04);border:1px solid rgba(148,163,184,.10)}
    #libraryRefresh:after{content:'↻';font-size:18px;color:#b6c1cf}
    #libraryView>p.muted{font-size:12.5px;line-height:1.55;margin:0 2px 14px;color:#788699}
    .librarySummary{padding:0 2px;font-size:10.5px;color:#687688}
    #libraryList{margin-top:3px}
    #libraryView>.actions{gap:7px;margin-top:12px!important}
    #libraryHome,#libraryOwnerApp{min-height:44px;border-radius:15px;font-size:12px}

    /* Profiles */
    #contactsTab>h2,#settingsTab>h2{font-size:27px;letter-spacing:-.8px;margin:4px 2px 6px;font-weight:760}
    #contactsTab>p{font-size:12.5px;line-height:1.55;margin:0 2px 14px;color:#788699}
    #contacts{gap:0!important;border-radius:18px;overflow:hidden;background:rgba(14,22,34,.52);box-shadow:inset 0 0 0 1px rgba(148,163,184,.065)}
    .contact{border:0;border-radius:0;background:transparent;padding:12px 13px;min-height:70px}
    .contact:not(:last-child){border-bottom:1px solid rgba(148,163,184,.07)}
    .contact b{font-size:14px;font-weight:740;color:#eef2f7}
    .contact .small{font-size:10.5px;color:#748296;margin-top:2px}
    .contact .msgAvatar{width:46px;height:46px}

    /* Settings */
    #settingsTab{padding-bottom:12px}
    #settingsTab>.card{
      margin-top:12px;
      padding:14px;
      gap:12px;
      border-radius:20px;
      background:rgba(15,24,36,.70);
      border:1px solid rgba(148,163,184,.09);
      box-shadow:none;
    }
    .settingGrid label{gap:6px;font-size:11px;font-weight:650;color:#8492a5;letter-spacing:.01em}
    .settingGrid input:not([type=checkbox]),.settingGrid textarea{font-size:14px;background:#0c141f;border-color:rgba(148,163,184,.10);border-radius:14px}
    .settingGrid input:not([type=checkbox]){height:46px}
    .settingGrid textarea{padding:12px 13px}
    .settingGrid input[type=file]{height:auto;padding:11px;font-size:11px;color:#8795a7}
    .logoPreview{width:76px;height:76px;border-radius:20px;border-color:rgba(148,163,184,.12)}
    .settingGrid label:has(input[type=checkbox]){
      display:flex;
      align-items:center;
      min-height:45px;
      padding:0 12px;
      border-radius:14px;
      background:rgba(255,255,255,.025);
      border:1px solid rgba(148,163,184,.075);
      color:#aab5c3;
    }
    .settingGrid input[type=checkbox]{accent-color:#7158e8;width:17px!important;height:17px;margin-right:8px}
    #saveSettings{min-height:48px;border-radius:15px;background:#7158e8;margin-top:2px}
    #logout{min-height:45px;border-radius:15px;background:rgba(255,117,143,.065);border-color:rgba(255,117,143,.16);color:#ffb6c4}

    /* Message actions refinement */
    .actionSheet{max-height:82vh;overflow:auto}
    .actionPreview{border-radius:12px;background:rgba(255,255,255,.03);color:#9eabba;border:1px solid rgba(148,163,184,.06)}
    .reactionPicker{gap:4px;justify-content:center}
    .reactionPicker button{width:43px;height:43px;background:rgba(255,255,255,.035);border-color:rgba(148,163,184,.08);transition:transform .14s ease,background .14s ease}
    .reactionPicker button:active{transform:scale(.9)}
    .actionGrid{gap:7px}
    .actionGrid button{min-height:45px;border-radius:14px;background:rgba(255,255,255,.032);border-color:rgba(148,163,184,.08);font-size:12px;font-weight:650}
    .forwardTarget{min-height:47px;border-radius:14px;background:rgba(255,255,255,.03);border-color:rgba(148,163,184,.08);font-size:12px}

    /* Attachment and reply details */
    .attachmentInfo{gap:1px}
    .attachmentName{font-size:12px;font-weight:700}
    .attachmentMeta{font-size:9.5px;color:#718095}
    .attachmentThumb{width:38px;height:38px;border-radius:10px}
    .replyComposerClose{border-color:rgba(148,163,184,.09);color:#94a2b4}

    /* Smooth interaction feedback */
    .conversationList,.contact,.card,.stat{transition:background-color .15s ease,border-color .15s ease,transform .15s ease}
    .chatRow,.contact{touch-action:manipulation}
    @media(hover:hover){
      .stat:hover{background:rgba(255,255,255,.045);border-color:rgba(148,163,184,.13)}
      .contact:hover{background:rgba(255,255,255,.025)}
      .actionGrid button:hover,.reactionPicker button:hover{background:rgba(255,255,255,.06)}
    }

    /* Better empty/error states */
    #newMessages>.card.muted,#contacts>.card.muted{
      margin:0;
      border:0;
      border-radius:18px;
      background:rgba(255,255,255,.018);
      box-shadow:none;
      color:#718095;
      text-align:center;
      padding:28px 15px;
      font-size:12px;
    }
    .chatError{margin:12px;border-radius:14px}

    /* Footer */
    .footer{padding:18px 4px 8px;color:#536174;font-size:10px;line-height:1.45}
    #dashboard~.footer{display:none}

    /* Mobile behavior */
    @media(max-width:620px){
      body{background:#0a1019}
      .shell{padding-left:12px;padding-right:12px}
      .libraryTop{flex-direction:row;align-items:center}
      .libraryTop button{width:42px}
      .settingGrid label:has(input[type=checkbox]){padding:0 10px}
      .actionBackdrop{padding:0;align-items:flex-end}
      .actionSheet{width:100%;border-radius:25px 25px 0 0;border-left:0;border-right:0;border-bottom:0;padding-bottom:calc(14px + env(safe-area-inset-bottom))}
    }
    @media(max-width:430px){
      .shell{padding-bottom:102px}
      .messengerTop{padding-left:12px;padding-right:12px}
      .topActions{gap:4px}
      .iconButton{width:38px;height:38px}
      .pageTitle{font-size:20px}
      .nav{width:calc(100% - 12px);bottom:max(5px,env(safe-area-inset-bottom));border-radius:22px}
      .nav button{min-height:48px}
      .chatScreenBody{padding-left:9px;padding-right:9px}
      .bubble{max-width:87%;font-size:13.7px}
      .chatComposer{padding-left:7px;padding-right:7px}
      .chatComposer textarea{padding-left:13px;padding-right:13px}
      #contactsTab>h2,#settingsTab>h2,.libraryTop h1{font-size:25px}
    }
    @media(max-width:350px){
      .navLabel{font-size:8.5px}
      .navIcon{font-size:17px}
      .reactionPicker button{width:39px;height:39px;font-size:18px}
      .actionGrid{grid-template-columns:1fr}
    }

    /* Respect accessibility preferences */
    @media(prefers-reduced-motion:reduce){
      *,*:before,*:after{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important;scroll-behavior:auto!important}
    }
    '''
    html=html.replace('</style>',css+'\n  </style>',1)
    INDEX.write_text(html,encoding='utf-8')

sw=SW.read_text(encoding='utf-8')
for old in ["const CACHE='anonbox-v10';","const CACHE='anonbox-v11';"]:
    if old in sw:
        sw=sw.replace(old,"const CACHE='anonbox-v11';",1)
        break
SW.write_text(sw,encoding='utf-8')
print('Premium UI v3 applied')
