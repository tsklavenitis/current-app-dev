// custom_admin.js
document.addEventListener('DOMContentLoaded', function () {
    const toggleFiltersButton = document.createElement('button');
    toggleFiltersButton.textContent = 'Toggle Filters';
    toggleFiltersButton.className = 'toggle-filters';
    document.querySelector('.changelist-filter').insertAdjacentElement('beforebegin', toggleFiltersButton);

    toggleFiltersButton.addEventListener('click', function () {
        document.querySelector('.changelist-filter').classList.toggle('hidden');
    });

    const printButton = document.createElement('button');
    printButton.textContent = 'Print';
    printButton.className = 'print-button';
    document.querySelector('.object-tools').insertAdjacentElement('afterend', printButton);
    
    printButton.addEventListener('click', function () {
        window.print();
    });
});
