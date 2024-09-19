function toggleCheckboxes(checked) {
    var checkboxes = document.querySelectorAll('input[type="checkbox"][name="selected_files"]');
    checkboxes.forEach(function(checkbox) {
        checkbox.checked = checked;
    });
}

function selectAll() {
    toggleCheckboxes(true);
}

function deselectAll() {
    toggleCheckboxes(false);
}

function filterFiles() {
    var filter = document.getElementById('file-type-filter').value;
    var fileItems = document.querySelectorAll('.file-item');

    fileItems.forEach(function(item) {
        var mimeType = item.getAttribute('data-mime-type');

        if (filter === 'all' || (mimeType && mimeType.startsWith(filter))) {
            item.style.display = 'table-row';  // Показываем элемент, если он соответствует фильтру
        } else {
            item.style.display = 'none';  // Скрываем элемент, если он не соответствует фильтру
        }
    });

    // Обновляем таблицу после фильтрации, чтобы она сохраняла фиксированные размеры
    var table = document.querySelector('.file-table');
    table.style.tableLayout = 'fixed';  // Принудительно фиксируем ширину столбцов
}

