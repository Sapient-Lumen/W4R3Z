from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher


def normalize_text(s: str) -> str:
    """Normalize text for robust matching.

    OCR output can include odd unicode spaces/characters. NFKC is a safe
    default that keeps intent while reducing surprises.
    """

    s2 = unicodedata.normalize("NFKC", s)
    # Collapse whitespace runs.
    s2 = re.sub(r"\s+", " ", s2)
    return s2.strip()


def ratio(a: str, b: str) -> float:
    """Return a similarity score in [0, 1]."""

    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return float(SequenceMatcher(None, a, b).ratio())


def partial_ratio(a: str, b: str) -> float:
    """Return a substring-style similarity score in [0, 1].

    This mirrors the widely-used "partial_ratio" approach popularized by
    fuzzywuzzy/RapidFuzz: align the shorter string against candidate substrings
    of the longer one and return the best similarity.
    """

    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    if len(a) <= len(b):
        short, long = a, b
    else:
        short, long = b, a

    m = SequenceMatcher(None, short, long)
    best = 0.0
    for i, j, n in m.get_matching_blocks():
        # Align the match block so the start positions coincide.
        start = max(0, int(j) - int(i))
        end = start + len(short)
        substring = long[start:end]
        r = ratio(short, substring)
        if r > best:
            best = r
            if best >= 0.995:
                return 1.0
    return best


def fuzzy_score(pattern: str, text: str, *, mode: str = "partial") -> float:
    m = (mode or "partial").strip().lower()
    if m == "ratio":
        return ratio(pattern, text)
    if m == "partial":
        return partial_ratio(pattern, text)
    raise ValueError("fuzzy_mode must be partial|ratio")
