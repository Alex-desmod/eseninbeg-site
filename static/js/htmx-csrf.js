function getCookie(name) {
    const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? decodeURIComponent(match[2]) : null;
}

document.body.addEventListener('htmx:configRequest', function (evt) {
    evt.detail.headers['X-CSRFToken'] = getCookie('csrftoken');
});
