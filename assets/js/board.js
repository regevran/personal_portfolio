(function () {
  var viewport = document.querySelector('.board-viewport');
  if (!viewport) return;

  function centeredLeft() {
    var max = viewport.scrollWidth - viewport.clientWidth;
    var portraitX = viewport.scrollWidth * 0.523;
    return Math.min(max, Math.max(0, portraitX - viewport.clientWidth / 2));
  }

  function centerBoard() {
    if (location.hash) return;
    if (viewport.scrollWidth <= viewport.clientWidth) {
      viewport.scrollLeft = 0;
      return;
    }
    viewport.scrollLeft = centeredLeft();
  }

  function panFromWheel(event) {
    if (viewport.scrollWidth <= viewport.clientWidth) return;
    if (Math.abs(event.deltaY) > Math.abs(event.deltaX)) {
      viewport.scrollLeft += event.deltaY;
      event.preventDefault();
    }
  }

  window.addEventListener('load', centerBoard);
  window.addEventListener('resize', centerBoard);
  viewport.addEventListener('wheel', panFromWheel, { passive: false });

  document.querySelectorAll('.topnav a').forEach(function (link) {
    link.addEventListener('click', function (event) {
      var id = link.getAttribute('href').slice(1);
      if (!document.getElementById(id)) return;
      event.preventDefault();
      var max = viewport.scrollWidth - viewport.clientWidth;
      var target = centeredLeft();
      if (id === 'nature') target = 0;
      if (id === 'work') target = max - Math.min(48, max / 4);
      var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      viewport.scrollTo({ left: target, behavior: reduce ? 'auto' : 'smooth' });
    });
  });
})();
