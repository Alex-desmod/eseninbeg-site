// Expand/collapse the detailed athlete info under a protocol result row.

document.querySelectorAll('[data-result-toggle]').forEach((trigger) => {
    const panel = document.getElementById(trigger.getAttribute('aria-controls'));
    if (!panel) return;

    const toggle = () => {
        const expanded = trigger.getAttribute('aria-expanded') === 'true';
        trigger.setAttribute('aria-expanded', String(!expanded));
        panel.classList.toggle('hidden', expanded);
    };

    trigger.addEventListener('click', toggle);
    trigger.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            toggle();
        }
    });
});
