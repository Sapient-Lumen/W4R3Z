# Current hygiene run ledger

`cube.hygiene.run.ledger` is the machine-readable evidence shape emitted by `tools/hygiene.py --ledger` or `tools/hygiene.py --ledger-json`. It records the selected profile, wrapper, generated version, per-check command, return code, elapsed seconds, best-effort child max RSS, stdout/stderr digests, byte and line counts, timeout classification, and whether the selected shard actually finished.


Current checked-in example snapshot for 2026-06-18r630. The canonical example is the current release-critical ledger; r630 keeps the release-critical ledger focused on admitted fixture repository snapshots, snapshot/catalog/payload drift rejection, and finite transitive closure substance rather than new schema families. The canonical example binds front-door docs to executable evidence, not terminal scrollback. The release-critical profile includes the dry-run runtime golden thread, the live checked-in import root gate, the real-host work-order checker, the self-verifying work-order digest guard, sealed returned-proof preflight/import, host-side preflight helper, idempotent sealed-import retry guard, and exclusive sibling import-root lock guard; default audit accepts only `real-host-proof` and the checked-in path requires preserved primary-production target tier evidence:

Current checked-in example snapshot:

```text
selected_profile: release-critical
checks_total: 52
checks_completed: 52
passed: 52
failed: 0
timed_out: 0
run_complete: true
```

Use it when a release run would otherwise rely on terminal scrollback:

```sh
python3 tools/hygiene.py --profile release-critical --ledger-json spec/examples/cube.hygiene.run.ledger.json
```

For bounded local experimentation, add `--timeout-seconds` with a positive number. Timed-out checks are recorded with status `timed-out` and return code `124`. If a cloudtainer or terminal session interrupts a ledgered run, rerun the same profile with `--resume-ledger` and the same `--ledger-json` path; already-passed rows for that profile are retained, while failed, timed-out, or missing checks run again. The ledger intentionally stores output digests and sizes rather than full stdout/stderr tails so the evidence remains compact and support-safe.

The r535 correction remains active in r562: a partial ledger can no longer look green merely because the checks that happened to finish passed. `checks_total` is the planned selected-check count, `checks_completed` is the number of result rows already written, and `run_complete` is true only when those match. A partial ledger has `run_complete = false` and `result = failed` until the shard finishes.


The r555 timeout correction adds process-boundary evidence to each row: `process_group_isolated`, `timeout_kill_scope`, `timeout_termination_signal`, and `timeout_grace_seconds`. The wrapper starts each checker in a separate process group and, on timeout, terminates the whole group before writing the row. This closes a cloudtainer completion-risk gap where parent-only timeout handling could leave a nested checker process running after the ledger marked the child timed out.

Rows also classify abnormal child termination. A negative return code must be explicit as `failure_class: terminated-by-signal`, `terminated_by_signal: true`, and a `signal_name` such as `SIGKILL`, so cloudtainer resource kills are not confused with ordinary assertion failures or timeouts.

Interrupted runs can be continued with `--resume-ledger`; passed rows from the same selected profile are kept, while failed, timed-out, missing, no-longer-selected, changed-checker, or stale-wrapper checks are rerun or dropped according to the current profile selection.


The r557 resume-safety correction binds the ledger and every result row to `cube_input_sha256`, `cube_input_fingerprint_scope`, and `cube_input_file_count` for the source/docs/spec/tools/fixtures surface, excluding ledger outputs. `--resume-ledger` remains useful after a cloudtainer interruption, but a schema, example, documentation, fixture, checker library, or executable-mode change now invalidates old passed rows instead of letting them hide drift. Session-review ledgers and the canonical ledger example are excluded from the fingerprint so the ledger file does not invalidate itself after every row. Timeout cleanup is also bounded after SIGKILL: if a cloudtainer leaves a checker temporarily unreapable, the row records `SIGKILL-unreaped` rather than hanging the ledger writer forever.

The r561 runner-environment correction binds the ledger and every result row to `runner_environment_sha256` and `runner_environment_scope`. Checker bytes and `cube_input_sha256` catch repository edits; the runner fingerprint catches validation-engine drift such as different interpreter bytes, Python version, platform, or `jsonschema` package version. The r614 correction hashes interpreter contents instead of the literal `sys.executable` path and discovers `jsonschema` independently of `site` initialization, so `python`, `python3`, renamed identical launchers, and the documented `-S` invocation share one identity while genuinely different runner bytes still invalidate resumed proof. `--resume-ledger` rejects passed rows only when that normalized validation engine fingerprint changes.


The r558 run-budget correction adds `--max-run-seconds` for ledger mode. When set, the wrapper records `run_budget_seconds` and `run_budget_status`, and stops cleanly between checks once the budget is reached. This is not a substitute for per-check `--timeout-seconds`; it is a cloudtainer-friendly chunk boundary so long release/post-detach runs can leave a coherent partial ledger before an outer execution window kills the whole wrapper.

The r559 check-budget correction makes `--max-checks` receipt-visible too. When a chunk stops because its check-count budget is reached, the ledger records `check_budget_limit` and `check_budget_status` (`stopped-before-check-budget`); completed check-budgeted runs record `completed-within-check-budget`. This distinguishes deliberate short chunks from accidental failure or an external kill.

The r630 release-critical profile keeps the runtime golden thread executable and now proves repository-snapshot admission before catalog projection: stale snapshot bytes are rejected, snapshot/payload dependency drift is rejected, and snapshot policy/digest evidence is carried through lock, plan, artifact, package-material manifest, activation, and explanation while retaining the r629 catalog/payload and r628 closure guards.

The r628 release-critical profile keeps the runtime golden thread executable and now proves finite fixture package dependency closure: requested `nginx` carries `openssl` and `pcre2` dependency bytes into lock/build/explain evidence, missing dependency targets are rejected before lock creation, and dependency cycles are rejected before they become artifact evidence while retaining the r627 material-byte and mutable-closure guards.

The r627 release-critical profile keeps the runtime golden thread executable and now proves checked-in package material-byte sha256/size verification, artifact carry-forward under `inputs/packages/`, and mutable `:latest` closure rejection while retaining the r626 transaction-spine guards.

The r625 release-critical profile keeps the runtime golden thread executable and now proves `.derive-runtime-state-journal.json` stale-journal refusal, journal preservation on refusal, and journal cleanup after successful activation/rollback while retaining the r624 state lock and no-clobber generation guards.

The r582 release-critical profile includes `tools/check_canonical_json_digest_contract.py`, `tools/check_json_duplicate_key_rejection.py`, `tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`, `tools/check_removable_media_local_fallback_freebsd_host_proof_bundle.py`, `tools/check_removable_media_local_fallback_freebsd_host_proof_handoff.py`, `tools/check_removable_media_local_fallback_freebsd_host_proof_importer.py`, `tools/check_removable_media_local_fallback_freebsd_host_proof_import_audit.py`, `tools/check_removable_media_local_fallback_freebsd_host_proof_checked_import_gate.py`, `tools/check_removable_media_local_fallback_freebsd_host_proof_preflight.py`, `tools/check_removable_media_local_fallback_freebsd_host_proof_collect_import.py`, and `tools/check_freebsd_real_host_proof_theatre_gate.py`, so a green release ledger now proves the restricted-JCS helper, duplicate-key rejection, command-shape digest verification, exact proof-tool-set refusal semantics, runner-contract / cube-cut version-clarity checks, valid visible PDF fixture binding, release-floor proof binding, finite digest-bound host-proof handoff verification, finite digest-named proof import, post-import import-root auditing, the live checked-in import root `validation/freebsd-host-proof-imports` where default audit accepts only `real-host-proof`, host-proof preflight refusal on unsupported hosts, one-command strict collect/import ordering, strict resume-from-handoff recovery, run-receipt failure observability, atomic symlink-refusing run-receipt writes, and rejection of checked-in real-proof theatre together.

The r560 partial-exit correction makes those deliberate chunks visible to shell wrappers too. A completed all-passing ledger returns exit code 0; a checker failure or timeout returns 1; and an otherwise clean incomplete budgeted ledger returns exit code 2. That keeps `--max-checks` or `--max-run-seconds` slices useful for cloudtainer progress without allowing CI, scripts, or future agents to mistake partial evidence for a completed green profile.

The r556 fresh-run correction makes resumable evidence explicitly opt-in. `write_ledger(..., preserve_existing_passed=False)` is the default, so a fresh `--ledger-json` run rewrites from the rows it actually executed; existing passed rows are merged only when `--resume-ledger` selects `preserve_existing_passed=True`. This prevents an old partial ledger at the same path from masquerading as a new run while preserving monotonic passed-row merge for explicit interrupted-run continuation. The write path remains atomic replace plus fsync, with a regression check in `tools/check_cube_hygiene_run_ledger.py`.

The r545 evidence correction binds each result row to `tool_sha256`. The r546 correction also binds the ledger itself to `hygiene_wrapper_sha256`, r557 adds `cube_input_sha256`, and r561 adds `runner_environment_sha256`, so a resumed row is reused only when the selected profile, command shape, checker file digest, current `tools/hygiene.py` digest, current checked cube input fingerprint, and current Python/jsonschema runner fingerprint still match. That keeps chunked release runs from becoming a stale-evidence cache after either a checker or the wrapper changes.

The r597 release-critical pass keeps the profile at 49 checks while making the existing FreeBSD handoff/import checkers prove optional handoff members are checksum-bound and imported proof summaries preserve host target tier. `tools/check_current_generated_surface_sync.py` still binds this doc, the schema-audit current doc, the schema-refactor current doc, and the hygiene-checkset current doc to their checked-in generated JSON examples before release evidence can pass.

The r615 release-critical pass grows the profile to 52 checks by promoting `tools/check_runtime_golden_thread.py`. A green release ledger now proves the local Spec → Lock → Plan → Artifact → Activate → Explain → Rollback seam on `spec/examples/microvm.spec.json`, while preserving the explicit boundary that no FreeBSD boot environment is activated and no bhyve VM is launched in the cloudtainer.


Schema and canonical example:

- `spec/cube.hygiene.run.ledger.schema.json`
- `spec/examples/cube.hygiene.run.ledger.json`

r541 adds `--max-checks` chunking, r558 adds `--max-run-seconds` run-budget chunking, r559 records `check_budget_status`, r560 makes clean incomplete chunks return exit code 2, and r561 binds resume rows to `runner_environment_sha256` so release-critical ledger rows can be accumulated without losing partial evidence or confusing intentional chunks with completed passes.

r546 adds stale-release resume protection: `tools/hygiene.py` refuses to resume or merge passed rows unless the existing ledger `generated_for_version` and `ledger_id` match the current release token, and `tools/check_cube_hygiene_run_ledger.py` proves stale prior-release rows are not reused. The wrapper also writes a current partial ledger before the first child check so early interruption cannot leave an older canonical ledger in place.

r584 note: release-critical still runs 45 checks, with the existing collect/import proof-path guard sharpened instead of adding another registry check. The collect/import guard now proves `tools/freebsd/collect_import_removable_media_local_fallback_host_proof.sh --run-receipt RUN_RECEIPT` writes a strict run receipt through the bound atomic writer, self-validates that payload before publish, accepts the emitted receipt with `tools/freebsd/validate_collect_import_run_receipt.py`, rejects tampered receipts that falsely report collection, rejects stray `proof_status = real-host-proof` claims and unexpected invariant keys, refuses symlink receipt destinations without overwriting their targets, and still proves `--resume-handoff HANDOFF_DIR` skips only the scarce collector before default verify/import/audit.


The r589 release-critical pass keeps the profile focused while tightening the scarce-host transport/import checks: broken allowed-name symlinks are rejected before handoff reads, import directories use the full receipt canonical digest instead of a short prefix, and unsealed replacements publish atomically without stale backup residue.

The r590 release-critical pass keeps the profile focused while tightening FreeBSD proof import auditability: `import.receipt.json` now binds source transport provenance, sealed imports record the sealed archive digest/size/format/policy before scratch cleanup, and the import auditor rejects missing source-transport evidence.

The r591 release-critical pass keeps the profile focused while tightening loose FreeBSD proof directory imports: copied handoff members now use the nofollow staging copy policy, import receipts bind `copy_policy`, and the import auditor rejects missing copy-policy evidence.

The r605 release-critical pass keeps the profile at 49 checks while correcting the live supported FreeBSD floor from 14.3 to 14.4. The checked-in import root gate still prevents proof theatre; the gap is not a simulated failure, it is the explicit absence of imported real-host proof.


The r606 release-critical pass keeps the checked-in import root gate in the profile, but its output now carries proof status counts from `tools/freebsd/report_removable_media_local_fallback_host_proof_imports.py`: the live checked-in import root `validation/freebsd-host-proof-imports` still has `status=blocked-no-real-host-proof-import`, `proof_complete=false`, `primary_production_real_host_proof=0`, and `real_host_proof=0`. The default audit accepts only `real-host-proof`, and a future checked-in proof must preserve the primary-production target tier; this status line prevents the empty-root structural audit from looking like completion.

The r608 release-critical pass keeps the profile at 50 checks while making `tools/check_removable_media_local_fallback_freebsd_host_proof_work_order.py` prove that the staged first-proof kit verifies itself before scarce FreeBSD host time is spent. The checked-in work order now binds `RUN_ON_FREEBSD.sh`, `IMPORT_IN_CLOUDTAINER.sh`, and `VERIFY_WORK_ORDER.sh` by size, mode, and sha256, and also binds the repo proof tools that the copied kit will execute. This is deliberately an import-readiness correction, not proof theatre: the live import status remains `blocked-no-real-host-proof-import` until a real 15.1 host handoff is imported.

The r609 release-critical pass grows the profile to 51 checks by promoting `tools/check_removable_media_local_fallback_freebsd_host_proof_sealed_preflight.py`. A green release ledger now proves that `tools/freebsd/preflight_sealed_removable_media_local_fallback_host_proof_import.py` can dry-run a returned sealed handoff archive, predict the import identity, reject duplicate publish targets by default, require the primary-production target when requested, and leave the live import root untouched before the real sealed importer runs.

The r610 release-critical pass keeps the profile at 51 checks while closing a host-side privilege split in the first-proof work order. The checked-in kit now includes `PREFLIGHT_ON_FREEBSD.sh`; it verifies the copied kit and runs the root-required FreeBSD host preflight directly as uid 0 or through `sudo env PYTHON=...` before `RUN_ON_FREEBSD.sh` attempts collection. This makes unsupported or misprivileged hosts fail before scarce collection, sealing, or import work.

Last updated: 2026-06-18r630
