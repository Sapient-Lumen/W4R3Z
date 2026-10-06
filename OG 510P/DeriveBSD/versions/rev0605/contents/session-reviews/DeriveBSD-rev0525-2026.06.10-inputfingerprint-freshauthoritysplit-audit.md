# DeriveBSD rev0525 session audit — input-fingerprinted resume and fresh-authority split

Date: 2026-06-10
Base: rev0524
Result: rev0525

## Risk-first changes

This pass avoided adding another receipt family and instead fixed two completion risks in the checker substrate:

1. Fresh `tools/hygiene.py --ledger` runs were already fixed in rev0524, but `--resume-ledger` still trusted passed rows by checker/wrapper digest without binding the source/docs/spec/tools/fixtures inputs read by those checkers. Rev0525 adds `cube_input_sha256`, `cube_input_fingerprint_scope`, and `cube_input_file_count` to the ledger root and every row. Resume now refuses old passed rows after any checked input changes.
2. The timeout path killed timed-out process groups, but the final SIGKILL reap could still hang if a cloudtainer left the child temporarily unreapable. Rev0525 bounds that wait and records `SIGKILL-unreaped` rather than letting the ledger writer hang forever.

The fingerprint intentionally excludes `session-reviews/` and `spec/examples/cube.hygiene.run.ledger.json`, because ledger outputs must not invalidate themselves after every row. It also excludes transient Python bytecode artifacts and `__pycache__` directories.

## Cube refactor

The p0 target `spec/removable.media.local.post_detach.fresh.authority.consumption.receipt.schema.json` was split into:

- `spec/removable.media.local.post_detach.fresh.authority.consumption.receipt.schema.json` — generic runtime contract with dynamic digest/schema/path slots.
- `spec/removable.media.local.post_detach.fresh.authority.consumption.receipt.fixture.schema.json` — exact canonical r512 fixture surface.

`tools/check_removable_media_local_post_detach_fresh_authority_consumption_receipt.py` now validates the canonical object against both schemas.

## Coupling found and corrected

The split exposed downstream fixture coupling in successor-index cutover/checkpoint and reader admission/use checks. Those checks were still demanding exact canonical digests from the runtime fresh-authority-consumption schema. Rev0525 moves exact digest assertions to the new fixture schema and keeps runtime schema checks generic via `sha256Digest`.

## Front-door budget

`docs/00-index.md` exceeded the hard line budget by two lines after the r557 entry. The fix compressed the “Where to add new work” block rather than raising the budget.

## Validation ledgers

- Release-critical: `session-reviews/DeriveBSD-rev0525-2026.06.10-release-critical-hygiene-ledger.json` — 35/35 passed.
- Post-detach: `session-reviews/DeriveBSD-rev0525-2026.06.10-post-detach-hygiene-ledger.json` — 39/39 passed.
- Schema-cube audit: `session-reviews/DeriveBSD-rev0525-2026.06.10-schema-cube-hygiene-ledger.json` — 3/3 passed.
- Generated surface: `session-reviews/DeriveBSD-rev0525-2026.06.10-generated-surface-hygiene-ledger.json` — 2/2 passed.

## Remaining risk

The cloudtainer still intermittently kills long post-detach invocations even when the individual checks pass on retry. The new ledger semantics make this less dangerous, but the next infrastructure improvement should add an official quiet/chunked runner mode so resumed runs do not reprint every prior passed row and can run one not-yet-passed check per invocation without ad hoc scripts.

## Next cube targets

After this split, the next p0 targets are successor-index checkpoint, reader-use ledger retention, reader-use ledger retention expiry, and launch evidence. The highest-leverage next split is successor-index checkpoint because it sits directly downstream of the fresh-authority consumption and cutover path touched here.
