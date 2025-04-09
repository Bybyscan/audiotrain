# @Bybyscan 09.04.2025
import asyncio
import logging
from pathlib import Path
from typing import Optional

import torch
from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoProcessor
from accelerate import Accelerator

logger = logging.getLogger(__name__)

class Transcriber:
    """Транскрибация аудио с помощью Whisper"""

    def __init__(self, config):
        self.config = config
        self._initialize()

    def _initialize(self):
        """Инициализация модели Whisper"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if self.device == "cuda" else torch.float32

        logger.info(f"Инициализация Whisper ({self.device}, {self.torch_dtype})")

        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.config.WHISPER_MODEL,
            torch_dtype=self.torch_dtype,
            low_cpu_mem_usage=True
        ).to(self.device)

        self.processor = AutoProcessor.from_pretrained(self.config.WHISPER_MODEL)

    async def transcribe(self, audio_path: Path) -> Optional[str]:
        """Транскрибация аудио на русском"""
        for attempt in range(self.config.MAX_RETRIES):
            try:
                audio_data = await AudioProcessor.process_audio(audio_path, self.config)
                if not audio_data:
                    return None

                waveform, _ = audio_data

                pipe = pipeline(
                    "automatic-speech-recognition",
                    model=self.model,
                    tokenizer=self.processor.tokenizer,
                    feature_extractor=self.processor.feature_extractor,
                    device=self.device,
                    torch_dtype=self.torch_dtype
                )

                result = pipe(
                    waveform.numpy()[0],
                    generate_kwargs={
                        "language": "russian",
                        "task": "transcribe",
                        "temperature": 0.0
                    }
                )

                text = result.get('text', '')
                return text if text else None

            except Exception as e:
                logger.warning(f"Попытка {attempt + 1} не удалась: {str(e)}")
                if attempt == self.config.MAX_RETRIES - 1:
                    logger.error("Превышено количество попыток транскрибации")
                    return None
                await asyncio.sleep(1)
