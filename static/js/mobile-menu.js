(function () {
    const btn = document.getElementById('burger-btn');
    const closeBtn = document.getElementById('burger-close');
    const menu = document.getElementById('mobile-menu');
    if (!btn || !menu) return;

    function open() {
        menu.classList.remove('hidden');
        btn.setAttribute('aria-expanded', 'true');
        document.body.classList.add('overflow-hidden');
    }

    function close() {
        menu.classList.add('hidden');
        btn.setAttribute('aria-expanded', 'false');
        document.body.classList.remove('overflow-hidden');
    }

    btn.addEventListener('click', open);
    closeBtn.addEventListener('click', close);

    // закрываем меню при клике на любую ссылку внутри него
    menu.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', close);
    });

    // страховка: если экран расширили до desktop прямо при открытом меню — закрыть
    window.addEventListener('resize', function () {
        if (window.innerWidth >= 1280 && !menu.classList.contains('hidden')) {
            close();
        }
    });
})();
