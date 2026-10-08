from __future__ import annotations

import json
import re
import shlex
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from . import VM, MicromaxError


BOOT_STDLIB_PORTABILITY_MANIFEST: dict[str, list[str]] = {
    "nip": ["stdlib-nip-drops-under-top-item"],
    "tuck": ["stdlib-tuck-copies-top-under-next"],
    "?dup": ["stdlib-qdup-zero-leaves-zero", "stdlib-qdup-nonzero-duplicates"],
    "1+": ["stdlib-one-plus-increments"],
    "1-": ["stdlib-one-minus-decrements"],
    "2*": ["stdlib-two-times-doubles"],
    "2/": ["stdlib-two-slash-halves-with-sign-propagation"],
    "2dup": ["stdlib-2dup-copies-pair"],
    "2drop": ["stdlib-2drop-removes-pair"],
    "2nip": ["stdlib-2nip-drops-underlying-pair"],
    "2over": ["stdlib-2over-copies-leading-pair"],
    "2tuck": ["stdlib-2tuck-tucks-top-pair-under-copy"],
    "2swap": ["stdlib-2swap-exchanges-top-pairs"],
    "2rot": ["stdlib-2rot-rotates-three-pairs-left", "stdlib-2rot-moves-front-pair-to-back"],
    "2>r": ["stdlib-2to-r-2r-from-roundtrip"],
    "2r>": ["stdlib-2to-r-2r-from-roundtrip"],
    "2r@": ["stdlib-2r-fetch-preserves-pair-on-return-stack", "stdlib-2r-fetch-keeps-return-stack-depth"],
    "2rdrop": ["stdlib-2rdrop-removes-pair-from-return-stack", "stdlib-2rdrop-preserves-older-return-stack-items"],
    "negate": ["stdlib-negate-zero-is-zero", "stdlib-negate-inverts-sign"],
    "0<": ["stdlib-zero-less-predicate"],
    "0>": ["stdlib-zero-greater-predicate"],
    "0<>": ["stdlib-zero-not-equals-predicate"],
    "<>": ["stdlib-not-equals-predicate", "stdlib-not-equals-handles-strings"],
    "abs": ["stdlib-abs-normalizes-sign"],
    "max": ["stdlib-max-picks-greater-value"],
    "min": ["stdlib-min-picks-smaller-value"],
    "rdrop": ["stdlib-rdrop-removes-top-return-stack-item", "stdlib-rdrop-preserves-older-return-stack-items"],
    "dip": ["stdlib-dip"],
    "keep": ["stdlib-keep"],
    "2dip": ["stdlib-2dip"],
    "2keep": ["stdlib-2keep"],
    "bi": ["stdlib-bi"],
    "tri": ["stdlib-tri"],
    "assert": ["stdlib-assert-true-drops-message-and-keeps-outer-stack", "stdlib-assert-false-throws-message-and-preserves-outer-stack"],
    "try?": ["stdlib-try-question-failure-restores-stack", "stdlib-try-question-success-returns-result-and-flag"],
    "try": [
        "stdlib-try-handler-on-failure",
        "stdlib-try-success-ignores-handler",
        "stdlib-try-handler-error-wins-on-failure",
    ],
    "recover": [
        "stdlib-recover-handler-on-failure",
        "stdlib-recover-success-ignores-handler",
        "stdlib-recover-handler-error-wins-on-failure",
    ],
    "ensure": [
        "stdlib-ensure-success-runs-cleanup",
        "stdlib-ensure-failure-reraises-after-cleanup",
        "stdlib-ensure-cleanup-error-wins-on-success",
        "stdlib-ensure-cleanup-error-wins-on-failure",
    ],
    "finally": [
        "stdlib-finally-success-runs-cleanup",
        "stdlib-finally-failure-reraises-after-cleanup",
        "stdlib-finally-cleanup-error-wins-on-success",
        "stdlib-finally-cleanup-error-wins-on-failure",
    ],
}


def boot_stdlib_portability_manifest() -> dict[str, list[str]]:
    return {word: list(case_names) for word, case_names in BOOT_STDLIB_PORTABILITY_MANIFEST.items()}


def boot_stdlib_source_path() -> Path:
    return Path(__file__).resolve().parent / "stdlib" / "core.mx"


_STDLIB_NUMBER_TOKEN = re.compile(r"^[+-]?\d+$")
_STDLIB_STRING_TOKEN = re.compile(r'^"(?:[^"\\]|\\.)*"$')


def _tokenize_stdlib_definition(definition: str) -> list[str]:
    return [tok for tok in re.split(r"\s+", str(definition or "").strip()) if tok]


def _is_stdlib_literal_token(token: str) -> bool:
    tok = str(token or "")
    if not tok:
        return False
    if _STDLIB_NUMBER_TOKEN.match(tok):
        return True
    if _STDLIB_STRING_TOKEN.match(tok):
        return True
    return False


def _classify_stdlib_definition(definition: str, known_words: set[str]) -> dict[str, Any]:
    body_tokens = _tokenize_stdlib_definition(definition)
    syntax_tokens = [tok for tok in body_tokens if tok in {"[", "]"}]
    literal_tokens = [tok for tok in body_tokens if _is_stdlib_literal_token(tok)]
    word_refs: list[str] = []
    stdlib_refs: list[str] = []
    nonstdlib_refs: list[str] = []
    for tok in body_tokens:
        if tok in {"[", "]"} or _is_stdlib_literal_token(tok):
            continue
        if tok not in word_refs:
            word_refs.append(tok)
        bucket = stdlib_refs if tok in known_words else nonstdlib_refs
        if tok not in bucket:
            bucket.append(tok)
    alias_of = ""
    if len(word_refs) == 1 and not syntax_tokens and not literal_tokens:
        alias_of = word_refs[0]
    return {
        "body_tokens": body_tokens,
        "syntax_tokens": syntax_tokens,
        "literal_tokens": literal_tokens,
        "word_refs": word_refs,
        "stdlib_refs": stdlib_refs,
        "nonstdlib_refs": nonstdlib_refs,
        "alias_of": alias_of,
    }


def _append_unique(items: list[str], values: Iterable[str]) -> None:
    for value in values:
        text = str(value or "")
        if text and text not in items:
            items.append(text)


def portability_case_name_args(case_names: Iterable[str]) -> list[str]:
    args: list[str] = []
    seen: list[str] = []
    for name in case_names:
        text = str(name or "")
        if not text or text in seen:
            continue
        seen.append(text)
        args.extend(["--name", text])
    return args


def portability_retest_env() -> dict[str, str]:
    return {"PYTHONPATH": "src"}


def portability_retest_argv(
    case_names: Iterable[str],
    *,
    json_mode: bool = False,
    base_argv: Iterable[str] | None = None,
) -> list[str]:
    argv = list(base_argv or ["python", "tools/mxportable.py"])
    argv.extend(portability_case_name_args(case_names))
    if json_mode:
        argv.append("--json")
    return argv


def _argv_suffix(args: Iterable[str] | None = None) -> str:
    return " ".join(shlex.quote(str(arg)) for arg in (args or []) if str(arg))


def portability_filter_metadata(*args: str) -> dict[str, Any]:
    argv = [str(arg) for arg in args if str(arg)]
    return {
        "filter_argv": argv,
        "filter_suffix": _argv_suffix(argv),
    }


def stdlib_impact_preview_fields(
    groups: Iterable[dict[str, Any]],
    *,
    cases: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    group_list = [dict(group) for group in groups]
    impact_words: list[str] = []
    impact_case_names: list[str] = []
    for group in group_list:
        _append_unique(impact_words, [str(group.get("word") or "")])
        _append_unique(impact_case_names, group.get("case_names") or [])
    stages = stdlib_impact_stages(group_list, cases=cases)
    return {
        "preview_impact_words": impact_words,
        "preview_impact_word_count": len(impact_words),
        "preview_impact_case_names": impact_case_names,
        "preview_impact_case_count": len(impact_case_names),
        "preview_impact_group_count": len(group_list),
        "preview_impact_stage_count": len(stages),
    }


def stdlib_impact_preview_delta_fields(
    preview: dict[str, Any],
    *,
    baseline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    current = dict(baseline or {})
    preview_words = [str(word) for word in (preview.get("preview_impact_words") or []) if str(word)]
    preview_case_names = [str(name) for name in (preview.get("preview_impact_case_names") or []) if str(name)]
    current_words = [str(word) for word in (current.get("preview_impact_words") or []) if str(word)]
    current_case_names = [str(name) for name in (current.get("preview_impact_case_names") or []) if str(name)]
    word_delta = int(preview.get("preview_impact_word_count") or 0) - int(current.get("preview_impact_word_count") or 0)
    case_delta = int(preview.get("preview_impact_case_count") or 0) - int(current.get("preview_impact_case_count") or 0)
    stage_delta = int(preview.get("preview_impact_stage_count") or 0) - int(current.get("preview_impact_stage_count") or 0)
    same_slice = preview_words == current_words and preview_case_names == current_case_names
    effect = "mixed"
    if same_slice:
        effect = "same-slice"
    elif word_delta == 0 and case_delta == 0 and stage_delta == 0:
        effect = "same-size-pivot"
    elif word_delta <= 0 and case_delta <= 0 and stage_delta <= 0:
        effect = "narrower"
    elif word_delta >= 0 and case_delta >= 0 and stage_delta >= 0:
        effect = "broader"
    return {
        "preview_is_current_slice": same_slice,
        "preview_changes_slice": not same_slice,
        "preview_effect": effect,
        "preview_impact_word_delta": word_delta,
        "preview_impact_case_delta": case_delta,
        "preview_impact_stage_delta": stage_delta,
        "preview_impact_word_reduction": max(-word_delta, 0),
        "preview_impact_case_reduction": max(-case_delta, 0),
        "preview_impact_stage_reduction": max(-stage_delta, 0),
    }


def impact_filter_transition_metadata(
    family_flag: str,
    *,
    current_family_argv: Iterable[str] | None = None,
    effective_family_argv: Iterable[str] | None = None,
    family_mode: str = "replace",
) -> dict[str, Any]:
    family = str(family_flag or "").strip()
    current_argv = [str(arg) for arg in (current_family_argv or []) if str(arg)]
    effective_argv = [str(arg) for arg in (effective_family_argv or []) if str(arg)]
    mode = "append" if str(family_mode or "").strip().lower() == "append" else "replace"
    return {
        "filter_family": family.lstrip("-"),
        "family_mode": mode,
        "current_family_argv": current_argv,
        "current_family_suffix": _argv_suffix(current_argv),
        "effective_family_argv": effective_argv,
        "effective_family_suffix": _argv_suffix(effective_argv),
    }


def impact_filter_option_label(family: str, row: dict[str, Any]) -> str:
    label = str(row.get("name") or "")
    if label:
        return label
    if family == "distances" and "distance" in row:
        return str(int(row.get("distance") or 0))
    return ""


def stdlib_impact_filter_equivalence_key(row: dict[str, Any]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    words = tuple(str(word) for word in (row.get("preview_impact_words") or []) if str(word))
    case_names = tuple(str(name) for name in (row.get("preview_impact_case_names") or []) if str(name))
    return (words, case_names)


def annotate_stdlib_impact_filter_option_equivalences(options: dict[str, Any]) -> dict[str, Any]:
    families = ("words", "distances", "categories", "tags", "names")
    grouped: dict[tuple[tuple[str, ...], tuple[str, ...]], list[dict[str, Any]]] = {}
    for family in families:
        for row in options.get(family) or []:
            entry = {
                "family": family,
                "label": impact_filter_option_label(family, row),
                "row": row,
            }
            key = stdlib_impact_filter_equivalence_key(row)
            grouped.setdefault(key, []).append(entry)
    for family in families:
        for row in options.get(family) or []:
            family_name = family
            label = impact_filter_option_label(family_name, row)
            key = stdlib_impact_filter_equivalence_key(row)
            row["equivalence_key"] = {
                "preview_impact_words": list(key[0]),
                "preview_impact_case_names": list(key[1]),
            }
            equivalents: list[dict[str, Any]] = []
            for entry in grouped.get(key, []):
                if entry["family"] == family_name and entry["label"] == label:
                    continue
                peer = dict(entry["row"])
                equivalents.append(
                    {
                        "option_family": entry["family"],
                        "option_label": entry["label"],
                        "filter_suffix": str(peer.get("filter_suffix") or ""),
                        "show_impact_command": str(peer.get("show_impact_command") or ""),
                    }
                )
            equivalents.sort(key=lambda item: (item["option_family"], item["option_label"]))
            row["equivalent_options"] = equivalents
            row["equivalent_option_count"] = len(equivalents)
            row["has_equivalent_options"] = bool(equivalents)
    return options


IMPACT_FILTER_FAMILY_PRIORITY = {
    "words": 0,
    "distances": 1,
    "tags": 2,
    "categories": 3,
    "names": 4,
}


def impact_filter_option_preference_reason(row: dict[str, Any]) -> dict[str, Any]:
    family = str(row.get("option_family") or "")
    alternatives = [dict(item) for item in (row.get("represented_alternatives") or [])]
    alt_labels = [
        f"{str(item.get('option_family') or '?')}:{str(item.get('option_label') or '')}".rstrip(":")
        for item in alternatives
    ]
    if not alternatives:
        return {
            "representative_reason_code": "only-option",
            "representative_reason": "only distinct cut for this slice",
            "represented_alternative_labels": [],
            "represented_alternative_families": [],
        }
    family_rank = IMPACT_FILTER_FAMILY_PRIORITY.get(family, 99)
    alt_ranks = [IMPACT_FILTER_FAMILY_PRIORITY.get(str(item.get("option_family") or ""), 99) for item in alternatives]
    alt_families = [str(item.get("option_family") or "") for item in alternatives]
    if alt_ranks and all(rank > family_rank for rank in alt_ranks):
        reason_code = "coarser-family"
        reason = f"preferred as the coarsest equivalent cut over {', '.join(alt_labels)}"
    elif alt_ranks and all(rank == family_rank for rank in alt_ranks):
        reason_code = "same-family-earlier-rank"
        reason = f"preferred as the highest-ranked equivalent cut over {', '.join(alt_labels)}"
    else:
        reason_code = "mixed-family-earlier-rank"
        reason = f"preferred as the highest-ranked reusable cut over {', '.join(alt_labels)}"
    return {
        "representative_reason_code": reason_code,
        "representative_reason": reason,
        "represented_alternative_labels": alt_labels,
        "represented_alternative_families": alt_families,
    }


def stdlib_recommended_impact_filter_options(
    options: dict[str, Any],
    *,
    limit: int = 5,
) -> list[dict[str, Any]]:
    family_priority = IMPACT_FILTER_FAMILY_PRIORITY
    candidates: list[dict[str, Any]] = []
    for family in ("words", "distances", "tags", "categories", "names"):
        for raw_row in options.get(family) or []:
            row = dict(raw_row)
            word_reduction = int(row.get("preview_impact_word_reduction") or 0)
            case_reduction = int(row.get("preview_impact_case_reduction") or 0)
            stage_reduction = int(row.get("preview_impact_stage_reduction") or 0)
            if not bool(row.get("preview_changes_slice")):
                continue
            if word_reduction <= 0 and case_reduction <= 0 and stage_reduction <= 0:
                continue
            label = impact_filter_option_label(family, row)
            row["option_family"] = family
            row["option_label"] = label
            candidates.append(row)
    candidates.sort(
        key=lambda row: (
            0 if str(row.get("preview_effect") or "") == "narrower" else 1,
            family_priority.get(str(row.get("option_family") or ""), 99),
            -int(row.get("preview_impact_case_reduction") or 0),
            -int(row.get("preview_impact_word_reduction") or 0),
            -int(row.get("preview_impact_stage_reduction") or 0),
            int(row.get("preview_impact_case_count") or 0),
            int(row.get("preview_impact_word_count") or 0),
            str(row.get("option_label") or row.get("name") or ""),
        )
    )
    out: list[dict[str, Any]] = []
    cap = max(int(limit), 0)
    for rank, row in enumerate(candidates[:cap], start=1):
        item = dict(row)
        item["recommendation_rank"] = rank
        out.append(item)
    return out


def impact_filter_option_summary(row: dict[str, Any]) -> dict[str, Any]:
    recommendation_rank = int(row.get("recommendation_rank") or 0)
    source_recommendation_rank = int(row.get("source_recommendation_rank") or recommendation_rank)
    return {
        "recommendation_rank": recommendation_rank,
        "source_recommendation_rank": source_recommendation_rank,
        "option_family": str(row.get("option_family") or ""),
        "option_label": str(row.get("option_label") or ""),
        "filter_suffix": str(row.get("filter_suffix") or ""),
        "show_impact_command": str(row.get("show_impact_command") or ""),
        "show_impact_json_command": str(row.get("show_impact_json_command") or ""),
    }


def stdlib_distinct_impact_filter_options(
    rows: Iterable[dict[str, Any]],
    *,
    limit: int = 5,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[tuple[str, ...], tuple[str, ...]], list[dict[str, Any]]] = {}
    ordered_keys: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
    for raw_row in rows:
        row = dict(raw_row)
        key = stdlib_impact_filter_equivalence_key(row)
        if key not in grouped:
            ordered_keys.append(key)
            grouped[key] = []
        grouped[key].append(row)
    distinct: list[dict[str, Any]] = []
    cap = max(int(limit), 0)
    for key in ordered_keys[:cap]:
        members = grouped.get(key) or []
        if not members:
            continue
        row = dict(members[0])
        row["source_recommendation_rank"] = int(row.get("recommendation_rank") or 0)
        represented = [impact_filter_option_summary(member) for member in members]
        represented_alternatives = [dict(item) for item in represented[1:]]
        represented_ranks = [
            int(item.get("source_recommendation_rank") or item.get("recommendation_rank") or 0)
            for item in represented
            if int(item.get("source_recommendation_rank") or item.get("recommendation_rank") or 0) > 0
        ]
        represented_alternative_ranks = [
            int(item.get("source_recommendation_rank") or item.get("recommendation_rank") or 0)
            for item in represented_alternatives
            if int(item.get("source_recommendation_rank") or item.get("recommendation_rank") or 0) > 0
        ]
        row["represented_options"] = represented
        row["represented_option_count"] = len(represented)
        row["represented_alternatives"] = represented_alternatives
        row["represented_alternative_count"] = len(represented_alternatives)
        row["represented_recommendation_ranks"] = represented_ranks
        row["represented_alternative_ranks"] = represented_alternative_ranks
        row["represented_rank_count"] = len(represented_ranks)
        row["represented_rank_min"] = min(represented_ranks) if represented_ranks else 0
        row["represented_rank_max"] = max(represented_ranks) if represented_ranks else 0
        row.update(impact_filter_option_preference_reason(row))
        distinct.append(row)
    for rank, row in enumerate(distinct, start=1):
        row["recommendation_rank"] = rank
    return distinct


def stdlib_distinct_impact_filter_groups(
    rows: Iterable[dict[str, Any]],
    *,
    limit: int = 5,
) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for row in stdlib_distinct_impact_filter_options(rows, limit=limit):
        represented = [dict(item) for item in (row.get("represented_options") or [])]
        represented_alternatives = [dict(item) for item in (row.get("represented_alternatives") or [])]
        groups.append(
            {
                "recommendation_rank": int(row.get("recommendation_rank") or 0),
                "source_recommendation_rank": int(row.get("source_recommendation_rank") or row.get("recommendation_rank") or 0),
                "equivalence_key": dict(row.get("equivalence_key") or {}),
                "representative": impact_filter_option_summary(row),
                "represented_options": represented,
                "represented_option_count": len(represented),
                "represented_alternatives": represented_alternatives,
                "represented_alternative_count": len(represented_alternatives),
                "represented_recommendation_ranks": list(row.get("represented_recommendation_ranks") or []),
                "represented_alternative_ranks": list(row.get("represented_alternative_ranks") or []),
                "represented_rank_count": int(row.get("represented_rank_count") or 0),
                "represented_rank_min": int(row.get("represented_rank_min") or 0),
                "represented_rank_max": int(row.get("represented_rank_max") or 0),
                "representative_reason_code": str(row.get("representative_reason_code") or ""),
                "representative_reason": str(row.get("representative_reason") or ""),
                "represented_alternative_labels": list(row.get("represented_alternative_labels") or []),
                "represented_alternative_families": list(row.get("represented_alternative_families") or []),
            }
        )
    return groups


def stdlib_primary_impact_filter_option(options: dict[str, Any]) -> dict[str, Any]:
    distinct = [dict(row) for row in (options.get("recommended_distinct") or [])]
    if distinct:
        return distinct[0]
    recommended = [dict(row) for row in (options.get("recommended") or [])]
    if recommended:
        return recommended[0]
    return {}


def stdlib_primary_impact_filter_group(options: dict[str, Any]) -> dict[str, Any]:
    groups = [dict(group) for group in (options.get("recommended_distinct_groups") or [])]
    if groups:
        return groups[0]
    primary = stdlib_primary_impact_filter_option(options)
    if not primary:
        return {}
    represented = [impact_filter_option_summary(primary)]
    represented_ranks = [int(primary.get("source_recommendation_rank") or primary.get("recommendation_rank") or 0)]
    represented_ranks = [rank for rank in represented_ranks if rank > 0]
    return {
        "recommendation_rank": int(primary.get("recommendation_rank") or 0),
        "source_recommendation_rank": int(primary.get("source_recommendation_rank") or primary.get("recommendation_rank") or 0),
        "equivalence_key": dict(primary.get("equivalence_key") or {}),
        "representative": impact_filter_option_summary(primary),
        "represented_options": represented,
        "represented_option_count": len(represented),
        "represented_alternatives": [],
        "represented_alternative_count": 0,
        "represented_recommendation_ranks": represented_ranks,
        "represented_alternative_ranks": [],
        "represented_rank_count": len(represented_ranks),
        "represented_rank_min": min(represented_ranks) if represented_ranks else 0,
        "represented_rank_max": max(represented_ranks) if represented_ranks else 0,
        "representative_reason_code": str(primary.get("representative_reason_code") or ""),
        "representative_reason": str(primary.get("representative_reason") or ""),
        "represented_alternative_labels": list(primary.get("represented_alternative_labels") or []),
        "represented_alternative_families": list(primary.get("represented_alternative_families") or []),
    }


def stdlib_manifest_filter_args(
    *,
    words: Iterable[str] | None = None,
    word_contains: str | None = None,
) -> list[str]:
    argv = ["--stdlib-manifest"]
    seen: list[str] = []
    for word in words or []:
        text = str(word or "")
        if not text or text in seen:
            continue
        seen.append(text)
        argv.extend(["--word", text])
    needle = str(word_contains or "").strip()
    if needle:
        argv.extend(["--word-contains", needle])
    return argv


def stdlib_impact_filter_args(
    *,
    impact_filter_words: Iterable[str] | None = None,
    impact_word_contains: str | None = None,
    impact_distances: Iterable[int] | None = None,
    impact_case_categories: Iterable[str] | None = None,
    impact_case_tags: Iterable[str] | None = None,
    impact_case_names: Iterable[str] | None = None,
    impact_case_name_contains: str | None = None,
) -> list[str]:
    argv: list[str] = []
    seen_words: list[str] = []
    for word in impact_filter_words or []:
        text = str(word or "")
        if not text or text in seen_words:
            continue
        seen_words.append(text)
        argv.extend(["--impact-word", text])
    word_needle = str(impact_word_contains or "").strip()
    if word_needle:
        argv.extend(["--impact-word-contains", word_needle])
    seen_distances: list[int] = []
    for distance in impact_distances or []:
        value = max(int(distance), 0)
        if value in seen_distances:
            continue
        seen_distances.append(value)
        argv.extend(["--impact-distance", str(value)])
    seen_categories: list[str] = []
    for category in impact_case_categories or []:
        text = str(category or "")
        if not text or text in seen_categories:
            continue
        seen_categories.append(text)
        argv.extend(["--impact-category", text])
    seen_tags: list[str] = []
    for tag in impact_case_tags or []:
        text = str(tag or "")
        if not text or text in seen_tags:
            continue
        seen_tags.append(text)
        argv.extend(["--impact-tag", text])
    seen_names: list[str] = []
    for name in impact_case_names or []:
        text = str(name or "")
        if not text or text in seen_names:
            continue
        seen_names.append(text)
        argv.extend(["--impact-name", text])
    name_needle = str(impact_case_name_contains or "").strip()
    if name_needle:
        argv.extend(["--impact-name-contains", name_needle])
    return argv


def stdlib_manifest_show_impact_metadata(
    *,
    selected_words: Iterable[str] | None = None,
    impact_filter_words: Iterable[str] | None = None,
    impact_word_contains: str | None = None,
    impact_distances: Iterable[int] | None = None,
    impact_case_categories: Iterable[str] | None = None,
    impact_case_tags: Iterable[str] | None = None,
    impact_case_names: Iterable[str] | None = None,
    impact_case_name_contains: str | None = None,
    base_argv: Iterable[str] | None = None,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    argv = list(base_argv or ["python", "tools/mxportable.py"])
    argv.extend(stdlib_manifest_filter_args(words=selected_words))
    argv.append("--show-impact")
    argv.extend(
        stdlib_impact_filter_args(
            impact_filter_words=impact_filter_words,
            impact_word_contains=impact_word_contains,
            impact_distances=impact_distances,
            impact_case_categories=impact_case_categories,
            impact_case_tags=impact_case_tags,
            impact_case_names=impact_case_names,
            impact_case_name_contains=impact_case_name_contains,
        )
    )
    json_argv = [*argv, "--json"]
    env_map = dict(env or portability_retest_env())
    return {
        "show_impact_env": env_map,
        "show_impact_argv": argv,
        "show_impact_json_argv": json_argv,
        "show_impact_command": shlex.join([*(f"{key}={value}" for key, value in env_map.items()), *argv]),
        "show_impact_json_command": shlex.join([*(f"{key}={value}" for key, value in env_map.items()), *json_argv]),
    }


def portability_retest_metadata(
    case_names: Iterable[str],
    *,
    base_argv: Iterable[str] | None = None,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    name_args = portability_case_name_args(case_names)
    env_map = dict(env or portability_retest_env())
    argv = portability_retest_argv(case_names, base_argv=base_argv)
    json_argv = portability_retest_argv(case_names, json_mode=True, base_argv=base_argv)
    return {
        "retest_name_args": name_args,
        "retest_env": env_map,
        "retest_argv": argv,
        "retest_json_argv": json_argv,
        "retest_command": shlex.join([*(f"{key}={value}" for key, value in env_map.items()), *argv]),
        "retest_json_command": shlex.join([*(f"{key}={value}" for key, value in env_map.items()), *json_argv]),
    }


def portability_retest_command(
    case_names: Iterable[str],
    *,
    json_mode: bool = False,
    base_argv: Iterable[str] | None = None,
) -> str:
    meta = portability_retest_metadata(case_names, base_argv=base_argv)
    return meta["retest_json_command" if json_mode else "retest_command"]


def portability_cases_by_name(cases: Iterable[dict[str, Any]], case_names: Iterable[str]) -> list[dict[str, Any]]:
    lookup = {str(case.get("name") or ""): case for case in cases}
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for name in case_names:
        text = str(name or "")
        if not text or text in seen:
            continue
        case = lookup.get(text)
        if case is None:
            continue
        out.append(case)
        seen.add(text)
    return out


def stdlib_impact_distance(paths: Iterable[Iterable[str]] | None, *, default: int = 0) -> int:
    distances: list[int] = []
    for raw_path in paths or []:
        path = [str(tok) for tok in raw_path if str(tok)]
        if path:
            distances.append(max(len(path) - 1, 0))
    return min(distances) if distances else max(int(default), 0)


def impact_inventory_fields(cases: Iterable[dict[str, Any]], case_names: Iterable[str]) -> dict[str, Any]:
    inventory = portability_inventory(portability_cases_by_name(cases, case_names))
    return {
        "impact_categories": inventory["categories"],
        "impact_tags": inventory["tags"],
    }


def boot_stdlib_impact_paths(specs: dict[str, dict[str, Any]], root_word: str) -> dict[str, list[str]]:
    root = str(root_word or "")
    if not root or root not in specs:
        return {}
    paths: dict[str, list[str]] = {root: [root]}
    queue: list[str] = [root]
    while queue:
        current = queue.pop(0)
        current_path = list(paths.get(current) or [current])
        for user in specs.get(current, {}).get("direct_stdlib_users") or []:
            user_s = str(user or "")
            if not user_s or user_s in paths:
                continue
            paths[user_s] = current_path + [user_s]
            queue.append(user_s)
    return paths


def stdlib_impact_groups(
    root_word: str,
    impact_words: Iterable[str],
    *,
    manifest: dict[str, list[str]] | None = None,
    specs: dict[str, dict[str, Any]] | None = None,
    cases: Iterable[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    manifest_entries = manifest or BOOT_STDLIB_PORTABILITY_MANIFEST
    spec_map = specs or {}
    path_map = boot_stdlib_impact_paths(spec_map, root_word)
    groups: list[dict[str, Any]] = []
    seen: set[str] = set()
    for word in impact_words:
        impact_word = str(word or "")
        if not impact_word or impact_word in seen:
            continue
        seen.add(impact_word)
        spec = spec_map.get(impact_word) or {}
        case_names = list(manifest_entries.get(impact_word) or [])
        path = list(path_map.get(impact_word) or ([impact_word] if impact_word else []))
        group = {
            "word": impact_word,
            "line": int(spec.get("line") or 0),
            "stack_effect": str(spec.get("stack_effect") or ""),
            "alias_of": str(spec.get("alias_of") or ""),
            "selected_words": [str(root_word)],
            "selected_word_count": 1,
            "paths": [path] if path else [],
            "path_count": 1 if path else 0,
            "distance": stdlib_impact_distance([path] if path else [], default=0),
            "case_names": case_names,
            "case_count": len(case_names),
        }
        group.update(portability_retest_metadata(case_names))
        if cases is not None:
            inventory = portability_inventory(portability_cases_by_name(cases, case_names))
            group["categories"] = inventory["categories"]
            group["tags"] = inventory["tags"]
        groups.append(group)
    return groups


def select_stdlib_impact_groups(
    groups: Iterable[dict[str, Any]],
    *,
    words: Iterable[str] | None = None,
    word_contains: str | None = None,
    distances: Iterable[int] | None = None,
) -> list[dict[str, Any]]:
    wanted = {str(word).strip() for word in (words or []) if str(word).strip()}
    needle = str(word_contains or "").strip().lower()
    distance_wanted = {max(int(distance), 0) for distance in (distances or [])}
    out: list[dict[str, Any]] = []
    for raw_group in groups:
        group = dict(raw_group)
        word = str(group.get("word") or "")
        if not word:
            continue
        if wanted and word not in wanted:
            continue
        if needle and needle not in word.lower():
            continue
        paths: list[list[str]] = []
        for raw_path in group.get("paths") or []:
            path = [str(tok) for tok in raw_path if str(tok)]
            if path and path not in paths:
                paths.append(path)
        distance = stdlib_impact_distance(paths, default=int(group.get("distance") or 0))
        if distance_wanted and distance not in distance_wanted:
            continue
        case_names: list[str] = []
        _append_unique(case_names, group.get("case_names") or [])
        selected_words: list[str] = []
        _append_unique(selected_words, group.get("selected_words") or [])
        group["paths"] = paths
        group["path_count"] = len(paths)
        group["distance"] = distance
        group["case_names"] = case_names
        group["case_count"] = len(case_names)
        group["selected_words"] = selected_words
        group["selected_word_count"] = len(selected_words)
        group.update(portability_retest_metadata(case_names))
        out.append(group)
    return out


def select_stdlib_impact_case_names(
    case_names: Iterable[str],
    *,
    cases: Iterable[dict[str, Any]] | None = None,
    categories: Iterable[str] | None = None,
    tags: Iterable[str] | None = None,
    names: Iterable[str] | None = None,
    name_contains: str | None = None,
) -> list[str]:
    selected_cases = portability_cases_by_name(cases or [], case_names)
    selected_cases = select_portability_cases(
        selected_cases,
        categories=categories,
        tags=tags,
        names=names,
        name_contains=name_contains,
    )
    return [str(case.get("name") or "") for case in selected_cases if str(case.get("name") or "")]


def refilter_stdlib_impact_groups(
    groups: Iterable[dict[str, Any]],
    *,
    cases: Iterable[dict[str, Any]] | None = None,
    case_categories: Iterable[str] | None = None,
    case_tags: Iterable[str] | None = None,
    case_names: Iterable[str] | None = None,
    case_name_contains: str | None = None,
) -> list[dict[str, Any]]:
    if (
        not list(case_categories or [])
        and not list(case_tags or [])
        and not list(case_names or [])
        and not str(case_name_contains or "").strip()
    ):
        return [dict(group) for group in groups]
    out: list[dict[str, Any]] = []
    for raw_group in groups:
        group = dict(raw_group)
        filtered_case_names = select_stdlib_impact_case_names(
            group.get("case_names") or [],
            cases=cases,
            categories=case_categories,
            tags=case_tags,
            names=case_names,
            name_contains=case_name_contains,
        )
        if not filtered_case_names:
            continue
        group["case_names"] = list(filtered_case_names)
        group["case_count"] = len(filtered_case_names)
        group.update(portability_retest_metadata(filtered_case_names))
        if cases is not None:
            inventory = portability_inventory(portability_cases_by_name(cases, filtered_case_names))
            group["categories"] = inventory["categories"]
            group["tags"] = inventory["tags"]
        out.append(group)
    return out


def merge_stdlib_impact_groups(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    by_word: dict[str, dict[str, Any]] = {}
    for row in rows:
        for group in row.get("impact_groups") or []:
            word = str(group.get("word") or "")
            if not word:
                continue
            current = by_word.get(word)
            if current is None:
                current = {
                    "word": word,
                    "line": int(group.get("line") or 0),
                    "stack_effect": str(group.get("stack_effect") or ""),
                    "alias_of": str(group.get("alias_of") or ""),
                    "selected_words": [],
                    "case_names": [str(name) for name in (group.get("case_names") or [])],
                    "case_count": int(group.get("case_count") or len(group.get("case_names") or [])),
                    "paths": [],
                    "distance": int(group.get("distance") or 0),
                }
                current.update(portability_retest_metadata(current["case_names"]))
                if "categories" in group:
                    current["categories"] = [dict(item) for item in (group.get("categories") or [])]
                if "tags" in group:
                    current["tags"] = [dict(item) for item in (group.get("tags") or [])]
                merged.append(current)
                by_word[word] = current
            _append_unique(current["selected_words"], group.get("selected_words") or [])
            for raw_path in group.get("paths") or []:
                path = [str(tok) for tok in raw_path if str(tok)]
                if path and path not in current["paths"]:
                    current["paths"].append(path)
            current["selected_word_count"] = len(current["selected_words"])
            current["path_count"] = len(current["paths"])
            current["distance"] = stdlib_impact_distance(current["paths"], default=int(current.get("distance") or 0))
            current.update(portability_retest_metadata(current["case_names"]))
    return merged


def stdlib_impact_stages(
    groups: Iterable[dict[str, Any]],
    *,
    cases: Iterable[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    by_distance: dict[int, dict[str, Any]] = {}
    ordered_distances: list[int] = []
    for group in groups:
        distance = stdlib_impact_distance(group.get("paths") or [], default=int(group.get("distance") or 0))
        stage = by_distance.get(distance)
        if stage is None:
            stage = {
                "distance": distance,
                "words": [],
                "selected_words": [],
                "case_names": [],
            }
            by_distance[distance] = stage
            ordered_distances.append(distance)
        _append_unique(stage["words"], [str(group.get("word") or "")])
        _append_unique(stage["selected_words"], group.get("selected_words") or [])
        _append_unique(stage["case_names"], group.get("case_names") or [])
    stages: list[dict[str, Any]] = []
    for distance in sorted(ordered_distances):
        stage = by_distance[distance]
        stage["word_count"] = len(stage["words"])
        stage["selected_word_count"] = len(stage["selected_words"])
        stage["case_count"] = len(stage["case_names"])
        stage.update(portability_retest_metadata(stage["case_names"]))
        if cases is not None:
            stage.update(impact_inventory_fields(cases, stage["case_names"]))
        stages.append(stage)
    return stages


def stdlib_impact_filter_options(
    groups: Iterable[dict[str, Any]],
    *,
    cases: Iterable[dict[str, Any]] | None = None,
    selected_words: Iterable[str] | None = None,
    impact_filter_words: Iterable[str] | None = None,
    impact_word_contains: str | None = None,
    impact_distances: Iterable[int] | None = None,
    impact_case_categories: Iterable[str] | None = None,
    impact_case_tags: Iterable[str] | None = None,
    impact_case_names: Iterable[str] | None = None,
    impact_case_name_contains: str | None = None,
) -> dict[str, Any]:
    group_list = list(groups)
    selection_words: list[str] = []
    _append_unique(selection_words, selected_words or [])
    if not selection_words:
        for group in group_list:
            _append_unique(selection_words, group.get("selected_words") or [])
    current_filter_words: list[str] = []
    _append_unique(current_filter_words, impact_filter_words or [])
    current_distances: list[int] = []
    for distance in impact_distances or []:
        value = max(int(distance), 0)
        if value not in current_distances:
            current_distances.append(value)
    current_categories: list[str] = []
    _append_unique(current_categories, impact_case_categories or [])
    current_tags: list[str] = []
    _append_unique(current_tags, impact_case_tags or [])
    current_names: list[str] = []
    _append_unique(current_names, impact_case_names or [])
    baseline_preview = stdlib_impact_preview_fields(group_list, cases=cases)

    def _preview(groups_subset: Iterable[dict[str, Any]]) -> dict[str, Any]:
        preview = stdlib_impact_preview_fields(groups_subset, cases=cases)
        preview.update(stdlib_impact_preview_delta_fields(preview, baseline=baseline_preview))
        return preview

    def _preview_by_name(case_name: str) -> dict[str, Any]:
        if cases is not None:
            filtered = refilter_stdlib_impact_groups(group_list, cases=cases, case_names=[case_name])
        else:
            wanted = str(case_name or "")
            filtered = []
            for raw_group in group_list:
                group = dict(raw_group)
                case_names = [name for name in (group.get("case_names") or []) if str(name) == wanted]
                if not case_names:
                    continue
                group["case_names"] = case_names
                group["case_count"] = len(case_names)
                group.update(portability_retest_metadata(case_names))
                filtered.append(group)
        return _preview(filtered)

    word_rows: list[dict[str, Any]] = []
    by_distance: dict[int, dict[str, Any]] = {}
    ordered_distances: list[int] = []
    category_counts: dict[str, int] = {}
    tag_counts: dict[str, int] = {}
    name_rows: list[dict[str, Any]] = []
    by_case_name: dict[str, dict[str, Any]] = {}
    for group in group_list:
        word = str(group.get("word") or "")
        if not word:
            continue
        distance = int(group.get("distance") or 0)
        case_names = [str(name) for name in (group.get("case_names") or []) if str(name)]
        word_rows.append(
            {
                "name": word,
                "distance": distance,
                "case_count": len(case_names),
                **_preview(select_stdlib_impact_groups(group_list, words=[word])),
                **portability_filter_metadata("--impact-word", word),
                **impact_filter_transition_metadata(
                    "--impact-word",
                    current_family_argv=stdlib_impact_filter_args(impact_filter_words=current_filter_words),
                    effective_family_argv=stdlib_impact_filter_args(impact_filter_words=[word]),
                    family_mode="replace",
                ),
                **stdlib_manifest_show_impact_metadata(
                    selected_words=selection_words,
                    impact_filter_words=[word],
                    impact_word_contains=impact_word_contains,
                    impact_distances=current_distances,
                    impact_case_categories=current_categories,
                    impact_case_tags=current_tags,
                    impact_case_names=current_names,
                    impact_case_name_contains=impact_case_name_contains,
                ),
            }
        )
        stage = by_distance.get(distance)
        if stage is None:
            stage = {
                "distance": distance,
                "words": [],
                "case_names": [],
            }
            by_distance[distance] = stage
            ordered_distances.append(distance)
        _append_unique(stage["words"], [word])
        _append_unique(stage["case_names"], case_names)
        for raw_category in group.get("categories") or []:
            name = str((raw_category or {}).get("name") or "")
            if not name:
                continue
            category_counts[name] = category_counts.get(name, 0) + int((raw_category or {}).get("count") or 0)
        for raw_tag in group.get("tags") or []:
            name = str((raw_tag or {}).get("name") or "")
            if not name:
                continue
            tag_counts[name] = tag_counts.get(name, 0) + int((raw_tag or {}).get("count") or 0)
        for case_name in case_names:
            current = by_case_name.get(case_name)
            if current is None:
                current = {
                    "name": case_name,
                    "words": [],
                    "distances": [],
                }
                by_case_name[case_name] = current
                name_rows.append(current)
            _append_unique(current["words"], [word])
            if distance not in current["distances"]:
                current["distances"].append(distance)
    distance_rows: list[dict[str, Any]] = []
    for distance in sorted(ordered_distances):
        stage = by_distance[distance]
        distance_rows.append(
            {
                "distance": distance,
                "words": list(stage["words"]),
                "word_count": len(stage["words"]),
                "case_count": len(stage["case_names"]),
                **_preview(select_stdlib_impact_groups(group_list, distances=[distance])),
                **portability_filter_metadata("--impact-distance", str(distance)),
                **impact_filter_transition_metadata(
                    "--impact-distance",
                    current_family_argv=stdlib_impact_filter_args(impact_distances=current_distances),
                    effective_family_argv=stdlib_impact_filter_args(impact_distances=[distance]),
                    family_mode="replace",
                ),
                **stdlib_manifest_show_impact_metadata(
                    selected_words=selection_words,
                    impact_filter_words=current_filter_words,
                    impact_word_contains=impact_word_contains,
                    impact_distances=[distance],
                    impact_case_categories=current_categories,
                    impact_case_tags=current_tags,
                    impact_case_names=current_names,
                    impact_case_name_contains=impact_case_name_contains,
                ),
            }
        )
    for row in name_rows:
        row["word_count"] = len(row["words"])
        row["distance_count"] = len(row["distances"])
        row.update(_preview_by_name(row["name"]))
        row.update(portability_filter_metadata("--impact-name", row["name"]))
        row.update(
            impact_filter_transition_metadata(
                "--impact-name",
                current_family_argv=stdlib_impact_filter_args(impact_case_names=current_names),
                effective_family_argv=stdlib_impact_filter_args(impact_case_names=[row["name"]]),
                family_mode="replace",
            )
        )
        row.update(
            stdlib_manifest_show_impact_metadata(
                selected_words=selection_words,
                impact_filter_words=current_filter_words,
                impact_word_contains=impact_word_contains,
                impact_distances=current_distances,
                impact_case_categories=current_categories,
                impact_case_tags=current_tags,
                impact_case_names=[row["name"]],
                impact_case_name_contains=impact_case_name_contains,
            )
        )
    category_rows = []
    for name, count in sorted(category_counts.items()):
        filtered = refilter_stdlib_impact_groups(group_list, cases=cases, case_categories=[name]) if cases is not None else []
        category_rows.append(
            {
                "name": name,
                "count": count,
                **_preview(filtered),
                **portability_filter_metadata("--impact-category", name),
                **impact_filter_transition_metadata(
                    "--impact-category",
                    current_family_argv=stdlib_impact_filter_args(impact_case_categories=current_categories),
                    effective_family_argv=stdlib_impact_filter_args(impact_case_categories=[name]),
                    family_mode="replace",
                ),
                **stdlib_manifest_show_impact_metadata(
                    selected_words=selection_words,
                    impact_filter_words=current_filter_words,
                    impact_word_contains=impact_word_contains,
                    impact_distances=current_distances,
                    impact_case_categories=[name],
                    impact_case_tags=current_tags,
                    impact_case_names=current_names,
                    impact_case_name_contains=impact_case_name_contains,
                ),
            }
        )
    tag_rows = []
    for name, count in sorted(tag_counts.items()):
        next_tags = list(current_tags)
        _append_unique(next_tags, [name])
        filtered = refilter_stdlib_impact_groups(group_list, cases=cases, case_tags=[name]) if cases is not None else []
        tag_rows.append(
            {
                "name": name,
                "count": count,
                **_preview(filtered),
                **portability_filter_metadata("--impact-tag", name),
                **impact_filter_transition_metadata(
                    "--impact-tag",
                    current_family_argv=stdlib_impact_filter_args(impact_case_tags=current_tags),
                    effective_family_argv=stdlib_impact_filter_args(impact_case_tags=next_tags),
                    family_mode="append",
                ),
                **stdlib_manifest_show_impact_metadata(
                    selected_words=selection_words,
                    impact_filter_words=current_filter_words,
                    impact_word_contains=impact_word_contains,
                    impact_distances=current_distances,
                    impact_case_categories=current_categories,
                    impact_case_tags=next_tags,
                    impact_case_names=current_names,
                    impact_case_name_contains=impact_case_name_contains,
                ),
            }
        )
    options = {
        "words": word_rows,
        "word_count": len(word_rows),
        "distances": distance_rows,
        "distance_count": len(distance_rows),
        "categories": category_rows,
        "category_count": len(category_rows),
        "tags": tag_rows,
        "tag_count": len(tag_rows),
        "names": name_rows,
        "name_count": len(name_rows),
    }
    annotate_stdlib_impact_filter_option_equivalences(options)
    options["recommended"] = stdlib_recommended_impact_filter_options(options)
    options["recommended_count"] = len(options["recommended"])
    options["recommended_distinct"] = stdlib_distinct_impact_filter_options(options["recommended"])
    options["recommended_distinct_count"] = len(options["recommended_distinct"])
    options["recommended_distinct_groups"] = stdlib_distinct_impact_filter_groups(options["recommended"])
    options["recommended_distinct_group_count"] = len(options["recommended_distinct_groups"])
    options["recommended_primary"] = stdlib_primary_impact_filter_option(options)
    options["recommended_primary_group"] = stdlib_primary_impact_filter_group(options)
    primary = dict(options["recommended_primary"] or {})
    options["recommended_primary_command"] = str(primary.get("show_impact_command") or "")
    options["recommended_primary_json_command"] = str(primary.get("show_impact_json_command") or "")
    return options


def stdlib_impact_slice(
    groups: Iterable[dict[str, Any]],
    *,
    cases: Iterable[dict[str, Any]] | None = None,
    selected_words: Iterable[str] | None = None,
    impact_filter_words: Iterable[str] | None = None,
    impact_word_contains: str | None = None,
    impact_distances: Iterable[int] | None = None,
    impact_case_categories: Iterable[str] | None = None,
    impact_case_tags: Iterable[str] | None = None,
    impact_case_names: Iterable[str] | None = None,
    impact_case_name_contains: str | None = None,
) -> dict[str, Any]:
    group_list = list(groups)
    slice_selected_words: list[str] = []
    _append_unique(slice_selected_words, selected_words or [])
    impact_words: list[str] = []
    impact_case_names_list: list[str] = []
    for group in group_list:
        _append_unique(slice_selected_words, group.get("selected_words") or [])
        _append_unique(impact_words, [str(group.get("word") or "")])
        _append_unique(impact_case_names_list, group.get("case_names") or [])
    impact_stages = stdlib_impact_stages(group_list, cases=cases)
    out = {
        "selected_words": slice_selected_words,
        "selected_word_count": len(slice_selected_words),
        "impact_words": impact_words,
        "impact_word_count": len(impact_words),
        "impact_case_names": impact_case_names_list,
        "impact_case_count": len(impact_case_names_list),
        "impact_groups": group_list,
        "impact_stages": impact_stages,
        "impact_stage_count": len(impact_stages),
        "impact_filter_options": stdlib_impact_filter_options(
            group_list,
            cases=cases,
            selected_words=slice_selected_words,
            impact_filter_words=impact_filter_words,
            impact_word_contains=impact_word_contains,
            impact_distances=impact_distances,
            impact_case_categories=impact_case_categories,
            impact_case_tags=impact_case_tags,
            impact_case_names=impact_case_names,
            impact_case_name_contains=impact_case_name_contains,
        ),
    }
    out.update(portability_retest_metadata(impact_case_names_list))
    out.update(
        stdlib_manifest_show_impact_metadata(
            selected_words=slice_selected_words,
            impact_filter_words=impact_filter_words,
            impact_word_contains=impact_word_contains,
            impact_distances=impact_distances,
            impact_case_categories=impact_case_categories,
            impact_case_tags=impact_case_tags,
            impact_case_names=impact_case_names,
            impact_case_name_contains=impact_case_name_contains,
        )
    )
    if cases is not None:
        out.update(impact_inventory_fields(cases, impact_case_names_list))
    return out


def stdlib_impact_summary(
    rows: Iterable[dict[str, Any]],
    *,
    cases: Iterable[dict[str, Any]] | None = None,
    impact_filter_words: Iterable[str] | None = None,
    impact_word_contains: str | None = None,
    impact_distances: Iterable[int] | None = None,
    impact_case_categories: Iterable[str] | None = None,
    impact_case_tags: Iterable[str] | None = None,
    impact_case_names: Iterable[str] | None = None,
    impact_case_name_contains: str | None = None,
) -> dict[str, Any]:
    row_list = list(rows)
    selected_words: list[str] = []
    for row in row_list:
        _append_unique(selected_words, [str(row.get("word") or "")])
    impact_groups = merge_stdlib_impact_groups(row_list)
    return stdlib_impact_slice(
        impact_groups,
        cases=cases,
        selected_words=selected_words,
        impact_filter_words=impact_filter_words,
        impact_word_contains=impact_word_contains,
        impact_distances=impact_distances,
        impact_case_categories=impact_case_categories,
        impact_case_tags=impact_case_tags,
        impact_case_names=impact_case_names,
        impact_case_name_contains=impact_case_name_contains,
    )


def _boot_stdlib_transitive_dependencies(
    specs: dict[str, dict[str, Any]],
    word: str,
    *,
    _cache: dict[str, dict[str, Any]] | None = None,
    _visiting: set[str] | None = None,
) -> dict[str, Any]:
    cache = _cache if _cache is not None else {}
    if word in cache:
        return cache[word]
    visiting = _visiting if _visiting is not None else set()
    if word in visiting:
        return {
            "transitive_stdlib_refs": [],
            "transitive_nonstdlib_refs": [],
            "dependency_order": [],
            "stdlib_depth": 0,
        }
    visiting.add(word)
    spec = specs.get(word) or {}
    transitive_stdlib_refs: list[str] = []
    transitive_nonstdlib_refs: list[str] = []
    dependency_order: list[str] = []
    stdlib_depth = 0
    _append_unique(transitive_nonstdlib_refs, spec.get("nonstdlib_refs") or [])
    for ref in spec.get("stdlib_refs") or []:
        child = _boot_stdlib_transitive_dependencies(specs, str(ref), _cache=cache, _visiting=visiting)
        _append_unique(transitive_stdlib_refs, child.get("transitive_stdlib_refs") or [])
        _append_unique(transitive_stdlib_refs, [ref])
        _append_unique(transitive_nonstdlib_refs, child.get("transitive_nonstdlib_refs") or [])
        _append_unique(dependency_order, child.get("dependency_order") or [])
        _append_unique(dependency_order, [ref])
        stdlib_depth = max(stdlib_depth, 1 + int(child.get("stdlib_depth") or 0))
    visiting.remove(word)
    out = {
        "transitive_stdlib_refs": transitive_stdlib_refs,
        "transitive_nonstdlib_refs": transitive_nonstdlib_refs,
        "dependency_order": dependency_order,
        "stdlib_depth": stdlib_depth,
    }
    cache[word] = out
    return out



def _boot_stdlib_reverse_dependencies(specs: dict[str, dict[str, Any]]) -> None:
    direct_users: dict[str, list[str]] = {word: [] for word in specs}
    transitive_users: dict[str, list[str]] = {word: [] for word in specs}
    for user_word, spec in specs.items():
        for ref in spec.get("stdlib_refs") or []:
            ref_s = str(ref)
            if ref_s in direct_users:
                _append_unique(direct_users[ref_s], [user_word])
        for ref in spec.get("transitive_stdlib_refs") or []:
            ref_s = str(ref)
            if ref_s in transitive_users:
                _append_unique(transitive_users[ref_s], [user_word])

    depth_cache: dict[str, int] = {}
    impact_cache: dict[str, list[str]] = {}

    def user_depth(word: str, visiting: set[str] | None = None) -> int:
        if word in depth_cache:
            return depth_cache[word]
        active = visiting if visiting is not None else set()
        if word in active:
            return 0
        active.add(word)
        depth = 0
        for user in direct_users.get(word) or []:
            depth = max(depth, 1 + user_depth(str(user), active))
        active.remove(word)
        depth_cache[word] = depth
        return depth

    def impact_words(word: str, visiting: set[str] | None = None) -> list[str]:
        if word in impact_cache:
            return list(impact_cache[word])
        active = visiting if visiting is not None else set()
        if word in active:
            return [word]
        active.add(word)
        impacted = [word]
        for user in direct_users.get(word) or []:
            _append_unique(impacted, impact_words(str(user), active))
        active.remove(word)
        impact_cache[word] = list(impacted)
        return list(impacted)

    for word, spec in specs.items():
        spec["direct_stdlib_users"] = list(direct_users.get(word) or [])
        spec["transitive_stdlib_users"] = list(transitive_users.get(word) or [])
        spec["user_depth"] = user_depth(word)
        spec["impact_words"] = impact_words(word)
        spec["impact_word_count"] = len(spec["impact_words"])


def boot_stdlib_word_specs(path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    p = Path(path) if path is not None else boot_stdlib_source_path()
    lines = p.read_text(encoding="utf-8").splitlines()
    specs: dict[str, dict[str, Any]] = {}
    pattern = re.compile(
        r'^:\s+([^\s]+)\s*(\([^)]*\))?\s*(.*?)\s*;\s*(?:\\.*)?$',
        flags=re.DOTALL,
    )
    start_line = 0
    block: list[str] = []
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not block:
            if not stripped.startswith(":"):
                continue
            start_line = idx
            block = [stripped]
        else:
            block.append(stripped)
        code_part = stripped.split("\\", 1)[0].rstrip()
        if ";" not in code_part:
            continue
        joined = " ".join(
            part.split("\\", 1)[0].rstrip()
            for part in block
            if part.split("\\", 1)[0].rstrip()
        )
        match = pattern.match(joined)
        if match:
            word = match.group(1)
            stack_effect = (match.group(2) or "").strip()
            body = re.sub(r"\s+", " ", (match.group(3) or "").strip())
            specs[word] = {
                "word": word,
                "line": start_line,
                "stack_effect": stack_effect,
                "definition": body,
                "source_path": str(p),
            }
        block = []
        start_line = 0
    known_words = set(specs)
    closure_cache: dict[str, dict[str, Any]] = {}
    for word, spec in specs.items():
        spec.update(_classify_stdlib_definition(str(spec.get("definition") or ""), known_words - {word}))
    for word, spec in specs.items():
        spec.update(_boot_stdlib_transitive_dependencies(specs, word, _cache=closure_cache))
    _boot_stdlib_reverse_dependencies(specs)
    return specs


def selected_boot_stdlib_word_inventory(
    *,
    manifest: dict[str, list[str]] | None = None,
    impact_manifest: dict[str, list[str]] | None = None,
    specs: dict[str, dict[str, Any]] | None = None,
    cases: Iterable[dict[str, Any]] | None = None,
    words: Iterable[str] | None = None,
    word_contains: str | None = None,
    impact_filter_words: Iterable[str] | None = None,
    impact_word_contains: str | None = None,
    impact_distances: Iterable[int] | None = None,
    impact_case_categories: Iterable[str] | None = None,
    impact_case_tags: Iterable[str] | None = None,
    impact_case_names: Iterable[str] | None = None,
    impact_case_name_contains: str | None = None,
) -> dict[str, Any]:
    manifest_entries = select_boot_stdlib_manifest_entries(
        manifest or BOOT_STDLIB_PORTABILITY_MANIFEST,
        words=words,
        word_contains=word_contains,
    )
    all_manifest_entries = impact_manifest or BOOT_STDLIB_PORTABILITY_MANIFEST
    spec_map = specs or boot_stdlib_word_specs()
    rows: list[dict[str, Any]] = []
    missing_words: list[str] = []
    for word in manifest_entries:
        spec = spec_map.get(word)
        if not spec:
            missing_words.append(word)
            continue
        all_impact_words = [str(tok) for tok in spec.get("impact_words") or [word]]
        impact_groups = stdlib_impact_groups(
            word,
            all_impact_words,
            manifest=all_manifest_entries,
            specs=spec_map,
            cases=cases,
        )
        impact_groups = select_stdlib_impact_groups(
            impact_groups,
            words=impact_filter_words,
            word_contains=impact_word_contains,
            distances=impact_distances,
        )
        impact_groups = refilter_stdlib_impact_groups(
            impact_groups,
            cases=cases,
            case_categories=impact_case_categories,
            case_tags=impact_case_tags,
            case_names=impact_case_names,
            case_name_contains=impact_case_name_contains,
        )
        row = {
            "word": word,
            "line": int(spec["line"]),
            "stack_effect": str(spec.get("stack_effect") or ""),
            "definition": str(spec.get("definition") or ""),
            "source_path": str(spec.get("source_path") or ""),
            "body_tokens": [str(tok) for tok in spec.get("body_tokens") or []],
            "syntax_tokens": [str(tok) for tok in spec.get("syntax_tokens") or []],
            "literal_tokens": [str(tok) for tok in spec.get("literal_tokens") or []],
            "word_refs": [str(tok) for tok in spec.get("word_refs") or []],
            "stdlib_refs": [str(tok) for tok in spec.get("stdlib_refs") or []],
            "nonstdlib_refs": [str(tok) for tok in spec.get("nonstdlib_refs") or []],
            "alias_of": str(spec.get("alias_of") or ""),
            "transitive_stdlib_refs": [str(tok) for tok in spec.get("transitive_stdlib_refs") or []],
            "transitive_nonstdlib_refs": [str(tok) for tok in spec.get("transitive_nonstdlib_refs") or []],
            "dependency_order": [str(tok) for tok in spec.get("dependency_order") or []],
            "stdlib_depth": int(spec.get("stdlib_depth") or 0),
            "direct_stdlib_users": [str(tok) for tok in spec.get("direct_stdlib_users") or []],
            "transitive_stdlib_users": [str(tok) for tok in spec.get("transitive_stdlib_users") or []],
            "user_depth": int(spec.get("user_depth") or 0),
        }
        row.update(
            stdlib_impact_slice(
                impact_groups,
                cases=cases,
                selected_words=[word],
                impact_filter_words=impact_filter_words,
                impact_word_contains=impact_word_contains,
                impact_distances=impact_distances,
                impact_case_categories=impact_case_categories,
                impact_case_tags=impact_case_tags,
                impact_case_names=impact_case_names,
                impact_case_name_contains=impact_case_name_contains,
            )
        )
        rows.append(row)
    return {
        "word_count": len(manifest_entries),
        "all_words_present": not missing_words,
        "missing_words": missing_words,
        "words": rows,
        "impact_summary": stdlib_impact_summary(
            rows,
            cases=cases,
            impact_filter_words=impact_filter_words,
            impact_word_contains=impact_word_contains,
            impact_distances=impact_distances,
            impact_case_categories=impact_case_categories,
            impact_case_tags=impact_case_tags,
            impact_case_names=impact_case_names,
            impact_case_name_contains=impact_case_name_contains,
        ),
    }


def select_boot_stdlib_manifest_entries(
    manifest: dict[str, list[str]] | None = None,
    *,
    words: Iterable[str] | None = None,
    word_contains: str | None = None,
) -> dict[str, list[str]]:
    entries = manifest or BOOT_STDLIB_PORTABILITY_MANIFEST
    out: dict[str, list[str]] = {}
    wanted = {str(word).strip() for word in (words or []) if str(word).strip()}
    needle = str(word_contains or "").strip().lower()
    for word, case_names in entries.items():
        if wanted and word not in wanted:
            continue
        if needle and needle not in word.lower():
            continue
        out[word] = list(case_names)
    return out


def boot_stdlib_manifest_inventory(
    cases: Iterable[dict[str, Any]],
    manifest: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    entries = manifest or BOOT_STDLIB_PORTABILITY_MANIFEST
    case_names = {str(case.get("name") or "") for case in cases}
    rows: list[dict[str, Any]] = []
    missing_words: list[str] = []
    all_manifest_case_names: set[str] = set()
    for word, names in entries.items():
        missing_case_names = [name for name in names if name not in case_names]
        if missing_case_names:
            missing_words.append(word)
        all_manifest_case_names.update(names)
        rows.append(
            {
                "word": word,
                "case_names": list(names),
                "covered": not missing_case_names,
                "missing_case_names": missing_case_names,
            }
        )
    return {
        "word_count": len(rows),
        "all_cases_present": not missing_words,
        "missing_words": missing_words,
        "manifest_case_count": len(all_manifest_case_names),
        "words": rows,
    }


@dataclass(frozen=True)
class PortabilityCaseResult:
    name: str
    ok: bool
    detail: str = ""


def portability_case_record(case: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "name": str(case.get("name") or ""),
        "category": str(case.get("category") or ""),
        "source": str(case.get("source") or ""),
    }
    tags = list(case.get("tags") or [])
    if tags:
        out["tags"] = [str(tag) for tag in tags]
    host_features = list(case.get("host_features") or [])
    if host_features:
        out["host_features"] = [str(feat) for feat in host_features]
    if "expect_stack" in case:
        out["expect_stack"] = _normalize_value(case.get("expect_stack"))
    if "expect_error_contains" in case:
        out["expect_error_contains"] = str(case.get("expect_error_contains") or "")
    return out


def portability_result_record(case: dict[str, Any], result: PortabilityCaseResult) -> dict[str, Any]:
    out = portability_case_record(case)
    out.update(asdict(result))
    return out


def portability_summary(cases: Iterable[dict[str, Any]]) -> dict[str, Any]:
    items = list(cases)
    by_category: dict[str, int] = {}
    by_tag: dict[str, int] = {}
    for case in items:
        cat = str(case.get("category") or "")
        if cat:
            by_category[cat] = by_category.get(cat, 0) + 1
        for tag in case.get("tags") or []:
            tag_s = str(tag)
            if tag_s:
                by_tag[tag_s] = by_tag.get(tag_s, 0) + 1
    return {
        "count": len(items),
        "by_category": dict(sorted(by_category.items())),
        "by_tag": dict(sorted(by_tag.items())),
    }


def portability_inventory(cases: Iterable[dict[str, Any]]) -> dict[str, Any]:
    items = list(cases)
    summary = portability_summary(items)
    return {
        "count": summary["count"],
        "categories": [
            {"name": name, "count": count} for name, count in summary["by_category"].items()
        ],
        "tags": [
            {"name": name, "count": count} for name, count in summary["by_tag"].items()
        ],
        "case_names": [str(case.get("name") or "") for case in items],
    }


def default_corpus_path() -> Path:
    return Path(__file__).resolve().parents[2] / "portability" / "kernel_cases.json"


def _normalize_string_list(raw: Any, *, case_idx: int, field: str) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValueError(f"portability case {case_idx} {field} must be a list")
    out: list[str] = []
    seen: set[str] = set()
    for item in raw:
        val = str(item).strip()
        if not val:
            raise ValueError(f"portability case {case_idx} {field} must be non-empty strings")
        if val in seen:
            continue
        out.append(val)
        seen.add(val)
    return out


def _normalize_tags(raw: Any, *, case_idx: int) -> list[str]:
    return _normalize_string_list(raw, case_idx=case_idx, field="tags")


def _validate_portability_case(raw: dict[str, Any], *, case_idx: int, seen_names: set[str]) -> dict[str, Any]:
    name = str(raw.get("name") or f"case-{case_idx+1}").strip()
    source = str(raw.get("source") or "")
    category = str(raw.get("category") or "").strip()
    tags = _normalize_tags(raw.get("tags"), case_idx=case_idx)
    host_features = _normalize_string_list(raw.get("host_features"), case_idx=case_idx, field="host_features")
    has_stack = "expect_stack" in raw
    has_error = "expect_error_contains" in raw

    if not name or not source or not category:
        raise ValueError(f"portability case {case_idx} must include name + category + source")
    if name in seen_names:
        raise ValueError(f"duplicate portability case name: {name}")
    if not has_stack and not has_error:
        raise ValueError(
            f"portability case {name!r} must include expect_stack and/or expect_error_contains"
        )

    case = dict(raw, name=name, category=category, source=source)
    if has_stack:
        _normalize_value(case.get("expect_stack"))
    else:
        want = str(case.get("expect_error_contains") or "")
        if not want:
            raise ValueError(f"portability case {name!r} expect_error_contains must be a non-empty string")
        case["expect_error_contains"] = want
    if tags:
        case["tags"] = tags
    elif "tags" in case:
        del case["tags"]
    if host_features:
        case["host_features"] = host_features
    elif "host_features" in case:
        del case["host_features"]
    seen_names.add(name)
    return case


def load_portability_cases(path: str | Path | None = None) -> list[dict[str, Any]]:
    p = Path(path) if path is not None else default_corpus_path()
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"portability corpus must be a list: {p}")
    out: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    for idx, raw in enumerate(data):
        if not isinstance(raw, dict):
            raise ValueError(f"portability case {idx} must be an object")
        out.append(_validate_portability_case(raw, case_idx=idx, seen_names=seen_names))
    return out


def select_portability_cases(
    cases: Iterable[dict[str, Any]],
    *,
    categories: Iterable[str] | None = None,
    tags: Iterable[str] | None = None,
    names: Iterable[str] | None = None,
    name_contains: str | None = None,
) -> list[dict[str, Any]]:
    selected = list(cases)
    if categories is not None:
        wanted = {str(cat).strip() for cat in categories if str(cat).strip()}
        if wanted:
            selected = [c for c in selected if str(c.get("category") or "") in wanted]
    if tags is not None:
        wanted_tags = {str(tag).strip() for tag in tags if str(tag).strip()}
        if wanted_tags:
            selected = [
                c for c in selected if wanted_tags <= set(str(t) for t in (c.get("tags") or []))
            ]
    if names is not None:
        wanted_names = {str(name).strip() for name in names if str(name).strip()}
        if wanted_names:
            selected = [c for c in selected if str(c.get("name") or "") in wanted_names]
    if name_contains:
        needle = str(name_contains).strip().lower()
        if needle:
            selected = [c for c in selected if needle in str(c.get("name") or "").lower()]
    return selected


def _normalize_value(value: Any) -> Any:
    if isinstance(value, (int, str)) or value is None:
        return value
    if isinstance(value, list):
        return [_normalize_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _normalize_value(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    raise TypeError(f"non-portable value in result stack: {type(value).__name__}")


def run_portability_case(case: dict[str, Any]) -> PortabilityCaseResult:
    name = str(case.get("name") or "<unnamed>")
    source = str(case.get("source") or "")
    filename = str(case.get("filename") or f"portability:{name}")
    expect_stack = case.get("expect_stack")
    expect_error = case.get("expect_error_contains")

    vm = VM()
    for feat in case.get("host_features") or []:
        vm.host_features.add(str(feat))
    try:
        vm.eval(source, filename=filename)
    except MicromaxError as exc:
        if expect_error is None:
            return PortabilityCaseResult(name=name, ok=False, detail=f"unexpected error: {exc}")
        want = str(expect_error)
        got = str(exc)
        if want and want not in got:
            return PortabilityCaseResult(
                name=name,
                ok=False,
                detail=f"error mismatch: wanted substring {want!r}, got {got!r}",
            )
        if expect_stack is not None:
            got_stack = _normalize_value(list(vm.stack))
            want_stack = _normalize_value(list(expect_stack or []))
            if got_stack != want_stack:
                return PortabilityCaseResult(
                    name=name,
                    ok=False,
                    detail=f"error-stack mismatch: wanted {want_stack!r}, got {got_stack!r}",
                )
        return PortabilityCaseResult(name=name, ok=True)

    if expect_error is not None:
        return PortabilityCaseResult(name=name, ok=False, detail="expected error, got success")

    got_stack = _normalize_value(list(vm.stack))
    want_stack = _normalize_value(list(expect_stack or []))
    if got_stack != want_stack:
        return PortabilityCaseResult(
            name=name,
            ok=False,
            detail=f"stack mismatch: wanted {want_stack!r}, got {got_stack!r}",
        )
    return PortabilityCaseResult(name=name, ok=True)


def run_portability_cases(cases: list[dict[str, Any]] | None = None) -> list[PortabilityCaseResult]:
    corpus = list(cases) if cases is not None else load_portability_cases()
    return [run_portability_case(case) for case in corpus]
