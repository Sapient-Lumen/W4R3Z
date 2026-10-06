# Removable-media Capsicum worker bridge

`removable.media.capsicum.worker.bridge` records the host-worker boundary that must be true before `tools/run_removable_media_local_freebsd_backend.py --mode apply-freebsd` can become a real mount/capture/worker path.

The cloudtainer claim is deliberately narrow: `tools/freebsd/rm_post_detach_capsicum_worker.c` is syntax-checked with `DERIVEBSD_CAPSICUM_COMPILE_PROBE` and `tools/freebsd/derivebsd_capsicum_probe_shim.h`, but Capsicum execution is not claimed here. The production claim is FreeBSD-only: compile the same source against `<sys/capsicum.h>` into a private work root, bind the source and binary digest in the host receipt, unmount/detach the media before exec, close fd 0/1/2 with the `close-fd-0-1-2-before-cap-enter` policy, then launch the worker with only fd 3 for the preserved CAS object and fd 4 for the broker-owned derivative output slot.

This bridge exists to prevent the Python fixture worker (`python-fd-worker-cloudtainer-only` vs `freebsd-capsicum-c-worker`) from becoming the accidental host backend. The canonical backend receipt now carries `worker_bridge`, marks the fixture launcher as `python-fd-worker-cloudtainer-only`, and sets `real_apply_python_fixture_worker_allowed = false`. Real CLI apply remains gated with `capsicum-worker-required-for-real-apply` until this bridge is compiled and wired on FreeBSD.


The r543 bridge also runs a cloudtainer shim execution probe. That probe compiles the C worker with the Capsicum shim, executes a regular-input fd 3 / fd 4 success case, executes a directory-fd failure case, and verifies that `input_fd_not_regular` is written as JSON on delegated fd 4. r544 extends the same execution probe with an argv/path rejection case and requires `path_arguments_rejected` on delegated fd 4 with zero stdout/stderr bytes, `failure_report_channel = delegated-output-fd-before-stdio-close`, and `stdio_fds_closed_before_report = false`. This remains `cloudtainer-shim-execution-probe-not-capsicum-execution`; it proves fd wiring and startup/failure-report visibility, not real Capsicum.

The syntax-probe command is intentionally recorded with repository-relative include/source paths. That keeps durable bridge evidence portable across cloudtainers while the actual command still runs with `cwd` pinned to the archive root. The build guard reuses the bridge module's command generator and writes `validation/removable-media-capsicum-worker-build-probe.receipt.json` as a durable probe receipt.

Run:

```sh
python3 tools/check_removable_media_local_fallback_capsicum_worker_bridge.py
python3 tools/check_removable_media_local_fallback_capsicum_worker_build.py
python3 tools/check_removable_media_local_fallback_freebsd_backend_run.py
```

- The C worker closes fd 0/1/2 before delegated-right limiting and before `cap_enter` so stdio cannot accidentally carry source-media authority into the post-detach worker. Startup failures and later failures use delegated output fd 4: startup failures bind `startup_failure_report_channel = delegated-output-fd-before-or-after-stdio-close` and distinguish `failure_report_channel = delegated-output-fd-before-stdio-close` before the close loop completes, while post-stdio failures bind `failure_report_channel = delegated-output-fd-after-stdio-close`. It then performs fd-type validation with `fstat` after entering capability mode, so delegated fd 3 and fd 4 must be regular files rather than pipes, devices, or sockets before payload bytes are read or written.


2026-06-05r545 correction: startup/path-argument rejection is now explicitly pre-stdio evidence. The worker reports those failures on delegated fd 4 with `failure_report_channel = delegated-output-fd-before-stdio-close`, `stdio_fds_closed_before_report = false`, and `stdio_fds_closed_before_cap_enter = false`; post-stdio failures still use `delegated-output-fd-after-stdio-close`. The cloudtainer probe shim also avoids a sentinel-style `cap_rights_init()` varargs loop by using a variadic macro wrapper.

2026-06-05r548 correction: the cloudtainer execution probe now passes fd-5 as a broker non-media canary into the child with `pass_fds=(3, 4, 5)` and the C worker/probe shim exercise `closefrom(FD_AFTER_DELEGATED_SET)`. Successful and post-stdio failure reports bind `extra_fd_canary_observed_before_closefrom = true`, `extra_fds_closed_before_cap_enter = true`, and `extra_fd_scan_limit = 64`; the argument-rejection path remains pre-stdio evidence and does not claim the closefrom proof.

2026-06-05r548 correction: the bridge now binds worker-reported `input_sha256` and the fd-5 canary observation-before-`closefrom` proof, so a future host-smoke run must prove the C worker processed the preserved CAS object and closed inherited authority.


2026-06-05r549 correction: the bridge execution probe now launches the C worker with `env={}`, records `worker_env_policy = empty-environment`, and uses a `worker-empty-cwd` private directory with `worker_cwd_policy = private-empty-directory-not-media-not-repo`. The bridge/backend binding also retains the `duplicate-target-fds-above-delegated-range-before-clearing-slots` fd-slot policy so inherited environment, cwd, and parent fd slots are all explicit launch-envelope evidence.

2026-06-05r549 digest-vector correction: `tools/check_removable_media_local_fallback_capsicum_worker_sha256_vectors.py` compiles the same shim worker and runs empty, SHA padding-boundary, block-boundary, and multi-block fd-3 inputs. Each worker-reported `input_sha256` must match Python `hashlib`, with fd 5 still passed and closed, so host-smoke is not relying on a one-string digest smoke test.
2026-06-05r550 correction: bridge execution evidence now carries the strengthened fd-slot launcher policy, including out-of-band saved duplicates above fd 3/4/5 so a backup cannot be confused with another target slot.
2026-06-05r550 evidence guard: `tools/check_removable_media_fd_slot_policy_consistency.py` keeps the fd-slot launcher policy synchronized across implementation, schemas, examples, validation receipts, backend binding, and documentation.

2026-06-05r552 correction: bridge/backend receipts are refreshed against the strict host-smoke parser and stable command-redaction evidence.

2026-06-05r554 correction: bridge/backend receipts are refreshed against the host-smoke private worker-source copy, sanitized host-command environment, and strict `fstyp` parser evidence.

Last updated: 2026-06-05r554
