document.addEventListener('DOMContentLoaded', function () {
    const mainImages = Array.from(
        document.querySelectorAll('.product-main-image')
    );

    const thumbnails = Array.from(
        document.querySelectorAll('.product-thumbnail')
    );

    const prevButton = document.getElementById('prev-photo');
    const nextButton = document.getElementById('next-photo');

    if (!mainImages.length) {
        return;
    }

    let currentIndex = 0;


    function showPhoto(index) {
        // Index cycling
        if (index < 0) {
            index = mainImages.length - 1;
        }

        if (index >= mainImages.length) {
            index = 0;
        }

        currentIndex = index;

        // Displaying the photo
        mainImages.forEach((image, i) => {
            image.classList.toggle('hidden', i !== currentIndex);
        });

        // Lighting the corresponding miniature
        thumbnails.forEach((thumbnail, i) => {
            thumbnail.classList.toggle(
                'ring-2',
                i === currentIndex
            );

            thumbnail.classList.toggle(
                'ring-neutral-900',
                i === currentIndex
            );
        });
    }


    // Click on the miniature
    thumbnails.forEach((thumbnail, index) => {
        thumbnail.addEventListener('click', function () {
            showPhoto(index);
        });
    });


    // Previous photo
    if (prevButton) {
        prevButton.addEventListener('click', function () {
            showPhoto(currentIndex - 1);
        });
    }


    // Next photo
    if (nextButton) {
        nextButton.addEventListener('click', function () {
            showPhoto(currentIndex + 1);
        });
    }


    // Switching by keyboard arrows
    document.addEventListener('keydown', function (event) {
        if (event.key === 'ArrowLeft') {
            showPhoto(currentIndex - 1);
        }

        if (event.key === 'ArrowRight') {
            showPhoto(currentIndex + 1);
        }
    });
});