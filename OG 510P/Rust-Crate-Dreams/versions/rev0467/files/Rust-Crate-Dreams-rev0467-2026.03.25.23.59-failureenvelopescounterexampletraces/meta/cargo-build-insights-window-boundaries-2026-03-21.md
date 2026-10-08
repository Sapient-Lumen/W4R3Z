# Cargo build-insights comparison-window boundaries — 2026-03-21

This note keeps **P-0035 cargo-build-insights** from collapsing comparison-window choice into generic “series compatibility” or “regression severity” talk.

## The distinct truth

A historical build artifact must say **why these sessions were compared**.
That is not identical to:

- whether the sessions are compatible enough to compare at all,
- whether the imported data was exact or inferred,
- or whether the resulting slowdown is severe.

A worthy build-insights crate should therefore keep **comparison-window truth** explicit.

## Windows that must not be flattened together

1. **PR review window**
   - head commit versus last green base-branch session
   - tuned for “should this change land?”

2. **Release window**
   - release candidate versus previous release baseline
   - tuned for “did this shipped version regress?”

3. **Rolling branch trend window**
   - several sessions on one branch or one CI lane
   - tuned for “when did the slowdown begin?”

4. **Local experiment window**
   - a developer's before/after pair with narrower scope and weaker portability
   - tuned for “did my attempted fix help here?”

## Why this matters

The same pair of sessions can lead to different judgments depending on the window.
A PR head compared to last green `main` is not the same review object as a release-vs-release check, even if some imported metrics overlap.

If the archive forgets this, it will quietly produce fake certainty such as:

- “regressed from baseline” when the baseline was just the previous local build,
- “stable across releases” when the comparison actually stayed inside one branch,
- or “main is slower now” when the sessions should have been split by toolchain or workspace scope first.

## Receiver-facing artifacts to prefer

- `comparison-window.receipt.json` — audience, candidate set, selected baseline/head, exclusions, and window rationale
- `series-compatibility.report.json` — whether the chosen window remained comparable enough to stand
- `exactness.report.json` — what was imported versus inferred in the final judgment

## Anti-patterns

Do **not** let future revisions treat these as interchangeable:

- selected baseline/head pair,
- series compatibility,
- regression severity,
- and portable export posture.

They are adjacent truths, not one “regression result.”
