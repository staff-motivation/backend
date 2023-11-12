from io import BytesIO

from django.core.files import File
from PIL import Image


def get_image_file(name='test.png', ext='png', size=(5, 5), color=(256, 0, 0)):
    file_obj = BytesIO()
    image = Image.new('RGBA', size=size, color=color)
    image.save(file_obj, ext)
    file_obj.seek(0)
    return File(file_obj, name=name)
