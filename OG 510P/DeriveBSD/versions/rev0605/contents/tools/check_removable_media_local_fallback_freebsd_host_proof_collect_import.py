#!/usr/bin/env python3
"""Guard the one-command strict FreeBSD host-proof collect/import wrapper.

The risk after handoff/import/audit hardening is operator choreography: a scarce
real FreeBSD run should not depend on a human remembering five commands in the
right order, and a preserved failed-run handoff should not require rerunning the
scarce collection.  This checker keeps the one-shot wrapper strict: collector
first on the normal path, resume skips collection only for an existing handoff,
default handoff verification, default importer, default import-root audit, and
no checker-simulation/refusal/failed evidence flags.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from cube_digest_lib import load_json_strict_text

from freebsd import host_proof_contract as contract
from freebsd import validate_collect_import_run_receipt as run_receipt_validator

ROOT = Path(__file__).resolve().parents[1]
COLLECT_IMPORT_REL = contract.HOST_PROOF_COLLECT_IMPORT_REL
COLLECTOR_REL = contract.HOST_SMOKE_COLLECTOR_REL
VERIFY_REL = contract.HOST_PROOF_HANDOFF_VERIFIER_REL
IMPORT_REL = contract.HOST_PROOF_HANDOFF_IMPORTER_REL
AUDIT_REL = contract.HOST_PROOF_IMPORT_AUDITOR_REL
RUN_RECEIPT_WRITER_REL = contract.HOST_PROOF_RUN_RECEIPT_WRITER_REL
RUN_RECEIPT_VALIDATOR_REL = contract.HOST_PROOF_RUN_RECEIPT_VALIDATOR_REL
PREFLIGHT_REL = contract.HOST_PROOF_PREFLIGHT_REL
DOC_REL = "docs/current/removable-media-freebsd-host-smoke.md"
START_REL = "docs/current/start-here-now.md"


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def run_help() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(ROOT / COLLECT_IMPORT_REL), "--help"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def run_missing_resume_arg() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(ROOT / COLLECT_IMPORT_REL), "--resume-handoff"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def ordered(text: str, tokens: list[str]) -> bool:
    pos = -1
    for token in tokens:
        idx = text.find(token, pos + 1)
        if idx < 0:
            return False
        pos = idx
    return True


def surface_errors() -> list[str]:
    errors: list[str] = []
    path = ROOT / COLLECT_IMPORT_REL
    require(errors, path.exists(), f"missing {COLLECT_IMPORT_REL}")
    if not path.exists():
        return errors
    require(errors, bool(path.stat().st_mode & 0o111), f"{COLLECT_IMPORT_REL} must be executable")
    text = path.read_text(encoding="utf-8", errors="replace")
    for token in [
        "set -eu",
        "DERIVEBSD_HOST_PROOF_IMPORT_ROOT",
        "DERIVEBSD_HOST_PROOF_HANDOFF_DIR",
        "DERIVEBSD_HOST_PROOF_HANDOFF_REPLACE",
        "DERIVEBSD_RESUME_HOST_PROOF_HANDOFF_DIR",
        "DERIVEBSD_KEEP_HOST_PROOF_HANDOFF",
        "DERIVEBSD_HOST_PROOF_IMPORT_REPLACE",
        "DERIVEBSD_HOST_PROOF_RUN_RECEIPT",
        "--resume-handoff",
        "--run-receipt",
        "--import-root",
        "RESUME_MODE",
        "RUN_RECEIPT",
        "CURRENT_STAGE",
        "STAGES_COMPLETED",
        "HANDOFF_RETENTION_RESULT",
        "write_run_receipt",
        "refuse_symlink_path",
        "refuse_symlink_components",
        "require_no_existing_symlink_component",
        "must not be a symlink before host proof collection/import",
        "must not contain existing symlink components before host proof work",
        RUN_RECEIPT_WRITER_REL,
        "RECEIPT_WRITE_STATUS",
        "preserved-after-run-receipt-write-failure",
        "mktemp -d",
        "COLLECT_IMPORT_OK",
        "trap cleanup_handoff",
        "preserving auto-created handoff_dir",
        "handoff_dir_removed_after_success",
        "DERIVEBSD_HOST_PROOF_HANDOFF_DIR cannot be combined",
        "host-proof strict collect/import resume starting",
        "host-proof strict collect/import resume OK",
        "run_receipt=",
        "skip the scarce host collector",
        COLLECTOR_REL,
        VERIFY_REL,
        IMPORT_REL,
        AUDIT_REL,
        "--import-root",
        "host-proof strict collect/import OK",
    ]:
        require(errors, token in text, f"{COLLECT_IMPORT_REL} missing token {token!r}")
    require(
        errors,
        ordered(text, [COLLECTOR_REL, VERIFY_REL, IMPORT_REL, AUDIT_REL]),
        "one-shot wrapper must run collector, verifier, importer, then auditor in order on the normal path",
    )
    resume_guard = 'if [ "$RESUME_MODE" != "1" ]; then'
    guard_pos = text.find(resume_guard)
    collector_pos = text.find(COLLECTOR_REL, guard_pos + 1) if guard_pos >= 0 else -1
    verify_pos = text.find(VERIFY_REL, collector_pos + 1) if collector_pos >= 0 else -1
    require(
        errors,
        guard_pos >= 0 and guard_pos < collector_pos < verify_pos,
        "resume path must skip only the scarce collector and still run verify/import/audit",
    )
    require(errors, 'mkdir -p "$IMPORT_ROOT"' not in text, "one-shot wrapper must let the Python importer safely create the import root instead of mkdir -p")
    for banned in ["--allow-checker-simulation", "--allow-refusal", "--allow-failed"]:
        require(errors, banned not in text, f"one-shot wrapper must never contain non-proof flag {banned!r}")

    contract_text = (ROOT / contract.HOST_PROOF_CONTRACT_REL).read_text(encoding="utf-8", errors="replace")
    require(errors, "HOST_PROOF_COLLECT_IMPORT_REL" in contract_text, "shared contract must name the strict collect/import wrapper")
    require(errors, COLLECT_IMPORT_REL in contract_text, "strict collect/import wrapper must be part of the bound proof-tool set")
    require(errors, "HOST_PROOF_RUN_RECEIPT_WRITER_REL" in contract_text, "shared contract must name the run receipt writer")
    require(errors, RUN_RECEIPT_WRITER_REL in contract_text, "run receipt writer must be part of the bound proof-tool set")

    writer = ROOT / RUN_RECEIPT_WRITER_REL
    require(errors, writer.exists(), f"missing {RUN_RECEIPT_WRITER_REL}")
    if writer.exists():
        require(errors, bool(writer.stat().st_mode & 0o111), f"{RUN_RECEIPT_WRITER_REL} must be executable")
        writer_text = writer.read_text(encoding="utf-8", errors="replace")
        for token in [
            run_receipt_validator.WRITE_POLICY,
            "validate_stage_state",
            "os.O_EXCL",
            "os.replace",
            "os.fsync",
            "is_symlink",
            "run_receipt_written_with_atomic_replace",
            "run_receipt_refuses_symlink_destination",
            "run_receipt_writer_bound_by_proof_tool_contract",
            "run_receipt_payload_self_validated_before_write",
            "run_receipt_exact_key_set_enforced",
            "validate_run_receipt",
            run_receipt_validator.KIND,
            "proof_mode",
            run_receipt_validator.PROOF_MODE,
        ]:
            require(errors, token in writer_text, f"{RUN_RECEIPT_WRITER_REL} missing token {token!r}")

    preflight = (ROOT / PREFLIGHT_REL).read_text(encoding="utf-8", errors="replace")
    require(errors, COLLECT_IMPORT_REL in preflight, "preflight must require the strict collect/import wrapper to exist")
    require(errors, RUN_RECEIPT_WRITER_REL in preflight, "preflight must require the run receipt writer to exist")
    require(errors, RUN_RECEIPT_VALIDATOR_REL in preflight, "preflight must require the run receipt validator to exist")
    require(errors, "run receipt writer is not importable" in preflight, "preflight must exercise run receipt writer --help")
    require(errors, "run receipt validator is not importable" in preflight, "preflight must exercise run receipt validator --help")
    require(errors, "strict collect/import wrapper help failed" in preflight, "preflight must exercise collect/import --help")
    return errors


def help_errors() -> list[str]:
    errors: list[str] = []
    proc = run_help()
    require(errors, proc.returncode == 0, f"{COLLECT_IMPORT_REL} --help should pass: {proc.stdout} {proc.stderr}")
    for token in [
        "Strict real-host path",
        "Strict resume path",
        "collect",
        "verify",
        "import",
        "audit",
        "--resume-handoff",
        "skips collection",
        "DERIVEBSD_HOST_PROOF_IMPORT_ROOT",
        "DERIVEBSD_HOST_PROOF_HANDOFF_DIR",
        "DERIVEBSD_HOST_PROOF_HANDOFF_REPLACE",
        "DERIVEBSD_RESUME_HOST_PROOF_HANDOFF_DIR",
        "DERIVEBSD_HOST_PROOF_RUN_RECEIPT",
        "--run-receipt",
        "current/failing stage",
        "exit trap",
        "removed only after a fully",
        "preserves the handoff directory",
    ]:
        require(errors, token in proc.stdout, f"--help output missing token {token!r}")
    missing = run_missing_resume_arg()
    require(errors, missing.returncode == 2, "--resume-handoff without a directory must fail before host work")
    require(errors, "--resume-handoff requires a directory" in missing.stderr, "missing resume argument error must be explicit")
    return errors


def path_guard_errors() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="derivebsd-host-proof-collect-import-path-guard-") as td_name:
        tmp = Path(td_name)
        target_handoff = tmp / "handoff-target"
        target_handoff.mkdir()
        symlink_handoff = tmp / "handoff-symlink"
        symlink_handoff.symlink_to(target_handoff, target_is_directory=True)
        env = dict(os.environ)
        env["DERIVEBSD_HOST_PROOF_HANDOFF_DIR"] = str(symlink_handoff)
        proc = subprocess.run(
            [str(ROOT / COLLECT_IMPORT_REL), "--import-root", str(tmp / "imports")],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        combined = proc.stdout + proc.stderr
        require(errors, proc.returncode == 2, "one-shot wrapper must refuse a user-supplied symlink handoff before collection")
        require(errors, "handoff directory must not be a symlink before host proof collection/import" in combined, "handoff symlink refusal should be operator-visible")
        require(errors, "requires FreeBSD host" not in combined, "handoff symlink refusal must happen before scarce FreeBSD preflight")

        import_target = tmp / "import-target"
        import_target.mkdir()
        symlink_import_root = tmp / "import-root-symlink"
        symlink_import_root.symlink_to(import_target, target_is_directory=True)
        missing_handoff = tmp / "missing-handoff"
        proc2 = subprocess.run(
            [str(ROOT / COLLECT_IMPORT_REL), "--resume-handoff", str(missing_handoff), "--import-root", str(symlink_import_root)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        combined2 = proc2.stdout + proc2.stderr
        require(errors, proc2.returncode == 2, "one-shot wrapper must refuse a symlink import root before verify/import")
        require(errors, "import root must not be a symlink before host proof collection/import" in combined2, "import-root symlink refusal should be operator-visible")
        require(errors, not any(import_target.iterdir()), "symlinked import-root target must remain untouched by early refusal")

        ancestor_target = tmp / "handoff-parent-target"
        ancestor_target.mkdir()
        ancestor_link = tmp / "handoff-parent-link"
        ancestor_link.symlink_to(ancestor_target, target_is_directory=True)
        ancestor_env = dict(os.environ)
        ancestor_env["DERIVEBSD_HOST_PROOF_HANDOFF_DIR"] = str(ancestor_link / "handoff")
        proc3 = subprocess.run(
            [str(ROOT / COLLECT_IMPORT_REL), "--import-root", str(tmp / "ancestor-imports")],
            cwd=ROOT,
            env=ancestor_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        combined3 = proc3.stdout + proc3.stderr
        require(errors, proc3.returncode == 2, "one-shot wrapper must refuse a handoff path with a symlink ancestor before collection")
        require(errors, "handoff directory must not contain existing symlink components before host proof work" in combined3, "handoff symlink-ancestor refusal should be operator-visible")
        require(errors, "requires FreeBSD host" not in combined3, "handoff symlink-ancestor refusal must happen before scarce FreeBSD preflight")
        require(errors, not (ancestor_target / "handoff").exists(), "handoff symlink-ancestor refusal must not create the redirected handoff directory")

        import_ancestor_target = tmp / "import-parent-target"
        import_ancestor_target.mkdir()
        import_ancestor_link = tmp / "import-parent-link"
        import_ancestor_link.symlink_to(import_ancestor_target, target_is_directory=True)
        proc4 = subprocess.run(
            [str(ROOT / COLLECT_IMPORT_REL), "--resume-handoff", str(missing_handoff), "--import-root", str(import_ancestor_link / "imports")],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        combined4 = proc4.stdout + proc4.stderr
        require(errors, proc4.returncode == 2, "one-shot wrapper must refuse an import-root path with a symlink ancestor before verify/import")
        require(errors, "import root must not contain existing symlink components before host proof work" in combined4, "import-root symlink-ancestor refusal should be operator-visible")
        require(errors, not (import_ancestor_target / "imports").exists(), "import-root symlink-ancestor refusal must not create the redirected import root")
    return errors


def run_receipt_errors() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="derivebsd-host-proof-run-receipt-check-") as td_name:
        tmp = Path(td_name)
        receipt = tmp / "run.receipt.json"
        import_root = tmp / "imports"
        missing_handoff = tmp / "missing-handoff"
        proc = subprocess.run(
            [
                str(ROOT / COLLECT_IMPORT_REL),
                "--resume-handoff",
                str(missing_handoff),
                "--import-root",
                str(import_root),
                "--run-receipt",
                str(receipt),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        require(errors, proc.returncode != 0, "failed resume run must return nonzero when handoff is missing")
        require(errors, receipt.is_file(), "failed resume run with --run-receipt must write a run receipt")
        if receipt.is_file():
            obj: Any = load_json_strict_text(receipt.read_text(encoding="utf-8"))
            require(errors, isinstance(obj, dict), "run receipt root must be a JSON object")
            if isinstance(obj, dict):
                require(errors, obj.get("kind") == run_receipt_validator.KIND, "run receipt must carry the collect/import run kind")
                require(errors, obj.get("generated_for_version") == contract.CURRENT_CUBE_CUT_VERSION, "run receipt must bind current cube cut")
                require(errors, obj.get("proof_mode") == run_receipt_validator.PROOF_MODE, "run receipt must name strict real-proof-only mode")
                require(errors, obj.get("run_receipt_writer") == RUN_RECEIPT_WRITER_REL, "run receipt must name the bound receipt writer")
                require(errors, obj.get("run_receipt_write_policy") == run_receipt_validator.WRITE_POLICY, "run receipt must name atomic symlink-refusing write policy")
                require(errors, obj.get("result") == "failed", "missing-handoff resume receipt must be failed")
                require(errors, obj.get("exit_status") == proc.returncode, "run receipt exit_status must match wrapper return code")
                require(errors, obj.get("current_stage") == "verify_handoff", "missing-handoff resume must fail at verify_handoff")
                require(errors, obj.get("resume_mode") is True, "run receipt must record resume mode")
                stages = obj.get("stages_completed")
                require(errors, isinstance(stages, list) and "resume_handoff" in stages, "resume receipt must record resume_handoff as completed")
                require(errors, isinstance(stages, list) and "collect" not in stages, "resume receipt must prove collection was not rerun")
                require(errors, obj.get("handoff_dir") == str(missing_handoff), "run receipt must record handoff directory")
                require(errors, obj.get("import_root") == str(import_root), "run receipt must record import root")
                require(errors, obj.get("handoff_retention_result") == "resume-handoff-reused", "run receipt must record resume handoff retention")
                invariants = obj.get("invariants", {}) if isinstance(obj.get("invariants"), dict) else {}
                for key in sorted(run_receipt_validator.REQUIRED_TRUE_INVARIANTS):
                    require(errors, invariants.get(key) is True, f"run receipt invariant {key} must be true")
                valid_proc = subprocess.run(
                    [sys.executable, "-B", "-S", str(ROOT / RUN_RECEIPT_VALIDATOR_REL), str(receipt)],
                    cwd=ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                require(errors, valid_proc.returncode == 0, f"run receipt validator must accept wrapper receipt: {valid_proc.stdout} {valid_proc.stderr}")
                tampered = tmp / "run.receipt.tampered-stage.json"
                tampered_obj = dict(obj)
                tampered_obj["stages_completed"] = ["collect"]
                tampered.write_text(json.dumps(tampered_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                tamper_proc = subprocess.run(
                    [sys.executable, "-B", "-S", str(ROOT / RUN_RECEIPT_VALIDATOR_REL), str(tampered)],
                    cwd=ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                require(errors, tamper_proc.returncode != 0, "run receipt validator must reject a resume receipt with a collect stage")
                extra_key = tmp / "run.receipt.tampered-extra-proof-status.json"
                extra_key_obj = dict(obj)
                extra_key_obj["proof_status"] = "real-host-proof"
                extra_key.write_text(json.dumps(extra_key_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                extra_key_proc = subprocess.run(
                    [sys.executable, "-B", "-S", str(ROOT / RUN_RECEIPT_VALIDATOR_REL), str(extra_key)],
                    cwd=ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                require(errors, extra_key_proc.returncode != 0, "run receipt validator must reject extra proof_status claims")
                extra_invariant = tmp / "run.receipt.tampered-extra-invariant.json"
                extra_invariant_obj = dict(obj)
                inv = dict(extra_invariant_obj.get("invariants", {}))
                inv["unexpected_extra_invariant"] = True
                extra_invariant_obj["invariants"] = inv
                extra_invariant.write_text(json.dumps(extra_invariant_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                extra_inv_proc = subprocess.run(
                    [sys.executable, "-B", "-S", str(ROOT / RUN_RECEIPT_VALIDATOR_REL), str(extra_invariant)],
                    cwd=ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                require(errors, extra_inv_proc.returncode != 0, "run receipt validator must reject unexpected invariant keys")
        victim = tmp / "victim.txt"
        victim.write_text("do-not-overwrite\n", encoding="utf-8")
        link = tmp / "run.receipt.symlink.json"
        link.symlink_to(victim)
        proc2 = subprocess.run(
            [
                str(ROOT / COLLECT_IMPORT_REL),
                "--resume-handoff",
                str(missing_handoff),
                "--import-root",
                str(import_root),
                "--run-receipt",
                str(link),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        require(errors, proc2.returncode != 0, "symlink run-receipt destination must not make a failed resume look green")
        require(errors, link.is_symlink(), "symlink run-receipt destination must not be replaced by wrapper failure path")
        require(errors, victim.read_text(encoding="utf-8") == "do-not-overwrite\n", "symlink run-receipt destination must not overwrite its target")
        require(
            errors,
            "run receipt write failed" in (proc2.stdout + proc2.stderr),
            "symlink run-receipt refusal must be visible in wrapper output",
        )
    return errors


def doc_errors() -> list[str]:
    errors: list[str] = []
    for rel in [DOC_REL, START_REL, "README.md", "docs/current/hygiene-run-ledger.md"]:
        path = ROOT / rel
        require(errors, path.exists(), f"missing {rel}")
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in [COLLECT_IMPORT_REL, "collect", "import", "audit"]:
            require(errors, token in text, f"{rel} missing strict collect/import token {token!r}")
    doc = (ROOT / DOC_REL).read_text(encoding="utf-8", errors="replace")
    require(errors, "preserves auto-created handoff directories on failure" in doc, f"{DOC_REL} must document failure handoff preservation")
    require(errors, "--resume-handoff" in doc and "resume" in doc, f"{DOC_REL} must document strict resume from preserved handoff")
    require(errors, "--run-receipt" in doc and "run receipt" in doc, f"{DOC_REL} must document machine-readable run receipts")
    require(errors, "atomic" in doc and "symlink" in doc, f"{DOC_REL} must document atomic symlink-refusing run receipt writes")
    require(errors, "symlink ancestor" in doc or "symlinked parent" in doc, f"{DOC_REL} must document symlink-ancestor path refusal")
    return errors


def main() -> int:
    errors = surface_errors() + help_errors() + path_guard_errors() + run_receipt_errors() + doc_errors()
    if errors:
        print("FreeBSD host proof strict collect/import check FAILED.")
        for error in errors:
            print("-", error)
        return 1
    print("FreeBSD host proof strict collect/import check OK")
    print("One-shot operator path chains collect -> verify -> import -> audit, resume skips only collection, and failed runs can leave exact-shape atomic symlink-refusing run receipts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
