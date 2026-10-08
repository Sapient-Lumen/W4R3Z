from __future__ import annotations

import csv
import gzip
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

BULK_SUFFIXES: tuple[str, ...] = (
    "_cpp_transitions.csv",
    "_segments.csv",
    "_trace_rows.csv",
    "_replay_traces.jsonl",
    "_public_traces.jsonl",
    "_training_dataset.csv",
)

SOURCE_EXTENSIONS: tuple[str, ...] = (".py", ".cpp", ".hpp", ".h", ".md", ".json", ".txt")
SCAN_DIRS: tuple[str, ...] = ("src", "scripts", "tests", "docs", "data")


@dataclass(frozen=True)
class EvidenceRecord:
    path: str
    bytes: int
    sha256: str
    row_count: int | None
    evidence_kind: str
    referenced_by_count: int
    referenced_by: tuple[str, ...]
    active_referenced_by_count: int
    active_referenced_by: tuple[str, ...]
    historical_referenced_by_count: int
    historical_referenced_by: tuple[str, ...]
    compact_derivatives: tuple[str, ...]
    retention_class: str
    migration_note: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _count_csv_rows(path: Path) -> int | None:
    try:
        opener = gzip.open if path.suffix == ".gz" else open
        with opener(path, "rt", encoding="utf-8", newline="") as handle:  # type: ignore[arg-type]
            return max(0, sum(1 for _ in handle) - 1)
    except Exception:
        return None


def _count_jsonl_rows(path: Path) -> int | None:
    try:
        with path.open("rt", encoding="utf-8") as handle:
            return sum(1 for line in handle if line.strip())
    except Exception:
        return None


def row_count(path: Path) -> int | None:
    name = path.name
    if name.endswith(".csv") or name.endswith(".csv.gz"):
        return _count_csv_rows(path)
    if name.endswith(".jsonl"):
        return _count_jsonl_rows(path)
    return None


def evidence_kind(path: Path) -> str:
    name = path.name
    if name.endswith("_cpp_transitions.csv"):
        return "cpp_transition_table"
    if name.endswith("_segments.csv"):
        return "segment_table"
    if name.endswith("_trace_rows.csv"):
        return "trace_row_table"
    if name.endswith("_replay_traces.jsonl") or name.endswith("_public_traces.jsonl"):
        return "replay_jsonl"
    if name.endswith("_training_dataset.csv"):
        return "training_dataset"
    if name.endswith(".csv") or name.endswith(".csv.gz"):
        return "csv_table"
    if name.endswith(".json"):
        return "json_summary"
    return "other"


def is_bulk_evidence(path: Path, *, min_bytes: int) -> bool:
    name = path.name
    return path.stat().st_size >= min_bytes and any(name.endswith(suffix) for suffix in BULK_SUFFIXES)


def _source_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for directory in SCAN_DIRS:
        base = root / directory
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in SOURCE_EXTENSIONS:
                continue
            name = path.name
            # The index must be idempotent: generated evidence-index files name
            # every candidate and should not themselves count as live consumers.
            if name.endswith("_evidence_index.json") or name.endswith("_evidence_index.csv"):
                continue
            if name == "CHECKSUMS.json":
                continue
            out.append(path)
    for path in (root / "README.md", root / "manifest.json"):
        if path.exists():
            out.append(path)
    return sorted(set(out))


def is_active_reference_path(relative_path: str) -> bool:
    """Return whether a reference should block raw-evidence migration.

    Generated data summaries often quote old filenames for provenance.  Those
    historical mentions should remain searchable, but they should not keep a
    bulky raw table in every linked working cube.  Source, scripts, tests, docs,
    README, and manifest references are treated as active surfaces that must be
    redirected before migration.
    """

    return relative_path.startswith(("src/", "scripts/", "tests/", "docs/")) or relative_path in {
        "README.md",
        "manifest.json",
    }


def source_references(root: str | Path, candidate_paths: Sequence[Path]) -> dict[str, tuple[str, ...]]:
    root_path = Path(root).resolve()
    needles = {path.relative_to(root_path).as_posix(): path.name for path in candidate_paths}
    references: dict[str, set[str]] = {rel: set() for rel in needles}
    for source in _source_files(root_path):
        try:
            text = source.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        source_rel = source.relative_to(root_path).as_posix()
        for rel, basename in needles.items():
            if source_rel == rel:
                continue
            if basename in text or rel in text:
                references[rel].add(source_rel)
    return {rel: tuple(sorted(paths)) for rel, paths in references.items()}


def compact_derivatives(root: str | Path, evidence_path: Path) -> tuple[str, ...]:
    root_path = Path(root).resolve()
    data = root_path / "data"
    name = evidence_path.name
    stems: list[str] = []
    for suffix in BULK_SUFFIXES:
        if name.endswith(suffix):
            stems.append(name[: -len(suffix)])
    if not stems and "." in name:
        stems.append(name.rsplit(".", 1)[0])
    wanted_suffixes = (
        "_summary.json",
        "_aggregate.csv",
        "_arm_summary.csv",
        "_comparisons.csv",
        "_mechanisms.csv",
        "_cpp_transition_sample.csv",
        "_replay_results.json",
    )
    found: list[str] = []
    for stem in stems:
        for suffix in wanted_suffixes:
            candidate = data / f"{stem}{suffix}"
            if candidate.exists() and candidate != evidence_path:
                found.append(candidate.relative_to(root_path).as_posix())
    return tuple(sorted(set(found)))


def build_evidence_index(root: str | Path, *, min_bytes: int = 1024 * 1024) -> list[EvidenceRecord]:
    root_path = Path(root).resolve()
    data = root_path / "data"
    candidates = sorted(
        (path for path in data.rglob("*") if path.is_file() and is_bulk_evidence(path, min_bytes=min_bytes)),
        key=lambda p: (-p.stat().st_size, p.as_posix()),
    )
    refs = source_references(root_path, candidates)
    records: list[EvidenceRecord] = []
    for path in candidates:
        rel = path.relative_to(root_path).as_posix()
        derivatives = compact_derivatives(root_path, path)
        referenced_by = refs.get(rel, ())
        active_referenced_by = tuple(ref for ref in referenced_by if is_active_reference_path(ref))
        historical_referenced_by = tuple(ref for ref in referenced_by if not is_active_reference_path(ref))
        kind = evidence_kind(path)
        if active_referenced_by:
            retention = "blocked_by_live_reference"
            note = "Do not migrate until source/script/test/doc references are redirected to summaries or the evidence index."
        elif not derivatives:
            retention = "blocked_missing_compact_derivative"
            note = "Create a compact derivative or reproducer before moving raw evidence out of core."
        else:
            retention = "evidence_archive_candidate"
            if historical_referenced_by:
                note = "Candidate despite historical generated-data mentions; active references are already clear."
            else:
                note = "Safe first-pass candidate once an immutable external evidence bundle location is assigned."
        records.append(
            EvidenceRecord(
                path=rel,
                bytes=path.stat().st_size,
                sha256=sha256_file(path),
                row_count=row_count(path),
                evidence_kind=kind,
                referenced_by_count=len(referenced_by),
                referenced_by=referenced_by,
                active_referenced_by_count=len(active_referenced_by),
                active_referenced_by=active_referenced_by,
                historical_referenced_by_count=len(historical_referenced_by),
                historical_referenced_by=historical_referenced_by,
                compact_derivatives=derivatives,
                retention_class=retention,
                migration_note=note,
            )
        )
    return records


def write_evidence_index(root: str | Path, *, json_path: str | Path, csv_path: str | Path, min_bytes: int = 1024 * 1024) -> dict[str, object]:
    root_path = Path(root).resolve()
    records = build_evidence_index(root_path, min_bytes=min_bytes)
    json_out = Path(json_path)
    csv_out = Path(csv_path)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "min_bytes": int(min_bytes),
        "records": [record.as_dict() for record in records],
        "summary": summarize_evidence_records(records),
    }
    json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rows = [flatten_evidence_record(record) for record in records]
    if rows:
        with csv_out.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        csv_out.write_text("", encoding="utf-8")
    return payload["summary"]


def flatten_evidence_record(record: EvidenceRecord) -> dict[str, object]:
    out = record.as_dict()
    out["referenced_by"] = ";".join(record.referenced_by)
    out["active_referenced_by"] = ";".join(record.active_referenced_by)
    out["historical_referenced_by"] = ";".join(record.historical_referenced_by)
    out["compact_derivatives"] = ";".join(record.compact_derivatives)
    return out


def summarize_evidence_records(records: Sequence[EvidenceRecord]) -> dict[str, object]:
    by_class: dict[str, int] = {}
    bytes_by_class: dict[str, int] = {}
    by_kind: dict[str, int] = {}
    bytes_by_kind: dict[str, int] = {}
    active_ref_records = 0
    historical_only_records = 0
    active_ref_edges = 0
    historical_ref_edges = 0
    for record in records:
        by_class[record.retention_class] = by_class.get(record.retention_class, 0) + 1
        bytes_by_class[record.retention_class] = bytes_by_class.get(record.retention_class, 0) + record.bytes
        by_kind[record.evidence_kind] = by_kind.get(record.evidence_kind, 0) + 1
        bytes_by_kind[record.evidence_kind] = bytes_by_kind.get(record.evidence_kind, 0) + record.bytes
        active_ref_edges += record.active_referenced_by_count
        historical_ref_edges += record.historical_referenced_by_count
        if record.active_referenced_by_count:
            active_ref_records += 1
        elif record.historical_referenced_by_count:
            historical_only_records += 1
    top = sorted(records, key=lambda r: r.bytes, reverse=True)[:10]
    return {
        "records": len(records),
        "bytes": sum(r.bytes for r in records),
        "bytes_mib": round(sum(r.bytes for r in records) / 1024 / 1024, 3),
        "records_by_retention_class": by_class,
        "bytes_by_retention_class": bytes_by_class,
        "records_by_kind": by_kind,
        "bytes_by_kind": bytes_by_kind,
        "records_with_active_references": active_ref_records,
        "records_with_historical_only_references": historical_only_records,
        "active_reference_edges": active_ref_edges,
        "historical_reference_edges": historical_ref_edges,
        "top_paths": [r.path for r in top],
    }


__all__ = [
    "BULK_SUFFIXES",
    "EvidenceRecord",
    "build_evidence_index",
    "compact_derivatives",
    "evidence_kind",
    "flatten_evidence_record",
    "is_active_reference_path",
    "is_bulk_evidence",
    "sha256_file",
    "source_references",
    "summarize_evidence_records",
    "write_evidence_index",
]
