# Removable-media local fallback FreeBSD backend run

`removable.media.local.freebsd.backend.run.receipt` is the executable bridge from the r536 FreeBSD backend plan to a runnable backend path. It does not claim that this cloudtainer performed a real FreeBSD mount. Instead, `tools/run_removable_media_local_freebsd_backend.py` with `--mode fixture` creates a private mount-shaped fixture tree, admits the claimed filesystem family, captures `invoice.pdf` through `tools/removable_media_safe_capture.py`, removes the mount-shaped tree before worker launch, and runs the shared fd-only worker from `tools/removable_media_fd_worker.py`.

The receipt must keep the following facts true: the active mount option tuple is `ro,nosuid,noexec,nosymfollow,untrusted`; `nodev` is not emitted as a generic FreeBSD mount option; capture is dirfd/openat-shaped with no-follow leaf and ancestor rejection; the mount-shaped tree is gone before the worker starts; no device path or mount path appears in worker argv/env; the worker sees no unexpected fds; and a broker-owned non-media canary fd is not leaked.

The r538 hardening closes three evidence-loss paths in the same runner. Preserved captures are committed to the CAS with a no-overwrite link-and-verify-existing policy, so a corrupt object already present at the digest path fails closed instead of being replaced. Capture failures such as a missing selected member now produce a structured failed receipt: the mount-shaped tree is removed, capture evidence stays absent, `capture.error_reason` records the closed failure, and the fd-only worker is not launched. The fd-only derivative worker now opens the broker-owned output slot create-exclusive without `O_TRUNC`, so stale derivative bytes cannot be silently replaced.

The r539 hardening closes two host-runner footguns before real apply work begins. First, `--work-dir` is treated as a user-owned base directory: the runner creates an exclusive private child work root and never recursively deletes the base. The canonical receipt records `workspace.runtime_work_root_policy = private-temp-or-create-exclusive-child-under-user-base-no-rmtree` and `workspace.destructive_cli_work_dir_cleanup = false`, and the checker proves a sentinel file in the user base survives a fixture run. Second, `--mode apply-freebsd` validates the exact `/dev` path shape before host work and, on a real FreeBSD host, lstat-rejects symlink or non-character-device nodes before `fstyp` or `mount` can run.

Fixture-mode receipts must not impersonate host evidence. `mount.command_result` and `detach.umount_result` are null in cloudtainer fixture mode; they are reserved for the real FreeBSD apply path, where command, return code, timeout status, stdout/stderr byte counts, and stdout/stderr digests can bind `fstyp`, `mount`, and `umount` results without storing raw command output.

The same runner has a guarded `--mode apply-freebsd` path. Outside FreeBSD, real apply returns an explicit non-FreeBSD real-apply refusal rather than pretending the host sequence ran. On a future FreeBSD host, the apply path is allowed only for base-system filesystem families first; exFAT remains helper-gated until `mount.exfat`/FUSE semantics and post-mount option behavior are qualified.

The production isolation bridge now has concrete source rather than only prose. `tools/freebsd/rm_post_detach_capsicum_worker.c` is a FreeBSD-only fd worker scaffold: the broker delegates input fd 3 and output fd 4 after detach, the worker calls `closefrom(5)`, limits those descriptors with `cap_rights_limit`, closes fd 0/1/2 with `close-fd-0-1-2-before-cap-enter`, enters `cap_enter`, accepts no argv paths, and writes only through the delegated output fd. `tools/check_removable_media_local_fallback_capsicum_worker_source.py` statically guards those properties until a real FreeBSD host can compile and run it.

Run:

```sh
python3 tools/check_removable_media_local_fallback_freebsd_backend_run.py
python3 tools/check_removable_media_local_fallback_vertical_slice.py
```

## r540 proof correction

This cut fixes the detach/fd-canary proof. The fixture backend and no-root prototype now close any source-media fd before detach and before worker launch. The fd-leak canary is broker-owned non-media state, so proving the child did not inherit it no longer keeps source-media authority alive. The worker input is also preflighted as a regular, non-symlink, digest-matched preserved CAS object before fd delegation. Real FreeBSD apply refuses before `fstyp` or `mount` with `capsicum-worker-required-for-real-apply` until the Capsicum worker bridge is compiled and wired.


## r541 bridge correction

The backend run receipt now includes `worker_bridge`, binding `removable.media.capsicum.worker.bridge` and the C worker source digest. Fixture mode still uses `tools/removable_media_fd_worker.py`, but the worker evidence is marked `python-fd-worker-cloudtainer-only` and `real_apply_python_fixture_worker_allowed = false`. The real apply function no longer carries dead `fstyp`/`mount`/Python-worker code behind an unconditional gate; it returns structured refusals until the FreeBSD Capsicum worker bridge is compiled and wired.

- `tools/freebsd/rm_post_detach_capsicum_worker.c` now closes stdio before delegated-right limiting and before `cap_enter()`, then `fstat`s the delegated input and output fds after entering capability mode. If fd delegation is wrong after stdio closure, the worker writes a JSON failure report through delegated output fd 4 with `failure_report_channel = delegated-output-fd-after-stdio-close`; the r543/r544 bridge probes exercise success, `input_fd_not_regular`, and `path_arguments_rejected` cases without claiming real Capsicum in the cloudtainer. Startup failure evidence is now bound by `startup_failure_report_channel = delegated-output-fd-before-or-after-stdio-close`; the argv/path rejection probe specifically reports `failure_report_channel = delegated-output-fd-before-stdio-close` and `stdio_fds_closed_before_report = false`, so it is fd-4-visible without pretending stdio was already closed.


2026-06-05r545 correction: startup/path-argument rejection is now explicitly pre-stdio evidence. The worker reports those failures on delegated fd 4 with `failure_report_channel = delegated-output-fd-before-stdio-close`, `stdio_fds_closed_before_report = false`, and `stdio_fds_closed_before_cap_enter = false`; post-stdio failures still use `delegated-output-fd-after-stdio-close`. The cloudtainer probe shim also avoids a sentinel-style `cap_rights_init()` varargs loop by using a variadic macro wrapper.

2026-06-05r548 correction: backend worker-bridge evidence now binds the fd-5 broker non-media canary, `extra_fds_closed_before_cap_enter`, and `extra_fd_scan_limit`; the companion FreeBSD host-smoke runner is documented in `docs/current/removable-media-freebsd-host-smoke.md` and refuses in this cloudtainer rather than pretending host proof occurred.

2026-06-05r548 correction: host-smoke failures are receipt-shaped before real FreeBSD proof. The host-smoke checker injects compile and mount failures, proves cleanup evidence and no worker launch, and keeps the production worker boundary tied to the C worker report fields including `input_sha256`, `extra_fds_closed_before_cap_enter`, and `extra_fd_scan_limit`.


2026-06-05r549 correction: backend `worker_bridge` evidence now binds `production_worker_env_policy = empty-environment` and `production_worker_cwd_policy = private-empty-directory-not-media-not-repo`, matching the C-worker bridge and FreeBSD host-smoke launch contract.
2026-06-05r550 correction: backend worker-bridge evidence now binds the strengthened fd-slot launcher policy so real apply cannot inherit the old target-slot cross-dup footgun.
2026-06-05r552 correction: backend worker-bridge evidence now binds the r552 Capsicum bridge id and the host-smoke command-redaction/parser hardening.

2026-06-05r554 correction: backend worker-bridge evidence now binds the r554 Capsicum bridge id while host-smoke evidence keeps private source-copy, sanitized host-command environment, and strict command-output parser proofs.

2026-06-16r572 fixture correction: backend fixture mode now uses the same valid visible deterministic PDF bytes as the local fallback harness (`sha256:01a0cd0826db2a58f930defd65189517c567703c224d715abefeb66897a5e2cc`) so the positive path is no longer backed by a malformed or blank-rendering PDF fixture.

Last updated: 2026-06-16r572
