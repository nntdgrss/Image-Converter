# Simple Image Converter

Веб-приложение для конвертации изображений в различные форматы с использованием FastAPI и Python.

## Возможности

- Конвертация изображений в форматы: JPEG, PNG, WebP, GIF, BMP, TIFF
- Оптимизация изображений при конвертации
- Простой и удобный веб-интерфейс
- Асинхронная обработка файлов
- Автоматическая очистка временных файлов

## Требования

- Python 3.7+
- pip

## Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/nntdgrs/File-Converter.git
cd File-Converter
```

2. Создайте виртуальное окружение и активируйте его:

```bash
python -m venv venv
source venv/bin/activate  # для Linux/macOS
# или
venv\Scripts\activate  # для Windows
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

## Запуск

Для запуска приложения выполните:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

После запуска приложение будет доступно по адресу: http://localhost:8000

## Использование

1. Откройте веб-интерфейс в браузере
2. Выберите изображение для конвертации
3. Выберите желаемый формат
4. Нажмите кнопку "Конвертировать"
5. Скачайте конвертированное изображение

## Структура проекта

```
File-Converter/
├── main.py           # Основной файл приложения
├── config.py         # Конфигурация приложения
├── requirements.txt  # Зависимости проекта
├── static/          # Статические файлы
│   └── script.js    # JavaScript для фронтенда
├── templates/       # HTML шаблоны
│   └── index.html  # Главная страница
└── utils/          # Вспомогательные функции
    └── utils.py    # Утилиты для работы с файлами
```

## API Endpoints

- `GET /` - Главная страница
- `POST /convert` - API endpoint для конвертации изображений

## Лицензия

MIT License

## Автор

[nntdgrs](https://github.com/nntdgrs)
