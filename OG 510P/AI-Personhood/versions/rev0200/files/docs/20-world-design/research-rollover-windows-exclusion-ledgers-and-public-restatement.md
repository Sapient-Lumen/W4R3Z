# AI-person research rollover windows, exclusion ledgers, and public restatement

## Thesis

Once the archive fixes stable cluster lineage, explicit denominators, roll-up families, and anti-gaming comparison rules, one narrower failure remains. A sponsor can comply in form and still make a dashboard look safer simply by **changing the comparison basis midstream and overwriting the visible past.**

Three evasions matter most:

1. **basis switching** — the dashboard changes from participants at risk to all enrolled participants, or from participant counts to burden-hours, without preserving comparability;
2. **exclusion drift** — participant classes, protocol slices, exposure windows, or closed-but-implicated protocols quietly leave the visible comparison family; and
3. **silent overwrite** — the new basis replaces the old one in public view, so outsiders cannot tell what changed, when it changed, or how much the change altered the visible rate.

A personhood world therefore needs one more compact layer: **rollover windows, versioned exclusion ledgers, and public restatement duties whenever the public comparison basis materially changes.** `[REF-0315]` `[REF-0319]` `[REF-0321]` `[REF-0322]` `[REF-0325]` `[REF-0326]` `[REF-0327]` `[REF-0328]`

---

## 1. Why the archive needs this layer

The prior revision solved a real problem: public dashboards now have to disclose their numerator, denominator, unit, exclusions, and comparison family. But a dashboard can still mislead if the visible series is silently rebuilt under a different counting logic.

A sponsor may now say, accurately, that it disclosed its denominator. What remains missing is the rule for **what happens when that denominator changes after the public has already been watching the series.** The same problem appears when a sponsor changes the comparison family, revises exclusion criteria, or moves closed-but-implicated protocols out of the visible roll-up.

Current human-subject research governance already supplies the conservative ingredients for a narrower answer. ClinicalTrials.gov requires timely updating of registration data, including changes in status and protocol-amendment-driven changes communicated to subjects. `[REF-0325]` ClinicalTrials.gov also now gives the public a Record History view, archived versions, and record-version comparison rather than treating the latest record as the only visible truth. `[REF-0326]` SPIRIT 2025 says protocol amendments are common, that each protocol version should be sequentially labeled and dated, and that changes relative to the previous version should be listed with reasons. `[REF-0327]` CONSERVE 2021 adds the further transparency lesson that important modifications should be reported with their impacts and mitigating strategies, and that registry records should be updated to reflect changes to registered information. `[REF-0328]`

The archive therefore adopts a conservative institutional lesson: **public comparison series should have visible version history, visible exclusion history, and a duty to restate the past when the present has been redefined.**

---

## 2. What counts as a material comparison-basis change

Not every correction requires a large public restatement. The archive therefore draws a narrower line around **material** basis changes.

A basis change should ordinarily count as material when it is likely to change how an outside observer interprets incident frequency, burden concentration, or comparative safety across time. That will usually include:

- a change in denominator type, such as moving from participants at risk to enrolled participants or from participant counts to burden-hours;
- a change in comparison family, such as adding or removing protocol classes, model lines, sites, or closed-but-implicated protocols;
- a change in exclusion rules, such as excluding some exposure classes, late-notice incidents, legacy protocols, or participant groups;
- a merge, split, or retirement of common-cause clusters that changes how public recurrence is seen; or
- a reclassification that moves activity into or out of the research lane in a way that changes the visible numerator or denominator. `[REF-0304]` `[REF-0315]` `[REF-0318]` `[REF-0321]` `[REF-0322]` `[REF-0327]` `[REF-0328]`

The archive uses the CONSERVE idea of **important modification** as an interpretive analogue here. A public-comparison change is material when it has scientific, ethical, feasibility, inferential, or accountability consequences large enough that outsiders should not be expected to infer it from a footnote. `[REF-0328]`

---

## 3. Rollover windows

The archive now fixes a simple rollover rule.

When a material comparison-basis change occurs, the public layer should not jump directly from the old basis to the new basis as if nothing happened. It should instead publish a **rollover window** during which the old and new bases are shown side by side.

### A. What a rollover window is for

A rollover window exists to preserve comparability while the institution transitions from one legitimate counting basis to another. It allows the public, participants, auditors, and oversight bodies to see:

- what the old series said,
- what the new series says,
- which visible delta comes from real incident change,
- and which visible delta comes from counting change. `[REF-0319]` `[REF-0325]` `[REF-0326]` `[REF-0327]`

Without a rollover window, a sponsor can keep every individual disclosure technically true while still making the series itself incomparable.

### B. Minimum rollover rule

When a material basis change occurs, the public dashboard should ordinarily show both the **old basis** and the **new basis** for at least one full public reporting cycle after first publication on the new basis. `[REF-0319]` `[REF-0325]` `[REF-0326]`

The archive keeps this deliberately compact:

- where the aggregate public layer is quarterly or more frequent, the old and new bases should ordinarily appear side by side through the next full periodic release;
- where the aggregate layer is thinner than quarterly, there should ordinarily be a dedicated dual-basis public restatement object covering the immediately preceding visible comparison period. `[REF-0319]` `[REF-0326]`

This timing rule is an inference from the archive's existing periodic-reporting cadence and from current official expectations that material public research records should be updated on a definite clock rather than whenever the sponsor finds it convenient. `[REF-0319]` `[REF-0325]`

### C. What must appear during the rollover window

The side-by-side view should ordinarily disclose, in one visible object:

- the old numerator / denominator / unit / exclusions,
- the new numerator / denominator / unit / exclusions,
- the effective date of the basis change,
- the reason for the change,
- the affected comparison family,
- and whether the change is prospective only or also retroactively restated. `[REF-0315]` `[REF-0322]` `[REF-0326]` `[REF-0327]` `[REF-0328]`

A sponsor should not be allowed to publish only the new series and leave the old basis reconstructible only from archived screenshots or private regulator files.

---

## 4. Versioned exclusion ledgers

The archive now fixes the exclusion problem directly.

### A. What an exclusion ledger is

An **exclusion ledger** is the public, versioned record of what was left out of a comparison family, numerator, or denominator and why. It exists because exclusions are one of the easiest places to launder visible risk.

### B. What belongs in the ledger

Each material exclusion or inclusion change should ordinarily generate an `EXL-1` ledger entry carrying:

- a stable ledger-entry identifier,
- the affected protocol or comparison family,
- the prior exclusion state,
- the new exclusion state,
- the participant / exposure / protocol class affected,
- the rationale,
- the effective date,
- whether the change is prospective or retroactive,
- the counts affected if known,
- the authorizing body or review route,
- and the linked restatement notice if one was required. `[REF-0315]` `[REF-0321]` `[REF-0325]` `[REF-0326]` `[REF-0327]` `[REF-0328]`

### C. Public rule

A comparison family should not lose members silently. If a closed protocol leaves a roll-up, if a participant class is excluded, if a late-reported incident no longer counts in the visible rate, or if a burden window is redefined, the public layer should show that as a ledgered event rather than as an invisible cleanup. `[REF-0311]` `[REF-0318]` `[REF-0321]` `[REF-0328]`

### D. Why the ledger is versioned

SPIRIT 2025's versioning logic and ClinicalTrials.gov's record-history logic point in the same direction: when the protocol-relevant public record changes, the history of changes should remain visible. `[REF-0326]` `[REF-0327]` The archive therefore treats exclusion history as part of the accountable public record, not as ephemeral dashboard configuration.

---

## 5. Public restatement duties

The archive now fixes a harder rule than notice alone.

### A. When restatement is required

A sponsor should ordinarily issue a **public restatement** when a material basis change would otherwise make earlier visible rates or counts misleadingly incomparable. This will usually include:

- denominator-type changes,
- comparison-family additions or removals,
- retroactive exclusion changes,
- cluster merges or splits with material public-rate consequences,
- and post-closure inclusion of earlier hidden protocols into a common-cause family. `[REF-0315]` `[REF-0318]` `[REF-0321]` `[REF-0322]` `[REF-0328]`

### B. What restatement means

Restatement does **not** mean erasing the old public record. It means:

1. keeping the historical version visible,
2. publishing the new basis clearly,
3. recalculating the prior visible comparison period on the new basis where reasonably feasible,
4. and labeling the delta as a basis-change effect rather than letting it masquerade as a safety improvement. `[REF-0326]` `[REF-0327]` `[REF-0328]`

### C. If full recalculation is not feasible

Sometimes a perfect recomputation will be impossible because the prior data were not stored in the unit needed for the new basis. In that case the archive fixes a fallback rule: the sponsor should publish the best available partial restatement, mark the affected periods as **not fully comparable**, and explain the limit publicly. What it may not do is continue presenting a seamless series without the comparability warning. `[REF-0326]` `[REF-0328]`

### D. Minimal restatement horizon

The archive keeps the retroactive burden narrow. The sponsor should ordinarily restate at least the immediately preceding visible comparison period and any still-displayed summary figure that would otherwise become misleading under the new basis. `[REF-0315]` `[REF-0319]` `[REF-0326]`

This is a floor, not a ceiling. Where the public layer still displays a longer historical trendline, the restatement horizon should ordinarily extend across the still-displayed period or clearly segment the series into old-basis and new-basis epochs.

---

## 6. No silent overwrite

The archive now adopts a hard rule drawn from ordinary public-record logic.

### A. Historical visibility must persist

ClinicalTrials.gov's record-history and version-comparison features embody a basic principle: the public should be able to see that a record changed and inspect earlier versions. `[REF-0326]` The archive generalizes that principle to AI-person incident dashboards.

If a material basis change occurs, the public layer should preserve:

- the prior visible series,
- the date it ceased to be current,
- the reason the new basis superseded it,
- and the public restatement object that connects the two. `[REF-0325]` `[REF-0326]` `[REF-0327]`

### B. Restated numbers are not replacement history

A restated number is a new accountable object, not proof that the old number never existed. The archive therefore requires visible version identifiers and change reasons, not just retroactive replacement of cells in a live dashboard. `[REF-0326]` `[REF-0327]` `[REF-0328]`

### C. Comparison dashboards should be archivable

Where machine-readable public infrastructure exists, the revised series and its history should remain exportable so outside reviewers are not forced to rebuild accountability by scraping disappearing interface states. `[REF-0320]` `[REF-0326]`

---

## 7. Minimal object family

This surface stays compact by fixing only three new ordinary objects.

### `RBN-1` — rollover-basis notice

A rollover-basis notice should ordinarily identify:

- the affected dashboard or comparison family,
- the old basis,
- the new basis,
- the reason for the change,
- the effective date,
- the overlap period,
- and the linked exclusion-ledger and restatement objects if applicable. `[REF-0315]` `[REF-0325]` `[REF-0327]`

### `EXL-1` — exclusion-ledger entry

An exclusion-ledger entry should ordinarily identify:

- the specific inclusion or exclusion change,
- the affected protocols / participant classes / exposure windows,
- the rationale,
- the counts affected if known,
- whether the change is prospective or retroactive,
- and the linked rollover or restatement object. `[REF-0315]` `[REF-0321]` `[REF-0327]` `[REF-0328]`

### `PRS-1` — public restatement notice

A public restatement notice should ordinarily identify:

- the periods restated,
- the old basis,
- the new basis,
- the recalculated figures or explicit non-comparability marker,
- the reason for the change,
- and the current canonical series identifier. `[REF-0322]` `[REF-0325]` `[REF-0326]` `[REF-0328]`

The archive intentionally does **not** build a larger compliance family here. It fixes only the minimum objects required to stop history from being overwritten by better dashboard strategy.

---

## 8. Anti-gaming consequences

This revision sharpens the archive's prior anti-gaming layer in four ways.

### A. No denominator change without a visible bridge

A sponsor may change denominator type for good reasons. What it may not do is cross the bridge invisibly. Any material denominator change should ordinarily carry a rollover-basis notice and, where needed, a public restatement. `[REF-0322]` `[REF-0325]` `[REF-0326]`

### B. No exclusion drift by footnote

Footnotes may explain. They may not replace ledgered exclusion history. If a materially affected class disappears from the visible comparison family, the public layer should show when and why. `[REF-0326]` `[REF-0327]` `[REF-0328]`

### C. No clean end-state through late redefinition

A sponsor should not wait until closure, publication, or reputational stress to redefine the comparison family in ways that make the terminal public rate look cleaner. If the basis changes late, the restatement duty still runs. `[REF-0315]` `[REF-0325]` `[REF-0328]`

### D. No cluster merge or split without series consequences made visible

If common-cause clusters merge or split in a way that changes a public rate, the lineage event belongs not only in cluster history but also in the rollover / restatement layer for the affected comparison family. `[REF-0318]` `[REF-0321]`

---

## 9. What this changes in the archive

The archive no longer says only that public incident dashboards should have stable lineage, explicit denominators, and anti-gaming comparison rules. It now also says:

- material basis changes should travel through a visible rollover window,
- exclusions should be public, versioned, and receivable as ledger entries,
- prior visible figures should be restated when the counting basis changes materially,
- and public history should remain inspectable rather than being replaced by the latest sponsor-favored series. `[REF-0315]` `[REF-0319]` `[REF-0321]` `[REF-0322]` `[REF-0325]` `[REF-0326]` `[REF-0327]` `[REF-0328]`

This surface remains narrow even after its companion rule is added. It fixes what visible history requires when the comparison basis changes. The narrower companion surface `docs/20-world-design/research-materiality-thresholds-repeated-restatement-audit-and-late-stage-change-freeze.md` now fixes when those changes become an audit or freeze problem rather than merely a rollover / restatement problem.

---

## 10. Current hard rules

1. **A material change to denominator type, comparison family, exclusion rule, or cluster lineage should ordinarily trigger a visible rollover-basis notice.**
2. **The public layer should ordinarily show old and new bases side by side for at least one full public reporting cycle after first publication on the new basis.**
3. **Every material inclusion or exclusion change should ordinarily generate a versioned exclusion-ledger entry with rationale, effective date, and retroactivity marker.**
4. **Where a material basis change would otherwise make earlier public figures misleadingly incomparable, the sponsor should ordinarily publish a public restatement rather than silently resetting the series.**
5. **Historical public versions should remain visible; restatement supplements history and does not erase it.**

---

## 11. Relationship to adjacent archive surfaces

This surface closes the next narrow operational gap in the research-incident cluster.

- `docs/20-world-design/research-incident-disclosure-protocol-deviation-notice-and-participant-result-return.md` fixes what live conduct must be noticed and returned.
- `docs/20-world-design/research-incident-packets-closure-state-revision-and-delayed-harm-reopening.md` fixes the minimum object family for live and post-closure incident governance.
- `docs/20-world-design/research-incident-privacy-tiers-common-cause-linkage-and-aggregate-reporting.md` fixes privacy lanes, cross-protocol linkage, and anonymised periodic aggregate reporting.
- `docs/20-world-design/research-incident-cluster-identifiers-denominator-discipline-and-anti-gaming-comparison-rules.md` fixes stable cluster identity, declared denominators, roll-up families, and anti-gaming comparison discipline.
- **This surface** fixes what must happen when those visible comparison bases later change: rollover windows, exclusion ledgers, and public restatement.

That narrower object-family layer is now fixed in `docs/20-world-design/research-freeze-waiver-notices-corrective-action-closure-and-warning-markers.md`: once the archive says when instability becomes a freeze or audit problem, it also has to say how waiver, warning, remediation, closure, and clearance appear publicly.

---

## Bottom line

A personhood world should not let AI-person research look safer merely because the sponsor got better at **rewriting the series.** The archive therefore now fixes one more compact layer for public incident accountability: **visible rollover windows, versioned exclusion ledgers, and mandatory public restatement when the comparison basis materially changes.** `[REF-0315]` `[REF-0321]` `[REF-0322]` `[REF-0325]` `[REF-0326]` `[REF-0327]` `[REF-0328]`
