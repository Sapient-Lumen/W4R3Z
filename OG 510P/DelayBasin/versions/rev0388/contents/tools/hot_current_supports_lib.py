import pathlib
import re
from typing import Any

MAX_HOT_CURRENT_SUPPORTS = 18
LANDING_SURFACES = ("README.md", "START_HERE.md", "AGENTS.md", "docs/README.md")
REQUIRED_HOT_ANCHORS = (
    "REVISION-RECEIPT.json",
    "FRONTIER-BACKLOG.json",
    "docs/20-constitution/open-question-registry.md",
)

LATEST_CUE_RE = re.compile(
    r"^Latest revision `(?P<revision>rev\d{4})` / "
    r"`(?P<bundle>DelayBasin-rev\d{4}-[^`]+\.zip)`\. "
    r"`(?P<resolved>OQ-\d{4})` is resolved by `(?P<resolution>RS-\d{4})`; "
    r"`(?P<successor>OQ-\d{4})` is the live successor\. "
    r"Current additions: (?P<additions>.*)$",
    re.M,
)
DOCS_HEAD_CUE_RE = re.compile(
    r"^Current packaged docs head: `(?P<revision>rev\d{4})` / "
    r"`(?P<bundle>DelayBasin-rev\d{4}-[^`]+\.zip)`\. "
    r"Current additions: (?P<additions>.*)$",
    re.M,
)


class HotCurrentSupportsError(ValueError):
    pass


def parse_current_additions(raw: str) -> list[str]:
    if not isinstance(raw, str) or not raw.strip():
        raise HotCurrentSupportsError("current-additions cue must be non-empty")
    items = [item.strip() for item in raw.split(";")]
    if any(not item for item in items):
        raise HotCurrentSupportsError("current-additions cue contains an empty item")
    if len(items) != len(set(items)):
        raise HotCurrentSupportsError("current-additions cue contains duplicate items")
    return items


def receipt_hot_current_supports(receipt: dict[str, Any]) -> list[str]:
    supports = receipt.get("hot_current_supports")
    if not isinstance(supports, list) or not supports:
        raise HotCurrentSupportsError("receipt hot_current_supports must be a non-empty list")
    if not all(isinstance(item, str) and item.strip() == item and item for item in supports):
        raise HotCurrentSupportsError("receipt hot_current_supports entries must be non-empty normalized strings")
    if len(supports) != len(set(supports)):
        raise HotCurrentSupportsError("receipt hot_current_supports must not contain duplicates")
    if len(supports) > MAX_HOT_CURRENT_SUPPORTS:
        raise HotCurrentSupportsError(
            f"receipt hot_current_supports count {len(supports)} exceeds budget {MAX_HOT_CURRENT_SUPPORTS}"
        )
    return list(supports)


def validate_hot_current_supports(root: pathlib.Path, receipt: dict[str, Any]) -> list[str]:
    root = pathlib.Path(root)
    supports = receipt_hot_current_supports(receipt)
    canon = receipt.get("canon_additions")
    touched = receipt.get("touched_surfaces")
    if not isinstance(canon, list) or not canon:
        raise HotCurrentSupportsError("receipt canon_additions must be a non-empty list")
    if not isinstance(touched, list) or not touched:
        raise HotCurrentSupportsError("receipt touched_surfaces must be a non-empty list")

    noncanon = [item for item in supports if item not in canon]
    if noncanon:
        raise HotCurrentSupportsError("hot_current_supports contains non-canon items: " + ", ".join(noncanon))
    missing = [item for item in supports if not (root / item).exists()]
    if missing:
        raise HotCurrentSupportsError("hot_current_supports names missing surfaces: " + ", ".join(missing))
    missing_anchors = [item for item in REQUIRED_HOT_ANCHORS if item not in supports]
    if missing_anchors:
        raise HotCurrentSupportsError("hot_current_supports missing reentry anchors: " + ", ".join(missing_anchors))
    if len(canon) > MAX_HOT_CURRENT_SUPPORTS and supports == canon:
        raise HotCurrentSupportsError("hot_current_supports regressed to the oversized canon_additions list")
    if len(touched) > MAX_HOT_CURRENT_SUPPORTS and supports == touched:
        raise HotCurrentSupportsError("hot_current_supports regressed to the oversized touched_surfaces list")
    return supports


def single_cue_match(pattern: re.Pattern[str], text: str, label: str) -> re.Match[str]:
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise HotCurrentSupportsError(f"{label} must contain exactly one matching cue, found {len(matches)}")
    return matches[0]


def latest_cue_items(text: str, label: str) -> tuple[re.Match[str], list[str]]:
    match = single_cue_match(LATEST_CUE_RE, text, label)
    return match, parse_current_additions(match.group("additions"))


def docs_head_cue_items(text: str, label: str = "docs/README.md") -> tuple[re.Match[str], list[str]]:
    match = single_cue_match(DOCS_HEAD_CUE_RE, text, label)
    return match, parse_current_additions(match.group("additions"))
