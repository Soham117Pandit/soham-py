"""Save practical contents to a local file.

This module writes the plain-text contents of a practical to a
user-specified file path.  **No stored code is ever executed.**
"""

from __future__ import annotations

import pathlib

from .core import get_practical


def save(subject: str, number: int, output_path: str) -> pathlib.Path:
    """Save a practical's contents to a local file.

    Parameters
    ----------
    subject : str
        Subject name or alias (case-insensitive).
    number : int
        Practical number (1–10).
    output_path : str
        Destination file path.

    Returns
    -------
    pathlib.Path
        The resolved path of the created file.

    Raises
    ------
    ValueError
        If the subject or practical number is invalid.
    FileNotFoundError
        If the practical file is missing from the package.
    OSError
        If the output path cannot be written to.
    """
    if not isinstance(output_path, (str, pathlib.Path)):
        raise TypeError(
            f"output_path must be a str or Path, got {type(output_path).__name__}."
        )
    if isinstance(output_path, str) and not output_path.strip():
        raise ValueError("output_path cannot be empty or only whitespace.")

    content = get_practical(subject, number)

    dest = pathlib.Path(output_path).resolve()

    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise OSError(
            f"Could not write to {output_path!r}: {exc}"
        ) from exc

    return dest

