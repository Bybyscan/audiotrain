import os
from pathlib import Path
from typing import Dict


class Config:
    """Конфигурация приложения"""

    def __init__(self):
        # API Keys
        self.TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
        self.HF_API_KEY = os.getenv("HF_API_KEY", "")

        # Model Settings
        self.WHISPER_MODEL = os.getenv("WHISPER_MODEL", "openai/whisper-medium")
        self.LLM_MODEL = os.getenv("LLM_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")

        # Audio Processing
        self.SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))
        self.CHUNK_LENGTH = int(os.getenv("CHUNK_LENGTH", "30"))
        self.MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "4000"))
        self.LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "30.0"))
        self.MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

    @property
    def paths(self) -> Dict[str, Path]:
        base = Path(os.getenv("AUDIOTRAIN_BASE_DIR", str(Path.home() / "audio_transcriber")))
        return {
            'input': base / 'input',
            'output': base / 'output',
            'logs': base / 'logs',
            'temp': base / 'temp'
        }

    @property
    def prompts(self) -> Dict[str, str]:
        return {
            'theses': """Создай основные тезисы на основе следующего текста.
                        Ответ выдай в виде маркированного списка только на русском языке.
                        Для имен личных и топонимов иностранного происхождения применяй транслитерацию.
                        Текст: {text}""",
            'tasks': """Создай список поручений на основе следующего текста.
                      Ответ выдай в виде нумерованного списка только на русском языке.
                      Для имен личных и топонимов иностранного происхождения применяй транслитерацию.
                      Текст: {text}"""
        }
