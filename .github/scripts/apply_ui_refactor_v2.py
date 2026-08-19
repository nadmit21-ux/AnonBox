from pathlib import Path

INDEX=Path('web/index.html')
SW=Path('web/sw.js')
html=INDEX.read_text(encoding='utf-8')
MARK='/* anonbox-premium-ui-v2 */'

if MARK not in html:
    css=r'''
    /* anonbox-premium-ui-v2 */
    :root{
      --soft-border:rgba(148,163,184,.105);
      --soft-fill:rgba(255,255,255,.032);
      --soft-fill-hover:rgba(255,255,255,.052);
      --accent-soft:rgba(124,92,255,.12);
      --accent-border:rgba(124,92,255,.28);
    }

    /* Global polish */
    ::selection{background:rgba(124,92,255,.34);color:#fff}
    *{scrollbar-color:#314055 transparent;scrollbar-width:thin}
    button:focus-visible,input:focus-visible,textarea:focus-visible{outline:2px solid rgba(142,124,255,.78);outline-offset:2px}
    button{letter-spacing:-.01em}
    .muted{color:#8492a5}
    .small{line-height:1.45}
    .empty{
      margin:8px 0;
      padding:30px 18px;
      border-radius:18px;
      border:1px dashed rgba(148,163,184,.12);
      background:rgba(255,255,255,.018);
      color:#738196;
    }
    .loading{color:#7e8ca0;animation:softPulse 1.45s ease-in-out infinite}
    @keyframes softPulse{0%,100%{opacity:.55}50%{opacity:1}}
    @keyframes softEnter{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}
    .tabPage:not(.hidden),#publicBox:not(.hidden),#authView:not(.hidden),#libraryView:not(.hidden){animation:softEnter .2s ease-out}

    /* Landing */
    #landing .hero{padding:48px 4px 22px}
    #landing .hero h1{font-size:clamp(38px,8.5vw,58px);letter-spacing:-2.5px;max-width:680px}
    #landing .hero p{max-width:610px;color:#8b98aa;font-size:15px}
    #landing .tag{background:rgba(124,92,255,.08);border-color:rgba(124,92,255,.18);color:#c9c2ff}
    #landing>.card{padding:14px;border-radius:22px;gap:8px;background:rgba(15,24,36,.74);box-shadow:none}
    #landing>.card button{min-height:49px;border-radius:16px}

    /* Owner home */
    #homeTab{gap:13px}
    #homeTab .stats{grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
    #homeTab .stat{
      min-height:84px;
      padding:14px 13px;
      display:flex;
      flex-direction:column;
      justify-content:space-between;
      background:linear-gradient(180deg,rgba(255,255,255,.035),rgba(255,255,255,.02));
      border:1px solid var(--soft-border);
    }
    #homeTab .stat span{font-size:10.5px;text-transform:uppercase;letter-spacing:.055em;color:#718095}
    #homeTab .stat b{font-size:27px;color:#f5f7fb}
    #homeTab>.card{
      padding:16px;
      border-radius:19px;
      background:linear-gradient(155deg,rgba(124,92,255,.065),rgba(17,26,39,.78) 45%,rgba(49,182,216,.025));
      border:1px solid rgba(124,92,255,.12);
      box-shadow:none;
    }
    #homeTab>.card>b{font-size:14px;color:#ece9ff}
    #homeTab>.card>p{margin:5px 0 12px}
    #shareLink{height:45px;background:rgba(8,13,21,.62);font-size:12px;color:#aab6c7}
    #copyLink{min-width:86px;background:#7158e8;box-shadow:none}
    #shareBtn,#openPublicBtn{min-height:44px}
    #homeTab #newMessages{gap:0;border-radius:18px;overflow:hidden;background:rgba(14,22,34,.50);box-shadow:inset 0 0 0 1px rgba(148,163,184,.065)}
    #homeTab #newMessages .conversationList{border-radius:0;margin:0}

    /* Public box */
    #publicView{max-width:680px;margin:0 auto}
    #publicView .hero{padding:34px 2px 20px}
    #publicView .profileHead{gap:13px}
    #publicView .profileHead .avatar{width:58px;height:58px;border-radius:50%;border:1px solid rgba(255,255,255,.09);box-shadow:0 6px 18px rgba(0,0,0,.17)}
    #publicView .profileHead .tag{padding:5px 9px;background:rgba(255,255,255,.025);border-color:rgba(148,163,184,.1);font-size:10px}
    #publicView #ownerName{font-size:20px;letter-spacing:-.35px}
    #publicView #welcome{font-size:clamp(29px,7vw,42px);letter-spacing:-1.6px;line-height:1.08;margin:22px 0 9px}
    #publicView #bio{font-size:14px;color:#8795a7;line-height:1.6}
    #publicView #publicBox>.card.stack{
      padding:15px;
      gap:10px;
      background:rgba(15,24,36,.78);
      border:1px solid rgba(148,163,184,.10);
      box-shadow:0 16px 45px rgba(0,0,0,.13);
    }
    #publicView .mode{margin:0;gap:7px}
    #publicView .mode button{min-height:43px;border-radius:14px;background:rgba(255,255,255,.03);border-color:rgba(148,163,184,.10);font-size:12px}
    #publicView .mode button.active{background:rgba(124,92,255,.13);border-color:rgba(124,92,255,.28);color:#e3dfff}
    #identityInfo{padding:2px 2px 4px;color:#758397}
    #messageBody{min-height:142px;border-radius:18px;background:#0c141f;border-color:rgba(148,163,184,.11);padding:15px;font-size:15px}
    #sendBtn{min-height:49px;border-radius:16px;background:#7158e8;box-shadow:0 7px 19px rgba(113,88,232,.18)}
    #publicLibrary{min-height:45px;border-radius:15px;background:rgba(255,255,255,.026)}
    #publicBox>.card:not(.stack){padding:15px 16px;border-radius:19px;background:rgba(255,255,255,.022);box-shadow:none}
    #publicBox>.card:not(.stack) p{font-size:13px;margin:6px 0 12px}
    #createMine{width:100%;min-height:44px}

    /* Authentication */
    #authView{max-width:600px;margin:0 auto}
    #authView .hero{padding:44px 3px 19px}
    #authView .hero .tag{background:rgba(124,92,255,.08);border-color:rgba(124,92,255,.16);color:#cbc5ff}
    #authView .hero h1{font-size:clamp(34px,8vw,48px);letter-spacing:-2px;line-height:1.06}
    #authView .hero p{font-size:14px;color:#8795a8}
    #authView>.card{
      padding:14px;
      border-radius:22px;
      background:rgba(15,24,36,.79);
      border:1px solid rgba(148,163,184,.10);
      box-shadow:0 18px 50px rgba(0,0,0,.16);
    }
    #authView .tabs{padding:4px;border-radius:14px;background:rgba(8,13,21,.55);border-color:rgba(148,163,184,.08)}
    #authView .tabs button{min-height:39px;border-radius:11px;font-size:12px}
    #authView .tabs button.active{background:#182437;color:#f3f6fa;box-shadow:0 3px 10px rgba(0,0,0,.12)}
    #loginForm,#signupForm{gap:9px!important}
    #loginForm input,#signupForm input{height:48px;border-radius:15px;background:#0d151f;border-color:rgba(148,163,184,.10)}
    #loginBtn,#signupBtn{min-height:49px;border-radius:15px;background:#7158e8;margin-top:2px}

    /* Status messages */
    .status{border-radius:14px;padding:10px 12px;font-size:12px}
    .status.ok{background:rgba(66,211,162,.075);border-color:rgba(66,211,162,.18);color:#a9eed5}
    .status.err{background:rgba(255,117,143,.075);border-color:rgba(255,117,143,.18);color:#ffc1cd}

    @media(max-width:620px){
      #landing .hero{padding-top:35px}
      #homeTab .stats{grid-template-columns:repeat(3,minmax(0,1fr))}
      #homeTab .stat{min-height:76px;padding:12px 10px}
      #homeTab .stat b{font-size:23px}
      #homeTab .stat span{font-size:9px}
      #publicView .hero{padding-top:25px}
      #publicView #welcome{font-size:31px}
      #authView .hero{padding-top:30px}
    }
    @media(max-width:390px){
      #homeTab .stat{padding:10px 8px}
      #homeTab .stat b{font-size:21px}
      #homeTab .stat span{letter-spacing:.03em}
    }
    '''
    html=html.replace('</style>',css+'\n  </style>',1)
    html=html.replace('<meta name="theme-color" content="#0a1019">','<meta name="theme-color" content="#0a1019">',1)
    INDEX.write_text(html,encoding='utf-8')

sw=SW.read_text(encoding='utf-8')
for old in ["const CACHE='anonbox-v9';","const CACHE='anonbox-v10';"]:
    if old in sw:
        sw=sw.replace(old,"const CACHE='anonbox-v10';",1)
        break
SW.write_text(sw,encoding='utf-8')
print('Premium UI v2 applied')
