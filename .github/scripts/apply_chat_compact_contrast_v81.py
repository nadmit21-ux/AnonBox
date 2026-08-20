from pathlib import Path

INDEX=Path('web/index.html')
SW=Path('web/sw.js')
VERSION=Path('web/version.txt')
html=INDEX.read_text(encoding='utf-8')
MARK='/* anonbox-chat-compact-contrast-v81 */'
if MARK in html:
    raise SystemExit(0)

css=r'''
    /* anonbox-chat-compact-contrast-v81 */
    .chatComposer{gap:5px!important;padding:7px 8px calc(7px + env(safe-area-inset-bottom))!important;align-items:center!important}
    #chatAttachmentBtn,#chatVoiceBtn,#chatViewOnceBtn{
      width:38px!important;height:38px!important;min-width:38px!important;min-height:38px!important;
      flex:0 0 38px!important;padding:0!important;border-radius:50%!important;font-size:17px!important;
      line-height:1!important;display:grid!important;place-items:center!important;box-shadow:none!important
    }
    #chatSendBtn{width:42px!important;height:42px!important;min-width:42px!important;min-height:42px!important;flex:0 0 42px!important;font-size:17px!important}
    #chatInput{min-width:90px!important;min-height:40px!important;height:40px;padding:9px 12px!important;border-radius:20px!important;font-size:15px!important}
    .chatHeaderName,.pageTitle,.chatRowName,.bubbleText{color:var(--text)!important}
    .chatHeaderSub,.chatNotice,.chatRowTime,.chatPreview,.bubbleMeta,.muted{color:var(--muted)!important}
    .bubble.left,.bubble.right{color:var(--text)!important}
    .chatHeaderName{font-weight:900!important}.chatHeaderSub{font-weight:600!important}.chatNotice{font-weight:500!important;line-height:1.45!important}

    html[data-anon-theme="night"]{--text:#f1f7f7!important;--muted:#b6c6c9!important;--line:#3b5660!important}
    html[data-anon-theme="night"] body{color:#f1f7f7!important;background:#1b2e36!important}
    html[data-anon-theme="night"] .chatScreenHeader{background:rgba(27,45,53,.98)!important;border-bottom-color:#38525c!important}
    html[data-anon-theme="night"] .chatHeaderName{color:#f6fbfb!important;text-shadow:0 1px 0 rgba(0,0,0,.16)}
    html[data-anon-theme="night"] .chatHeaderSub{color:#c3d1d3!important}
    html[data-anon-theme="night"] .backBtn{color:#eaf4f4!important}
    html[data-anon-theme="night"] .headerAction{background:#2d434c!important;border-color:#48616a!important;color:#f0f7f7!important}
    html[data-anon-theme="night"] .chatScreenBody{background:radial-gradient(circle at 12% 8%,rgba(69,118,117,.14),transparent 28%),radial-gradient(circle at 90% 90%,rgba(68,92,125,.10),transparent 30%),#1d3038!important}
    html[data-anon-theme="night"] .dayPill{background:#31464e!important;border-color:#48616a!important;color:#eef6f7!important;box-shadow:none!important}
    html[data-anon-theme="night"] .bubble.left{background:#293e47!important;border-color:#39535e!important;color:#f4f9f9!important}
    html[data-anon-theme="night"] .bubble.right{background:linear-gradient(135deg,#315e58,#3a6b60)!important;border-color:#4c7c72!important;color:#f7fffd!important}
    html[data-anon-theme="night"] .bubbleText{color:#f7fbfb!important}
    html[data-anon-theme="night"] .bubbleMeta{color:#c1ced0!important}
    html[data-anon-theme="night"] .sentMark{color:#d5e0e2!important}
    html[data-anon-theme="night"] .readMark{color:#67b9ff!important}
    html[data-anon-theme="night"] .chatNotice{color:#b9c8cb!important}
    html[data-anon-theme="night"] .chatComposer{background:rgba(25,43,51,.985)!important;border-top-color:#38535d!important}
    html[data-anon-theme="night"] #chatInput{background:#253b44!important;border-color:#45616b!important;color:#f5fbfb!important;box-shadow:none!important}
    html[data-anon-theme="night"] #chatInput::placeholder{color:#a7b8bc!important;opacity:1!important}
    html[data-anon-theme="night"] #chatAttachmentBtn,html[data-anon-theme="night"] #chatVoiceBtn,html[data-anon-theme="night"] #chatViewOnceBtn{background:#30474f!important;border:1px solid #4b6670!important;color:#edf6f7!important}
    html[data-anon-theme="night"] #chatViewOnceBtn.active{background:#594fc4!important;border-color:#7b72e5!important;color:#fff!important}
    html[data-anon-theme="night"] #chatSendBtn{background:#6657dd!important;color:white!important;box-shadow:0 4px 12px rgba(66,52,174,.28)!important}
    html[data-anon-theme="night"] .replyComposerBar{background:#293e47!important;color:#eef6f7!important;border-left-color:#8276ee!important}
    html[data-anon-theme="night"] .replyComposerText b{color:#ddd8ff!important}
    html[data-anon-theme="night"] .replyComposerText span{color:#b9c8cb!important}
    html[data-anon-theme="night"] .attachmentCard,html[data-anon-theme="night"] .viewOnceCard{background:#2b4049!important;border-color:#49636d!important;color:#eef7f7!important}
    html[data-anon-theme="night"] .voiceDuration,html[data-anon-theme="night"] .viewOnceHint{color:#c0ced0!important;opacity:1!important}

    @media(max-width:420px){
      .chatComposer{gap:4px!important;padding-left:6px!important;padding-right:6px!important}
      #chatAttachmentBtn,#chatVoiceBtn,#chatViewOnceBtn{width:36px!important;height:36px!important;min-width:36px!important;min-height:36px!important;flex-basis:36px!important;font-size:16px!important}
      #chatSendBtn{width:40px!important;height:40px!important;min-width:40px!important;min-height:40px!important;flex-basis:40px!important}
      #chatInput{font-size:14px!important;padding-left:10px!important;padding-right:10px!important}
    }
'''
if '</style>' not in html:
    raise SystemExit('style close missing')
html=html.replace('</style>',css+'\n  </style>',1)
INDEX.write_text(html,encoding='utf-8')

sw=SW.read_text(encoding='utf-8').replace("const CACHE='anonbox-v19';","const CACHE='anonbox-v20';")
SW.write_text(sw,encoding='utf-8')
VERSION.write_text('AnonBox web UI v8.1\nCompact chat composer controls\nImproved text contrast, especially in Night theme\nVoice and view-once features preserved\n13 selectable themes preserved\nCache: anonbox-v20\n',encoding='utf-8')
print('chat compact contrast v8.1 applied')
