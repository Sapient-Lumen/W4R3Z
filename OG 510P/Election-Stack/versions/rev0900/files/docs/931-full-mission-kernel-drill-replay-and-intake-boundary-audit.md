# 931 — Full mission-kernel drill replay and intake boundary audit

**Track:** A — mission-kernel closeout and evidence intake.

v892 proved the operator evidence submitter against one work item, `LWC-001`. That was useful but still left an operational risk: the remaining six blocker families could drift or remain unexercised until a real jurisdiction tries to use them.

v893 adds a full non-production drill replay.

## Added surface

- `tools/mission_kernel_full_drill_replay.py`
- `scripts/check_mission_kernel_full_drill_replay.py`
- `artifacts/reports/mission-kernel-full-drill-replay-audit-rev0893.json`
- `artifacts/examples/example_county_2026_municipal_pilot/public-full-closeout-drill-replay.md`

The drill creates temporary records outside the governed archive for all seven live-closeout work items and all 28 minimum evidence classes. It then sends those records through the same submitter and intake functions that future operator paths use.

## What the replay proves

The release-gated replay proves that:

- all seven `LWC-*` rows can be represented as operator evidence submissions;
- all 28 required evidence classes can be digest-bound;
- no temporary local file path or `file_path` field leaks into the published audit;
- no governed synthetic-tree locator is accepted as source evidence;
- the intake validator classifies all rows as `DRILL_COMPLETE_NOT_LIVE_EVIDENCE`;
- the overall decision is `DRILL_COMPLETE_NOT_LIVE_READY`; and
- live evidence object count remains zero.

This is forward momentum because it tests the whole intake surface, not only a single happy-path row.

## Refactor performed

The full drill deliberately does not duplicate intake logic. It imports and uses:

- `mission_kernel_evidence_submitter.build_submission()`; and
- `mission_kernel_live_evidence_intake.evaluate_submission()`.

The new release check validates the generated audit rather than implementing a parallel submission evaluator. This keeps the drill from becoming a second definition of the intake contract.

## Why this remains no-go

A complete drill is only an end-to-end plumbing test. The records are created for a non-production replay and are not bundled as field evidence.

The live workqueue remains unclosed because real closure requires authorized local records, custody and ballot-accounting evidence, CVR/results export bytes, audit/recount/adjudication records, approved public notices/corrections, independent verifier transcripts, incident/remedy closeout records, and local retention/redaction/publication decisions.

## Maintainer commands

Regenerate the full drill replay report:

```bash
python3 tools/mission_kernel_full_drill_replay.py --write
```

Check the full drill replay boundary and refactor audit:

```bash
python3 scripts/check_mission_kernel_full_drill_replay.py
```

## Boundary

This is a non-production drill replay and intake-boundary audit. It is not live election evidence, not jurisdiction authorization, not certification, not outcome proof, not public-release approval, not current voter instruction, not source-byte completeness, and not legal advice.
