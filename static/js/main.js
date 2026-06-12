/**
 * AttendEase — Main JavaScript
 * Handles sidebar toggle, auto-dismiss alerts, and stat counter animations.
 */

document.addEventListener('DOMContentLoaded', () => {

    // ── Sidebar Toggle (Mobile) ──
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarClose = document.getElementById('sidebarClose');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    function openSidebar() {
        if (sidebar) sidebar.classList.add('show');
        if (sidebarOverlay) sidebarOverlay.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove('show');
        if (sidebarOverlay) sidebarOverlay.classList.remove('show');
        document.body.style.overflow = '';
    }

    if (sidebarToggle) sidebarToggle.addEventListener('click', openSidebar);
    if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);
    if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeSidebar);

    // ── Auto-dismiss Flash Messages ──
    const alerts = document.querySelectorAll('.messages-container .alert');
    alerts.forEach((alert) => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // ── Animated Stat Counters ──
    const counters = document.querySelectorAll('.stat-value[data-count]');
    const animateCounter = (el) => {
        const target = parseInt(el.getAttribute('data-count'), 10);
        if (isNaN(target) || target === 0) {
            el.textContent = '0';
            return;
        }
        const duration = 800;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease-out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(eased * target);
            if (progress < 1) requestAnimationFrame(update);
        }

        requestAnimationFrame(update);
    };

    // Use IntersectionObserver so counters animate when visible
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.3 });

        counters.forEach((counter) => observer.observe(counter));
    } else {
        counters.forEach(animateCounter);
    }

    // ── Button Click Ripple ──
    const animatedButtons = document.querySelectorAll('.btn, .filter-tab, .nav-link-item');
    animatedButtons.forEach((button) => {
        button.addEventListener('click', (event) => {
            const ripple = document.createElement('span');
            const rect = button.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);

            ripple.className = 'btn-ripple';
            ripple.style.width = `${size}px`;
            ripple.style.height = `${size}px`;
            ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
            ripple.style.top = `${event.clientY - rect.top - size / 2}px`;

            button.appendChild(ripple);
            ripple.addEventListener('animationend', () => ripple.remove());
        });
    });
});
