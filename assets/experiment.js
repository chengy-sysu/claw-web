(function () {
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

  var printBtn = document.getElementById('printPage');
  if (printBtn) {
    printBtn.addEventListener('click', function () {
      window.print();
    });
  }
})();

