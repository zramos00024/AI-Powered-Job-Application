/* Design 5 extras: the route line that runs the length of the page */
(function(){
  var d=document,I=window.ITC,main=d.querySelector('main'),svg=main.querySelector('.route');
  if(!svg)return;
  var bg=svg.querySelector('.route-bg'),fg=svg.querySelector('.route-fg'),dot=main.querySelector('.route-dot');
  var len=0,H=0,built=0;
  // Runs down one margin and crosses to the other between sections; hugs the left edge on small screens.
  function build(){
    var W=main.clientWidth;H=main.offsetHeight;
    if(W+'x'+H===built)return;built=W+'x'+H;
    svg.setAttribute('viewBox','0 0 '+W+' '+H);
    var m=Math.max(13,(W-Math.min(W-40,1240))/4),xs=[W-m,m],side=0,path='M'+xs[0]+' 0';
    if(W>=1000)I.$$('[data-sec]').forEach(function(s,i){
      if(!i||i%2)return;
      var y=s.offsetTop,a=xs[side],b=xs[1-side];side=1-side;
      path+=' L'+a+' '+(y-110)+' C'+a+' '+(y+30)+' '+b+' '+(y-30)+' '+b+' '+(y+110);
    });
    else{xs=[m,m];path='M'+m+' 0';}
    path+=' L'+xs[side]+' '+H;
    bg.setAttribute('d',path);fg.setAttribute('d',path);
    len=fg.getTotalLength();fg.style.strokeDasharray=len;
    draw(window.scrollY,window.innerHeight);
  }
  // The path only ever travels downwards, so the length for a given depth can be bisected.
  function lengthAt(y){
    var lo=0,hi=len;
    for(var i=0;i<14;i++){var mid=(lo+hi)/2;if(fg.getPointAtLength(mid).y<y)lo=mid;else hi=mid;}
    return lo;
  }
  function draw(y,vh){
    if(!len)return;
    if(I.reduce){fg.style.strokeDashoffset=0;return;}
    var depth=I.clamp(y+vh*.55-main.offsetTop,0,H),l=lengthAt(depth),pt=fg.getPointAtLength(l);
    fg.style.strokeDashoffset=len-l;
    dot.style.translate=pt.x+'px '+pt.y+'px';dot.classList.add('on');
  }
  if('ResizeObserver' in window)new ResizeObserver(build).observe(main);
  window.addEventListener('load',build);build();
  I.onScroll(draw);
})();
