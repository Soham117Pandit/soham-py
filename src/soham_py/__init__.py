"""SohamPy — College practical programs as importable plain text.

A lightweight Python package that bundles college practical programs
for three subjects (DS, WT, DBMS) as plain ``.txt`` files and lets
you retrieve them with a simple import.

**No stored code is ever executed.**

Quick start::

    import soham_py

    print(soham_py.ds(1))
    print(soham_py.wt(1))
    print(soham_py.dbms(1))
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from .core import get_practical, list_practicals
from .search import search
from .saver import save
from .subjects import get_subjects

__version__ = "0.1.0"
__author__ = "Soham Pandit"
__all__ = [
    "ds",
    "wt",
    "dbms",
    "list_practicals",
    "subjects",
    "search",
    "save",
    "get_practical",
    "__version__",
    "__author__",
]


# ── Convenience functions ───────────────────────────────────────────

def ds(number: int) -> str:
    """Return the contents of a Data Science practical.

    Parameters
    ----------
    number : int
        Practical number (1–10).

    Returns
    -------
    str
        Plain-text contents of the practical file.
    """
    return get_practical("ds", number)


def wt(number: int) -> str:
    """Return the contents of a Web Technology practical.

    Parameters
    ----------
    number : int
        Practical number (1–10).

    Returns
    -------
    str
        Plain-text contents of the practical file.
    """
    return get_practical("wt", number)


def dbms(number: int) -> str:
    """Return the contents of a DBMS practical.

    Parameters
    ----------
    number : int
        Practical number (1–10).

    Returns
    -------
    str
        Plain-text contents of the practical file.
    """
    return get_practical("dbms", number)


def subjects() -> List[Tuple[str, str]]:
    """Return the three primary subjects and their descriptions.

    Returns
    -------
    list of tuple
        ``[(key, description), ...]`` sorted alphabetically.
    """
    return get_subjects()

