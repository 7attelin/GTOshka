"""
Бот-помощник для сдачи нормативов.
Поддерживает вузовские нормативы (СПО/ВО) и нормативы ГТО.
Реализует редактирование сообщений при навигации по кнопкам.
"""

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


def get_main_menu_keyboard():
    """Клавиатура главного меню."""
    keyboard = [
        [InlineKeyboardButton("📚 Вузовские Нормативы", callback_data="vuz_menu")],
        [InlineKeyboardButton("🎯 Нормативы ГТО", callback_data="gto_menu")],
        [InlineKeyboardButton("ℹ️ Инфо", callback_data="info")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_vuz_menu_keyboard():
    """Клавиатура меню вузовских нормативов."""
    keyboard = [
        [InlineKeyboardButton("Нормативы СПО", callback_data="spo_standards")],
        [InlineKeyboardButton("Нормативы ВО", callback_data="vo_standards")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_gto_stage_keyboard():
    """Клавиатура выбора ступени ГТО."""
    keyboard = [
        [InlineKeyboardButton("Ступень 6 (13-15 лет)", callback_data="gto_stage_6")],
        [InlineKeyboardButton("Ступень 7 (16-17 лет)", callback_data="gto_stage_7")],
        [InlineKeyboardButton("Ступень 8 (18-29 лет)", callback_data="gto_stage_8")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_gto_detail_keyboard(stage: int):
    """Клавиатура для детального просмотра ступени ГТО."""
    keyboard = [
        [InlineKeyboardButton("📋 Рекомендации", callback_data=f"gto_rec_{stage}")],
        [InlineKeyboardButton("🔙 Назад к выбору ступени", callback_data="gto_menu")],
        [InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    await update.message.edit_text(
        config.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard()
    )


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ главного меню."""
    query = update.callback_query
    await query.answer()
    
    # Редактируем существующее сообщение вместо отправки нового
    await query.edit_message_text(
        config.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard()
    )


async def vuz_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню вузовских нормативов."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        config.VUZ_MENU_TEXT,
        reply_markup=get_vuz_menu_keyboard()
    )


async def show_spo_standards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ нормативов СПО."""
    query = update.callback_query
    await query.answer()
    
    image_path = config.IMAGES.get("spo_standards")
    
    if image_path and Path(image_path).exists():
        # Отправляем фото с подписью и кнопками
        photo_with_caption = await query.message.reply_photo(
            photo=open(image_path, 'rb'),
            caption="📊 Нормативы СПО\n\n" + 
                    config.FOOTER_TEMPLATE.format(
                        stage_info="Вузовские нормативы СПО",
                        link=config.GTO_MAIN_SITE
                    ),
            reply_markup=get_vuz_menu_keyboard()
        )
        # Удаляем предыдущее сообщение с меню
        await query.message.delete()
    else:
        await query.edit_message_text(
            "📊 Нормативы СПО\n\nИзображение временно недоступно.\n\n" +
            config.FOOTER_TEMPLATE.format(
                stage_info="Вузовские нормативы СПО",
                link=config.GTO_MAIN_SITE
            ),
            reply_markup=get_vuz_menu_keyboard()
        )


async def show_vo_standards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ нормативов ВО (несколько изображений)."""
    query = update.callback_query
    await query.answer()
    
    # Удаляем сообщение с меню перед отправкой фотографий
    await query.message.delete()
    
    vo_images = [key for key in config.IMAGES.keys() if key.startswith("vo_standards")]
    
    for i, img_key in enumerate(vo_images):
        image_path = config.IMAGES.get(img_key)
        is_last = (i == len(vo_images) - 1)
        
        if image_path and Path(image_path).exists():
            if is_last:
                # К последнему фото прикрепляем клавиатуру
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=open(image_path, 'rb'),
                    caption=f"📊 Нормативы ВО ({i+1}/{len(vo_images)})\n\n" +
                            config.FOOTER_TEMPLATE.format(
                                stage_info="Вузовские нормативы ВО",
                                link=config.GTO_MAIN_SITE
                            ),
                    reply_markup=get_vuz_menu_keyboard()
                )
            else:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=open(image_path, 'rb'),
                    caption=f"📊 Нормативы ВО ({i+1}/{len(vo_images)})"
                )
        else:
            text = f"📊 Нормативы ВО ({i+1}/{len(vo_images)})\n\nИзображение временно недоступно."
            if is_last:
                text += "\n\n" + config.FOOTER_TEMPLATE.format(
                    stage_info="Вузовские нормативы ВО",
                    link=config.GTO_MAIN_SITE
                )
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=text,
                    reply_markup=get_vuz_menu_keyboard()
                )
            else:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=text
                )


async def gto_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню выбора ступени ГТО."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        config.GTO_STAGE_SELECT_TEXT,
        reply_markup=get_gto_stage_keyboard()
    )


async def show_gto_stage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ выбранной ступени ГТО."""
    query = update.callback_query
    await query.answer()
    
    stage = int(query.data.split("_")[-1])
    image_path = config.IMAGES.get(f"gto_stage_{stage}")
    stage_link = config.GTO_STAGE_LINKS.get(stage, config.GTO_MAIN_SITE)
    
    stage_info = f"Ступень {stage}"
    if stage == 6:
        stage_info += " (13-15 лет)"
    elif stage == 7:
        stage_info += " (16-17 лет)"
    elif stage == 8:
        stage_info += " (18-29 лет)"
    
    if image_path and Path(image_path).exists():
        # Удаляем старое сообщение и отправляем новое с фото
        await query.message.delete()
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=open(image_path, 'rb'),
            caption=f"🎯 {stage_info}\n\n" +
                    config.FOOTER_TEMPLATE.format(
                        stage_info=stage_info,
                        link=stage_link
                    ),
            reply_markup=get_gto_detail_keyboard(stage)
        )
    else:
        await query.edit_message_text(
            f"🎯 {stage_info}\n\nИзображение временно недоступно.\n\n" +
            config.FOOTER_TEMPLATE.format(
                stage_info=stage_info,
                link=stage_link
            ),
            reply_markup=get_gto_detail_keyboard(stage)
        )


async def show_gto_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ рекомендаций для выбранной ступени ГТО."""
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
    
    # Удаляем старое сообщение и отправляем новое с рекомендациями
    await query.message.delete()
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=recommendations + "\n" +
             config.FOOTER_TEMPLATE.format(
                 stage_info=stage_info,
                 link=stage_link
             ),
        reply_markup=get_gto_detail_keyboard(stage)
    )


async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ раздела информации."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        config.INFO_TEXT,
        reply_markup=get_main_menu_keyboard()
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Универсальный обработчик нажатий на кнопки."""
    query = update.callback_query
    data = query.data
    
    # Маршрутизация по callback_data
    handlers = {
        "main_menu": main_menu,
        "vuz_menu": vuz_menu,
        "spo_standards": show_spo_standards,
        "vo_standards": show_vo_standards,
        "gto_menu": gto_menu,
        "info": show_info,
    }
    
    # Обработка специфичных callback_data
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
    """Создание и настройка приложения бота."""
    token = os.getenv("TOKEN")
    
    if not token or token == "your_bot_token_here":
        raise ValueError(
            "Токен бота не найден! Создайте файл .env и укажите TOKEN=ваш_токен\n"
            "Получить токен можно у @BotFather в Telegram"
        )
    
    application = Application.builder().token(token).build()
    
    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    return application


def main():
    """Запуск бота."""
    logger.info("Запуск бота...")
    
    try:
        app = create_application()
        
        # Запуск polling (для разработки)
        # Для продакшена на сервере используйте app.run_webhook()
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
