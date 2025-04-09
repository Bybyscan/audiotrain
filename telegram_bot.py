# @Bybyscan 09.04.2025
import asyncio
import logging
from datetime import datetime
from pathlib import Path

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

logger = logging.getLogger(__name__)


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE, config, transcriber, analyzer):
    """Обработка входящих аудиосообщений"""
    user = update.message.from_user
    logger.info(f"Новое сообщение от {user.username} ({user.id})")

    try:
        if update.message.audio:
            file = await update.message.audio.get_file()
            file_name = f"audio_{user.id}_{int(datetime.now().timestamp())}.ogg"
        elif update.message.voice:
            file = await update.message.voice.get_file()
            file_name = f"voice_{user.id}_{int(datetime.now().timestamp())}.ogg"
        else:
            await update.message.reply_text("Пожалуйста, отправьте аудио или голосовое сообщение")
            return

        input_path = config.paths['input'] / file_name
        input_path.parent.mkdir(exist_ok=True, parents=True)

        await file.download_to_drive(input_path)
        logger.info(f"Файл сохранён: {input_path}")

        await update.message.reply_text("🔊 Начинаю обработку аудио...")
        text = await transcriber.transcribe(input_path)

        if not text:
            await update.message.reply_text("Не удалось распознать речь в аудио")
            return

        await update.message.reply_text("🧠 Анализирую текст...")
        results = await analyzer.analyze(text)

        await _send_results(update, results, config)

    except Exception as e:
        logger.error(f"Ошибка обработки: {str(e)}")
        await update.message.reply_text(f"⚠️ Произошла ошибка: {str(e)}")
    finally:
        if 'input_path' in locals() and input_path.exists():
            input_path.unlink()


async def _send_results(update: Update, results: Dict[str, str], config):
    """Отправка результатов пользователю"""
    try:
        output_dir = config.paths['output']
        output_dir.mkdir(exist_ok=True, parents=True)

        await update.message.reply_text("✅ Результаты транскрибации:")
        for i in range(0, len(results['original']), config.MAX_TEXT_LENGTH):
            await update.message.reply_text(results['original'][i:i + config.MAX_TEXT_LENGTH])

        await update.message.reply_text("📌 Основные тезисы:")
        await update.message.reply_text(results['theses'])

        await update.message.reply_text("📋 Список задач:")
        await update.message.reply_text(results['tasks'])

    except Exception as e:
        logger.error(f"Ошибка отправки результатов: {str(e)}")
        await update.message.reply_text("⚠️ Ошибка при отправке результатов")


async def run_bot(config):
    """Запуск бота в асинхронном режиме"""
    try:
        setup_logging(config)

        for path in config.paths.values():
            path.mkdir(parents=True, exist_ok=True)

        await check_dependencies()
        await test_api_connection(config)

        app = Application.builder().token(config.TELEGRAM_TOKEN).build()

        transcriber = Transcriber(config)
        analyzer = TextAnalyzer(config)

        app.add_handler(MessageHandler(
            filters.AUDIO | filters.VOICE,
            lambda update, context: handle_audio(update, context, config, transcriber, analyzer)
        ))

        logger.info("Бот запущен и готов к работе")
        await app.initialize()
        await app.start()
        await app.updater.start_polling()

        # Бесконечный цикл для работы бота
        while True:
            await asyncio.sleep(3600)

    except asyncio.CancelledError:
        logger.info("Получен сигнал завершения работы")
    except Exception as e:
        logger.critical(f"Критическая ошибка: {str(e)}")
        raise
    finally:
        if 'app' in locals():
            await app.updater.stop()
            await app.stop()
            await app.shutdown()
