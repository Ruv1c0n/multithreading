# The `gui/__init__.py` file is a special Python file that is used to define a package. In this
# specific file, it is defining the contents of the `gui` package. It provides a brief description of
# the package and lists the modules it contains. In this case, it imports `LabTab` from the `lab_tab`
# module and specifies that `LabTab` is part of the package's public interface by including it in the
# `__all__` list. This allows users to access `LabTab` directly when importing the `gui` package.
"""
Пакет gui — отвечает за интерфейс приложения.
Содержит:
- lab_tab.py — вкладка лабораторной работы
"""

from .lab_tab import LabTab

__all__ = ["LabTab"]
