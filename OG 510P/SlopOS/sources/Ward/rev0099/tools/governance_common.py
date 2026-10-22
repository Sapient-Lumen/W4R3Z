#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable
import copy
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
_JSON_CACHE: dict[Path, dict[str, Any]] = {}
_SHA_CACHE: dict[Path, str] = {}
_CHECKER_CACHE: dict[tuple[Path, str], Any] = {}
_SOURCE_VALIDATION_CACHE: dict[tuple[str | None, str, str, str | None], tuple[dict[str, Any], list[str]]] = {}


def load_json(path: Path) -> dict[str, Any]:
    key = path.resolve()
    if key not in _JSON_CACHE:
        _JSON_CACHE[key] = json.loads(path.read_text(encoding="utf-8"))
    return copy.deepcopy(_JSON_CACHE[key])


def sha256_file(path: Path) -> str:
    key = path.resolve()
    if key not in _SHA_CACHE:
        _SHA_CACHE[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    return _SHA_CACHE[key]


def stable_digest(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def parse_time(value: str | None, field: str) -> datetime:
    if not value:
        raise ValueError(f"{field} missing")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} is not ISO-8601 parseable: {value}") from exc


def require(cond: bool, msg: str, errors: list[str]) -> None:
    if not cond:
        errors.append(msg)


def repo_path(rel: str | None, errors: list[str], label: str) -> Path | None:
    if not rel:
        errors.append(f"{label} missing")
        return None
    path = (ROOT / rel).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        errors.append(f"{label} escapes repository root: {rel}")
        return None
    if not path.exists():
        errors.append(f"{label} missing on disk: {rel}")
        return None
    return path


def load_checker(path: Path, module_name: str):
    key = (path.resolve(), module_name)
    if key in _CHECKER_CACHE:
        return _CHECKER_CACHE[key]
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load checker {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _CHECKER_CACHE[key] = module
    return module


def validate_ref(
    ref: dict[str, Any],
    *,
    label: str,
    expected_schema: str,
    checker_script: str | None,
    checker_module_name: str,
    errors: list[str],
) -> dict[str, Any] | None:
    if ref.get("receipt_sha256_checked") is not True:
        errors.append(f"{label}.receipt_sha256_checked must be true")
    path = repo_path(ref.get("receipt_path"), errors, f"{label}.receipt_path")
    if path is None:
        return None
    actual_sha = sha256_file(path)
    if ref.get("receipt_sha256") != actual_sha:
        errors.append(f"{label}.receipt_sha256 mismatch")
    obj = load_json(path)
    if obj.get("schema") != expected_schema:
        errors.append(f"{label} must point at {expected_schema}")
    if ref.get("receipt_id") != obj.get("receipt_id"):
        errors.append(f"{label}.receipt_id does not match referenced receipt")
    if checker_script:
        cache_key = (checker_script, str(path.resolve()), actual_sha, expected_schema)
        cached = _SOURCE_VALIDATION_CACHE.get(cache_key)
        if cached is None:
            checker = load_checker(ROOT / "tools" / checker_script, checker_module_name)
            source_errors = checker.validate_receipt(obj, path)
            _SOURCE_VALIDATION_CACHE[cache_key] = (obj, list(source_errors))
        else:
            _, source_errors = cached
        if source_errors:
            errors.append(f"referenced {label} receipt is invalid: " + "; ".join(source_errors))
    return obj


def run_fixture_checker(
    *,
    fixture_dir: Path,
    valid_glob: str,
    invalid_glob: str,
    validate_receipt: Callable[[dict[str, Any], Path], list[str]],
    label: str,
) -> int:
    valid_paths = sorted(fixture_dir.glob(valid_glob))
    invalid_paths = sorted((fixture_dir / "negative").glob(invalid_glob))
    if not valid_paths:
        print(f"No valid {label} fixtures found.")
        return 1
    if not invalid_paths:
        print(f"No negative {label} fixtures found.")
        return 1
    failures: list[str] = []
    for path in valid_paths:
        errors = validate_receipt(load_json(path), path)
        if errors:
            failures.append(f"{path} should be valid but failed:\n  - " + "\n  - ".join(errors))
    for path in invalid_paths:
        errors = validate_receipt(load_json(path), path)
        if not errors:
            failures.append(f"{path} should be invalid but passed")
    if failures:
        print(f"{label} check failed.")
        for failure in failures:
            print(failure)
        return 1
    print(f"{label} check passed ({len(valid_paths)} valid, {len(invalid_paths)} negative fixtures).")
    return 0


def load_registry() -> dict[str, Any]:
    return load_json(ROOT / "tools" / "governance_checker_registry.json")


def fixture_counts(fixture_dir: Path) -> tuple[int, int]:
    return (len(list(fixture_dir.glob("*.valid.json"))), len(list((fixture_dir / "negative").glob("*.invalid.json"))))


def governance_checker_scripts() -> list[str]:
    return sorted(
        p.name
        for p in (ROOT / "tools").glob("check_governance_*.py")
        if p.name not in {"check_governance_suite.py", "check_governance_registry_integrity.py"}
    )
