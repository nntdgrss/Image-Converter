import os
from pathlib import Path

# Базовые пути
BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
CONVERTED_DIR = BASE_DIR / "converted"

# Создание необходимых директорий
UPLOADS_DIR.mkdir(exist_ok=True)
CONVERTED_DIR.mkdir(exist_ok=True)

# Настройки приложения
APP_TITLE = "Media Converter"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Поддерживаемые форматы изображений
SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "webp", "bmp", "gif", "tiff"]

# Настройки конвертации
CONVERSION_SETTINGS = {
    "jpeg": {"quality": 95, "optimize": True},
    "jpg": {"quality": 95, "optimize": True},
    "png": {"optimize": True},
    "webp": {"quality": 85, "method": 6},
}

# Логирование
LOG_FILE = BASE_DIR / "app.log"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = "INFO"
