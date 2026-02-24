(function () {
  // Smooth scroll for in-page anchors (index.html).
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var href = anchor.getAttribute('href');
      if (!href || href.length < 2) return;
      var target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      window.scrollTo({
        top: target.offsetTop - 80,
        behavior: 'smooth',
      });
    });
  });

  // Index experiment list search.
  var searchEl = document.getElementById('expIndexSearch');
  if (searchEl) {
    var apply = function () {
      var q = (searchEl.value || '').trim().toLowerCase();
      document.querySelectorAll('.exp-link').forEach(function (card) {
        var txt = (card.textContent || '').toLowerCase();
        card.style.display = !q || txt.indexOf(q) !== -1 ? '' : 'none';
      });
    };
    searchEl.addEventListener('input', apply);
  }

  // Contact form: demo only.
  var form = document.getElementById('contactForm');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var btn = document.getElementById('submitBtn');
      var alertBox = document.getElementById('formAlert');
      if (!btn || !alertBox) return;
      btn.disabled = true;
      btn.textContent = '提交中...';
      setTimeout(function () {
        btn.disabled = false;
        btn.textContent = '提交问题';
        alertBox.style.display = 'block';
        alertBox.className = 'form-alert success';
        alertBox.textContent = '已收到你的化学问题！我们会尽快为你解答，并可能将答案添加到学习资源中。';
        form.reset();
      }, 800);
    });
  }
})();

