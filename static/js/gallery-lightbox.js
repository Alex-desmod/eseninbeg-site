(function () {
    const items = Array.from(document.querySelectorAll('.gallery-item'));
    if (!items.length) return;

    const lightbox = document.getElementById('lightbox');
    const mediaEl = document.getElementById('lightbox-media');
    const captionEl = document.getElementById('lightbox-caption');
    let currentIndex = 0;

    function render(index) {
        currentIndex = (index + items.length) % items.length;
        const item = items[currentIndex];
        const src = item.dataset.src;
        const caption = item.dataset.caption;

        mediaEl.innerHTML = '';
        const img = document.createElement('img');
        img.src = src;
        img.alt = caption;
        img.className = 'max-w-[90vw] max-h-[75vh] object-contain rounded-md';
        mediaEl.appendChild(img);
        captionEl.textContent = caption;
    }

    function open(index) {
        render(index);
        lightbox.style.display = 'flex';
        document.body.classList.add('overflow-hidden');
    }

    function close() {
        lightbox.style.display = 'none';
        mediaEl.innerHTML = '';
        document.body.classList.remove('overflow-hidden');
    }

    items.forEach((item, index) => {
        item.addEventListener('click', () => open(index));
    });

    document.getElementById('lightbox-close').addEventListener('click', close);
    document.getElementById('lightbox-prev').addEventListener('click', () => render(currentIndex - 1));
    document.getElementById('lightbox-next').addEventListener('click', () => render(currentIndex + 1));

    lightbox.addEventListener('click', function (e) {
        if (e.target === lightbox) close();
    });

    document.addEventListener('keydown', function (e) {
        if (lightbox.style.display === 'none') return;
        if (e.key === 'Escape') close();
        if (e.key === 'ArrowLeft') render(currentIndex - 1);
        if (e.key === 'ArrowRight') render(currentIndex + 1);
    });
})();
