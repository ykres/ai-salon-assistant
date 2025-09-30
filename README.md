# 🤖 AI-Ассистент для Салона Красоты

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green?style=flat-square&logo=fastapi)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange?style=flat-square&logo=openai)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=flat-square&logo=telegram)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

Интеллектуальный ассистент для салонов красоты с двумя интерфейсами: **Telegram-бот** и **веб-чат виджет**. Использует OpenAI Assistant API для общения с клиентами и автоматического сохранения записей в Google Таблицы.

## ✨ Основные возможности

- 💬 **Умный диалог** с клиентами через Telegram или веб-сайт
- 📅 **Автоматическая запись** клиентов на услуги
- 📊 **Интеграция с Google Sheets** для хранения записей
- 🎨 **Готовый веб-сайт** салона красоты с чат-виджетом
- 🔄 **Единая система** управления записями из разных источников

## 🏗️ Архитектура системы

```
┌─────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│   Telegram Bot  │    │   Web Widget    │    │  OpenAI Assistant│
│                 │    │                 │    │                  │
│  • Polling      │    │  • REST API     │    │  • GPT-4         │
│  • Commands     │◄──►│  • FastAPI      │◄──►│  • Tools API     │
│  • Messages     │    │  • CORS         │    │  • Conversations │
└─────────────────┘    └─────────────────┘    └──────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────┐
                    │   Google Sheets     │
                    │                     │
                    │  • Записи клиентов  │
                    │  • История          │
                    │  • Отчетность       │
                    └─────────────────────┘
```

## 🛠️ Технологический стек

### Backend
- **Python 3.10+** - основной язык
- **FastAPI** - веб-фреймворк для API
- **python-telegram-bot** - Telegram Bot API
- **OpenAI Python SDK** - интеграция с GPT
- **gspread** - работа с Google Sheets

### Frontend
- **Vanilla JavaScript** - чат-виджет
- **HTML/CSS** - адаптивный дизайн
- **REST API** - связь с бэкендом

### Интеграции
- **OpenAI Assistant API** - ИИ-диалоги
- **Google Sheets API** - хранение данных
- **Telegram Bot API** - мессенджер

## 🚀 Быстрый старт

### 1. Подготовка окружения

```bash
# Клонирование репозитория
git clone https://github.com/your-username/ai-beauty-assistant.git
cd ai-beauty-assistant

# Создание виртуального окружения
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_ASSISTANT_ID=asst_your-assistant-id

# Telegram Bot
TG_BOT_TOKEN=your-telegram-bot-token

# Google Sheets Integration
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service-account.json
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id
GOOGLE_SHEETS_WORKSHEET=Записи  # необязательно

# Optional
GOOGLE_SERVICE_ACCOUNT=service-account@project.iam.gserviceaccount.com
```

### 3. Настройка Google Sheets

1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Google Sheets API и Google Drive API
3. Создайте сервисный аккаунт и скачайте JSON-ключ
4. Создайте Google Таблицу и предоставьте доступ сервисному аккаунту
5. Скопируйте ID таблицы из URL

### 4. Настройка OpenAI Assistant

1. Войдите в [OpenAI Platform](https://platform.openai.com/)
2. Создайте нового Assistant с инструментом:

```json
{
  "name": "save_booking_data",
  "description": "Сохраняет данные записи клиента в Google Таблицы",
  "parameters": {
    "type": "object",
    "properties": {
      "name": {"type": "string", "description": "Имя клиента"},
      "phone": {"type": "string", "description": "Телефон клиента"},
      "service": {"type": "string", "description": "Выбранная услуга"},
      "datetime": {"type": "string", "description": "Дата и время записи"},
      "master_category": {"type": "string", "description": "Категория мастера"},
      "comments": {"type": "string", "description": "Дополнительные комментарии"}
    },
    "required": ["name", "phone", "service", "datetime"]
  }
}
```

### 5. Запуск приложения

#### Telegram Bot
```bash
python bot.py
```

#### Веб-сервер (FastAPI)
```bash
# Запуск локально
uvicorn server:app --host 0.0.0.0 --port 8000

# Или через таск (если настроен)
# Используйте VS Code Task: "Run FastAPI backend (uvicorn)"
```

#### Веб-сайт
Откройте `index.html` в браузере или разверните на веб-сервере.

## 📱 Использование

### Telegram Bot
1. Найдите бота по имени в Telegram
2. Отправьте `/start` для начала диалога
3. Общайтесь с ботом на естественном языке
4. Бот поможет записаться на услуги

### Веб-чат
1. Откройте сайт салона (`index.html`)
2. Нажмите кнопку "Чат" в правом нижнем углу
3. Общайтесь с ассистентом через веб-интерфейс

## 🔌 API Endpoints

### POST `/chat/start`
Создает новую сессию чата
```json
Response: {"sessionId": "uuid"}
```

### POST `/chat/message`
Отправляет сообщение ассистенту
```json
Request: {"sessionId": "uuid", "text": "Хочу записаться на стрижку"}
Response: {"reply": "Конечно! На какое время хотели бы записаться?"}
```

## 📊 Структура данных в Google Sheets

| Timestamp | Name | Phone | Service | Datetime | Master Category | Comments |
|-----------|------|--------|---------|----------|----------------|----------|
| 2025-01-15T10:30:00 | Анна | +7999... | Стрижка | 2025-01-20 14:00 | Топ-стилист | Длинные волосы |

## 🎨 Демо-сайт

В проекте включен готовый сайт салона красоты (`index.html`) с:
- 🏠 Главной страницей
- 📋 Каталогом услуг  
- 💰 Прайс-листом
- 🖼️ Галереей работ
- 📞 Контактами
- 💬 Встроенным чат-виджетом

## 🔧 Конфигурация

### Настройка веб-чата для продакшена

Для использования в продакшене измените URL бэкенда в `index.html`:

```javascript
// Замените на ваш публичный домен
const BACKEND_URL = 'https://your-domain.com';
```

Или используйте туннель для разработки:
```bash
# ngrok
ngrok http 8000

# cloudflare tunnel  
cloudflared tunnel --url http://localhost:8000
```

### CORS настройки

В `server.py` настройте CORS для продакшена:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # укажите домен
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 📂 Структура проекта

```
ai-beauty-assistant/
├── 📄 README.md           # Документация
├── 🤖 bot.py             # Telegram Bot
├── 🌐 server.py          # FastAPI веб-сервер  
├── 🎨 index.html         # Сайт салона + чат
├── 📋 requirements.txt   # Python зависимости
├── 🔐 .env              # Переменные окружения
├── 📊 data/             # Локальные данные
│   ├── threads.json     # Сессии Telegram
│   └── web_threads.json # Сессии веб-чата
└── 📦 app/             # Модули приложения
    ├── assistants.py   # OpenAI Assistant
    ├── config.py       # Конфигурация
    ├── sheets_tool.py  # Google Sheets
    └── thread_store.py # Управление сессиями
```

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature-ветку (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## 👨‍💻 Автор

**Yury** - [GitHub Profile](https://github.com/ykres)

---

⭐ Поставьте звезду, если проект был полезен!
