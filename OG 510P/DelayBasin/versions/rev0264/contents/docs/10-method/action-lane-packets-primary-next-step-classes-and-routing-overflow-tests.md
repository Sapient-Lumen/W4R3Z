# Action-lane packets, primary next-step classes, and routing overflow tests

This is the compact successor surface for `OQ-0113`.

DelayBasin already had a compact `action_lane` family, but one pressure kept recurring in durable ledgers:
later careful passes could still see the current state and the discharge prose and yet disagree about the **primary next step**.
Some rows are mainly waiting to be promoted.
Some are mainly waiting to be validated.
Some are mainly waiting for review, retirement, narrowing, replacement, or cooled adjudication.
When that routing truth stays ambient, a compact family exists on paper but not yet as an easy successor surface for future reuse.

The compact repair is:
**preserve one explicit action-lane packet that says the existing admitted `action_lane` family is already the right bounded place to keep primary next-step truth public, while leaving thresholds, evidence details, and branch logic in surrounding prose.**

This does **not** justify a route court, lane senate, queue-code constitution, or standing discharge router.
It only resolves the missing compact successor surface for a family DelayBasin already admitted.

## Practice / observation

DelayBasin's ledgers already distinguish state, discharge prose, and a compact `action_lane` token.
That was enough to stop many rows from collapsing into generic “needs work” folklore.
But a smaller gap remained:
- some future rereads still had to recover whether the item was mainly waiting for **promotion** or only **validation**;
- some had to recover whether the main next move was **rereview**, **retest**, **narrow**, **replace**, or **retire**;
- and some needed an explicit reminder that `await-adjudication` is a real routing class rather than merely fancier caution prose.

The archive therefore did not need a bigger family first.
It needed one compact packet that says the admitted family is already the right public place to preserve **primary next-step class**.

## External pressure from phased rollout and deployment-gate systems

Current rollout and deployment systems repeatedly separate current posture from next-step class.

1. Argo Rollouts documents explicit `promote`, `abort`, and `retry` commands around paused or failed rollouts. That pressures DelayBasin to keep next-step routing explicit rather than pretending state alone says what move is currently primary. ([`REF-0800`](../00-meta/bibliography.md), [`REF-0801`](../00-meta/bibliography.md))

2. GitHub deployment reviews document explicit `Approve and deploy` versus `Reject`, while GitHub Actions workflow-run APIs separately expose `re-run` and `cancel`. That pressures DelayBasin to keep approval, retry, and stop-like next steps public rather than reconstructing them from status prose alone. ([`REF-0802`](../00-meta/bibliography.md), [`REF-0803`](../00-meta/bibliography.md))

3. GitHub deployment controls also document jobs that sit in `Waiting` until approval and environment protection rules pass. That pressures DelayBasin to treat `await-adjudication` as a real routing class rather than ambient caution prose. ([`REF-0802`](../00-meta/bibliography.md))

4. AWS CodeDeploy documents `ContinueDeployment` with `READY_WAIT` and `TERMINATION_WAIT`, where traffic rerouting does not begin until the deployment is actually ready to continue. That pressures DelayBasin to preserve compact next-step truth even when current status and later route are not the same thing. ([`REF-0804`](../00-meta/bibliography.md))

5. LaunchDarkly release pipelines move flags through ordered phases and let each phase specify automation, approvals, and guarded rollouts. That pressures DelayBasin to keep one bounded next-step lane public without importing a larger release-governance court. ([`REF-0805`](../00-meta/bibliography.md), [`REF-0806`](../00-meta/bibliography.md))

## Working synthesis

> DelayBasin should preserve one compact **action-lane packet / primary next-step class** on durable queue and ledger items that already carry state plus discharge prose, and the admitted family should stay **`promote`**, **`replace`**, **`retest`**, **`rereview`**, **`retire`**, **`narrow`**, **`keep-compact`**, **`validate`**, and **`await-adjudication`**. Use the token only to name the primary next-step class. Keep thresholds, branch conditions, vetoes, and exact evidence in surrounding prose. Keep the family narrow. Extend only explicitly and fail closed on drift.

## Primary lane vs state vs gate class

This distinction is the heart of the successor surface.

- **state** says what posture the row is already in.
- **action lane** says the primary next move now licensed.
- **gate class** says what kind of future event would legitimately change the row.
- **discharge prose** says the concrete threshold, branch logic, or evidence condition that decides the row in detail.

A row can have state `open`, action lane `validate`, and gate class `concrete-evidence`.
A row can have state `cooling`, action lane `keep-compact`, and gate class `overflow`.
A row can have state `queued`, action lane `await-adjudication`, and gate class `scheduled-window`.

So the packet does not add a new court.
It only makes the already-admitted separation easier to reopen honestly.

## Countermodels / probes

1. **Discharge-prose-is-enough countermodel**
   - Maybe state plus prose already preserves routing honestly.
   - Probe: compare later rereads on rows with similar discharge prose and inspect whether operators still disagree about the real next step without the compact lane being foregrounded.

2. **Queue-code-inflation countermodel**
   - Any packet about primary routes may quietly promote a larger workflow controller.
   - Probe: keep the admitted family unchanged, preserve thresholds in prose, and quarantine any stronger route-governance story.

3. **Token-without-causal-force countermodel**
   - The packet may merely restate an existing field without improving future reuse.
   - Probe: inspect whether later passes more honestly preserve promote-vs-validate-vs-await-adjudication posture once the compact successor surface exists.

## Design consequences

- keep the controlled `action_lane` family unchanged in `WITNESS-VOCABULARY.json` for now;
- use the family only on governed durable queues and ledgers that already carry discharge prose;
- preserve one compact successor surface for the family so later passes can reopen routing truth directly;
- keep exact thresholds, evidence, and branch logic outside the token itself;
- and quarantine any stronger route court, lane senate, or next-step router board unless repeated overflow shows that one compact packet is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact packet is no longer enough — for example, if the archive honestly needs standing route arbitration across many candidate moves, durable queue-code governance, or a next-step router that cannot be expressed as one bounded family plus existing discharge prose.

Until then, prefer this compact successor surface over a route court, lane senate, or next-step router board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something slightly sharper than “what state is this row in?”
It is also preserving **what class of move is currently primary**.
That matters because later stateless passes can otherwise preserve the row and its evidence yet still misroute what sort of continuation the archive presently licenses.
