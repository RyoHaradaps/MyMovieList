document.addEventListener('DOMContentLoaded', function() {
    var statusMain = document.getElementById('status-main');
    var statusCompact = document.getElementById('status-compact');
    var progressMain = document.getElementById('progress-main');
    var progressCompact = document.getElementById('progress-compact');
    var contentType = null;
    if (statusMain && statusMain.getAttribute('data-content-type')) {
      contentType = statusMain.getAttribute('data-content-type');
    } else if (statusCompact && statusCompact.getAttribute('data-content-type')) {
      contentType = statusCompact.getAttribute('data-content-type');
    }
  
    function setProgressIfCompleted(statusValue) {
      if (contentType === 'movie' && statusValue === 'completed') {
        if (progressMain) progressMain.value = 1;
        if (progressCompact) progressCompact.value = 1;
      }
    }
  
    if (statusMain) {
      statusMain.addEventListener('change', function() {
        setProgressIfCompleted(statusMain.value);
      });
    }
    if (statusCompact) {
      statusCompact.addEventListener('change', function() {
        setProgressIfCompleted(statusCompact.value);
      });
    }
  });