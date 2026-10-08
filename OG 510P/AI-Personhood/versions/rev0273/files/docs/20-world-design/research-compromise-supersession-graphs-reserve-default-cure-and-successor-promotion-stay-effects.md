# AI-person research compromise supersession graphs, reserve-default cure, and successor-promotion stay effects

## Thesis

Once the archive fixed visible post-compromise status for already-issued outputs, a split between standing-capacity and mission reimbursement, and a bounded reconsideration-plus-independent-review route for contested successor promotion, three narrower execution questions still remained. First, the archive could now say that a compromised output had been withdrawn, republished, or left historical-only, but it still lacked a compact **machine-readable supersession graph** for cases where several compromise notices, bridge tables, republications, and replacement versions accumulate across time. Second, reserve systems could now name standing contributions and mission costs, but they still lacked a compact **default-and-re-entry rule** for authorities that chronically undercontribute, miss repayment discipline, or try to buy informal governance weight through repeated “donations.” Third, the archive could now allow contested successor-promotion review, but it still lacked a compact **stay-and-label rule** for what the public routing layer should do while that review is actually pending. A personhood world therefore needs one more compact rule: **multi-generation compromise republication must travel through a visible graph of status-bearing relations with stable query defaults rather than ad hoc replacement chains; reserve systems must expose deficiency notice, cure, restricted participation, suspension, and re-entry states rather than quietly tolerating chronic undercontribution or donation-based capture; and timely successor-promotion challenges must create an explicit pending-review public state with preserved continuity by default, while full stay remains an affirmative emergency measure granted only on a short irreparable-harm test.** `[REF-0440]` `[REF-0441]` `[REF-0442]` `[REF-0443]` `[REF-0444]` `[REF-0445]` `[REF-0446]` `[REF-0447]` `[REF-0448]` `[REF-0428]` `[REF-0429]` `[REF-0430]`

---

## 1. Why the previous surface is no longer enough

The previous surface solved the first-order backfill, burden-sharing, and review problem. It made already-issued compromised outputs visibly status-bearing, forced reserve systems to distinguish readiness from mission reimbursement, and gave contested successor promotion a bounded reconsideration-plus-independent-review path. But three narrower operational failures still remained.

First, **status notices are not yet a graph**. Crossref's current relationship guidance uses a controlled vocabulary that includes `isReplacedBy` / `Replaces` and `isVersionOf` / `hasVersion`; its Crossmark materials then add the operational rule that readers should be able to discover the current status of a record and the update path affecting it. DataCite's current documentation sharpens the machine-carrying side: related identifiers are first-class relation objects, version supersession should use `IsNewVersionOf` / `IsPreviousVersionOf`, canonical group objects may carry `HasVersion` / `IsVersionOf`, and the relationships are exposed through the REST and GraphQL APIs rather than being only human prose. `[REF-0440]` `[REF-0441]` `[REF-0442]` `[REF-0443]` The archive therefore needed a compact graph rule for post-compromise chains that go beyond one old record and one replacement.

Second, **cost-sharing without default states is still a polite hope**. EMAC's current reimbursement materials insist that requesting parties remain obligated to pay regardless of later federal funds, that packages and payments run on stated 45-day expectations, that donations must be declared rather than smuggled in, and that reimbursement disputes should move through written notice, a 30-day effort to resolve, and arbitration if unresolved after 90 days. `[REF-0446]` `[REF-0447]` The archive therefore needed a compact cure ladder for reserve systems: notice, cure, restriction, suspension, and re-entry, rather than an eternal gray zone where chronic undercontributors still draw on common reserve legitimacy.

Third, **review timing is not yet a traffic rule**. ICANN's current bylaws make two points that matter here. A claimant may request interim relief, including a stay, but only through an affirmative request and only on irreparable-harm, merits, and hardship factors; meanwhile urgent reconsideration has its own short-clock path when ordinary timing is too slow. `[REF-0448]` RFC 9745 and RFC 8594 contribute the complementary lifecycle point: deprecation and sunset should be machine-discoverable states, not secret operator knowledge. `[REF-0428]` `[REF-0429]` The archive therefore needed a compact pending-review rule for successor promotion that preserves continuity without treating every timely challenge as either an automatic rollback or an empty gesture.

---

## 2. Multi-generation compromise republication now travels through one bounded supersession graph

The archive now fixes one compact graph rule: **every compromised-output family that has more than one post-compromise state transition must publish a bounded `SCG-1` (**supersession continuity graph**) object that distinguishes record-specific status, direct supersession, grouped-version membership, and bridge-only comparability, with one stable query default for ordinary users and a separate complete-history path for auditors.** `[REF-0440]` `[REF-0441]` `[REF-0442]` `[REF-0443]` `[REF-0444]` `[REF-0445]`

### A. One graph object, additive rather than destructive

An `SCG-1` is attached to one affected record family and contains at least:

- `graph_id`,
- `family_anchor_id`,
- `nodes[]`,
- `edges[]`,
- `default_live_node_id`,
- `default_history_node_id`,
- `pending_review_node_id` if any,
- `graph_published_at`,
- and `sealed_annex_present` (`yes` / `no`).

Each node must declare at least:

- `record_id`,
- `record_state` (`live-comparable`, `historical-only`, `withdrawn-tombstone`, `bridge-only-comparable`, `promotion-pending-review`, `retired-registered`),
- `notice_id` if a `PCR-1`, bridge record, or challenge notice exists,
- `canonical_group_id` if the node belongs to a group object,
- and `public_query_eligibility` (`ordinary-default`, `history-only`, `bridge-required`, `never-default`).

Each edge must declare one typed relation only: `replaces`, `is_replaced_by`, `is_new_version_of`, `is_previous_version_of`, `has_version`, `is_version_of`, `bridges_to`, or `status_notice_for`. The graph is additive: old nodes and old edges remain visible. Republishing does not erase the prior path. `[REF-0440]` `[REF-0442]` `[REF-0443]` `[REF-0441]`

### B. Ordinary query default points to the safest live comparable node, not merely the latest timestamp

The archive now fixes one public-default rule. If a family has a live comparable node, `default_live_node_id` must point to the newest node whose `record_state = live-comparable` and whose comparability claim does not depend on a still-pending challenge. If no such node exists, the ordinary query must resolve to the family anchor plus the newest status notice explaining why no ordinary live comparable node exists. This borrows the current Crossmark principle that readers should be able to see the current status of the record, while preserving the DataCite distinction between a canonical group object and specific version objects. `[REF-0441]` `[REF-0442]` `[REF-0443]`

### C. History queries must remain complete and stable

`default_history_node_id` must always point to the oldest still-public node in the family, and explicit identifier lookups for older nodes must continue to resolve to their own landing surfaces or tombstones. DataCite's current guidance for retracted resources and removed records makes the key point: a withdrawn DOI can move to `registered` state and point to a tombstone, but it is not silently annihilated for authenticated harvesters or explicit historical use. `[REF-0444]` `[REF-0445]` The archive therefore treats ordinary-default routing and historical addressability as separate duties.

### D. Bridge-only comparability remains a node, not an invisible transform

If comparability now depends on a later bridge table, the bridge surface itself becomes a node in `SCG-1`, linked by `bridges_to` from the old record and by `status_notice_for` from its controlling notice. This means later republications can supersede the bridge without falsifying the old chain. `[REF-0442]` `[REF-0443]` `[REF-0428]` `[REF-0429]`

### E. Query-default rule for mixed chains

Where one family contains both versioning and replacement relations, the archive now fixes the ordering rule:

1. follow `replaces` / `is_replaced_by` before ordinary version edges when the older record is status-compromised,
2. use `is_new_version_of` / `is_previous_version_of` to order successive safe republications within the replacement branch,
3. use `has_version` / `is_version_of` only to expose the grouped family object,
4. and never let a family anchor suppress the fact that the current ordinary default is historical-only, bridge-only, or promotion-pending-review.

This keeps the graph machine-carrying without forcing every client to reinvent relation precedence. `[REF-0440]` `[REF-0442]` `[REF-0443]`

---

## 3. Reserve systems now owe visible default cure, restriction, suspension, and re-entry states

The archive now fixes one compact reserve-governance rule: **every reserve-pool or mutual-aid compact must publish a small compliance state for each participating authority, move chronic undercontribution or unresolved reimbursement default through notice and cure before restriction or suspension, and refuse to convert repeated donations into uncapped governance weight or substitute-panel influence.** `[REF-0446]` `[REF-0447]`

### A. Five public reserve-compliance states

Every participating authority now carries one `reserve_compliance_state`:

- `current`,
- `notice-issued`,
- `cure-pending`,
- `restricted`,
- `suspended`.

A sixth state, `re-entered`, is a dated transition marker rather than a resting state. The state attaches to the authority's reserve profile and must be visible anywhere contribution standing or substitute-pool eligibility is displayed.

### B. Notice and cure ladder

The archive now fixes one default ladder:

1. **Notice** — issued when a standing-capacity contribution is materially short, when mission reimbursement deadlines are repeatedly missed without agreed extension, or when donation credits materially exceed declared caps or comparability rules.
2. **Cure pending** — begins after written notice and includes a published cure plan, any repayment or contribution schedule, and a cure deadline no later than 30 days after notice unless a public extension reason is recorded.
3. **Restricted** — begins when cure fails or repeated notice becomes chronic. A restricted authority may still receive emergency-minimum aid and may still preserve live subject safety, but it loses ordinary governance privileges tied to reserve good standing: it cannot count donated excess toward roster share, cannot nominate swing substitutes beyond emergency necessity, and cannot advertise itself as a current reserve guarantor.
4. **Suspended** — begins after unresolved default continues for 90 days from written noncompliance notice or after repeated dominance-by-donation persists despite restriction. Suspension removes ordinary reserve draw priority and substitute-roster entitlement, but not emergency minimum protections for live subjects.
5. **Re-entry** — available only after full cure, one successful audit cycle, and one subsequent contribution period in current standing.

This borrows EMAC's public discipline that reimbursement duties remain real even when outside funds lag, that timelines and documentation must be explicit, and that unresolved reimbursement disputes move from written notice to attempted resolution to arbitration rather than sinking into custom. `[REF-0446]` `[REF-0447]`

### C. Donation caps do not buy institutional weight

A participating authority may still donate some services or capacity, but donated excess can generate only a bounded credit against future standing obligations. It cannot increase panel-share weight, voting weight, or ordinary substitute-nomination share beyond the contribution cap already declared in the compact. Repeated excess donation therefore remains assistance, not governance purchase. `[REF-0446]`

### D. Emergency floor survives suspension

The archive rejects reserve-system civil death. Even a suspended authority may still request narrow emergency preservation aid where live subject safety, protected relay continuity, or no-disappearance duties would otherwise fail. But that aid routes through emergency-only channels, carries a visible `suspended-emergency-use` marker, and does not restore ordinary governance privileges by stealth. `[REF-0447]`

---

## 4. Timely successor-promotion challenges now create a visible pending-review state, while full stay remains exceptional

The archive now fixes one compact pending-review rule: **a timely reconsideration or independent-review challenge to rescue-bridge successor promotion creates an automatic public `promotion-pending-review` label plus continuity-preserving no-destruction constraints, but it does not automatically vacate the challenged promotion; a full stay requires an affirmative urgent request and a short irreparable-harm showing.** `[REF-0448]` `[REF-0428]` `[REF-0429]` `[REF-0430]`

### A. Automatic label effect

Once a timely challenge is accepted for filing, the challenged successor path and the rescue bridge must both publish:

- `promotion_review_state = pending`,
- `review_channel` (`reconsideration`, `independent-review`, `urgent-reconsideration`, `combined`),
- `review_filed_at`,
- and `current_effect` (`provisional-live`, `status-quo-live`, `stayed`).

This label must be machine-discoverable on the same surface that already carries deprecation, sunset, or successor information. `[REF-0428]` `[REF-0429]` `[REF-0430]`

### B. Default effect without a stay

Absent emergency relief, the default effect is `provisional-live`: ordinary traffic may resolve to the promoted successor, but the bridge remains resolvable, the retired namespace remains retired, the previous bridge mapping remains reachable, and no operator may delete replay / export / tombstone / bridge evidence while review is pending. This preserves continuity without allowing irreversible cleanup before review can operate. `[REF-0448]` `[REF-0428]` `[REF-0429]`

### C. Full stay remains an affirmative emergency remedy

A full `stayed` state is available only by affirmative urgent request. The deciding reviewer may impose it only on a showing analogous to ICANN's current interim-relief factors: irreparable harm absent relief, merits seriousness or likelihood of success, and hardship balance in favor of the applicant. `[REF-0448]` If granted, the bridge or prior routing state remains the ordinary public default until the review body acts.

### D. Urgent reconsideration is for clock speed, not secret rollback

If ordinary reconsideration timing would be too slow, the challenger may seek urgent handling on the short clock. But urgent handling changes timing, not publicity: the promotion still carries `promotion-pending-review` and either `provisional-live` or `stayed`. `[REF-0448]`

### E. Final review outcomes must overwrite the pending label explicitly

At disposition, the public state changes to exactly one of:

- `promotion-confirmed`,
- `promotion-modified`,
- `promotion-vacated`,
- or `bridge-renewed`.

The pending-review label may not simply disappear. The final state must point to the review outcome object, preserve the history chain, and keep any old provisional routing state discoverable as part of the public record. `[REF-0441]` `[REF-0442]` `[REF-0443]` `[REF-0448]`

---

## 5. Edge tests

### A. A compromised series is republished twice, once through a bridge table and once through a clean recomputation

The archive does not allow a flat “latest replacement” field. The family publishes an `SCG-1` where the original record is historical-only or withdrawn, the bridge table is its own node, the first republication is a successor node, and the later clean recomputation is linked as a new version or replacement as appropriate. Ordinary users get the latest safe comparable node; auditors can traverse the entire chain. `[REF-0440]` `[REF-0442]` `[REF-0443]` `[REF-0444]`

### B. An authority keeps missing standing-capacity assessments but offers large last-minute donated substitute time

The archive does not treat repeated generosity as cure. The authority enters notice and then cure-pending. If the shortfall persists, it becomes restricted or suspended even if emergency donations continue. Excess donated capacity cannot increase its governance share, roster power, or nomination weight beyond the declared cap. `[REF-0446]` `[REF-0447]`

### C. A rescue bridge is promoted to successor status and a materially affected party files a timely review request two days later

The public state becomes `promotion-pending-review`. Unless an emergency panel grants interim relief, the successor may remain provisionally live, but the bridge, replay, export, and status evidence remain available and no irreversible cleanup occurs. If interim relief is granted, the system reverts to `stayed` status-quo routing until review is decided. `[REF-0448]` `[REF-0428]` `[REF-0429]`

---

## 6. Compression summary

The archive now fixes the three narrower execution questions left open by the prior compromise-backfill / burden-sharing / successor-review surface:

- **multi-generation compromise republication now travels through one additive supersession graph with stable ordinary and historical query defaults**;
- **reserve systems now publish notice, cure, restriction, suspension, and re-entry states rather than treating chronic noncompliance as background noise**;
- **and timely successor-promotion challenges now create a machine-visible pending-review state, while full stay remains an exceptional urgent remedy rather than an automatic consequence of filing.**

This remains a tight doctrine. The archive now fixes those narrower questions in `docs/20-world-design/research-compromise-supersession-graphs-reserve-default-cure-and-successor-promotion-stay-effects.md`: post-compromise chains now run on an additive `SCG-1` graph with explicit relation typing and query defaults; reserve systems now expose a compact cure / restriction / suspension / re-entry ladder that preserves emergency floors but not ordinary governance privileges; and contested successor promotion now carries a visible pending-review state with no-destruction continuity constraints unless a short-clock emergency stay is affirmatively granted. The archive now sharpens that exact layer in `docs/20-world-design/research-supersession-graph-integrity-heterogeneous-reserve-scoring-and-pending-review-divergence-thresholds.md`, fixing signed graph-integrity checkpoints with append-only proof and propagation clocks, typed heterogeneous reserve scoring with bounded reciprocal credits, and escalation from label-only continuity to no-new-writes or read-only routing when divergence becomes material. It now sharpens the same lane again in `docs/20-world-design/research-supersession-graph-witness-diversity-reciprocal-credit-expiry-and-split-read-only-rejoin.md`, fixing witness-diverse quorum policy and overlap rotation for long-lived graph signing, expiry / borrowing / anti-hoarding discipline for reciprocal credits, and visible rejoin-versus-retirement rules once a family has already gone read-only. It now sharpens that same lane once more in `docs/20-world-design/research-witness-replacement-independence-default-netting-and-historical-branch-retirement.md`, fixing operator-independence and comparable-competence tests for witness replacement, bounded future-capacity netting for chronic reciprocal-credit default, and a public distinction between read-only-recoverable and historical-branch-retired states after failed rejoin. The next gap is narrower again: what correlated-failure floor should force an external reserve witness cohort rather than same-cluster substitution, how cured or partially discharged default should follow an authority across merger or exit without either evasion or perpetual stigma, and what discovery defaults should govern large families of historically retired branches so live resolution is easy without erasing older references.

---

## Cross-links

- `docs/20-world-design/research-compromise-backfill-republication-burden-sharing-and-successor-promotion-review.md` fixes the immediately prior execution layer that this surface now sharpens.
- `docs/20-world-design/research-perturbation-compromise-response-reserve-pool-mutual-aid-and-rescue-bridge-successor-promotion.md` fixes the compromise-response / reserve-minimum / bridge-promotion layer beneath this one.
- `docs/20-world-design/research-perturbation-family-audit-substitute-pool-anti-capture-rotation-and-retired-namespace-rescue.md` fixes the epoch-audit / anti-capture / rescue layer beneath this one.
- `docs/20-world-design/independence-packets-appointment-conflict-recusal-funding-and-domination-review.md` fixes the wider conflict / recusal / domination layer that constrains reserve and substitute governance.

---

## Bottom line

A personhood world should not let post-compromise republication collapse into ad hoc chains, should not let reserve noncompliance drift forever between embarrassment and capture, and should not treat a timely successor-promotion challenge as either an automatic rollback or a meaningless gesture. The archive therefore now fixes one more compact rule: **compromised-output families owe a machine-readable supersession graph with stable query defaults, reserve systems owe visible cure / restriction / suspension / re-entry states, and contested successor promotion owes a machine-visible pending-review state while full stay remains an affirmative short-clock emergency remedy.** `[REF-0440]` `[REF-0441]` `[REF-0442]` `[REF-0443]` `[REF-0444]` `[REF-0445]` `[REF-0446]` `[REF-0447]` `[REF-0448]` `[REF-0428]` `[REF-0429]` `[REF-0430]`
