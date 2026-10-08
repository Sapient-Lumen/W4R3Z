# Meta: Pilot Scorecard Protocol (rev0433)

## Purpose
Use this protocol when the repo is evaluating whether a seam-specific pilot actually proved itself.
This protocol is **not** the same as:
- candidate triage before a proposal enters the canon;
- broad ranking of seams;
- or stage ordering across the portfolio.

It exists for the narrower question:
> what minimum evidence should a serious pilot leave behind so the archive can graduate, deepen, fold, delay, or kill it honestly?

Read with:
- `design/portfolio-pilot-evaluation-2026Q1.md`
- `design/portfolio-proving-grounds-2026Q1.md`
- `design/portfolio-selection-rubric-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`

## Required scorecard fields
Every serious pilot card should include:

1. **Identity**
   - seam name
   - pilot title
   - ranking class
   - revision/date
   - steward or owner class

2. **Lane statement**
   - exact lane exercised
   - target user/operator
   - why the lane is representative
   - baseline workflow / pain before the pilot

3. **Scenario binding**
   - proving-ground scenario ID(s) exercised
   - skipped expected scenario ID(s) and why
   - prohibited conclusions after those skips

4. **Imports and assumptions**
   - official or maintainer-authored substrate imported
   - versions / freshness caveats
   - manual inputs or simulated data
   - assumptions held constant

5. **Artifacts emitted**
   - canonical pack(s)
   - brief / receipt / attachment slices
   - validators or schema/lint checks
   - unsupported / stale / fallback states

6. **Decisions exercised**
   - downstream decision(s) improved
   - who consumed them
   - what action actually changed

7. **Outcome deltas**
   - time / latency / loop reduction where meaningful
   - correctness or false-positive / false-negative posture where meaningful
   - auditability / operator-confidence improvements where numerical metrics are weak
   - what did **not** improve

8. **Steward cost**
   - renewal sources and cadence
   - compatibility burden
   - brittle dependencies or rot risks
   - expected maintainer load

9. **Verdict**
   - `graduate`
   - `deepen`
   - `fold`
   - `delay`
   - `kill`

10. **Why this verdict**
   - one short paragraph tying the verdict to lane proof, artifact proof, decision proof, and steward proof.

## Default interpretation
- Prefer **graduate** only when the pilot proved real lane value, emitted honest artifacts, improved a decision, and has a believable steward story.
- Prefer **deepen** when the seam still looks right but the lane, proof, or artifacts are too weak.
- Prefer **fold** when the pilot found something useful that belongs under an existing seam.
- Prefer **delay** when substrate or maintainer reality is not ready.
- Prefer **kill** when the pilot adds more upkeep than strategic leverage.

## Minimum anti-cheating rules
- A screenshot, dashboard, or polished demo is **not** a scorecard.
- “It felt better” is **not** enough without lane context.
- Silent scenario skips should count against broad claims.
- “Someone could use this later” is **not** consumer proof.
- “We can maintain it somehow” is **not** a steward story.
- Silence about unsupported/stale/manual cases should count against graduation.
