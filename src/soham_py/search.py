"""Search through all bundled practicals for SohamPy.

Provides case-insensitive full-text search across every subject and
practical file.  Empty files are silently skipped.
"""

from __future__ import annotations

from typing import Dict, List

from .core import get_practical, list_practicals
from .subjects import SUBJECT_INFO


# ── Public search result type ───────────────────────────────────────
# Each result is a dict with keys: subject, practical, snippet

SearchResult = Dict[str, object]


def search(query: str) -> List[SearchResult]:
    """Search all practicals for *query* (case-insensitive).

    Parameters
    ----------
    query : str
        The search term.

    Returns
    -------
    list of dict
        Each dict contains:
        - ``"subject"`` (str) – canonical subject key
        - ``"practical"`` (int) – practical number
        - ``"snippet"`` (str) – the first line containing the match

    Raises
    ------
    ValueError
        If *query* is empty or contains only whitespace.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Search query must be a non-empty string.")

    term = query.strip().lower()
    results: List[SearchResult] = []

    for subject_key in sorted(SUBJECT_INFO.keys()):
        for num in list_practicals(subject_key):
            try:
                content = get_practical(subject_key, num)
            except FileNotFoundError:
                continue

            # Skip empty files or missing notices
            if not content.strip() or "no file present for" in content.lower():
                continue

            # Case-insensitive search
            if term in content.lower():
                # Extract the first matching line as a snippet
                snippet = ""
                for line in content.splitlines():
                    if term in line.lower():
                        snippet = line.strip()
                        break

                results.append(
                    {
                        "subject": subject_key,
                        "practical": num,
                        "snippet": snippet,
                    }
                )

    return results

