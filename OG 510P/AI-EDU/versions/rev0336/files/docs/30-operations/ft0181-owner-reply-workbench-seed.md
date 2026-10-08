# FT-0181 owner-reply workbench seed

Rev0295 keeps the seed bounded, places it behind `owner-returned-reply-work` for the normal path, and routes valid seeds through `owner-workbench-review-brief` before any human-entered review record. Rev0289 added the provenance split: a seed may source either an active contact-status-gated intake bundle or a post-readout context-receipt-gated intake bundle, but never both and never neither. It must route to a local review brief and then to [`ft0181-workbench-review-record.md`](ft0181-workbench-review-record.md) before the first-packet decision board, one workbench-sourced re-ask, or a block/trim outcome.

Normal operators should reach this through `make owner-returned-reply-work`. Use the direct seed command only after a real returned owner CSV has already produced a local `PROCEED-STAGED` intake bundle and the compressed helper cannot be used.

```bash
make owner-reply-workbench-seed BUNDLE=scratch/field/ft0181/owner-reply-intakes/<bundle-dir>
```

Optional explicit output:

```bash
make owner-reply-workbench-seed BUNDLE=scratch/field/ft0181/owner-reply-intakes/<bundle-dir> OUT=scratch/field/ft0181/owner-reply-workbench-seeds/<seed-dir>
```

The seed tool reads the intake bundle manifest, revalidates the preserved `source_contact_status.reference`, verifies the receipt, triage, and proceed-staged note hashes, and writes a single local `workbench-seed.json`. It refuses non-`PROCEED-STAGED` bundles, SRC0 smoke bundles, stale pre-rev0251 self-hash manifests, bundles without a revalidatable active source contact clock, and output into root, `docs/`, `examples/`, `fixtures/`, `schemas/`, `templates/`, or `tools/`.

## Boundary

The workbench seed is not an evidence acceptance step. It records hashes, a revalidated source-contact-status summary, the required next surface, and a `NOT_ACCEPTED` state only. It does not copy owner answers from the CSV, receipt, triage JSON, or proceed-staged note, and it does not copy contact details. It does not upgrade source truth, close `FT-0181`, or support public claims.

The next human step is still [`ft0181-owner-packet-workbench.md`](ft0181-owner-packet-workbench.md), but the next recorded local artifact is now a scratch-local review brief, followed by [`ft0181-workbench-review-record.md`](ft0181-workbench-review-record.md) only after human review. Copy only minimized surviving row answers from the proceed-staged note into the human workbench after confirming the source is a real owner reply and still satisfies the local redaction, source, date-range, action-boundary, fallback, stop-condition, and public-claim ceilings. The recorded review stores counts and route labels only.

## Required gates after seed

| Gate | Required posture |
|---|---|
| source | real owner-returned CSV, not SRC0/SRC1 rehearsal content |
| acceptance | `NOT_ACCEPTED` until custody and downstream gates pass |
| copied content | none in the seed or review; review stores counts, hashes, route labels, and flags only |
| workbench copy | minimized surviving row answers only in the human workbench; not in the review JSON |
| review brief | `make owner-workbench-review-brief SEED=scratch/.../workbench-seed.json` before the human-entered review command |
| review record | `make owner-workbench-review ... CONFIRM=human-reviewed-minimized-workbench-record` after a human chooses one route and counts fields |
| public claim | process-only or weaker, no learning/safety/access/workload/compliance/scale/effectiveness claim |
| closure | `FT-0181` remains live |

## Rev0295 compressed path

The router emits `owner-returned-reply-work` when a real returned CSV is provided with a valid source contact clock or post-readout context receipt. That helper runs intake, calls this seed tool only when the bundle is `PROCEED-STAGED`, and then prepares a scratch-local workbench review brief. Non-proceed outcomes stop at the intake note.

## Rev0289 provenance rule

The seed must preserve exactly one provenance flag: `source_contact_status_revalidated: true` or `source_post_readout_context_receipt_revalidated: true`. If the referenced scratch artifact is missing, malformed, mismatched against the source CSV hash, or mixed with another provenance source, the seed blocks. This keeps an old or hand-edited intake bundle from becoming the workbench handoff.

## Rev0295 review-brief rule

After a seed exists, rerun the router. It emits `make owner-workbench-review-brief ...` unless a valid review brief already exists. After the brief exists, the router emits `make owner-workbench-review ...` with the source seed and confirmation token. A `PROCEED-DECISION-BOARD` review requires `SRC2` or stronger, at least two reviewer roles, at least one surviving field, at least one decision-changing field, no pending re-ask fields, and no raw/protected/security/public-claim-upgrade flags. A `REASK-OWNER` review can source one bounded clarification clock. Blocks and trims remain local summaries.

FT-0181 remains live after the seed and after the review.
