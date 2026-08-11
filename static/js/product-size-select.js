document.querySelectorAll('.size-btn').forEach(function (btn) {
    if (btn.disabled) return;

    btn.addEventListener('click', function () {
        document.querySelectorAll('.size-btn').forEach(function (b) {
            b.classList.remove('border-neutral-900', 'bg-neutral-900', 'text-white');
        });
        btn.classList.add('border-neutral-900', 'bg-neutral-900', 'text-white');

        document.getElementById('selected-variant').value = btn.dataset.variantId;
        document.getElementById('order-btn').removeAttribute('disabled');
    });
});
