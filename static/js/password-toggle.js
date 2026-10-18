document.addEventListener('DOMContentLoaded', function () {
    window.lucide?.createIcons();

    document.querySelectorAll('[data-toggle-password]').forEach(function (button) {
        const input = document.getElementById(button.dataset.togglePassword);
        if (!input) return;

        button.addEventListener('click', function () {
            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            button.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
            button.innerHTML = `<i data-lucide="${isPassword ? 'eye-off' : 'eye'}" class="h-4 w-4" aria-hidden="true"></i>`;
            window.lucide?.createIcons();
        });
    });
});
