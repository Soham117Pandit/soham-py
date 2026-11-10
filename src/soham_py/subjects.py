"""Subject definitions and alias resolution for SohamPy.

This module defines the three primary subjects (DS, WT, DBMS) and
provides case-insensitive alias resolution.
"""

from typing import Dict, List, Tuple

# ── Subject metadata ────────────────────────────────────────────────
SUBJECT_INFO: Dict[str, str] = {
    "ds": "Data Science",
    "wt": "Web Technology",
    "dbms": "Database Management Systems",
}

# ── Alias mapping (all lowercase) ──────────────────────────────────
SUBJECT_ALIASES: Dict[str, str] = {
    "ds": "ds",
    "data_science": "ds",
    "wt": "wt",
    "web": "wt",
    "web_technology": "wt",
    "dbms": "dbms",
    "database": "dbms",
}

# ── Practical count per subject ─────────────────────────────────────
PRACTICALS_PER_SUBJECT: int = 10


def resolve_subject(name: str) -> str:
    """Resolve a subject name or alias to its canonical key.

    Parameters
    ----------
    name : str
        Subject name or alias (case-insensitive).

    Returns
    -------
    str
        Canonical subject key (``"ds"``, ``"wt"``, or ``"dbms"``).

    Raises
    ------
    ValueError
        If *name* is not a string, is empty, or is not a recognised subject/alias.
    """
    if not isinstance(name, str):
        raise ValueError(
            f"Subject name must be a string, got {type(name).__name__}."
        )
    key = name.strip().lower().replace(" ", "_")
    if not key:
        raise ValueError("Subject name cannot be empty or only whitespace.")
    if key not in SUBJECT_ALIASES:
        valid = ", ".join(sorted(SUBJECT_ALIASES.keys()))
        raise ValueError(
            f"Invalid subject: {name!r}. "
            f"Valid subjects and aliases are: {valid}"
        )
    return SUBJECT_ALIASES[key]


def get_subjects() -> List[Tuple[str, str]]:
    """Return a list of ``(key, description)`` tuples for every subject.

    Returns
    -------
    list of tuple
        Sorted list of ``(subject_key, description)`` pairs.
    """
    return sorted(SUBJECT_INFO.items())

