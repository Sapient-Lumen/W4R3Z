#!/usr/bin/env python3
"""Guard one-command sealed FreeBSD host-proof archive import.

A scarce real-host proof may arrive in the cloudtainer as a deterministic sealed
ZIP rather than as three loose handoff files.  This check proves the sealed
archive importer remains a strict composition of existing primitives: validate
archive, unseal into scratch, verify handoff, import by full copied-snapshot
digest, audit the import root, and remove scratch state.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from cube_digest_lib import canonical_digest, load_json_strict_text, write_pretty_json  # noqa: E402
from freebsd import host_proof_contract as contract  # noqa: E402
from freebsd import import_sealed_removable_media_local_fallback_host_proof_handoff as sealed_importer  # noqa: E402
from freebsd import unseal_removable_media_local_fallback_host_proof_handoff as handoff_unsealer  # noqa: E402

FINALIZER_REL = contract.HOST_PROOF_FINALIZER_REL
SEAL_REL = contract.HOST_PROOF_HANDOFF_SEALER_REL
SEALED_IMPORT_REL = contract.HOST_PROOF_SEALED_HANDOFF_IMPORTER_REL
VERIFY_REL = contract.HOST_PROOF_HANDOFF_VERIFIER_REL
AUDIT_REL = contract.HOST_PROOF_IMPORT_AUDITOR_REL
DOC_REL = "docs/current/removable-media-freebsd-host-smoke.md"
START_REL = "docs/current/start-here-now.md"
OPERATOR_PACKET_REL = "docs/current/freebsd-real-host-proof-operator-packet.md"
SUCCESS_SIM_REL = "validation/removable-media-local-freebsd-host-smoke.success-simulation.json"
GENERATED_AT = "2026-06-12T23:00:00Z"


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> object:
    return load_json_strict_text(path.read_text(encoding="utf-8"))


def copied_snapshot_manifest(handoff: Path) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    total_size = 0
    for name in sorted(contract.HANDOFF_ALLOWED_NAMES):
        child = handoff / name
        if child.exists() and child.is_file() and not child.is_symlink():
            size = child.stat().st_size
            total_size += size
            rows.append({"path": f"handoff/{child.name}", "sha256": sha256_file(child), "size_bytes": size})
    core: dict[str, object] = {
        "kind": contract.IMPORT_RECEIPT_SNAPSHOT_KIND,
        "snapshot_policy": contract.IMPORT_RECEIPT_SNAPSHOT_POLICY,
        "file_count": len(rows),
        "total_size_bytes": total_size,
        "files": rows,
    }
    return {**core, "canonical_sha256": canonical_digest(core)}


def run_tool(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-B", "-S", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def write_sums(directory: Path) -> None:
    rows = [contract.RECEIPT_NAME, contract.BUNDLE_NAME]
    if (directory / contract.README_NAME).exists():
        rows.append(contract.README_NAME)
    (directory / contract.SUMS_NAME).write_text(
        "".join(f"{sha256_file(directory / name).removeprefix('sha256:')}  {name}\n" for name in rows),
        encoding="utf-8",
    )


def build_checker_handoff(directory: Path, *, smoke_id_suffix: str = "") -> None:
    directory.mkdir()
    receipt_obj = load_json(ROOT / SUCCESS_SIM_REL)
    if not isinstance(receipt_obj, dict):
        raise RuntimeError("success simulation fixture must be a JSON object")
    if smoke_id_suffix:
        receipt_obj = dict(receipt_obj)
        receipt_obj["smoke_id"] = f"{receipt_obj.get('smoke_id')}-{smoke_id_suffix}"
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
        "Checker-simulation handoff for release-critical sealed import mechanics only; not release proof.\n",
        encoding="utf-8",
    )
    write_sums(directory)




def _set_checker_only_false(value: object) -> None:
    if isinstance(value, dict):
        for key, child in list(value.items()):
            if "checker_only" in str(key) and child is True:
                value[key] = False
            else:
                _set_checker_only_false(child)
    elif isinstance(value, list):
        for child in value:
            _set_checker_only_false(child)


def _rewrite_probe(receipt: dict[str, object], role: str, observed_value: str) -> None:
    for row in receipt.get("host_probes", []):
        if isinstance(row, dict) and row.get("command_role") == role:
            row["observed_value"] = observed_value
            row["observed_stdout_text"] = f"{observed_value}\n"
            row["stdout_sha256"] = "sha256:" + hashlib.sha256(str(row["observed_stdout_text"]).encode("utf-8")).hexdigest()


def build_synthetic_real_handoff(directory: Path, *, uname_release: str, osreldate: str, host_target_tier: str) -> None:
    """Build a temp-only real-like handoff so primary-target importer gates can be exercised."""
    directory.mkdir()
    receipt_obj = load_json(ROOT / SUCCESS_SIM_REL)
    if not isinstance(receipt_obj, dict):
        raise RuntimeError("success simulation fixture must be a JSON object")
    receipt = json.loads(json.dumps(receipt_obj))
    receipt["cube_cut_version"] = contract.CURRENT_CUBE_CUT_VERSION
    _set_checker_only_false(receipt)
    simulation = receipt.get("simulation") if isinstance(receipt.get("simulation"), dict) else {}
    simulation["claims_real_freebsd_execution"] = True
    simulation["fake_commands_observed"] = []
    simulation["not_freebsd_host_proof"] = False
    simulation["safe_capture_executed_against_simulated_mount_tree"] = False
    simulation["worker_runner_is_checker_only"] = False
    host = receipt.get("host") if isinstance(receipt.get("host"), dict) else {}
    host["observed_system"] = "FreeBSD"
    host["cloudtainer_refusal_is_expected"] = False
    host["host_probe_uname_release"] = uname_release
    host["host_probe_osreldate"] = osreldate
    host["host_target_tier"] = host_target_tier
    host_smoke = receipt.get("host_smoke") if isinstance(receipt.get("host_smoke"), dict) else {}
    host_smoke["host_target_tier"] = host_target_tier
    host_smoke["host_target_matrix_id"] = contract.HOST_TARGET_MATRIX_ID
    _rewrite_probe(receipt, "host-probe-uname-system", "FreeBSD")
    _rewrite_probe(receipt, "host-probe-uname-release", uname_release)
    _rewrite_probe(receipt, "host-probe-effective-uid", "0")
    _rewrite_probe(receipt, "host-probe-osreldate", osreldate)
    _rewrite_probe(receipt, "host-probe-capsicum-capability-mode", "1")
    _rewrite_probe(receipt, "host-probe-capsicum-capabilities", "1")
    (directory / contract.RECEIPT_NAME).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    proc = run_tool([
        FINALIZER_REL,
        str(directory / contract.RECEIPT_NAME),
        "--generated-at",
        GENERATED_AT,
        "--output",
        str(directory / contract.BUNDLE_NAME),
    ])
    if proc.returncode != 0:
        raise RuntimeError(f"could not build synthetic real handoff: {proc.stdout} {proc.stderr}")
    (directory / contract.README_NAME).write_text(
        "Synthetic temp-only real-like handoff for release-critical primary-target gate mechanics; not checked-in release proof.\n",
        encoding="utf-8",
    )
    write_sums(directory)

def import_root_children(root: Path) -> list[str]:
    if not root.exists():
        return []
    return sorted(child.name for child in root.iterdir())


def make_compressed_archive(source_archive: Path, output: Path) -> None:
    with zipfile.ZipFile(source_archive) as src, zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as dst:
        for row in src.infolist():
            info = zipfile.ZipInfo(row.filename, contract.HANDOFF_ARCHIVE_FIXED_ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (contract.HANDOFF_ARCHIVE_FIXED_FILE_MODE & 0xFFFF) << 16
            dst.writestr(info, src.read(row.filename))


def make_archive_with_comment(source_archive: Path, output: Path) -> None:
    shutil.copy2(source_archive, output)
    with zipfile.ZipFile(output, "a") as zf:
        zf.comment = b"noncanonical-comment"


def make_archive_with_entry_extra(source_archive: Path, output: Path) -> None:
    with zipfile.ZipFile(source_archive) as src, zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as dst:
        for row in src.infolist():
            info = zipfile.ZipInfo(row.filename, contract.HANDOFF_ARCHIVE_FIXED_ZIP_DATE)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = (contract.HANDOFF_ARCHIVE_FIXED_FILE_MODE & 0xFFFF) << 16
            info.extra = b"\x99\x99\x00\x00"
            dst.writestr(info, src.read(row.filename))


def make_reordered_archive(source_archive: Path, output: Path) -> None:
    with zipfile.ZipFile(source_archive) as src, zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as dst:
        for row in reversed(src.infolist()):
            info = zipfile.ZipInfo(row.filename, contract.HANDOFF_ARCHIVE_FIXED_ZIP_DATE)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = (contract.HANDOFF_ARCHIVE_FIXED_FILE_MODE & 0xFFFF) << 16
            dst.writestr(info, src.read(row.filename))


def make_archive_without_regular_file_type(source_archive: Path, output: Path) -> None:
    with zipfile.ZipFile(source_archive) as src, zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as dst:
        for row in src.infolist():
            info = zipfile.ZipInfo(row.filename, contract.HANDOFF_ARCHIVE_FIXED_ZIP_DATE)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = (0o644 & 0xFFFF) << 16
            dst.writestr(info, src.read(row.filename))


def sealed_import_mode_errors() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="derivebsd-host-proof-sealed-import-check-") as td_name:
        tmp = Path(td_name)
        handoff = tmp / "handoff"
        import_root = tmp / "imports"
        build_checker_handoff(handoff)

        archive = tmp / "handoff.zip"
        sealed = run_tool([SEAL_REL, str(handoff), "--output", str(archive), "--allow-checker-simulation"])
        require(errors, sealed.returncode == 0, f"checker handoff should seal explicitly: {sealed.stdout} {sealed.stderr}")

        default_import = run_tool([SEALED_IMPORT_REL, str(archive), "--import-root", str(import_root)])
        require(errors, default_import.returncode != 0, "default sealed importer must reject checker-simulation-non-proof archives")
        require(errors, "default handoff verification accepts only real-host-proof" in default_import.stderr, "default sealed importer rejection should come from strict unseal/handoff verification")
        require(errors, import_root_children(import_root) == [], "failed default sealed import must leave no import-root children or scratch state")
        require(errors, not any(child.name.startswith(".imports.sealed-handoff-import-") for child in tmp.iterdir()), "failed default sealed import must remove sibling scratch state")

        legacy_handoff = tmp / "legacy-real-like-handoff"
        build_synthetic_real_handoff(
            legacy_handoff,
            uname_release=f"{contract.SUPPORTED_FREEBSD_RELEASE_FLOOR}-p0",
            osreldate=str(contract.MIN_FREEBSD_OSRELDATE),
            host_target_tier=contract.HOST_TARGET_LEGACY_TIER,
        )
        legacy_archive = tmp / "legacy-real-like.zip"
        legacy_sealed = run_tool([SEAL_REL, str(legacy_handoff), "--output", str(legacy_archive)])
        require(errors, legacy_sealed.returncode == 0, f"legacy real-like handoff should seal in default mode: {legacy_sealed.stdout} {legacy_sealed.stderr}")
        legacy_required_root = tmp / "legacy-required-imports"
        legacy_required = run_tool([SEALED_IMPORT_REL, str(legacy_archive), "--import-root", str(legacy_required_root), "--require-primary-target"])
        require(errors, legacy_required.returncode != 0, "sealed importer --require-primary-target must reject supported-floor legacy real proof before publish")
        require(errors, "primary-target sealed import requires primary-production" in legacy_required.stderr, "primary-target rejection should name the observed non-primary tier")
        require(errors, import_root_children(legacy_required_root) == [], "primary-target rejection must leave the import root empty")
        require(errors, not any(child.name.startswith(".legacy-required-imports.sealed-handoff-import-") for child in tmp.iterdir()), "primary-target rejection must cleanup sealed-import scratch state")
        legacy_default_root = tmp / "legacy-default-imports"
        legacy_default = run_tool([SEALED_IMPORT_REL, str(legacy_archive), "--import-root", str(legacy_default_root)])
        require(errors, legacy_default.returncode == 0, f"default sealed importer may still import supported-floor real proof without the primary-only gate: {legacy_default.stdout} {legacy_default.stderr}")
        require(errors, len(import_root_children(legacy_default_root)) == 1, "default legacy real-proof import should publish one digest directory")

        locked_root = tmp / "locked-imports"
        locked_root.mkdir()
        locked_dir = tmp / ".locked-imports.sealed-import.lock"
        locked_dir.mkdir()
        locked_import = run_tool([SEALED_IMPORT_REL, str(archive), "--import-root", str(locked_root), "--allow-checker-simulation"])
        require(errors, locked_import.returncode != 0, "sealed importer must refuse to run while another sealed import lock is present")
        require(errors, "active sealed import lock already exists" in locked_import.stderr, "lock refusal should identify active sealed import lock")
        require(errors, import_root_children(locked_root) == [], "locked sealed import must not publish into import root")
        require(errors, locked_dir.exists(), "lock refusal must not remove a lock it did not acquire")
        shutil.rmtree(locked_dir)

        allowed = run_tool([SEALED_IMPORT_REL, str(archive), "--import-root", str(import_root), "--allow-checker-simulation"])
        require(errors, allowed.returncode == 0, f"explicit checker sealed import should pass: {allowed.stdout} {allowed.stderr}")
        children = import_root_children(import_root)
        require(errors, len(children) == 1, "sealed import should leave exactly one digest import directory")
        require(errors, not any(child.name.startswith(".imports.sealed-handoff-import-") for child in tmp.iterdir()), "successful sealed import must remove sibling scratch state")
        require(errors, not any(child.name.endswith(".sealed-import.lock") for child in tmp.iterdir()), "successful sealed import must remove sibling import lock state")
        if children:
            expected_name = contract.import_directory_name("checker-simulation-non-proof", copied_snapshot_manifest(handoff)["canonical_sha256"])
            import_dir = import_root / children[0]
            require(errors, import_dir.name == expected_name, "sealed importer must publish under the same full copied-snapshot import name as the directory importer")
            verify_imported = run_tool([VERIFY_REL, str(import_dir / "handoff"), "--allow-checker-simulation"])
            require(errors, verify_imported.returncode == 0, f"sealed-imported handoff should verify: {verify_imported.stdout} {verify_imported.stderr}")
            audit = run_tool([AUDIT_REL, str(import_root), "--allow-checker-simulation"])
            require(errors, audit.returncode == 0, f"sealed importer must leave the import root audit-clean: {audit.stdout} {audit.stderr}")
            record = load_json(import_dir / contract.IMPORT_RECEIPT_NAME)
            if isinstance(record, dict):
                require(errors, record.get("source_handoff_dir", "").endswith("/handoff"), "import receipt should identify the temporary unsealed handoff source")
                transport = record.get("source_transport", {}) if isinstance(record.get("source_transport"), dict) else {}
                require(errors, transport.get("kind") == contract.SEALED_IMPORT_SOURCE_KIND, "sealed import receipt must bind sealed archive source transport")
                require(errors, transport.get("byte_sha256") == sha256_file(archive), "sealed import receipt must bind the copied source archive snapshot digest")
                require(errors, transport.get("archive_format") == contract.HANDOFF_ARCHIVE_FORMAT, "sealed import receipt must bind the archive format")
                require(errors, transport.get("archive_size_bytes") == archive.stat().st_size, "sealed import receipt must bind the copied source archive snapshot size")
                require(errors, transport.get("sealed_import_policy") == contract.SEALED_IMPORT_POLICY, "sealed import receipt must bind the sealed import policy")
                require(errors, transport.get("sealed_import_lock_policy") == contract.SEALED_IMPORT_LOCK_POLICY, "sealed import receipt must bind the exclusive sealed import lock policy")
                require(errors, isinstance(transport.get("sealed_import_lock_path"), str) and transport.get("sealed_import_lock_path", "").endswith(".sealed-import.lock"), "sealed import receipt must bind the sibling lock path")
                require(errors, transport.get("canonical_zip_metadata_policy") == contract.HANDOFF_ARCHIVE_CANONICAL_METADATA_POLICY, "sealed import receipt must bind the canonical ZIP metadata policy")
                archive_snapshot = transport.get("archive_snapshot", {}) if isinstance(transport.get("archive_snapshot"), dict) else {}
                require(errors, archive_snapshot.get("kind") == contract.HANDOFF_ARCHIVE_SNAPSHOT_KIND, "sealed import receipt must bind the archive snapshot kind")
                require(errors, archive_snapshot.get("snapshot_policy") == contract.HANDOFF_ARCHIVE_SNAPSHOT_POLICY, "sealed import receipt must bind the nofollow archive snapshot policy")
                require(errors, archive_snapshot.get("canonical_zip_metadata_policy") == contract.HANDOFF_ARCHIVE_CANONICAL_METADATA_POLICY, "sealed import receipt archive snapshot must bind the canonical ZIP metadata policy")
                require(errors, archive_snapshot.get("byte_sha256") == transport.get("byte_sha256"), "sealed archive snapshot digest must match source_transport byte_sha256")
                require(errors, archive_snapshot.get("archive_size_bytes") == transport.get("archive_size_bytes"), "sealed archive snapshot size must match source_transport archive_size_bytes")
                require(errors, archive_snapshot.get("source_path") == transport.get("path"), "sealed archive snapshot must bind the operator source path")
                require(errors, transport.get("unsealed_scratch_handoff") == record.get("source_handoff_dir"), "sealed import receipt must connect scratch source to source_handoff_dir")
                require(errors, transport.get("scratch_cleanup") == "removed-after-import-or-failure", "sealed import receipt must record scratch cleanup behavior")
                require(errors, archive_snapshot.get("cleanup") == transport.get("scratch_cleanup"), "sealed archive snapshot cleanup must match scratch cleanup behavior")
                invariants = record.get("invariants", {}) if isinstance(record.get("invariants"), dict) else {}
                require(errors, invariants.get("import_receipt_binds_source_transport") is True, "sealed import receipt must assert source transport binding")
                require(errors, invariants.get("directory_import_copies_allowed_regular_files_without_following_symlinks") is True, "sealed import must still use the nofollow staging copy path")
                require(errors, invariants.get("import_receipt_binds_copied_snapshot_not_mutable_source") is True, "sealed import must bind the copied scratch snapshot")
                require(errors, invariants.get("import_receipt_binds_copied_snapshot_manifest_digest") is True, "sealed import must bind the copied scratch snapshot manifest digest")
                require(errors, invariants.get("staged_files_and_import_receipt_fsynced_before_publish") is True, "sealed import must fsync staged files and import receipt before publish")
                require(errors, invariants.get("import_parent_directory_fsynced_after_publish") is True, "sealed import must fsync the import parent after publish")
                require(errors, invariants.get("sealed_import_receipt_binds_archive_digest") is True, "sealed import receipt must assert sealed archive digest binding")
                require(errors, invariants.get("sealed_import_receipt_binds_copied_archive_snapshot") is True, "sealed import receipt must assert copied archive snapshot binding")
                require(errors, invariants.get("sealed_import_archive_snapshot_taken_before_zip_validation") is True, "sealed import receipt must assert archive snapshot before ZIP validation")
                require(errors, invariants.get("sealed_import_rejects_noncanonical_zip_metadata") is True, "sealed import receipt must assert noncanonical ZIP metadata rejection")
                require(errors, invariants.get("directory_import_receipt_binds_source_handoff") is False, "sealed import receipt must not claim direct directory provenance")
                require(errors, record.get("copy_policy") == contract.DIRECTORY_IMPORT_COPY_POLICY, "sealed import must bind the shared nofollow staging copy policy")
                require(errors, record.get("durable_write_policy") == contract.IMPORT_DURABLE_WRITE_POLICY, "sealed import must bind the durable fsync write policy")
                require(errors, record.get("copied_handoff_snapshot") == copied_snapshot_manifest(import_dir / "handoff"), "sealed import must bind the copied handoff snapshot manifest")
                require(errors, record.get("atomic_publish_policy") == "copy-verify-fsync-write-receipt-fsync-then-rename-and-fsync-parent-to-full-digest-import-dir", "sealed import must keep the directory import fsync atomic publish policy")

                missing_transport_root = tmp / "missing-sealed-source-transport-imports"
                shutil.copytree(import_root, missing_transport_root)
                missing_transport_dir = next(missing_transport_root.iterdir())
                missing_transport_record = load_json(missing_transport_dir / contract.IMPORT_RECEIPT_NAME)
                missing_transport_record.pop("source_transport", None)
                write_pretty_json(missing_transport_dir / contract.IMPORT_RECEIPT_NAME, missing_transport_record)
                missing_transport_audit = run_tool([AUDIT_REL, str(missing_transport_root), "--allow-checker-simulation"])
                require(errors, missing_transport_audit.returncode != 0, "auditor must reject sealed imports without source_transport provenance")
                require(errors, "source_transport provenance" in missing_transport_audit.stderr, "sealed missing source_transport rejection should name provenance")

        before_duplicate = import_root_children(import_root)
        duplicate = run_tool([SEALED_IMPORT_REL, str(archive), "--import-root", str(import_root), "--allow-checker-simulation"])
        require(errors, duplicate.returncode != 0, "sealed importer must refuse duplicate full copied-snapshot imports without --replace or --reuse-existing-import")
        require(errors, "import directory already exists" in duplicate.stderr, "duplicate sealed import rejection should identify the existing digest import")
        require(errors, import_root_children(import_root) == before_duplicate, "duplicate sealed import must not alter the existing import or leave scratch state")
        require(errors, not any(child.name.startswith(".imports.sealed-handoff-import-") for child in tmp.iterdir()), "duplicate sealed import must cleanup scratch state")

        reused = run_tool([SEALED_IMPORT_REL, str(archive), "--import-root", str(import_root), "--allow-checker-simulation", "--reuse-existing-import"])
        require(errors, reused.returncode == 0, f"sealed importer --reuse-existing-import should accept an audit-clean matching digest import: {reused.stdout} {reused.stderr}")
        require(errors, "existing_import_reuse_policy" in reused.stdout, "sealed importer reuse output must print the reuse policy")
        require(errors, import_root_children(import_root) == before_duplicate, "sealed reuse should not replace or add import directories")
        require(errors, not any(child.name.startswith(".imports.sealed-handoff-import-") for child in tmp.iterdir()), "sealed reuse must cleanup scratch state")

        replaced = run_tool([SEALED_IMPORT_REL, str(archive), "--import-root", str(import_root), "--allow-checker-simulation", "--replace"])
        require(errors, replaced.returncode == 0, f"sealed importer --replace should delegate to atomic replacement import: {replaced.stdout} {replaced.stderr}")
        require(errors, import_root_children(import_root) == before_duplicate, "sealed replace should leave only the digest import directory")

        compressed = tmp / "compressed.zip"
        make_compressed_archive(archive, compressed)
        compressed_import = run_tool([SEALED_IMPORT_REL, str(compressed), "--import-root", str(tmp / "compressed-imports"), "--allow-checker-simulation"])
        require(errors, compressed_import.returncode != 0, "sealed importer must reject compressed transport archives")
        require(errors, "must use stored deterministic ZIP entry" in compressed_import.stderr, "compressed sealed import rejection should come from archive validation")

        commented = tmp / "commented.zip"
        make_archive_with_comment(archive, commented)
        commented_import = run_tool([SEALED_IMPORT_REL, str(commented), "--import-root", str(tmp / "commented-imports"), "--allow-checker-simulation"])
        require(errors, commented_import.returncode != 0, "sealed importer must reject ZIP archive comments")
        require(errors, "archive comment must be empty" in commented_import.stderr, "commented archive rejection should come from canonical ZIP metadata validation")

        extra_field = tmp / "entry-extra.zip"
        make_archive_with_entry_extra(archive, extra_field)
        extra_import = run_tool([SEALED_IMPORT_REL, str(extra_field), "--import-root", str(tmp / "extra-imports"), "--allow-checker-simulation"])
        require(errors, extra_import.returncode != 0, "sealed importer must reject ZIP entry extra fields")
        require(errors, "must not carry ZIP extra fields" in extra_import.stderr, "entry-extra rejection should come from canonical ZIP metadata validation")

        reordered = tmp / "entry-order.zip"
        make_reordered_archive(archive, reordered)
        reordered_import = run_tool([SEALED_IMPORT_REL, str(reordered), "--import-root", str(tmp / "reordered-imports"), "--allow-checker-simulation"])
        require(errors, reordered_import.returncode != 0, "sealed importer must reject noncanonical ZIP entry order")
        require(errors, "canonical sorted handoff order" in reordered_import.stderr, "entry-order rejection should come from canonical ZIP metadata validation")

        missing_file_type = tmp / "missing-file-type.zip"
        make_archive_without_regular_file_type(archive, missing_file_type)
        missing_type_import = run_tool([SEALED_IMPORT_REL, str(missing_file_type), "--import-root", str(tmp / "missing-type-imports"), "--allow-checker-simulation"])
        require(errors, missing_type_import.returncode != 0, "sealed importer must reject ZIP entries missing regular-file mode bits")
        require(errors, "exact regular-file mode" in missing_type_import.stderr, "file-mode rejection should come from canonical ZIP metadata validation")

        symlink_archive = tmp / "archive-symlink.zip"
        symlink_archive.symlink_to(archive)
        symlink_import = run_tool([SEALED_IMPORT_REL, str(symlink_archive), "--import-root", str(tmp / "symlink-imports"), "--allow-checker-simulation"])
        require(errors, symlink_import.returncode != 0, "sealed importer must reject a symlinked archive path")
        require(
            errors,
            "handoff archive must" in symlink_import.stderr and "symlink" in symlink_import.stderr,
            "symlink archive rejection should come from the safe unsealer",
        )

        race_handoff_a = tmp / "race-handoff-a"
        race_handoff_b = tmp / "race-handoff-b"
        build_checker_handoff(race_handoff_a, smoke_id_suffix="archive-snapshot-a")
        build_checker_handoff(race_handoff_b, smoke_id_suffix="archive-snapshot-b")
        archive_a = tmp / "race-a.zip"
        archive_b = tmp / "race-b.zip"
        race_source = tmp / "race-source.zip"
        for handoff_dir, out_archive in [(race_handoff_a, archive_a), (race_handoff_b, archive_b)]:
            sealed_race = run_tool([SEAL_REL, str(handoff_dir), "--output", str(out_archive), "--allow-checker-simulation"])
            require(errors, sealed_race.returncode == 0, f"race handoff should seal: {sealed_race.stdout} {sealed_race.stderr}")
        shutil.copy2(archive_a, race_source)
        original_snapshot = sealed_importer.handoff_unsealer.copy_archive_snapshot
        flipped = {"done": False}

        def flipping_snapshot(source_archive: Path, snapshot_path: Path) -> dict[str, object]:
            info = original_snapshot(source_archive, snapshot_path)
            if Path(source_archive).resolve() == race_source.resolve() and not flipped["done"]:
                shutil.copy2(archive_b, race_source)
                flipped["done"] = True
            return info

        sealed_importer.handoff_unsealer.copy_archive_snapshot = flipping_snapshot
        handoff_unsealer.copy_archive_snapshot = flipping_snapshot
        try:
            race_import = sealed_importer.import_sealed_handoff(race_source, import_root=tmp / "race-imports", allow_checker_simulation=True)
        finally:
            sealed_importer.handoff_unsealer.copy_archive_snapshot = original_snapshot
            handoff_unsealer.copy_archive_snapshot = original_snapshot
        require(errors, flipped["done"], "sealed importer race regression must mutate source archive after snapshot")
        expected_a = contract.import_directory_name("checker-simulation-non-proof", copied_snapshot_manifest(race_handoff_a)["canonical_sha256"])
        expected_b = contract.import_directory_name("checker-simulation-non-proof", copied_snapshot_manifest(race_handoff_b)["canonical_sha256"])
        require(errors, race_import.name == expected_a, "sealed import must follow the copied archive snapshot handoff bytes after source mutation")
        require(errors, race_import.name != expected_b, "sealed import must not follow the post-snapshot mutated archive")
        require(errors, sha256_file(race_source) == sha256_file(archive_b), "race source archive should be mutated after snapshot")
        race_record = load_json(race_import / contract.IMPORT_RECEIPT_NAME)
        if isinstance(race_record, dict):
            race_transport = race_record.get("source_transport", {}) if isinstance(race_record.get("source_transport"), dict) else {}
            race_snapshot = race_transport.get("archive_snapshot", {}) if isinstance(race_transport.get("archive_snapshot"), dict) else {}
            require(errors, race_transport.get("byte_sha256") == sha256_file(archive_a), "sealed import receipt must bind the pre-mutation copied archive snapshot digest")
            require(errors, race_snapshot.get("snapshot_policy") == contract.HANDOFF_ARCHIVE_SNAPSHOT_POLICY, "race import must record the archive snapshot policy")
    return errors


def surface_errors() -> list[str]:
    errors: list[str] = []
    for rel in [SEALED_IMPORT_REL, SEAL_REL, contract.HOST_PROOF_HANDOFF_UNSEALER_REL, contract.HOST_PROOF_HANDOFF_IMPORTER_REL, AUDIT_REL]:
        require(errors, (ROOT / rel).exists(), f"missing {rel}")
    tool_text = (ROOT / SEALED_IMPORT_REL).read_text(encoding="utf-8", errors="replace")
    for token in [
        "SEALED_IMPORT_POLICY",
        "unseal_archive",
        "import_handoff",
        "audit_import_root",
        "shutil.rmtree",
        "default mode accepts only strict",
        "--allow-checker-simulation",
        "source_transport",
        "SEALED_IMPORT_SOURCE_KIND",
        "DIRECTORY_IMPORT_COPY_POLICY",
        "IMPORT_DURABLE_WRITE_POLICY",
        "copy_archive_snapshot",
        "archive_snapshot",
        "HANDOFF_ARCHIVE_SNAPSHOT_POLICY",
        "HANDOFF_ARCHIVE_CANONICAL_METADATA_POLICY",
        "canonical_zip_metadata_policy",
        "--require-primary-target",
        "SEALED_IMPORT_PRIMARY_TARGET_POLICY",
        "SEALED_IMPORT_FAILURE_CLEANUP_POLICY",
        "SEALED_IMPORT_EXISTING_REUSE_POLICY",
        "SEALED_IMPORT_LOCK_POLICY",
        "_sealed_import_lock",
        "--reuse-existing-import",
        "_reuse_existing_import_if_matching_archive",
        "pre-import audit failed",
    ]:
        require(errors, token in tool_text, f"sealed importer must bind token {token!r}")
    contract_text = (ROOT / contract.HOST_PROOF_CONTRACT_REL).read_text(encoding="utf-8", errors="replace")
    for token in ["HOST_PROOF_SEALED_HANDOFF_IMPORTER_REL", SEALED_IMPORT_REL, "SEALED_IMPORT_POLICY", "SEALED_IMPORT_PRIMARY_TARGET_POLICY", "SEALED_IMPORT_FAILURE_CLEANUP_POLICY", "SEALED_IMPORT_EXISTING_REUSE_POLICY", "SEALED_IMPORT_LOCK_POLICY", "IMPORT_RECEIPT_SOURCE_TRANSPORT_POLICY", "IMPORT_RECEIPT_SNAPSHOT_POLICY", "IMPORT_DURABLE_WRITE_POLICY", "HANDOFF_ARCHIVE_SNAPSHOT_POLICY", "HANDOFF_ARCHIVE_CANONICAL_METADATA_POLICY"]:
        require(errors, token in contract_text, f"shared proof-tool contract must bind sealed importer token {token!r}")
    for rel in [DOC_REL, START_REL, OPERATOR_PACKET_REL]:
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for token in [SEALED_IMPORT_REL, "sealed", "import", "audit", "--require-primary-target", "--reuse-existing-import", "lock"]:
            require(errors, token in text, f"{rel} missing sealed-import operator token {token!r}")
    start_text = (ROOT / START_REL).read_text(encoding="utf-8", errors="replace")
    require(errors, "exactly 18 FreeBSD proof-tool rows" in start_text, "start-here doc must reflect the 18-row proof-tool set")
    return errors


def main() -> int:
    errors = sealed_import_mode_errors() + surface_errors()
    if errors:
        print("FreeBSD host proof sealed importer check FAILED.")
        for error in errors:
            print("-", error)
        return 1
    print("FreeBSD host proof sealed importer check OK")
    print("Sealed archives now unseal, import, audit, and cleanup through one strict command")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
