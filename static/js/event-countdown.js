document.addEventListener('DOMContentLoaded', () => {
    const el = document.getElementById('event-countdown');
    if (!el) return;

    const target = new Date(el.dataset.target);
    if (isNaN(target.getTime())) return;

    const daysEl = el.querySelector('[data-countdown="days"]');
    const hoursEl = el.querySelector('[data-countdown="hours"]');
    const minutesEl = el.querySelector('[data-countdown="minutes"]');
    const secondsEl = el.querySelector('[data-countdown="seconds"]');

    const pad = (n) => String(n).padStart(2, '0');

    let timerId;

    function update() {
        const diff = target.getTime() - Date.now();

        if (diff <= 0) {
            daysEl.textContent = '00';
            hoursEl.textContent = '00';
            minutesEl.textContent = '00';
            secondsEl.textContent = '00';
            clearInterval(timerId);
            return;
        }

        const totalSeconds = Math.floor(diff / 1000);
        daysEl.textContent = pad(Math.floor(totalSeconds / 86400));
        hoursEl.textContent = pad(Math.floor((totalSeconds % 86400) / 3600));
        minutesEl.textContent = pad(Math.floor((totalSeconds % 3600) / 60));
        secondsEl.textContent = pad(totalSeconds % 60);
    }

    update();
    timerId = setInterval(update, 1000);
});