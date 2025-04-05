import os

from PIL import Image
from fastapi import UploadFile

# Указываем поддерживаемые форматы для конвертации
SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "webp", "bmp", "gif", "tiff"]


async def validate_image_file(file: UploadFile) -> bool:
    header = await file.read(1024)
    await file.seek(0)

    import magic
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(header)

    return file_type.startswith('image/')


# Функция для проверки допустимости формата
def is_format_supported(format_name: str) -> bool:
    return format_name.lower() in SUPPORTED_IMAGE_FORMATS


# Функция для определения MIME-типа
def get_mime_type(format_name: str) -> str:
    format_name = format_name.lower()
    mime_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
        "gif": "image/gif",
        "bmp": "image/bmp",
        "tiff": "image/tiff"
    }
    return mime_map.get(format_name, "application/octet-stream")


# Расширенная функция конвертации
async def convert_image(input_path: str, output_path: str, target_format: str):
    try:
        # Открываем изображение с Pillow
        with Image.open(input_path) as img:
            # Специфические настройки для разных форматов
            if target_format.lower() in ["jpg", "jpeg"]:
                # Для JPEG указываем качество
                img.save(output_path, quality=95, optimize=True)
            elif target_format.lower() == "png":
                # Для PNG оптимизируем сжатие
                img.save(output_path, optimize=True)
            elif target_format.lower() == "webp":
                # Для WebP балансируем качество и размер
                img.save(output_path, quality=85, method=6)
            else:
                # Для других форматов используем стандартные настройки
                img.save(output_path)

        return True
    except Exception as e:
        print(f"Ошибка при конвертации: {str(e)}")
        return False


async def delete_file(file_path: str):
    """Удаляет файл по указанному пути."""
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Ошибка при удалении файла {file_path}: {e}")