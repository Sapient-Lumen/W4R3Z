# DeriveBSD rev0526 session audit: successor checkpoint split and run-budget ledger

## Scope

This pass deliberately stayed implementation-heavy: close the next p0 schema-cube split, remove a real cloudtainer completion risk, and keep the post-detach closure profile green without adding new doctrine or registry-only surfaces.

## Priority change: cloudtainer run-budget ledger

`tools/hygiene.py` now accepts `--max-run-seconds` in ledger mode. The wrapper checks the budget between child checks, writes a coherent partial ledger, and exits before an outer cloudtainer execution limit can kill the whole run mid-row. The ledger schema now records `run_budget_seconds` and `run_budget_status` so this behavior is receipt-visible instead of hidden operator lore.

The budget is intentionally not a replacement for per-check `--timeout-seconds`. It is a chunk boundary for long profiles. Per-check timeout still owns stuck children; the run budget owns the wrapper's total wall-clock slice.

## Cube refactor: successor-index checkpoint split

The p0 target `spec/removable.media.local.post_detach.successor.index.checkpoint.receipt.schema.json` was split into a generic runtime schema plus `spec/removable.media.local.post_detach.successor.index.checkpoint.receipt.fixture.schema.json` for the exact r514 canonical fixture. The runtime schema now carries digest shape and receipt structure instead of embedding exact fixture digests.

That split exposed useful downstream coupling in reader admission and reader use checks. Both were still demanding exact successor-checkpoint reader digests from the runtime checkpoint schema. Those exact checks now target the checkpoint fixture schema, while the runtime schema check requires the generic `sha256Digest` shape.

## Risk corrected over time

The first full post-detach attempt exceeded the interactive outer execution window around the launch-evidence row even though that checker passes directly. Chunked resume completed the profile. This validates the direction of `--max-run-seconds`: long lifecycle profiles should stop deliberately between rows rather than rely on the host to preserve process state.

The front-door budget also caught a small but real line-count regression in `docs/00-index.md`. The correction tightened whitespace instead of raising the budget, preserving the hard line ceiling.

## Current validation evidence

- `release-critical`: 35/35 passed.
- `post-detach`: 39/39 passed, completed via explicit resume chunks.
- `schema-cube-audit`: 3/3 passed.
- `generated-surface`: 2/2 passed.
- `validate_spec_examples.py`: 467 examples passed as part of release-critical.
- `check_cube_hygiene_run_ledger.py`: passed with run-budget fields and regression coverage.

## Remaining next risks

The next schema-cube p0 targets are reader-use ledger retention, reader-use ledger retention expiry, and launch evidence. Launch evidence is operationally tempting because it sits near the cloudtainer timeout pain, but the two retention schemas are closer to the p0 split queue and likely smaller. A good next pass would split reader-use ledger retention and check whether retention-expiry/enforcement consumers are still tied to exact fixture literals in runtime schemas.

The project still needs a real FreeBSD host proof path for mdconfig/mount/fstyp/Capsicum behavior. Linux/cloudtainer checks can validate shape, join discipline, and regression semantics, but they should not be mistaken for native-kernel execution evidence.
