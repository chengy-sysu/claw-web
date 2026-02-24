(function () {
  // --- Hamburger menu toggle ---
  var menuBtn = document.getElementById('menuToggle');
  var navLinks = document.querySelector('.nav-links');
  if (menuBtn && navLinks) {
    menuBtn.addEventListener('click', function () {
      navLinks.classList.toggle('open');
      var expanded = navLinks.classList.contains('open');
      menuBtn.setAttribute('aria-expanded', String(expanded));
    });
    // Close menu when a nav link is clicked.
    navLinks.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        navLinks.classList.remove('open');
        menuBtn.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // --- Smooth scroll for in-page anchors (index.html) ---
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

  // --- Learning progress (localStorage) ---
  var STORAGE_KEY = 'chem_learned';

  function getLearned() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    } catch (_) {
      return [];
    }
  }

  function renderProgress() {
    var learned = getLearned();
    var cards = document.querySelectorAll('.exp-link[data-exp-id]');
    var total = cards.length;
    if (!total) return;

    // Update progress bar.
    var infoEl = document.getElementById('progressInfo');
    var fillEl = document.getElementById('progressFill');
    if (infoEl && fillEl) {
      var count = learned.length;
      infoEl.textContent = '已学习 ' + count + ' / ' + total + ' 个实验';
      fillEl.style.width = Math.round((count / total) * 100) + '%';
    }

    // Add badges to learned cards.
    cards.forEach(function (card) {
      var id = card.getAttribute('data-exp-id');
      var existing = card.querySelector('.learned-badge');
      if (learned.indexOf(id) !== -1) {
        if (!existing) {
          var badge = document.createElement('span');
          badge.className = 'learned-badge';
          badge.textContent = '已学习';
          card.appendChild(badge);
        }
      } else if (existing) {
        existing.remove();
      }
    });
  }

  // --- Index experiment list search ---
  var searchEl = document.getElementById('expIndexSearch');
  var noResultsEl = document.getElementById('noResults');
  if (searchEl) {
    var debounceTimer;
    var apply = function () {
      var q = (searchEl.value || '').trim().toLowerCase();
      var visible = 0;
      document.querySelectorAll('.exp-link').forEach(function (card) {
        var txt = (card.textContent || '').toLowerCase();
        var show = !q || txt.indexOf(q) !== -1;
        card.style.display = show ? '' : 'none';
        if (show) visible++;
      });
      if (noResultsEl) {
        noResultsEl.style.display = visible === 0 && q ? 'block' : 'none';
      }
    };
    searchEl.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(apply, 150);
    });
  }

  // --- Contact form: demo only ---
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

  // --- Theme toggle (dark/light) ---
  var THEME_KEY = 'chem_theme';
  var themeBtn = document.getElementById('themeToggle');
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    if (themeBtn) themeBtn.textContent = theme === 'light' ? '暗色' : '亮色';
    try { localStorage.setItem(THEME_KEY, theme); } catch (_) {}
  }
  (function initTheme() {
    var saved = '';
    try { saved = localStorage.getItem(THEME_KEY) || ''; } catch (_) {}
    if (saved === 'light' || saved === 'dark') applyTheme(saved);
  })();
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var current = document.documentElement.getAttribute('data-theme');
      applyTheme(current === 'light' ? 'dark' : 'light');
    });
  }

  // --- Font size toggle (A- / A / A+) ---
  var FONT_KEY = 'chem_fontsize';
  var fontSizes = ['font-sm', 'font-md', 'font-lg'];
  var fontLabels = ['A-', 'A', 'A+'];
  function applyFontSize(cls) {
    fontSizes.forEach(function (c) { document.documentElement.classList.remove(c); });
    document.documentElement.classList.add(cls);
    try { localStorage.setItem(FONT_KEY, cls); } catch (_) {}
    // Highlight active button.
    document.querySelectorAll('.font-btn').forEach(function (btn) {
      btn.classList.toggle('active', btn.getAttribute('data-font') === cls);
    });
  }
  (function initFont() {
    var saved = '';
    try { saved = localStorage.getItem(FONT_KEY) || ''; } catch (_) {}
    if (fontSizes.indexOf(saved) !== -1) applyFontSize(saved);
    else applyFontSize('font-md');
  })();
  document.querySelectorAll('.font-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var cls = btn.getAttribute('data-font');
      if (cls) applyFontSize(cls);
    });
  });

  // Render progress on page load.
  renderProgress();

  // Expose for use by experiment pages loaded in same origin.
  window.__chemLearned = { get: getLearned, render: renderProgress };
})();
