function openModal(id) {
    const modal = document.getElementById(id);
    if (!modal) return;

    modal.classList.remove('hidden');
    modal.classList.add('flex');
    document.body.classList.add('overflow-hidden');
}

function closeModal(event, id) {
    if (event) event.stopPropagation();

    const modal = document.getElementById(id);
    if (!modal) return;

    modal.classList.add('hidden');
    modal.classList.remove('flex');
    document.body.classList.remove('overflow-hidden');
}

function openDeleteModal(action, itemName) {
    const form = document.getElementById('deleteForm');
    const item = document.getElementById('deleteItemName');

    if (!form || !item) return;

    form.action = action;
    item.textContent = itemName;
    openModal('deleteModal');
}

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('cancelDelete')?.addEventListener('click', function () {
        closeModal(null, 'deleteModal');
    });

    document.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape') return;

        document.querySelectorAll('[role="dialog"]:not(.hidden)').forEach(function (modal) {
            closeModal(null, modal.id);
        });
    });
});
