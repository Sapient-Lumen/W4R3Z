#!/usr/bin/env python3
"""Exercise the FreeBSD host-proof handoff importer.

The verifier made the future host proof handoff finite.  This guard makes the
next step finite too: importing a verified package must create a digest-named
import directory with a preserved handoff subdirectory and an import receipt,
while default mode still rejects checker simulations.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from cube_digest_lib import canonical_digest, load_json_strict_text
from freebsd import host_proof_contract as contract

ROOT = Path(__file__).resolve().parents[1]
FINALIZER_REL = "tools/freebsd/finalize_removable_media_local_fallback_host_proof_bundle.py"
VERIFY_REL = contract.HOST_PROOF_HANDOFF_VERIFIER_REL
IMPORT_REL = contract.HOST_PROOF_HANDOFF_IMPORTER_REL
DOC_REL = "docs/current/removable-media-freebsd-host-smoke.md"
SUCCESS_SIM_REL = "validation/removable-media-local-freebsd-host-smoke.success-simulation.json"
GENERATED_AT = "2026-06-12T23:00:00Z"


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def run_tool(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-B", "-S", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def load_json(path: Path) -> Any:
    return load_json_strict_text(path.read_text(encoding="utf-8"))


def copied_snapshot_manifest(handoff: Path) -> dict[str, Any]:
    return contract.copied_handoff_snapshot(handoff)


def load_importer_module() -> Any:
    spec = importlib.util.spec_from_file_location("derivebsd_host_proof_importer_under_test", ROOT / IMPORT_REL)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load importer module spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def write_sums(directory: Path) -> None:
    names = [contract.RECEIPT_NAME, contract.BUNDLE_NAME]
    if (directory / contract.README_NAME).exists():
        names.append(contract.README_NAME)
    (directory / contract.SUMS_NAME).write_text(
        "".join(f"{sha256_file(directory / name).removeprefix('sha256:')}  {name}\n" for name in names),
        encoding="utf-8",
    )


def import_root_children(import_root: Path) -> list[str]:
    if not import_root.exists():
        return []
    return sorted(child.name for child in import_root.iterdir())


def build_checker_handoff(directory: Path, *, smoke_id_suffix: str = "") -> None:
    directory.mkdir()
    if smoke_id_suffix:
        receipt_obj = load_json(ROOT / SUCCESS_SIM_REL)
        if not isinstance(receipt_obj, dict):
            raise RuntimeError("success simulation receipt must be an object")
        receipt_obj["smoke_id"] = f"{receipt_obj.get('smoke_id')}{smoke_id_suffix}"
        receipt_obj["generated_at_utc"] = "2026-06-12T23:00:01Z"
        (directory / contract.RECEIPT_NAME).write_text(json.dumps(receipt_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        shutil.copy2(ROOT / SUCCESS_SIM_REL, directory / contract.RECEIPT_NAME)
    proc = run_tool([
        FINALIZER_REL,
        str(directory / contract.RECEIPT_NAME),
        "--allow-checker-simulation",
        "--generated-at",
        GENERATED_AT,
        "--output",
        str(directory / contract.BUNDLE_NAME),
    ])
    if proc.returncode != 0:
        raise RuntimeError(f"could not build checker handoff: {proc.stdout} {proc.stderr}")
    (directory / contract.README_NAME).write_text(
        "Checker-simulation handoff for release-critical importer mechanics only; not release proof.\n",
        encoding="utf-8",
    )
    write_sums(directory)


def import_mode_errors() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="derivebsd-host-proof-import-check-") as td_name:
        tmp = Path(td_name)
        handoff = tmp / "handoff"
        import_root = tmp / "imports"
        build_checker_handoff(handoff)

        default_import = run_tool([IMPORT_REL, str(handoff), "--import-root", str(import_root)])
        require(errors, default_import.returncode != 0, "default importer must reject checker-simulation-non-proof handoff")
        require(errors, "default handoff verification accepts only real-host-proof" in default_import.stderr, "default importer rejection should come from strict handoff verification")
        require(errors, import_root_children(import_root) == [], "failed default import must leave no staging or partial import directories")

        symlink_source = tmp / "handoff-source-symlink"
        symlink_source.symlink_to(handoff, target_is_directory=True)
        symlink_import = run_tool([IMPORT_REL, str(symlink_source), "--import-root", str(import_root), "--allow-checker-simulation"])
        require(errors, symlink_import.returncode != 0, "importer must reject a symlinked handoff source before verification/copy")
        require(errors, "handoff directory must" in symlink_import.stderr and "symlink" in symlink_import.stderr, "symlink source import rejection should name the handoff root")
        require(errors, import_root_children(import_root) == [], "failed symlink-source import must leave no staging or partial import directories")

        ancestor_target = tmp / "handoff-ancestor-target"
        ancestor_target.mkdir()
        shutil.copytree(handoff, ancestor_target / "handoff")
        ancestor_link = tmp / "handoff-ancestor-link"
        ancestor_link.symlink_to(ancestor_target, target_is_directory=True)
        ancestor_import = run_tool([IMPORT_REL, str(ancestor_link / "handoff"), "--import-root", str(import_root), "--allow-checker-simulation"])
        require(errors, ancestor_import.returncode != 0, "importer must reject handoff sources with symlink ancestors before verification/copy")
        require(errors, "handoff directory must not contain existing symlink components" in ancestor_import.stderr, "symlink-ancestor source rejection should name the handoff path")
        require(errors, import_root_children(import_root) == [], "failed symlink-ancestor source import must leave no staging or partial import directories")

        import_ancestor_target = tmp / "import-ancestor-target"
        import_ancestor_target.mkdir()
        import_ancestor_link = tmp / "import-ancestor-link"
        import_ancestor_link.symlink_to(import_ancestor_target, target_is_directory=True)
        import_ancestor = run_tool([IMPORT_REL, str(handoff), "--import-root", str(import_ancestor_link / "imports"), "--allow-checker-simulation"])
        require(errors, import_ancestor.returncode != 0, "importer must reject import roots with symlink ancestors before creating staging directories")
        require(errors, "import root must not contain existing symlink components" in import_ancestor.stderr, "symlink-ancestor import-root rejection should name the import root")
        require(errors, not (import_ancestor_target / "imports").exists(), "symlink-ancestor import-root refusal must not create redirected import directories")

        unsafe_copy_source = tmp / "unsafe-copy-source"
        unsafe_copy_dest = tmp / "unsafe-copy-dest"
        unsafe_copy_source.mkdir()
        (unsafe_copy_source / "outside.json").write_text("{}\n", encoding="utf-8")
        (unsafe_copy_source / contract.RECEIPT_NAME).symlink_to(unsafe_copy_source / "outside.json")
        importer_module = load_importer_module()
        try:
            importer_module.copy_handoff(unsafe_copy_source, unsafe_copy_dest)
        except ValueError as exc:
            require(errors, "regular file" in str(exc) or "symlink" in str(exc), "safe copy rejection should name symlink/non-regular source members")
        else:
            require(errors, False, "copy_handoff must reject allowed-name symlink members even if called after a stale pre-verify")


        race_source = tmp / "race-source-handoff"
        race_replacement = tmp / "race-replacement-handoff"
        race_import_root = tmp / "race-imports"
        build_checker_handoff(race_source)
        build_checker_handoff(race_replacement, smoke_id_suffix="-copied-snapshot-race")
        importer_module = load_importer_module()
        original_copy_handoff = importer_module.copy_handoff

        def copy_replacement_handoff(_source: Path, destination: Path) -> None:
            original_copy_handoff(race_replacement, destination)

        importer_module.copy_handoff = copy_replacement_handoff
        try:
            imported_race_dir = importer_module.import_handoff(
                race_source,
                import_root=race_import_root,
                allow_checker_simulation=True,
            )
        finally:
            importer_module.copy_handoff = original_copy_handoff
        copied_receipt = load_json(race_replacement / contract.RECEIPT_NAME)
        source_name = contract.import_directory_name("checker-simulation-non-proof", copied_snapshot_manifest(race_source)["canonical_sha256"])
        copied_name = contract.import_directory_name("checker-simulation-non-proof", copied_snapshot_manifest(race_replacement)["canonical_sha256"])
        require(errors, imported_race_dir.name == copied_name, "import directory identity must be derived from the copied/reverified handoff snapshot")
        require(errors, imported_race_dir.name != source_name, "import directory identity must not come from the mutable pre-copy source receipt")
        race_record = load_json(imported_race_dir / contract.IMPORT_RECEIPT_NAME)
        race_invariants = race_record.get("invariants", {}) if isinstance(race_record.get("invariants"), dict) else {}
        require(errors, race_record.get("identity_policy") == contract.IMPORT_STAGED_IDENTITY_POLICY, "import receipt must bind staged snapshot identity policy")
        require(errors, race_record.get("receipt", {}).get("canonical_sha256") == canonical_digest(copied_receipt), "import receipt summary must be loaded from the copied snapshot receipt")
        require(errors, race_invariants.get("import_directory_identity_derived_from_reverified_copied_snapshot") is True, "import receipt must assert copied-snapshot import identity")
        require(errors, race_invariants.get("import_receipt_summaries_loaded_from_reverified_copied_snapshot") is True, "import receipt must assert copied-snapshot summaries")

        allowed = run_tool([IMPORT_REL, str(handoff), "--import-root", str(import_root), "--allow-checker-simulation"])
        require(errors, allowed.returncode == 0, f"explicit checker import should pass: {allowed.stdout} {allowed.stderr}")
        imported_dirs = sorted(import_root.iterdir()) if import_root.exists() else []
        require(errors, len(imported_dirs) == 1, "checker import should create exactly one digest-named import directory")
        if imported_dirs:
            import_dir = imported_dirs[0]
            expected_name = contract.import_directory_name("checker-simulation-non-proof", copied_snapshot_manifest(handoff)["canonical_sha256"])
            require(errors, import_dir.name == expected_name, "import directory must bind proof status and the full copied handoff snapshot canonical digest")
            require(errors, len(import_dir.name.rsplit("-", 1)[-1]) == contract.IMPORT_DIRECTORY_DIGEST_HEX_LENGTH, "import directory must use the full 64-hex copied snapshot digest, not a prefix")
            imported_handoff = import_dir / "handoff"
            import_receipt = import_dir / contract.IMPORT_RECEIPT_NAME
            require(errors, imported_handoff.is_dir(), "import must preserve the handoff as a finite subdirectory")
            require(errors, import_receipt.is_file(), "import must write a sibling import.receipt.json")
            verify_imported = run_tool([VERIFY_REL, str(imported_handoff), "--allow-checker-simulation"])
            require(errors, verify_imported.returncode == 0, f"copied handoff should reverify: {verify_imported.stdout} {verify_imported.stderr}")
            if import_receipt.exists():
                record = load_json(import_receipt)
                bundle = load_json(imported_handoff / contract.BUNDLE_NAME)
                require(errors, record.get("kind") == "removable.media.local.freebsd.host.proof.handoff.import.receipt", "import receipt must carry the expected kind")
                require(errors, record.get("generated_for_version") == contract.CURRENT_CUBE_CUT_VERSION, "import receipt must bind current cube cut")
                require(errors, record.get("import_status") == "checker-simulation-non-proof-import", "checker import receipt must remain non-proof")
                require(errors, record.get("proof_status") == "checker-simulation-non-proof", "import receipt proof_status must match bundle")
                invariants = record.get("invariants", {}) if isinstance(record.get("invariants"), dict) else {}
                for key in [
                    "handoff_verified_before_copy",
                    "handoff_reverified_after_copy",
                    "checker_simulation_import_requires_explicit_flag",
                    "import_directory_name_binds_full_copied_handoff_snapshot_canonical_digest",
                    "import_preserves_finite_handoff_subdirectory",
                    "import_receipt_enumerates_all_imported_handoff_files",
                    "import_copied_to_staging_before_publish",
                    "import_receipt_written_before_publish",
                    "import_published_by_atomic_rename_after_reverification",
                    "failed_import_keeps_existing_digest_import_until_publish",
                    "import_receipt_binds_source_transport",
                    "directory_import_copies_allowed_regular_files_without_following_symlinks",
                    "import_receipt_binds_copied_snapshot_not_mutable_source",
                    "import_receipt_binds_copied_snapshot_manifest_digest",
                    "import_directory_identity_derived_from_reverified_copied_snapshot",
                    "import_receipt_summaries_loaded_from_reverified_copied_snapshot",
                    "staged_files_and_import_receipt_fsynced_before_publish",
                    "import_parent_directory_fsynced_after_publish",
                ]:
                    require(errors, invariants.get(key) is True, f"import invariant {key} must be true")
                transport = record.get("source_transport", {}) if isinstance(record.get("source_transport"), dict) else {}
                require(errors, transport.get("kind") == contract.DIRECTORY_IMPORT_SOURCE_KIND, "directory importer receipt must record directory source transport")
                require(errors, transport.get("path") == record.get("source_handoff_dir"), "directory importer source transport path must match source_handoff_dir")
                require(errors, transport.get("sha256sums_byte_sha256") == sha256_file(handoff / contract.SUMS_NAME), "directory importer source transport must bind SHA256SUMS bytes")
                require(errors, invariants.get("directory_import_receipt_binds_source_handoff") is True, "directory importer must assert directory source provenance")
                require(errors, invariants.get("sealed_import_receipt_binds_archive_digest") is False, "directory importer must not assert sealed archive provenance")
                require(errors, record.get("copy_policy") == contract.DIRECTORY_IMPORT_COPY_POLICY, "import receipt must bind the nofollow staging copy policy")
                require(errors, record.get("identity_policy") == contract.IMPORT_STAGED_IDENTITY_POLICY, "import receipt must bind staged snapshot identity policy")
                require(errors, record.get("durable_write_policy") == contract.IMPORT_DURABLE_WRITE_POLICY, "import receipt must bind the durable fsync write policy")
                require(errors, record.get("atomic_publish_policy") == "copy-verify-fsync-write-receipt-fsync-then-rename-and-fsync-parent-to-full-digest-import-dir", "import receipt must bind atomic fsync staging publish policy")
                require(errors, record.get("copied_handoff_snapshot") == copied_snapshot_manifest(imported_handoff), "import receipt must bind a canonical copied handoff snapshot manifest")
                require(errors, record.get("bundle", {}).get("canonical_sha256") == canonical_digest(bundle), "import receipt must bind bundle canonical digest")
                require(errors, record.get("receipt", {}).get("host_target_matrix_id") == contract.HOST_TARGET_MATRIX_ID, "import receipt must preserve host target matrix id in the receipt summary")
                require(errors, record.get("receipt", {}).get("host_target_tier") == contract.HOST_TARGET_PRIMARY_TIER, "import receipt must preserve host target tier in the receipt summary")
                require(errors, record.get("bundle", {}).get("host_target_matrix_id") == contract.HOST_TARGET_MATRIX_ID, "import receipt must preserve host target matrix id in the bundle summary")
                require(errors, record.get("bundle", {}).get("host_target_tier") == contract.HOST_TARGET_PRIMARY_TIER, "import receipt must preserve host target tier in the bundle summary")
                require(errors, invariants.get("import_receipt_preserves_host_target_tier") is True, "import receipt invariant must assert host target preservation")
                file_paths = {row.get("path") for row in record.get("files", []) if isinstance(row, dict)}
                require(errors, f"handoff/{contract.README_NAME}" in file_paths, "import receipt must enumerate copied optional README.import.txt")

            same_receipt_different_note = tmp / "same-receipt-different-note"
            shutil.copytree(handoff, same_receipt_different_note)
            (same_receipt_different_note / contract.README_NAME).write_text(
                "Same receipt and bundle, but a different checksum-bound operator note.\n",
                encoding="utf-8",
            )
            write_sums(same_receipt_different_note)
            note_import = run_tool([IMPORT_REL, str(same_receipt_different_note), "--import-root", str(import_root), "--allow-checker-simulation"])
            require(errors, note_import.returncode == 0, f"same-receipt handoff with different checksum-bound note should not collide: {note_import.stdout} {note_import.stderr}")
            note_expected = contract.import_directory_name("checker-simulation-non-proof", copied_snapshot_manifest(same_receipt_different_note)["canonical_sha256"])
            require(errors, note_expected in import_root_children(import_root), "import directory identity must include checksum-bound optional handoff bytes, not only receipt.json")
            require(errors, note_expected != expected_name, "changed README.import.txt must produce a different copied-snapshot import identity")

            before_duplicate_children = import_root_children(import_root)
            duplicate = run_tool([IMPORT_REL, str(handoff), "--import-root", str(import_root), "--allow-checker-simulation"])
            require(errors, duplicate.returncode != 0, "importer must refuse duplicate digest import without --replace")
            require(errors, "import directory already exists" in duplicate.stderr, "duplicate import rejection should name existing import directory")
            require(errors, import_root_children(import_root) == before_duplicate_children, "duplicate import refusal must not leave staging directories or alter the imported proof")

            replaced = run_tool([IMPORT_REL, str(handoff), "--import-root", str(import_root), "--allow-checker-simulation", "--replace"])
            require(errors, replaced.returncode == 0, f"deliberate --replace should pass for deterministic re-import: {replaced.stdout} {replaced.stderr}")
            require(errors, import_root_children(import_root) == before_duplicate_children, "deliberate replace should leave only the digest-named import directory and no backup/staging residue")
    return errors


def surface_errors() -> list[str]:
    errors: list[str] = []
    for rel in [IMPORT_REL, VERIFY_REL, contract.HOST_PROOF_CONTRACT_REL]:
        require(errors, (ROOT / rel).exists(), f"missing {rel}")
    importer_text = (ROOT / IMPORT_REL).read_text(encoding="utf-8", errors="replace")
    for token in [
        "tempfile.mkdtemp",
        "os.replace",
        "copy-verify-fsync-write-receipt-fsync-then-rename-and-fsync-parent-to-full-digest-import-dir",
        "failed_import_keeps_existing_digest_import_until_publish",
        "staging_dir",
        "replace-backup",
        "_checked_handoff_source",
        "_checked_import_root",
        "handoff directory must not be a symlink",
        "contract.import_directory_name",
        "source_transport",
        "directory_source_transport",
        "DIRECTORY_IMPORT_COPY_POLICY",
        "copy_policy",
        "O_NOFOLLOW",
        "dir_fd",
        "import_receipt_binds_source_transport",
        "directory_import_copies_allowed_regular_files_without_following_symlinks",
        "import_receipt_binds_copied_snapshot_not_mutable_source",
        "import_receipt_binds_copied_snapshot_manifest_digest",
        "IMPORT_RECEIPT_SNAPSHOT_POLICY",
        "IMPORT_DURABLE_WRITE_POLICY",
        "IMPORT_STAGED_IDENTITY_POLICY",
        "identity_policy",
        "import_directory_identity_derived_from_reverified_copied_snapshot",
        "import_receipt_summaries_loaded_from_reverified_copied_snapshot",
        "import_receipt_preserves_host_target_tier",
        "host_target_tier",
        "copied_handoff_snapshot",
        "_fsync_dir",
        "_write_pretty_json_durable",
    ]:
        require(errors, token in importer_text, f"importer must bind atomic publish token {token!r}")
    require(errors, "return 0\n    return 0" not in importer_text, "importer must not retain unreachable duplicate return statements")
    contract_text = (ROOT / contract.HOST_PROOF_CONTRACT_REL).read_text(encoding="utf-8", errors="replace")
    for token in ["IMPORT_DIRECTORY_DIGEST_HEX_LENGTH", "IMPORT_DIRECTORY_DIGEST_POLICY", "DIRECTORY_IMPORT_COPY_POLICY", "IMPORT_RECEIPT_SNAPSHOT_POLICY", "IMPORT_DURABLE_WRITE_POLICY", "IMPORT_STAGED_IDENTITY_POLICY", "def import_directory_name"]:
        require(errors, token in contract_text, f"shared contract must bind import-directory token {token!r}")
    bundle_text = (ROOT / "tools/freebsd/finalize_removable_media_local_fallback_host_proof_bundle.py").read_text(encoding="utf-8", errors="replace")
    validator_text = (ROOT / "tools/freebsd/validate_removable_media_local_fallback_host_proof_bundle.py").read_text(encoding="utf-8", errors="replace")
    for text, label in [(bundle_text, "finalizer"), (validator_text, "bundle validator")]:
        require(errors, "host_proof_contract" in text, f"{label} must use shared host-proof contract constants")
        require(errors, "REQUIRED_PROOF_TOOL" in text, f"{label} must use shared proof-tool path set")
    doc = (ROOT / DOC_REL).read_text(encoding="utf-8", errors="replace")
    for token in [IMPORT_REL, "import.receipt.json", "digest-named import directory", "shared FreeBSD proof-tool contract", "tools/freebsd/audit_removable_media_local_fallback_host_proof_imports.py", "atomic staging", "full copied handoff snapshot canonical digest", "preserve an existing digest import until replacement publish", "handoff directory must not be a symlink", "symlink ancestor", "nofollow staging copy policy", "staged snapshot identity policy"]:
        require(errors, token in doc, f"{DOC_REL} missing importer token {token!r}")
    return errors


def main() -> int:
    errors = import_mode_errors() + surface_errors()
    if errors:
        print("FreeBSD host proof importer check FAILED.")
        for error in errors:
            print("-", error)
        return 1
    print("FreeBSD host proof importer check OK")
    print("Importer rejects checker simulations by default and creates a finite digest-named import directory only under an explicit non-proof flag")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
