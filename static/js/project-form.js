document.addEventListener('DOMContentLoaded', function () {
    const clientSearch = document.getElementById('clientSearch');
    const clientSelect = document.getElementById('id_client');
    const clientOptions = document.getElementById('clientOptions');
    const architectButton = document.getElementById('architectSelectButton');
    const architectOptions = document.getElementById('architectOptions');
    const architectSearch = document.getElementById('architectSearch');
    const architectSelection = document.getElementById('architectSelection');

    if (clientSearch && clientSelect && clientOptions) {
        const options = clientOptions.querySelectorAll('[data-client-option]');

        clientSearch.value = clientSelect.options[clientSelect.selectedIndex]?.text || '';
        clientSearch.addEventListener('focus', function () {
            clientOptions.classList.remove('hidden');
        });
        clientSearch.addEventListener('input', function () {
            const query = clientSearch.value.trim().toLowerCase();
            clientOptions.classList.remove('hidden');
            options.forEach(function (option) {
                option.hidden = !option.textContent.toLowerCase().includes(query);
            });
        });
        options.forEach(function (option) {
            option.addEventListener('click', function () {
                clientSelect.value = option.dataset.value;
                clientSearch.value = option.textContent.trim();
                clientOptions.classList.add('hidden');
            });
        });
    }

    function updateArchitectSelection() {
        const selected = architectOptions?.querySelectorAll('input:checked') || [];
        architectSelection.textContent = selected.length
            ? Array.from(selected).map(function (input) {
                return input.closest('label').querySelector('span').textContent.trim();
            }).join(', ')
            : 'Search and select architects';
    }

    if (architectButton && architectOptions && architectSearch) {
        architectButton.addEventListener('click', function () {
            architectOptions.classList.toggle('hidden');
            if (!architectOptions.classList.contains('hidden')) architectSearch.focus();
        });
        architectSearch.addEventListener('input', function () {
            const query = architectSearch.value.trim().toLowerCase();
            architectOptions.querySelectorAll('[data-architect-option]').forEach(function (option) {
                option.hidden = !option.textContent.toLowerCase().includes(query);
            });
        });
        architectOptions.querySelectorAll('input').forEach(function (input) {
            input.addEventListener('change', updateArchitectSelection);
        });
        updateArchitectSelection();
    }

    document.addEventListener('click', function (event) {
        if (clientOptions && clientSearch && !clientOptions.parentElement.contains(event.target)) {
            clientOptions.classList.add('hidden');
        }
        if (architectOptions && architectButton &&
            !architectOptions.parentElement.contains(event.target)) {
            architectOptions.classList.add('hidden');
        }
    });
});
