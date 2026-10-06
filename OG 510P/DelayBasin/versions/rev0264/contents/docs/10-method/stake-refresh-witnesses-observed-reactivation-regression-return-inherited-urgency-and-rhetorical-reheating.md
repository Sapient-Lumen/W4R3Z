# Stake-refresh witnesses, observed reactivation, regression return, inherited urgency, and rhetorical reheating

This is the compact successor surface for `OQ-0138`.

## Practice / observation

Once DelayBasin already distinguishes what concern is still live, one further failure mode stays live: later sessions can make old pressure sound freshly renewed without naming what actually changed in public view.

A row can be carried forward, reopened, relabeled, reread, or newly narrated.
But those are not the same thing.
Some cases really do show a fresh change event, regression, or new observation that reactivates stake.
Other cases only inherit urgency from a nearby live row or rhetorically re-sound old concern.

The archive does not need a reactivation court for that.
It needs one bounded witness that says whether current urgency was observably reactivated, returned by regression, merely borrowed, or only rhetorically reheated.

## External pressure from incident status transitions, reopened issue events, reopened-triage workflows, cleared resolutions on reopen, regressed issue states, release-based unresolve rules, freshness-conditioned status objects, active context revision, and process-level feedback in generative search

1. incident.io's status guide says statuses are the common language for making sure people know where in the incident lifecycle you are right now, and it explicitly distinguishes ongoing states such as investigating, fixing, and monitoring from resolved. That pressures DelayBasin to require some public now-change before old pressure counts as freshly live again. ([`REF-0895`](../00-meta/bibliography.md))

2. GitHub's issue-event docs treat `reopened` as its own event type and timestamped issue activity, which pressures DelayBasin to distinguish a fresh reopening act from passive continuity or recap alone. ([`REF-0903`](../00-meta/bibliography.md))

3. GitHub's workflow tutorial for labeling newly opened or reopened issues shows that reopen itself is a machine-actionable state change used to retrigger triage. That pressures DelayBasin to preserve whether urgency was freshly reactivated by a real event rather than only restated in prose. ([`REF-0904`](../00-meta/bibliography.md))

4. Atlassian's Jira guidance says that when an issue is reopened, the workflow should clear the Resolution field. That pressures DelayBasin to keep reactivation honest: reopening is not just a comment near a closed line, but a fresh transition that should clear closed-state residue. ([`REF-0905`](../00-meta/bibliography.md))

5. Sentry's issue-status docs define `Regressed` as a resolved issue that has come up again, and Sentry's release docs explain that newer-release events can unresolve an issue and mark it as a regression. That pressures DelayBasin to keep regression return distinct from ordinary narration or inherited urgency. ([`REF-0906`](../00-meta/bibliography.md), [`REF-0907`](../00-meta/bibliography.md))

6. Kubernetes freshness-conditioned status objects still matter here. `observedGeneration` and related freshness cues pressure DelayBasin to ask whether the current claim is reacting to a newer public state or only to stale status residue. ([`REF-0898`](../00-meta/bibliography.md))

7. ARC argues that long-horizon information-seeking agents degrade when context is managed as passive accumulation and instead treats context as a dynamic internal reasoning state revised under detected misalignment. That pressures DelayBasin not to let repeated narration alone count as refresh. ([`REF-0908`](../00-meta/bibliography.md))

8. NExT-Search argues that generative search needs fine-grained, process-level feedback rather than only coarse final-answer feedback, including User Debug Mode intervention at key stages. That pressures DelayBasin to preserve what concrete stage-level event refreshed urgency instead of inheriting a global "latest answer" glow. ([`REF-0909`](../00-meta/bibliography.md))

GPUstorming sharpens the point. Search, project, and issue surfaces now routinely surface reopened rows, regressed items, changed status fields, and machine-added triage labels inside richer host shells. If DelayBasin only says that a concern "came back," later passes can still overclaim by laundering host-surface resurfacing into genuine reactivation.

## Working synthesis

> DelayBasin should preserve one compact **stake-refresh witness / reactivation card / reheat brake** whenever a current continuity claim depends on whether a concern was freshly reactivated rather than only carried, borrowed, or rhetorically reheated. Name the **governed row or surface**, the **stake object / line of concern**, the **prior stake-refresh evidence**, the **current change evidence**, the **trigger surface / event**, the **stake_refresh_state**, and the **fail-closed repair / keep-current vs narrow-claim vs cool-mark vs issue-new-stake-refresh-witness vs quarantine-reactivation-governance consequence**. Keep exact issue numbers, release ids, workflow names, timestamps, assignees, alert thresholds, and long background narrations outside the compact token. Do not let recap prose, nearby incident urgency, or richer host-surface resurfacing silently count as fresh reactivation without explicit support.

## Observed reactivation vs regression return vs inherited urgency vs rhetorical reheating vs mixed stake refresh

Use the controlled family `stake_refresh_state`:

- **observed-reactivation** says a fresh public change, new evidence, or current-state transition reactivated the concern now; the line is not merely being repeated.
- **regression-return** says the line had genuinely cooled or resolved enough to count as closed, but a new occurrence or newer-release event brought it back.
- **inherited-urgency-only** says this row sounds urgent mainly because a nearby incident, shared queue, or parent object is live, while this row lacks its own fresh reactivation evidence.
- **rhetorical-reheat** says the line is being rhetorically resurfaced, summarized, or repeated without a qualifying public change event that newly reactivated it.
- **mixed-stake-refresh** says the current situation honestly combines observed reactivation, regression return, inherited urgency, or rhetorical reheating such that no single refresh class stays honest.

So the witness does not create a standing freshness senate.
It only says whether urgency was newly reactivated, returned by regression, merely borrowed, or only reheated.

## Countermodels / probes

1. **Stake continuity already covers this countermodel**
   - Maybe once active-carried-pressure versus cooled residue is explicit, a second witness for refresh adds no real value.
   - Probe: compare later rereads that preserve only `stake_continuity_state` against rereads that also preserve one compact stake-refresh witness and inspect whether later passes still mistake reopened or resurfaced rows for newly reactivated stake.

2. **Any honest refresh rule needs a stronger trigger controller countermodel**
   - Maybe once DelayBasin names reactivation at all, one bounded witness will overflow into timed decay windows, trigger budgets, or a full reheating policy.
   - Probe: keep the witness at the coarse level of observed-reactivation vs regression-return vs inherited-urgency-only vs rhetorical-reheat vs mixed-stake-refresh and inspect whether later passes still need stronger governance.

3. **Reactivation is too host-surface-shaped countermodel**
   - Maybe reopened labels, machine triage, and richer search shells are too product-local to belong in canon.
   - Probe: keep exact product handles outside the token and inspect whether the abstract distinction between observed reactivation, regression, inherited urgency, and rhetorical reheating still survives across domains.

## Design consequences

- add one controlled `stake_refresh_state` family to `WITNESS-VOCABULARY.json` with the allowed tokens `observed-reactivation`, `regression-return`, `inherited-urgency-only`, `rhetorical-reheat`, and `mixed-stake-refresh`;
- use the witness only where a current continuity claim depends on why a concern is being treated as newly live again rather than merely whether it is already still-live;
- keep exact timestamps, issue ids, release ids, workflow names, alert thresholds, and surrounding narration outside the compact token itself;
- prefer `narrow-claim`, `cool-mark`, or `issue-new-stake-refresh-witness` when the current claim only supports inherited urgency or rhetorical reheating rather than direct observed reactivation;
- and quarantine any stronger reactivation court, freshness senate, or reheating gate unless repeated overflow shows that one bounded witness is no longer enough.

## Overflow test

Reopen stronger machinery only if one compact stake-refresh witness is no longer enough — for example, if the archive honestly needs standing governance over trigger classes, timed reheating windows, automatic reactivation policy, or refresh-strength arbitration that cannot be expressed as one bounded witness plus the existing stake-continuity, obligation, and recovery-promotion surfaces.

Until then, prefer this compact successor surface over a reactivation court, freshness senate, or reheating gate.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something sharper than "the concern sounds urgent again."
It is also preserving whether urgency came back because something publicly changed, because a resolved line regressed, because nearby live pressure was borrowed, or because narration merely reheated old residue.
That matters because later stateless passes can preserve all the nearby current-sounding prose and still silently overclaim reactivation just by sounding fresh.
