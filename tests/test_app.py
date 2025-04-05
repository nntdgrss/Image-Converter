import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import magic
from main import app
from config import SUPPORTED_IMAGE_FORMATS
from utils.utils import is_format_supported, validate_image_file

client = TestClient(app)

def test_root_endpoint():
    """Тест главной страницы"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_supported_formats():
    """Тест проверки поддерживаемых форматов"""
    for format in ["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"]:
        assert is_format_supported(format)
        assert is_format_supported(format.upper())
    
    assert not is_format_supported("xyz")
    assert not is_format_supported("")

@pytest.mark.asyncio
async def test_validate_image_file(tmp_path):
    """Тест валидации файлов изображений"""
    # Создаем тестовое изображение
    test_image = tmp_path / "test.png"
    from PIL import Image
    image = Image.new('RGB', (100, 100), color='red')
    image.save(test_image)
    
    # Создаем тестовый текстовый файл
    test_text = tmp_path / "test.txt"
    test_text.write_text("This is not an image")
    
    # Тестируем файлы
    class MockUploadFile:
        def __init__(self, path):
            self.path = path
            self.file = open(path, 'rb')
        
        async def read(self, size=None):
            return self.file.read(size)
        
        async def seek(self, offset):
            self.file.seek(offset)
            
        def close(self):
            self.file.close()
    
    # Проверяем изображение
    image_file = MockUploadFile(test_image)
    assert await validate_image_file(image_file)
    image_file.close()
    
    # Проверяем текстовый файл
    text_file = MockUploadFile(test_text)
    assert not await validate_image_file(text_file)
    text_file.close()

def test_convert_endpoint_validation():
    """Тест валидации входных данных для конвертации"""
    # Тест без файла
    response = client.post("/convert", data={"targetFormat": "png"})
    assert response.status_code == 422
    
    # Тест без формата
    with open("tests/test_files/test.png", "rb") as f:
        response = client.post("/convert", files={"file": f})
        assert response.status_code == 422

    # Тест с неподдерживаемым форматом
    with open("tests/test_files/test.png", "rb") as f:
        response = client.post(
            "/convert",
            files={"file": f},
            data={"targetFormat": "xyz"}
        )
        assert response.status_code == 400
        assert "не поддерживается" in response.json()["detail"]

@pytest.fixture(scope="session", autouse=True)
def setup_test_files(tmp_path_factory):
    """Создание тестовых файлов"""
    test_dir = tmp_path_factory.mktemp("test_files")
    test_image = test_dir / "test.png"
    
    # Создаем тестовое изображение
    image = Image.new('RGB', (100, 100), color='red')
    image.save(test_image)
    
    Path("tests/test_files").mkdir(parents=True, exist_ok=True)
    image.save("tests/test_files/test.png")
    
    return test_dir
