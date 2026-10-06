# Priority-0 frozen-response / score-sheet split — 2026-06-16

## Why this revision exists

`rev0371` correctly stopped treating further gate-hardening as external replay progress, but it still carried a practical collision in the clean replay lane: the response template contained a `scorer_stage.manual_metric_scores` slot inside the same response file that the custody record is supposed to freeze by SHA256.

That creates a bad fork:

- if the scorer adds manual scores into the response after freeze, the response hash changes and the custody record no longer names the scored file;
- if the manual scores are already in the response before freeze, scorer-only material has effectively entered the responder artifact too early;
- if the response remains hash-stable and unscored, the compact gate cannot confirm, narrow, or reverse.

So the riskiest work was not another custody rule. It was separating the frozen responder artifact from the post-response scoring artifact.

## Change made

`rev0372` introduces a score-separated external replay workbench:

- the responder bundle contains only the responder packet, response template, and responder README;
- the frozen response template no longer carries manual metric scores;
- the submission kit carries the responder bundle plus custody template/readme;
- a separate scorer kit carries the scorer intake, score-sheet template, scoring tool, and minimal scoring libraries;
- the scorer tool rejects strict clean scoring if manual scores are embedded in the frozen response;
- strict clean scoring can use `--score-sheet` to read manual metric scores from a separate score sheet whose `response_file_sha256` matches the frozen response and whose custody-record hash matches the completed custody record.

This is a workbench repair, not external replay evidence. No clean external/operator-independent response exists yet.

## Audit / refactor

The handoff bundle builder lane was refactored to use a shared deterministic ZIP helper for generic bundles, not only responder bundles. That lets the current responder bundle, submission kit, and scorer kit share the same deterministic writer while keeping answer-key material out of the responder path.

Historical checker pressure was also narrowed. The rev0371 custody-timeline checker now preserves the old fixture as evidence without forcing the rev0371 scorer to remain the live `auto:frontier` scorer. The rev0369 and rev0370 historical checkers no longer force themselves into every future current additions list merely because they were once refactored.

## Current score-separated command

After a clean responder has completed and a distinct custodian has frozen the response and evidence record, the scorer should use the scorer kit and run:

```bash
python -S tools/score_priority_zero_external_replay_response.py \
  --scorer-intake assays/priority-zero-score-separated-external-replay-scorer-intake-2026-06-16.json \
  --evidence-record <completed-custody-record.json> \
  --score-sheet <completed-score-sheet.json> \
  --summary-out <score-summary.json> \
  <frozen-response.json>
```

The frozen response must not be edited to add scores after it is frozen.

## Stopgate

`OQ-0263` is resolved only as: the prior clean-response decision path was internally inconsistent because it placed scorer scores inside the frozen response artifact. `OQ-0264` carries the actual external replay collection and scoring work using the score-separated submission kit and scorer kit.

Forbidden shortcuts remain unchanged: bundle existence, custody template existence, score-sheet template existence, negative canaries, scorer-kit existence, same-session dry-runs, and further gate repairs do not count as clean external replay success.
