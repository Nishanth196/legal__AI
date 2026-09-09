/**
 * LexReg AI – Dashboard JavaScript
 */
document.addEventListener('DOMContentLoaded', function () {
  animateCounters();
});

// Animate stat card numbers
function animateCounters() {
  document.querySelectorAll('.stat-value').forEach(el => {
    const target = parseInt(el.textContent, 10);
    if (isNaN(target)) return;
    let current  = 0;
    const step   = Math.max(1, Math.floor(target / 40));
    const timer  = setInterval(() => {
      current += step;
      if (current >= target) {
        el.textContent = target;
        clearInterval(timer);
      } else {
        el.textContent = current;
      }
    }, 30);
  });
}
