#!/usr/bin/env python3
"""Guard deterministic sealing of scarce FreeBSD host-proof handoffs.

The real proof handoff is currently a small directory.  In practice, the scarce
operator will usually move it through chat, storage, or another machine, where a
single finite archive is safer than three loose files.  This check proves the
archive helper remains default-real-proof-only, deterministic, finite, and wired
into the operator packet without introducing a new proof status.
"""
from __future__ import annotations

import hashlib
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from freebsd import host_proof_contract as contract

ROOT = Path(__file__).resolve().parents[1]
SEAL_REL = contract.HOST_PROOF_HANDOFF_SEALER_REL
UNSEAL_REL = contract.HOST_PROOF_HANDOFF_UNSEALER_REL
FINALIZER_REL = contract.HOST_PROOF_FINALIZER_REL
VERIFY_REL = contract.HOST_PROOF_HANDOFF_VERIFIER_REL
PACKET_REL = "tools/freebsd/print_real_host_proof_operator_packet.py"
PACKET_DOC_REL = "docs/current/freebsd-real-host-proof-operator-packet.md"
SMOKE_DOC_REL = "docs/current/removable-media-freebsd-host-smoke.md"
SUCCESS_SIM_REL = "validation/removable-media-local-freebsd-host-smoke.success-simulation.json"
GENERATED_AT = "2026-06-12T23:00:00Z"
EXPECTED_ZIP_NAMES = sorted([contract.BUNDLE_NAME, contract.README_NAME, contract.RECEIPT_NAME, contract.SUMS_NAME])
FIXED_ZIP_DATE = contract.HANDOFF_ARCHIVE_FIXED_ZIP_DATE


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def run_tool(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-B", "-S", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def load_sealer_module():
    spec = importlib.util.spec_from_file_location("derivebsd_host_proof_sealer_under_test", ROOT / SEAL_REL)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load sealer module spec")
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


def build_checker_handoff(directory: Path) -> None:
    directory.mkdir()
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
        "Checker-simulation handoff for deterministic sealer mechanics only; not release proof.\n",
        encoding="utf-8",
    )
    write_sums(directory)


def _zip_rows(path: Path) -> list[zipfile.ZipInfo]:
    with zipfile.ZipFile(path) as zf:
        return zf.infolist()


def archive_mode_errors() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="derivebsd-host-proof-seal-check-") as td_name:
        tmp = Path(td_name)
        handoff = tmp / "handoff"
        build_checker_handoff(handoff)

        default_archive = tmp / "default.zip"
        default = run_tool([SEAL_REL, str(handoff), "--output", str(default_archive)])
        require(errors, default.returncode != 0, "default sealer must reject checker-simulation-non-proof handoff")
        require(errors, "default handoff verification accepts only real-host-proof" in default.stderr, "default sealer rejection should come from strict handoff verification")
        require(errors, not default_archive.exists(), "failed default seal must not leave the requested archive")

        archive_a = tmp / "handoff-a.zip"
        archive_b = tmp / "handoff-b.zip"
        allowed_a = run_tool([SEAL_REL, str(handoff), "--output", str(archive_a), "--allow-checker-simulation"])
        allowed_b = run_tool([SEAL_REL, str(handoff), "--output", str(archive_b), "--allow-checker-simulation"])
        require(errors, allowed_a.returncode == 0, f"explicit checker seal should pass: {allowed_a.stdout} {allowed_a.stderr}")
        require(errors, allowed_b.returncode == 0, f"second checker seal should pass: {allowed_b.stdout} {allowed_b.stderr}")
        if archive_a.exists() and archive_b.exists():
            require(errors, sha256_file(archive_a) == sha256_file(archive_b), "deterministic seal should produce identical archive bytes for the same handoff")
            with zipfile.ZipFile(archive_a) as zf:
                require(errors, zf.comment == b"", "sealed archive must not carry a ZIP archive comment")
                rows = zf.infolist()
            require(errors, [row.filename for row in rows] == EXPECTED_ZIP_NAMES, "sealed archive must contain exactly the sorted finite handoff files")
            for row in rows:
                require(errors, row.date_time == FIXED_ZIP_DATE, f"{row.filename} must use fixed ZIP timestamp")
                require(errors, row.compress_type == zipfile.ZIP_STORED, f"{row.filename} must use stored deterministic ZIP entry")
                require(errors, row.create_system == 3, f"{row.filename} must use Unix create_system metadata")
                require(errors, row.extra == b"", f"{row.filename} must not carry ZIP extra fields")
                require(errors, row.comment == b"", f"{row.filename} must not carry ZIP entry comments")
                require(errors, (row.external_attr >> 16) & 0o777777 == contract.HANDOFF_ARCHIVE_FIXED_FILE_MODE, f"{row.filename} must use exact normalized regular-file mode")

        alternate = tmp / "alternate-handoff"
        build_checker_handoff(alternate)
        alternate_note = "Alternate checksum-bound README copied by the seal staging snapshot.\n"
        (alternate / contract.README_NAME).write_text(alternate_note, encoding="utf-8")
        write_sums(alternate)
        patched_archive = tmp / "patched-staging-source.zip"
        sealer_module = load_sealer_module()
        original_copy = sealer_module.handoff_importer.copy_handoff

        def copy_alternate_handoff(_source: Path, destination: Path) -> None:
            original_copy(alternate, destination)

        sealer_module.handoff_importer.copy_handoff = copy_alternate_handoff
        try:
            patched_out = sealer_module.seal_handoff(handoff, output=patched_archive, allow_checker_simulation=True)
        finally:
            sealer_module.handoff_importer.copy_handoff = original_copy
        require(errors, patched_out == patched_archive, "module sealer should return the requested archive path")
        with zipfile.ZipFile(patched_archive) as zf:
            archived_note = zf.read(contract.README_NAME).decode("utf-8")
        require(errors, archived_note == alternate_note, "sealer must archive the nofollow copied staging snapshot, not reread the mutable source after verification")

        duplicate = run_tool([SEAL_REL, str(handoff), "--output", str(archive_a), "--allow-checker-simulation"])
        require(errors, duplicate.returncode != 0, "sealer must refuse existing archive without --replace")
        require(errors, "archive already exists" in duplicate.stderr, "duplicate archive refusal should name existing archive")

        replaced = run_tool([SEAL_REL, str(handoff), "--output", str(archive_a), "--allow-checker-simulation", "--replace"])
        require(errors, replaced.returncode == 0, "sealer --replace should rewrite an existing regular archive")

        symlink_target = tmp / "target.zip"
        symlink_target.write_text("do-not-overwrite\n", encoding="utf-8")
        symlink_out = tmp / "symlink.zip"
        symlink_out.symlink_to(symlink_target)
        symlink_proc = run_tool([SEAL_REL, str(handoff), "--output", str(symlink_out), "--allow-checker-simulation", "--replace"])
        require(errors, symlink_proc.returncode != 0, "sealer must refuse symlink archive outputs")
        require(errors, symlink_target.read_text(encoding="utf-8") == "do-not-overwrite\n", "symlink output refusal must not overwrite the target")

        extra = tmp / "extra"
        shutil.copytree(handoff, extra)
        (extra / "debug.log").write_text("not part of proof\n", encoding="utf-8")
        extra_proc = run_tool([SEAL_REL, str(extra), "--output", str(tmp / "extra.zip"), "--allow-checker-simulation"])
        require(errors, extra_proc.returncode != 0, "sealer must refuse handoffs with loose files through the verifier")
        require(errors, "unexpected files" in extra_proc.stderr, "loose-file seal refusal should name unexpected files")

        symlink_handoff = tmp / "handoff-root-symlink"
        symlink_handoff.symlink_to(handoff, target_is_directory=True)
        symlink_seal = run_tool([SEAL_REL, str(symlink_handoff), "--output", str(tmp / "symlink-source.zip"), "--allow-checker-simulation"])
        require(errors, symlink_seal.returncode != 0, "sealer must reject a symlinked handoff directory root before archive write")
        require(errors, "handoff directory must" in symlink_seal.stderr and "symlink" in symlink_seal.stderr, "symlink-source seal rejection should name the handoff root")

        output_parent_target = tmp / "archive-output-parent-target"
        output_parent_target.mkdir()
        output_parent_link = tmp / "archive-output-parent-link"
        output_parent_link.symlink_to(output_parent_target, target_is_directory=True)
        ancestor_output = run_tool([SEAL_REL, str(handoff), "--output", str(output_parent_link / "sealed.zip"), "--allow-checker-simulation"])
        require(errors, ancestor_output.returncode != 0, "sealer must reject archive outputs with symlink ancestors")
        require(errors, "archive output must not contain existing symlink components" in ancestor_output.stderr, "archive symlink-ancestor rejection should name the output path")
        require(errors, not (output_parent_target / "sealed.zip").exists(), "archive symlink-ancestor refusal must not write through the redirected parent")

        handoff_parent_target = tmp / "handoff-parent-target"
        handoff_parent_target.mkdir()
        shutil.copytree(handoff, handoff_parent_target / "handoff")
        handoff_parent_link = tmp / "handoff-parent-link"
        handoff_parent_link.symlink_to(handoff_parent_target, target_is_directory=True)
        ancestor_handoff_seal = run_tool([SEAL_REL, str(handoff_parent_link / "handoff"), "--output", str(tmp / "ancestor-source.zip"), "--allow-checker-simulation"])
        require(errors, ancestor_handoff_seal.returncode != 0, "sealer must reject handoff sources with symlink ancestors")
        require(errors, "handoff directory must not contain existing symlink components" in ancestor_handoff_seal.stderr, "handoff symlink-ancestor seal rejection should be operator-visible")

        archive_parent_target = tmp / "archive-parent-target"
        archive_parent_target.mkdir()
        shutil.copy2(archive_a, archive_parent_target / "handoff.zip")
        archive_parent_link = tmp / "archive-parent-link"
        archive_parent_link.symlink_to(archive_parent_target, target_is_directory=True)
        archive_ancestor_unseal = run_tool([UNSEAL_REL, str(archive_parent_link / "handoff.zip"), "--output-dir", str(tmp / "archive-ancestor-out"), "--allow-checker-simulation"])
        require(errors, archive_ancestor_unseal.returncode != 0, "unsealer must reject archive inputs with symlink ancestors before snapshot copy")
        require(errors, "handoff archive must not contain existing symlink components" in archive_ancestor_unseal.stderr, "archive symlink-ancestor unseal rejection should be visible")

        default_unseal_dir = tmp / "default-unseal"
        default_unseal = run_tool([UNSEAL_REL, str(archive_a), "--output-dir", str(default_unseal_dir)])
        require(errors, default_unseal.returncode != 0, "default unsealer must reject checker-simulation-non-proof archive")
        require(errors, "default handoff verification accepts only real-host-proof" in default_unseal.stderr, "default unseal rejection should come from strict handoff verification")
        require(errors, not default_unseal_dir.exists(), "failed default unseal must not publish the requested handoff directory")

        unseal_parent_target = tmp / "unseal-output-parent-target"
        unseal_parent_target.mkdir()
        unseal_parent_link = tmp / "unseal-output-parent-link"
        unseal_parent_link.symlink_to(unseal_parent_target, target_is_directory=True)
        unseal_ancestor = run_tool([UNSEAL_REL, str(archive_a), "--output-dir", str(unseal_parent_link / "unsealed"), "--allow-checker-simulation"])
        require(errors, unseal_ancestor.returncode != 0, "unsealer must reject output directories with symlink ancestors before extraction")
        require(errors, "handoff output directory must not contain existing symlink components" in unseal_ancestor.stderr, "unseal output symlink-ancestor refusal should be visible")
        require(errors, not (unseal_parent_target / "unsealed").exists(), "unseal symlink-ancestor refusal must not publish through redirected parent")

        unsealed_dir = tmp / "unsealed"
        allowed_unseal = run_tool([UNSEAL_REL, str(archive_a), "--output-dir", str(unsealed_dir), "--allow-checker-simulation"])
        require(errors, allowed_unseal.returncode == 0, f"explicit checker unseal should pass: {allowed_unseal.stdout} {allowed_unseal.stderr}")
        if unsealed_dir.exists():
            verify = run_tool([VERIFY_REL, str(unsealed_dir), "--allow-checker-simulation"])
            require(errors, verify.returncode == 0, f"unsealed handoff should verify: {verify.stdout} {verify.stderr}")
            require(errors, sorted(child.name for child in unsealed_dir.iterdir()) == EXPECTED_ZIP_NAMES, "unsealed directory must contain exactly the finite handoff files")

        duplicate_unseal = run_tool([UNSEAL_REL, str(archive_a), "--output-dir", str(unsealed_dir), "--allow-checker-simulation"])
        require(errors, duplicate_unseal.returncode != 0, "unsealer must refuse existing output without --replace")
        require(errors, "output directory already exists" in duplicate_unseal.stderr, "duplicate output refusal should name existing directory")

        replaced_unseal = run_tool([UNSEAL_REL, str(archive_a), "--output-dir", str(unsealed_dir), "--allow-checker-simulation", "--replace"])
        require(errors, replaced_unseal.returncode == 0, "unsealer --replace should republish an existing real directory after staging verification")
        require(errors, not any(child.name.startswith(f".{unsealed_dir.name}.replace-backup-") for child in tmp.iterdir()), "unsealer --replace must not leave replacement backup residue")

        stale_backup = tmp / f".{unsealed_dir.name}.replace-backup-locked"
        stale_backup.mkdir()
        stale_backup_proc = run_tool([UNSEAL_REL, str(archive_a), "--output-dir", str(unsealed_dir), "--allow-checker-simulation", "--replace"])
        require(errors, stale_backup_proc.returncode != 0, "unsealer --replace must refuse when a replacement backup path already exists")
        require(errors, "stale unseal replacement backup" in stale_backup_proc.stderr, "stale backup refusal should name the replacement backup")
        shutil.rmtree(stale_backup)

        traversal = tmp / "traversal.zip"
        with zipfile.ZipFile(traversal, "w") as zf:
            zf.writestr("../evil", b"nope")
            zf.writestr(contract.RECEIPT_NAME, b"{}")
            zf.writestr(contract.BUNDLE_NAME, b"{}")
            zf.writestr(contract.SUMS_NAME, b"")
        traversal_out = tmp / "traversal-out"
        traversal_proc = run_tool([UNSEAL_REL, str(traversal), "--output-dir", str(traversal_out), "--allow-checker-simulation"])
        require(errors, traversal_proc.returncode != 0, "unsealer must reject path-traversal archive entries before extraction")
        require(errors, "unexpected or unsafe filename" in traversal_proc.stderr, "path-traversal archive rejection should name unsafe filename")
        require(errors, not (tmp / "evil").exists(), "path-traversal archive rejection must not create sibling files")

        compressed = tmp / "compressed.zip"
        with zipfile.ZipFile(compressed, "w") as zf:
            for name in EXPECTED_ZIP_NAMES:
                info = zipfile.ZipInfo(name, FIXED_ZIP_DATE)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = (0o100644 & 0xFFFF) << 16
                zf.writestr(info, (handoff / name).read_bytes())
        compressed_out = tmp / "compressed-out"
        compressed_proc = run_tool([UNSEAL_REL, str(compressed), "--output-dir", str(compressed_out), "--allow-checker-simulation"])
        require(errors, compressed_proc.returncode != 0, "unsealer must reject compressed non-deterministic archive entries before extraction")
        require(errors, "must use stored deterministic ZIP entry" in compressed_proc.stderr, "compressed archive rejection should name the stored-entry invariant")
        require(errors, not compressed_out.exists(), "compressed archive rejection must not publish output")

        reordered = tmp / "reordered.zip"
        with zipfile.ZipFile(reordered, "w") as zf:
            for name in reversed(EXPECTED_ZIP_NAMES):
                info = zipfile.ZipInfo(name, FIXED_ZIP_DATE)
                info.compress_type = zipfile.ZIP_STORED
                info.create_system = 3
                info.external_attr = (contract.HANDOFF_ARCHIVE_FIXED_FILE_MODE & 0xFFFF) << 16
                zf.writestr(info, (handoff / name).read_bytes())
        reordered_out = tmp / "reordered-out"
        reordered_proc = run_tool([UNSEAL_REL, str(reordered), "--output-dir", str(reordered_out), "--allow-checker-simulation"])
        require(errors, reordered_proc.returncode != 0, "unsealer must reject archives whose finite entries are not in canonical sorted order")
        require(errors, "canonical sorted handoff order" in reordered_proc.stderr, "reordered archive rejection should name canonical entry order")
        require(errors, not reordered_out.exists(), "reordered archive rejection must not publish output")

        missing_file_type = tmp / "missing-file-type.zip"
        with zipfile.ZipFile(missing_file_type, "w") as zf:
            for name in EXPECTED_ZIP_NAMES:
                info = zipfile.ZipInfo(name, FIXED_ZIP_DATE)
                info.compress_type = zipfile.ZIP_STORED
                info.create_system = 3
                info.external_attr = (0o644 & 0xFFFF) << 16
                zf.writestr(info, (handoff / name).read_bytes())
        missing_file_type_out = tmp / "missing-file-type-out"
        missing_file_type_proc = run_tool([UNSEAL_REL, str(missing_file_type), "--output-dir", str(missing_file_type_out), "--allow-checker-simulation"])
        require(errors, missing_file_type_proc.returncode != 0, "unsealer must reject entries missing exact regular-file mode bits")
        require(errors, "exact regular-file mode" in missing_file_type_proc.stderr, "missing file type rejection should name exact regular-file mode")
        require(errors, not missing_file_type_out.exists(), "missing file type archive rejection must not publish output")
    return errors


def surface_errors() -> list[str]:
    errors: list[str] = []
    for rel in [SEAL_REL, UNSEAL_REL, VERIFY_REL, contract.HOST_PROOF_CONTRACT_REL]:
        path = ROOT / rel
        require(errors, path.exists(), f"missing {rel}")
    seal_text = (ROOT / SEAL_REL).read_text(encoding="utf-8", errors="replace")
    unseal_text = (ROOT / UNSEAL_REL).read_text(encoding="utf-8", errors="replace")
    for token in [
        "verify_removable_media_local_fallback_host_proof_handoff",
        "validate_handoff_dir",
        "ZIP_STORED",
        "FIXED_ZIP_DATE",
        "HANDOFF_ALLOWED_NAMES",
        "refusing to write archive through symlink path",
        "archive already exists",
        "ARCHIVE_FORMAT",
        "_checked_handoff_dir",
        "_copy_handoff_for_seal",
        "handoff_importer.copy_handoff",
        "handoff directory must not be a symlink",
        "require_no_existing_symlink_component",
        "symlink components before host proof work",
    ]:
        require(errors, token in seal_text, f"{SEAL_REL} missing deterministic-seal token {token!r}")
    for token in [
        "ZipFile",
        "validate_handoff_dir",
        "unexpected or unsafe filename",
        "os.O_EXCL",
        "os.replace",
        "output directory already exists",
        "MAX_MEMBER_BYTES",
        "MAX_ARCHIVE_BYTES",
        "must use stored deterministic ZIP entry",
        "canonical sorted handoff order",
        "exact regular-file mode",
        "O_NOFOLLOW",
        "_atomic_publish_unsealed",
        "replace-backup",
        "stale unseal replacement backup",
        "require_no_existing_symlink_component",
        "symlink components before host proof work",
    ]:
        require(errors, token in unseal_text, f"{UNSEAL_REL} missing safe-unseal token {token!r}")
    for banned in ["--allow-refusal", "--allow-failed"]:
        require(errors, banned not in seal_text, f"{SEAL_REL} must not expose non-proof flag {banned!r}")
        require(errors, banned not in unseal_text, f"{UNSEAL_REL} must not expose non-proof flag {banned!r}")
    contract_text = (ROOT / contract.HOST_PROOF_CONTRACT_REL).read_text(encoding="utf-8", errors="replace")
    require(errors, "HOST_PROOF_HANDOFF_SEALER_REL" in contract_text, "shared proof-tool contract must name the handoff sealer")
    require(errors, "HOST_PROOF_HANDOFF_UNSEALER_REL" in contract_text, "shared proof-tool contract must name the handoff unsealer")
    require(errors, "MAX_HANDOFF_MEMBER_BYTES" in contract_text, "shared proof-tool contract must bind handoff member size limit")
    require(errors, "HANDOFF_ARCHIVE_FORMAT" in contract_text, "shared proof-tool contract must bind handoff archive format")
    require(errors, SEAL_REL in contract_text, "handoff sealer must be part of the bound proof-tool set")
    require(errors, UNSEAL_REL in contract_text, "handoff unsealer must be part of the bound proof-tool set")
    packet_source = (ROOT / PACKET_REL).read_text(encoding="utf-8", errors="replace")
    for token in ["HOST_PROOF_HANDOFF_SEALER_REL", "HOST_PROOF_HANDOFF_UNSEALER_REL", "deterministic", "sealed handoff"]:
        require(errors, token in packet_source, f"{PACKET_REL} missing sealer token {token!r}")
    for rel in [PACKET_DOC_REL, SMOKE_DOC_REL]:
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for token in [SEAL_REL, UNSEAL_REL, "deterministic", "sealed handoff", "symlinked handoff", "symlink ancestor", "finite size", "atomic publish"]:
            require(errors, token in text, f"{rel} missing sealer token {token!r}")
    packet = run_tool([PACKET_REL])
    require(errors, packet.returncode == 0, "operator packet should still print")
    require(errors, SEAL_REL in packet.stdout, "operator packet output must include the handoff sealer command")
    require(errors, UNSEAL_REL in packet.stdout, "operator packet output must include the handoff unsealer command")
    return errors


def main() -> int:
    errors = archive_mode_errors() + surface_errors()
    if errors:
        print("FreeBSD host proof handoff archive check FAILED.")
        for error in errors:
            print("-", error)
        return 1
    print("FreeBSD host proof handoff archive check OK")
    print("Sealer/unsealer are default-real-proof-only, deterministic, finite, and wired into the operator packet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
