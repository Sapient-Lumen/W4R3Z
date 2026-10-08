# Frontier salience snapshot — 2026-03-21-144

This pass did **not** add another test runner, another XML exporter, or another flaky-test dashboard.
It deepened **P-0106 Test Run Artifact Standard Kit**.

## Why this frontier moved up

The current substrate now makes the missing layer much sharper:

- Cargo still builds libtest executables and forwards selection args, but Cargo also explicitly says its JSON output does **not** control arbitrary tool output;
- the Rust project goal for libtest JSON shows durable demand for machine-readable test results, but that still leaves stability and bundle semantics open;
- nextest now records full event streams, captured outputs, workspace metadata, retries, attempt IDs, and portable recordings,
- and nextest also explicitly warns that portable recordings can contain sensitive data that it does not redact;
- `libtest-mimic` proves custom harness diversity is real even when output looks like libtest.

That combination means “supports test output” is now too vague as a crate claim.
A worthy crate in this frontier should publish at least:

1. run-identity truth,
2. selection-basis truth,
3. attempt-topology truth,
4. bundle-sensitivity truth,
5. and one portable manifest that can honestly say what was imported or lost.

## Main conclusion

Promote **P-0106** sharply upward, but keep it narrow.
The sharper next move is not a universal runner.
It is a boring contract that keeps **run identity**, **selection basis**, **attempt topology**, and **share-safety** separately reviewable.

## Ranked near-term frontier from this pass

1. **P-0532 Async Runtime Assurance Profile Kit** — still strongest because runtime-family and qualification posture remain major ecosystem gaps.
2. **P-0106 Test Run Artifact Standard Kit** — strengthened because real recording substrate exists, but stable portable run-contract truth is still fragmented.
3. **P-0533 Error Surface Contract Kit** — still strong because identity/audience/remediation/sensitivity remain broadly under-specified.
4. **P-0076 Local-first Sync Kit** — still strong because durable state, presence, and history truth remain under-contracted.
5. **P-0521 Crate Resource Surface Pack Kit** — still strong because budget-topology truth remains a broad operational gap.

## Keep these boundaries sharp

- **P-0106** is run identity + selection basis + attempt topology + bundle sensitivity + portable manifest truth.
- raw test runners are separate substrate.
- JUnit/XML exports are separate interchange substrate.
- flake detectors and dashboards are separate analysis layers.
- support/incident bundles are adjacent but separate product lanes.

Do not let “recorded test run” flatten those into one fake crate.
