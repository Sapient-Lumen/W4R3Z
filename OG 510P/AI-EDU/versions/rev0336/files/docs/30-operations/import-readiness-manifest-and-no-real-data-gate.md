# Import-readiness manifest and no-real-data gate

`FT-0181` should not close merely because the archive has realistic examples, import maps, redaction
profiles, and validators. This surface adds a preflight record that proves the archive is ready to
receive real pilot records while still blocking the false claim that real records have already been
imported.

The rule is simple: **readiness is not import**. A readiness manifest can say the lane, owners,
exclusions, source map, and decision-delta questions are prepared. It cannot count synthetic records
or operator-drafted templates as field evidence.

## Readiness states

| Code | Meaning | FT-0181 posture |
|---|---|---|
| `IR0` | Synthetic or realistic examples only | Keep `FT-0181` queued. |
| `IR1` | Import map exists and example service records pass lint | Keep queued; examples are not evidence. |
| `IR2` | Source inventory, owner, protected-exclusion, and security-exclusion plan are named | Keep queued unless an `SRC2+` source is staged. |
| `IR3` | De-identification and minimization plan is verified by the record owner | Keep queued unless a candidate `SRC2+` record is normalized. |
| `IR4` | Candidate service record is normalized from an `SRC2+` source | Review; do not close until decision delta is written. |
| `IR5` | Decision-delta log is complete and schema changes are justified | May close if public-summary rendering and owner verification pass. |
| `IR6` | Redacted public summaries, adapters, expiry clocks, and rollback fields pass review | May close and cite the imported record set. |
| `IRX` | Protected, conflicting, unsafe, or legally constrained source | Quarantine; do not normalize into public examples. |

`IR4-IR6` require a source truth class of `SRC2`, `SRC3`, or `SRC4`. `IR0-IR3` can improve the lane,
but they cannot close `FT-0181`.

## Manifest contract

A readiness manifest lives in `examples/import-readiness/` and declares:

- the related followthrough item, normally `FT-0181`;
- current readiness state and source truth class;
- whether closure is permitted;
- candidate service-record IDs and import-map IDs;
- source inventory and data-dictionary requirements still missing;
- protected and security exclusions;
- required checks before import and acceptance;
- decision-delta requirements;
- stop conditions;
- last reviewed date.

`tools/check_import_readiness.py` fails if a manifest with `SRC0` or `SRC1` permits closure. It also
fails if `FT-0181` is marked done without at least one readiness manifest that permits closure.

## Closure rule for FT-0181

Close `FT-0181` only when all of these are true:

1. At least one manifest has `closure_permitted: true`.
2. The manifest source truth class is `SRC2`, `SRC3`, or `SRC4`.
3. At least one normalized service record came from a real pilot export or local record set.
4. A source data dictionary gives field meaning, sensitivity, owner review, and import action.
5. A real-import acceptance packet passes with no unresolved closure-critical block.
6. A decision-delta note says which fields changed the decision, which fields were trimmed, and
   whether the schema needs revision.
7. Public-summary rendering passes for every referenced audience profile.
8. A first-packet decision board, lifecycle decision, and real-import closeout board record explain whether the service stays sandbox, pilot, recurring, watch, deprecate, archive-only, or quarantine.
9. Protected facts, raw learner traces, and security exploit details remain outside the public
   archive.

Until then, `FT-0181` stays live even if every readiness check passes.

## No-real-data posture

The shipped manifest `IMP-READY-FT0181-NO-REAL-DATA` intentionally has `closure_permitted: false`.
Rev0233 keeps it at `IR2`: the first-packet lane, owner-role path, exclusions, workbench, decision board, dictionary, and map are prepared, but the archive still has no `SRC2+` pilot export in hand.

This prevents three subtle errors:

- treating realistic examples as implementation evidence;
- treating an import map as proof that an import occurred;
- letting public summaries imply that a service has real-world learning, access, workload, or safety
  evidence when it only has a schema-backed example.

## Current archive bet

A blocked honest import is better than a completed fake one. The archive should be able to say:
“we can import the first real record safely, and we have not done so yet.”

See [`real-pilot-record-import-and-normalization-workflow.md`](real-pilot-record-import-and-normalization-workflow.md),
[`pilot-source-data-dictionary-template.md`](pilot-source-data-dictionary-template.md),
[`real-import-acceptance-tests-and-reviewer-calibration.md`](real-import-acceptance-tests-and-reviewer-calibration.md),
[`minimum-real-data-request-packet.md`](minimum-real-data-request-packet.md),
[`ft0181-owner-packet-workbench.md`](ft0181-owner-packet-workbench.md),
[`ft0181-first-packet-decision-board.md`](ft0181-first-packet-decision-board.md),
[`import-negative-fixtures-and-failure-mode-catalog.md`](import-negative-fixtures-and-failure-mode-catalog.md),
[`decision-delta-log-template-and-field-pruning-rules.md`](decision-delta-log-template-and-field-pruning-rules.md),
[`public-summary-render-smoke-tests.md`](public-summary-render-smoke-tests.md),
[`operator-handoff-and-maintainer-runbook.md`](operator-handoff-and-maintainer-runbook.md),
[`service-lifecycle-deprecation-and-archive-exit-rules.md`](service-lifecycle-deprecation-and-archive-exit-rules.md),
[`real-import-closeout-board-and-decision-minutes.md`](real-import-closeout-board-and-decision-minutes.md),
and `AS-0226`, `AS-0236`, `AS-0237`, and `AS-0239`.
