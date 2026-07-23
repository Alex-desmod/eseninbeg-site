// glaring effect for the record portraits.

(function () {
    const details = document.getElementById('records-details');
    if (!details) return;

    details.addEventListener('toggle', function () {
        if (!details.open) return;

        const photos = details.querySelectorAll('.record-photo');
        photos.forEach(function (photo, index) {
            photo.classList.remove('shine-play');
            void photo.offsetWidth;
            setTimeout(function () {
                photo.classList.add('shine-play');
            }, index * 200);
        });
    });
})();
