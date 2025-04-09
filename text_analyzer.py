# @Bybyscan 09.04.2025
import re
import asyncio
import logging
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

class TextAnalyzer:
    """Генерация тезисов и задач с помощью LLM"""

    def __init__(self, config):
        self.config = config

    async def analyze(self, text: str) -> Dict[str, str]:
        """Анализ текста и генерация результатов"""
        try:
            clean_text = self._clean_text(text)
            if not clean_text:
                return self._error_response(text)

            chunks = self._split_text(clean_text)
            results = {'theses': [], 'tasks': []}

            async with httpx.AsyncClient(timeout=self.config.LLM_TIMEOUT) as client:
                tasks = []
                for chunk in chunks:
                    tasks.append(self._process_chunk(client, chunk, 'theses'))
                    tasks.append(self._process_chunk(client, chunk, 'tasks'))

                chunk_results = await asyncio.gather(*tasks, return_exceptions=True)

                for i, result in enumerate(chunk_results):
                    if not isinstance(result, Exception) and result:
                        key = 'theses' if i % 2 == 0 else 'tasks'
                        results[key].append(result)

            return {
                'original': clean_text,
                'theses': "\n\n".join(results['theses']) if results['theses'] else "Не удалось сгенерировать тезисы",
                'tasks': "\n\n".join(results['tasks']) if results['tasks'] else "Не удалось сгенерировать задачи"
            }
        except Exception as e:
            logger.error(f"Ошибка анализа текста: {str(e)}")
            return self._error_response(text)

    @staticmethod
    def _clean_text(text: str) -> str:
        """Очистка текста"""
        if not text or not isinstance(text, str):
            return ""

        text = re.sub(r'[^\w\sа-яА-ЯёЁ.,!?\-:;\n]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def _split_text(text: str, max_length: int = 1500) -> List[str]:
        """Разбивка текста на части"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence + " "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    async def _process_chunk(self, client: httpx.AsyncClient, chunk: str, prompt_type: str) -> Optional[str]:
        """Обработка части текста"""
        for attempt in range(self.config.MAX_RETRIES):
            try:
                prompt = self.config.prompts[prompt_type].format(text=chunk)

                response = await client.post(
                    f"https://api-inference.huggingface.co/models/{self.config.LLM_MODEL}",
                    headers={"Authorization": f"Bearer {self.config.HF_API_KEY}"},
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 250,
                            "temperature": 0.7,
                            "do_sample": True
                        }
                    }
                )

                response.raise_for_status()
                result = response.json()[0]['generated_text']
                return result.split(prompt)[-1].strip()

            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error (attempt {attempt + 1}): {e.response.status_code}")
                if attempt == self.config.MAX_RETRIES - 1 or e.response.status_code == 400:
                    raise
                await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"Error (attempt {attempt + 1}): {str(e)}")
                if attempt == self.config.MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(1)

    @staticmethod
    def _error_response(text: str) -> Dict[str, str]:
        """Формирование ответа при ошибке"""
        truncated = text[:1000] + "..." if len(text) > 1000 else text
        return {
            'original': truncated,
            'theses': "Ошибка генерации тезисов",
            'tasks': "Ошибка генерации задач"
        }
