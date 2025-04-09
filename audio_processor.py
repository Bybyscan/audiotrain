# @Bybyscan 09.04.2025
import asyncio
import logging
from pathlib import Path
from typing import Optional, Tuple
from tempfile import NamedTemporaryFile

import torch
import torchaudio

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Обработка и конвертация аудио"""

    @staticmethod
    async def process_audio(input_path: Path, config) -> Optional[Tuple[torch.Tensor, int]]:
        """Полный цикл обработки аудио"""
        try:
            wav_path = await AudioProcessor._convert_to_wav(input_path, config)
            if not wav_path:
                return None
            return await AudioProcessor._load_audio(wav_path, config)
        finally:
            if 'wav_path' in locals() and wav_path.exists():
                wav_path.unlink()

    @staticmethod
    async def _convert_to_wav(input_path: Path, config) -> Optional[Path]:
        """Конвертация в WAV формат"""
        try:
            with NamedTemporaryFile(suffix='.wav', dir=config.paths['temp'], delete=False) as tmp_file:
                output_path = Path(tmp_file.name)

                cmd = [
                    'ffmpeg', '-y', '-i', str(input_path),
                    '-ar', str(config.SAMPLE_RATE),
                    '-ac', '1', '-acodec', 'pcm_s16le',
                    '-hide_banner', '-loglevel', 'error',
                    str(output_path)
                ]

                proc = await asyncio.create_subprocess_exec(*cmd)
                await proc.communicate()

                if proc.returncode != 0:
                    logger.error(f"Ошибка конвертации файла {input_path}")
                    return None

                return output_path
        except Exception as e:
            logger.error(f"Ошибка при конвертации: {str(e)}")
            return None

    @staticmethod
    async def _load_audio(file_path: Path, config) -> Optional[Tuple[torch.Tensor, int]]:
        """Загрузка и ресемплинг аудио"""
        try:
            waveform, sample_rate = torchaudio.load(file_path)

            if sample_rate != config.SAMPLE_RATE:
                waveform = torchaudio.functional.resample(
                    waveform,
                    orig_freq=sample_rate,
                    new_freq=config.SAMPLE_RATE
                )

            return waveform, config.SAMPLE_RATE
        except Exception as e:
            logger.error(f"Ошибка загрузки аудио: {str(e)}")
            return None
