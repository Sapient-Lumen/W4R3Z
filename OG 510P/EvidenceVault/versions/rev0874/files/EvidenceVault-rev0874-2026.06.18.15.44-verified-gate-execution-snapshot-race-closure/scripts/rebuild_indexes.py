#!/usr/bin/env python3
"""Rebuild INDEX/files.{json,csv} and MANIFEST.sha256 for EvidenceVault.

Design goal: produce a stable MANIFEST that covers all files (except itself) without
self-referential hash loops.

- INDEX lists *all files except* MANIFEST.sha256 and INDEX/files.{json,csv}.
  (Those two index files are convenience outputs; including them inside INDEX would
  require a self-referential fixed point.)
- MANIFEST.sha256 lists sha256 and relative path for every file *except* MANIFEST.sha256.

Usage:
  python3 scripts/rebuild_indexes.py
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
INDEX_DIR = ROOT / "INDEX"
EXTRACTION_MAP = ROOT / "papers" / "EXTRACTION_MAP.json"
CORE_JSONS = [
    EXTRACTION_MAP,
    ROOT / "OPENING_CONTRACT.json",
    ROOT / "CURRENT_FRONTIER.json",
    ROOT / "SOURCE_INDEX.json",
    ROOT / "OPENING_SURFACE_CONFORMANCE.json",
    ROOT / "REVISION_RECEIPT.json",
    ROOT / "VALIDATION_INDEX.json",
    ROOT / "CLAIM_OBLIGATION_MAP.json",
    ROOT / "RFC_INDEX.json",
    ROOT / "CONTROL_SURFACES.json",
    ROOT / "LIFECYCLE_GATES.json",
    ROOT / "RELEASE_MANIFEST.json",
    ROOT / "ARCHIVE_INDEX.json",
    ROOT / "TOOLCHAIN_LOCK.json",
    ROOT / "COMMAND_RUNNER_SEQUENCE.json",
    ROOT / "publishing" / "CANONICAL_POLICY.json",
]

EXCLUDE_FROM_INDEX = {
    "MANIFEST.sha256",
    "INDEX/files.json",
    "INDEX/files.csv",
}
EXCLUDE_FROM_MANIFEST = {"MANIFEST.sha256"}
PY_MODULE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _path_parts_relative_to_root(root: Path, path: Path) -> tuple[str, ...] | None:
    try:
        return path.relative_to(root).parts
    except ValueError:
        try:
            return path.resolve(strict=False).relative_to(root.resolve()).parts
        except ValueError:
            return None


def first_symlink_component(root: Path, path: Path) -> Path | None:
    """Return the first symlink component under root, if any."""
    parts = _path_parts_relative_to_root(root, path)
    if parts is None:
        return path if path.is_symlink() else None
    cursor = root
    if root.is_symlink():
        return root
    for part in parts:
        cursor = cursor / part
        if cursor.is_symlink():
            return cursor
    return None


def fsync_directory(path: Path) -> None:
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def prepare_generated_output_path(path: Path, label: str) -> None:
    """Reject generated-output destinations outside ROOT or through symlinks."""
    if _path_parts_relative_to_root(ROOT, path) is None:
        raise RuntimeError(f"{label} generated output escapes archive root: {path}")
    symlink = first_symlink_component(ROOT, path)
    if symlink is not None:
        raise RuntimeError(f"{label} generated output resolves through a symlink component: {_rel_for_error(ROOT, symlink)}")
    if path.exists() and path.is_dir():
        raise RuntimeError(f"{label} generated output path is a directory: {_rel_for_error(ROOT, path)}")
    if path.parent.exists() and not path.parent.is_dir():
        raise RuntimeError(f"{label} generated output parent is not a directory: {_rel_for_error(ROOT, path.parent)}")


def atomic_write_bytes(path: Path, payload: bytes, *, label: str) -> None:
    """Atomically replace a generated release-critical surface."""
    prepare_generated_output_path(path, label)
    path.parent.mkdir(parents=True, exist_ok=True)
    prepare_generated_output_path(path, label)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    committed = False
    try:
        with os.fdopen(fd, "wb") as f:
            os.fchmod(f.fileno(), 0o644)
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
        committed = True
        fsync_directory(path.parent)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
        if committed:
            fsync_directory(path.parent)


def atomic_write_text(path: Path, text: str, *, label: str) -> None:
    atomic_write_bytes(path, text.encode("utf-8"), label=label)


def atomic_write_json(path: Path, data: Any, *, label: str) -> None:
    atomic_write_text(path, json.dumps(data, indent=2) + "\n", label=label)


def _rel_for_error(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def collect_regular_archive_files(root: Path) -> list[Path]:
    """Return regular files under root and fail closed on symlink boundaries.

    Generated indexes and manifests are release-critical digest surfaces.  They
    must not follow archive-internal symlinks into host/cloudtainer paths or
    silently digest mutable link targets.
    """
    root = root.resolve()
    if root.is_symlink():
        raise RuntimeError(f"archive root must not be a symlink: {root}")
    files: list[Path] = []
    symlinks: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        directory = Path(dirpath)
        for name in list(dirnames):
            child = directory / name
            if child.is_symlink():
                symlinks.append(_rel_for_error(root, child))
                dirnames.remove(name)
        for name in filenames:
            child = directory / name
            if child.is_symlink():
                symlinks.append(_rel_for_error(root, child))
                continue
            if child.is_file():
                files.append(child)
    if symlinks:
        shown = ", ".join(symlinks[:10])
        suffix = "" if len(symlinks) <= 10 else f"; +{len(symlinks) - 10} more"
        raise RuntimeError(f"refusing to index symlink paths: {shown}{suffix}")
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def require_regular_file(path: Path, label: str | None = None) -> None:
    """Require an archive-local regular file with no symlinked components.

    Rebuild-indexes reads several metadata files before the final full-tree
    symlink scan runs.  This helper is therefore used by hash and JSON readers so
    release-critical metadata cannot be read through host/cloudtainer symlink
    boundaries during the earlier refresh phases.
    """
    label_text = label or _rel_for_error(ROOT, path)
    symlink = first_symlink_component(ROOT, path)
    if symlink is not None:
        raise RuntimeError(f"{label_text} resolves through a symlink component: {_rel_for_error(ROOT, symlink)}")
    try:
        path.resolve(strict=False).relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"{label_text} escapes archive root: {path}") from exc
    if not path.is_file():
        raise RuntimeError(f"{label_text} must be a regular file")


def read_text_file(path: Path, label: str | None = None) -> str:
    require_regular_file(path, label)
    return path.read_text(encoding="utf-8")


def load_json_file(path: Path, label: str | None = None) -> Any:
    label_text = label or _rel_for_error(ROOT, path)
    try:
        data = json.loads(read_text_file(path, label_text))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label_text} is not valid JSON: {exc}") from exc
    return data


def sha256_file(p: Path) -> str:
    require_regular_file(p)
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def file_count(root: Path) -> int:
    return len(collect_regular_archive_files(root))


def refresh_release_manifest_identity() -> None:
    """Refresh release identity digests before rebuilding INDEX/MANIFEST.

    This keeps `make gate` and `make rebuild-indexes` from leaving a stale
    RELEASE_MANIFEST.json digest row after revision metadata or generated
    source-index surfaces change.
    """
    path = ROOT / "RELEASE_MANIFEST.json"
    data = load_json_file(path, "RELEASE_MANIFEST.json")
    data["repo_root"] = ROOT.name
    data["file_count"] = file_count(ROOT)
    data["identity_digests"] = {
        "revision_receipt_sha256": sha256_file(ROOT / data["revision_receipt"]),
        "opening_contract_sha256": sha256_file(ROOT / data["opening_contract"]),
        "revision_anchors_sha256": sha256_file(ROOT / data["revision_anchors"]),
        "context_pack_sha256": sha256_file(ROOT / "CONTEXT_PACK.json"),
        "agents_sha256": sha256_file(ROOT / data["agent_contract"]),
        "makefile_sha256": sha256_file(ROOT / data["command_surface"]),
        "source_index_json_sha256": sha256_file(ROOT / data["source_index_json"]),
        "current_frontier_json_sha256": sha256_file(ROOT / data["current_frontier_json"]),
        "validation_index_json_sha256": sha256_file(ROOT / data["validation_index_json"]),
        "assimilation_ledger_json_sha256": sha256_file(ROOT / "ASSIMILATION_LEDGER.json"),
        "adr_index_json_sha256": sha256_file(ROOT / data["adr_index_json"]),
        "rfc_index_json_sha256": sha256_file(ROOT / data["rfc_index_json"]),
        "archive_index_json_sha256": sha256_file(ROOT / data["archive_index_json"]),
        "control_surfaces_sha256": sha256_file(ROOT / "CONTROL_SURFACES.json"),
        "lifecycle_gates_sha256": sha256_file(ROOT / "LIFECYCLE_GATES.json"),
        "artifact_index_json_sha256": sha256_file(ROOT / "artifacts" / "ARTIFACTS_INDEX.json"),
        "cert_index_json_sha256": sha256_file(ROOT / "certs" / "CERTS_INDEX.json"),
        "toolchain_lock_json_sha256": sha256_file(ROOT / "TOOLCHAIN_LOCK.json"),
        "claim_obligation_map_json_sha256": sha256_file(ROOT / "CLAIM_OBLIGATION_MAP.json"),
        "public_status_json_sha256": sha256_file(ROOT / "PUBLIC_STATUS.json"),
        "command_runner_sequence_json_sha256": sha256_file(ROOT / "COMMAND_RUNNER_SEQUENCE.json"),
        "release_artifact_verifier_sha256": sha256_file(ROOT / data["release_artifact_verifier"]),
        "release_artifact_verifier_validator_sha256": sha256_file(ROOT / data["release_artifact_verifier_validator"]),
        "release_manifest_schema_sha256": sha256_file(ROOT / data["release_manifest_schema"]),
        "archive_identity_validator_sha256": sha256_file(ROOT / data["archive_identity_validator"]),
        "ro_crate_metadata_schema_sha256": sha256_file(ROOT / data["ro_crate_metadata_schema"]),
        "ro_crate_metadata_validator_sha256": sha256_file(ROOT / data["ro_crate_metadata_validator"]),
    }
    atomic_write_json(path, data, label="RELEASE_MANIFEST.json")



RO_CRATE_REQUIRED_HAS_PARTS = [
    'RELEASE_MANIFEST.json',
    'REVISION_RECEIPT.json',
    'REVISION_ANCHORS.json',
    'VALIDATION_INDEX.json',
    'CLAIM_OBLIGATION_MAP.json',
    'PUBLIC_STATUS.json',
    'TOOLCHAIN_LOCK.json',
    'COMMAND_RUNNER_SEQUENCE.json',
    'SOURCE_INDEX.json',
    'ARCHIVE_INDEX.json',
    'CONTROL_SURFACES.json',
    'LIFECYCLE_GATES.json',
    'papers/EXTRACTION_MAP.json',
    'published/PUBLIC_SURFACE.json',
    'MANIFEST.sha256',
    'INDEX/files.json',
    'ev_acceptability_kernel.pdf',
    'ev_interpretation_profiles.pdf',
    'ev_streamfold.pdf',
    'ev_zkrtp.pdf',
    'ev_pact_ocf.pdf',
    'sources/',
    'artifacts/',
    'certs/',
    'published/',
]
RO_CRATE_DIGESTED_FILE_ENTITIES = [
    'RELEASE_MANIFEST.json',
    'REVISION_RECEIPT.json',
    'REVISION_ANCHORS.json',
    'VALIDATION_INDEX.json',
    'CLAIM_OBLIGATION_MAP.json',
    'PUBLIC_STATUS.json',
    'TOOLCHAIN_LOCK.json',
    'COMMAND_RUNNER_SEQUENCE.json',
    'SOURCE_INDEX.json',
    'ARCHIVE_INDEX.json',
    'CONTROL_SURFACES.json',
    'LIFECYCLE_GATES.json',
    'papers/EXTRACTION_MAP.json',
    'published/PUBLIC_SURFACE.json',
    'ev_acceptability_kernel.pdf',
    'ev_interpretation_profiles.pdf',
    'ev_streamfold.pdf',
    'ev_zkrtp.pdf',
    'ev_pact_ocf.pdf',
]


def refresh_ro_crate_metadata() -> None:
    """Refresh the RO-Crate bridge after release-manifest identity moves.

    The RO-Crate bridge carries digests for selected governance files, including
    RELEASE_MANIFEST.json.  Refresh it here so rebuild-indexes cannot leave the
    external research-object bridge stale after identity digests are rewritten.
    """
    path = ROOT / 'ro-crate-metadata.json'
    if not path.exists():
        return
    crate = load_json_file(path, 'ro-crate-metadata.json')
    graph = crate.get('@graph', [])
    entities = {entity.get('@id'): entity for entity in graph if isinstance(entity, dict)}
    receipt = load_json_file(ROOT / 'REVISION_RECEIPT.json', 'REVISION_RECEIPT.json')
    manifest = load_json_file(ROOT / 'RELEASE_MANIFEST.json', 'RELEASE_MANIFEST.json')
    root = entities.get('./')
    if isinstance(root, dict):
        root['name'] = f"EvidenceVault {receipt['revision']}"
        root['version'] = receipt['revision']
        root['identifier'] = manifest['archive_name']
        root['datePublished'] = receipt['date']
        root['hasPart'] = [{'@id': rel} for rel in RO_CRATE_REQUIRED_HAS_PARTS]
    for rel in RO_CRATE_REQUIRED_HAS_PARTS:
        if rel not in entities:
            ent = {'@id': rel, '@type': 'Dataset' if rel.endswith('/') else 'File', 'name': rel.rstrip('/')}
            graph.append(ent)
            entities[rel] = ent
    for rel in RO_CRATE_DIGESTED_FILE_ENTITIES:
        ent = entities[rel]
        target = ROOT / rel
        require_regular_file(target, f"RO-Crate digested entity {rel}")
        ent['@type'] = 'File'
        ent['contentSize'] = str(target.stat().st_size)
        ent['sha256'] = sha256_file(target)
        ent.setdefault('encodingFormat', 'application/json' if rel.endswith('.json') else 'application/pdf' if rel.endswith('.pdf') else 'text/plain')
    for rel in ('MANIFEST.sha256', 'INDEX/files.json'):
        ent = entities.get(rel)
        if isinstance(ent, dict):
            ent.pop('sha256', None)
            ent.pop('contentSize', None)
    atomic_write_json(path, crate, label='ro-crate-metadata.json')
    try:
        from validate_ro_crate_metadata import render_markdown
        atomic_write_text(ROOT / 'RO_CRATE_PROFILE.md', render_markdown(crate), label='RO_CRATE_PROFILE.md')
    except Exception as exc:
        raise RuntimeError(f'failed to refresh RO_CRATE_PROFILE.md: {exc}') from exc



def archive_python_script_path(module_name: str) -> Path:
    """Return an archive-local, non-symlink Python helper script path."""
    if not PY_MODULE_RE.match(module_name):
        raise RuntimeError(f"unsafe material builder module name: {module_name!r}")
    script = ROOT / "scripts" / f"{module_name}.py"
    symlink = first_symlink_component(ROOT, script)
    if symlink is not None:
        raise RuntimeError(f"material builder resolves through a symlink component: {_rel_for_error(ROOT, symlink)}")
    try:
        script.resolve(strict=False).relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"material builder escapes archive root: {module_name}.py") from exc
    if not script.is_file():
        raise RuntimeError(f"material builder is missing or not a regular file: scripts/{module_name}.py")
    return script


def run_material_builder_subprocess(module_name: str) -> None:
    """Run one material-surface builder in an isolated Python subprocess."""
    script = archive_python_script_path(module_name)
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    print(f"rebuild-indexes: refreshing {module_name}.py", flush=True)
    result = subprocess.run([sys.executable, "-u", str(script)], cwd=ROOT, env=env, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"{module_name}.py returned non-zero status {result.returncode}")




def _require_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        data = load_json_file(path, f"{label} output {path.relative_to(ROOT).as_posix()}")
    except Exception as exc:
        raise RuntimeError(f"{label} did not emit valid JSON at {path.relative_to(ROOT).as_posix()}: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"{label} emitted non-object JSON at {path.relative_to(ROOT).as_posix()}")
    return data


def refresh_source_index_subprocess() -> None:
    """Refresh SOURCE_INDEX surfaces through a subprocess and JSON handoff.

    build_source_index.py owns SOURCE_INDEX.json and SOURCE_INDEX.md rendering.
    rebuild_indexes.py only coordinates the build and validates that the child
    process produced a parseable JSON object plus the markdown companion before
    continuing to expensive downstream refreshes.
    """
    run_material_builder_subprocess("build_source_index")
    source_json = ROOT / "SOURCE_INDEX.json"
    source_md = ROOT / "SOURCE_INDEX.md"
    data = _require_json_object(source_json, "build_source_index.py")
    if not source_md.is_file():
        raise RuntimeError("build_source_index.py did not emit SOURCE_INDEX.md")
    if source_md.stat().st_size <= 0:
        raise RuntimeError("build_source_index.py emitted empty SOURCE_INDEX.md")
    if not data:
        raise RuntimeError("build_source_index.py emitted empty SOURCE_INDEX.json")


def refresh_cycle_safe_material_surfaces() -> None:
    """Refresh generated audit/rights/SBOM surfaces before final INDEX/MANIFEST.

    These surfaces are content-derived and should not rot during the normal
    release refresh path. They intentionally exclude MANIFEST.sha256 and
    INDEX/files.* where needed, so running them before final index/manifest
    emission does not create a digest fixed-point problem.
    """
    builders = [
        # Asset indexes are release-identity inputs, so refresh them before
        # RELEASE_MANIFEST.json identity digests are recomputed.
        ("build_asset_indexes", "main"),
        ("build_release_refresh_asset_index_audit_rev0834", "main"),
        ("build_upstream_retention_coverage", "main"),
        ("build_absolute_path_reference_audit", "main"),
        ("build_path_reference_shape_audit", "main"),
        ("build_external_license_evidence_candidates_rev0834", "main"),
        ("build_rights_evidence_scan", "main"),
        ("build_license_reference_integrity_audit", "main"),
        ("build_rights_readiness", "main"),
        ("build_publication_rights_gate_audit_rev0837", "main"),
        ("build_publication_entrypoint_rights_gate_audit_rev0838", "main"),
        ("build_publication_state_transition_rights_gate_audit_rev0839", "main"),
        ("build_publication_preflight_dry_run_safety_audit_rev0840", "main"),
        ("build_rebuild_indexes_subprocess_refresh_audit_rev0839", "main"),
    ]
    for module_name, entrypoint in builders:
        if entrypoint != "main":
            raise RuntimeError(f"unsupported material-surface entrypoint for subprocess refresh: {module_name}.{entrypoint}")
        run_material_builder_subprocess(module_name)

def classify(rel_path: str) -> tuple[str, str, str]:
    parts = rel_path.split("/")
    if len(parts) == 1:
        category = parts[0]
        project = ""
    else:
        category = parts[0]
        project = parts[1] if len(parts) > 1 else ""
    ext = Path(rel_path).suffix.lower()
    return category, project, ext


def _walk_strings(x):
    if isinstance(x, dict):
        for v in x.values():
            yield from _walk_strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from _walk_strings(v)
    elif isinstance(x, str):
        yield x


def validate_metadata() -> None:
    """Fail fast if core machine-readable metadata is malformed or semantically corrupted."""
    for path in CORE_JSONS:
        data = load_json_file(path, path.relative_to(ROOT).as_posix())
        for s in _walk_strings(data):
            bad = [c for c in s if ord(c) < 32 and c not in "\n"]
            if bad:
                codes = ", ".join(str(ord(c)) for c in sorted(set(bad)))
                raise ValueError(f"{path} contains control characters in parsed strings: {codes}")


def main() -> None:
    # Refresh governed source inventory in a child interpreter, then consume the
    # emitted SOURCE_INDEX.json as the handoff contract.  This keeps the rebuild
    # coordinator from importing build_source_index.py and sharing its module
    # state with later material-surface refreshes.
    refresh_source_index_subprocess()

    # Refresh all content-derived surfaces before identity digests.  Asset
    # indexes are among those surfaces, and RELEASE_MANIFEST.json carries their
    # digests as archive-identity inputs.
    refresh_cycle_safe_material_surfaces()
    validate_metadata()
    refresh_release_manifest_identity()
    refresh_ro_crate_metadata()

    # DEDUPE_REPORT.md is another content-derived freshness surface.  Refresh
    # it after release/RO-Crate identity files settle, and before SPDX, so the
    # SPDX inventory digests the current dedupe report.  The dedupe builder
    # excludes itself, SPDX, MANIFEST.sha256, and INDEX/files.* to avoid
    # generated-surface digest/count loops.
    run_material_builder_subprocess("build_dedupe_report")

    # SPDX digests RELEASE_MANIFEST.json, RO_CRATE_PROFILE.md, and the current
    # DEDUPE_REPORT.md, but it must still be emitted before final INDEX/files.*
    # and MANIFEST.sha256.  Keep it out of refresh_cycle_safe_material_surfaces()
    # so it does not run before identity/RO-Crate/dedupe surfaces have settled.
    run_material_builder_subprocess("build_spdx_inventory")

    validate_metadata()

    # Build INDEX rows.
    all_files = collect_regular_archive_files(ROOT)
    print(f"rebuild-indexes: indexing {len(all_files)} files", flush=True)
    rows = []
    for idx, p in enumerate(all_files, start=1):
        rel = p.relative_to(ROOT).as_posix()
        if rel in EXCLUDE_FROM_INDEX:
            continue
        digest = sha256_file(p)
        category, project, ext = classify(rel)
        rows.append(
            {
                "path": rel,
                "size": p.stat().st_size,
                "sha256": digest,
                "category": category,
                "project": project,
                "ext": ext,
            }
        )
        if idx % 500 == 0:
            print(f"rebuild-indexes: indexed {idx}", flush=True)

    # Write INDEX through same-directory temporary files so interrupted rebuilds do
    # not leave truncated release-critical digest surfaces behind.
    atomic_write_text(INDEX_DIR / "files.json", json.dumps(rows, indent=2, sort_keys=False) + "\n", label="INDEX/files.json")
    csv_buffer = io.StringIO()
    w = csv.DictWriter(
        csv_buffer,
        fieldnames=["path", "size", "sha256", "category", "project", "ext"],
        lineterminator="\n",
    )
    w.writeheader()
    for r in rows:
        w.writerow(r)
    atomic_write_text(INDEX_DIR / "files.csv", csv_buffer.getvalue(), label="INDEX/files.csv")

    # Write MANIFEST (covers everything except itself).
    # Reuse the already captured file set rather than walking the tree a second
    # time after INDEX/files.* has been rewritten.  The Path objects point to the
    # refreshed files, so their digests are current, while the rebuild stays
    # closed over one stable package file set.
    print("rebuild-indexes: writing manifest", flush=True)
    manifest_lines = []
    for idx, p in enumerate(all_files, start=1):
        rel = p.relative_to(ROOT).as_posix()
        if rel in EXCLUDE_FROM_MANIFEST:
            continue
        digest = sha256_file(p)
        manifest_lines.append(f"{digest}  {rel}")
        if idx % 500 == 0:
            print(f"rebuild-indexes: manifested {idx}", flush=True)

    atomic_write_text(ROOT / "MANIFEST.sha256", "\n".join(manifest_lines) + "\n", label="MANIFEST.sha256")

    print(f"Wrote INDEX for {len(rows)} files; MANIFEST for {len(manifest_lines)} files")


if __name__ == "__main__":
    main()
