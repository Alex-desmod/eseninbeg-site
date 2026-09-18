(function () {
    const strip = document.getElementById('gallery-strip');
    const prevBtn = document.getElementById('gallery-prev');
    const nextBtn = document.getElementById('gallery-next');
    if (!strip || !prevBtn || !nextBtn) return;

    function scrollAmount() {
        return strip.clientWidth * 0.8;
    }

    function updateArrowsVisibility() {
        const scrollable = strip.scrollWidth > strip.clientWidth + 1;
        prevBtn.style.display = scrollable ? '' : 'none';
        nextBtn.style.display = scrollable ? '' : 'none';
    }

    prevBtn.addEventListener('click', function () {
        strip.scrollBy({ left: -scrollAmount(), behavior: 'smooth' });
    });

    nextBtn.addEventListener('click', function () {
        strip.scrollBy({ left: scrollAmount(), behavior: 'smooth' });
    });

    updateArrowsVisibility();
    window.addEventListener('resize', updateArrowsVisibility);
})();
