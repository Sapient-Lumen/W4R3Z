#!/usr/bin/env python3
"""mkrevzip.py

Create a standard-named Micromax release zip from the current working tree.

This exists to make "hand-evolved offline archives" easy and repeatable.
It intentionally does *not* modify the repo (no auto-bump); it just packages.

Usage:
  python tools/mkrevzip.py --tag fsstat-helplink-heading-mkrevzip-skyotter

The resulting filename uses the conventional pattern:
  Micromax-rev####-YYYY.MM.DD.HH.MM-<tag>.zip

Rev is inferred from the current repo context.
Timestamp is created in America/New_York by default.
Each archive also embeds one machine-readable repo-context snapshot so future
humans/LLMs can inspect the packaged revision without reopening half the tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path, PurePosixPath
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))


class RevisionLineageError(ValueError):
    """Raised when revision breadcrumbs disagree or an archive name is invalid."""


ARCHIVE_NAME_RE = re.compile(
    r"^Micromax-rev(?P<rev>\d{4,})-"
    r"(?P<stamp>\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-"
    r"(?P<tag>[a-z0-9]+(?:-[a-z0-9]+)*)\.zip$"
)

ZIP_COMPRESSION_LEVEL = 9
SNAPSHOT_FILE_MODE = 0o644
SNAPSHOT_DIR_MODE = 0o755
ZIP_FILE_MODE = stat.S_IFREG | SNAPSHOT_FILE_MODE


def parse_archive_name(name: str) -> dict[str, object]:
    """Parse and validate the canonical Micromax revision archive filename."""

    raw = str(name or "")
    match = ARCHIVE_NAME_RE.fullmatch(raw)
    if match is None:
        raise RevisionLineageError(
            "archive filename must match "
            "Micromax-rev####-YYYY.MM.DD.HH.MM-lowercase-hyphen-tag.zip"
        )
    stamp = str(match.group("stamp"))
    try:
        parsed_stamp = datetime.strptime(stamp, "%Y.%m.%d.%H.%M")
    except ValueError as exc:
        raise RevisionLineageError(f"archive timestamp is invalid: {stamp}") from exc
    if not 1980 <= parsed_stamp.year <= 2107:
        raise RevisionLineageError(
            f"archive timestamp year is outside the ZIP range 1980..2107: {stamp}"
        )
    return {
        "revision": int(match.group("rev")),
        "timestamp": stamp,
        "tag": str(match.group("tag")),
    }


def _revision_evidence(
    *,
    todo_text: str,
    readme_text: str,
    revision_index: object,
    context: object | None = None,
) -> dict[str, int]:
    """Extract the independent revision breadcrumbs used for handoff lineage."""

    evidence: dict[str, int] = {}
    todo_lines = str(todo_text).splitlines()
    if todo_lines:
        match = re.search(r"\brev\s*(\d+)\s+note:", todo_lines[0], flags=re.IGNORECASE)
        if match is not None:
            evidence["TODO.md note"] = int(match.group(1))
    for line in todo_lines:
        match = re.match(r"^#\s+TODO\s*\(\s*rev\s*(\d+)\s*\)\s*$", line, flags=re.IGNORECASE)
        if match is not None:
            evidence["TODO.md heading"] = int(match.group(1))
            break

    for line in str(readme_text).splitlines()[:12]:
        match = re.search(r"\bRev\s*(\d+)\s+note:", line, flags=re.IGNORECASE)
        if match is not None:
            evidence["README.md note"] = int(match.group(1))
            break

    if isinstance(revision_index, dict):
        current = revision_index.get("current_rev")
        if isinstance(current, int) and not isinstance(current, bool):
            evidence["revision-index current_rev"] = int(current)
        entries = revision_index.get("entries")
        if isinstance(entries, list) and entries and isinstance(entries[0], dict):
            head = entries[0].get("rev")
            if isinstance(head, int) and not isinstance(head, bool):
                evidence["revision-index head"] = int(head)

    if isinstance(context, dict):
        context_rev = context.get("rev")
        if isinstance(context_rev, int) and not isinstance(context_rev, bool):
            evidence["context rev"] = int(context_rev)
    return evidence


def _context_payload(data: object) -> dict[str, object] | None:
    """Return a repo-context payload from a plain snapshot or archive wrapper."""

    if not isinstance(data, dict):
        return None
    if data.get("project") == "micromax":
        return data
    nested = data.get("context")
    if isinstance(nested, dict) and nested.get("project") == "micromax":
        return nested
    return None


def _agreed_revision(
    evidence: dict[str, int],
    *,
    expected: int | None = None,
    required: tuple[str, ...],
    prefix: str,
) -> int:
    missing = [label for label in required if label not in evidence]
    if missing:
        raise RevisionLineageError(
            f"{prefix} is missing revision source(s): {', '.join(missing)}"
        )
    values = {label: int(evidence[label]) for label in required}
    distinct = sorted(set(values.values()))
    if len(distinct) != 1:
        detail = ", ".join(f"{label}={value}" for label, value in values.items())
        raise RevisionLineageError(f"{prefix} revision sources disagree: {detail}")
    revision = distinct[0]
    if expected is not None and revision != int(expected):
        detail = ", ".join(f"{label}={value}" for label, value in values.items())
        raise RevisionLineageError(
            f"{prefix} does not match expected revision {int(expected)}: {detail}"
        )
    return revision


def infer_rev(root: Path) -> int:
    """Infer the current revision only when all durable breadcrumbs agree."""

    try:
        todo_text = (root / "TODO.md").read_text(encoding="utf-8", errors="replace")
        readme_text = (root / "README.md").read_text(encoding="utf-8", errors="replace")
        revision_index = _strict_json_object(
            (root / "docs" / "revision-index.json").read_bytes(),
            label="repository revision index",
            error_type=RevisionLineageError,
        )
        raw_context = _strict_json_object(
            (root / "MICROMAX-CONTEXT.json").read_bytes(),
            label="repository context",
            error_type=RevisionLineageError,
        )
    except OSError as exc:
        raise RevisionLineageError(f"could not read revision lineage inputs: {exc}") from exc
    context = _context_payload(raw_context)
    evidence = _revision_evidence(
        todo_text=todo_text,
        readme_text=readme_text,
        revision_index=revision_index,
        context=context,
    )
    return _agreed_revision(
        evidence,
        required=(
            "TODO.md note",
            "TODO.md heading",
            "README.md note",
            "revision-index current_rev",
            "revision-index head",
            "context rev",
        ),
        prefix="repository",
    )


HANDOFF_ARTIFACT_NAMES = {
    "mxtest-all.json",
    "mxtest-all-64.json",
    "mxtimely-summary.json",
    "mxrelease-full-suite.json",
}
REVISION_EVIDENCE_ARTIFACT_RE = re.compile(
    r"^rev\d{4,}-[a-z0-9]+(?:-[a-z0-9]+)*\.json$"
)
REVISION_EVIDENCE_ARTIFACT_MAX_BYTES = 1024 * 1024


def is_revision_evidence_artifact(rel: Path) -> bool:
    """Return True for one canonical, permanent per-revision JSON receipt."""

    parts = rel.parts
    return (
        len(parts) == 2
        and parts[0] == ".artifacts"
        and REVISION_EVIDENCE_ARTIFACT_RE.fullmatch(parts[1]) is not None
    )


def is_handoff_artifact(rel: Path) -> bool:
    """Return True for compact evidence manifests worth carrying in handoff zips."""

    parts = rel.parts
    return (
        len(parts) == 2
        and parts[0] == ".artifacts"
        and (
            parts[1] in HANDOFF_ARTIFACT_NAMES
            or is_revision_evidence_artifact(rel)
        )
    )


def should_skip(rel: Path) -> bool:
    if is_handoff_artifact(rel):
        return False
    parts = rel.parts
    if not parts:
        return True

    top = parts[0]
    if top.startswith("."):
        if top == ".artifacts":
            return True
        if top in {".git", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv"}:
            return True
        if top.startswith(".tmp"):
            return True
    if "__pycache__" in parts:
        return True
    if any(part.endswith(".egg-info") for part in parts):
        return True
    if rel.suffix.lower() in {".pyc", ".pyo", ".zip"}:
        return True
    if top in {"build", "dist"}:
        return True
    return False


def _load_existing_context(root: Path, *, rev: int) -> dict[str, object] | None:
    """Return a current checked context snapshot already present in the tree.

    Packaging used to rebuild ``mxcontext.payload()`` for every mkrevzip
    subprocess.  That is correct but needlessly heavy in the test/doctor lanes,
    where several archive smoke tests can run in one pytest process and push a
    constrained cloudtainer over its memory ceiling.  Prefer the committed
    ``MICROMAX-CONTEXT.json`` snapshot when it matches the revision and reports a
    clean context check; fall back to live generation when the snapshot is absent
    or stale.
    """

    path = root / "MICROMAX-CONTEXT.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    data = _context_payload(data)
    if data is None:
        return None
    if data.get("project") != "micromax" or data.get("rev") != int(rev):
        return None
    checks = data.get("checks")
    if isinstance(checks, dict) and checks.get("ok") is not True:
        return None
    sources = data.get("revision_sources")
    if isinstance(sources, dict) and sources.get("ok") is not True:
        return None
    return data


def context_snapshot(root: Path, *, rev: int) -> dict[str, object]:
    """Return the context snapshot embedded into the archive manifest."""

    existing = _load_existing_context(root, rev=rev)
    if existing is not None:
        snapshot = existing
    else:
        from mxcontext import payload as context_payload

        snapshot = context_payload()
    if not isinstance(snapshot, dict):
        raise RevisionLineageError("context snapshot root is not an object")
    if snapshot.get("project") != "micromax":
        raise RevisionLineageError("context snapshot project is not micromax")
    if snapshot.get("rev") != int(rev):
        raise RevisionLineageError(
            f"context snapshot revision {snapshot.get('rev')!r} does not match requested revision {int(rev)}"
        )
    return snapshot


ARCHIVE_PROVENANCE_SCHEMA = "micromax.mkrevzip.archive-provenance.v1"
RELEASE_SOURCE_SCHEMA = "micromax.release-source.v1"
RELEASE_RECEIPT_SCHEMA = "micromax.release-receipt.v1"
MIN_ZIP_EPOCH = 315532800  # 1980-01-01, the oldest timestamp representable by ZIP.
DEFAULT_RELEASE_RECEIPT_MAX_BYTES = 1024 * 1024


class ArchiveVerificationError(ValueError):
    """Raised when a revision archive does not match its embedded provenance."""


ARCHIVE_VERIFICATION_SCHEMA = "micromax.mkrevzip.archive-verification.v1"
DEFAULT_VERIFY_MAX_MEMBERS = 20_000
DEFAULT_VERIFY_MAX_UNCOMPRESSED_BYTES = 512 * 1024 * 1024
DEFAULT_VERIFY_MAX_COMPRESSED_BYTES = 512 * 1024 * 1024


class _StrictJsonFailure(ValueError):
    """Internal marker used to preserve strict-parser failure detail."""


def _strict_json_object(
    data: bytes | str,
    *,
    label: str,
    error_type: type[ValueError],
) -> dict[str, object]:
    """Decode a UTF-8 JSON object without duplicate names or NaN constants."""

    try:
        text = data.decode("utf-8") if isinstance(data, bytes) else str(data)
    except UnicodeDecodeError as exc:
        raise error_type(f"{label} is not valid UTF-8 JSON") from exc

    def reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise _StrictJsonFailure(f"contains duplicate JSON name: {key!r}")
            result[key] = value
        return result

    def reject_constant(value: str) -> object:
        raise _StrictJsonFailure(f"contains non-standard JSON number: {value}")

    try:
        value = json.loads(
            text,
            object_pairs_hook=reject_duplicate_pairs,
            parse_constant=reject_constant,
        )
    except _StrictJsonFailure as exc:
        raise error_type(f"{label} {exc}") from exc
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise error_type(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise error_type(f"{label} root is not an object")
    return value


def canonical_json_bytes(value: object) -> bytes:
    """Return the stable JSON encoding used for receipt digests."""

    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def context_input_bytes(context: dict[str, object]) -> bytes:
    """Return the exact canonical source form of ``MICROMAX-CONTEXT.json``."""

    return (
        json.dumps(context, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def archive_stamp_epoch(stamp: str, tz_name: str) -> int:
    """Convert one canonical archive stamp to an integer Unix timestamp."""

    try:
        timezone = ZoneInfo(str(tz_name))
        moment = datetime.strptime(str(stamp), "%Y.%m.%d.%H.%M").replace(
            tzinfo=timezone
        )
    except (ValueError, ZoneInfoNotFoundError) as exc:
        raise RevisionLineageError(
            f"could not derive archive epoch from stamp={stamp!r} timezone={tz_name!r}"
        ) from exc
    return max(MIN_ZIP_EPOCH, int(moment.timestamp()))


def release_source_descriptor(
    *,
    provenance: dict[str, object],
    context: dict[str, object],
    revision: int,
    context_path: str,
    source_date_epoch: int,
    epoch_origin: str,
) -> dict[str, object]:
    """Name the complete source generation consumed by tests and packaging.

    Archive provenance intentionally excludes the generated archive manifest.
    The release-source identity closes that gap by adding the exact canonical
    context input that materialized snapshots carry at ``context_path``.
    """

    if provenance.get("schema") != ARCHIVE_PROVENANCE_SCHEMA:
        raise RevisionLineageError("release source uses unrecognized archive provenance")
    epoch = int(source_date_epoch)
    if epoch < MIN_ZIP_EPOCH:
        raise RevisionLineageError(
            f"SOURCE_DATE_EPOCH must be at least {MIN_ZIP_EPOCH}, got {epoch}"
        )
    reason = _unsafe_member_reason(str(context_path))
    if reason is not None:
        raise RevisionLineageError(
            f"release source context path {context_path!r} is unsafe: {reason}"
        )
    origin = str(epoch_origin or "").strip()
    if not origin:
        raise RevisionLineageError("release source epoch origin is empty")

    context_bytes = context_input_bytes(context)
    context_row = {
        "path": str(context_path),
        "bytes": len(context_bytes),
        "sha256": hashlib.sha256(context_bytes).hexdigest(),
    }
    member_digest = str(provenance.get("digest") or "")
    member_count = int(provenance.get("file_count") or 0)
    member_bytes = int(provenance.get("total_bytes") or 0)
    if not re.fullmatch(r"[0-9a-f]{64}", member_digest):
        raise RevisionLineageError("release source archive-member digest is invalid")
    if member_count < 0 or member_bytes < 0:
        raise RevisionLineageError("release source archive-member totals are invalid")
    file_count = member_count + 1
    total_bytes = member_bytes + len(context_bytes)

    source_digest = _release_source_digest(
        revision=int(revision),
        member_digest=member_digest,
        context_row=context_row,
        source_date_epoch=epoch,
        epoch_origin=origin,
    )

    return {
        "schema": RELEASE_SOURCE_SCHEMA,
        "revision": int(revision),
        "digest": source_digest,
        "file_count": file_count,
        "total_bytes": total_bytes,
        # Do not duplicate the full per-file entry list already carried at
        # archive.provenance.  The verifier reconstructs this compact identity
        # from the actual archive bytes and compares it to the receipt source.
        "archive_members": {
            "schema": ARCHIVE_PROVENANCE_SCHEMA,
            "digest": member_digest,
            "file_count": member_count,
            "total_bytes": member_bytes,
        },
        "context_input": context_row,
        "source_date_epoch": {
            "value": epoch,
            "origin": origin,
        },
    }


def _release_source_digest(
    *,
    revision: int,
    member_digest: str,
    context_row: dict[str, object],
    source_date_epoch: int,
    epoch_origin: str,
) -> str:
    """Digest every release input that can affect the resulting artifacts."""

    identity = hashlib.sha256()
    identity.update(RELEASE_SOURCE_SCHEMA.encode("ascii"))
    identity.update(b"\n")
    identity.update(str(int(revision)).encode("ascii"))
    identity.update(b"\n")
    identity.update(str(member_digest).encode("ascii", errors="strict"))
    identity.update(b"\n")
    identity.update(str(context_row["sha256"]).encode("ascii", errors="strict"))
    identity.update(b" ")
    identity.update(str(int(context_row["bytes"])).encode("ascii"))
    identity.update(b" ")
    identity.update(str(context_row["path"]).encode("utf-8"))
    identity.update(b"\n")
    identity.update(str(int(source_date_epoch)).encode("ascii"))
    identity.update(b" ")
    identity.update(str(epoch_origin).encode("utf-8"))
    identity.update(b"\n")
    return identity.hexdigest()


def validate_release_source_descriptor(source: object) -> dict[str, object]:
    """Validate the compact source declaration without trusting its digest."""

    if not isinstance(source, dict):
        raise RevisionLineageError("release source declaration is not an object")
    if source.get("schema") != RELEASE_SOURCE_SCHEMA:
        raise RevisionLineageError("release source schema is not recognized")

    revision = source.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        raise RevisionLineageError("release source revision is invalid")

    archive_members = source.get("archive_members")
    if not isinstance(archive_members, dict):
        raise RevisionLineageError("release source archive-member identity is absent")
    if archive_members.get("schema") != ARCHIVE_PROVENANCE_SCHEMA:
        raise RevisionLineageError("release source archive-member schema is not recognized")
    member_digest = str(archive_members.get("digest") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", member_digest):
        raise RevisionLineageError("release source archive-member digest is invalid")
    member_count = archive_members.get("file_count")
    member_bytes = archive_members.get("total_bytes")
    if (
        not isinstance(member_count, int)
        or isinstance(member_count, bool)
        or member_count < 0
        or not isinstance(member_bytes, int)
        or isinstance(member_bytes, bool)
        or member_bytes < 0
    ):
        raise RevisionLineageError("release source archive-member totals are invalid")

    context_row = source.get("context_input")
    if not isinstance(context_row, dict):
        raise RevisionLineageError("release source context input is absent")
    context_path = str(context_row.get("path") or "")
    reason = _unsafe_member_reason(context_path)
    if reason is not None:
        raise RevisionLineageError(
            f"release source context path {context_path!r} is unsafe: {reason}"
        )
    context_digest = str(context_row.get("sha256") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", context_digest):
        raise RevisionLineageError("release source context digest is invalid")
    context_bytes = context_row.get("bytes")
    if (
        not isinstance(context_bytes, int)
        or isinstance(context_bytes, bool)
        or context_bytes < 0
    ):
        raise RevisionLineageError("release source context byte count is invalid")

    epoch_row = source.get("source_date_epoch")
    if not isinstance(epoch_row, dict):
        raise RevisionLineageError("release source epoch declaration is absent")
    epoch = epoch_row.get("value")
    if (
        not isinstance(epoch, int)
        or isinstance(epoch, bool)
        or epoch < MIN_ZIP_EPOCH
    ):
        raise RevisionLineageError("release source epoch value is invalid")
    origin = str(epoch_row.get("origin") or "").strip()
    if not origin:
        raise RevisionLineageError("release source epoch origin is empty")

    source_digest = str(source.get("digest") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", source_digest):
        raise RevisionLineageError("release source digest is invalid")

    file_count = source.get("file_count")
    total_bytes = source.get("total_bytes")
    if (
        not isinstance(file_count, int)
        or isinstance(file_count, bool)
        or file_count < 1
        or not isinstance(total_bytes, int)
        or isinstance(total_bytes, bool)
        or total_bytes < 0
    ):
        raise RevisionLineageError("release source aggregate totals are invalid")
    if file_count != member_count + 1:
        raise RevisionLineageError("release source file count does not close over context")
    if total_bytes != member_bytes + context_bytes:
        raise RevisionLineageError("release source byte total does not close over context")

    expected_digest = _release_source_digest(
        revision=revision,
        member_digest=member_digest,
        context_row=context_row,
        source_date_epoch=epoch,
        epoch_origin=origin,
    )
    if source_digest != expected_digest:
        raise RevisionLineageError("release source digest mismatch")
    return source


def seal_release_receipt(payload: dict[str, object]) -> dict[str, object]:
    """Return a receipt with a digest over every other field."""

    sealed = dict(payload)
    sealed.pop("receipt_digest", None)
    sealed["receipt_digest"] = hashlib.sha256(canonical_json_bytes(sealed)).hexdigest()
    return sealed


def validate_release_receipt(
    receipt: object,
    *,
    expected_source: dict[str, object] | None = None,
) -> dict[str, object]:
    """Validate one successful, self-digested source-test-wheel receipt."""

    if not isinstance(receipt, dict):
        raise RevisionLineageError("release receipt root is not an object")
    if receipt.get("schema") != RELEASE_RECEIPT_SCHEMA:
        raise RevisionLineageError("release receipt schema is not recognized")
    expected_digest = str(receipt.get("receipt_digest") or "")
    unsigned = dict(receipt)
    unsigned.pop("receipt_digest", None)
    actual_digest = hashlib.sha256(canonical_json_bytes(unsigned)).hexdigest()
    if expected_digest != actual_digest:
        raise RevisionLineageError("release receipt digest mismatch")
    if receipt.get("ok") is not True:
        raise RevisionLineageError("release receipt does not report success")

    source = validate_release_source_descriptor(receipt.get("source"))
    if expected_source is not None and source != expected_source:
        raise RevisionLineageError(
            "release receipt source does not match the declared archive source"
        )

    tests = receipt.get("tests")
    if not isinstance(tests, dict) or tests.get("ok") is not True:
        raise RevisionLineageError("release receipt test lane is not successful")

    wheels = receipt.get("wheels")
    if not isinstance(wheels, dict) or wheels.get("reproducible") is not True:
        raise RevisionLineageError("release receipt does not prove reproducible wheels")
    first = wheels.get("first")
    second = wheels.get("second")
    if not isinstance(first, dict) or not isinstance(second, dict):
        raise RevisionLineageError("release receipt wheel records are absent")
    if first != second:
        raise RevisionLineageError("release receipt wheel records are not identical")
    if first.get("schema") != "micromax.mxrepro.wheel-verification.v1":
        raise RevisionLineageError("release receipt wheel schema is not recognized")
    wheel_name = str(first.get("filename") or "")
    if Path(wheel_name).name != wheel_name or not wheel_name.endswith(".whl"):
        raise RevisionLineageError("release receipt wheel filename is invalid")
    wheel_sha = str(first.get("sha256") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", wheel_sha):
        raise RevisionLineageError("release receipt wheel digest is invalid")
    wheel_bytes = first.get("bytes")
    if (
        not isinstance(wheel_bytes, int)
        or isinstance(wheel_bytes, bool)
        or wheel_bytes <= 0
    ):
        raise RevisionLineageError("release receipt wheel byte count is invalid")
    return receipt


def load_release_receipt(
    path: Path,
    *,
    max_bytes: int = DEFAULT_RELEASE_RECEIPT_MAX_BYTES,
) -> dict[str, object]:
    """Load one bounded regular-file JSON release receipt."""

    data = _read_regular_file(Path(path), max_bytes=int(max_bytes))
    payload = _strict_json_object(
        data,
        label="release receipt",
        error_type=RevisionLineageError,
    )
    return validate_release_receipt(payload)


def _unsafe_member_reason(name: str) -> str | None:
    """Return a human-readable reason when a zip member name is unsafe.

    The project archives are generated with repo-relative POSIX paths.  The
    verifier is deliberately stricter than ``zipfile`` so a future extraction or
    inspection lane cannot accidentally treat absolute paths, parent traversal,
    platform-specific separators, or empty components as ordinary members.
    """

    if not name:
        return "empty member name"
    if "\x00" in name:
        return "NUL byte"
    if "\\" in name:
        return "backslash path separator"
    if name.startswith("/"):
        return "absolute POSIX path"
    if re.match(r"^[A-Za-z]:", name):
        return "drive-qualified path"
    # Inspect raw slash-delimited components before PurePosixPath can normalize
    # away aliases such as ``./a`` or ``a//b``. Archive provenance is keyed by
    # exact names, and future extraction must never see two spellings for one
    # filesystem target.
    if any(part in {"", ".", ".."} for part in name.split("/")):
        return "empty, current, or parent path component"
    path = PurePosixPath(name)
    if path.is_absolute():
        return "absolute path"
    return None


def _manifest_from_zip(zf: zipfile.ZipFile, *, manifest_name: str) -> dict[str, object]:
    try:
        raw = zf.read(manifest_name)
    except KeyError as exc:
        raise ArchiveVerificationError(f"missing archive manifest: {manifest_name}") from exc
    return _strict_json_object(
        raw,
        label=f"archive manifest {manifest_name}",
        error_type=ArchiveVerificationError,
    )


def _read_utf8_member(zf: zipfile.ZipFile, name: str) -> str:
    try:
        raw = zf.read(name)
    except KeyError as exc:
        raise ArchiveVerificationError(f"missing archive lineage source: {name}") from exc
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ArchiveVerificationError(f"archive lineage source is not UTF-8: {name}") from exc


def _archive_revision_lineage(
    zf: zipfile.ZipFile,
    *,
    archive_path: Path,
    manifest: dict[str, object],
) -> dict[str, object]:
    """Verify filename, metadata, context, and source-tree revision agreement."""

    try:
        filename = parse_archive_name(archive_path.name)
    except RevisionLineageError as exc:
        raise ArchiveVerificationError(str(exc)) from exc
    expected = int(filename["revision"])

    archive = manifest.get("archive")
    if not isinstance(archive, dict):
        raise ArchiveVerificationError("manifest archive metadata is absent")
    if str(archive.get("tag") or "") != str(filename["tag"]):
        raise ArchiveVerificationError("manifest archive tag does not match zip filename")
    if str(archive.get("timestamp") or "") != str(filename["timestamp"]):
        raise ArchiveVerificationError("manifest archive timestamp does not match zip filename")
    timezone_name = str(archive.get("timezone") or "")
    try:
        ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ArchiveVerificationError(
            f"manifest archive timezone is invalid: {timezone_name!r}"
        ) from exc
    metadata_revision = archive.get("revision")
    if metadata_revision is not None and metadata_revision != expected:
        raise ArchiveVerificationError(
            f"manifest archive revision {metadata_revision!r} does not match filename revision {expected}"
        )

    context = manifest.get("context")
    if not isinstance(context, dict):
        raise ArchiveVerificationError("manifest context is absent")
    if context.get("project") != "micromax":
        raise ArchiveVerificationError("manifest context project is not micromax")

    revision_index = _strict_json_object(
        _read_utf8_member(zf, "docs/revision-index.json"),
        label="archive revision index",
        error_type=ArchiveVerificationError,
    )
    evidence = _revision_evidence(
        todo_text=_read_utf8_member(zf, "TODO.md"),
        readme_text=_read_utf8_member(zf, "README.md"),
        revision_index=revision_index,
        context=context,
    )
    try:
        revision = _agreed_revision(
            evidence,
            expected=expected,
            required=(
                "TODO.md note",
                "TODO.md heading",
                "README.md note",
                "revision-index current_rev",
                "revision-index head",
                "context rev",
            ),
            prefix="archive",
        )
    except RevisionLineageError as exc:
        raise ArchiveVerificationError(str(exc)) from exc

    context_sources = context.get("revision_sources")
    if isinstance(context_sources, dict):
        if context_sources.get("ok") is not True:
            raise ArchiveVerificationError("manifest context reports inconsistent revision sources")
        for key in (
            "current_rev",
            "todo_first_line_rev",
            "todo_heading_rev",
            "readme_latest_rev",
        ):
            value = context_sources.get(key)
            if isinstance(value, int) and not isinstance(value, bool) and value != revision:
                raise ArchiveVerificationError(
                    f"manifest context {key}={value} does not match archive revision {revision}"
                )
    checks = context.get("checks")
    if isinstance(checks, dict) and checks.get("ok") is not True:
        raise ArchiveVerificationError("manifest context reports failed repository checks")

    return {
        "revision": revision,
        "timestamp": str(filename["timestamp"]),
        "tag": str(filename["tag"]),
        "sources": evidence,
    }


def _zip_member_rows(zf: zipfile.ZipFile, *, manifest_name: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for info in sorted(zf.infolist(), key=lambda item: item.filename):
        name = info.filename
        if name == manifest_name:
            continue
        if info.is_dir():
            raise ArchiveVerificationError(f"unexpected directory member: {name}")
        data = zf.read(info)
        rows.append(
            {
                "path": name,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return rows


def _verify_deterministic_zip_metadata(
    zf: zipfile.ZipFile,
    *,
    manifest_name: str,
    stamp: str,
) -> None:
    """Reject build-host ZIP metadata that would make equal sources differ."""

    infos = zf.infolist()
    names = [info.filename for info in infos]
    if manifest_name not in names:
        raise ArchiveVerificationError(f"missing archive manifest: {manifest_name}")
    expected_order = sorted(name for name in names if name != manifest_name) + [manifest_name]
    if names != expected_order:
        raise ArchiveVerificationError(
            "archive member order is not canonical (sorted source members, manifest last)"
        )
    if zf.comment:
        raise ArchiveVerificationError("archive global comment is not empty")

    expected_time = zip_datetime_from_stamp(stamp)
    expected_external_attr = ZIP_FILE_MODE << 16
    for info in infos:
        name = info.filename
        if info.date_time != expected_time:
            raise ArchiveVerificationError(
                f"archive member timestamp is not normalized to filename stamp: {name}"
            )
        if info.compress_type != zipfile.ZIP_DEFLATED:
            raise ArchiveVerificationError(
                f"archive member compression method is not DEFLATE: {name}"
            )
        if info.create_system != 3:
            raise ArchiveVerificationError(
                f"archive member creator platform is not normalized to Unix: {name}"
            )
        if info.external_attr != expected_external_attr:
            raise ArchiveVerificationError(
                f"archive member mode is not normalized to regular 0644: {name}"
            )
        if info.extra:
            raise ArchiveVerificationError(f"archive member carries noncanonical extra fields: {name}")
        if info.comment:
            raise ArchiveVerificationError(f"archive member comment is not empty: {name}")
        unsupported_flags = info.flag_bits & ~(0x800)
        if unsupported_flags:
            raise ArchiveVerificationError(
                f"archive member carries unsupported general-purpose flags: {name}"
            )


def verify_archive(
    path: Path,
    *,
    manifest_name: str = "MICROMAX-CONTEXT.json",
    max_members: int = DEFAULT_VERIFY_MAX_MEMBERS,
    max_uncompressed_bytes: int = DEFAULT_VERIFY_MAX_UNCOMPRESSED_BYTES,
    max_compressed_bytes: int = DEFAULT_VERIFY_MAX_COMPRESSED_BYTES,
) -> dict[str, object]:
    """Verify an archive against the provenance embedded by ``mkrevzip``.

    Verification consumes the rev0926 provenance instead of merely carrying it:
    it checks zip CRC/header integrity, rejects duplicate or unsafe member names,
    recomputes SHA-256 rows from actual archive bytes, and compares both per-file
    rows and aggregate digest to the manifest.
    """

    archive_path = Path(path)
    try:
        filename_identity = parse_archive_name(archive_path.name)
    except RevisionLineageError as exc:
        raise ArchiveVerificationError(str(exc)) from exc
    with zipfile.ZipFile(archive_path) as zf:
        infos = zf.infolist()
        if len(infos) > max_members:
            raise ArchiveVerificationError(f"archive has too many members: {len(infos)} > {max_members}")
        names = [info.filename for info in infos]
        counts = Counter(names)
        duplicates = sorted(name for name, count in counts.items() if count > 1)
        if duplicates:
            raise ArchiveVerificationError("duplicate archive members: " + ", ".join(duplicates[:5]))
        for info in infos:
            name = info.filename
            reason = _unsafe_member_reason(name)
            if reason is not None:
                raise ArchiveVerificationError(f"unsafe archive member {name!r}: {reason}")
            if info.is_dir():
                raise ArchiveVerificationError(f"unexpected directory member: {name}")
        _verify_deterministic_zip_metadata(
            zf,
            manifest_name=manifest_name,
            stamp=str(filename_identity["timestamp"]),
        )
        total_uncompressed = sum(int(info.file_size) for info in infos)
        total_compressed = sum(int(info.compress_size) for info in infos)
        if total_uncompressed > max_uncompressed_bytes:
            raise ArchiveVerificationError(
                f"archive uncompressed bytes exceed verifier budget: "
                f"{total_uncompressed} > {max_uncompressed_bytes}"
            )
        if total_compressed > max_compressed_bytes:
            raise ArchiveVerificationError(
                f"archive compressed bytes exceed verifier budget: {total_compressed} > {max_compressed_bytes}"
            )

        bad_member = zf.testzip()
        if bad_member is not None:
            raise ArchiveVerificationError(f"zip CRC/header check failed for: {bad_member}")

        manifest = _manifest_from_zip(zf, manifest_name=manifest_name)
        archive = manifest.get("archive")
        if not isinstance(archive, dict):
            raise ArchiveVerificationError("manifest archive metadata is absent")
        if str(archive.get("name") or "") != archive_path.name:
            raise ArchiveVerificationError("manifest archive name does not match zip filename")
        if str(archive.get("context_path") or "") != manifest_name:
            raise ArchiveVerificationError("manifest context_path does not match verifier manifest name")
        lineage = _archive_revision_lineage(
            zf,
            archive_path=archive_path,
            manifest=manifest,
        )
        provenance = archive.get("provenance")
        if not isinstance(provenance, dict):
            raise ArchiveVerificationError("archive provenance is absent")
        if provenance.get("schema") != ARCHIVE_PROVENANCE_SCHEMA:
            raise ArchiveVerificationError("archive provenance schema is not recognized")

        actual_rows = _zip_member_rows(zf, manifest_name=manifest_name)

    expected_entries = provenance.get("entries")
    if not isinstance(expected_entries, list):
        raise ArchiveVerificationError("archive provenance entries are absent")
    expected_rows = [
        {
            "path": str(row.get("path") or ""),
            "bytes": int(row.get("bytes") or 0),
            "sha256": str(row.get("sha256") or ""),
        }
        for row in expected_entries
        if isinstance(row, dict)
    ]
    if len(expected_rows) != len(expected_entries):
        raise ArchiveVerificationError("archive provenance entries contain non-object rows")
    expected_by_path = {str(row["path"]): row for row in expected_rows}
    actual_by_path = {str(row["path"]): row for row in actual_rows}
    if len(expected_by_path) != len(expected_rows):
        raise ArchiveVerificationError("archive provenance contains duplicate paths")
    if expected_by_path != actual_by_path:
        missing = sorted(set(expected_by_path) - set(actual_by_path))
        extra = sorted(set(actual_by_path) - set(expected_by_path))
        changed = sorted(
            path
            for path in set(expected_by_path).intersection(actual_by_path)
            if expected_by_path[path] != actual_by_path[path]
        )
        fragments: list[str] = []
        if missing:
            fragments.append("missing=" + ",".join(missing[:5]))
        if extra:
            fragments.append("extra=" + ",".join(extra[:5]))
        if changed:
            fragments.append("changed=" + ",".join(changed[:5]))
        raise ArchiveVerificationError("archive member provenance mismatch: " + "; ".join(fragments))

    actual_provenance = archive_member_provenance(actual_rows)
    if provenance.get("digest") != actual_provenance["digest"]:
        raise ArchiveVerificationError("archive provenance aggregate digest mismatch")
    if int(provenance.get("file_count") or -1) != actual_provenance["file_count"]:
        raise ArchiveVerificationError("archive provenance file count mismatch")
    if int(provenance.get("total_bytes") or -1) != actual_provenance["total_bytes"]:
        raise ArchiveVerificationError("archive provenance byte total mismatch")

    source_digest: str | None = None
    receipt_digest: str | None = None
    source = manifest.get("source")
    release_evidence = manifest.get("release_evidence")
    if source is not None:
        if not isinstance(source, dict):
            raise ArchiveVerificationError("archive release source is not an object")
        source_epoch = source.get("source_date_epoch")
        if not isinstance(source_epoch, dict):
            raise ArchiveVerificationError("archive release source epoch is absent")
        context = manifest.get("context")
        if not isinstance(context, dict):
            raise ArchiveVerificationError("archive context is absent")
        try:
            expected_source = release_source_descriptor(
                provenance=actual_provenance,
                context=context,
                revision=int(lineage["revision"]),
                context_path=manifest_name,
                source_date_epoch=int(source_epoch.get("value") or 0),
                epoch_origin=str(source_epoch.get("origin") or ""),
            )
        except (RevisionLineageError, TypeError, ValueError) as exc:
            raise ArchiveVerificationError(
                f"archive release source is invalid: {exc}"
            ) from exc
        if source != expected_source:
            raise ArchiveVerificationError(
                "archive release source does not match member provenance and context"
            )
        source_digest = str(expected_source["digest"])
    elif release_evidence is not None:
        raise ArchiveVerificationError(
            "archive release evidence is present without a release source"
        )

    if release_evidence is not None:
        try:
            validated_receipt = validate_release_receipt(
                release_evidence,
                expected_source=source,
            )
        except RevisionLineageError as exc:
            raise ArchiveVerificationError(f"archive release evidence is invalid: {exc}") from exc
        receipt_digest = str(validated_receipt["receipt_digest"])

    result: dict[str, object] = {
        "schema": ARCHIVE_VERIFICATION_SCHEMA,
        "ok": True,
        "archive": archive_path.name,
        "manifest": manifest_name,
        "revision": lineage["revision"],
        "timestamp": lineage["timestamp"],
        "tag": lineage["tag"],
        "revision_sources": lineage["sources"],
        "file_count": actual_provenance["file_count"],
        "total_bytes": actual_provenance["total_bytes"],
        "digest": actual_provenance["digest"],
    }
    if source_digest is not None:
        result["source_digest"] = source_digest
    if receipt_digest is not None:
        result["release_receipt_digest"] = receipt_digest
    return result


def _read_regular_file(path: Path, *, max_bytes: int | None = None) -> bytes:
    """Read one regular file without following a final-component symlink.

    ``max_bytes`` retains at most one over-limit witness byte, so externally
    supplied release receipts are refused before an unbounded allocation.
    """

    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        if path.is_symlink():
            raise RevisionLineageError(f"package member is a symbolic link: {path}") from exc
        raise
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise RevisionLineageError(f"package member is not a regular file: {path}")
        chunks: list[bytes] = []
        total = 0
        while True:
            if max_bytes is None:
                request = 1024 * 1024
            else:
                remaining = int(max_bytes) + 1 - total
                if remaining <= 0:
                    break
                request = min(1024 * 1024, remaining)
            block = os.read(fd, request)
            if not block:
                break
            chunks.append(block)
            total += len(block)
        data = b"".join(chunks)
        if max_bytes is not None and len(data) > int(max_bytes):
            raise RevisionLineageError(
                f"regular file exceeds byte budget: {len(data)} > {int(max_bytes)}"
            )
        return data
    finally:
        os.close(fd)


def archive_member_rows(root: Path, *, manifest_rel: Path) -> list[dict[str, object]]:
    """Return a content snapshot of every source member intended for the zip."""

    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if rel == manifest_rel or should_skip(rel):
            continue
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError as exc:
            raise RevisionLineageError(
                f"source tree changed while enumerating package members: {rel.as_posix()}"
            ) from exc
        if stat.S_ISDIR(mode):
            continue
        if stat.S_ISLNK(mode):
            raise RevisionLineageError(
                f"package member is a symbolic link: {rel.as_posix()}"
            )
        if not stat.S_ISREG(mode):
            raise RevisionLineageError(
                f"package member is not a regular file: {rel.as_posix()}"
            )
        data = _read_regular_file(path)
        if is_revision_evidence_artifact(rel):
            if len(data) > REVISION_EVIDENCE_ARTIFACT_MAX_BYTES:
                raise RevisionLineageError(
                    "revision evidence artifact exceeds byte budget: "
                    f"{rel.as_posix()} {len(data)} > "
                    f"{REVISION_EVIDENCE_ARTIFACT_MAX_BYTES}"
                )
            _strict_json_object(
                data,
                label=f"revision evidence artifact {rel.as_posix()}",
                error_type=RevisionLineageError,
            )
        rows.append(
            {
                "path": rel.as_posix(),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return rows


def _rows_by_path(rows: list[dict[str, object]]) -> dict[str, tuple[int, str]]:
    result: dict[str, tuple[int, str]] = {}
    for row in rows:
        path = str(row.get("path") or "")
        if not path or path in result:
            raise RevisionLineageError("package member snapshot contains duplicate or empty paths")
        result[path] = (int(row.get("bytes") or 0), str(row.get("sha256") or ""))
    return result


def assert_source_tree_unchanged(
    root: Path,
    *,
    manifest_rel: Path,
    expected_rows: list[dict[str, object]],
    phase: str,
) -> None:
    """Fail packaging when source membership or bytes changed mid-build."""

    expected = _rows_by_path(expected_rows)
    actual = _rows_by_path(archive_member_rows(root, manifest_rel=manifest_rel))
    if actual == expected:
        return
    missing = sorted(set(expected) - set(actual))
    added = sorted(set(actual) - set(expected))
    changed = sorted(path for path in set(expected) & set(actual) if expected[path] != actual[path])
    details: list[str] = []
    if missing:
        details.append("removed=" + ",".join(missing[:5]))
    if added:
        details.append("added=" + ",".join(added[:5]))
    if changed:
        details.append("changed=" + ",".join(changed[:5]))
    raise RevisionLineageError(
        f"source tree changed during {phase}; refusing a mixed-generation archive"
        + (": " + "; ".join(details) if details else "")
    )


def snapshot_archive_members(
    root: Path,
    snapshot_root: Path,
    rows: list[dict[str, object]],
) -> None:
    """Copy verified package bytes into an immutable build-local snapshot."""

    snapshot_root.mkdir(parents=True, exist_ok=False)
    os.chmod(snapshot_root, SNAPSHOT_DIR_MODE)
    for row in rows:
        rel = Path(str(row.get("path") or ""))
        reason = _unsafe_member_reason(rel.as_posix())
        if reason is not None:
            raise RevisionLineageError(f"unsafe package member {rel.as_posix()!r}: {reason}")
        data = _read_regular_file(root / rel)
        expected_size = int(row.get("bytes") or 0)
        expected_sha = str(row.get("sha256") or "")
        if len(data) != expected_size or hashlib.sha256(data).hexdigest() != expected_sha:
            raise RevisionLineageError(
                f"source tree changed while snapshotting {rel.as_posix()}; "
                "refusing a mixed-generation archive"
            )
        destination = snapshot_root / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        # Source permissions are not part of the byte snapshot.  Normalize them
        # explicitly so caller umask and hand-carried archive modes cannot leak
        # into wheel member metadata.
        os.chmod(destination, SNAPSHOT_FILE_MODE)

    # ``mkdir`` respects the process umask.  Set every materialized directory to
    # one declared traversal mode after the complete tree exists.
    for directory in sorted(
        (path for path in snapshot_root.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    ):
        os.chmod(directory, SNAPSHOT_DIR_MODE)
    os.chmod(snapshot_root, SNAPSHOT_DIR_MODE)


def zip_datetime_from_stamp(stamp: str) -> tuple[int, int, int, int, int, int]:
    """Return one canonical ZIP timestamp derived from the archive filename."""

    probe = parse_archive_name(
        f"Micromax-rev0000-{str(stamp)}-timestamp-probe.zip"
    )
    parsed = datetime.strptime(str(probe["timestamp"]), "%Y.%m.%d.%H.%M")
    return (parsed.year, parsed.month, parsed.day, parsed.hour, parsed.minute, 0)


def deterministic_zip_info(name: str, *, stamp: str) -> zipfile.ZipInfo:
    """Return normalized regular-file metadata for one archive member."""

    reason = _unsafe_member_reason(name)
    if reason is not None:
        raise RevisionLineageError(f"unsafe package member {name!r}: {reason}")
    info = zipfile.ZipInfo(filename=name, date_time=zip_datetime_from_stamp(stamp))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = ZIP_FILE_MODE << 16
    return info


def write_deterministic_archive(
    path: Path,
    *,
    snapshot_root: Path,
    member_rows: list[dict[str, object]],
    manifest_name: str,
    manifest: dict[str, object],
    stamp: str,
) -> None:
    """Write a revision ZIP without source/build mtime or mode leakage."""

    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with zipfile.ZipFile(
        path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=ZIP_COMPRESSION_LEVEL,
    ) as archive:
        for row in member_rows:
            rel = Path(str(row.get("path") or ""))
            if not str(rel):
                continue
            data = _read_regular_file(snapshot_root / rel)
            expected_size = int(row.get("bytes") or 0)
            expected_sha = str(row.get("sha256") or "")
            if len(data) != expected_size or hashlib.sha256(data).hexdigest() != expected_sha:
                raise RevisionLineageError(
                    f"source snapshot changed while writing {rel.as_posix()}"
                )
            archive.writestr(
                deterministic_zip_info(rel.as_posix(), stamp=stamp),
                data,
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=ZIP_COMPRESSION_LEVEL,
            )
        archive.writestr(
            deterministic_zip_info(manifest_name, stamp=stamp),
            manifest_bytes,
            compress_type=zipfile.ZIP_DEFLATED,
            compresslevel=ZIP_COMPRESSION_LEVEL,
        )


def archive_member_provenance(rows: list[dict[str, object]]) -> dict[str, object]:
    """Return a compact digest over the archive member list."""

    h = hashlib.sha256()
    total_bytes = 0
    normalized: list[dict[str, object]] = []
    for row in sorted(rows, key=lambda item: str(item.get("path") or "")):
        path = str(row.get("path") or "")
        byte_count = int(row.get("bytes") or 0)
        sha = str(row.get("sha256") or "")
        total_bytes += byte_count
        h.update(sha.encode("ascii", errors="ignore"))
        h.update(b" ")
        h.update(str(byte_count).encode("ascii"))
        h.update(b" ")
        h.update(path.encode("utf-8"))
        h.update(b"\n")
        normalized.append({"path": path, "bytes": byte_count, "sha256": sha})
    return {
        "schema": ARCHIVE_PROVENANCE_SCHEMA,
        "digest": h.hexdigest(),
        "file_count": len(normalized),
        "total_bytes": total_bytes,
        "entries": normalized,
    }




def package_input_snapshot(root: Path) -> dict[str, object]:
    """Return the release package/dependency input policy report, fail-closed."""

    try:
        from mxrelease import package_input_report

        report = package_input_report(root)
        return report if isinstance(report, dict) else {"schema": "unknown", "ok": False}
    except Exception as exc:
        return {
            "schema": "micromax.mxrelease.package-inputs.v1",
            "ok": False,
            "error": str(exc),
        }

def archive_manifest(
    *,
    root: Path,
    rev: int,
    archive_name: str,
    tag: str,
    stamp: str,
    tz_name: str,
    manifest_name: str,
    provenance: dict[str, object] | None = None,
    source_date_epoch: int | None = None,
    epoch_origin: str = "archive-stamp",
    release_evidence: dict[str, object] | None = None,
) -> dict[str, object]:
    context = context_snapshot(root, rev=rev)
    epoch = (
        archive_stamp_epoch(stamp, tz_name)
        if source_date_epoch is None
        else int(source_date_epoch)
    )
    archive = {
        "name": archive_name,
        "revision": int(rev),
        "tag": tag,
        "timestamp": stamp,
        "timezone": tz_name,
        "context_path": manifest_name,
        "created_by": "tools/mkrevzip.py",
        "source_date_epoch": epoch,
    }
    if provenance is not None:
        archive["provenance"] = provenance
    manifest: dict[str, object] = {
        "archive": archive,
        "package_inputs": package_input_snapshot(root),
        "context": context,
    }
    if provenance is not None:
        source = release_source_descriptor(
            provenance=provenance,
            context=context,
            revision=rev,
            context_path=manifest_name,
            source_date_epoch=epoch,
            epoch_origin=epoch_origin,
        )
        manifest["source"] = source
        if release_evidence is not None:
            manifest["release_evidence"] = validate_release_receipt(
                release_evidence,
                expected_source=source,
            )
    elif release_evidence is not None:
        raise RevisionLineageError(
            "release evidence requires archive member provenance"
        )
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", help="hyphenated archive tag (include a codename at end)")
    ap.add_argument("--verify-archive", default=None, help="verify an existing rev zip against its embedded provenance")
    ap.add_argument("--verify-json", action="store_true", help="emit JSON for --verify-archive")
    ap.add_argument("--outdir", default=".", help="output directory (default: repo root)")
    ap.add_argument("--tz", default="America/New_York", help="IANA timezone for timestamp")
    ap.add_argument(
        "--rev",
        type=int,
        default=None,
        help="assert the expected rev (must match every repository breadcrumb)",
    )
    ap.add_argument("--stamp", default=None, help="override timestamp (YYYY.MM.DD.HH.MM) for deterministic packaging/tests")
    ap.add_argument(
        "--manifest-name",
        default="MICROMAX-CONTEXT.json",
        help="archive-internal context snapshot filename (default: MICROMAX-CONTEXT.json)",
    )
    ap.add_argument(
        "--release-receipt",
        default=None,
        help=(
            "successful micromax.release-receipt.v1 JSON whose declared source "
            "must match this archive"
        ),
    )
    args = ap.parse_args()

    if args.verify_archive:
        try:
            result = verify_archive(Path(str(args.verify_archive)), manifest_name=str(args.manifest_name))
        except (OSError, zipfile.BadZipFile, ArchiveVerificationError) as exc:
            if args.verify_json:
                print(json.dumps({"schema": ARCHIVE_VERIFICATION_SCHEMA, "ok": False, "error": str(exc)}, sort_keys=True))
            else:
                print(f"archive verification failed: {exc}", file=sys.stderr)
            raise SystemExit(1)
        if args.verify_json:
            print(json.dumps(result, sort_keys=True))
        else:
            print(f"archive verification ok: {result['archive']} files={result['file_count']} digest={result['digest']}")
        return

    if not args.tag:
        ap.error("--tag is required unless --verify-archive is used")

    root = Path(__file__).resolve().parents[1]
    try:
        inferred_rev = infer_rev(root)
        if args.rev is not None and int(args.rev) != inferred_rev:
            raise RevisionLineageError(
                f"requested revision {int(args.rev)} does not match repository revision {inferred_rev}"
            )
        rev = inferred_rev
        timezone_name = str(args.tz)
        try:
            timezone = ZoneInfo(timezone_name)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise RevisionLineageError(f"archive timezone is invalid: {timezone_name!r}") from exc
        stamp = (
            str(args.stamp)
            if args.stamp
            else datetime.now(tz=timezone).strftime("%Y.%m.%d.%H.%M")
        )
        tag = str(args.tag).strip()
        name = f"Micromax-rev{rev:04d}-{stamp}-{tag}.zip"
        parse_archive_name(name)
        manifest_name = str(args.manifest_name).strip() or "MICROMAX-CONTEXT.json"
        reason = _unsafe_member_reason(manifest_name)
        if reason is not None:
            raise RevisionLineageError(f"unsafe manifest name {manifest_name!r}: {reason}")
        if manifest_name in {"README.md", "TODO.md", "docs/revision-index.json"}:
            raise RevisionLineageError(
                f"manifest name collides with required revision source: {manifest_name}"
            )
    except (RevisionLineageError, OSError) as exc:
        print(f"archive generation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)

    outdir = (root / str(args.outdir)).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / name
    if outpath.exists():
        print(f"archive generation failed: refusing to overwrite {outpath}", file=sys.stderr)
        raise SystemExit(1)
    manifest_rel = Path(manifest_name)
    member_rows = archive_member_rows(root, manifest_rel=manifest_rel)
    try:
        provenance = archive_member_provenance(member_rows)
        release_receipt = (
            load_release_receipt(Path(str(args.release_receipt)).resolve())
            if args.release_receipt
            else None
        )
        if release_receipt is not None:
            receipt_source = release_receipt.get("source")
            assert isinstance(receipt_source, dict)
            receipt_epoch = receipt_source.get("source_date_epoch")
            assert isinstance(receipt_epoch, dict)
            source_date_epoch = int(receipt_epoch.get("value") or 0)
            epoch_origin = str(receipt_epoch.get("origin") or "")
        else:
            source_date_epoch = archive_stamp_epoch(stamp, str(args.tz))
            epoch_origin = "archive-stamp"
        manifest = archive_manifest(
            root=root,
            rev=rev,
            archive_name=name,
            tag=tag,
            stamp=stamp,
            tz_name=str(args.tz),
            manifest_name=manifest_name,
            provenance=provenance,
            source_date_epoch=source_date_epoch,
            epoch_origin=epoch_origin,
            release_evidence=release_receipt,
        )
        assert_source_tree_unchanged(
            root,
            manifest_rel=manifest_rel,
            expected_rows=member_rows,
            phase="manifest generation",
        )
        with tempfile.TemporaryDirectory(prefix=".tmp-mkrevzip-", dir=outdir) as tmp:
            build_root = Path(tmp)
            snapshot_root = build_root / "source-snapshot"
            snapshot_archive_members(root, snapshot_root, member_rows)
            assert_source_tree_unchanged(
                root,
                manifest_rel=manifest_rel,
                expected_rows=member_rows,
                phase="source snapshot",
            )
            candidate = build_root / name
            write_deterministic_archive(
                candidate,
                snapshot_root=snapshot_root,
                member_rows=member_rows,
                manifest_name=manifest_name,
                manifest=manifest,
                stamp=stamp,
            )
            verify_archive(candidate, manifest_name=manifest_name)
            assert_source_tree_unchanged(
                root,
                manifest_rel=manifest_rel,
                expected_rows=member_rows,
                phase="archive verification",
            )
            os.replace(candidate, outpath)
    except (OSError, zipfile.BadZipFile, RevisionLineageError, ArchiveVerificationError) as exc:
        print(f"archive generation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print(str(outpath))


if __name__ == "__main__":
    main()
