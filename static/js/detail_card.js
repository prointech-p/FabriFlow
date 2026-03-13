$(document).ready(function() {
    // Переменная для хранения графика
    var completionChart = null;

    // ФЛАГ ДЛЯ ОТСЛЕЖИВАНИЯ ИЗМЕНЕНИЙ
    let dataChanged = false;
    
    // Обработчик клика по кнопке просмотра
    $('.view-detail').on('click', function() {
        var detailId = $(this).data('detail-id');
        loadDetailData(detailId);
        // Сбрасываем флаг при открытии нового модального окна
        dataChanged = false;
    });
    
    // ОБРАБОТЧИК ЗАКРЫТИЯ МОДАЛЬНОГО ОКНА
    $('#detailModal').on('hidden.bs.modal', function () {
        if (dataChanged) {
            // Показываем уведомление о перезагрузке
            showNotification('info', 'Данные изменены. Страница будет перезагружена...');
            
            // Небольшая задержка для показа уведомления
            setTimeout(function() {
                location.reload();
            }, 500);
        }
    });

    // Функция загрузки данных детали
    function loadDetailData(detailId) {
        // Показываем загрузчик, скрываем контент
        $('#detailModalLoader').show();
        $('#detailModalContent').hide();
        
        // Показываем модальное окно
        var detailModal = new bootstrap.Modal(document.getElementById('detailModal'));
        detailModal.show();
        
        // Загружаем данные через AJAX
        $.ajax({
            url: '/details/' + detailId + '/',
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                // Заполняем основную информацию
                $('#detailArticle').text(data.article);
                $('#detailName').text(data.name);
                $('#detailDrawing').text('Чертёж: ' + (data.drawing_number || 'не указан'));
                $('#detailCreated').text(data.created_at);
                $('#detailUpdated').text(data.updated_at);
                $('#plannedDate').text(data.planned_completion_date || 'не указана');
                $('#detailDescription').text(data.description || 'Нет описания');
                
                // Статус
                var statusClass = 'bg-secondary';
                if (data.status.name.toLowerCase().includes('готов')) {
                    statusClass = 'bg-success';
                } else if (data.status.name.toLowerCase().includes('работе')) {
                    statusClass = 'bg-warning';
                } else if (data.status.name.toLowerCase().includes('ожида')) {
                    statusClass = 'bg-info';
                }
                $('#detailStatus').text(data.status.name).addClass(statusClass);
                
                // Процент готовности
                $('#completionPercent').text(data.completion_percent + '%');
                $('#completionProgressBar').css('width', data.completion_percent + '%');
                
                // График готовности
                updateCompletionChart(data.completion_percent);
                
                // Заполняем таблицу этапов
                renderStagesTable(data.stages);
                
                // Сохраняем ID детали для кнопок
                $('#recalculateBtn').data('detail-id', detailId);
                $('#editDetailBtn').data('detail-id', detailId);
                
                // Скрываем загрузчик, показываем контент
                $('#detailModalLoader').hide();
                $('#detailModalContent').show();
            },
            error: function(xhr, status, error) {
                $('#detailModalLoader').hide();
                alert('Ошибка при загрузке данных детали: ' + error);
            }
        });
    }
    
    // Функция обновления графика готовности
    function updateCompletionChart(percent) {
        var ctx = document.getElementById('completionChart').getContext('2d');
        
        if (completionChart) {
            completionChart.destroy();
        }
        
        completionChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [percent, 100 - percent],
                    backgroundColor: ['#28a745', '#e9ecef'],
                    borderWidth: 0,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                cutout: '70%',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            }
        });
    }
    
    // Функция отрисовки таблицы этапов
    function renderStagesTable(stages) {
        var tbody = $('#stagesTableBody');
        tbody.empty();
        
        if (stages.length === 0) {
            tbody.append('<tr><td colspan="7" class="text-center py-4">Нет этапов для данной детали</td></tr>');
            return;
        }
        
        stages.forEach(function(stage) {
            var row = $('<tr>');
            
            // Номер этапа
            row.append($('<td>').text(stage.order_num));
            
            // Операция
            row.append($('<td>').text(stage.stage_type.name));
            
            // Станок
            var machineCell = $('<td>');
            if (stage.machine) {
                machineCell.html(`
                    <div class="machine-badge">
                        <i class="bi bi-cpu"></i>
                        ${stage.machine.inventory_number}
                        <small class="text-muted">(${stage.machine.workshop})</small>
                        <br>
                        <small class="text-muted">Загрузка: ${stage.machine.load_percent}%</small>
                    </div>
                `);
            } else {
                machineCell.html('<span class="text-muted">—</span>');
            }
            row.append(machineCell);
            
            // Статус
            var statusCell = $('<td>');
            if (stage.is_completed) {
                statusCell.html('<span class="badge bg-success stage-badge"><i class="bi bi-check-circle-fill"></i> Выполнен</span>');
            } else if (stage.is_overdue) {
                statusCell.html('<span class="badge bg-danger stage-badge"><i class="bi bi-exclamation-triangle-fill"></i> Просрочен</span>');
            } else if (stage.machine) {
                statusCell.html('<span class="badge bg-warning stage-badge"><i class="bi bi-gear-fill"></i> В работе</span>');
            } else {
                statusCell.html('<span class="badge bg-secondary stage-badge"><i class="bi bi-clock"></i> Ожидание</span>');
            }
            row.append(statusCell);
            
            // Дата выполнения
            var dateCell = $('<td>');
            if (stage.completion_date) {
                dateCell.text(stage.completion_date);
            } else {
                dateCell.html('<span class="text-muted">—</span>');
            }
            row.append(dateCell);
            
            // Примечания
            var notesCell = $('<td>');
            if (stage.notes) {
                notesCell.html(`<i class="bi bi-chat-dots text-muted" data-bs-toggle="tooltip" title="${stage.notes}"></i>`);
            } else {
                notesCell.html('<span class="text-muted">—</span>');
            }
            row.append(notesCell);
            
            // Действия
            var actionsCell = $('<td>');
            var actionsDiv = $('<div class="btn-group btn-group-sm">');
            
            if (!stage.is_completed) {
                actionsDiv.append(`
                    <button class="btn btn-outline-success complete-stage" 
                            data-stage-id="${stage.id}" 
                            title="Отметить выполнение">
                        <i class="bi bi-check-lg"></i>
                    </button>
                `);
            }
            
            if (!stage.machine) {
                actionsDiv.append(`
                    <button class="btn btn-outline-warning assign-machine" 
                            data-stage-id="${stage.id}" 
                            title="Назначить станок">
                        <i class="bi bi-cpu"></i>
                    </button>
                `);
            }
            
            // actionsDiv.append(`
            //     <button class="btn btn-outline-secondary" title="Редактировать">
            //         <i class="bi bi-pencil"></i>
            //     </button>
            // `);
            actionsDiv.append(`
                <a href="/admin/core/stage/${stage.id}/change/"
                    target="_blank"
                    class="btn btn-outline-secondary"
                    title="Редактировать"
                >
                    <i class="bi bi-pencil"></i>
                </a>
            `);

            actionsCell.append(actionsDiv);
            row.append(actionsCell);
            
            tbody.append(row);
        });
        
        // Инициализируем tooltips
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Обработчик кнопки пересчета готовности
    $('#recalculateBtn').on('click', function() {
        var detailId = $(this).data('detail-id');
        
        $.ajax({
            url: '/details/' + detailId + '/recalculate/',
            method: 'POST',
            headers: {
                'X-CSRFToken': window.CSRF_TOKEN
            },
            success: function(response) {
                if (response.success) {
                    // УСТАНАВЛИВАЕМ ФЛАГ ИЗМЕНЕНИЙ
                    dataChanged = true;

                    $('#completionPercent').text(response.completion_percent + '%');
                    $('#completionProgressBar').css('width', response.completion_percent + '%');
                    updateCompletionChart(response.completion_percent);
                    
                    // Показываем уведомление
                    showNotification('success', response.message);
                }
            },
            error: function() {
                showNotification('danger', 'Ошибка при пересчете готовности');
            }
        });
    });
    
    // Обработчик отметки выполнения этапа (через делегирование)
    $(document).on('click', '.complete-stage', function() {
        var stageId = $(this).data('stage-id');
        var detailId = $('#recalculateBtn').data('detail-id');
        var button = $(this);
        
        if (!confirm('Отметить этот этап как выполненный?')) {
            return;
        }
        
        $.ajax({
            url: '/details/' + detailId + '/stage/' + stageId + '/complete/',
            method: 'POST',
            headers: {
                'X-CSRFToken': window.CSRF_TOKEN
            },
            success: function(response) {
                if (response.success) {
                    // УСТАНАВЛИВАЕМ ФЛАГ ИЗМЕНЕНИЙ
                    dataChanged = true;

                    // Обновляем строку этапа
                    button.closest('tr').find('td:eq(4)').html('<span class="badge bg-success stage-badge"><i class="bi bi-check-circle-fill"></i> Выполнен</span>');
                    button.closest('td').find('.complete-stage').remove();
                    
                    // Обновляем процент готовности
                    $('#completionPercent').text(response.completion_percent + '%');
                    $('#completionProgressBar').css('width', response.completion_percent + '%');
                    updateCompletionChart(response.completion_percent);
                    
                    showNotification('success', response.message);
                } else {
                    showNotification('warning', response.message);
                }
            },
            error: function() {
                showNotification('danger', 'Ошибка при отметке этапа');
            }
        });
    });
    
    // Функция показа уведомлений
    function showNotification(type, message) {
        var alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3" 
                 style="z-index: 9999; min-width: 300px;" role="alert">
                <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}-fill me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        $('body').append(alertHtml);
        setTimeout(function() {
            $('.alert').alert('close');
        }, 3000);
    }
    
    // Обработчик кнопки редактирования
    $('#editDetailBtn').on('click', function() {
        var detailId = $(this).data('detail-id');
        var adminUrl = '/admin/core/detail/' + detailId + '/change/';

        // УСТАНАВЛИВАЕМ ФЛАГ ИЗМЕНЕНИЙ (так как открывается админка для редактирования)
        dataChanged = true;

        window.open(adminUrl, '_blank');
    });

    // Дополнительно: обработчик для назначения станка (если есть такая функция)
    $(document).on('click', '.assign-machine', function() {
        // Если есть логика назначения станка, тоже устанавливаем флаг
        dataChanged = true;
    });
});
