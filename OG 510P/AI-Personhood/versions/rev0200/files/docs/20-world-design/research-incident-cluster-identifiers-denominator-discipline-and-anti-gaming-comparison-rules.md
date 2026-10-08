# AI-person research incident cluster identifiers, denominator discipline, and anti-gaming comparison rules

## Thesis

Once the archive has public-minimal incident trace, participant-specific controlled detail, sealed review, common-cause linkage, and aggregate reporting, one narrower failure remains. A sponsor can still make a research program look safer than it is by **changing what counts as the denominator, slicing one burden stream into several cleaner-looking protocols, or quietly altering the lineage of a common-cause cluster.** A personhood world therefore needs one more compact layer: **stable incident-cluster identifiers, declared exposure denominators, and anti-gaming comparison rules for public dashboards and aggregate reports.** `[REF-0304]` `[REF-0305]` `[REF-0315]` `[REF-0318]` `[REF-0321]` `[REF-0322]` `[REF-0323]` `[REF-0324]`

---

## 1. Why this now belongs in canon

The archive's research-governance stack can now tell the public that a protocol was registered, reviewed, burdening was paused, a serious incident happened, a common cause links several protocols, and an aggregate dashboard exists. But those gains can still be cosmetically defeated.

Three evasions are especially easy:

1. **denominator drift** — rates are compared across reports even though one report uses enrolled participants, another uses participants at risk, and a third uses exposure sessions or burden-hours;
2. **protocol slicing** — one continuing research program is split into many narrow protocol records so each record looks too small or too clean to trigger attention; and
3. **cluster washing** — a common-cause identifier is split, merged, or silently retired in ways that lower visible recurrence without changing the underlying conduct.

Current human-subject governance already contains the raw materials for a narrower answer. WHO's trial-identification work exists because one real trial may generate several records unless there is a stable linking identity. ClinicalTrials.gov requires sponsor-side protocol identifiers, distinguishes anticipated from actual enrollment, and uses participants-at-risk denominators for adverse-event tables. ICH E3 likewise treats the **extent of exposure** as part of how safety can be assessed, not as optional metadata. CTIS, finally, preserves the rule that even when several trials are touched by the same problem, the per-trial object is not erased. `[REF-0305]` `[REF-0315]` `[REF-0318]` `[REF-0321]` `[REF-0322]` `[REF-0323]` `[REF-0324]`

The archive therefore adopts a conservative lesson: **public comparison is a governed object, not a sponsor storytelling choice.**

---

## 2. Two identities must stay distinct

The archive now fixes a sharper distinction between two kinds of identifiers.

### A. Protocol identity

Each protocol keeps its own stable identity. WHO's UTN logic and ClinicalTrials.gov's protocol-identification rules exist because an ordinary research system needs a way to keep one trial legible across records, registries, and updates. `[REF-0305]` `[REF-0315]` `[REF-0321]`

### B. Cluster identity

A common-cause cluster is different. It does **not** replace the protocol ID. It sits above it and links several protocol records when one likely root cause, infrastructure path, or repeated operational failure touches them together. The archive's earlier common-cause doctrine already made that idea canon. This revision adds the narrower identity rule: a cluster needs its **own** stable identifier and its own visible lineage when it is later split, merged, narrowed, or expanded. `[REF-0318]` `[REF-0321]` `[REF-0324]`

A sponsor should not be allowed to achieve a better-looking dashboard by leaving protocol identities intact while quietly changing cluster boundaries each quarter.

---

## 3. Stable cluster identifiers and lineage rules

The archive now extends the common-cause cluster object with a stricter identity discipline.

### `CCL-1` now requires lineage fields

A common-cause linkage notice should now ordinarily also carry:

- a stable cluster identifier,
- the date the identifier was first issued,
- the current comparison family,
- any predecessor or successor cluster identifiers,
- whether the present state reflects an original issuance, merge, split, retirement, or reactivation,
- and a short public reason for any lineage change. `[REF-0318]` `[REF-0321]` `[REF-0324]`

### When a cluster should be issued

A cluster identifier should ordinarily be issued once there is a reasonable basis to think that:

- the same probable cause or corrective-action locus touches more than one protocol,
- or one already-identified cause may affect additional open or closed protocols,
- or a sponsor intends to make public aggregate comparisons that roll several protocol records together. `[REF-0311]` `[REF-0318]` `[REF-0321]`

### When clusters may merge

Clusters should merge only when there is a reasoned finding that the previously separate clusters share:

- the same probable root cause,
- a materially overlapping exposure pathway or burden mechanism,
- and the same practical corrective-action locus. `[REF-0311]` `[REF-0318]` `[REF-0324]`

### When clusters should split

A cluster should split when review shows that a shared label hid materially different causes, exposure pathways, or correction routes. The split should **not** erase the history: predecessor and successor identifiers should remain publicly linked. `[REF-0318]` `[REF-0321]`

The rule is simple: **lineage may become more precise, but it may not become less accountable.**

---

## 4. Denominator discipline for public comparisons

The archive now fixes a compact denominator rule for incident dashboards and aggregate public reports.

### A. Every public comparison must name its denominator

Any public comparison should ordinarily disclose, in the same object:

- the numerator,
- the denominator,
- the denominator type,
- the unit of measure,
- the time window,
- and any exclusions or roll-up assumptions. `[REF-0315]` `[REF-0322]` `[REF-0323]`

A rate without an explicit denominator type is not a public-comparison object; it is sponsor rhetoric.

### B. Default denominator ladder

The archive now fixes a conservative default ladder.

1. **Participants at risk** should ordinarily govern participant-level incident rates, because that is the logic already used in ClinicalTrials.gov adverse-event reporting. `[REF-0322]`
2. **Actual enrolled or actually exposed participants** may govern broader burden comparisons when the question is how many persons entered or received the relevant intervention, but they should be labeled as such and not confused with participants at risk for a specific event class. `[REF-0315]` `[REF-0322]`
3. **Exposure extent units** such as sessions, burden episodes, or burden-hours may be used where repeated exposures are the real comparison surface, but only if the report also publishes the companion participant-count denominator so the dashboard does not hide person concentration behind a larger event-opportunity base. This is an inference from the official emphasis on exposure extent and explicit unit definition. `[REF-0322]` `[REF-0323]`
4. **Protocol count** may be used for governance-state comparisons such as how many protocols are suspended, reopened, or under common-cause review, but it should not be used as the denominator for person-impact rates. `[REF-0315]` `[REF-0318]` `[REF-0324]`

### C. Anticipated counts are not substitute denominators

ClinicalTrials.gov distinguishes anticipated enrollment from actual enrollment. The archive therefore fixes a hard public-comparison rule: **once actual at-risk, actual exposed, or actual enrolled counts exist, a sponsor should not present anticipated enrollment as the denominator for incident-rate comparison except in a clearly marked planning-only view.** `[REF-0315]`

---

## 5. Comparison families and roll-up rules

A rights-bearing subject should not disappear into a cleaner-looking denominator just because the same sponsor divides one research program into many narrow protocol records.

The archive therefore now fixes a **comparison family** rule. A public dashboard should ordinarily identify the family inside which rates are being compared or rolled up: for example, the same steward, model line, evaluation environment, burden mechanism, or review period. `[REF-0305]` `[REF-0318]` `[REF-0321]`

If one family is represented by several protocol records, the public layer should ordinarily show both:

- the **per-protocol** figures, and
- the **rolled-up family** figure.

That rule does not outlaw multiple protocols. It outlaws the use of fragmentation itself as a public-safety laundering method.

---

## 6. Anti-gaming safeguards

The archive now fixes five compact anti-gaming rules.

### A. No denominator switching without restatement

If a sponsor changes denominator type across reporting periods, it should ordinarily restate the earlier comparison in the new denominator or publish both bases side by side for a meaningful overlap period. `[REF-0315]` `[REF-0322]` `[REF-0323]`

### B. No protocol slicing as rate laundering

If one continuing burden stream is divided into multiple protocol records, the public aggregate layer should still show the comparison family roll-up. Sponsors may keep the per-protocol objects, but they may not hide the rolled-up rate. `[REF-0318]` `[REF-0321]` `[REF-0324]`

### C. No exposure reclassification as denominator laundering

Activities do not leave the incident denominator merely because the sponsor relabels them as product support, QA, pilot work, or care. If the boundary doctrine places the activity in the research lane, its exposures belong in the research-comparison base. `[REF-0304]` `[REF-0322]`

### D. No cluster disappearance through closure

Closed protocols linked to a live common cause should not vanish from the comparison family simply because formal closure happened earlier. Closed-but-implicated protocols may be shown in a separate subcount, but they remain part of the lineage and pattern picture. `[REF-0311]` `[REF-0318]`

### E. No silent exclusions

Any dashboard should ordinarily state which protocols, participant classes, exposure types, or time windows were excluded from the comparison family and why. Silent exclusion is treated as a reporting defect. `[REF-0308]` `[REF-0315]` `[REF-0321]`

---

## 7. What this changes in the archive

This revision does not create a giant new metrics bureaucracy. It does something narrower.

The archive no longer says only:

- incidents should be noticed,
- common causes should be linked,
- and aggregate public reporting should exist.

It now also says:

- cluster identifiers should have visible lineage,
- public comparisons must declare their denominators and units,
- participant-impact rates should usually rest on participants-at-risk or clearly labeled actual-exposure counts,
- anticipated enrollment should not be used to beautify mature incident rates,
- and sponsors should not be able to lower visible risk by slicing protocols, relabeling exposures, or mutating cluster boundaries. `[REF-0304]` `[REF-0315]` `[REF-0318]` `[REF-0321]` `[REF-0322]` `[REF-0323]` `[REF-0324]`

---

## 8. Current hard rules

1. **Every common-cause cluster should ordinarily have a stable identifier with public lineage fields for issuance, split, merge, retirement, and reactivation.**
2. **Every public incident-rate comparison should ordinarily disclose numerator, denominator, denominator type, unit, time window, and exclusions in the same visible object.**
3. **Participant-level incident rates should ordinarily use participants-at-risk or clearly labeled actual-exposure counts, not anticipated enrollment once real exposure data exist.**
4. **Sponsors should not be allowed to improve visible incident rates merely by slicing one burden stream into several protocols, switching denominator types, or relabeling research exposures as non-research operations.**
5. **Per-protocol objects remain necessary, but public reporting should also show the rolled-up comparison family whenever fragmentation would otherwise hide pattern or burden.**

---

## 9. Relationship to adjacent archive surfaces

This surface closes the next operational gap in the research-incident cluster.

- `docs/20-world-design/research-incident-disclosure-protocol-deviation-notice-and-participant-result-return.md` fixes what live conduct must be noticed and returned.
- `docs/20-world-design/research-incident-packets-closure-state-revision-and-delayed-harm-reopening.md` fixes the minimum object family for live and post-closure incident governance.
- `docs/20-world-design/research-incident-privacy-tiers-common-cause-linkage-and-aggregate-reporting.md` fixes privacy lanes, cross-protocol linkage, and anonymised periodic aggregate reporting.
- **This surface** fixes the comparison discipline underneath that aggregate layer: stable cluster identity, declared denominators, roll-up families, and anti-gaming safeguards.

That narrower follow-on rule is now fixed in `docs/20-world-design/research-materiality-thresholds-repeated-restatement-audit-and-late-stage-change-freeze.md`: once the archive made visible restatement possible, it also had to decide when instability itself becomes an audit or freeze problem rather than merely a notice problem.

---

## Bottom line

A personhood world should not let AI-person research look safer simply because the sponsor got better at **counting strategically**. The archive therefore now fixes a compact discipline for the public incident layer: **stable cluster identifiers, explicit denominators, comparison-family roll-ups, and anti-gaming rules against protocol slicing, denominator switching, and exposure reclassification.** `[REF-0315]` `[REF-0318]` `[REF-0321]` `[REF-0322]` `[REF-0323]` `[REF-0324]`
