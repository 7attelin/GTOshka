import logging
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
import os

import config

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Различные пути к разным данным
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
FILES_DIR = DATA_DIR / "files"

# Список главного меню
def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📚 Вузовские Нормативы", callback_data="vuz_menu")],
        [InlineKeyboardButton("🎯 Нормативы ГТО", callback_data="gto_menu")],
        [InlineKeyboardButton("ℹ️ Инфо", callback_data="info")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Список меню вузовских нормативов
def get_vuz_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Нормативы СПО", callback_data="spo_standards")],
        [InlineKeyboardButton("Нормативы ВО", callback_data="vo_standards")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Список выбора ступени ГТО
def get_gto_stage_keyboard():
    keyboard = [
        [InlineKeyboardButton("Ступень 6 (13-15 лет)", callback_data="gto_stage_6")],
        [InlineKeyboardButton("Ступень 7 (16-17 лет)", callback_data="gto_stage_7")],
        [InlineKeyboardButton("Ступень 8 (18-29 лет)", callback_data="gto_stage_8")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Список для детального просмотра ступени ГТО
def get_gto_detail_keyboard(stage: int):
    keyboard = [
        [InlineKeyboardButton("📋 Рекомендации", callback_data=f"gto_rec_{stage}")],
        [InlineKeyboardButton("🔙 Назад к выбору ступени", callback_data="gto_menu")],
        [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            config.MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard()
        )

# Главное меню
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        config.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard()
    )

# Вузовские нормативы
async def vuz_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        config.VUZ_MENU_TEXT,
        reply_markup=get_vuz_menu_keyboard()
    )

# Нормативы СПО
async def show_spo_standards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Удаляем сообщение с меню
    try:
        await query.message.delete()
    except Exception:
        pass

    chat_id = query.message.chat_id
    file_name = "spo_1.jpg"
    image_path = IMAGES_DIR / file_name
    
    if image_path.exists():
        caption = "📊 Нормативы СПО"
        with open(image_path, 'rb') as photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=caption)

    # Финальное сообщение с ссылкой
    footer_text = (
        "-------------------------------\n"
        "Вузовские нормативы СПО\n"
        f"Ссылка на ГТО для подробного ознакомления: {config.GTO_MAIN_SITE}\n"
        "-------------------------------\n"
        "⚠️ Информация может обновляться, уточняйте актуальные данные на официальном сайте."
    )
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=footer_text,
        reply_markup=get_vuz_menu_keyboard()
    )

# Показ нормативов ВО (PDF файл + Описание + Текст)
async def show_vo_standards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Удаляем сообщение с меню
    try:
        await query.message.delete()
    except Exception:
        pass

    chat_id = query.message.chat_id
    pdf_file_name = "Контрольные и практические задания для ВО.pdf"
    pdf_path = FILES_DIR / pdf_file_name

    # 1. Отправляем PDF файл
    if pdf_path.exists():
        with open(pdf_path, 'rb') as doc:
            await context.bot.send_document(
                chat_id=chat_id,
                document=doc,
                caption="📄 Полный файл нормативов ВО (PDF)"
            )
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Файл {pdf_file_name} не найден в папке data/files.")

    # 2. Отправляем описание
    description_text = (
        "В этом файле находятся нормативы для ВО по:\n"
        "*- Легкой атлетике*🏃‍♂️\n"
        "*- Волейболу*🏐\n"
        "*- Баскетболу*🏀\n"
        "*- Бадминтону*🏸\n"
        "*- Адаптивной физической культуре*🧗‍♂️\n"
        "-------------------------------\n"
        "Так же в этом файле присутствует информация для студентов относящиеся по состоянию здоровья к подготовительному и специальному медицинскому отделению.📋🏥\n"
        "Для них доступны те нормативы, которые доступны по состоянию здоровья (Таблица 2, стр. 5)\n"
        "-------------------------------\n"
        "Студенты освобожденные от занятий по состоянию здоровья или временно освобожденные от практических занятий по состоянию здоровья, будут оцениваться по результатам:\n"
        "*- Устного опроса*🗣\n"
        "*- Реферата*📃\n"
        "*- Контрольной работы*📜\n"
        "Вся информация так же содержится в этом файле (стр. 5-8)."
    )
    
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=description_text,
    )

    # 3. Финальное сообщение с ссылкой
    footer_text = (
        "-------------------------------\n"
        "Вузовские нормативы ВО\n"
        f"Ссылка на ГТО для подробного ознакомления: {config.GTO_MAIN_SITE}\n"
        "-------------------------------\n"
        "⚠️ Информация может обновляться, уточняйте актуальные данные на официальном сайте."
    )
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=footer_text,
        reply_markup=get_vuz_menu_keyboard()
    )

# Меню выбора ступени ГТО
async def gto_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        config.GTO_STAGE_SELECT_TEXT,
        reply_markup=get_gto_stage_keyboard()
    )

# Показ выбранной ступени ГТО (1 фото)
async def show_gto_stage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    stage = int(query.data.split("_")[-1])
    
    # Формируем имя файла: gto_stage_6/7/8.jpg
    file_name = f"gto_stage_{stage}.jpg"
    image_path = IMAGES_DIR / file_name
    
    stage_link = config.GTO_STAGE_LINKS.get(stage, config.GTO_MAIN_SITE)
    
    stage_info = f"Ступень {stage}"
    if stage == 6:
        stage_info += " (13-15 лет)"
    elif stage == 7:
        stage_info += " (16-17 лет)"
    elif stage == 8:
        stage_info += " (18-29 лет)"

    # Удаляем сообщение с выбором ступени
    try:
        await query.message.delete()
    except Exception:
        pass

    chat_id = query.message.chat_id

    # Отправляем фото
    if image_path.exists():
        with open(image_path, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=f"🎯 {stage_info}"
            )
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Изображение {file_name} не найдено.")

    # Отправляем финальный текст с кнопками
    footer_text = (
        "-------------------------------\n"
        f"{stage_info}\n"
        f"Ссылка на ГТО для подробного ознакомления: {stage_link}\n"
        "-------------------------------\n"
        "⚠️ Информация может обновляться, уточняйте актуальные данные на официальном сайте."
    )
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=footer_text,
        reply_markup=get_gto_detail_keyboard(stage)
    )

# Показ рекомендаций для выбранной ступени ГТО
async def show_gto_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    stage = int(query.data.split("_")[-1])
    recommendations = config.GTO_RECOMMENDATIONS.get(stage, "Рекомендации временно недоступны.")
    stage_link = config.GTO_STAGE_LINKS.get(stage, config.GTO_MAIN_SITE)
    
    stage_info = f"Ступень {stage}"
    if stage == 6:
        stage_info += " (13-15 лет)"
    elif stage == 7:
        stage_info += " (16-17 лет)"
    elif stage == 8:
        stage_info += " (18-29 лет)"
    
    # Удаляем предыдущее сообщение (если оно было) или просто шлем новое
    # В данном случае, так как мы переходим из меню ступени, лучше удалить старое, чтобы не засорять чат
    try:
        await query.message.delete()
    except Exception:
        pass

    full_text = (
        f"📋 <b>Рекомендации для {stage_info}</b>\n\n"
        f"{recommendations}\n\n"
        "-------------------------------\n"
        f"Ссылка на ГТО для подробного ознакомления: {stage_link}\n"
        "-------------------------------\n"
        "⚠️ Информация может обновляться."
    )
    
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=full_text,
        reply_markup=get_gto_detail_keyboard(stage),
        parse_mode='HTML'
    )

# Показ раздела информации (данные из config подразумевается)
async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = config.INFO_DATA
    
    # Формируем текст сообщения
    text_parts = [
        f"*{data['title']}*",
        "",
        data['description'],
        ""
    ]
    
    # Добавляем список ссылок текстом
    # Но основные ссылки будут кнопками ниже
    links_text = "\n".join([f"• {item['text']}" for item in data['links']])
    text_parts.append(links_text)
    text_parts.append("")
    text_parts.append(data['contacts'])
    
    full_text = "\n".join(text_parts)
    
    # Формируем клавиатуру с кнопками-ссылками
    keyboard = []
    for item in data['links']:
        keyboard.append([InlineKeyboardButton(item['text'], url=item['url'])])
    
    # Кнопка назад
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])
    
    await query.edit_message_text(
        text=full_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# Универсальный обработчик нажатий на кнопки
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    handlers = {
        "main_menu": main_menu,
        "vuz_menu": vuz_menu,
        "spo_standards": show_spo_standards,
        "vo_standards": show_vo_standards,
        "gto_menu": gto_menu,
        "info": show_info,
    }
    
    if data.startswith("gto_stage_"):
        await show_gto_stage(update, context)
    elif data.startswith("gto_rec_"):
        await show_gto_recommendations(update, context)
    elif data in handlers:
        await handlers[data](update, context)
    else:
        logger.warning(f"Неизвестный callback_data: {data}") # На случай, если будут изменения в разделах
        await query.answer("Этот раздел в разработке", show_alert=True)

# Создание и настройка приложения бота
def create_application():
    token = os.getenv("TOKEN")
    
    if not token or token == "your_bot_token_here":
        raise ValueError(
            "Токен бота не найден! Создайте файл .env и укажите TOKEN=ваш_токен\n"
        )
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    return application

# Запуск бота
def main():
    logger.info("Запуск бота...")
    
    try:
        app = create_application()
        logger.info("Бот успешно запущен. Ожидание команд.")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()