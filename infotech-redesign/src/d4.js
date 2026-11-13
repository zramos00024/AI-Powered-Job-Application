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
