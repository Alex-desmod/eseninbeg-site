document.addEventListener('click', function (e) {
    if (e.target.tagName === 'DIALOG' && e.target.id === 'waitlist-dialog') {
        e.target.close();
    }
});
