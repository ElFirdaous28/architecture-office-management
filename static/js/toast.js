document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-toast]').forEach(function (toast) {
        const dismiss = function () {
            toast.classList.add('opacity-0', 'translate-x-4');
            window.setTimeout(function () {
                toast.remove();
            }, 200);
        };

        toast.querySelector('[data-dismiss-toast]')?.addEventListener('click', dismiss);
        window.setTimeout(dismiss, 5000);
    });
});
