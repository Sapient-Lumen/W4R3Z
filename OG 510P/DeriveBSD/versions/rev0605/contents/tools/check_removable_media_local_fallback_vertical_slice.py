#!/usr/bin/env python3
"""Assert the removable-media local fallback examples form one runnable slice.

This is deliberately not another schema-family registry check. It cross-links
the existing first-cut artifacts as a concrete story: a present USB block device
is granted read-only attach authority, a single selected file is capture-first
into quarantine, the device is detached before later work, and post-detach
workers operate only through a constrained preserved-object projection.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from cube_digest_lib import load_json

ROOT = Path(__file__).resolve().parents[1]
EX = "spec/examples/"
CAPSICUM_WORKER_SOURCE = ROOT / "tools" / "freebsd" / "rm_post_detach_capsicum_worker.c"
CAPSICUM_BRIDGE_EXAMPLE = "removable.media.capsicum.worker.bridge.json"


def ex(name: str) -> Any:
    return load_json(ROOT, EX + name)


def get(obj: dict[str, Any], *path: str) -> Any:
    cur: Any = obj
    for part in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    profile = ex("device.profile.removable-media-local-ingest.exfat.json")
    grant = ex("device.attach.grant.removable-media-local-ingest.json")
    attach = ex("device.attach.receipt.removable-media-local-ingest.json")
    mount = ex("mount.view.removable-media-local-ingest.json")
    plan = ex("content.import.plan.removable-media-local-ingest.json")
    receipt = ex("content.import.receipt.removable-media-local-ingest.json")
    detach = ex("device.detach.receipt.removable-media-local-ingest.json")
    contract = ex("removable.media.local.post_detach.contract.json")
    launch = ex("removable.media.local.post_detach.launch.evidence.json")
    reader_admission = ex("removable.media.local.post_detach.reader.admission.receipt.json")
    prototype_receipt = load_json(ROOT, "validation/removable-media-local-fallback-prototype-run.receipt.json")
    safe_capture_receipt = load_json(ROOT, "validation/removable-media-safe-capture.receipt.json")
    freebsd_backend_plan = ex("removable.media.local.freebsd.backend.plan.json")
    freebsd_backend_run = ex("removable.media.local.freebsd.backend.run.receipt.json")
    capsicum_bridge = ex(CAPSICUM_BRIDGE_EXAMPLE)
    host_smoke_refusal = load_json(ROOT, "validation/removable-media-local-freebsd-host-smoke.refusal.json")
    host_smoke_success_sim = load_json(ROOT, "validation/removable-media-local-freebsd-host-smoke.success-simulation.json")
    host_smoke_failure_sim = load_json(ROOT, "validation/removable-media-local-freebsd-host-smoke.failure-simulation.json")
    host_smoke_fstyp_output_failure_sim = load_json(ROOT, "validation/removable-media-local-freebsd-host-smoke.fstyp-output-failure-simulation.json")
    host_smoke_fixture_admission_failure_sim = load_json(ROOT, "validation/removable-media-local-freebsd-host-smoke.fixture-admission-failure-simulation.json")
    host_smoke_fixture_copy_change_sim = load_json(ROOT, "validation/removable-media-local-freebsd-host-smoke.fixture-copy-change-simulation.json")
    host_smoke_worker_source_copy_change_sim = load_json(ROOT, "validation/removable-media-local-freebsd-host-smoke.worker-source-copy-change-simulation.json")
    harness_run = ex("removable.media.local.fallback.harness.run.json")

    errors: list[str] = []

    device_ids = {
        profile.get("device_id"),
        get(grant, "device", "id"),
        get(attach, "device", "id"),
        get(detach, "device", "id"),
        get(plan, "origin", "source", "device_id"),
    }
    require(errors, len(device_ids) == 1 and None not in device_ids, f"device identity does not stay exact across slice: {sorted(str(x) for x in device_ids)}")
    require(errors, "removable-media" in profile.get("risk_tags", []), "device profile is not risk-tagged removable-media")
    require(errors, "local-fallback-ingest" in profile.get("risk_tags", []), "device profile is not tagged for local fallback ingest")

    constraints = grant.get("constraints", {})
    require(errors, grant.get("permissions") == ["attach", "mount-read-only"], "attach grant permissions should be attach then mount-read-only")
    require(errors, constraints.get("read_only") is True, "attach grant must be read_only")
    require(errors, set(constraints.get("required_mount_flags", [])) >= {"ro", "nosuid", "noexec", "nosymfollow", "untrusted"}, "mount hardening flags are incomplete")
    require(errors, "nodev" not in constraints.get("required_mount_flags", []), "Linux-style nodev must not be modeled as a FreeBSD mount flag")
    require(errors, constraints.get("device_node_posture") == "enforced-by-devfs-and-regular-file-ingest-not-freebsd-nodev-mount-flag", "device node posture must stay explicit outside mount flags")
    require(errors, "exfat" in constraints.get("allowed_filesystem_families", []), "canonical exfat family is not admitted")
    require(errors, "unknown" in constraints.get("denied_filesystem_families", []), "unknown filesystem family must fail closed")
    require(errors, mount.get("constraints", {}).get("host_fallback") == "forbidden", "mount view should not silently fall back to host ambient mounts")

    require(errors, freebsd_backend_plan.get("kind") == "removable.media.local.freebsd.backend.plan", "FreeBSD backend plan must be present in the slice")
    require(errors, get(freebsd_backend_plan, "host_requirements", "required_os") == "FreeBSD", "backend plan must target FreeBSD")
    require(errors, get(freebsd_backend_plan, "preflight", "fstyp_command") == ["/usr/sbin/fstyp", get(freebsd_backend_plan, "inputs", "device_node")], "backend plan must probe exact device with fstyp")
    require(errors, "nodev" not in get(freebsd_backend_plan, "mount_admission", "contract_desired_inertness_flags"), "backend plan must not keep nodev as active desired mount inertness")
    require(errors, "nodev" not in get(freebsd_backend_plan, "mount_admission", "freebsd_generic_mount_options_to_emit"), "backend plan must not emit nodev as a generic FreeBSD mount option")
    require(errors, get(freebsd_backend_plan, "mount_admission", "not_claimed_as_freebsd_generic_mount_options") == ["nodev"], "backend plan must explicitly mark nodev as not a generic FreeBSD mount option")
    require(errors, get(freebsd_backend_plan, "capture_sequence", "selected_member_open", "shares_cloudtainer_capture_helper") == "tools/removable_media_safe_capture.py", "backend plan must share the safe-capture helper semantics")
    require(errors, get(freebsd_backend_plan, "capture_sequence", "phase_order")[-2:] == ["umount-before-worker", "launch-post-detach-worker"], "backend plan must unmount before worker launch")
    require(errors, get(freebsd_backend_plan, "post_detach_worker", "launch_mode") == "preopened-fds-only", "backend plan worker must be fd-only")
    require(errors, get(freebsd_backend_plan, "post_detach_worker", "devfs_visible_devices") == [], "backend plan worker must see no devices")

    require(errors, freebsd_backend_run.get("kind") == "removable.media.local.freebsd.backend.run.receipt", "FreeBSD backend run receipt must be present in the slice")
    require(errors, freebsd_backend_run.get("result") == "passed", "FreeBSD backend run receipt must pass")
    require(errors, get(freebsd_backend_run, "plan_binding", "plan_id") == freebsd_backend_plan.get("plan_id"), "backend run must bind the backend plan id")
    require(errors, get(freebsd_backend_run, "workspace", "destructive_cli_work_dir_cleanup") is False, "backend run must not permit destructive user work-dir cleanup")
    require(errors, get(freebsd_backend_run, "workspace", "runtime_work_root_policy") == "private-temp-or-create-exclusive-child-under-user-base-no-rmtree", "backend run must bind the no-rmtree work-root policy")
    require(errors, get(freebsd_backend_run, "preflight", "device_node_validated") is True, "backend run must validate the device-node shape before the fixture/prototype path")
    require(errors, get(freebsd_backend_run, "preflight", "device_node_validation_method") == "shape-only-fixture-backend", "backend run must disclose fixture device-node validation scope")
    require(errors, get(freebsd_backend_run, "mount", "real_mount_performed") is False, "cloudtainer backend run must not overclaim a real mount")
    require(errors, get(freebsd_backend_run, "mount", "command_result") is None, "cloudtainer backend run must not mint real mount command evidence")
    require(errors, get(freebsd_backend_run, "mount", "mount_options") == ["ro", "nosuid", "noexec", "nosymfollow", "untrusted"], "backend run must keep the FreeBSD-shaped mount tuple")
    run_capture = get(freebsd_backend_run, "capture", "evidence") or {}
    require(errors, run_capture.get("capture_api") == "dirfd-openat-no-symlink-components", "backend run must use dirfd/openat capture")
    require(errors, run_capture.get("cas_write_policy") == "no-overwrite-link-then-verify-existing", "backend run must publish CAS objects without overwrite")
    require(errors, get(freebsd_backend_run, "invariants", "cas_publish_no_overwrite") is True, "backend run invariant must prove no-overwrite CAS publish")
    require(errors, get(freebsd_backend_run, "invariants", "worker_output_slot_create_exclusive") is True, "backend run invariant must prove create-exclusive/no-truncate worker output")
    require(errors, run_capture.get("digest") == get(harness_run, "capture", "observed_subject_digest"), "backend run digest must bind the canonical fixture subject")
    require(errors, get(freebsd_backend_run, "detach", "unmounted_before_worker") is True, "backend run must detach before worker")
    require(errors, get(freebsd_backend_run, "detach", "umount_result") is None, "cloudtainer backend run must not mint real umount command evidence")
    require(errors, get(freebsd_backend_run, "worker", "launched_after_detach") is True, "backend run worker must launch after detach")
    require(errors, get(freebsd_backend_run, "worker", "unexpected_fds") == [], "backend run worker must not inherit unexpected fds")
    require(errors, get(freebsd_backend_run, "detach", "source_media_fd_closed_before_detach") is True, "backend run must close source-media fd before detach")
    require(errors, get(freebsd_backend_run, "detach", "source_media_fd_closed_before_worker") is True, "backend run must close source-media fd before worker launch")
    require(errors, get(freebsd_backend_run, "worker", "leak_canary_fd_seen") is False, "backend run worker must not inherit broker non-media fd canary")
    require(errors, get(freebsd_backend_run, "worker", "leak_canary_fd_source") == "broker-nonmedia-canary-not-source-media", "backend run fd leak canary must not be source-media authority")
    require(errors, get(freebsd_backend_run, "worker", "prelaunch_input_digest_matched") is True, "backend run must preflight preserved input digest before fd delegation")
    require(errors, get(freebsd_backend_run, "worker", "launcher_kind") == "python-fd-worker-cloudtainer-fixture-only", "fixture backend worker must be marked fixture-only")
    require(errors, get(freebsd_backend_run, "worker", "real_apply_python_fixture_worker_allowed") is False, "real apply must not use the Python fixture worker")
    require(errors, get(freebsd_backend_run, "worker", "real_apply_requires_capsicum_worker_bridge") is True, "real apply must require the Capsicum worker bridge")
    require(errors, get(freebsd_backend_run, "worker_bridge", "bridge_id") == capsicum_bridge.get("bridge_id"), "backend run must bind the Capsicum bridge id")
    require(errors, get(freebsd_backend_run, "worker_bridge", "real_apply_python_fixture_worker_allowed") is False, "backend bridge binding must disallow Python worker for real apply")
    require(errors, get(freebsd_backend_run, "worker_bridge", "production_worker_env_policy") == "empty-environment", "backend bridge binding must clear production worker environment")
    require(errors, get(freebsd_backend_run, "worker_bridge", "production_worker_cwd_policy") == "private-empty-directory-not-media-not-repo", "backend bridge binding must use a private non-media production worker cwd")
    require(errors, get(freebsd_backend_run, "worker_bridge", "production_stdio_policy") == "close-fd-0-1-2-before-cap-enter", "backend bridge binding must close production stdio before cap_enter")
    require(errors, get(freebsd_backend_run, "worker_bridge", "worker_failure_report_channel") == "delegated-output-fd-after-stdio-close", "backend bridge binding must keep post-stdio failures visible on delegated output fd")
    require(errors, get(freebsd_backend_run, "worker_bridge", "startup_failure_report_channel") == "delegated-output-fd-before-or-after-stdio-close", "backend bridge binding must keep startup failures visible on delegated output fd")
    require(errors, get(freebsd_backend_run, "worker_bridge", "startup_pre_stdio_failure_report_channel") == "delegated-output-fd-before-stdio-close", "backend bridge binding must distinguish pre-stdio startup failures from post-stdio failures")
    require(errors, get(freebsd_backend_run, "worker_bridge", "extra_fd_canary") == 5, "backend bridge binding must carry the fd-5 inherited-fd canary")
    require(errors, get(freebsd_backend_run, "worker_bridge", "extra_fd_canary_source") == "broker-nonmedia-canary-not-source-media", "backend bridge fd-5 canary must not be source-media authority")
    require(errors, get(freebsd_backend_run, "worker_bridge", "extra_fd_canary_must_be_observed_before_closefrom") is True, "backend bridge must require the worker to observe fd-5 before closing it")
    require(errors, get(freebsd_backend_run, "worker_bridge", "extra_fds_closed_before_cap_enter") is True, "backend bridge must require extra fd closure before cap_enter")
    require(errors, get(freebsd_backend_run, "invariants", "non_freebsd_apply_refusal_path_exercised_by_checker") is True, "backend run must keep the real-apply refusal path checked")
    require(errors, get(freebsd_backend_run, "invariants", "real_apply_python_fixture_worker_disallowed") is True, "backend run invariant must forbid Python fixture worker for real apply")
    require(errors, get(freebsd_backend_run, "invariants", "capsicum_worker_bridge_bound") is True, "backend run invariant must bind Capsicum bridge")
    require(errors, capsicum_bridge.get("kind") == "removable.media.capsicum.worker.bridge", "Capsicum worker bridge receipt must be present")
    require(errors, capsicum_bridge.get("result") == "passed", "Capsicum worker bridge receipt must pass")
    require(errors, get(capsicum_bridge, "source", "path") == "tools/freebsd/rm_post_detach_capsicum_worker.c", "Capsicum bridge must bind the C worker source")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_probe_result", "return_code") == 0, "Capsicum bridge syntax probe must pass")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "result") == "passed", "Capsicum bridge shim execution probe must pass")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "failure_run", "output_report", "error_code") == "input_fd_not_regular", "Capsicum bridge execution probe must surface non-regular fd failures")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "success_run", "extra_fd_canary") == 5, "Capsicum bridge success probe must pass fd-5 canary")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "success_run", "pass_fds") == [3, 4, 5], "Capsicum bridge success probe must inherit fd-5 into the child")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "success_run", "worker_env_policy") == "empty-environment", "Capsicum bridge success probe must clear worker environment")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "success_run", "worker_cwd_policy") == "private-empty-directory-not-media-not-repo", "Capsicum bridge success probe must use private non-media cwd")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "success_run", "output_report", "extra_fd_canary_observed_before_closefrom") is True, "Capsicum bridge success probe must prove fd-5 existed before closefrom")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "success_run", "output_report", "extra_fds_closed_before_cap_enter") is True, "Capsicum bridge success probe must prove fd-5 canary closure")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "failure_run", "pass_fds") == [3, 4, 5], "Capsicum bridge failure probe must inherit fd-5 into the child")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "failure_run", "worker_env_policy") == "empty-environment", "Capsicum bridge failure probe must clear worker environment")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "failure_run", "worker_cwd_policy") == "private-empty-directory-not-media-not-repo", "Capsicum bridge failure probe must use private non-media cwd")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "failure_run", "output_report", "extra_fd_canary_observed_before_closefrom") is True, "Capsicum bridge failure probe must prove fd-5 existed before closefrom")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "failure_run", "output_report", "extra_fds_closed_before_cap_enter") is True, "Capsicum bridge post-stdio failure probe must prove fd-5 canary closure")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "argument_rejection_run", "pass_fds") == [3, 4, 5], "Capsicum bridge argument-rejection probe must inherit fd-5 into the child")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "argument_rejection_run", "worker_env_policy") == "empty-environment", "Capsicum bridge argument-rejection probe must clear worker environment")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "argument_rejection_run", "worker_cwd_policy") == "private-empty-directory-not-media-not-repo", "Capsicum bridge argument-rejection probe must use private non-media cwd")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "argument_rejection_run", "output_report", "extra_fd_canary_observed_before_closefrom") is True, "Capsicum bridge argument-rejection probe must prove fd-5 existed before startup rejection")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "argument_rejection_run", "output_report", "error_code") == "path_arguments_rejected", "Capsicum bridge execution probe must surface argv/path rejection through fd 4")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "argument_rejection_run", "output_report", "failure_report_channel") == "delegated-output-fd-before-stdio-close", "Capsicum bridge argv/path rejection must not pretend stdio was already closed")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "argument_rejection_run", "output_report", "stdio_fds_closed_before_cap_enter") is False, "Capsicum bridge argv/path rejection must record stdio closure truthfully")
    require(errors, get(capsicum_bridge, "build", "cloudtainer_execution_probe_result", "argument_rejection_run", "stderr_bytes") == 0, "Capsicum bridge argv/path rejection probe must not rely on stderr")
    require(errors, get(capsicum_bridge, "launch_contract", "broker_must_unmount_before_exec") is True, "Capsicum bridge must require umount before exec")
    require(errors, get(capsicum_bridge, "launch_contract", "worker_environment_policy") == "empty-environment", "Capsicum bridge must require empty worker environment")
    require(errors, get(capsicum_bridge, "launch_contract", "worker_cwd_policy") == "private-empty-directory-not-media-not-repo", "Capsicum bridge must require a private non-media worker cwd")
    require(errors, get(capsicum_bridge, "launch_contract", "worker_must_close_stdio_fds_before_cap_enter") is True, "Capsicum bridge must close stdio before cap_enter")
    require(errors, get(capsicum_bridge, "launch_contract", "worker_must_verify_extra_fds_closed_before_cap_enter") is True, "Capsicum bridge must verify fd-5/extra-fd closure before cap_enter")
    require(errors, get(capsicum_bridge, "launch_contract", "broker_must_pass_nonmedia_fd5_canary_in_host_smoke") is True, "Capsicum bridge must require fd-5 canary in the real host smoke")
    require(errors, get(capsicum_bridge, "launch_contract", "worker_must_report_fd5_canary_observed_before_closefrom") is True, "Capsicum bridge must require fd-5 observation before closefrom")
    require(errors, get(capsicum_bridge, "source", "stdio_policy") == "close-fd-0-1-2-before-cap-enter", "Capsicum bridge source policy must bind stdio closure")
    require(errors, get(capsicum_bridge, "source", "failure_report_channel") == "delegated-output-fd-after-stdio-close", "Capsicum bridge source must bind delegated-output failure reports")
    require(errors, get(capsicum_bridge, "source", "startup_failure_report_channel") == "delegated-output-fd-before-or-after-stdio-close", "Capsicum bridge source must bind startup delegated-output failure reports")
    require(errors, get(capsicum_bridge, "source", "startup_pre_stdio_failure_report_channel") == "delegated-output-fd-before-stdio-close", "Capsicum bridge source must bind pre-stdio startup delegated-output failure reports")
    require(errors, get(capsicum_bridge, "source", "extra_fd_canary") == 5, "Capsicum bridge source must bind fd-5 canary")
    require(errors, get(capsicum_bridge, "source", "extra_fd_canary_source") == "broker-nonmedia-canary-not-source-media", "Capsicum bridge source fd-5 canary must be non-media")
    require(errors, get(capsicum_bridge, "source", "extra_fd_canary_must_be_observed_before_closefrom") is True, "Capsicum bridge source must require fd-5 observation before closefrom")
    require(errors, get(capsicum_bridge, "source", "extra_fd_scan_limit") == 64, "Capsicum bridge source must bind extra-fd scan limit")
    require(errors, get(capsicum_bridge, "backend_integration", "real_apply_cli_gate") == "capsicum-worker-required-for-real-apply", "Capsicum bridge must bind real-apply gate reason")
    require(errors, CAPSICUM_WORKER_SOURCE.exists(), "FreeBSD Capsicum fd-worker source must exist for the real apply bridge")
    if CAPSICUM_WORKER_SOURCE.exists():
        capsicum_src = CAPSICUM_WORKER_SOURCE.read_text(encoding="utf-8", errors="replace")
        for token in ["cap_enter()", "cap_rights_limit(REMEDIA_INPUT_FD", "cap_rights_limit(REMEDIA_OUTPUT_FD", "observe_extra_fd_canary_before_closefrom();", "extra_fd_canary_observed_before_closefrom", "closefrom(FD_AFTER_DELEGATED_SET)", "verify_extra_fds_closed_before_cap_enter();", "close_standard_fds();", "fatal_to_delegated_output", "failure_report_channel", "delegated-output-fd-before-stdio-close", "path_arguments_rejected", "stdio_fd_close_failed", "extra_fd_still_open_before_cap_enter"]:
            require(errors, token in capsicum_src, f"Capsicum worker source missing {token}")

    require(errors, host_smoke_refusal.get("kind") == "removable.media.local.freebsd.host.smoke.receipt", "FreeBSD host-smoke refusal receipt must be present")
    require(errors, host_smoke_refusal.get("result") == "refused", "cloudtainer host-smoke receipt must refuse rather than overclaim host execution")
    require(errors, host_smoke_refusal.get("refusal_reason") == "non-freebsd-host", "cloudtainer host-smoke refusal must be non-freebsd-host")
    require(errors, get(host_smoke_refusal, "scope", "worker_bridge_id") == capsicum_bridge.get("bridge_id"), "host-smoke refusal must bind the current Capsicum bridge id")
    require(errors, get(host_smoke_refusal, "scope", "fd5_canary_source") == "broker-nonmedia-canary-not-source-media", "host-smoke must bind a non-media fd-5 canary")
    require(errors, get(host_smoke_refusal, "scope", "mount_options") == ["ro", "nosuid", "noexec", "nosymfollow", "untrusted"], "host-smoke must bind the hardened FreeBSD mount tuple")
    require(errors, get(host_smoke_refusal, "invariants", "no_host_commands_after_refusal") is True, "host-smoke refusal must run no host commands in cloudtainer")
    require(errors, get(host_smoke_refusal, "invariants", "cloudtainer_does_not_claim_freebsd_capsicum_execution") is True, "host-smoke refusal must not claim cloudtainer Capsicum execution")


    require(errors, host_smoke_success_sim.get("result") == "passed", "host-smoke success simulation must pass")
    require(errors, get(host_smoke_success_sim, "simulation", "claims_real_freebsd_execution") is False, "host-smoke success simulation must not claim real FreeBSD execution")
    require(errors, get(host_smoke_success_sim, "simulation", "safe_capture_executed_against_simulated_mount_tree") is True, "host-smoke success simulation must exercise safe capture")
    require(errors, get(host_smoke_success_sim, "scope", "worker_bridge_id") == capsicum_bridge.get("bridge_id"), "host-smoke success simulation must bind the current bridge id")
    require(errors, get(host_smoke_success_sim, "host_smoke", "observed_fstyp") == "ufs", "host-smoke success simulation must observe UFS before mount")
    require(errors, get(host_smoke_success_sim, "host_smoke", "umounted_before_worker") is True, "host-smoke success simulation must unmount before worker")
    require(errors, get(host_smoke_success_sim, "host_smoke", "mdconfig_detached_before_worker") is True, "host-smoke success simulation must detach mdconfig before worker")
    require(errors, get(host_smoke_success_sim, "host_smoke", "worker_env_policy") == "empty-environment", "host-smoke success simulation must clear worker environment")
    require(errors, get(host_smoke_success_sim, "host_smoke", "worker_cwd_policy") == "private-empty-directory-not-media-not-repo", "host-smoke success simulation must use private non-media cwd")
    success_worker_report = get(host_smoke_success_sim, "host_smoke", "worker", "output_report") or {}
    require(errors, get(host_smoke_success_sim, "host_smoke", "capture_digest") == success_worker_report.get("input_sha256"), "host-smoke success simulation must bind worker input digest to safe-capture digest")
    require(errors, success_worker_report.get("extra_fd_canary_observed_before_closefrom") is True, "host-smoke success simulation must prove fd5 inheritance before closefrom")
    require(errors, success_worker_report.get("extra_fds_closed_before_cap_enter") is True, "host-smoke success simulation must prove extra fds closed before cap_enter")
    require(errors, get(host_smoke_success_sim, "invariants", "worker_input_sha256_matches_capture_digest") is True, "host-smoke success invariant must bind worker input digest")
    require(errors, get(host_smoke_success_sim, "invariants", "worker_environment_empty") is True, "host-smoke success invariant must bind empty environment")
    require(errors, get(host_smoke_success_sim, "invariants", "worker_cwd_private_not_media") is True, "host-smoke success invariant must bind private non-media cwd")
    require(errors, get(host_smoke_success_sim, "invariants", "fixture_root_admitted_before_host_commands") is True, "host-smoke success simulation must admit fixture root before host commands")
    require(errors, get(host_smoke_success_sim, "invariants", "fixture_source_stable_during_copy") is True, "host-smoke success simulation must prove source-stable fixture copy")
    require(errors, get(host_smoke_success_sim, "invariants", "fixture_copy_matches_source_manifest") is True, "host-smoke success simulation must bind fixture copy manifest equality")
    require(errors, get(host_smoke_success_sim, "invariants", "worker_source_copied_before_compile") is True, "host-smoke success simulation must copy worker source before compile")
    require(errors, get(host_smoke_success_sim, "invariants", "worker_source_stable_during_copy") is True, "host-smoke success simulation must prove source-stable worker source copy")
    require(errors, get(host_smoke_success_sim, "invariants", "worker_source_copy_matches_digest") is True, "host-smoke success simulation must bind worker source copy digest equality")
    require(errors, get(host_smoke_success_sim, "invariants", "compile_uses_private_worker_source_copy") is True, "host-smoke success simulation must compile from the private worker source copy")
    require(errors, get(host_smoke_success_sim, "invariants", "host_command_environment_sanitized") is True, "host-smoke success simulation must sanitize host command environment")
    require(errors, get(host_smoke_success_sim, "host_smoke", "host_command_env_policy") == "sanitized-locale-and-path-only", "host-smoke success simulation must bind sanitized host command env policy")
    require(errors, host_smoke_fstyp_output_failure_sim.get("result") == "failed", "host-smoke fstyp output simulation must fail receipt-shaped")
    require(errors, get(host_smoke_fstyp_output_failure_sim, "failure", "stage") == "fstyp-verify-ufs", "host-smoke malformed fstyp output must stop at fstyp-verify-ufs")
    require(errors, get(host_smoke_fstyp_output_failure_sim, "host_smoke", "worker_launched") is False, "host-smoke malformed fstyp output must not launch worker")
    require(errors, get(host_smoke_fstyp_output_failure_sim, "simulation", "fstyp_stdout_was_multiline") is True, "host-smoke fstyp simulation must bind malformed multiline output")
    require(errors, not any(isinstance(cmd, list) and cmd and cmd[0] == "/sbin/mount" for cmd in get(host_smoke_fstyp_output_failure_sim, "simulation", "fake_commands_observed") or []), "host-smoke malformed fstyp output must not reach mount")
    require(errors, host_smoke_fixture_admission_failure_sim.get("result") == "failed", "host-smoke fixture admission simulation must fail receipt-shaped")
    require(errors, get(host_smoke_fixture_admission_failure_sim, "failure", "stage") == "fixture-root-admission", "host-smoke fixture admission simulation must stop at fixture-root-admission")
    require(errors, host_smoke_fixture_admission_failure_sim.get("commands") == [], "host-smoke fixture admission failure must run no host commands")
    require(errors, get(host_smoke_fixture_admission_failure_sim, "invariants", "no_host_commands_after_fixture_admission_failure") is True, "fixture admission failure must bind no host commands")
    require(errors, host_smoke_fixture_copy_change_sim.get("result") == "passed", "host-smoke fixture copy source-change regression must pass")
    require(errors, get(host_smoke_fixture_copy_change_sim, "failure", "stage") == "fixture-root-copy", "fixture source mutation must fail at fixture-root-copy")
    require(errors, get(host_smoke_fixture_copy_change_sim, "invariants", "fixture_copy_change_detected") is True, "fixture copy source-change regression must bind change detection")
    require(errors, get(host_smoke_fixture_copy_change_sim, "invariants", "no_host_commands_after_fixture_copy_change") is True, "fixture copy source-change regression must run no host commands")
    require(errors, host_smoke_worker_source_copy_change_sim.get("result") == "passed", "host-smoke worker source copy source-change regression must pass")
    require(errors, get(host_smoke_worker_source_copy_change_sim, "failure", "stage") == "worker-source-copy", "worker source mutation must fail at worker-source-copy")
    require(errors, get(host_smoke_worker_source_copy_change_sim, "invariants", "worker_source_copy_change_detected") is True, "worker source copy regression must bind change detection")
    require(errors, get(host_smoke_worker_source_copy_change_sim, "invariants", "no_host_commands_after_worker_source_copy_change") is True, "worker source copy regression must run no host commands")
    require(errors, host_smoke_failure_sim.get("result") == "failed", "host-smoke failure simulation must fail receipt-shaped")
    require(errors, get(host_smoke_failure_sim, "failure", "receipt_shaped_instead_of_traceback") is True, "host-smoke failure simulation must stay receipt-shaped")
    require(errors, get(host_smoke_failure_sim, "host_smoke", "worker_launched") is False, "host-smoke pre-worker failure simulation must not launch worker")
    require(errors, get(host_smoke_failure_sim, "simulation", "claims_real_freebsd_execution") is False, "host-smoke failure simulation must not claim real FreeBSD execution")


    plan_ops = [op.get("op") for op in plan.get("operations", [])]
    receipt_ops = [op.get("op") for op in receipt.get("operations", [])]
    require(errors, plan_ops == ["capture", "classify", "scan", "sanitize"], f"plan op order drifted: {plan_ops}")
    require(errors, receipt_ops == plan_ops, f"receipt op order {receipt_ops} does not replay plan order {plan_ops}")

    plan_subject = get(plan, "subject", "digest")
    receipt_subject = get(receipt, "subject", "digest")
    capture_op = next((op for op in receipt.get("operations", []) if op.get("op") == "capture"), {})
    require(errors, plan_subject == receipt_subject, "plan and receipt subject digests differ")
    require(errors, capture_op.get("output_digest") == plan_subject, "capture output digest must equal selected subject digest")
    require(errors, get(harness_run, "capture", "observed_subject_digest") == plan_subject, "runnable harness observed digest must bind to selected subject digest")
    require(errors, get(harness_run, "capture", "observed_size_bytes") == get(plan, "subject", "size_bytes"), "runnable harness observed size must bind to selected subject size")
    harness_path_capture = get(harness_run, "capture", "path_capture") or {}
    require(errors, harness_path_capture.get("capture_api") == "dirfd-openat-no-symlink-components", "runnable harness must use dirfd/openat no-symlink path capture")
    require(errors, harness_path_capture.get("root_fd_pinned") is True, "runnable harness must pin the media root fd during capture")
    require(errors, harness_path_capture.get("opened_with_openat") is True, "runnable harness must open the selected subject via openat/dir_fd")
    require(errors, harness_path_capture.get("ancestor_symlink_policy") == "deny-each-ancestor-by-openat-o_directory-o_nofollow", "runnable harness must reject symlink ancestors")
    require(errors, harness_path_capture.get("leaf_symlink_policy") == "deny-leaf-by-openat-o_nofollow", "runnable harness must reject symlink leaves")

    first_plan_op = plan.get("operations", [{}])[0]
    first_params = first_plan_op.get("params", {}) if isinstance(first_plan_op, dict) else {}
    require(errors, first_plan_op.get("op") == "capture", "first operation must be capture")
    require(errors, first_params.get("post_capture_detach_evidence") == "device-detach-receipt-required-before-later-ops", "capture plan must require detach receipt before later ops")
    require(errors, first_params.get("post_detach_ingest_visibility") == "ingest-absent-in-later-worker", "later worker must not see the /ingest tree")
    require(errors, first_params.get("post_detach_reference_carryover") == "no-inherited-ingest-fd-cwd-root", "later worker must not inherit live ingest references")

    outputs = {o.get("role"): o for o in receipt.get("outputs", []) if isinstance(o, dict)}
    captured = outputs.get("captured-subject", {})
    derivative = outputs.get("sanitized-derivative", {})
    require(errors, captured.get("digest") == plan_subject, "preserved captured-subject output must keep the selected digest")
    require(errors, captured.get("locator_kind") == "digest-addressed-store", "captured subject must commit to digest-addressed store")
    require(errors, captured.get("locator_visibility") == "receipt-only-not-worker-visible", "store locator should not become worker-visible authority")
    require(errors, derivative.get("role") == "sanitized-derivative", "sanitized derivative output is missing")
    require(errors, derivative.get("digest") != captured.get("digest"), "derivative must be separate from preserved capture")
    require(errors, receipt.get("result", {}).get("status") == "ok", "canonical receipt result should stay ok")

    detach_map = get(detach, "runtime", "mapping") or {}
    require(errors, detach_map.get("detach_trigger") == "selected-subject-capture-verified", "detach must be triggered by verified capture")
    require(errors, detach_map.get("later_ops_dependency") == "no-device-presence-required-after-detach", "later ops must not require device presence")
    require(errors, detach_map.get("post_detach_ingest_visibility") == "ingest-absent-in-later-worker", "detach receipt must record absent ingest visibility for later worker")
    require(errors, detach_map.get("post_detach_projection_source_digest") == plan_subject, "post-detach projection source digest must bind to selected subject")

    execution = receipt.get("execution", {})
    require(errors, execution.get("network") == "none", "content import execution must have no network")
    require(errors, execution.get("post_detach_capability_mode_posture") == contract.get("worker", {}).get("capability_mode"), "receipt capability-mode posture must match post-detach contract")
    require(errors, execution.get("post_detach_network_posture") == contract.get("worker", {}).get("network"), "receipt network posture must match post-detach contract")

    capsicum = get(launch, "confinement", "capsicum") or {}
    devfs = get(launch, "confinement", "devfs") or {}
    pf = get(launch, "confinement", "pf") or {}
    mounts = get(launch, "confinement", "mounts") or {}
    network = launch.get("network", {})
    require(errors, capsicum.get("capability_mode_entered") is True, "launch evidence must prove cap_enter")
    require(errors, capsicum.get("path_reopen_after_entry") == "forbidden", "launch evidence must forbid path reopen after cap_enter")
    require(errors, devfs.get("visible_devices") == [], "post-detach worker must not see device nodes")
    require(errors, pf.get("network_default") == "deny-all", "post-detach pf posture must be deny-all")
    require(errors, mounts.get("media_mount_visible_to_worker") is False, "media mount must be absent from post-detach worker")
    require(errors, network.get("socket_descriptors") == [], "post-detach worker must not inherit sockets")

    prototype_invariants = prototype_receipt.get("invariants", {}) if isinstance(prototype_receipt, dict) else {}
    prototype_capture = prototype_receipt.get("capture", {}) if isinstance(prototype_receipt, dict) else {}
    prototype_worker = prototype_receipt.get("worker", {}) if isinstance(prototype_receipt, dict) else {}
    prototype_derivative = prototype_receipt.get("derivative", {}) if isinstance(prototype_receipt, dict) else {}
    require(errors, prototype_receipt.get("kind") == "removable.media.local.fallback.prototype.run.receipt", "prototype receipt is missing or has the wrong kind")
    require(errors, prototype_receipt.get("result") == "passed", "prototype receipt must pass")
    require(errors, prototype_receipt.get("mode_value") == "exercises-real-byte-capture-detach-ordering-and-fd-only-worker-delivery", "prototype must exercise byte capture, detach, and fd-only delivery")
    require(errors, prototype_capture.get("subject_kind") == "regular-file", "prototype must capture a regular file")
    require(errors, prototype_capture.get("verified_after_copy") is True, "prototype must verify preserved capture after copy")
    require(errors, prototype_capture.get("source_stable_after_copy") is True, "prototype must prove source stayed stable through capture")
    require(errors, prototype_capture.get("capture_api") == "dirfd-openat-no-symlink-components", "prototype must use dirfd/openat no-symlink path capture")
    require(errors, prototype_capture.get("root_fd_pinned") is True, "prototype capture must pin the media root fd")
    require(errors, prototype_capture.get("opened_with_openat") is True, "prototype capture must use openat/dir_fd")
    require(errors, prototype_receipt.get("detach", {}).get("original_media_root_removed_before_worker") is True, "prototype source tree must be detached before worker")
    require(errors, prototype_worker.get("input_delivery") == "preopened-read-fd-to-preserved-cas-object", "prototype worker must use preserved-copy fd input")
    require(errors, prototype_worker.get("source_path_passed_to_worker") is False, "prototype worker must not receive live source path")
    require(errors, prototype_worker.get("fd_inventory_supported") is True, "prototype worker must inventory inherited fds")
    require(errors, prototype_worker.get("unexpected_fds") == [], "prototype worker must not inherit unexpected fds")
    require(errors, prototype_receipt.get("detach", {}).get("source_media_fd_closed_before_detach") is True, "prototype must close source-media fd before detach")
    require(errors, prototype_receipt.get("detach", {}).get("source_media_fd_closed_before_worker") is True, "prototype must close source-media fd before worker launch")
    require(errors, prototype_worker.get("leak_canary_fd_seen") is False, "prototype worker must not inherit broker non-media fd canary")
    require(errors, prototype_worker.get("leak_canary_fd_source") == "broker-nonmedia-canary-not-source-media", "prototype fd leak canary must not be source-media authority")
    require(errors, prototype_worker.get("prelaunch_input_digest_matched") is True, "prototype must preflight preserved input digest before fd delegation")
    require(errors, prototype_derivative.get("payload_input_digest") == prototype_capture.get("digest"), "prototype derivative must bind the captured digest")
    for key in [
        "capture_before_detach",
        "no_live_media_path_after_detach",
        "worker_input_digest_equals_capture_digest",
        "rejected_path_traversal",
        "rejected_symlink_subject",
        "rejected_symlink_ancestor",
        "dirfd_openat_capture",
        "root_fd_pinned_capture",
        "source_stable_after_copy",
        "worker_fd_inventory_clean",
        "source_media_fd_closed_before_detach",
        "source_media_fd_closed_before_worker",
        "worker_nonmedia_fd_canary_not_leaked",
        "worker_leak_canary_not_source_media",
        "worker_preserved_input_preflighted",
    ]:
        require(errors, prototype_invariants.get(key) is True, f"prototype invariant {key} must be true")

    safe_capture_invariants = safe_capture_receipt.get("invariants", {}) if isinstance(safe_capture_receipt, dict) else {}
    safe_capture_capture = safe_capture_receipt.get("capture", {}) if isinstance(safe_capture_receipt, dict) else {}
    require(errors, safe_capture_receipt.get("kind") == "removable.media.local.safe_capture.probe.receipt", "safe-capture probe receipt is missing or has wrong kind")
    require(errors, safe_capture_receipt.get("result") == "passed", "safe-capture probe must pass")
    require(errors, safe_capture_capture.get("capture_api") == "dirfd-openat-no-symlink-components", "safe-capture probe must exercise dirfd/openat capture")
    for key in ["regular_file_capture_passed", "symlink_leaf_denied", "symlink_ancestor_denied", "directory_subject_denied", "path_traversal_denied", "source_stable_after_copy", "cas_write_policy_no_overwrite", "cas_idempotent_recapture_verified_existing", "cas_corrupt_existing_object_denied"]:
        require(errors, safe_capture_invariants.get(key) is True, f"safe-capture invariant {key} must be true")

    checkpoint_binding = reader_admission.get("checkpoint_binding", {})
    admission_state = reader_admission.get("admission_state", {})
    admitted = reader_admission.get("admitted_authority", {})
    require(errors, checkpoint_binding.get("checkpoint_observed") is True, "reader admission must observe checkpoint before broker use")
    require(errors, admission_state.get("broker_use_before_admission") is False, "broker use before admission must stay false")
    require(errors, admitted.get("query_projection_allowed") is True, "query projection lane should be admitted")
    require(errors, admitted.get("export_allowed") is False, "vertical slice should not silently grant export authority")
    require(errors, admitted.get("authority_broadened") is False, "reader admission must not broaden authority")

    if errors:
        print("Removable-media local fallback vertical slice check FAILED.")
        for error in errors:
            print("-", error)
        return 1

    print("Removable-media local fallback vertical slice check OK")
    print("Slice: read-only attach -> FreeBSD backend plan -> executable backend runner -> safe capture -> detach -> Capsicum-shaped fd worker -> reader admission")
    print("Executable prototype evidence: validation/removable-media-local-fallback-prototype-run.receipt.json")
    print("Safe capture evidence: validation/removable-media-safe-capture.receipt.json")
    print("FreeBSD host-smoke refusal: validation/removable-media-local-freebsd-host-smoke.refusal.json")
    print("FreeBSD backend plan: spec/examples/removable.media.local.freebsd.backend.plan.json")
    print("FreeBSD backend run: spec/examples/removable.media.local.freebsd.backend.run.receipt.json")
    print("Capsicum worker bridge: spec/examples/removable.media.capsicum.worker.bridge.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
