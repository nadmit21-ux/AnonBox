from pathlib import Path

INDEX=Path('web/index.html')
SW=Path('web/sw.js')
VERSION=Path('web/version.txt')
html=INDEX.read_text(encoding='utf-8')
MARK='/* anonbox-extra-themes-v71 */'
if MARK in html:
    raise SystemExit(0)

css=r'''
    /* anonbox-extra-themes-v71 */
    html[data-anon-theme="violet"]{--ab-bg:#d6d0e3;--ab-surface:#e3ddea;--ab-surface2:#d9d2e2;--ab-header:#cec6db;--ab-active:#baaed3;--ab-in:#e2dce8;--ab-out:#c3b4dc;--ab-text:#352d43;--ab-muted:#756c82;--ab-border:rgba(70,55,91,.16);background:var(--ab-bg)!important;color-scheme:light}
    html[data-anon-theme="turquoise"]{--ab-bg:#c5dcda;--ab-surface:#d5e6e4;--ab-surface2:#cbdedc;--ab-header:#bdd4d2;--ab-active:#9fc8c4;--ab-in:#d7e6e4;--ab-out:#a9d1cd;--ab-text:#203c3c;--ab-muted:#627b7a;--ab-border:rgba(39,78,78,.15);background:var(--ab-bg)!important;color-scheme:light}
    html[data-anon-theme="rose"]{--ab-bg:#dfcfd5;--ab-surface:#eadde1;--ab-surface2:#e1d2d8;--ab-header:#d7c5cc;--ab-active:#cfabb9;--ab-in:#eadde1;--ab-out:#ddb6c4;--ab-text:#463039;--ab-muted:#7e6871;--ab-border:rgba(93,54,69,.14);background:var(--ab-bg)!important;color-scheme:light}
    html[data-anon-theme="amber"]{--ab-bg:#ddd2bc;--ab-surface:#e8dfcc;--ab-surface2:#dfd4be;--ab-header:#d4c7ae;--ab-active:#cdb987;--ab-in:#e8dfcc;--ab-out:#dcc79b;--ab-text:#443a28;--ab-muted:#786e5d;--ab-border:rgba(92,74,42,.15);background:var(--ab-bg)!important;color-scheme:light}
    html[data-anon-theme="ocean"]{--ab-bg:#bfd3dc;--ab-surface:#d0e0e5;--ab-surface2:#c6d9df;--ab-header:#b5ced7;--ab-active:#98becb;--ab-in:#d2e1e5;--ab-out:#9fc5d2;--ab-text:#233c47;--ab-muted:#647b85;--ab-border:rgba(43,79,92,.15);background:var(--ab-bg)!important;color-scheme:light}
    html[data-anon-theme="forest"]{--ab-bg:#c5d3c5;--ab-surface:#d5dfd3;--ab-surface2:#cad7c9;--ab-header:#bbcdbb;--ab-active:#9fbba0;--ab-in:#d6e0d4;--ab-out:#abc5ad;--ab-text:#293d2c;--ab-muted:#667768;--ab-border:rgba(50,80,55,.15);background:var(--ab-bg)!important;color-scheme:light}
    html[data-anon-theme="sand"]{--ab-bg:#d8d0c3;--ab-surface:#e5ddd1;--ab-surface2:#dcd3c5;--ab-header:#cec3b2;--ab-active:#c2ae91;--ab-in:#e5ddd1;--ab-out:#d5c1a3;--ab-text:#433b31;--ab-muted:#776f64;--ab-border:rgba(84,70,51,.14);background:var(--ab-bg)!important;color-scheme:light}
    html[data-anon-theme="bordeaux"]{--ab-bg:#d6c6ca;--ab-surface:#e3d5d8;--ab-surface2:#d9cbd0;--ab-header:#ccb9bf;--ab-active:#bd99a4;--ab-in:#e4d7da;--ab-out:#cfadb7;--ab-text:#482f37;--ab-muted:#7d666d;--ab-border:rgba(91,48,62,.15);background:var(--ab-bg)!important;color-scheme:light}

    html[data-anon-theme="violet"] body,html[data-anon-theme="turquoise"] body,html[data-anon-theme="rose"] body,html[data-anon-theme="amber"] body,html[data-anon-theme="ocean"] body,html[data-anon-theme="forest"] body,html[data-anon-theme="sand"] body,html[data-anon-theme="bordeaux"] body{background:radial-gradient(circle at 8% -6%,rgba(255,255,255,.19),transparent 30%),radial-gradient(circle at 98% 0,rgba(64,101,110,.08),transparent 28%),var(--ab-bg)!important;color:var(--ab-text)!important}
    html[data-anon-theme="violet"] .card,html[data-anon-theme="turquoise"] .card,html[data-anon-theme="rose"] .card,html[data-anon-theme="amber"] .card,html[data-anon-theme="ocean"] .card,html[data-anon-theme="forest"] .card,html[data-anon-theme="sand"] .card,html[data-anon-theme="bordeaux"] .card,
    html[data-anon-theme="violet"] .messengerList,html[data-anon-theme="turquoise"] .messengerList,html[data-anon-theme="rose"] .messengerList,html[data-anon-theme="amber"] .messengerList,html[data-anon-theme="ocean"] .messengerList,html[data-anon-theme="forest"] .messengerList,html[data-anon-theme="sand"] .messengerList,html[data-anon-theme="bordeaux"] .messengerList,
    html[data-anon-theme="violet"] .stat,html[data-anon-theme="turquoise"] .stat,html[data-anon-theme="rose"] .stat,html[data-anon-theme="amber"] .stat,html[data-anon-theme="ocean"] .stat,html[data-anon-theme="forest"] .stat,html[data-anon-theme="sand"] .stat,html[data-anon-theme="bordeaux"] .stat,
    html[data-anon-theme="violet"] .contact,html[data-anon-theme="turquoise"] .contact,html[data-anon-theme="rose"] .contact,html[data-anon-theme="amber"] .contact,html[data-anon-theme="ocean"] .contact,html[data-anon-theme="forest"] .contact,html[data-anon-theme="sand"] .contact,html[data-anon-theme="bordeaux"] .contact{background:var(--ab-surface)!important;border-color:var(--ab-border)!important;color:var(--ab-text)!important}

    html[data-anon-theme="violet"] input,html[data-anon-theme="turquoise"] input,html[data-anon-theme="rose"] input,html[data-anon-theme="amber"] input,html[data-anon-theme="ocean"] input,html[data-anon-theme="forest"] input,html[data-anon-theme="sand"] input,html[data-anon-theme="bordeaux"] input,
    html[data-anon-theme="violet"] textarea,html[data-anon-theme="turquoise"] textarea,html[data-anon-theme="rose"] textarea,html[data-anon-theme="amber"] textarea,html[data-anon-theme="ocean"] textarea,html[data-anon-theme="forest"] textarea,html[data-anon-theme="sand"] textarea,html[data-anon-theme="bordeaux"] textarea{background:var(--ab-surface2)!important;color:var(--ab-text)!important;border-color:var(--ab-border)!important}

    html[data-anon-theme="violet"] .messengerTop,html[data-anon-theme="turquoise"] .messengerTop,html[data-anon-theme="rose"] .messengerTop,html[data-anon-theme="amber"] .messengerTop,html[data-anon-theme="ocean"] .messengerTop,html[data-anon-theme="forest"] .messengerTop,html[data-anon-theme="sand"] .messengerTop,html[data-anon-theme="bordeaux"] .messengerTop,
    html[data-anon-theme="violet"] .chatScreenHeader,html[data-anon-theme="turquoise"] .chatScreenHeader,html[data-anon-theme="rose"] .chatScreenHeader,html[data-anon-theme="amber"] .chatScreenHeader,html[data-anon-theme="ocean"] .chatScreenHeader,html[data-anon-theme="forest"] .chatScreenHeader,html[data-anon-theme="sand"] .chatScreenHeader,html[data-anon-theme="bordeaux"] .chatScreenHeader,
    html[data-anon-theme="violet"] .nav,html[data-anon-theme="turquoise"] .nav,html[data-anon-theme="rose"] .nav,html[data-anon-theme="amber"] .nav,html[data-anon-theme="ocean"] .nav,html[data-anon-theme="forest"] .nav,html[data-anon-theme="sand"] .nav,html[data-anon-theme="bordeaux"] .nav{background:var(--ab-header)!important;border-color:var(--ab-border)!important}

    html[data-anon-theme="violet"] .nav button.active,html[data-anon-theme="turquoise"] .nav button.active,html[data-anon-theme="rose"] .nav button.active,html[data-anon-theme="amber"] .nav button.active,html[data-anon-theme="ocean"] .nav button.active,html[data-anon-theme="forest"] .nav button.active,html[data-anon-theme="sand"] .nav button.active,html[data-anon-theme="bordeaux"] .nav button.active,
    html[data-anon-theme="violet"] .filterChip.active,html[data-anon-theme="turquoise"] .filterChip.active,html[data-anon-theme="rose"] .filterChip.active,html[data-anon-theme="amber"] .filterChip.active,html[data-anon-theme="ocean"] .filterChip.active,html[data-anon-theme="forest"] .filterChip.active,html[data-anon-theme="sand"] .filterChip.active,html[data-anon-theme="bordeaux"] .filterChip.active{background:var(--ab-active)!important;color:var(--ab-text)!important}

    html[data-anon-theme="violet"] .chatScreenShell,html[data-anon-theme="turquoise"] .chatScreenShell,html[data-anon-theme="rose"] .chatScreenShell,html[data-anon-theme="amber"] .chatScreenShell,html[data-anon-theme="ocean"] .chatScreenShell,html[data-anon-theme="forest"] .chatScreenShell,html[data-anon-theme="sand"] .chatScreenShell,html[data-anon-theme="bordeaux"] .chatScreenShell,
    html[data-anon-theme="violet"] .chatScreenBody,html[data-anon-theme="turquoise"] .chatScreenBody,html[data-anon-theme="rose"] .chatScreenBody,html[data-anon-theme="amber"] .chatScreenBody,html[data-anon-theme="ocean"] .chatScreenBody,html[data-anon-theme="forest"] .chatScreenBody,html[data-anon-theme="sand"] .chatScreenBody,html[data-anon-theme="bordeaux"] .chatScreenBody{background:var(--ab-bg)!important;color:var(--ab-text)!important}

    html[data-anon-theme="violet"] .bubble.left,html[data-anon-theme="turquoise"] .bubble.left,html[data-anon-theme="rose"] .bubble.left,html[data-anon-theme="amber"] .bubble.left,html[data-anon-theme="ocean"] .bubble.left,html[data-anon-theme="forest"] .bubble.left,html[data-anon-theme="sand"] .bubble.left,html[data-anon-theme="bordeaux"] .bubble.left{background:var(--ab-in)!important;color:var(--ab-text)!important;border-color:var(--ab-border)!important}
    html[data-anon-theme="violet"] .bubble.right,html[data-anon-theme="turquoise"] .bubble.right,html[data-anon-theme="rose"] .bubble.right,html[data-anon-theme="amber"] .bubble.right,html[data-anon-theme="ocean"] .bubble.right,html[data-anon-theme="forest"] .bubble.right,html[data-anon-theme="sand"] .bubble.right,html[data-anon-theme="bordeaux"] .bubble.right{background:var(--ab-out)!important;color:var(--ab-text)!important;border-color:var(--ab-border)!important}

    html[data-anon-theme="violet"] .chatComposer,html[data-anon-theme="turquoise"] .chatComposer,html[data-anon-theme="rose"] .chatComposer,html[data-anon-theme="amber"] .chatComposer,html[data-anon-theme="ocean"] .chatComposer,html[data-anon-theme="forest"] .chatComposer,html[data-anon-theme="sand"] .chatComposer,html[data-anon-theme="bordeaux"] .chatComposer{background:linear-gradient(180deg,transparent,rgba(0,0,0,.025) 22%,var(--ab-bg))!important}
    html[data-anon-theme="violet"] .chatComposer textarea,html[data-anon-theme="turquoise"] .chatComposer textarea,html[data-anon-theme="rose"] .chatComposer textarea,html[data-anon-theme="amber"] .chatComposer textarea,html[data-anon-theme="ocean"] .chatComposer textarea,html[data-anon-theme="forest"] .chatComposer textarea,html[data-anon-theme="sand"] .chatComposer textarea,html[data-anon-theme="bordeaux"] .chatComposer textarea,
    html[data-anon-theme="violet"] .actionSheet,html[data-anon-theme="turquoise"] .actionSheet,html[data-anon-theme="rose"] .actionSheet,html[data-anon-theme="amber"] .actionSheet,html[data-anon-theme="ocean"] .actionSheet,html[data-anon-theme="forest"] .actionSheet,html[data-anon-theme="sand"] .actionSheet,html[data-anon-theme="bordeaux"] .actionSheet{background:var(--ab-surface)!important;color:var(--ab-text)!important}

    html[data-anon-theme="violet"] .muted,html[data-anon-theme="turquoise"] .muted,html[data-anon-theme="rose"] .muted,html[data-anon-theme="amber"] .muted,html[data-anon-theme="ocean"] .muted,html[data-anon-theme="forest"] .muted,html[data-anon-theme="sand"] .muted,html[data-anon-theme="bordeaux"] .muted{color:var(--ab-muted)!important}
    .anonThemeChoices{max-height:460px;overflow:auto;overscroll-behavior:contain;padding-right:2px}
    .anonExtraThemeBadge{display:inline-flex;align-items:center;margin-left:5px;padding:2px 5px;border-radius:999px;font-size:8px;font-weight:800;background:rgba(60,95,100,.11);color:inherit;vertical-align:middle}
'''
html=html.replace('</style>',css+'\n  </style>',1)

js=r'''
<script>
(function(){
  var extraThemes=[
    {id:'violet',label:'Violet',desc:'Lavande et ardoise',swatch:'linear-gradient(135deg,#bcaed3,#e3ddea)',meta:'#d6d0e3'},
    {id:'turquoise',label:'Turquoise',desc:'Aqua doux et gris',swatch:'linear-gradient(135deg,#9fc8c4,#d5e6e4)',meta:'#c5dcda'},
    {id:'rose',label:'Rose',desc:'Rose poudré et gris',swatch:'linear-gradient(135deg,#cfabb9,#eadde1)',meta:'#dfcfd5'},
    {id:'amber',label:'Ambre',desc:'Doré doux et beige',swatch:'linear-gradient(135deg,#cdb987,#e8dfcc)',meta:'#ddd2bc'},
    {id:'ocean',label:'Océan',desc:'Bleu profond et aqua',swatch:'linear-gradient(135deg,#98becb,#d0e0e5)',meta:'#bfd3dc'},
    {id:'forest',label:'Forêt',desc:'Vert naturel et gris',swatch:'linear-gradient(135deg,#9fbba0,#d5dfd3)',meta:'#c5d3c5'},
    {id:'sand',label:'Sable',desc:'Beige minéral et gris',swatch:'linear-gradient(135deg,#c2ae91,#e5ddd1)',meta:'#d8d0c3'},
    {id:'bordeaux',label:'Bordeaux',desc:'Rouge doux et ardoise',swatch:'linear-gradient(135deg,#bd99a4,#e3d5d8)',meta:'#d6c6ca'}
  ];
  var labels={mix:'Mixte',blue:'Bleu',green:'Vert',gray:'Gris',night:'Nuit'};
  extraThemes.forEach(function(t){labels[t.id]=t.label});

  function current(){try{return localStorage.getItem('anonbox_theme_v1')||'mix'}catch(e){return 'mix'}}
  function metaColor(id){for(var i=0;i<extraThemes.length;i++)if(extraThemes[i].id===id)return extraThemes[i].meta;var map={mix:'#cad8d8',blue:'#c8d7e5',green:'#cbdccf',gray:'#cfd4da',night:'#1c2830'};return map[id]||map.mix}
  function themeIdOf(btn){return btn.getAttribute('data-extra-theme-id')||btn.getAttribute('data-theme')||btn.getAttribute('data-anon-theme')||''}
  function syncUI(){
    var id=current(),name=labels[id]||id;
    document.querySelectorAll('.anonThemeChoice').forEach(function(b){b.classList.toggle('active',themeIdOf(b)===id)});
    document.querySelectorAll('.anonThemeSettings p,.anonThemeSheet p').forEach(function(el){if(/^Thème actuel\s*:/.test((el.textContent||'').trim()))el.textContent='Thème actuel : '+name});
  }
  function apply(id){
    try{localStorage.setItem('anonbox_theme_v1',id)}catch(e){}
    document.documentElement.setAttribute('data-anon-theme',id);
    document.documentElement.style.colorScheme=id==='night'?'dark':'light';
    var meta=document.querySelector('meta[name="theme-color"]');if(meta)meta.setAttribute('content',metaColor(id));
    try{if(window.AnonBoxThemeBridge&&typeof window.AnonBoxThemeBridge.setTheme==='function')window.AnonBoxThemeBridge.setTheme(id)}catch(e){}
    syncUI();
    try{window.dispatchEvent(new CustomEvent('anonbox-theme-change',{detail:{theme:id}}))}catch(e){}
  }
  function button(t){
    var b=document.createElement('button');b.type='button';b.className='anonThemeChoice';b.setAttribute('data-extra-theme-id',t.id);b.setAttribute('data-theme',t.id);b.setAttribute('data-anon-theme',t.id);
    b.innerHTML='<span class="anonThemeSwatch" style="background:'+t.swatch+'"></span><span><b>'+t.label+' <span class="anonExtraThemeBadge">Nouveau</span></b><span>'+t.desc+'</span></span>';
    b.addEventListener('click',function(ev){ev.preventDefault();ev.stopPropagation();apply(t.id)});return b;
  }
  function augment(){
    document.querySelectorAll('.anonThemeChoices').forEach(function(box){
      extraThemes.forEach(function(t){if(!box.querySelector('[data-extra-theme-id="'+t.id+'"]'))box.appendChild(button(t))});
    });
    syncUI();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',augment);else augment();
  var obs=new MutationObserver(function(){augment()});
  function observe(){if(document.body)obs.observe(document.body,{childList:true,subtree:true});else setTimeout(observe,50)}observe();
  setTimeout(function(){apply(current())},50);
})();
</script>
'''
html=html.replace('</body>',js+'\n</body>',1)
INDEX.write_text(html,encoding='utf-8')

sw=SW.read_text(encoding='utf-8').replace("const CACHE='anonbox-v17';","const CACHE='anonbox-v18';")
SW.write_text(sw,encoding='utf-8')
VERSION.write_text('AnonBox web UI v7.1\n13 selectable themes: Mixte, Bleu, Vert, Gris, Nuit, Violet, Turquoise, Rose, Ambre, Ocean, Foret, Sable, Bordeaux\nTheme choice stored locally on device\nAnonymous profile features unchanged\nCache: anonbox-v18\n',encoding='utf-8')
