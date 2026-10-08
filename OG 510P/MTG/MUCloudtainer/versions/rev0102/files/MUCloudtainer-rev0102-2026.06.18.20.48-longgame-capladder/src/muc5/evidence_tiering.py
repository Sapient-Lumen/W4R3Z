from __future__ import annotations

import csv
import hashlib
import json
import shutil
import stat
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from .evidence_index import EvidenceRecord, build_evidence_index

CATALOG_FORMAT = "muc5-evidence-tiering-v1"
BUNDLE_FORMAT = "muc5-evidence-bundle-v1"


@dataclass(frozen=True)
class ReferenceRoleSummary:
    producers: tuple[str, ...] = ()
    consumers: tuple[str, ...] = ()
    audit_metadata: tuple[str, ...] = ()
    documentation: tuple[str, ...] = ()
    unknown: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TieredEvidenceRecord:
    path: str
    bytes: int
    sha256: str
    row_count: int | None
    evidence_kind: str
    storage_class: str
    storage_reason: str
    compact_derivatives: tuple[str, ...]
    reference_roles: ReferenceRoleSummary
    bundle_member: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["reference_roles"] = self.reference_roles.as_dict()
        return payload


def sha256_file(path: str | Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _reference_lines(root: Path, record: EvidenceRecord) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    basename = Path(record.path).name
    for relative in record.referenced_by:
        source = root / relative
        if not source.is_file():
            continue
        try:
            lines = source.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue
        for line in lines:
            if basename in line or record.path in line:
                out.append((relative, line.strip()))
    return out


def classify_reference_roles(root: str | Path, record: EvidenceRecord) -> ReferenceRoleSummary:
    root_path = Path(root).resolve()
    buckets: dict[str, set[str]] = {
        "producers": set(),
        "consumers": set(),
        "audit_metadata": set(),
        "documentation": set(),
        "unknown": set(),
    }
    producer_tokens = (
        "write_csv(",
        "write_trace_jsonl(",
        ".to_csv(",
        ".write_text(",
        ".write_bytes(",
        "csv.writer(",
        "DictWriter(",
    )
    consumer_tokens = (
        "read_csv(",
        "read_trace_jsonl(",
        "csv.DictReader(",
        "json.load(",
        ".read_text(",
        ".read_bytes(",
        ".open()",
        ".open(\"r",
        ".open('r",
        "gzip.open(",
    )
    audit_tokens = ("count_csv_rows(", "count_csv_rows_or_catalog(", ".exists()", "row_count", "sha256")

    for relative, line in _reference_lines(root_path, record):
        if relative.startswith("data/") or relative.startswith("docs/") or relative in {"README.md", "manifest.json"}:
            buckets["documentation"].add(relative)
            continue
        if relative.endswith("run_rev0068_cloudtainer_audit.py") or relative.endswith("run_rev0072_evidence_tiering.py"):
            buckets["audit_metadata"].add(relative)
            continue
        if any(token in line for token in producer_tokens):
            buckets["producers"].add(relative)
            continue
        if relative.endswith("audit_cube.py") and any(token in line for token in audit_tokens):
            buckets["audit_metadata"].add(relative)
            continue
        if any(token in line for token in consumer_tokens):
            buckets["consumers"].add(relative)
            continue
        # Cache probes usually mean the historical script can optionally reuse
        # materialized raw evidence; they are consumers, not reasons to keep it hot.
        if "cached_" in line or "cache" in line.lower():
            buckets["consumers"].add(relative)
            continue
        buckets["unknown"].add(relative)

    return ReferenceRoleSummary(**{key: tuple(sorted(value)) for key, value in buckets.items()})


def build_tiering_catalog(
    root: str | Path,
    *,
    hot_paths: Iterable[str],
    min_bytes: int = 1024 * 1024,
    bundle_filename: str | None = None,
    bundle_root: str | None = None,
    bundle_sha256: str | None = None,
    bundle_bytes: int | None = None,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    hot = {PurePosixPath(path).as_posix() for path in hot_paths}
    indexed = build_evidence_index(root_path, min_bytes=min_bytes)
    records: list[TieredEvidenceRecord] = []
    for record in indexed:
        roles = classify_reference_roles(root_path, record)
        if record.path in hot:
            storage_class = "hot_core"
            reason = "Retained because the current inherited audit reads row-level contents, not only compact derivatives."
            bundle_member = None
        else:
            storage_class = "cold_sidecar"
            if roles.consumers:
                reason = "Historical runtime consumer exists; materialize from the immutable sidecar before rerunning that script."
            elif roles.audit_metadata:
                reason = "Only row-count/hash audit use remains; the core audit reads this metadata from the catalog."
            elif roles.producers:
                reason = "Producer-only historical output; preserved in the immutable sidecar and reproducible from source."
            else:
                reason = "No current row-level core dependency; preserved in the immutable sidecar."
            bundle_member = f"{bundle_root}/{record.path}" if bundle_root else record.path
        records.append(
            TieredEvidenceRecord(
                path=record.path,
                bytes=record.bytes,
                sha256=record.sha256,
                row_count=record.row_count,
                evidence_kind=record.evidence_kind,
                storage_class=storage_class,
                storage_reason=reason,
                compact_derivatives=record.compact_derivatives,
                reference_roles=roles,
                bundle_member=bundle_member,
            )
        )

    cold = [record for record in records if record.storage_class == "cold_sidecar"]
    hot_records = [record for record in records if record.storage_class == "hot_core"]
    return {
        "format": CATALOG_FORMAT,
        "source_cube": root_path.name,
        "min_bytes": min_bytes,
        "bundle": {
            "filename": bundle_filename,
            "root": bundle_root,
            "sha256": bundle_sha256,
            "bytes": bundle_bytes,
        },
        "summary": {
            "records": len(records),
            "hot_core_records": len(hot_records),
            "hot_core_bytes": sum(record.bytes for record in hot_records),
            "cold_sidecar_records": len(cold),
            "cold_sidecar_bytes": sum(record.bytes for record in cold),
            "cold_records_with_runtime_consumers": sum(bool(record.reference_roles.consumers) for record in cold),
            "cold_records_producer_only": sum(
                bool(record.reference_roles.producers)
                and not record.reference_roles.consumers
                and not record.reference_roles.unknown
                for record in cold
            ),
        },
        "records": [record.as_dict() for record in records],
    }


def write_tiering_catalog(path: str | Path, catalog: Mapping[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(catalog, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def load_tiering_catalog(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("format") != CATALOG_FORMAT:
        raise ValueError(f"unsupported evidence catalog: {path}")
    return payload


def catalog_records_by_path(catalog: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(record["path"]): record
        for record in catalog.get("records", [])
        if isinstance(record, Mapping) and record.get("path")
    }


def tiering_catalog_candidates(root: str | Path) -> tuple[Path, ...]:
    """Return known evidence-tier catalogs newest first.

    rev0072 introduced cold evidence sidecars.  Hardcoding that one filename made
    every later revision depend on stale path literals.  Newer revisions can now
    copy or regenerate the catalog with their own revision prefix while old
    rev0072 packages still work unchanged.
    """

    data = Path(root).resolve() / "data"
    if not data.is_dir():
        return ()
    return tuple(sorted(data.glob("rev*_evidence_tiering_catalog.json"), reverse=True))


def find_tiering_catalog(root: str | Path, preferred: str | Path | None = None) -> Path | None:
    if preferred is not None:
        path = Path(preferred)
        if not path.is_absolute():
            path = Path(root).resolve() / path
        return path if path.is_file() else None
    candidates = tiering_catalog_candidates(root)
    return candidates[0] if candidates else None


def catalog_row_count(
    root: str | Path,
    relative_path: str,
    *,
    catalog_path: str | Path | None = None,
) -> int | None:
    root_path = Path(root).resolve()
    resolved = find_tiering_catalog(root_path, catalog_path)
    if resolved is None:
        return None
    record = catalog_records_by_path(load_tiering_catalog(resolved)).get(PurePosixPath(relative_path).as_posix())
    if not record:
        return None
    value = record.get("row_count")
    return int(value) if value is not None else None


def _bundle_timestamp(timestamp: str) -> tuple[int, int, int, int, int, int]:
    dt = datetime.strptime(timestamp, "%Y.%m.%d.%H.%M")
    return (dt.year, dt.month, dt.day, dt.hour, dt.minute, 0)


def _file_info(name: str, timestamp: tuple[int, int, int, int, int, int]) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=timestamp)
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def _dir_info(name: str, timestamp: tuple[int, int, int, int, int, int]) -> zipfile.ZipInfo:
    if not name.endswith("/"):
        name += "/"
    info = zipfile.ZipInfo(name, date_time=timestamp)
    info.create_system = 3
    info.external_attr = ((stat.S_IFDIR | 0o755) << 16) | 0x10
    info.compress_type = zipfile.ZIP_STORED
    return info


def build_evidence_bundle(
    root: str | Path,
    catalog: Mapping[str, Any],
    output: str | Path,
    *,
    bundle_root: str,
    timestamp: str,
    compresslevel: int = 9,
) -> Path:
    root_path = Path(root).resolve()
    output_path = Path(output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()
    stamp = _bundle_timestamp(timestamp)
    cold = [
        record
        for record in catalog.get("records", [])
        if isinstance(record, Mapping) and record.get("storage_class") == "cold_sidecar"
    ]
    bundle_manifest = {
        "format": BUNDLE_FORMAT,
        "bundle_root": bundle_root,
        "source_cube": catalog.get("source_cube"),
        "record_count": len(cold),
        "records": [
            {
                "path": record["path"],
                "member": f"{bundle_root}/{record['path']}",
                "bytes": record["bytes"],
                "sha256": record["sha256"],
                "row_count": record.get("row_count"),
                "evidence_kind": record.get("evidence_kind"),
            }
            for record in cold
        ],
    }
    with zipfile.ZipFile(
        output_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=compresslevel,
        allowZip64=True,
        strict_timestamps=False,
    ) as archive:
        archive.writestr(_dir_info(bundle_root, stamp), b"")
        archive.writestr(
            _file_info(f"{bundle_root}/evidence_manifest.json", stamp),
            json.dumps(bundle_manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n",
        )
        created_dirs: set[str] = {bundle_root}
        for record in sorted(cold, key=lambda item: str(item["path"])):
            relative = PurePosixPath(str(record["path"]))
            source = root_path / Path(*relative.parts)
            if not source.is_file():
                raise FileNotFoundError(source)
            parent_parts = list(relative.parent.parts)
            for index in range(1, len(parent_parts) + 1):
                directory = f"{bundle_root}/{'/'.join(parent_parts[:index])}"
                if directory not in created_dirs:
                    archive.writestr(_dir_info(directory, stamp), b"")
                    created_dirs.add(directory)
            member = f"{bundle_root}/{relative.as_posix()}"
            info = _file_info(member, stamp)
            info.file_size = source.stat().st_size
            with source.open("rb") as source_handle, archive.open(info, "w", force_zip64=True) as target:
                shutil.copyfileobj(source_handle, target, length=1024 * 1024)
    return output_path


def audit_evidence_bundle(bundle: str | Path, catalog: Mapping[str, Any]) -> dict[str, Any]:
    bundle_path = Path(bundle).resolve()
    errors: list[str] = []
    checked = 0
    expected = {
        str(record["bundle_member"]): record
        for record in catalog.get("records", [])
        if isinstance(record, Mapping) and record.get("storage_class") == "cold_sidecar"
    }
    with zipfile.ZipFile(bundle_path, "r") as archive:
        names = set(archive.namelist())
        missing = sorted(set(expected) - names)
        if missing:
            errors.append(f"missing members: {missing[:10]}")
        bad_member = archive.testzip()
        if bad_member is not None:
            errors.append(f"CRC failure: {bad_member}")
        for member, record in expected.items():
            if member not in names:
                continue
            digest = hashlib.sha256()
            size = 0
            with archive.open(member) as handle:
                while chunk := handle.read(1024 * 1024):
                    digest.update(chunk)
                    size += len(chunk)
            if size != int(record["bytes"]):
                errors.append(f"size mismatch: {member}")
            if digest.hexdigest() != record["sha256"]:
                errors.append(f"sha256 mismatch: {member}")
            checked += 1
    return {
        "passed": not errors,
        "bundle": str(bundle_path),
        "bundle_bytes": bundle_path.stat().st_size,
        "bundle_sha256": sha256_file(bundle_path),
        "expected_records": len(expected),
        "checked_records": checked,
        "errors": errors,
    }


def prune_cold_evidence(root: str | Path, catalog: Mapping[str, Any]) -> dict[str, Any]:
    root_path = Path(root).resolve()
    removed: list[str] = []
    removed_bytes = 0
    for record in catalog.get("records", []):
        if not isinstance(record, Mapping) or record.get("storage_class") != "cold_sidecar":
            continue
        relative = PurePosixPath(str(record["path"])).as_posix()
        path = root_path / Path(*PurePosixPath(relative).parts)
        if path.is_file():
            if sha256_file(path) != record.get("sha256"):
                raise ValueError(f"refusing to prune modified evidence: {relative}")
            removed_bytes += path.stat().st_size
            path.unlink()
            removed.append(relative)
    return {"removed": removed, "removed_count": len(removed), "removed_bytes": removed_bytes}


def materialize_evidence_bundle(
    root: str | Path,
    bundle: str | Path,
    *,
    selected_paths: Sequence[str] | None = None,
    catalog_path: str | Path | None = None,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    resolved_catalog = find_tiering_catalog(root_path, catalog_path)
    if resolved_catalog is None:
        raise FileNotFoundError("no rev*_evidence_tiering_catalog.json found")
    catalog = load_tiering_catalog(resolved_catalog)
    bundle_path = Path(bundle).resolve()
    expected_bundle = catalog.get("bundle", {})
    if expected_bundle.get("sha256") and sha256_file(bundle_path) != expected_bundle["sha256"]:
        raise ValueError("evidence bundle digest does not match catalog")
    wanted = None if selected_paths is None else {PurePosixPath(path).as_posix() for path in selected_paths}
    records = [
        record
        for record in catalog.get("records", [])
        if isinstance(record, Mapping)
        and record.get("storage_class") == "cold_sidecar"
        and (wanted is None or record.get("path") in wanted)
    ]
    restored: list[str] = []
    with zipfile.ZipFile(bundle_path, "r") as archive:
        for record in records:
            relative = PurePosixPath(str(record["path"]))
            destination = root_path / Path(*relative.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            member = str(record["bundle_member"])
            with archive.open(member) as source, destination.open("wb") as target:
                shutil.copyfileobj(source, target, length=1024 * 1024)
            if destination.stat().st_size != int(record["bytes"]) or sha256_file(destination) != record["sha256"]:
                destination.unlink(missing_ok=True)
                raise ValueError(f"materialized evidence failed verification: {relative.as_posix()}")
            restored.append(relative.as_posix())
    return {"restored": restored, "restored_count": len(restored)}


def validate_core_tiering(root: str | Path, catalog: Mapping[str, Any]) -> dict[str, Any]:
    root_path = Path(root).resolve()
    errors: list[str] = []
    hot_present = 0
    cold_absent = 0
    for record in catalog.get("records", []):
        if not isinstance(record, Mapping):
            continue
        relative = PurePosixPath(str(record["path"]))
        path = root_path / Path(*relative.parts)
        if record.get("storage_class") == "hot_core":
            if not path.is_file():
                errors.append(f"missing hot evidence: {relative.as_posix()}")
            elif path.stat().st_size != int(record["bytes"]) or sha256_file(path) != record["sha256"]:
                errors.append(f"modified hot evidence: {relative.as_posix()}")
            else:
                hot_present += 1
        elif record.get("storage_class") == "cold_sidecar":
            if path.exists():
                errors.append(f"cold evidence leaked into core: {relative.as_posix()}")
            else:
                cold_absent += 1
    return {
        "passed": not errors,
        "hot_present": hot_present,
        "cold_absent": cold_absent,
        "errors": errors,
    }


__all__ = [
    "BUNDLE_FORMAT",
    "CATALOG_FORMAT",
    "ReferenceRoleSummary",
    "TieredEvidenceRecord",
    "audit_evidence_bundle",
    "build_evidence_bundle",
    "build_tiering_catalog",
    "catalog_records_by_path",
    "catalog_row_count",
    "classify_reference_roles",
    "find_tiering_catalog",
    "load_tiering_catalog",
    "materialize_evidence_bundle",
    "prune_cold_evidence",
    "sha256_file",
    "tiering_catalog_candidates",
    "validate_core_tiering",
    "write_tiering_catalog",
]
