## Установка напрямую из GitHUB

```bash
pip install git+https://github.com/bybyscan/audiotrain.git
```

### Как библиотека

```python
from audiotrain import Config, AudioProcessor, Transcriber, TextAnalyzer

config = Config()
transcriber = Transcriber(config)
analyzer = TextAnalyzer(config)

# Обработка аудио
text = await transcriber.transcribe("audio.mp3")
results = await analyzer.analyze(text)
```

### Запуск Telegram бота

```python
from audiotrain import Config, run_bot

config = Config()
config.TELEGRAM_TOKEN = "your_telegram_token"
config.HF_API_KEY = "your_huggingface_token"

asyncio.run(run_bot(config))
```

## Конфигурация

Все параметры можно настроить через переменные окружения или напрямую в объекте Config:

- `TELEGRAM_TOKEN` - токен Telegram бота
- `HF_API_KEY` - API ключ Hugging Face
- `WHISPER_MODEL` - модель Whisper (по умолчанию "openai/whisper-medium")
- `LLM_MODEL` - модель для анализа текста (по умолчанию "mistralai/Mistral-7B-Instruct-v0.2")
- `AUDIOTRAIN_BASE_DIR` - базовый каталог для хранения файлов

## Требования

- Python 3.8+
- FFmpeg (должен быть установлен в системе)


## Как опубликовать и установить

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Соберите пакет:
```bash
python setup.py sdist bdist_wheel
```

Эта библиотека предоставляет:
- Конфигурируемую систему обработки аудио
- Транскрибацию с помощью Whisper
- Анализ текста с помощью LLM
- Готового Telegram бота
- Поддержку асинхронного выполнения
- Гибкую систему настроек через переменные окружения

Все компоненты разделены на модули и могут использоваться как вместе, так и по отдельности.
