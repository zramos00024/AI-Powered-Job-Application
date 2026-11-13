/* Infotech Consultancy: home page script (no dependencies) */
(function(){
  var d=document,root=d.documentElement,w=window;
  var reduce=w.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine=w.matchMedia('(hover:hover) and (pointer:fine)').matches;
  var $$=function(s,c){return Array.prototype.slice.call((c||d).querySelectorAll(s));};
  var clamp=function(v,a,b){return v<a?a:v>b?b:v;};

  /* ---- navigation: mobile panel + dropdowns (unchanged behaviour) ---- */
  var header=d.querySelector('.site-header'),toggle=d.querySelector('.nav-toggle');
  var mq=w.matchMedia('(max-width:1100px)'),subs=$$('.has-sub');
  function closeSubs(except){subs.forEach(function(li){if(li!==except){li.classList.remove('open');var b=li.querySelector('.sub-toggle');if(b)b.setAttribute('aria-expanded','false');}});}
  function setNav(open){
    d.body.classList.toggle('nav-open',open);
    if(toggle){toggle.setAttribute('aria-expanded',open?'true':'false');toggle.setAttribute('aria-label',open?'Close menu':'Open menu');}
    if(!open)closeSubs(null);
  }
  if(toggle)toggle.addEventListener('click',function(){setNav(!d.body.classList.contains('nav-open'));});
  subs.forEach(function(li){
    var b=li.querySelector('.sub-toggle');if(!b)return;
    b.addEventListener('click',function(e){
      e.preventDefault();e.stopPropagation();
      var open=!li.classList.contains('open');
      closeSubs(li);li.classList.toggle('open',open);b.setAttribute('aria-expanded',open?'true':'false');
    });
  });
  d.addEventListener('click',function(e){if(!mq.matches&&!e.target.closest('.has-sub'))closeSubs(null);});
  d.addEventListener('keydown',function(e){
    if(e.key!=='Escape')return;
    if(d.body.classList.contains('nav-open')){setNav(false);if(toggle)toggle.focus();}else closeSubs(null);
  });
  mq.addEventListener('change',function(){if(!mq.matches)setNav(false);});

  /* ---- email (kept out of the HTML source) + year ---- */
  $$('[data-eml]').forEach(function(el){
    var p=el.getAttribute('data-eml').split('|').map(function(s){return s.split('').reverse().join('');});
    var addr=p[0]+'@'+p[1]+'.'+p[2],a=d.createElement('a');
    a.href='mailto:'+addr;a.textContent=addr;el.textContent='';el.appendChild(a);
  });
  $$('[data-year]').forEach(function(el){el.textContent=new Date().getFullYear();});

  /* ---- split headings into words (same text, lets CSS stagger them) ---- */
  function split(el){
    var words=el.textContent.trim().split(/\s+/);el.textContent='';
    words.forEach(function(t,i){
      var s=d.createElement('span');s.className='w';s.style.setProperty('--i',i);
      var n=d.createElement('span');n.textContent=t;s.appendChild(n);
      el.appendChild(s);if(i<words.length-1)el.appendChild(d.createTextNode(' '));
    });
    el.style.setProperty('--n',words.length);
  }
  $$('[data-split],[data-scrub]').forEach(split);

  /* ---- one-shot reveals ---- */
  var rv=$$('[data-rv]');
  rv.forEach(function(el){
    var sibs=$$(':scope > [data-rv]',el.parentNode);
    el.style.setProperty('--d',Math.min(sibs.indexOf(el),8));
  });
  if(reduce||!('IntersectionObserver' in w)){rv.forEach(function(el){el.classList.add('in');});}
  else{
    var io=new IntersectionObserver(function(es){es.forEach(function(en){
      if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target);}
    });},{rootMargin:'0px 0px -10% 0px',threshold:.05});
    rv.forEach(function(el){io.observe(el);});
  }
  w.requestAnimationFrame(function(){root.classList.add('ready');});

  /* ---- stat counters: animate up to the value already in the markup ---- */
  function count(el){
    var txt=el.textContent,m=txt.match(/\d+/);if(!m)return;
    var end=+m[0],start=end>1000?end-13:0,t0=null,pre=txt.slice(0,m.index),post=txt.slice(m.index+m[0].length);
    (function tick(t){
      if(t0===null)t0=t;var k=clamp((t-t0)/1300,0,1),e=1-Math.pow(1-k,4);
      el.textContent=pre+Math.round(start+(end-start)*e)+post;
      if(k<1)w.requestAnimationFrame(tick);else el.textContent=txt;
    })(w.performance.now());
  }
  if(!reduce&&'IntersectionObserver' in w){
    var cio=new IntersectionObserver(function(es){es.forEach(function(en){
      if(en.isIntersecting){count(en.target);cio.unobserve(en.target);}
    });},{threshold:.6});
    $$('[data-count]').forEach(function(el){cio.observe(el);});
  }

  /* ---- scroll state: header, --p progress for [data-p] / [data-scrub] / [data-pin] ---- */
  var tracked=$$('[data-p],[data-scrub],[data-pin]'),lastY=w.scrollY,ticking=false;
  var hooks=[];w.ITC={onScroll:function(fn){hooks.push(fn);},clamp:clamp,reduce:reduce,fine:fine,$$:$$};
  function frame(){
    ticking=false;
    var y=w.scrollY,vh=w.innerHeight;
    if(header){
      header.classList.toggle('scrolled',y>8);
      if(!d.body.classList.contains('nav-open')){
        if(y>lastY+4&&y>240)root.classList.add('hdr-away');else if(y<lastY-4||y<=240)root.classList.remove('hdr-away');
      }
    }
    lastY=y;
    if(!reduce)tracked.forEach(function(el){
      var r=el.getBoundingClientRect();if(r.bottom<-vh||r.top>vh*2)return;
      var p=el.hasAttribute('data-pin')?(-r.top)/Math.max(1,r.height-vh)
        :el.hasAttribute('data-scrub')?(vh*.9-r.top)/(vh*.55+r.height)
        :(vh-r.top)/(vh+r.height);
      el.style.setProperty('--p',clamp(p,0,1).toFixed(4));
    });
    for(var i=0;i<hooks.length;i++)hooks[i](y,vh);
  }
  function req(){if(!ticking){ticking=true;w.requestAnimationFrame(frame);}}
  w.addEventListener('scroll',req,{passive:true});w.addEventListener('resize',req);
  w.addEventListener('load',req);req();

  /* ---- pointer effects (mouse only) ---- */
  if(fine&&!reduce){
    $$('[data-spot]').forEach(function(el){
      el.addEventListener('pointermove',function(e){
        var r=el.getBoundingClientRect();
        el.style.setProperty('--mx',(e.clientX-r.left)+'px');el.style.setProperty('--my',(e.clientY-r.top)+'px');
      });
    });
    $$('[data-tilt]').forEach(function(el){
      el.addEventListener('pointermove',function(e){
        var r=el.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;
        el.style.setProperty('--ry',(x*7).toFixed(2)+'deg');el.style.setProperty('--rx',(-y*7).toFixed(2)+'deg');
      });
      el.addEventListener('pointerleave',function(){el.style.setProperty('--ry','0deg');el.style.setProperty('--rx','0deg');});
    });
    $$('[data-magnetic]').forEach(function(el){
      el.addEventListener('pointermove',function(e){
        var r=el.getBoundingClientRect();
        el.style.setProperty('--tx',((e.clientX-r.left-r.width/2)*.25).toFixed(1)+'px');
        el.style.setProperty('--ty',((e.clientY-r.top-r.height/2)*.35).toFixed(1)+'px');
      });
      el.addEventListener('pointerleave',function(){el.style.setProperty('--tx','0px');el.style.setProperty('--ty','0px');});
    });
  }

  /* ---- highlight the list row crossing the middle of the screen ---- */
  $$('[data-active-list]').forEach(function(list){
    if(!('IntersectionObserver' in w))return;
    var items=$$(':scope > *',list);
    var aio=new IntersectionObserver(function(es){es.forEach(function(en){
      if(en.isIntersecting){items.forEach(function(i){i.classList.toggle('is-active',i===en.target);});}
    });},{rootMargin:'-48% 0px -48% 0px'});
    items.forEach(function(i){aio.observe(i);});
  });
})();

/* Design 4 extras: the stacking deck */
(function(){
  var I=window.ITC;if(I.reduce)return;
  var cards=I.$$('[data-sec]');
  // A card taller than the screen pins when its last line is in view; a shorter one pins at the top.
  function measure(){
    var vh=window.innerHeight;
    cards.forEach(function(c){c.style.setProperty('--top',Math.min(0,vh-c.offsetHeight)+'px');});
  }
  if('ResizeObserver' in window){var ro=new ResizeObserver(measure);cards.forEach(function(c){ro.observe(c);});}
  window.addEventListener('resize',measure);measure();
  // --c: how far the next card has travelled over this one.
  I.onScroll(function(y,vh){
    for(var i=0;i<cards.length-1;i++){
      var c=I.clamp(1-cards[i+1].getBoundingClientRect().top/vh,0,1);
      cards[i].style.setProperty('--c',c.toFixed(3));
    }
  });
})();
