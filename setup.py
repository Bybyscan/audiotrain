# @Bybyscan 09.04.2025
from setuptools import setup, find_packages

setup(
    name="audiotrain",
    version="1.0.0",
    description="Библиотека для транскрибации и анализа аудио",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="@Bybyscan",
    author_email="bybyscan@yandex.ru",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "torchaudio>=2.0.0",
        "transformers>=4.30.0",
        "accelerate>=0.20.0",
        "python-telegram-bot>=20.0",
        "requests>=2.28.0",
        "httpx>=0.23.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="audio transcription whisper speech-to-text nlp",
)
