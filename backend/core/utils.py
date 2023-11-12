from datetime import datetime, timezone
from io import BytesIO

from dateutil.relativedelta import relativedelta  # type: ignore
from django.core.files import File
from PIL import Image


def get_image_file(name='test.png', ext='png', size=(5, 5), color=(256, 0, 0)):
    file_obj = BytesIO()
    image = Image.new('RGBA', size=size, color=color)
    image.save(file_obj, ext)
    file_obj.seek(0)
    return File(file_obj, name=name)


PERIODS = {
    'years': ['лет', 'год', 'года'],
    'month': ['месяцев', 'месяц', 'месяца'],
    'days': ['дней', 'день', 'дня'],
}


def how_much_time_has_passed(dt: datetime) -> str:
    result = ''
    now = datetime.now(timezone.utc)
    delta = relativedelta(now, dt)
    result += get_time_str(delta.years, PERIODS['years'])
    result += get_time_str(delta.months, PERIODS['month'])
    result += get_time_str(delta.days, PERIODS['days'])
    return result.rstrip() if len(result) > 1 else 'Меньше одного дня'


def get_time_str(value: int, period_str: list[str]) -> str:
    if value == 0:
        return ''
    remainder = value % 10
    if remainder == 0 or (value % 100) in range(11, 19) or remainder >= 5:
        return f'{value} {period_str[0]} '
    elif remainder == 1:
        return f'{value} {period_str[1]} '
    return f'{value} {period_str[2]} '
