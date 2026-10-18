document.addEventListener('DOMContentLoaded', function () {
    const statusClasses = [
        'border-amber-200',
        'bg-amber-50',
        'text-amber-700',
        'focus:border-amber-500',
        'border-blue-200',
        'bg-blue-50',
        'text-blue-700',
        'focus:border-blue-500',
        'border-emerald-200',
        'bg-emerald-50',
        'text-emerald-700',
        'focus:border-emerald-500',
        'border-border',
        'bg-surface',
        'text-neutral',
        'focus:border-primary',
    ];

    document.querySelectorAll('[data-status-select]').forEach(function (select) {
        function applyStatusColor() {
            select.classList.remove(...statusClasses);

            const classesByStatus = {
                TODO: ['border-amber-200', 'bg-amber-50', 'text-amber-700', 'focus:border-amber-500'],
                IN_PROGRESS: ['border-blue-200', 'bg-blue-50', 'text-blue-700', 'focus:border-blue-500'],
                COMPLETED: ['border-emerald-200', 'bg-emerald-50', 'text-emerald-700', 'focus:border-emerald-500'],
            };

            select.classList.add(
                ...(classesByStatus[select.value] || [
                    'border-border',
                    'bg-surface',
                    'text-neutral',
                    'focus:border-primary',
                ]),
            );
        }

        applyStatusColor();
        select.addEventListener('change', applyStatusColor);
    });
});
