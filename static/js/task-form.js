document.addEventListener('DOMContentLoaded', function () {
    const search = document.getElementById('architectSearch');
    const select = document.getElementById('id_architect');
    const optionsContainer = document.getElementById('architectOptions');

    if (!search || !select || !optionsContainer) return;

    const options = optionsContainer.querySelectorAll('[data-architect-option]');
    search.value = select.options[select.selectedIndex]?.text || '';

    search.addEventListener('focus', function () {
        optionsContainer.classList.remove('hidden');
    });
    search.addEventListener('input', function () {
        const query = search.value.trim().toLowerCase();
        optionsContainer.classList.remove('hidden');
        options.forEach(function (option) {
            option.hidden = !option.textContent.toLowerCase().includes(query);
        });
    });
    options.forEach(function (option) {
        option.addEventListener('click', function () {
            select.value = option.dataset.value;
            search.value = option.textContent.trim();
            optionsContainer.classList.add('hidden');
        });
    });
    document.addEventListener('click', function (event) {
        if (!optionsContainer.parentElement.contains(event.target)) {
            optionsContainer.classList.add('hidden');
        }
    });
});
