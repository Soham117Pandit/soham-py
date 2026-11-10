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
    """Raise ``ValueError`` if *number* is not a valid practical number."""
    if not isinstance(number, int) or isinstance(number, bool):
        raise ValueError(
            f"Practical number must be an integer, got {type(number).__name__}."
        )
    if number < 1:
        raise ValueError(
            f"Practical number must be a positive integer, got {number}."
        )


def get_practical(subject: str, number: int) -> str:
    """Return the contents of a practical file as a plain-text string.

    Parameters
    ----------
    subject : str
        Subject name or alias (case-insensitive).
    number : int
        Practical number (any positive integer).

    Returns
    -------
    str
        The full contents of the practical file if it exists (or ``""`` if empty).
        If the practical file does not exist, returns:
        ``"There is no file present for {SUBJECT} practical {number}."``

    Raises
    ------
    ValueError
        If the subject name is invalid, or if practical number is not a positive integer.
    """
    key = resolve_subject(subject)
    _validate_practical_number(number)

    filename = f"practical{number}.txt"
    resource_package = f"soham_py.practicals.{key}"

    try:
        package_files = files(resource_package)
    except (ModuleNotFoundError, FileNotFoundError):
        return f"There is no file present for {key.upper()} practical {number}."

    resource = package_files.joinpath(filename)
    if not resource.is_file():
        return f"There is no file present for {key.upper()} practical {number}."

    try:
        return resource.read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError):
        return f"There is no file present for {key.upper()} practical {number}."


def list_practicals(subject: str) -> List[int]:
    """Return a sorted list of available practical numbers for *subject*.

    Parameters
    ----------
    subject : str
        Subject name or alias (case-insensitive).

    Returns
    -------
    list of int
        Available practical numbers for which files actually exist.

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
                if num >= 1 and item.is_file():
                    numbers.append(num)

    return sorted(numbers)

