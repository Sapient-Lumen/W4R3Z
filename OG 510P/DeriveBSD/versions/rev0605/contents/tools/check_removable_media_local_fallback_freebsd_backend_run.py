#!/usr/bin/env python3
"""Validate the executable FreeBSD-shaped backend runner receipt.

This check is intentionally risk-first.  It proves that the new backend runner is
not merely prose over the r536 plan: the checked example is generated from the
runner, captures real fixture bytes through the shared safe-capture helper,
detaches the mount-shaped tree before worker launch, and runs the shared fd-only
worker.  It also checks the non-FreeBSD real-apply refusal path so the runner
cannot overclaim a rooted host mount from this cloudtainer.
"""
from __future__ import annotations

import copy
import os
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

import removable_media_capsicum_worker_bridge as capsicum_bridge
import removable_media_fd_worker as fd_worker
import removable_media_local_freebsd_backend_plan as plan_builder
import removable_media_safe_capture as safe_capture
import run_removable_media_local_freebsd_backend as runner
from cube_digest_lib import load_json

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = "spec/removable.media.local.freebsd.backend.run.receipt.schema.json"
EXAMPLE_REL = "spec/examples/removable.media.local.freebsd.backend.run.receipt.json"
VALIDATION_REL = "validation/removable-media-local-freebsd-backend-run.receipt.json"
INVALID_DIR = ROOT / "spec" / "examples" / "invalid" / "removable-media" / "freebsd-backend-run"
DOC_TOKENS = {
    "README.md": [runner.VERSION, "FreeBSD backend runner", "tools/run_removable_media_local_freebsd_backend.py"],
    "docs/00-index.md": [runner.VERSION, "spec/removable.media.local.freebsd.backend.run.receipt.schema.json"],
    "docs/99-llm-runbook.md": ["check_removable_media_local_fallback_freebsd_backend_run.py", "apply-freebsd"],
    "docs/current/removable-media-local-fallback-freebsd-backend-run.md": [
        "removable.media.local.freebsd.backend.run.receipt",
        "non-FreeBSD real-apply refusal",
        "fd-only worker",
        "worker_bridge",
        "removable.media.capsicum.worker.bridge",
        "tools/removable_media_fd_worker.py",
    ],
}


def validate_schema(obj: dict[str, Any]) -> list[str]:
    schema = load_json(ROOT, SCHEMA_REL)
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def get(obj: dict[str, Any], *path: str) -> Any:
    cur: Any = obj
    for part in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def semantic_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(errors, obj.get("kind") == "removable.media.local.freebsd.backend.run.receipt", "wrong kind")
    require(errors, obj.get("schema_version") == "0.1", "schema_version must be 0.1")
    require(errors, obj.get("run_id") == runner.RUN_ID, "run_id must bind current backend runner cut")
    require(errors, obj.get("generated_for_version") == runner.VERSION, "generated_for_version must bind current backend runner cut")
    require(errors, obj.get("result") == "passed", "canonical backend run must pass")
    require(errors, obj.get("execution_mode") == "cloudtainer-fixture-backend-simulation-no-root", "canonical example must stay cloudtainer fixture mode")

    host = obj.get("host", {}) if isinstance(obj.get("host"), dict) else {}
    inputs = obj.get("inputs", {}) if isinstance(obj.get("inputs"), dict) else {}
    workspace = obj.get("workspace", {}) if isinstance(obj.get("workspace"), dict) else {}
    preflight = obj.get("preflight", {}) if isinstance(obj.get("preflight"), dict) else {}
    plan = obj.get("plan_binding", {}) if isinstance(obj.get("plan_binding"), dict) else {}
    mount = obj.get("mount", {}) if isinstance(obj.get("mount"), dict) else {}
    capture = get(obj, "capture", "evidence") or {}
    detach = obj.get("detach", {}) if isinstance(obj.get("detach"), dict) else {}
    worker = obj.get("worker", {}) if isinstance(obj.get("worker"), dict) else {}
    worker_bridge = obj.get("worker_bridge", {}) if isinstance(obj.get("worker_bridge"), dict) else {}
    derivative = obj.get("derivative", {}) if isinstance(obj.get("derivative"), dict) else {}
    invariants = obj.get("invariants", {}) if isinstance(obj.get("invariants"), dict) else {}

    require(errors, host.get("required_os_for_real_apply") == "FreeBSD", "real apply must target FreeBSD")
    require(errors, host.get("non_freebsd_apply_refuses") is True, "non-FreeBSD apply must refuse")
    require(errors, host.get("network_required") is False, "backend runner must not require network")
    require(errors, host.get("package_install_in_lane") is False, "backend runner must not install packages")

    require(errors, workspace.get("runtime_work_root_policy") == runner.WORK_ROOT_POLICY, "workspace must bind no-rmtree work-root policy")
    require(errors, workspace.get("destructive_cli_work_dir_cleanup") is False, "workspace must not permit destructive cleanup of user work dirs")
    require(errors, workspace.get("session_root_mode") == "0700", "session root mode must be private")

    require(errors, preflight.get("device_node_validated") is True, "fixture preflight must validate device-node shape")
    require(errors, preflight.get("device_node_validation_method") == "shape-only-fixture-backend", "fixture preflight must state shape-only validation")
    require(errors, preflight.get("device_node_error_detail") is None, "canonical preflight must have no device-node error")

    require(errors, inputs.get("claimed_fstyp") == "exfat", "canonical fixture models exfat")
    require(errors, inputs.get("selected_member_normalized") == "invoice.pdf", "selected member must normalize exactly")
    require(errors, "nodev" not in plan.get("mount_options_to_emit", []), "runner must not emit nodev as FreeBSD mount option")
    require(errors, plan.get("nodev_not_emitted_as_generic_freebsd_mount_option") is True, "runner must carry nodev correction")
    require(errors, plan.get("phase_order", [])[-2:] == ["umount-before-worker", "launch-post-detach-worker"], "plan binding must keep umount before worker")

    require(errors, worker_bridge == capsicum_bridge.backend_binding_summary(), "backend run must bind the Capsicum worker bridge summary")
    require(errors, worker_bridge.get("bridge_id") == capsicum_bridge.BRIDGE_ID, "backend run must bind current Capsicum bridge id")
    require(errors, worker_bridge.get("real_apply_python_fixture_worker_allowed") is False, "real apply must disallow Python fixture worker")
    require(errors, worker_bridge.get("cloudtainer_executes_capsicum") is False, "fixture run must not claim Capsicum execution")

    require(errors, mount.get("attempted") is True, "fixture backend must attempt mount-shaped setup")
    require(errors, mount.get("real_mount_performed") is False, "cloudtainer fixture mode must not claim a real mount")
    require(errors, mount.get("command_result") is None, "fixture mount-shaped setup must not mint real mount command evidence")
    require(errors, mount.get("mount_options") == ["ro", "nosuid", "noexec", "nosymfollow", "untrusted"], "mount options must be FreeBSD-shaped tuple")

    require(errors, capture.get("digest") == "sha256:01a0cd0826db2a58f930defd65189517c567703c224d715abefeb66897a5e2cc", "fixture invoice digest must remain bound")
    require(errors, capture.get("capture_api") == "dirfd-openat-no-symlink-components", "capture must use shared safe-capture API")
    for key in [
        "root_fd_pinned",
        "opened_with_openat",
        "opened_with_no_follow",
        "regular_file_only",
        "lstat_fstat_same_object",
        "source_stable_after_copy",
        "verified_after_copy",
    ]:
        require(errors, capture.get(key) is True, f"capture.{key} must be true")
    require(errors, capture.get("cas_write_policy") == "no-overwrite-link-then-verify-existing", "capture must publish CAS objects without overwrite")
    require(errors, capture.get("cas_object_preexisted") is False, "canonical fixture publish should create a fresh CAS object")
    require(errors, capture.get("cas_existing_object_verified") is False, "canonical first publish should not claim pre-existing object verification")

    require(errors, detach.get("attempted") is True, "detach must be attempted before worker")
    require(errors, detach.get("umount_result") is None, "fixture detach must not mint real umount command evidence")
    require(errors, detach.get("unmounted_before_worker") is True, "mount-shaped tree must be removed before worker")
    require(errors, detach.get("mountpoint_visible_to_worker") is False, "mountpoint must not be worker-visible")
    require(errors, detach.get("device_node_closed_before_worker") is True, "device node must be closed before worker")
    require(errors, detach.get("source_media_fd_closed_before_detach") is True, "source media fd must be closed before detach")
    require(errors, detach.get("source_media_fd_closed_before_worker") is True, "source media fd must be closed before worker launch")
    require(errors, detach.get("selected_member_accessible_after_detach") is False, "selected member path must be absent after detach")

    require(errors, worker.get("attempted") is True, "worker must be attempted")
    require(errors, worker.get("launcher_kind") == "python-fd-worker-cloudtainer-fixture-only", "fixture worker must be explicitly fixture-only")
    require(errors, worker.get("real_apply_python_fixture_worker_allowed") is False, "Python fixture worker must be forbidden for real apply")
    require(errors, worker.get("real_apply_requires_capsicum_worker_bridge") is True, "real apply must require the Capsicum worker bridge")
    require(errors, worker.get("capsicum_worker_bridge_id") == capsicum_bridge.BRIDGE_ID, "worker evidence must bind the current Capsicum bridge id")
    require(errors, worker.get("launched_after_detach") is True, "worker must launch after detach")
    require(errors, worker.get("input_delivery") == "preopened-read-fd-to-preserved-cas-object", "input must be fd-only preserved capture")
    require(errors, worker.get("output_delivery") == "preopened-write-fd-to-broker-owned-derivative-slot", "output must be fd-only derivative slot")
    require(errors, worker.get("output_open_policy") == "create-exclusive-no-truncate", "worker output slot must be opened create-exclusive without truncation")
    require(errors, worker.get("output_truncates_existing") is False, "worker output must not truncate existing derivative bytes")
    require(errors, worker.get("argv_contains_device_or_mount_path") is False, "argv must not carry device or mount path")
    require(errors, worker.get("env_contains_device_or_mount_path") is False, "env must not carry device or mount path")
    require(errors, worker.get("source_path_passed_to_worker") is False, "worker must not receive source path")
    require(errors, worker.get("fd_inventory_supported") is True, "worker must inventory fds")
    require(errors, worker.get("prelaunch_input_lstat_regular") is True, "preserved worker input must be lstat-regular before fd delegation")
    require(errors, worker.get("prelaunch_input_not_symlink") is True, "preserved worker input must not be a symlink before fd delegation")
    require(errors, worker.get("prelaunch_input_digest") == capture.get("digest"), "preserved worker input digest must match capture before fd delegation")
    require(errors, worker.get("prelaunch_input_digest_matched") is True, "prelaunch input digest check must pass")
    require(errors, worker.get("unexpected_fds") == [], "worker must not inherit unexpected fds")
    require(errors, worker.get("leak_canary_fd_seen") is False, "worker must not inherit broker non-media fd canary")
    require(errors, worker.get("leak_canary_fd_source") == "broker-nonmedia-canary-not-source-media", "fd leak canary must not be source-media authority")
    require(errors, worker.get("exit_code") == 0, "worker must exit cleanly")

    require(errors, derivative.get("payload_input_digest") == capture.get("digest"), "derivative must bind preserved capture digest")
    require(errors, derivative.get("separate_from_preserved_capture") is True, "derivative must be separate from preserved capture")

    expected_invariant_keys = [
        "fixture_source_copied_to_private_mountpoint",
        "claimed_fstyp_admitted_before_mount",
        "real_mount_not_claimed_in_cloudtainer",
        "safe_capture_openat_no_symlink_walk",
        "capture_verified_after_copy",
        "capture_source_stable_after_copy",
        "cas_publish_no_overwrite",
        "mountpoint_removed_before_worker",
        "selected_member_not_accessible_after_detach",
        "worker_launched_after_detach",
        "worker_fd_inventory_clean",
        "source_media_fd_closed_before_detach",
        "source_media_fd_closed_before_worker",
        "worker_nonmedia_fd_canary_not_leaked",
        "worker_leak_canary_not_source_media",
        "worker_preserved_input_preflighted",
        "worker_output_slot_create_exclusive",
        "worker_digest_equals_preserved_capture",
        "device_and_mount_paths_not_passed_to_worker",
        "derivative_separate_from_preserved_capture",
        "non_freebsd_apply_refusal_path_exercised_by_checker",
        "real_apply_python_fixture_worker_disallowed",
        "capsicum_worker_bridge_bound",
    ]
    for key in expected_invariant_keys:
        require(errors, invariants.get(key) is True, f"invariant {key} must be true")
    return errors


def check_builder_replay(observed: dict[str, Any]) -> list[str]:
    expected = runner.build_default_fixture_receipt()
    if expected != observed:
        return ["runner output differs from canonical FreeBSD backend run receipt example"]
    return []


def check_refusal_path() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="derivebsd-rm-freebsd-apply-refusal-") as tmp:
        refused = runner.build_apply_receipt(
            Path(tmp),
            selected_member=runner.DEFAULT_SELECTED_MEMBER,
            claimed_fstyp=runner.DEFAULT_CLAIMED_FSTYP,
            device_node=runner.DEFAULT_DEVICE_NODE,
            generated_at_utc=runner.FIXED_GENERATED_AT,
        )
    require(errors, refused.get("result") == "refused", "non-FreeBSD real apply must produce refused result")
    require(errors, refused.get("execution_mode") == "freebsd-apply-refused", "refusal execution mode must be explicit")
    require(errors, get(refused, "preflight", "refusal_reason") == "non-freebsd-host", "refusal reason must bind non-FreeBSD host")
    require(errors, get(refused, "preflight", "device_node_validated") is True, "non-FreeBSD refusal must still validate device-node shape")
    require(errors, get(refused, "preflight", "device_node_validation_method") == "shape-only-non-freebsd-refusal", "non-FreeBSD refusal must disclose shape-only device validation")
    require(errors, get(refused, "mount", "attempted") is False, "refusal must not attempt mount")
    require(errors, get(refused, "mount", "command_result") is None, "refusal must not mint mount command evidence")
    require(errors, get(refused, "detach", "umount_result") is None, "refusal must not mint umount command evidence")
    require(errors, get(refused, "worker", "attempted") is False, "refusal must not launch worker")
    require(errors, get(refused, "invariants", "no_mount_attempted_after_refusal") is True, "refusal invariant must keep mount absent")
    schema_errors = validate_schema(refused)
    if schema_errors:
        errors.append(f"refusal receipt failed schema: {schema_errors[:5]}")
    return errors


def check_apply_device_validation() -> list[str]:
    errors: list[str] = []
    for bad in ["/dev/./da0", "/dev/foo/../bar", "/dev//da0", "/tmp/da0", "/dev/da0;rm"]:
        try:
            plan_builder.validate_device_node(bad)
        except ValueError:
            pass
        else:
            errors.append(f"unsafe device-node shape was admitted: {bad}")
    for good in ["/dev/null", "/dev/da0p1", "/dev/gpt/DERIVEBSD_MEDIA"]:
        try:
            plan_builder.validate_device_node(good)
        except ValueError as exc:
            errors.append(f"safe device-node shape was rejected: {good}: {exc}")

    with tempfile.TemporaryDirectory(prefix="derivebsd-rm-freebsd-apply-invalid-device-") as tmp:
        invalid_receipt = runner.build_apply_receipt(
            Path(tmp),
            selected_member=runner.DEFAULT_SELECTED_MEMBER,
            claimed_fstyp=runner.DEFAULT_CLAIMED_FSTYP,
            device_node="/dev/./da0",
            generated_at_utc=runner.FIXED_GENERATED_AT,
        )
    require(errors, invalid_receipt.get("result") == "refused", "invalid device shape must be a structured refusal")
    require(errors, get(invalid_receipt, "preflight", "refusal_reason") == "invalid-device-node-shape", "invalid device shape refusal must name the reason")
    require(errors, get(invalid_receipt, "mount", "attempted") is False, "invalid device shape must not reach mount")
    require(errors, get(invalid_receipt, "worker", "attempted") is False, "invalid device shape must not launch worker")
    schema_errors = validate_schema(invalid_receipt)
    if schema_errors:
        errors.append(f"invalid device shape receipt failed schema: {schema_errors[:5]}")

    try:
        runner._validate_device_node_for_apply("/dev/null")  # type: ignore[attr-defined]
    except ValueError as exc:
        errors.append(f"character device /dev/null should pass lstat validation in checker host: {exc}")
    if Path("/dev/fd").exists():
        try:
            runner._validate_device_node_for_apply("/dev/fd")  # type: ignore[attr-defined]
        except ValueError as exc:
            require(errors, str(exc) == "device-node-is-symlink", f"/dev/fd should fail as symlink when present, got {exc}")
        else:
            errors.append("symlink device path /dev/fd was admitted by lstat validation")
    return errors


def check_work_dir_policy() -> list[str]:
    errors: list[str] = []
    runner_source = (ROOT / "tools" / "run_removable_media_local_freebsd_backend.py").read_text(encoding="utf-8")
    require(errors, "shutil.rmtree(work_dir)" not in runner_source, "runner must not recursively delete user-supplied --work-dir")
    require(errors, runner.WORK_ROOT_POLICY in runner_source, "runner source must carry the no-rmtree work-root policy token")
    with tempfile.TemporaryDirectory(prefix="derivebsd-rm-freebsd-workdir-policy-") as tmp:
        base = Path(tmp) / "user-base"
        base.mkdir()
        sentinel = base / "keep.txt"
        sentinel.write_text("must survive backend runner\n", encoding="utf-8")
        output = Path(tmp) / "receipt.json"
        proc = subprocess.run(
            [
                sys.executable,
                "-B",
                str(ROOT / "tools" / "run_removable_media_local_freebsd_backend.py"),
                "--mode",
                "fixture",
                "--work-dir",
                str(base),
                "--output",
                str(output),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=30,
        )
        require(errors, proc.returncode == 0, f"fixture run with user work-dir should pass without cleanup, rc={proc.returncode}, stderr={proc.stderr[:200]!r}")
        require(errors, sentinel.exists(), "user work-dir sentinel must survive fixture run")
        child_dirs = [p for p in base.iterdir() if p.is_dir()]
        require(errors, len(child_dirs) == 1, "runner must create one exclusive child under user work-dir")
        if output.exists():
            obj = json.loads(output.read_text(encoding="utf-8"))
            require(errors, get(obj, "workspace", "destructive_cli_work_dir_cleanup") is False, "receipt must bind non-destructive work-dir cleanup")
            require(errors, get(obj, "workspace", "runtime_work_root_policy") == runner.WORK_ROOT_POLICY, "receipt must bind work-root policy")
    return errors


def check_capture_failure_path() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="derivebsd-rm-freebsd-backend-missing-member-") as tmp:
        failed = runner.build_fixture_receipt(Path(tmp), selected_member="missing.pdf")
    require(errors, failed.get("result") == "failed", "missing selected member must produce a structured failed receipt")
    require(errors, get(failed, "capture", "attempted") is True, "capture failure receipt must record an attempted capture")
    require(errors, get(failed, "capture", "evidence") is None, "capture failure receipt must not mint capture evidence")
    require(errors, get(failed, "capture", "error_reason") == "missing-member", "capture failure reason must be missing-member")
    require(errors, get(failed, "detach", "unmounted_before_worker") is True, "capture failure must still detach/remove mountpoint before returning")
    require(errors, get(failed, "worker", "attempted") is False, "worker must not launch after capture failure")
    require(errors, get(failed, "worker", "input_delivery") == "not-launched-capture-failed-before-worker", "worker input delivery must explain capture failure")
    require(errors, get(failed, "invariants", "worker_not_launched_after_capture_failure") is True, "capture-failure invariant must prove no worker launch")
    schema_errors = validate_schema(failed)
    if schema_errors:
        errors.append(f"capture failure receipt failed schema: {schema_errors[:5]}")
    return errors



def check_fd_worker_output_slot_policy() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="derivebsd-rm-fd-worker-output-policy-") as tmp:
        root = Path(tmp)
        input_path = root / "input.bin"
        output_path = root / "derivative.json"
        payload = b"fd worker output-slot policy probe\n"
        input_path.write_bytes(payload)
        output_path.write_bytes(b"stale derivative that must not be truncated\n")
        before_digest = safe_capture.sha256_file(output_path)
        try:
            fd_worker.run_fd_worker(input_path, output_path, safe_capture.sha256_bytes(payload))
        except FileExistsError:
            pass
        except OSError as exc:
            require(errors, getattr(exc, "errno", None) == 17, f"pre-existing derivative slot should fail with EEXIST/FileExistsError, got {exc!r}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"pre-existing derivative slot raised unexpected exception {exc!r}")
        else:
            errors.append("pre-existing derivative slot was overwritten instead of failing closed")
        after_digest = safe_capture.sha256_file(output_path)
        require(errors, after_digest == before_digest, "pre-existing derivative slot bytes must remain unchanged")
    worker_source = (ROOT / "tools" / "removable_media_fd_worker.py").read_text(encoding="utf-8")
    require(errors, "O_TRUNC" not in worker_source, "fd worker must not open derivative output with O_TRUNC")
    require(errors, "O_EXCL" in worker_source, "fd worker must create derivative output exclusively")
    return errors


def check_real_apply_capsicum_gate() -> list[str]:
    errors: list[str] = []
    source = (ROOT / "tools" / "run_removable_media_local_freebsd_backend.py").read_text(encoding="utf-8")
    require(errors, "import removable_media_capsicum_worker_bridge as capsicum_bridge" in source, "backend runner must import the Capsicum worker bridge")
    require(errors, "capsicum_bridge.REAL_APPLY_GATE_REASON" in source, "real FreeBSD apply must refuse on the bridge gate")
    apply_source = runner.build_apply_receipt.__code__.co_names
    require(errors, "fd_worker" not in apply_source, "real apply preflight must not reference the Python fixture worker")
    import inspect
    apply_text = inspect.getsource(runner.build_apply_receipt)
    require(errors, '"/usr/sbin/fstyp"' not in apply_text, "build_apply_receipt must not carry dead fstyp code behind the bridge refusal")
    require(errors, "run_fd_worker" not in apply_text, "build_apply_receipt must not carry dead worker-launch code behind the bridge refusal")
    return errors

def check_invalid_fixtures() -> list[str]:
    errors: list[str] = []
    paths = sorted(INVALID_DIR.glob("*.json")) if INVALID_DIR.exists() else []
    if len(paths) < 4:
        errors.append("expected at least four FreeBSD backend run negative fixtures")
    for path in paths:
        obj = json.loads(path.read_text(encoding="utf-8"))
        schema_errors = validate_schema(obj)
        semantic = semantic_errors(obj)
        if not schema_errors and not semantic:
            errors.append(f"{path.relative_to(ROOT)} unexpectedly passed schema and semantic checks")
    return errors


def check_doc_tokens() -> list[str]:
    errors: list[str] = []
    for rel, tokens in DOC_TOKENS.items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"{rel} missing")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token not in text:
                errors.append(f"{rel} missing token {token!r}")
    return errors


def write_validation_copy(obj: dict[str, Any]) -> None:
    path = ROOT / VALIDATION_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    observed = load_json(ROOT, EXAMPLE_REL)
    errors = validate_schema(observed) + semantic_errors(observed) + check_builder_replay(observed)
    errors.extend(check_refusal_path())
    errors.extend(check_apply_device_validation())
    errors.extend(check_work_dir_policy())
    errors.extend(check_capture_failure_path())
    errors.extend(check_fd_worker_output_slot_policy())
    errors.extend(check_real_apply_capsicum_gate())
    errors.extend(check_invalid_fixtures())
    errors.extend(check_doc_tokens())
    if errors:
        print("removable-media FreeBSD backend run check FAILED.")
        for error in errors:
            print("-", error)
        return 1
    write_validation_copy(observed)
    print("removable-media FreeBSD backend run check OK")
    print("Backend runner: fixture/private mount shape -> safe capture -> detach -> fd-only worker; real apply refuses outside FreeBSD; derivative output fails closed if pre-existing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
