"""Core practical retrieval for SohamPy.

This module reads bundled ``.txt`` practical files using
``importlib.resources`` so the package works after installation without
depending on the current working directory or absolute paths.

**No stored code is ever executed.**
"""

from __future__ import annotations

import sys
from typing import List

from .subjects import (
    PRACTICALS_PER_SUBJECT,
    SUBJECT_INFO,
    resolve_subject,
)

# ── importlib.resources compatibility ───────────────────────────────
# Python 3.9+ has importlib.resources.files; earlier versions need the
# backport, but we only support >=3.9 so importlib.resources is fine.
if sys.version_info >= (3, 9):
    from importlib.resources import files
else:  # pragma: no cover – we require >=3.9
    from importlib.resources import files  # type: ignore[attr-defined]


def _validate_practical_number(number: int) -> None:
    """Raise ``ValueError`` if *number* is outside 1..PRACTICALS_PER_SUBJECT."""
    if not isinstance(number, int) or isinstance(number, bool):
        raise ValueError(
            f"Practical number must be an integer, got {type(number).__name__}."
        )
    if number < 1 or number > PRACTICALS_PER_SUBJECT:
        raise ValueError(
            f"Practical number must be between 1 and {PRACTICALS_PER_SUBJECT}, "
            f"got {number}."
        )


def get_practical(subject: str, number: int) -> str:
    """Return the contents of a practical file as a plain-text string.

    Parameters
    ----------
    subject : str
        Subject name or alias (case-insensitive).
    number : int
        Practical number (1–10).

    Returns
    -------
    str
        The full contents of the practical file.  Returns ``""`` when the
        file is empty.

    Raises
    ------
    ValueError
        If the subject or practical number is invalid.
    FileNotFoundError
        If the underlying resource package or ``.txt`` file is missing.
    """
    key = resolve_subject(subject)
    _validate_practical_number(number)

    filename = f"practical{number}.txt"
    resource_package = f"soham_py.practicals.{key}"

    try:
        package_files = files(resource_package)
    except (ModuleNotFoundError, FileNotFoundError) as exc:
        raise FileNotFoundError(
            f"Practical package not found: {resource_package}"
        ) from exc

    resource = package_files.joinpath(filename)

    try:
        return resource.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Practical file not found: {key}/{filename}"
        ) from exc


def list_practicals(subject: str) -> List[int]:
    """Return a sorted list of available practical numbers for *subject*.

    Parameters
    ----------
    subject : str
        Subject name or alias (case-insensitive).

    Returns
    -------
    list of int
        Practical numbers, e.g. ``[1, 2, 3, ..., 10]``.

    Raises
    ------
    ValueError
        If the subject is invalid.
    FileNotFoundError
        If the underlying resource package or directory is missing.
    """
    key = resolve_subject(subject)
    resource_package = f"soham_py.practicals.{key}"

    try:
        package_dir = files(resource_package)
    except (ModuleNotFoundError, FileNotFoundError) as exc:
        raise FileNotFoundError(
            f"Practical package not found: {resource_package}"
        ) from exc

    try:
        items = list(package_dir.iterdir())
    except (FileNotFoundError, ModuleNotFoundError) as exc:
        raise FileNotFoundError(
            f"Practical directory not found: {resource_package}"
        ) from exc

    numbers: List[int] = []
    for item in items:
        name = item.name
        if name.startswith("practical") and name.endswith(".txt"):
            stem = name[len("practical"):-len(".txt")]
            if stem.isdigit():
                num = int(stem)
                if 1 <= num <= PRACTICALS_PER_SUBJECT:
                    numbers.append(num)

    return sorted(numbers)

