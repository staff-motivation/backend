from drf_spectacular.utils import extend_schema

from users.serializers import UploadUserImageSerializer


class SCHEMA:
    custom_dj_user = {
        'list': extend_schema(
            summary='Получение списка пользователей',
            description=(
                'Фильтрация по роли (role), по должности (position), по '
                'подразделению (department).\n\nПоиск по email, по имени '
                '(first_name), по фамилии (last_name)'
            ),
        ),
        'create': extend_schema(summary='Создание нового пользователя.'),
        'retrieve': extend_schema(summary='Получение пользователя по id.'),
        'destroy': extend_schema(summary='Удаление пользователя по id.'),
        'update': extend_schema(
            summary='Обновление пользователя по id.',
            description='Меняет объект целиком.',
        ),
        'partial_update': extend_schema(
            summary='Обновление пользователя по id.',
            description='Изменяет только переданные поля.',
        ),
        'me': extend_schema(
            summary='Получить информацию о себе.',
            description=(
                'Стаж (experience) и полный стаж (general_experience) '
                'выводятся в текстовом виде (количество лет, месяцев и дней). '
                'Если дата не установлена вернет: "Нет данных", если прошло '
                'меньше дня, то вернет: "Меньше одного дня"'
            ),
        ),
        'upload_image': extend_schema(
            summary='Загрузка изображения для профиля пользователя.',
            responses=UploadUserImageSerializer,
            request={
                'multipart/form-data': {
                    'type': 'object',
                    'properties': {
                        'image': {'type': 'string', 'format': 'binary'}
                    },
                },
            },
        ),
        'delete_image': extend_schema(
            summary='Удаление изображения профиля пользователя.'
        ),
        'progress': extend_schema(
            summary=(
                'Получение прогресса пользователя и его департамента за '
                'месяц.'
            ),
            description=(
                'Значение в процентах от всех выполненных задач за ' 'месяц.'
            ),
        ),
        'add_achievements': extend_schema(
            summary='Добавление достижений в профиль пользователя.'
        ),
    }
    short_user_profile = {
        'summary': 'Получение информации пользователя для хедера.'
    }


user_schema = SCHEMA()
