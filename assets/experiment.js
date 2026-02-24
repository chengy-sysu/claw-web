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

  // --- Equation practice mode ---
  var eqBtn = document.getElementById('eqPractice');
  if (eqBtn) {
    // Hide button if no interactive blanks exist
    var hasBlanks = document.querySelectorAll('.cond-blank, .symbol-blank').length > 0;
    if (!hasBlanks) {
      eqBtn.style.display = 'none';
    } else {
    var isEqMode = false;
    eqBtn.addEventListener('click', function () {
      isEqMode = !isEqMode;
      document.querySelectorAll('.chem-eq-display').forEach(function (el) {
        el.style.display = isEqMode ? 'none' : '';
      });
      document.querySelectorAll('.chem-eq-interactive').forEach(function (el) {
        el.style.display = isEqMode ? 'inline' : 'none';
      });
      eqBtn.textContent = isEqMode ? '退出练习' : '方程式练习';
      eqBtn.classList.toggle('active', isEqMode);
      if (!isEqMode) {
        document.querySelectorAll('.cond-blank, .symbol-blank').forEach(function (el) {
          el.textContent = '?';
          el.classList.remove('cond-correct');
        });
      }
    });

    document.addEventListener('click', function (e) {
      if (!isEqMode) return;
      var blank = e.target.closest('.cond-blank, .symbol-blank');
      if (!blank) return;
      var choices = (blank.getAttribute('data-choices') || '').split(',');
      var answer = blank.getAttribute('data-answer');
      var current = blank.textContent;
      var idx = choices.indexOf(current);
      var next = choices[(idx + 1) % choices.length];
      blank.textContent = next;
      blank.classList.toggle('cond-correct', next === answer);
    });
    } // end else (hasBlanks)
  }

  // --- Step ordering game ---
  document.querySelectorAll('.step-order-game').forEach(function (game) {
    var correct = JSON.parse(game.getAttribute('data-correct'));
    var choicesEl = game.querySelector('.step-order-choices');
    var answerEl = game.querySelector('.step-order-answer');
    var resetBtn = game.querySelector('.step-reset-btn');
    var successEl = game.querySelector('.step-order-success');
    var whyEl = game.parentElement.querySelector('.step-why-questions');
    var selected = [];

    function shuffle(container) {
      var items = Array.from(container.children);
      for (var i = items.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        container.appendChild(items[j]);
        var tmp = items[i]; items[i] = items[j]; items[j] = tmp;
      }
    }
    shuffle(choicesEl);

    choicesEl.addEventListener('click', function (e) {
      var chip = e.target.closest('.step-chip');
      if (!chip || chip.classList.contains('used')) return;
      var label = chip.getAttribute('data-label');
      if (label === correct[selected.length]) {
        selected.push(label);
        chip.classList.add('used', 'step-correct');
        var placed = document.createElement('span');
        placed.className = 'step-placed';
        placed.textContent = label;
        answerEl.appendChild(placed);
        if (selected.length === correct.length) {
          if (successEl) successEl.style.display = 'block';
          if (whyEl) whyEl.style.display = '';
        }
      } else {
        chip.classList.add('step-wrong');
        setTimeout(function () { chip.classList.remove('step-wrong'); }, 500);
      }
    });

    if (resetBtn) {
      resetBtn.addEventListener('click', function () {
        selected = [];
        answerEl.innerHTML = '';
        choicesEl.querySelectorAll('.step-chip').forEach(function (c) {
          c.classList.remove('used', 'step-correct', 'step-wrong');
        });
        shuffle(choicesEl);
        if (successEl) successEl.style.display = 'none';
        if (whyEl) whyEl.style.display = 'none';
        whyEl && whyEl.querySelectorAll('.why-a').forEach(function (a) {
          a.classList.remove('revealed');
        });
      });
    }
  });

  // --- Why question reveal ---
  document.addEventListener('click', function (e) {
    var ans = e.target.closest('.why-a');
    if (ans) ans.classList.toggle('revealed');
  });

  // --- Q&A card reveal ---
  document.addEventListener('click', function (e) {
    var ans = e.target.closest('.qa-answer');
    if (ans) ans.classList.toggle('qa-hidden');
  });
})();
