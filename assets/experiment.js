(function () {
  // --- Hamburger menu toggle (shared with experiment pages) ---
  var menuBtn = document.getElementById('menuToggle');
  var navLinks = document.querySelector('.nav-links');
  if (menuBtn && navLinks) {
    menuBtn.addEventListener('click', function () {
      navLinks.classList.toggle('open');
      var expanded = navLinks.classList.contains('open');
      menuBtn.setAttribute('aria-expanded', String(expanded));
    });
    navLinks.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        navLinks.classList.remove('open');
        menuBtn.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // --- Expand / Collapse all ---
  var expandBtn = document.getElementById('expandAll');
  if (expandBtn) {
    expandBtn.addEventListener('click', function () {
      document.querySelectorAll('details.exp-block').forEach(function (d) {
        d.open = true;
      });
    });
  }

  var collapseBtn = document.getElementById('collapseAll');
  if (collapseBtn) {
    collapseBtn.addEventListener('click', function () {
      document.querySelectorAll('details.exp-block').forEach(function (d) {
        d.open = false;
      });
    });
  }

  // --- Print: expand all details before printing ---
  var printBtn = document.getElementById('printPage');
  if (printBtn) {
    printBtn.addEventListener('click', function () {
      document.querySelectorAll('details.exp-block').forEach(function (d) {
        d.open = true;
      });
      setTimeout(function () { window.print(); }, 100);
    });
  }

  // --- Quiz (cover) mode ---
  var quizBtn = document.getElementById('quizMode');
  if (quizBtn) {
    var page = document.querySelector('.page') || document.body;
    var isQuiz = false;

    quizBtn.addEventListener('click', function () {
      isQuiz = !isQuiz;
      if (isQuiz) {
        page.classList.add('quiz-mode');
        quizBtn.textContent = '退出自测';
        quizBtn.classList.add('active');
        // Reset all revealed items.
        document.querySelectorAll('.block-list li.revealed').forEach(function (li) {
          li.classList.remove('revealed');
        });
      } else {
        page.classList.remove('quiz-mode');
        quizBtn.textContent = '自测模式';
        quizBtn.classList.remove('active');
      }
    });

    // Click to reveal individual items in quiz mode.
    document.addEventListener('click', function (e) {
      if (!isQuiz) return;
      var li = e.target.closest('.block-list li');
      if (li) {
        li.classList.toggle('revealed');
      }
    });
  }

  // --- Mark as learned (localStorage) ---
  var STORAGE_KEY = 'chem_learned';
  var learnedBtn = document.getElementById('markLearned');
  var expId = document.body.getAttribute('data-exp-id');

  function getLearned() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    } catch (_) {
      return [];
    }
  }

  function setLearned(arr) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(arr));
  }

  function updateLearnedBtn() {
    if (!learnedBtn || !expId) return;
    var list = getLearned();
    var done = list.indexOf(expId) !== -1;
    learnedBtn.textContent = done ? '已学习 ✓' : '标记为已学习';
    learnedBtn.classList.toggle('is-learned', done);
  }

  if (learnedBtn && expId) {
    updateLearnedBtn();
    learnedBtn.addEventListener('click', function () {
      var list = getLearned();
      var idx = list.indexOf(expId);
      if (idx === -1) {
        list.push(expId);
      } else {
        list.splice(idx, 1);
      }
      setLearned(list);
      updateLearnedBtn();
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
  function applyFontSize(cls) {
    fontSizes.forEach(function (c) { document.documentElement.classList.remove(c); });
    document.documentElement.classList.add(cls);
    try { localStorage.setItem(FONT_KEY, cls); } catch (_) {}
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
})();
