from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from vhk.core.models import I3WindowSelector


@dataclass(frozen=True)
class SelectorSuggestion:
    """A best-effort selector suggestion derived from multiple observations."""

    stable: I3WindowSelector
    exact: I3WindowSelector
    title_strategy: str  # none | exact | alternation | prefix
    stats: dict[str, Any]


def _norm_str(v: object | None) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def _common_value(values: list[str | None]) -> str | None:
    """Return the shared non-empty value if all non-empty values match."""

    vals = [_norm_str(v) for v in values]
    non_empty = [v for v in vals if v is not None]
    if not non_empty:
        return None
    if all(v == non_empty[0] for v in non_empty):
        # If some are empty and some are non-empty, treat as unstable.
        if len(non_empty) != len(vals):
            return None
        return non_empty[0]
    return None


def _common_prefix(values: list[str]) -> str:
    if not values:
        return ""
    prefix = values[0]
    for v in values[1:]:
        # shrink until it is a prefix of v
        while prefix and not v.startswith(prefix):
            prefix = prefix[:-1]
        if not prefix:
            break
    return prefix


def _title_pattern(titles: list[str], *, max_alternations: int = 6, min_prefix_len: int = 6) -> tuple[str | None, bool, str]:
    """Choose a conservative title matcher.

    Returns (pattern, is_regex, strategy).
    """

    uniq = [t for t in dict.fromkeys([_norm_str(t) for t in titles]).keys() if t]
    if not uniq:
        return None, False, "none"
    if len(uniq) == 1:
        return uniq[0], False, "exact"

    # Exact alternation is safe and explicit, but cap to keep configs readable.
    if len(uniq) <= max_alternations:
        alts = "|".join(re.escape(t) for t in uniq)
        return rf"^(?:{alts})$", True, "alternation"

    # Fallback: common prefix, if it looks meaningful.
    prefix = _common_prefix(uniq)
    if len(prefix) >= min_prefix_len:
        return rf"^{re.escape(prefix)}.*", True, "prefix"

    # Give up on title; better to be stable than wrong.
    return None, False, "none"


def suggest_selectors(
    window_infos: list[dict[str, Any]],
    *,
    include_workspace: bool = False,
    include_title_in_stable: bool = False,
    include_title_in_exact: bool = True,
) -> SelectorSuggestion:
    """Suggest stable/exact selectors from a sequence of active-window observations.

    The inputs are dicts such as those returned by `get_active_window_info()` or
    `window_info_from_event()`.

    Philosophy:
    - Prefer stable identifiers (app_id/class/instance/role)
    - Only include title when it appears consistent or can be matched safely
    """

    # Normalize fields.
    app_ids = [_norm_str(w.get("app_id")) for w in window_infos]
    classes = [_norm_str(w.get("class") or w.get("wm_class")) for w in window_infos]
    instances = [_norm_str(w.get("instance")) for w in window_infos]
    roles = [_norm_str(w.get("window_role")) for w in window_infos]
    workspaces = [_norm_str(w.get("workspace")) for w in window_infos]
    titles = [_norm_str(w.get("title")) for w in window_infos]

    common_app_id = _common_value(app_ids)
    common_class = _common_value(classes)
    common_instance = _common_value(instances)
    common_role = _common_value(roles)
    common_ws = _common_value(workspaces) if include_workspace else None

    stable_data: dict[str, Any] = {}
    if common_app_id:
        stable_data["app_id"] = common_app_id
    if common_class:
        stable_data["class"] = common_class
    if common_instance:
        stable_data["instance"] = common_instance
    if common_role:
        stable_data["window_role"] = common_role
    if common_ws:
        stable_data["workspace"] = common_ws

    title_pat, title_regex, title_strategy = _title_pattern([t for t in titles if t])

    exact_data = dict(stable_data)
    if include_title_in_exact and title_pat:
        exact_data["title"] = title_pat
        exact_data["title_regex"] = bool(title_regex)

    stable2 = dict(stable_data)
    if include_title_in_stable and title_pat:
        stable2["title"] = title_pat
        stable2["title_regex"] = bool(title_regex)

    stable_sel = I3WindowSelector.model_validate(stable2)
    exact_sel = I3WindowSelector.model_validate(exact_data)

    uniq_titles = sorted({t for t in titles if t})
    uniq_classes = sorted({c for c in classes if c})
    uniq_app_ids = sorted({a for a in app_ids if a})

    stats: dict[str, Any] = {
        "samples": len(window_infos),
        "unique": {
            "titles": uniq_titles,
            "classes": uniq_classes,
            "app_ids": uniq_app_ids,
        },
        "title_consistent": len(uniq_titles) <= 1,
    }

    return SelectorSuggestion(stable=stable_sel, exact=exact_sel, title_strategy=title_strategy, stats=stats)
