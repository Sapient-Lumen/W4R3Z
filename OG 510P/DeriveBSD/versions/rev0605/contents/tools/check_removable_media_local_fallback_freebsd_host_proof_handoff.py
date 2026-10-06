#!/usr/bin/env python3
"""Guard the real FreeBSD host-proof handoff/import path.

The proof bundle gate stops checked-in evidence theatre.  This checker guards the
operator package before import: a real host handoff must be a finite directory
with receipt.json, bundle.json, and SHA256SUMS, and default verification must
accept only strict real-host proof.  The checker exercises the mechanics with the
existing checker-only simulation while proving that default import mode rejects
that non-proof handoff.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from freebsd import host_proof_contract as contract

ROOT = Path(__file__).resolve().parents[1]
VERIFY_REL = "tools/freebsd/verify_removable_media_local_fallback_host_proof_handoff.py"
FINALIZER_REL = "tools/freebsd/finalize_removable_media_local_fallback_host_proof_bundle.py"
COLLECTOR_REL = "tools/freebsd/collect_removable_media_local_fallback_host_proof.sh"
DOC_REL = "docs/current/removable-media-freebsd-host-smoke.md"
SUCCESS_SIM_REL = "validation/removable-media-local-freebsd-host-smoke.success-simulation.json"
GENERATED_AT = "2026-06-12T23:00:00Z"


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_tool(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-B", "-S", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def write_sums(directory: Path, *, receipt_name: str = "receipt.json", bundle_name: str = "bundle.json") -> None:
    names = [receipt_name, bundle_name]
    readme = contract.README_NAME
    if (directory / readme).exists():
        names.append(readme)
    (directory / "SHA256SUMS").write_text(
        "".join(f"{sha256_file(directory / name)}  {name}\n" for name in names),
        encoding="utf-8",
    )


def build_checker_handoff(directory: Path) -> None:
    directory.mkdir()
    shutil.copy2(ROOT / SUCCESS_SIM_REL, directory / "receipt.json")
    proc = run_tool([
        FINALIZER_REL,
        str(directory / "receipt.json"),
        "--allow-checker-simulation",
        "--generated-at",
        GENERATED_AT,
        "--output",
        str(directory / "bundle.json"),
    ])
    if proc.returncode != 0:
        raise RuntimeError(f"could not build checker handoff: {proc.stdout} {proc.stderr}")
    write_sums(directory)


def check_handoff_verifier_modes() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="derivebsd-host-proof-handoff-check-") as td_name:
        root = Path(td_name)
        handoff = root / "handoff"
        build_checker_handoff(handoff)

        allowed = run_tool([VERIFY_REL, str(handoff), "--allow-checker-simulation"])
        require(errors, allowed.returncode == 0, f"checker-only handoff should validate only with explicit non-proof flag: {allowed.stdout} {allowed.stderr}")

        default = run_tool([VERIFY_REL, str(handoff)])
        require(errors, default.returncode != 0, "default handoff verification must reject checker-simulation-non-proof")
        require(errors, "default handoff verification accepts only real-host-proof" in default.stderr, "default rejection should explain real-host-proof requirement")

        tampered_sums = root / "tampered-sums"
        shutil.copytree(handoff, tampered_sums)
        (tampered_sums / "SHA256SUMS").write_text("0" * 64 + "  receipt.json\n" + sha256_file(tampered_sums / "bundle.json") + "  bundle.json\n", encoding="utf-8")
        tampered = run_tool([VERIFY_REL, str(tampered_sums), "--allow-checker-simulation"])
        require(errors, tampered.returncode != 0, "handoff verifier must reject stale SHA256SUMS")
        require(errors, "receipt.json digest mismatch" in tampered.stderr, "tampered checksum rejection should name receipt.json digest mismatch")

        extra_file = root / "extra-file"
        shutil.copytree(handoff, extra_file)
        (extra_file / "loose-proof-copy.json").write_text("{}\n", encoding="utf-8")
        extra = run_tool([VERIFY_REL, str(extra_file), "--allow-checker-simulation"])
        require(errors, extra.returncode != 0, "handoff verifier must reject unexpected loose files")
        require(errors, "unexpected files" in extra.stderr, "extra-file rejection should name unexpected files")

        unsafe_name = root / "unsafe-name"
        shutil.copytree(handoff, unsafe_name)
        (unsafe_name / "SHA256SUMS").write_text(
            f"{sha256_file(unsafe_name / 'receipt.json')}  ../receipt.json\n"
            f"{sha256_file(unsafe_name / 'bundle.json')}  bundle.json\n",
            encoding="utf-8",
        )
        unsafe = run_tool([VERIFY_REL, str(unsafe_name), "--allow-checker-simulation"])
        require(errors, unsafe.returncode != 0, "handoff verifier must reject path-traversal checksum names")
        require(errors, "unsafe filename" in unsafe.stderr, "unsafe checksum rejection should name unsafe filename")

        uppercase_sums = root / "uppercase-sums"
        shutil.copytree(handoff, uppercase_sums)
        (uppercase_sums / contract.SUMS_NAME).write_text(
            f"{sha256_file(uppercase_sums / contract.RECEIPT_NAME).upper()}  {contract.RECEIPT_NAME}\n"
            f"{sha256_file(uppercase_sums / contract.BUNDLE_NAME)}  {contract.BUNDLE_NAME}\n",
            encoding="utf-8",
        )
        uppercase = run_tool([VERIFY_REL, str(uppercase_sums), "--allow-checker-simulation"])
        require(errors, uppercase.returncode != 0, "handoff verifier must reject non-canonical uppercase SHA256SUMS digests")
        require(errors, "digest is not lowercase hex64" in uppercase.stderr, "uppercase checksum rejection should name lowercase hex64")

        readme_missing_sum = root / "readme-missing-sum"
        shutil.copytree(handoff, readme_missing_sum)
        (readme_missing_sum / contract.README_NAME).write_text("optional note must still be checksum-bound\n", encoding="utf-8")
        readme_missing = run_tool([VERIFY_REL, str(readme_missing_sum), "--allow-checker-simulation"])
        require(errors, readme_missing.returncode != 0, "handoff verifier must reject an optional README without a checksum row")
        require(errors, "present optional handoff file README.import.txt" in readme_missing.stderr, "missing README checksum rejection should name the optional member")

        readme_bound = root / "readme-bound"
        shutil.copytree(readme_missing_sum, readme_bound)
        write_sums(readme_bound)
        readme_allowed = run_tool([VERIFY_REL, str(readme_bound), "--allow-checker-simulation"])
        require(errors, readme_allowed.returncode == 0, f"handoff verifier should allow a checksum-bound optional README: {readme_allowed.stdout} {readme_allowed.stderr}")

        readme_tampered = root / "readme-tampered"
        shutil.copytree(readme_bound, readme_tampered)
        (readme_tampered / contract.README_NAME).write_text("tampered after checksum\n", encoding="utf-8")
        readme_bad_digest = run_tool([VERIFY_REL, str(readme_tampered), "--allow-checker-simulation"])
        require(errors, readme_bad_digest.returncode != 0, "handoff verifier must reject a stale optional README checksum")
        require(errors, "README.import.txt digest mismatch" in readme_bad_digest.stderr, "stale README checksum rejection should name digest mismatch")

        absent_optional_row = root / "absent-optional-row"
        shutil.copytree(handoff, absent_optional_row)
        (absent_optional_row / contract.SUMS_NAME).write_text(
            f"{sha256_file(absent_optional_row / contract.RECEIPT_NAME)}  {contract.RECEIPT_NAME}\n"
            f"{sha256_file(absent_optional_row / contract.BUNDLE_NAME)}  {contract.BUNDLE_NAME}\n"
            f"{hashlib.sha256(b'not-present').hexdigest()}  {contract.README_NAME}\n",
            encoding="utf-8",
        )
        absent_optional = run_tool([VERIFY_REL, str(absent_optional_row), "--allow-checker-simulation"])
        require(errors, absent_optional.returncode != 0, "handoff verifier must reject checksum rows for absent optional files")
        require(errors, "absent handoff file README.import.txt" in absent_optional.stderr, "absent optional checksum row rejection should name the optional member")

        oversize = root / "oversize"
        shutil.copytree(handoff, oversize)
        with (oversize / contract.README_NAME).open("wb") as handle:
            handle.seek(contract.MAX_HANDOFF_MEMBER_BYTES)
            handle.write(b"x")
        oversize_bad = run_tool([VERIFY_REL, str(oversize), "--allow-checker-simulation"])
        require(errors, oversize_bad.returncode != 0, "handoff verifier must reject over-limit loose handoff members before checksum/JSON reads")
        require(errors, "finite handoff member size limit" in oversize_bad.stderr, "oversize loose member rejection should name the finite member size limit")

        readme_symlink = root / "readme-symlink"
        shutil.copytree(handoff, readme_symlink)
        (readme_symlink / "README.import.txt").symlink_to("receipt.json")
        readme_bad = run_tool([VERIFY_REL, str(readme_symlink), "--allow-checker-simulation"])
        require(errors, readme_bad.returncode != 0, "handoff verifier must reject optional README symlinks")
        require(errors, "README.import.txt must not be a symlink" in readme_bad.stderr, "README symlink rejection should name the optional README")

        broken_optional_symlink = root / "broken-optional-symlink"
        shutil.copytree(handoff, broken_optional_symlink)
        (broken_optional_symlink / "README.import.txt").symlink_to("missing-target")
        broken_optional = run_tool([VERIFY_REL, str(broken_optional_symlink), "--allow-checker-simulation"])
        require(errors, broken_optional.returncode != 0, "handoff verifier must reject broken optional symlinks instead of ignoring them")
        require(errors, "README.import.txt must not be a symlink" in broken_optional.stderr, "broken optional symlink rejection should name the README")

        broken_required_symlink = root / "broken-required-symlink"
        shutil.copytree(handoff, broken_required_symlink)
        (broken_required_symlink / "receipt.json").unlink()
        (broken_required_symlink / "receipt.json").symlink_to("missing-target")
        broken_required = run_tool([VERIFY_REL, str(broken_required_symlink), "--allow-checker-simulation"])
        require(errors, broken_required.returncode != 0, "handoff verifier must reject broken required symlinks without tracebacking")
        require(errors, "receipt.json must not be a symlink" in broken_required.stderr, "broken required symlink rejection should name receipt.json")
        require(errors, "Traceback" not in broken_required.stderr, "broken required symlink rejection must stay operator-shaped")

        handoff_root_symlink = root / "handoff-root-symlink"
        handoff_root_symlink.symlink_to(handoff, target_is_directory=True)
        symlink_root_bad = run_tool([VERIFY_REL, str(handoff_root_symlink), "--allow-checker-simulation"])
        require(errors, symlink_root_bad.returncode != 0, "handoff verifier must reject a symlinked handoff directory root")
        require(errors, "handoff directory must not be a symlink" in symlink_root_bad.stderr, "handoff root symlink rejection should name the root directory")
    return errors


def check_collector_preflight_guards() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="derivebsd-host-proof-collector-guard-") as td_name:
        root = Path(td_name)
        target = root / "handoff-target"
        target.mkdir()
        symlink_handoff = root / "handoff-symlink"
        symlink_handoff.symlink_to(target, target_is_directory=True)
        env = dict(os.environ)
        env["DERIVEBSD_HOST_PROOF_HANDOFF_DIR"] = str(symlink_handoff)
        proc = subprocess.run(
            [str(ROOT / COLLECTOR_REL)],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        combined = proc.stdout + proc.stderr
        require(errors, proc.returncode == 2, "collector must refuse a symlinked handoff directory before FreeBSD preflight")
        require(errors, "handoff directory must not be a symlink before host proof collection" in combined, "collector symlink refusal should name the handoff root")
        require(errors, "requires FreeBSD host" not in combined, "collector symlink refusal must happen before FreeBSD/root preflight")
    return errors


def check_collector_handoff_surface() -> list[str]:
    errors: list[str] = []
    path = ROOT / COLLECTOR_REL
    require(errors, path.exists(), f"missing {COLLECTOR_REL}")
    if not path.exists():
        return errors
    text = path.read_text(encoding="utf-8", errors="replace")
    for token in [
        "HANDOFF_DIR",
        "DERIVEBSD_HOST_PROOF_HANDOFF_DIR",
        "handoff directory must not be a symlink before host proof collection",
        "receipt.json",
        "bundle.json",
        "SHA256SUMS",
        VERIFY_REL,
        "handoff=",
    ]:
        require(errors, token in text, f"collector missing handoff token {token!r}")
    for banned in ["--allow-checker-simulation", "--allow-refusal", "--allow-failed", "rm -rf"]:
        require(errors, banned not in text, f"collector must not contain non-proof or destructive token {banned!r}")
    return errors


def check_docs() -> list[str]:
    errors: list[str] = []
    doc = ROOT / DOC_REL
    require(errors, doc.exists(), f"missing {DOC_REL}")
    if doc.exists():
        text = doc.read_text(encoding="utf-8", errors="replace")
        for token in [
            VERIFY_REL,
            "DERIVEBSD_HOST_PROOF_HANDOFF_DIR",
            "receipt.json",
            "bundle.json",
            "SHA256SUMS",
            "default handoff verification accepts only `real-host-proof`",
            "handoff directory must not be a symlink",
            "README.import.txt must not be a symlink",
            "SHA256SUMS covers every present optional handoff member",
            "finite handoff member size limit",
            "lowercase hex64",
        ]:
            require(errors, token in text, f"{DOC_REL} missing handoff token {token!r}")
    return errors


def main() -> int:
    errors = check_handoff_verifier_modes() + check_collector_preflight_guards() + check_collector_handoff_surface() + check_docs()
    if errors:
        print("FreeBSD host proof handoff check FAILED.")
        for error in errors:
            print("-", error)
        return 1
    print("FreeBSD host proof handoff check OK")
    print("Handoff verifier accepts only finite digest-bound real-proof packages by default; checker simulations need an explicit non-proof flag")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
