import pathlib
import sys
from collections import Counter
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from gpu_witness_contract_specs import (
    GPU_WITNESS_CONTRACT_SPEC_PARTS,
    GPU_WITNESS_CONTRACT_SPEC_SEGMENTS,
    GPU_WITNESS_CONTRACT_SPECS,
    iter_gpu_witness_contract_specs,
)
from gpustorming_standard_contract_specs import (
    GPUSTORMING_STANDARD_CONTRACT_SPEC_PARTS,
    GPUSTORMING_STANDARD_CONTRACT_SPEC_SEGMENTS,
    GPUSTORMING_STANDARD_CONTRACT_SPECS,
    iter_gpustorming_standard_contract_specs,
)
from method_doc_ratchet_contract_specs import (
    METHOD_DOC_RATCHET_CONTRACT_SPEC_PARTS,
    METHOD_DOC_RATCHET_CONTRACT_SPEC_SEGMENTS,
    METHOD_DOC_RATCHET_CONTRACT_SPECS,
    iter_method_doc_ratchet_contract_specs,
)
from core_method_contract_specs import (
    CORE_METHOD_CONTRACT_SPEC_PARTS,
    CORE_METHOD_CONTRACT_SPEC_SEGMENTS,
    CORE_METHOD_CONTRACT_SPECS,
    iter_core_method_contract_specs,
)

MAX_SPEC_PART_BYTES = 100_000
EXPECTED_GPU_CONTRACTS = 54
EXPECTED_STANDARD_GPUSTORMING_CONTRACTS = 40
EXPECTED_METHOD_DOC_RATCHET_CONTRACTS = 18
EXPECTED_CORE_METHOD_CONTRACTS = 20


def _check_part_paths(label: str, part_paths: list[str], *, min_parts: int) -> None:
    if len(part_paths) < min_parts:
        raise SystemExit(f"{label} specs must be split into locality-sized parts")
    seen = set()
    for rel in part_paths:
        if rel in seen:
            raise SystemExit(f"{label} spec part listed twice: {rel}")
        seen.add(rel)
        path = ROOT / rel
        if not path.exists():
            raise SystemExit(f"{label} spec part missing: {rel}")
        size = path.stat().st_size
        if size <= 0 or size > MAX_SPEC_PART_BYTES:
            raise SystemExit(f"{label} spec part outside locality budget: {rel} has {size} bytes")


def _check_segment_iterator(
    label: str,
    segments: list[tuple[str, list[dict[str, Any]]]],
    part_paths: list[str],
    aggregate_rows: list[dict[str, Any]],
    iterator_rows: list[tuple[str, dict[str, Any]]],
) -> None:
    segment_paths = [segment_path for segment_path, _rows in segments]
    if part_paths != segment_paths:
        raise SystemExit(f"{label} part-path list drifted from segment table")
    flattened = [row for _segment_path, rows in segments for row in rows]
    iter_flattened = [row for _segment_path, row in iterator_rows]
    if aggregate_rows != flattened or iter_flattened != flattened:
        raise SystemExit(f"{label} aggregate specs must be derived from segment rows, not from a separate authority list")
    empty = [path for path, rows in segments if not rows]
    if empty:
        raise SystemExit(f"{label} segment(s) have no rows: {empty}")
    unknown_segment = [segment for segment, _row in iterator_rows if segment not in part_paths]
    if unknown_segment:
        raise SystemExit(f"{label} iterator emitted row from unknown segment: {unknown_segment[:3]}")


def _check_sources(label: str, rows: list[dict[str, Any]], expected: int) -> None:
    if len(rows) != expected:
        raise SystemExit(f"{label} specs expected {expected} rows, found {len(rows)}")
    sources = [row.get("source_checker") for row in rows]
    bad = [source for source in sources if not isinstance(source, str) or not source.startswith("check_")]
    if bad:
        raise SystemExit(f"{label} specs have bad source checker names: {bad[:3]}")
    duplicates = [source for source, count in Counter(sources).items() if count > 1]
    if duplicates:
        raise SystemExit(f"{label} specs duplicate source checkers: {duplicates}")


def _check_former_wrappers_absent(label: str, rows: list[dict[str, Any]]) -> None:
    present = []
    for row in rows:
        source = row.get("source_checker")
        if isinstance(source, str) and (ROOT / "tools" / source).exists():
            present.append(source)
    if present:
        raise SystemExit(f"{label} former wrapper(s) still exist: {present[:5]}")


gpu_iter_rows = list(iter_gpu_witness_contract_specs())
_check_part_paths("GPU witness", GPU_WITNESS_CONTRACT_SPEC_PARTS, min_parts=4)
_check_segment_iterator(
    "GPU witness",
    GPU_WITNESS_CONTRACT_SPEC_SEGMENTS,
    GPU_WITNESS_CONTRACT_SPEC_PARTS,
    GPU_WITNESS_CONTRACT_SPECS,
    gpu_iter_rows,
)
_check_sources("GPU witness", GPU_WITNESS_CONTRACT_SPECS, EXPECTED_GPU_CONTRACTS)
_check_former_wrappers_absent("GPU witness", GPU_WITNESS_CONTRACT_SPECS)

std_iter_rows = list(iter_gpustorming_standard_contract_specs())
_check_part_paths("standard GPustorming", GPUSTORMING_STANDARD_CONTRACT_SPEC_PARTS, min_parts=4)
_check_segment_iterator(
    "standard GPustorming",
    GPUSTORMING_STANDARD_CONTRACT_SPEC_SEGMENTS,
    GPUSTORMING_STANDARD_CONTRACT_SPEC_PARTS,
    GPUSTORMING_STANDARD_CONTRACT_SPECS,
    std_iter_rows,
)
_check_sources("standard GPustorming", GPUSTORMING_STANDARD_CONTRACT_SPECS, EXPECTED_STANDARD_GPUSTORMING_CONTRACTS)
_check_former_wrappers_absent("standard GPustorming", GPUSTORMING_STANDARD_CONTRACT_SPECS)
for row in GPUSTORMING_STANDARD_CONTRACT_SPECS:
    if "source" in row:
        raise SystemExit(f"standard GPustorming specs must not retain executable source payloads: {row.get('source_checker')}")
    if row.get("mode") not in {"needle_map", "standard_family", "phrase_family"}:
        raise SystemExit(f"standard GPustorming spec has unsupported mode: {row.get('source_checker')} -> {row.get('mode')}")

method_iter_rows = list(iter_method_doc_ratchet_contract_specs())
_check_part_paths("method-doc ratchet", METHOD_DOC_RATCHET_CONTRACT_SPEC_PARTS, min_parts=2)
_check_segment_iterator(
    "method-doc ratchet",
    METHOD_DOC_RATCHET_CONTRACT_SPEC_SEGMENTS,
    METHOD_DOC_RATCHET_CONTRACT_SPEC_PARTS,
    METHOD_DOC_RATCHET_CONTRACT_SPECS,
    method_iter_rows,
)
_check_sources("method-doc ratchet", METHOD_DOC_RATCHET_CONTRACT_SPECS, EXPECTED_METHOD_DOC_RATCHET_CONTRACTS)
_check_former_wrappers_absent("method-doc ratchet", METHOD_DOC_RATCHET_CONTRACT_SPECS)
for row in METHOD_DOC_RATCHET_CONTRACT_SPECS:
    if set(row) != {"source_checker", "doc_path", "doc_needles", "prompt_runbook_needles"}:
        raise SystemExit(f"method-doc ratchet spec has unsupported keys: {row.get('source_checker')} -> {sorted(row)}")

core_iter_rows = list(iter_core_method_contract_specs())
_check_part_paths("core method", CORE_METHOD_CONTRACT_SPEC_PARTS, min_parts=2)
_check_segment_iterator(
    "core method",
    CORE_METHOD_CONTRACT_SPEC_SEGMENTS,
    CORE_METHOD_CONTRACT_SPEC_PARTS,
    CORE_METHOD_CONTRACT_SPECS,
    core_iter_rows,
)
_check_sources("core method", CORE_METHOD_CONTRACT_SPECS, EXPECTED_CORE_METHOD_CONTRACTS)
_check_former_wrappers_absent("core method", CORE_METHOD_CONTRACT_SPECS)
for row in CORE_METHOD_CONTRACT_SPECS:
    if set(row) != {"source_checker", "doc_path", "doc_needles", "surface_needles"}:
        raise SystemExit(f"core method spec has unsupported keys: {row.get('source_checker')} -> {sorted(row)}")

print(
    "check_batch_spec_locality_contract: OK "
    f"({len(GPU_WITNESS_CONTRACT_SPEC_PARTS)} GPU parts, "
    f"{len(GPUSTORMING_STANDARD_CONTRACT_SPEC_PARTS)} GPustorming parts, "
    f"{len(METHOD_DOC_RATCHET_CONTRACT_SPEC_PARTS)} method-doc ratchet parts, "
    f"{len(CORE_METHOD_CONTRACT_SPEC_PARTS)} core method parts, no separate index authority)"
)
