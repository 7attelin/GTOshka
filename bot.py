import logging
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
import os
import glob

import config

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- КОНФИГУРАЦИЯ ПУТЕЙ К ФОТО ---
# Предполагаем, что фото лежат в папке 'photo' рядом с скриптом.
# Если у вас в config.py задан другой путь, замените BASE_PHOTO_PATH на config.PHOTO_DIR
BASE_PHOTO_PATH = Path("photo")

def get_photo_paths(prefix: str, count: int = 3):
    """
    Ищет файлы в папке photo, начинающиеся с prefix.
    Ожидает имена вида: spo_1.jpg, spo_2.jpg, spo_3.jpg (или .png)
    """
    paths = []
    # Пробуем найти файлы с разными расширениями
    for i in range(1, count + 1):
        found = False
        for ext in ['jpg', 'jpeg', 'png']:
            file_path = BASE_PHOTO_PATH / f"{prefix}_{i}.{ext}"
            if file_path.exists():
                paths.append(file_path)
                found = True
                break
        
        # Если точного имени нет, пробуем найти любые файлы с префиксом (fallback)
        if not found:
            # Ищем все файлы, начинающиеся с prefix_
            matches = list(BASE_PHOTO_PATH.glob(f"{prefix}_{i}.*"))
            if matches:
                paths.append(matches[0])
    
    return paths

# --- КЛАВИАТУРЫ ---

def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📚 Вузовские Нормативы", callback_data="vuz_menu")],
        [InlineKeyboardButton("🎯 Нормативы ГТО", callback_data="gto_menu")],
        [InlineKeyboardButton("ℹ️ Инфо", callback_data="info")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_vuz_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Нормативы СПО", callback_data="spo_standards")],
        [InlineKeyboardButton("Нормативы ВО", callback_data="vo_standards")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_gto_stage_keyboard():
    keyboard = [
        [InlineKeyboardButton("Ступень 6 (13-15 лет)", callback_data="gto_stage_6")],
        [InlineKeyboardButton("Ступень 7 (16-17 лет)", callback_data="gto_stage_7")],
        [InlineKeyboardButton("Ступень 8 (18-29 лет)", callback_data="gto_stage_8")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_gto_detail_keyboard(stage: int):
    keyboard = [
        [InlineKeyboardButton("📋 Рекомендации", callback_data=f"gto_rec_{stage}")],
        [InlineKeyboardButton("🔙 Назад к выбору ступени", callback_data="gto_menu")],
        [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard(callback: str):
    """Клавиатура только с кнопкой назад"""
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data=callback)],
    ]
    return InlineKeyboardMarkup(keyboard)

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

async def safe_delete_message(message):
    """Безопасное удаление сообщения без ошибок, если оно уже удалено."""
    try:
        await message.delete()
    except Exception as e:
        logger.debug(f"Не удалось удалить сообщение: {e}")

def get_footer_text(title: str, link: str):
    """Формирует финальный текст сообщения."""
    return (
        "-------------------------------\n"
        f"{title}\n"
        f"Ссылка на ГТО для подробного ознакомления: {link}\n"
        "-------------------------------\n"
        "⚠️ Информация может обновляться, уточняйте актуальные данные на официальном сайте."
    )

# --- ОБРАБОТЧИКИ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            config.MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard()
        )

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        config.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard()
    )

async def vuz_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        config.VUZ_MENU_TEXT,
        reply_markup=get_vuz_menu_keyboard()
    )

async def show_spo_standards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ 3 фото СПО + финальный текст"""
    query = update.callback_query
    await query.answer()
    await safe_delete_message(query.message)

    chat_id = query.message.chat_id
    title = "Вузовские нормативы СПО"
    link = config.GTO_MAIN_SITE
    
    # Ищем фото: spo_1, spo_2, spo_3
    photos = get_photo_paths("spo", 3)
    
    if not photos:
        await context.bot.send_message(chat_id, f"❌ Фотографии для {title} не найдены в папке photo/", reply_markup=get_back_keyboard("vuz_menu"))
        return

    # Отправляем 3 фото
    captions = [
        f"📊 {title} - Часть 1",
        f"📊 {title} - Часть 2",
        f"📊 {title} - Часть 3"
    ]

    for i, photo_path in enumerate(photos):
        caption = captions[i] if i < len(captions) else f"📊 {title}"
        with open(photo_path, 'rb') as photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=caption)

    # Отправляем финальный текст отдельно
    await context.bot.send_message(
        chat_id=chat_id,
        text=get_footer_text(title, link),
        reply_markup=get_vuz_menu_keyboard()
    )

async def show_vo_standards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ 3 фото ВО + финальный текст"""
    query = update.callback_query
    await query.answer()
    await safe_delete_message(query.message)

    chat_id = query.message.chat_id
    title = "Вузовские нормативы ВО"
    link = config.GTO_MAIN_SITE

    # Ищем фото: vo_1, vo_2, vo_3 (или vo_standards_1 и т.д. зависит от naming)
    # Попробуем сначала vo, потом vo_standards
    photos = get_photo_paths("vo", 3)
    if not photos:
        photos = get_photo_paths("vo_standards", 3)

    if not photos:
        await context.bot.send_message(chat_id, f"❌ Фотографии для {title} не найдены в папке photo/\nОжидаются имена: vo_1.jpg, vo_2.jpg...", reply_markup=get_back_keyboard("vuz_menu"))
        return

    captions = [
        f"🎓 {title} - Блок 1",
        f"🎓 {title} - Блок 2",
        f"🎓 {title} - Блок 3"
    ]

    for i, photo_path in enumerate(photos):
        caption = captions[i] if i < len(captions) else f"🎓 {title}"
        with open(photo_path, 'rb') as photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=caption)

    # Финальный текст
    await context.bot.send_message(
        chat_id=chat_id,
        text=get_footer_text(title, link),
        reply_markup=get_vuz_menu_keyboard()
    )

async def gto_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        config.GTO_STAGE_SELECT_TEXT,
        reply_markup=get_gto_stage_keyboard()
    )

async def show_gto_stage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ 3 фото ступени ГТО + финальный текст"""
    query = update.callback_query
    await query.answer()
    
    stage = int(query.data.split("_")[-1])
    stage_info = f"Ступень {stage}"
    if stage == 6: stage_info += " (13-15 лет)"
    elif stage == 7: stage_info += " (16-17 лет)"
    elif stage == 8: stage_info += " (18-29 лет)"
    
    await safe_delete_message(query.message)
    chat_id = query.message.chat_id
    link = config.GTO_STAGE_LINKS.get(stage, config.GTO_MAIN_SITE)

    # Ищем фото: gto_6_1, gto_6_2... или stage_6_1...
    # Попробуем несколько форматов имен
    prefixes_to_try = [f"gto_{stage}", f"stage_{stage}", f"gto_stage_{stage}"]
    photos = []
    for prefix in prefixes_to_try:
        photos = get_photo_paths(prefix, 3)
        if photos:
            break

    if not photos:
        await context.bot.send_message(
            chat_id, 
            f"❌ Фотографии для {stage_info} не найдены.\nПроверьте имена файлов (например: gto_6_1.jpg)", 
            reply_markup=get_gto_detail_keyboard(stage)
        )
        return

    captions = [
        f"🎯 {stage_info} - Норматив 1",
        f"🎯 {stage_info} - Норматив 2",
        f"🎯 {stage_info} - Норматив 3"
    ]

    for i, photo_path in enumerate(photos):
        caption = captions[i] if i < len(captions) else f"🎯 {stage_info}"
        with open(photo_path, 'rb') as photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=caption)

    # Финальный текст
    await context.bot.send_message(
        chat_id=chat_id,
        text=get_footer_text(stage_info, link),
        reply_markup=get_gto_detail_keyboard(stage)
    )

async def show_gto_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    stage = int(query.data.split("_")[-1])
    recommendations = config.GTO_RECOMMENDATIONS.get(stage, "Рекомендации временно недоступны.")
    stage_link = config.GTO_STAGE_LINKS.get(stage, config.GTO_MAIN_SITE)
    
    stage_info = f"Ступень {stage}"
    if stage == 6: stage_info += " (13-15 лет)"
    elif stage == 7: stage_info += " (16-17 лет)"
    elif stage == 8: stage_info += " (18-29 лет)"
    
    await safe_delete_message(query.message)
    
    full_text = (
        f"📋 <b>Рекомендации: {stage_info}</b>\n\n"
        f"{recommendations}\n\n"
        "-------------------------------\n"
        f"🌐 <a href='{stage_link}'>Ссылка на ГТО для подробного ознакомления</a>"
    )
    
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=full_text,
        reply_markup=get_gto_detail_keyboard(stage),
        parse_mode='HTML'
    )

async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        config.INFO_TEXT,
        reply_markup=get_main_menu_keyboard()
    )

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
        logger.warning(f"Неизвестный callback_data: {data}")
        await query.answer("Этот раздел в разработке", show_alert=True)

def create_application():
    token = os.getenv("TOKEN")
    
    if not token or token == "your_bot_token_here":
        raise ValueError("Токен бота не найден! Проверьте файл .env")
    
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    return application

def main():
    logger.info("Запуск бота...")
    try:
        app = create_application()
        logger.info("Бот запущен. Ожидание сообщений...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()