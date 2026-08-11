document.addEventListener('click', function (e) {
    if (e.target.tagName === 'DIALOG') {
        e.target.close();
    }
});
