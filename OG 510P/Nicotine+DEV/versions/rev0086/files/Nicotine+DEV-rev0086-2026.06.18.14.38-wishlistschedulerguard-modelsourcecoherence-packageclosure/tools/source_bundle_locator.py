#!/usr/bin/env python3
"""Content-addressed source-bundle discovery for current cube workflows.

The machine-readable source contract is the sole authority for bundle digest,
archive members, lane heads, and observed public refs. A renamed upload remains
usable without editing current tools. Compatibility constants are exported for
historical probes that import this module.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import sha256_path  # noqa: E402

SOURCE_CONTRACT_PATH = Path("data/current_source_contract.json")
FALLBACK_PATTERNS = ("Nicotine-source*.zip", "*upstream*source*.zip")


class SourceBundleError(RuntimeError):
    """Raised when no content-valid source bundle can be selected."""


def load_source_contract(root: Path | None = None) -> dict[str, Any]:
    contract_root = ROOT if root is None else root.resolve()
    path = contract_root / SOURCE_CONTRACT_PATH
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SourceBundleError(f"cannot read source contract {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SourceBundleError(f"source contract is not an object: {path}")
    return value


def bundle_contract(contract: dict[str, Any] | None = None) -> dict[str, Any]:
    value = load_source_contract() if contract is None else contract
    bundle = value.get("source_bundle")
    if not isinstance(bundle, dict):
        raise SourceBundleError("source contract has no source_bundle object")
    return bundle


_SOURCE_CONTRACT = load_source_contract()
_BUNDLE_CONTRACT = bundle_contract(_SOURCE_CONTRACT)
EXPECTED_SOURCE_SHA256 = str(_BUNDLE_CONTRACT.get("sha256", ""))
SOURCE_PREFIX = str(_BUNDLE_CONTRACT.get("source_prefix", ""))
ARCHIVE_PREFIX = str(_BUNDLE_CONTRACT.get("archive_prefix", ""))
GIT_ROOT_SUFFIX = str(_BUNDLE_CONTRACT.get("git_root_suffix", ""))
_patterns = _BUNDLE_CONTRACT.get("default_patterns")
DEFAULT_PATTERNS = tuple(_patterns) if isinstance(_patterns, list) else FALLBACK_PATTERNS
_LANES = _BUNDLE_CONTRACT.get("lanes", {})
REQUIRED_LANES = tuple(sorted(_LANES)) if isinstance(_LANES, dict) else ()
LANE_HEADS = {
    lane: str(details.get("head", ""))
    for lane, details in _LANES.items()
    if isinstance(lane, str) and isinstance(details, dict)
} if isinstance(_LANES, dict) else {}
_DERIVED = _SOURCE_CONTRACT.get("derived_lanes", {})
DERIVED_SOURCE_REFS = {
    lane: str(details.get("head", ""))
    for lane, details in _DERIVED.items()
    if isinstance(lane, str) and isinstance(details, dict)
} if isinstance(_DERIVED, dict) else {}
_PUBLIC = _SOURCE_CONTRACT.get("public_observations", {})
PUBLIC_SOURCE_REFS = {
    lane: str(details.get("head", ""))
    for lane, details in _PUBLIC.items()
    if isinstance(lane, str) and isinstance(details, dict)
} if isinstance(_PUBLIC, dict) else {}


@dataclass(frozen=True)
class BundleInspection:
    path: str
    exists: bool
    sha256: str
    entries: int
    lanes: tuple[str, ...]
    digest_ok: bool
    lanes_ok: bool
    zip_ok: bool
    status: str
    error: str = ""


def archive_member_name(lane: str, *, contract: dict[str, Any] | None = None) -> str:
    bundle = bundle_contract(_SOURCE_CONTRACT if contract is None else contract)
    lanes = bundle.get("lanes", {})
    details = lanes.get(lane) if isinstance(lanes, dict) else None
    archive = details.get("archive") if isinstance(details, dict) else None
    prefix = bundle.get("archive_prefix")
    if not isinstance(prefix, str) or not isinstance(archive, str):
        raise SourceBundleError(f"source contract has no archive for lane {lane}")
    return prefix + archive


def inspect_bundle(path: Path) -> BundleInspection:
    path = path.expanduser().resolve()
    if not path.is_file():
        return BundleInspection(str(path), False, "", 0, (), False, False, False, "fail", "not a file")
    try:
        digest = sha256_path(path)
        lanes: set[str] = set()
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            for name in names:
                if not name.startswith(SOURCE_PREFIX):
                    continue
                rest = name[len(SOURCE_PREFIX):]
                lane = rest.split("/", 1)[0]
                if lane in REQUIRED_LANES:
                    lanes.add(lane)
        lane_tuple = tuple(sorted(lanes))
        digest_ok = digest == EXPECTED_SOURCE_SHA256
        lanes_ok = set(lane_tuple) == set(REQUIRED_LANES)
        status = "pass" if digest_ok and lanes_ok else "fail"
        return BundleInspection(
            str(path), True, digest, len(names), lane_tuple,
            digest_ok, lanes_ok, True, status,
        )
    except (OSError, zipfile.BadZipFile) as exc:
        return BundleInspection(str(path), True, "", 0, (), False, False, False, "fail", str(exc))


def _unique_paths(paths: Iterable[Path]) -> list[Path]:
    seen: set[str] = set()
    output: list[Path] = []
    for path in paths:
        resolved = str(path.expanduser().resolve())
        if resolved in seen:
            continue
        seen.add(resolved)
        output.append(Path(resolved))
    return output


def candidate_paths(
    explicit: str | Path | None = None,
    *,
    search_dirs: Sequence[Path] | None = None,
    env: dict[str, str] | None = None,
) -> list[Path]:
    env = os.environ if env is None else env
    candidates: list[Path] = []
    if explicit and str(explicit).lower() != "auto":
        return _unique_paths([Path(explicit)])
    env_path = env.get("NICOTINE_SOURCE_ZIP", "").strip()
    if env_path:
        candidates.append(Path(env_path))
    dirs = list(search_dirs or (Path("/mnt/data"), Path.cwd(), ROOT))
    for directory in dirs:
        if not directory.is_dir():
            continue
        for pattern in DEFAULT_PATTERNS:
            candidates.extend(sorted(directory.glob(pattern)))
    return _unique_paths(candidates)


def locate_source_bundle(
    explicit: str | Path | None = None,
    *,
    search_dirs: Sequence[Path] | None = None,
    env: dict[str, str] | None = None,
) -> tuple[Path, list[BundleInspection]]:
    paths = candidate_paths(explicit, search_dirs=search_dirs, env=env)
    inspections = [inspect_bundle(path) for path in paths]
    valid = [row for row in inspections if row.status == "pass"]
    if not valid:
        details = "; ".join(f"{row.path}: {row.error or row.status}" for row in inspections) or "no candidates"
        raise SourceBundleError(
            f"no source bundle matches the pinned digest/lane contract ({details})"
        )
    return Path(valid[0].path), inspections


def main() -> int:
    parser = argparse.ArgumentParser(description="locate the Nicotine+ source bundle by content contract")
    parser.add_argument("--source-zip", default="auto", help="explicit path or 'auto'")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()
    try:
        selected, inspections = locate_source_bundle(args.source_zip)
        output = {
            "status": "pass",
            "selected": str(selected),
            "contract": SOURCE_CONTRACT_PATH.as_posix(),
            "expected_sha256": EXPECTED_SOURCE_SHA256,
            "required_lanes": list(REQUIRED_LANES),
            "lane_heads": LANE_HEADS,
            "derived_source_refs": DERIVED_SOURCE_REFS,
            "public_source_refs": PUBLIC_SOURCE_REFS,
            "candidates": [asdict(row) for row in inspections],
        }
        if args.json:
            print(json.dumps(output, indent=2, sort_keys=True))
        else:
            print(selected)
        return 0
    except SourceBundleError as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
