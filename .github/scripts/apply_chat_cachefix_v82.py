from pathlib import Path

INDEX=Path('web/index.html')
SW=Path('web/sw.js')
VERSION=Path('web/version.txt')
html=INDEX.read_text(encoding='utf-8')
MARK='/* anonbox-chat-cachefix-v82 */'
if MARK in html:
    raise SystemExit(0)

css=r'''
    /* anonbox-chat-cachefix-v82 */
    .chatComposer{gap:4px!important;padding:6px 7px calc(6px + env(safe-area-inset-bottom))!important;align-items:center!important}
    #chatAttachmentBtn,#chatVoiceBtn,#chatViewOnceBtn{
      width:32px!important;height:32px!important;min-width:32px!important;min-height:32px!important;
      flex:0 0 32px!important;padding:0!important;border-radius:50%!important;font-size:15px!important;
      line-height:1!important;display:grid!important;place-items:center!important;
      background:rgba(72,91,100,.14)!important;border:1px solid rgba(70,90,100,.22)!important;
      color:var(--text)!important;box-shadow:none!important
    }
    #chatViewOnceBtn.active{background:#6557d9!important;border-color:#7669e6!important;color:#fff!important}
    #chatSendBtn{width:38px!important;height:38px!important;min-width:38px!important;min-height:38px!important;flex:0 0 38px!important;font-size:16px!important}
    #chatInput{flex:1 1 auto!important;min-width:110px!important;min-height:38px!important;height:38px!important;padding:8px 11px!important;border-radius:19px!important;font-size:14px!important}
    .chatHeaderName{color:var(--text)!important;opacity:1!important}
    .chatHeaderSub{color:var(--muted)!important;opacity:1!important}
    .chatNotice{color:var(--muted)!important;opacity:1!important;padding:7px 13px!important;font-size:10.5px!important}
    .bubbleText{color:inherit!important;opacity:1!important}
    .bubbleMeta{opacity:.9!important}

    html[data-anon-theme="night"]{--text:#f4f9f9!important;--muted:#c1ced1!important;--line:#3d5862!important}
    html[data-anon-theme="night"] .chatHeaderName{color:#ffffff!important}
    html[data-anon-theme="night"] .chatHeaderSub{color:#cbd7d9!important}
    html[data-anon-theme="night"] .chatNotice{color:#c0cccf!important;background:#20343c!important;border-top:1px solid #304a54!important}
    html[data-anon-theme="night"] .bubble.left{background:#2b414a!important;border-color:#3d5963!important;color:#ffffff!important}
    html[data-anon-theme="night"] .bubble.right{background:linear-gradient(135deg,#35675f,#3d7166)!important;border-color:#54867a!important;color:#ffffff!important}
    html[data-anon-theme="night"] .bubbleMeta{color:#d0dadd!important}
    html[data-anon-theme="night"] .chatComposer{background:#1b2e36!important;border-top-color:#35505a!important}
    html[data-anon-theme="night"] #chatInput{background:#263d46!important;border-color:#45636d!important;color:#ffffff!important}
    html[data-anon-theme="night"] #chatInput::placeholder{color:#b4c2c5!important;opacity:1!important}
    html[data-anon-theme="night"] #chatAttachmentBtn,
    html[data-anon-theme="night"] #chatVoiceBtn,
    html[data-anon-theme="night"] #chatViewOnceBtn{background:#263d46!important;border-color:#405d67!important;color:#f2f8f8!important}
    html[data-anon-theme="night"] #chatViewOnceBtn.active{background:#6557d9!important;border-color:#8174ec!important;color:#fff!important}
    html[data-anon-theme="night"] #chatSendBtn{background:#6557d9!important;color:#fff!important;box-shadow:0 3px 10px rgba(66,52,174,.25)!important}

    @media(max-width:380px){
      .chatComposer{gap:3px!important;padding-left:5px!important;padding-right:5px!important}
      #chatAttachmentBtn,#chatVoiceBtn,#chatViewOnceBtn{width:30px!important;height:30px!important;min-width:30px!important;min-height:30px!important;flex-basis:30px!important;font-size:14px!important}
      #chatSendBtn{width:36px!important;height:36px!important;min-width:36px!important;min-height:36px!important;flex-basis:36px!important}
      #chatInput{min-width:92px!important;padding-left:9px!important;padding-right:9px!important}
    }
'''
if '</style>' not in html: raise SystemExit('style close missing')
# Put it at the very end of the last style block, not an earlier style block.
pos=html.rfind('</style>')
html=html[:pos]+css+'\n'+html[pos:]

# Add a visible build marker for diagnostics.
html=html.replace('<body>', '<body data-anonbox-ui="8.2">', 1)

INDEX.write_text(html,encoding='utf-8')

sw=SW.read_text(encoding='utf-8')
sw=sw.replace("const CACHE='anonbox-v20';","const CACHE='anonbox-v21';")
# Force existing open clients to refresh exactly once when v21 activates.
old="""self.addEventListener('activate',event=>{\n  event.waitUntil((async()=>{\n    const keys=await caches.keys();\n    await Promise.all(keys.filter(k=>k!==CACHE&&k.startsWith('anonbox-')).map(k=>caches.delete(k)));\n    await self.clients.claim();\n  })());\n});"""
new="""self.addEventListener('activate',event=>{\n  event.waitUntil((async()=>{\n    const keys=await caches.keys();\n    await Promise.all(keys.filter(k=>k!==CACHE&&k.startsWith('anonbox-')).map(k=>caches.delete(k)));\n    await self.clients.claim();\n    const clients=await self.clients.matchAll({type:'window',includeUncontrolled:true});\n    for(const client of clients){\n      try{\n        const u=new URL(client.url);\n        if(u.searchParams.get('_abv')!=='21'){\n          u.searchParams.set('_abv','21');\n          await client.navigate(u.toString());\n        }\n      }catch(e){}\n    }\n  })());\n});"""
if old not in sw: raise SystemExit('activate block missing')
sw=sw.replace(old,new,1)
SW.write_text(sw,encoding='utf-8')
VERSION.write_text('AnonBox web UI v8.2\nForced refresh when a new UI service worker activates\nCompact 30-32px chat utility buttons\nHigher Night-theme text contrast\nVoice and view-once preserved\nCache: anonbox-v21\n',encoding='utf-8')
print('v8.2 cachefix applied')
