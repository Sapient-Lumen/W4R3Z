from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from . import VM, MicromaxError


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
    if has_stack == has_error:
        raise ValueError(
            f"portability case {name!r} must include exactly one of expect_stack or expect_error_contains"
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
