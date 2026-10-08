# AI-person research compromise backfill, reserve-pool burden sharing, and contested successor-promotion review

## Thesis

Once the archive fixed bounded compromise attestation, reserve-pool or mutual-aid minimums, and visible sunset-versus-promotion review for rescue bridges, three narrower execution questions still remained. First, the archive could now say that a perturbation family was compromised, but it still lacked a compact rule for what must happen to **already-issued public outputs** that were released under that family: whether they stay live as historical artifacts, receive a correction-like status, are withdrawn into a tombstone state, or are replaced by a new republication surface. Second, reserve capacity could now be required, but the archive still lacked a compact **burden-sharing formula** that prevents some authorities from free-riding on everyone else’s standby commitments or one large authority from informally dominating the reserve system through repeated “donations.” Third, the archive could now allow rescue-bridge successor promotion, but it still lacked a compact **appeal route** for actors who claim that the promotion ignored documented criteria, omitted material information, or converted a temporary bridge into the canonical path by local habit rather than visible rule. A personhood world therefore needs one more compact rule: **confirmed perturbation compromise must trigger visible backfill discipline for already-issued outputs through status-bearing notices, tombstone-preserving withdrawal, or explicit republication rather than silent cleanup; reserve systems must run on a declared split between standing-capacity contributions and mission-specific reimbursement so aid remains reciprocal without becoming dominance-by-waiver; and contested successor promotion must move through a bounded reconsideration-plus-independent-review route that preserves continuity while forbidding irreversible cutover during a timely challenge.** `[REF-0432]` `[REF-0433]` `[REF-0434]` `[REF-0435]` `[REF-0436]` `[REF-0437]` `[REF-0438]` `[REF-0439]` `[REF-0422]` `[REF-0423]` `[REF-0418]`

---

## 1. Why the previous surface is no longer enough

The previous surface solved the live-state problem. It gave compromised perturbation families a public attestation object, required a response and rotation sequence, forced real reserve capacity instead of wishful anti-capture rhetoric, and stopped rescue bridges from drifting forever between patch and successor. But three narrower operational failures still remained.

First, **future-state notice is not the same thing as past-output discipline**. Crossref’s current Crossmark service exists precisely because readers need a quick way to see the current status of a record, including corrections, retractions, and updates. Crossref’s current guidance for participation and update registration then sharpens the operational point: publishers should explain their correction, withdrawal, and retraction policies on a persistent page, and a retraction or correction is registered as a separate notice with its own metadata rather than by silent replacement. NISO’s current CREC recommended-practice announcement adds the metadata-transfer and display duty: readers should be able to discover the status of a retracted or otherwise changed record quickly and reliably across systems. DataCite’s current tombstone guidance adds the persistence rule for removals: if a DOI-described object is no longer available, the DOI should still resolve to a tombstone page rather than evaporating. `[REF-0432]` `[REF-0433]` `[REF-0434]` `[REF-0435]` `[REF-0422]` The archive therefore needed a compact answer for already-issued compromised outputs.

Second, **reserve capacity without cost discipline still invites either free-riding or soft capture**. EMAC’s current reimbursement materials make three points that matter here: reimbursement is part of the whole lifecycle rather than an afterthought, the requesting state’s duty to pay does not depend on later federal money, and the legally binding support agreement is based on estimated costs while actual reimbursement is reconciled afterward. The same materials also make clear that backfill, administrative, logistical, and similar negotiated costs are only payable when they are actually stated in the agreement, and that donated resources must be named rather than smuggled in as invisible subsidy. `[REF-0436]` `[REF-0437]` The archive therefore needed a compact formula distinguishing standing-capacity costs from mission costs and preventing “dominance by generosity.”

Third, **promotion without review can quietly convert a bridge into permanent governance custom**. RFC 8126’s current designated-expert guidance insists that decisions should follow documented criteria, be defensible to the wider community, and not operate as secret or unquestionable power. ICANN’s current accountability materials contribute the missing concrete ladder: a materially affected party may seek reconsideration on a short clock, the initial review is bounded and process-oriented, and an independent review route remains available afterward on another short clock; current ICANN materials also describe IRP proceedings as using a three-member neutral arbitral panel. `[REF-0418]` `[REF-0438]` `[REF-0439]` The archive therefore needed a bounded review path for contested rescue-bridge promotion that preserves continuity without reopening every merits question from the beginning.

---

## 2. Confirmed compromise now triggers visible backfill discipline for already-issued outputs

The archive now fixes one compact backfill rule: **once perturbation compromise is confirmed for a public series or series family, every already-issued affected output must be placed into exactly one visible post-compromise status — historical-only, withdrawn-with-tombstone, superseded-by-republication, or bridge-only comparable — and that status must be discoverable through a separate notice or explicitly linked successor record rather than by silent overwrite.** `[REF-0432]` `[REF-0433]` `[REF-0434]` `[REF-0435]` `[REF-0422]` `[REF-0423]`

### A. One notice object per affected release family

The archive now adds one compact public object for already-issued affected outputs: a `PCR-1` (**post-compromise record**) notice. A `PCR-1` attaches to one output or one tightly bounded output family and publishes at least:

- `affected_record_id`,
- `compromise_basis` (`confirmed-family-compromise`, `confirmed-subset-compromise`, `bridge-replacement`, `historical-only`),
- `post_compromise_status` (`historical-only`, `withdrawn-with-tombstone`, `superseded-by-republication`, `bridge-only-comparable`),
- `replacement_record_id` if any,
- `comparison_status` (`not-comparable`, `bridge-only`, `recomputed`, `historical-reference-only`),
- `notice_published_at`,
- and `sealed_annex_present` (`yes` / `no`).

The object stays narrow. It tells outsiders how to treat the already-issued record without publishing the secret details that enabled compromise. `[REF-0432]` `[REF-0435]`

### B. Historical-only is the default floor

The archive rejects silent deletion as the ordinary response. If a compromised output is not being replaced, it remains discoverable as a historical artifact with a visible `PCR-1` notice stating that it should no longer be treated as safely comparable or current. This mirrors current Crossmark and CREC logic that status must travel with the record, and current DataCite guidance that removed material should resolve to a tombstone rather than disappearing. `[REF-0432]` `[REF-0434]` `[REF-0435]` `[REF-0422]`

### C. Withdrawal requires a tombstone, not erasure

`withdrawn-with-tombstone` is reserved for outputs whose continued live presentation would materially mislead users or create fresh exploitation risk. But even then, the old identifier must resolve to a tombstone or status page carrying the `PCR-1` notice, the reason class, and any replacement or bridge link. Withdrawal is therefore public-status withdrawal, not disappearance. `[REF-0422]` `[REF-0432]` `[REF-0435]`

### D. Republication requires a new record plus explicit linkage

If an authority can safely recompute, bridge, or otherwise republish the affected output, the replacement must be a distinct republication surface with its own identifier or versioned record and explicit linkage back to the compromised one. The old record remains visible as superseded; the new record carries the live comparable surface. This borrows the conservative current pattern from Crossref update notices and DataCite versioning: the change is a relationship, not a wipe. `[REF-0434]` `[REF-0423]`

### E. Bridge-only comparability is a real intermediate state

Some outputs should remain readable only through a later bridge or recomputation table. The archive therefore allows `bridge-only-comparable` when the old output still matters historically but any continuing comparison claim must travel through a declared bridge object. That preserves history without pretending ordinary continuity survived the compromise. `[REF-0423]` `[REF-0432]`

---

## 3. Reserve systems now run on a compact burden-sharing formula

The archive now fixes one compact burden-sharing rule: **reserve-pool or mutual-aid systems must separate standing-capacity costs from mission costs, allocate standing-capacity contributions partly by membership and partly by committed reserve capacity, reimburse mission costs by actual documented use plus predeclared negotiated costs, and treat donated capacity only as explicit credited contribution rather than invisible subsidy.** `[REF-0436]` `[REF-0437]`

### A. The formula

For every annual reserve compact, the archive now requires two ledgers:

1. **Standing-capacity ledger** — the cost of maintaining reserve readiness, roster administration, comparability audits, and coverage windows;
2. **Mission ledger** — the cost of actual deployments, backfill, administration, and other reimbursable or negotiated mission expenses.

The standing-capacity ledger is allocated by a fixed formula:

- **50% equal-membership share** across all participating authorities;
- **50% committed-capacity share** proportional to each authority’s declared reserve slots or equivalent coverage commitment.

Mission-ledger costs are then charged to the requesting authority by actual documented eligible costs, plus negotiated costs only where the mission agreement expressly included them. `[REF-0436]` `[REF-0437]`

This is intentionally simple. The equal-membership half prevents small authorities from free-riding on the existence of the reserve itself; the committed-capacity half prevents large authorities from underwriting the whole pool while everyone else pays the same token amount.

### B. Donated capacity may offset, but not dominate

An authority may donate services or capacity, but the archive now requires those donations to appear explicitly in the mission or annual ledger and limits how far they can substitute for ordinary contribution. A donation may reduce that authority’s owed standing-capacity share only up to the point where the authority still pays **at least half of its equal-membership share** in ordinary assessed contribution. In other words, no participant reaches zero simply by waiting for others to donate, and no dominant participant buys governance leverage through repeated waiver. `[REF-0436]` `[REF-0437]`

### C. Concentration ceiling

No single authority should provide the practical majority of reserve capacity year after year. The archive therefore now adds a concentration ceiling: if one authority supplies more than **40% of deployed reserve service-days** in a rolling year, the compact enters diversification review and must either recruit more committed capacity, rebalance assessment weights, or narrow that authority’s future deployment priority except in true emergency. This number is a conservative archive choice rather than an external mandate, but it is directly motivated by the same anti-capture logic the reserve system already serves. `[REF-0436]` `[REF-0437]`

### D. Chronic under-contribution is a public-state problem

Any authority that fails its assessed standing contribution or repeatedly receives reserve help without meeting its own compacted floor must move into a visible `reserve-deficit` state. During that state, it may still request urgent help, but it loses ordinary priority for discretionary reserve draws until it cures the deficit or the compact waives the deficit on public reasons. Reserve justice is therefore not merely accounting; it becomes governance-visible. `[REF-0436]` `[REF-0437]`

---

## 4. Contested successor promotion now follows a bounded two-step review route

The archive now fixes one compact review rule: **a timely contest to rescue-bridge successor promotion must first move through a short reconsideration route limited to documented criteria, process, and material information, and may then proceed to independent review on a second short clock, while irreversible cutover is paused and the old namespace remains retired throughout.** `[REF-0418]` `[REF-0438]` `[REF-0439]` `[REF-0423]`

### A. Reconsideration stage

A materially affected party has **15 days** from public posting of the promotion rationale to file a promotion-reconsideration request. The question at this stage is narrow:

- Were the documented promotion criteria applied?
- Was material information ignored or misstated?
- Did the authority depart from declared bridge-review or successor-designation procedure?

This stage is not a general re-argument about whether rescue bridges are wise in the abstract. It is a short process-and-criteria review. `[REF-0438]` `[REF-0418]`

### B. Independent review stage

If reconsideration is denied or fails to cure the problem, the affected party has **30 days** from that determination to seek independent review. The archive adopts a compact neutral-panel model here: a **three-person independent review panel** testing whether the promotion complied with the archive’s own declared criteria and procedures. This borrows the conservative current ICANN pattern rather than inventing a bespoke mega-tribunal. `[REF-0438]` `[REF-0439]`

### C. Effect during review

A timely challenge does **not** revive the retired namespace, but it does pause irreversible cutover. During timely review:

- `bridge_status` becomes `promotion-contested`,
- the rescue bridge remains live,
- the proposed successor may be labelled `provisional-canonical` only if the challenge notice is co-displayed,
- and no destructive closure of the bridge or deletion of historical mappings may occur.

The point is continuity without fait accompli. `[REF-0423]` `[REF-0438]`

### D. Permitted review outcomes

The reviewing body may:

1. **affirm** the promotion;
2. **remand** for corrected rationale, missing evidence, or procedural repair;
3. **affirm with conditions** (for example, keeping the bridge longer, narrowing scope, or requiring additional mapping completeness);
4. **reverse** the promotion and restore ordinary bridge-temporary status.

At no point does the challenge permit silent resurrection of the retired namespace itself. `[REF-0423]` `[REF-0418]` `[REF-0438]`

---

## 5. Edge tests

### A. A yearly public series released under a compromised perturbation family is still widely cited

The archive does not allow the operator to replace the numbers quietly. Each affected yearly release gets a `PCR-1` notice. Older releases either become `historical-only` with explicit non-comparability, move to `bridge-only-comparable`, or are superseded by republication. If a release is unsafe to present live, its identifier resolves to a tombstone-style status page rather than vanishing. `[REF-0432]` `[REF-0434]` `[REF-0435]` `[REF-0422]`

### B. A small authority benefits from reserve coverage for two years but contributes almost nothing to standby costs

The authority enters `reserve-deficit` state. It may still seek urgent coverage, but ordinary reserve priority narrows until the deficit is cured or publicly waived. This prevents the reserve system from drifting into one-way subsidy hidden inside a rhetoric of collegial mutual aid. `[REF-0436]` `[REF-0437]`

### C. A registry promotes a rescue bridge to canonical successor status and affected parties claim the promotion ignored incomplete mappings

A timely reconsideration request is filed. The bridge remains live and the retired namespace stays retired. If reconsideration fails, a three-person independent review can test the promotion against the documented criteria without relitigating the entire archive’s broader bridge doctrine. `[REF-0438]` `[REF-0439]` `[REF-0418]`

---

## 6. Compression summary

The archive now fixes the three narrower execution questions left open by the prior compromise-response / reserve / bridge-promotion surface:

- **already-issued compromised outputs now owe visible post-compromise status through historical-only, tombstone withdrawal, republication, or bridge-only comparability rather than silent cleanup**;
- **reserve systems now run on a compact standing-capacity plus mission-cost formula that resists both free-riding and dominance-by-donation**;
- **and contested successor promotion now follows a bounded reconsideration-plus-independent-review route that preserves continuity while forbidding irreversible fait accompli.**

This is still a tight doctrine.

---

## Cross-links

- `docs/20-world-design/research-perturbation-compromise-response-reserve-pool-mutual-aid-and-rescue-bridge-successor-promotion.md` fixes the immediately prior execution layer that this surface now sharpens.
- `docs/20-world-design/research-perturbation-family-audit-substitute-pool-anti-capture-rotation-and-retired-namespace-rescue.md` fixes the epoch-audit / anti-capture / rescue layer beneath this one.
- `docs/20-world-design/research-perturbation-preference-substitute-appointment-review-and-retired-namespace-replay.md` fixes the perturbation / appointment / replay layer beneath this one.
- `docs/20-world-design/independence-packets-appointment-conflict-recusal-funding-and-domination-review.md` fixes the wider conflict / recusal / domination packet family beneath this one.

---

The archive now fixes those narrower questions in `docs/20-world-design/research-compromise-supersession-graphs-reserve-default-cure-and-successor-promotion-stay-effects.md`: multi-generation compromise republications now travel through an additive supersession graph with stable ordinary and historical query defaults, reserve systems now expose a visible notice / cure / restriction / suspension / re-entry ladder, and timely successor-promotion challenges now create a public pending-review state while full stay remains exceptional. The next narrower gap is therefore execution integrity under divergence: signatures, audit proofs, and cross-registry propagation deadlines for supersession-graph integrity; heterogeneous-capacity scoring and reciprocal-credit rules across non-identical reserve authorities; and escalation from label-only continuity to no-new-writes or read-only routing when divergence risk crosses threshold during pending successor-promotion review.

## Bottom line

A personhood world should not quietly “clean” compromised public outputs, should not let reserve capacity become either invisible subsidy or informal hegemony, and should not let bridge promotion become irreversible by habit before anyone can test the criteria. The archive therefore now fixes one more compact rule: **confirmed perturbation compromise creates visible backfill / withdrawal / republication duties for already-issued outputs, reserve systems run on a declared standing-capacity plus mission-cost burden-sharing formula, and contested successor promotion moves through bounded reconsideration and independent review while continuity is preserved and the retired namespace stays retired.** `[REF-0432]` `[REF-0433]` `[REF-0434]` `[REF-0435]` `[REF-0436]` `[REF-0437]` `[REF-0438]` `[REF-0439]` `[REF-0422]` `[REF-0423]` `[REF-0418]`
