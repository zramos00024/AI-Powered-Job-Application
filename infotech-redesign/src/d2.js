/* Design 2 extras: section rail + decode effect on service names */
(function(){
  var d=document,I=window.ITC,secs=I.$$('[data-sec]');
  // Rail: one marker per section, labelled from that section's own heading.
  var nav=d.createElement('nav'),ul=d.createElement('ul'),links=[];
  nav.setAttribute('aria-label','Page sections');ul.className='rail';
  secs.forEach(function(s){
    var h=s.querySelector('h1,h2,.muted-label');if(!h)return;
    var li=d.createElement('li'),a=d.createElement('a');
    a.href='#'+s.id;a.setAttribute('aria-label',h.textContent.trim());a.title=h.textContent.trim();
    li.appendChild(a);ul.appendChild(li);links.push([s,a]);
  });
  nav.appendChild(ul);d.body.appendChild(nav);
  I.onScroll(function(y,vh){
    var cur=null;
    links.forEach(function(p){if(p[0].getBoundingClientRect().top<vh*.5)cur=p[1];});
    links.forEach(function(p){if(p[1]===cur)p[1].setAttribute('aria-current','true');else p[1].removeAttribute('aria-current');});
  });

  // Decode: the name briefly scrambles and resolves back to itself.
  if(I.reduce||!I.fine)return;
  var glyphs='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/<>';
  I.$$('[data-scramble]').forEach(function(el){
    var text=el.textContent,row=el.closest('a'),raf=0;
    el.setAttribute('aria-label',text);
    row.addEventListener('pointerenter',function(){
      cancelAnimationFrame(raf);var t0=performance.now();
      (function tick(t){
        var k=Math.min(1,(t-t0)/450),done=Math.floor(k*text.length),out=text.slice(0,done);
        for(var i=done;i<text.length;i++){var c=text.charAt(i);out+=/[A-Za-z]/.test(c)?glyphs.charAt(Math.floor(Math.random()*glyphs.length)):c;}
        el.textContent=out;
        if(k<1)raf=requestAnimationFrame(tick);else el.textContent=text;
      })(t0);
    });
    row.addEventListener('pointerleave',function(){cancelAnimationFrame(raf);el.textContent=text;});
  });
})();
