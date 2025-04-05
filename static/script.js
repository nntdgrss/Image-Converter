document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("uploadForm");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    // Проверка, выбран ли файл
    const fileInput = document.getElementById("fileInput");
    if (!fileInput.files.length) {
      showMessage("Пожалуйста, выберите файл для конвертации", "error");
      return;
    }

    // Показать индикатор загрузки
    showLoading(true);

    try {
      // Отправка формы с использованием Fetch API
      const formData = new FormData(form);
      const response = await fetch("/convert", {
        method: "POST",
        body: formData,
      });

      // Проверка на тип ответа (JSON = ошибка, Blob = файл)
      const contentType = response.headers.get("content-type");

      if (contentType && contentType.includes("application/json")) {
        // Если сервер вернул JSON, значит это сообщение об ошибке
        const data = await response.json();
        throw new Error(
          data.error || data.detail || "Неизвестная ошибка при конвертации"
        );
      }

      if (!response.ok) {
        throw new Error(`Ошибка сервера: ${response.status}`);
      }

      // Получаем имя файла из заголовков, если оно там есть
      const contentDisposition = response.headers.get("content-disposition");
      let filename = "converted-file";

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      // Получаем бинарные данные и создаем объект Blob
      const blob = await response.blob();

      // Скачиваем файл
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      showMessage("Файл успешно конвертирован!", "success");
    } catch (error) {
      showMessage(
        error.message || "Произошла ошибка при конвертации файла",
        "error"
      );
    } finally {
      showLoading(false);
    }
  });

  // Функция для отображения сообщений (ошибки/успех)
  function showMessage(message, type) {
    // Удаляем предыдущие сообщения
    const existingMessages = document.querySelectorAll(".message-alert");
    existingMessages.forEach((el) => el.remove());

    // Создаем новое сообщение
    const messageEl = document.createElement("div");
    messageEl.className =
      "message-alert fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 transform transition-transform duration-300 ease-in-out";

    if (type === "error") {
      messageEl.className += " bg-red-100 border border-red-400 text-red-700";
    } else {
      messageEl.className +=
        " bg-green-100 border border-green-400 text-green-700";
    }

    messageEl.textContent = message;
    document.body.appendChild(messageEl);

    // Анимация появления
    setTimeout(() => {
      messageEl.classList.add("translate-y-1");
    }, 10);

    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
      messageEl.classList.add("opacity-0");
      setTimeout(() => {
        if (messageEl.parentNode) {
          messageEl.parentNode.removeChild(messageEl);
        }
      }, 300);
    }, 5000);
  }

  // Функция для отображения/скрытия индикатора загрузки
  function showLoading(isLoading) {
    // Находим или создаем контейнер для загрузки
    let loadingIndicator = document.getElementById("loading-indicator");

    if (!loadingIndicator && isLoading) {
      loadingIndicator = document.createElement("div");
      loadingIndicator.id = "loading-indicator";
      loadingIndicator.className =
        "fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50";
      loadingIndicator.innerHTML = `
        <div class="bg-white p-5 rounded-lg flex flex-col items-center">
          <div class="w-16 h-16 border-t-4 border-b-4 border-blue-500 rounded-full animate-spin"></div>
          <p class="mt-3 text-gray-700 font-medium">Идет конвертация...</p>
        </div>
      `;
      document.body.appendChild(loadingIndicator);
    } else if (loadingIndicator && !isLoading) {
      loadingIndicator.remove();
    }

    // Блокируем/разблокируем кнопку конвертации
    const convertButton = document.getElementById("convertButton");
    if (convertButton) {
      convertButton.disabled = isLoading;
      if (isLoading) {
        convertButton.classList.add("opacity-50", "cursor-not-allowed");
      } else {
        convertButton.classList.remove("opacity-50", "cursor-not-allowed");
      }
    }
  }
});
