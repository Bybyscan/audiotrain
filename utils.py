# @Bybyscan 09.04.2025
import asyncio
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

async def check_dependencies():
    """Проверка системных зависимостей"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"FFmpeg version: {result.stdout.splitlines()[0].split()[2]}")
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        logger.critical("FFmpeg не найден или не работает! Установите с https://ffmpeg.org/")
        raise RuntimeError("FFmpeg не установлен")

async def test_api_connection(config):
    """Тестирование подключения к API Hugging Face"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"https://api-inference.huggingface.co/models/{config.LLM_MODEL}",
                headers={"Authorization": f"Bearer {config.HF_API_KEY}"}
            )
            response.raise_for_status()
            logger.info("Hugging Face API доступен")
    except Exception as e:
        logger.error(f"Ошибка подключения к API: {str(e)}")
        raise

def setup_logging(config):
    """Настройка системы логирования"""
    config.paths['logs'].mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.paths['logs'] / 'transcriber.log'),
            logging.StreamHandler()
        ]
    )
    logging.captureWarnings(True)
