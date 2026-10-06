# DeriveBSD rev0514 session review: wrapper-digest resume guard

This cut packages the unfinished r545 removable-media/Capsicum evidence work and adds one more validation-evidence hardening before archive creation.

## Risk focus

The release-critical hygiene ledger already bound each row to the checker file digest with `tool_sha256`, but the ledger itself did not bind the wrapper that decides how rows are resumed, merged, and executed. That left a smaller stale-evidence gap: a changed `tools/hygiene.py` could still reuse old passed rows if the checker files themselves had not changed.

## Changes made

- `tools/hygiene.py` now emits top-level `hygiene_wrapper_sha256`.
- `tools/hygiene.py --resume-ledger` now refuses to reuse passed rows when the existing ledger's wrapper digest does not match the current `tools/hygiene.py` digest.
- `merge_existing_passed_rows()` now applies the same wrapper-digest gate before preserving old passed rows during atomic rewrites.
- `spec/cube.hygiene.run.ledger.schema.json` now requires `hygiene_wrapper_sha256`.
- `tools/check_cube_hygiene_run_ledger.py` now verifies the wrapper digest, verifies every row's `tool_sha256` against the current checker file, and includes a stale-wrapper regression probe.
- `docs/current/hygiene-run-ledger.md` now documents that resume is gated by selected profile, command shape, checker digest, and hygiene-wrapper digest.

## Why this matters

The project depends on chunked validation because the cloudtainer can interrupt long runs. Resume is valuable, but stale resume is dangerous. This cut keeps resumability while making wrapper changes invalidate prior rows instead of letting old green evidence survive silently.

## Validation evidence

Completed ledger:

`session-reviews/DeriveBSD-rev0514-2026.06.05-release-critical-hygiene-ledger.json`

Final result: `32 / 32` release-critical checks passed.

Additional direct checks run after copying the completed ledger into `spec/examples/cube.hygiene.run.ledger.json`:

- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`
- `python3 -B tools/validate_spec_examples.py`
- `python3 -B tools/lint_spec_schemas.py`
- `python3 -B tools/check_generated_docs.py`
- `python3 -B tools/check_no_python_bytecode_artifacts.py`
- `python3 -B tools/check_no_root_hygiene_log_dumps.py`
- `python3 -B tools/check_text_files_final_newline.py`

## Remaining risk

The next validation-evidence improvement should consider a stable selected-input digest for resumed rows. `tool_sha256` plus `hygiene_wrapper_sha256` prevents stale checker/wrapper reuse, but it does not by itself prove that all documents and examples consumed by a checker were unchanged between chunks. That is probably the next stale-evidence class to close.
