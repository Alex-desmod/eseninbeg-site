// Expand/collapse the detailed athlete info under a protocol result row.

const triggers = Array.from(document.querySelectorAll('[data-result-toggle]'));

const setExpanded = (trigger, panel, expanded) => {
    trigger.setAttribute('aria-expanded', String(expanded));
    panel.classList.toggle('hidden', !expanded);
};

triggers.forEach((trigger) => {
    const panel = document.getElementById(trigger.getAttribute('aria-controls'));
    if (!panel) return;

    const toggle = () => {
        const expanded = trigger.getAttribute('aria-expanded') === 'true';

        if (expanded) {
            setExpanded(trigger, panel, false);
            return;
        }

        // Close any other open result before opening this one.
        triggers.forEach((other) => {
            if (other === trigger) return;
            const otherPanel = document.getElementById(other.getAttribute('aria-controls'));
            if (otherPanel) setExpanded(other, otherPanel, false);
        });

        setExpanded(trigger, panel, true);
    };

    trigger.addEventListener('click', toggle);
    trigger.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            toggle();
        }
    });
});
