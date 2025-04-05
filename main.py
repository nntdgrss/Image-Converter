import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, BackgroundTasks, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
from datetime import datetime
from starlette.responses import StreamingResponse, JSONResponse
from utils.utils import is_format_supported, validate_image_file, convert_image
from config import (
    APP_TITLE, MAX_FILE_SIZE, LOG_FILE, LOG_FORMAT, LOG_LEVEL,
    UPLOADS_DIR, CONVERTED_DIR
)

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("converter_app")

# Создаем экземпляр FastAPI
app = FastAPI(
    title=APP_TITLE,
    description="API для конвертации изображений в различные форматы",
    version="1.0.0"
)

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настраиваем шаблонизатор
templates = Jinja2Templates(directory="templates")

async def clean_up_files(path1: str, path2: str = None):
    """Асинхронная функция для очистки временных файлов."""
    try:
        if path1 and await delete_file(path1) and path2:
            await delete_file(path2)
    except Exception as e:
        logger.error(f"Ошибка при очистке файлов: {e}")

async def delete_file(file_path: str) -> bool:
    """Удаляет файл и возвращает статус операции."""
    try:
        file_path = str(file_path)  # Преобразуем Path в строку если нужно
        if file_path and (str(UPLOADS_DIR) in file_path or str(CONVERTED_DIR) in file_path):
            import os
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Удален файл: {file_path}")
                return True
        return False
    except Exception as e:
        logger.error(f"Ошибка при удалении файла {file_path}: {e}")
        return False

@app.get("/")
async def root(request: Request):
    """Главная страница приложения."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/convert")
async def convert(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    targetFormat: str = Form(...)
):
    """
    Конвертирует загруженное изображение в указанный формат.
    
    Args:
        background_tasks: Фоновые задачи FastAPI
        file: Загруженный файл
        targetFormat: Целевой формат конвертации
    
    Returns:
        StreamingResponse с конвертированным файлом или JSONResponse с ошибкой
    """
    start_time = datetime.now()
    
    try:
        # Проверка формата
        if not is_format_supported(targetFormat):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Формат {targetFormat} не поддерживается"
            )

        # Проверка размера файла
        if file.file._file.tell() > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Размер файла превышает максимально допустимый ({MAX_FILE_SIZE / 1024 / 1024:.1f} МБ)"
            )

        # Сброс указателя и проверка типа файла
        await file.seek(0)
        if not await validate_image_file(file):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Загруженный файл не является изображением"}
            )

        # Получение оригинального расширения и генерация UUID
        original_extension = file.filename.split('.')[-1].lower()
        file_id = str(uuid.uuid4())

        # Пути для файлов
        upload_path = UPLOADS_DIR / f"{file_id}.{original_extension}"
        converted_path = CONVERTED_DIR / f"{file_id}.{targetFormat.lower()}"

        # Сохранение загруженного файла
        content = await file.read()
        with open(upload_path, "wb") as buffer:
            buffer.write(content)

        # Конвертация
        if not await convert_image(str(upload_path), str(converted_path), targetFormat.lower()):
            raise Exception("Ошибка при конвертации изображения")

        # Подготовка ответа
        original_filename = '.'.join(file.filename.split('.')[:-1])
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Конвертация завершена за {processing_time:.2f} секунд")

        # Отправка файла
        file_like = open(converted_path, mode="rb")
        response = StreamingResponse(
            file_like,
            media_type=f"image/{targetFormat.lower()}",
            headers={
                "Content-Disposition": f"attachment; filename={original_filename}.{targetFormat.lower()}"
            }
        )

        # Добавление задачи очистки
        background_tasks.add_task(clean_up_files, str(upload_path), str(converted_path))
        
        return response

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Ошибка при конвертации файла: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Внутренняя ошибка сервера при конвертации файла"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
