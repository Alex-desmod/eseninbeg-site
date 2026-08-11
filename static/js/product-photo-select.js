document.addEventListener('DOMContentLoaded', function () {
    const mainImages = document.querySelectorAll('.product-main-image');
    const thumbnails = document.querySelectorAll('.product-thumbnail');

    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function () {
            const photoId = this.dataset.photoId;

            // Shows the selected photo
            mainImages.forEach(image => {
                image.classList.toggle(
                    'hidden',
                    image.dataset.photoId !== photoId
                );
            });

            // Switch the miniature frame
            thumbnails.forEach(item => {
                item.classList.remove('ring-2', 'ring-neutral-900');
            });

            this.classList.add('ring-2', 'ring-neutral-900');
        });
    });
});