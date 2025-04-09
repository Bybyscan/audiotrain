"""AudioTrain - библиотека для транскрибации и анализа аудио"""
from .config import Config
from .audio_processor import AudioProcessor
from .transcriber import Transcriber
from .text_analyzer import TextAnalyzer
from .telegram_bot import run_bot

__version__ = "1.0.0"
__all__ = ['Config', 'AudioProcessor', 'Transcriber', 'TextAnalyzer', 'run_bot']
