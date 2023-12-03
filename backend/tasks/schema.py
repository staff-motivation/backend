from drf_spectacular.utils import extend_schema


class SCHEMA:
    task = {
        'list': extend_schema(
            summary='Получение списка задач.',
            description=(
                'Получение списка задач текущего пользователя или тимлида.'
                '\n\nУпорядочено по дате создания (сначала новые).'
                '\n\nФильтрация задач по статусу и просроченным дедлайнам.'
                '\n\nПример запроса с фильтрацией - Новые задачи:'
                'http://example.com/api/tasks/?status=createdx'
                '\n\nПример запроса с фильтрацией - На подтверждении:'
                'http://example.com/api/tasks/?status=sent_for_review'
                '\n\nПример запроса с фильтрацией - Просроченные:'
                'http://example.com/api/tasks/?is_overdue=true'
            ),
        ),
        'retrieve': extend_schema(summary='Получение задачи по id.'),
        'destroy': extend_schema(summary='Удаление задачи по id.'),
        'update': extend_schema(
            summary='Обновление задачи по id.',
            description='Меняет объект целиком.',
        ),
        'partial_update': extend_schema(
            summary='Обновление задачи по id.',
            description='Изменяет только переданные поля.',
        ),
        'update_overdue_tasks': extend_schema(
            summary='Обновление статуса просроченных задач.'
        ),
        'create': extend_schema(
            summary='Создание новой задачи тимлидером.',
            description=(
                'Возможные ошибки: '
                '\n\n400: Если указать дедлайн прошедшей датой. '
                '\n\n400: Eсли указанного сотрудника нет в указанном '
                'департаменте.'
            ),
        ),
        'send_for_review': extend_schema(
            summary=(
                'Отправка задачи текущего пользователя на проверку '
                'тимлидеру.'
            )
        ),
        'review_task': extend_schema(
            summary='Проверка задачи тимлидом и изменение её статуса.'
        ),
    }


task_schema = SCHEMA()
