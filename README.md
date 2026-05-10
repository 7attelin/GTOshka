# Бот-помощник для сдачи нормативов

Telegram-бот для помощи студентам в подготовке и сдаче вузовских нормативов и нормативов ГТО.

## 📋 Возможности

- **Вузовские нормативы**
  - Нормативы СПО
  - Нормативы ВО (с несколькими изображениями)
  
- **Нормативы ГТО**
  - Выбор ступени (6, 7, 8) с указанием возраста
  - Просмотр нормативов по каждой ступени
  - Рекомендации для каждой ступени
  - Ссылки на официальные ресурсы ГТО
  
- **Инфо**
  - Полезные ссылки на сайт института и ГТО
  - Дополнительная информация

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Получение токена бота

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Придумайте имя и username для бота
4. Скопируйте полученный токен

### 3. Настройка

Создайте файл `.env` в корне проекта:

```bash
cp .env.example .env
```

Откройте `.env` и вставьте ваш токен:

```
TOKEN=ваш_токен_от_botfather
```

### 4. Добавление изображений

Поместите ваши изображения в папку `data/images/`:

```
data/images/
├── spo_normativy.jpg          # Нормативы СПО
├── vo_normativy_1.jpg         # Нормативы ВО (часть 1)
├── vo_normativy_2.jpg         # Нормативы ВО (часть 2)
├── vo_normativy_3.jpg         # Нормативы ВО (часть 3)
├── gto_stage_6.jpg            # ГТО ступень 6
├── gto_stage_7.jpg            # ГТО ступень 7
└── gto_stage_8.jpg            # ГТО ступень 8
```

> ⚠️ Если у вас другое количество изображений, обновите файл `config.py`

### 5. Запуск бота

```bash
python bot.py
```

## 🔧 Настройка

### Изменение текстов и ссылок

Все настройки находятся в файле `config.py`:

- `INSTITUTE_SITE` - ссылка на сайт вашего института
- `GTO_MAIN_SITE` - основная ссылка на сайт ГТО
- `GTO_STAGE_LINKS` - ссылки на страницы конкретных ступеней
- `GTO_RECOMMENDATIONS` - рекомендации для каждой ступени
- `IMAGES` - пути к изображениям
- Тексты сообщений

### Обновление рекомендаций

Отредактируйте словарь `GTO_RECOMMENDATIONS` в `config.py`:

```python
GTO_RECOMMENDATIONS = {
    6: """Ваш текст рекомендаций для ступени 6""",
    7: """Ваш текст рекомендаций для ступени 7""",
    8: """Ваш текст рекомендаций для ступени 8""",
}
```

## 🖥️ Развертывание на сервере

### Требования для продакшена

- Python 3.8+
- Постоянное подключение к интернету
- Доменное имя (для webhook режима)

### Режимы работы

#### 1. Polling (для разработки и тестирования)

Используется по умолчанию в `bot.py`:

```python
app.run_polling(allowed_updates=Update.ALL_TYPES)
```

Просто запустите скрипт на сервере:

```bash
python bot.py
```

Для работы в фоне используйте `nohup`, `screen` или `systemd`.

#### 2. Webhook (для продакшена)

Рекомендуемый режим для промышленных серверов.

Пример настройки webhook:

```python
# В функции main() замените run_polling на:
app.run_webhook(
    listen='0.0.0.0',
    port=8443,
    url_path='YOUR_BOT_TOKEN',
    webhook_url='https://your-domain.com/YOUR_BOT_TOKEN',
    cert='./cert.pem',
    key='./private.key'
)
```

### Пример systemd сервиса

Создайте файл `/etc/systemd/system/normativ-bot.service`:

```ini
[Unit]
Description=Telegram Bot for Normativs
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/bot
ExecStart=/usr/bin/python3 /path/to/bot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Активируйте сервис:

```bash
sudo systemctl enable normativ-bot
sudo systemctl start normativ-bot
sudo systemctl status normativ-bot
```

## 📁 Структура проекта

```
.
├── bot.py                 # Основной код бота
├── config.py              # Конфигурация и тексты
├── requirements.txt       # Зависимости
├── .env                   # Токен бота (не коммитить!)
├── .env.example           # Пример .env
├── README.md              # Этот файл
└── data/
    └── images/            # Изображения нормативов
```

## 🎯 Как работает навигация

Бот использует **редактирование сообщений** вместо отправки новых:

1. При нажатии на кнопку сообщение **обновляется** (текст + клавиатура)
2. При просмотре изображений старое сообщение **удаляется**, новое отправляется с фото
3. Это создаёт эффект "интерактивного меню" без спама сообщениями

## 🔒 Безопасность

- Никогда не коммитьте файл `.env` в репозиторий
- Добавьте `.env` в `.gitignore`
- Используйте переменные окружения для чувствительных данных

## 🤝 Вклад в проект

1. Fork репозиторий
2. Создайте ветку (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📝 Лицензия

Этот проект создан для образовательных целей.

## ❓ Вопросы?

Обратитесь к разработчику или изучите документацию [python-telegram-bot](https://docs.python-telegram-bot.org/).
