# core/__init__.py
"""
Пакет core — ядро приложения.
Содержит:
- compiler.py — сборка программ
- experiment.py — запуск и анализ экспериментов
- logger.py — централизованный логгер
"""

from .compiler import Compiler
from .experiment import ExperimentRunner
from .logger import UILogger

__all__ = ["Compiler", "ExperimentRunner", "UILogger"]
