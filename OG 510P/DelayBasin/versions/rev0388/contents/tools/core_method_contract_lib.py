import pathlib
import re
from collections import Counter
from typing import Any

WORD_RE = re.compile(r"[A-Za-z0-9_]+(?:[-'][A-Za-z0-9_]+)*")
EXPECTED_CORE_METHOD_CONTRACTS = 20
ALLOWED_ROW_KEYS = {"source_checker", "doc_path", "doc_needles", "surface_needles"}
MIN_SOURCE_DOC_WORDS = 600
MAX_DOC_NEEDLES = 16
MAX_SURFACE_NEEDLE_GROUPS = 8
MAX_NEEDLE_CHAR_FRACTION = 0.20


class CoreMethodContractError(Exception):
    pass


def _fail(message: str) -> None:
    raise CoreMethodContractError(message)


def _display_path(root: pathlib.Path, path: pathlib.Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def _require_text(root: pathlib.Path, rel: str, source: str, text_overrides: dict[str, str] | None = None) -> str:
    if text_overrides and rel in text_overrides:
        return text_overrides[rel]
    path = root / rel
    if not path.exists():
        _fail(f"{source}: missing surface {_display_path(root, path)}")
    return path.read_text(encoding="utf-8")


def _wrapper_exists(root: pathlib.Path, source: str, wrapper_exists_overrides: dict[str, bool] | None = None) -> bool:
    if wrapper_exists_overrides and source in wrapper_exists_overrides:
        return wrapper_exists_overrides[source]
    return (root / "tools" / source).exists()


def _check_all_needles(segment: str, source: str, label: str, text: str, needles: list[str]) -> None:
    missing = [needle for needle in needles if needle not in text]
    if missing:
        _fail(f"{source} [{segment}] missing {label}: " + ", ".join(missing))


def _check_surface_needles(segment: str, source: str, rel: str, text: str, specs: list[Any]) -> None:
    if len(specs) > MAX_SURFACE_NEEDLE_GROUPS:
        _fail(f"{source} [{segment}] has too many surface needle groups for {rel}")
    for idx, spec in enumerate(specs, start=1):
        label = f"{rel} needle group {idx}"
        if isinstance(spec, str):
            _check_all_needles(segment, source, label, text, [spec])
            continue
        if not isinstance(spec, dict) or set(spec) not in ({"all"}, {"any"}):
            _fail(f"{source} [{segment}] has invalid surface needle spec for {rel}: {spec!r}")
        key, values = next(iter(spec.items()))
        if not isinstance(values, list) or not values or not all(isinstance(value, str) and value for value in values):
            _fail(f"{source} [{segment}] has invalid {key} needles for {rel}")
        if key == "all":
            _check_all_needles(segment, source, label, text, values)
        elif not any(value in text for value in values):
            _fail(f"{source} [{segment}] missing any of {label}: " + ", ".join(values))


def validate_core_method_contracts(
    root: pathlib.Path,
    rows: list[tuple[str, dict[str, Any]]],
    *,
    text_overrides: dict[str, str] | None = None,
    wrapper_exists_overrides: dict[str, bool] | None = None,
) -> str:
    if len(rows) != EXPECTED_CORE_METHOD_CONTRACTS:
        _fail(f"core method batch expected {EXPECTED_CORE_METHOD_CONTRACTS} contracts, found {len(rows)}")

    seen_sources: set[str] = set()
    by_segment = Counter(segment for segment, _row in rows)
    for segment, row in rows:
        if set(row) != ALLOWED_ROW_KEYS:
            _fail(f"core method spec has unsupported keys in {segment}: {sorted(row)}")
        source = row.get("source_checker")
        doc_path = row.get("doc_path")
        doc_needles = row.get("doc_needles")
        surface_needles = row.get("surface_needles")
        if not isinstance(source, str) or not source.startswith("check_") or not source.endswith("_contract.py"):
            _fail(f"core method spec has invalid source checker in {segment}: {source!r}")
        if source in seen_sources:
            _fail(f"core method spec duplicates source checker: {source}")
        seen_sources.add(source)
        if _wrapper_exists(root, source, wrapper_exists_overrides):
            _fail(f"former core method wrapper still exists: tools/{source}")
        if not isinstance(doc_path, str) or not doc_path.startswith("docs/10-method/"):
            _fail(f"{source} [{segment}] has invalid doc_path: {doc_path!r}")
        if not isinstance(doc_needles, list) or not 4 <= len(doc_needles) <= MAX_DOC_NEEDLES or not all(isinstance(item, str) and item for item in doc_needles):
            _fail(f"{source} [{segment}] has invalid doc needles")
        if not isinstance(surface_needles, dict):
            _fail(f"{source} [{segment}] has invalid surface_needles")

        doc_text = _require_text(root, doc_path, source, text_overrides)
        if _word_count(doc_text) < MIN_SOURCE_DOC_WORDS:
            _fail(f"{source} [{segment}] source document is too small to remain the semantic source")
        if sum(len(needle) for needle in doc_needles) > len(doc_text) * MAX_NEEDLE_CHAR_FRACTION:
            _fail(f"{source} [{segment}] doc needles are too large; spec is drifting toward semantic substitution")
        _check_all_needles(segment, source, "doc needles", doc_text, doc_needles)

        for rel, specs in surface_needles.items():
            if not isinstance(rel, str) or not rel.startswith(("docs/", "REVISION-", "SURFACE-", "FOLLOWTHROUGH-", "ASSUMPTION-", "OBLIGATION-")):
                _fail(f"{source} [{segment}] has invalid auxiliary surface path: {rel!r}")
            if not isinstance(specs, list):
                _fail(f"{source} [{segment}] surface_needles for {rel} must be a list")
            surface_text = _require_text(root, rel, source, text_overrides)
            _check_surface_needles(segment, source, rel, surface_text, specs)

    return (
        "check_core_method_batch_contract: OK "
        f"({len(rows)} contracts across {len(by_segment)} segments; source docs remain semantic surfaces)"
    )


def _first_surface_needle(row: dict[str, Any]) -> tuple[str, str]:
    for rel, specs in row.get("surface_needles", {}).items():
        if not specs:
            continue
        first = specs[0]
        if isinstance(first, str):
            return rel, first
        if isinstance(first, dict):
            values = first.get("all") or first.get("any") or []
            if values:
                return rel, values[0]
    raise CoreMethodContractError("no surface needle available for negative canary")


def core_method_negative_canary_results(root: pathlib.Path, rows: list[tuple[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    if not rows:
        raise CoreMethodContractError("no core-method specs available for negative canaries")
    segment, row = rows[0]
    source = row["source_checker"]
    doc_path = row["doc_path"]
    doc_text = (root / doc_path).read_text(encoding="utf-8")
    doc_needle = row["doc_needles"][0]
    aux_rel, aux_needle = _first_surface_needle(row)
    aux_text = (root / aux_rel).read_text(encoding="utf-8")

    scenarios = [
        {
            "id": "doc-needle-removal",
            "expected_failure_contains": [source, segment, "missing doc needles", doc_needle],
            "kwargs": {"text_overrides": {doc_path: doc_text.replace(doc_needle, "", 1)}},
        },
        {
            "id": "source-doc-shrink",
            "expected_failure_contains": [source, segment, "source document is too small"],
            "kwargs": {"text_overrides": {doc_path: "too small semantic stub " * 20}},
        },
        {
            "id": "auxiliary-surface-needle-removal",
            "expected_failure_contains": [source, segment, aux_rel, aux_needle],
            "kwargs": {"text_overrides": {aux_rel: aux_text.replace(aux_needle, "", 1)}},
        },
        {
            "id": "former-wrapper-regrowth",
            "expected_failure_contains": ["former core method wrapper still exists", f"tools/{source}"],
            "kwargs": {"wrapper_exists_overrides": {source: True}},
        },
        {
            "id": "duplicate-source-checker",
            "expected_failure_contains": ["duplicates source checker", source],
            "rows": [rows[0], rows[0], *rows[2:]],
            "kwargs": {},
        },
    ]
    results: list[dict[str, Any]] = []
    for scenario in scenarios:
        scenario_rows = scenario.get("rows", rows)
        kwargs = scenario.get("kwargs", {})
        try:
            validate_core_method_contracts(root, scenario_rows, **kwargs)
        except CoreMethodContractError as exc:
            message = str(exc)
            expected = scenario["expected_failure_contains"]
            passed = all(token in message for token in expected)
            results.append({
                "id": scenario["id"],
                "expected_failure_contains": expected,
                "observed_failure": message,
                "status": "pass" if passed else "fail",
            })
            continue
        results.append({
            "id": scenario["id"],
            "expected_failure_contains": scenario["expected_failure_contains"],
            "observed_failure": None,
            "status": "fail",
        })
    return results
