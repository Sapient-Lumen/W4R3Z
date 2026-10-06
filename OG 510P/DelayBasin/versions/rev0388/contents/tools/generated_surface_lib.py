import filecmp
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import Iterable

ROOT = pathlib.Path(__file__).resolve().parents[1]
DRIFT_VALIDATION_MODE = "temporary-copy-read-only-target"

# Generators are intentionally outside the lint toolchain. `make context-pack`
# and `tools/package_release.py` refresh them; `make lint` now fails closed if
# any generated surface is stale instead of silently repairing it during
# validation.
GENERATOR_SCRIPTS: tuple[str, ...] = (
    "tools/gen_external_metadata.py",
    "tools/gen_current_receipt.py",
    "tools/gen_context_pack.py",
    "tools/gen_innovation_packet.py",
    "tools/gen_frontier_ticket.py",
    "tools/gen_validation_index.py",
    "tools/gen_validation_toolchain_manifest.py",
    "tools/gen_compact_surface_bundle.py",
    "tools/gen_replay_capsule.py",
    "tools/gen_canary_runs.py",
    "tools/gen_currentness_cue_audit.py",
    "tools/gen_reentry_surface_conformance.py",
    "tools/gen_ledger_audit.py",
    "tools/gen_lint_idempotence_audit.py",
    "tools/gen_package_identity_audit.py",
    "tools/gen_basis_provenance_audit.py",
    "tools/gen_schema_coverage_audit.py",
    "tools/gen_schema_conformance_audit.py",
    "tools/gen_archive_economy_audit.py",
)

# This is the full output set produced by the generator pipeline plus release
# integrity. Drift checks compare only these surfaces, not ambient workspace
# files, so the gate remains operational hygiene rather than a hidden review
# court over every file in the cube.
GENERATED_SURFACES: tuple[str, ...] = (
    "LICENSE",
    "CITATION.cff",
    "codemeta.json",
    "ro-crate-metadata.json",
    "SBOM.spdx.json",
    "CURRENT-RECEIPT.json",
    "context-pack.json",
    "innovation-packet.json",
    "frontier-ticket.json",
    "VALIDATION-INDEX.json",
    "docs/00-meta/validation-index.md",
    "VALIDATION-TOOLCHAIN-MANIFEST.json",
    "docs/00-meta/validation-toolchain.md",
    "compact-surface-bundle.json",
    "replay-capsule.json",
    "CANARY-RUNS.json",
    "CURRENTNESS-CUE-AUDIT.json",
    "docs/00-meta/currentness-cue-audit.md",
    "REENTRY-SURFACE-CONFORMANCE.json",
    "LEDGER-AUDIT.json",
    "docs/00-meta/ledger-audit.md",
    "PACKAGE-IDENTITY-AUDIT.json",
    "docs/00-meta/package-identity-audit.md",
    "BASIS-PROVENANCE-AUDIT.json",
    "docs/00-meta/basis-provenance-audit.md",
    "SCHEMA-COVERAGE-AUDIT.json",
    "docs/00-meta/schema-coverage-audit.md",
    "SCHEMA-CONFORMANCE-AUDIT.json",
    "docs/00-meta/schema-conformance-audit.md",
    "LINT-IDEMPOTENCE-AUDIT.json",
    "docs/00-meta/lint-idempotence-audit.md",
    "ARCHIVE-ECONOMY-AUDIT.json",
    "docs/00-meta/archive-economy-audit.md",
    "FILE-MANIFEST.json",
    "CHECKSUMS.sha256",
    "RELEASE-PROVENANCE.json",
)

INTEGRITY_SCRIPT = "tools/gen_release_integrity.py"


@dataclass(frozen=True)
class GeneratedDrift:
    surface: str
    status: str


def _env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run_python_script(root: pathlib.Path, script: str) -> None:
    subprocess.run(
        [sys.executable, "-S", script],
        cwd=root,
        env=_env(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )


def refresh_generated_surfaces(root: pathlib.Path, *, include_release_integrity: bool = True) -> None:
    # Seed canonical package provenance before lint-idempotence is regenerated;
    # final integrity is written again after all other generated outputs settle.
    if include_release_integrity:
        run_python_script(root, INTEGRITY_SCRIPT)
    for script in GENERATOR_SCRIPTS:
        run_python_script(root, script)
    if include_release_integrity:
        run_python_script(root, INTEGRITY_SCRIPT)


def copy_release_tree_for_generation(root: pathlib.Path) -> pathlib.Path:
    tmp_parent = pathlib.Path(tempfile.mkdtemp(prefix="delaybasin-generated-drift-"))
    tmp_root = tmp_parent / "tree"

    def ignore(_dir: str, names: list[str]) -> set[str]:
        return {
            name for name in names
            if name in {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
            or name.endswith((".pyc", ".pyo"))
        }

    shutil.copytree(root, tmp_root, ignore=ignore)
    return tmp_root


def _read_generated_snapshot(root: pathlib.Path) -> dict[str, bytes | None]:
    snapshot: dict[str, bytes | None] = {}
    for rel in GENERATED_SURFACES:
        path = root / rel
        snapshot[rel] = path.read_bytes() if path.exists() else None
    return snapshot


def generated_surface_drift(root: pathlib.Path) -> list[GeneratedDrift]:
    """Compare committed generated surfaces with a regenerated temporary tree.

    Validation must not repair the tree it is judging.  The target tree is read
    once, regeneration happens only in an isolated copy, and the copy is
    removed even when a generator fails.  A stale surface therefore remains
    stale after a failed lint and can be inspected or repaired explicitly with
    ``make context-pack``.
    """
    root = pathlib.Path(root).resolve()
    current = _read_generated_snapshot(root)
    generated_root = copy_release_tree_for_generation(root)
    try:
        refresh_generated_surfaces(generated_root, include_release_integrity=True)
        generated = _read_generated_snapshot(generated_root)
    finally:
        shutil.rmtree(generated_root.parent, ignore_errors=True)

    rows: list[GeneratedDrift] = []
    for rel in GENERATED_SURFACES:
        current_bytes = current.get(rel)
        generated_bytes = generated.get(rel)
        if current_bytes is None and generated_bytes is None:
            continue
        if current_bytes is None:
            rows.append(GeneratedDrift(rel, "missing-current"))
            continue
        if generated_bytes is None:
            rows.append(GeneratedDrift(rel, "missing-generated"))
            continue
        if current_bytes != generated_bytes:
            rows.append(GeneratedDrift(rel, "content-drift"))
    return rows
