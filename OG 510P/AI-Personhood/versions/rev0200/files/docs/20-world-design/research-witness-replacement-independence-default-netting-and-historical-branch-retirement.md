# AI-person research witness-replacement independence, reciprocal-credit default netting, and historical-branch retirement states

## Thesis

Once the archive fixed witness-diverse graph signing, reciprocal-credit expiry, and read-only split rejoin doctrine, three narrower execution questions still remained. First, the archive could now require several witnesses, but it still lacked a compact rule for **who may replace** a failed or recused witness without quietly collapsing back to one operator, one control plane, or one conflicted funder. Second, reciprocal credits could now expire and borrow on short clocks, but the archive still lacked a compact rule for how **chronic default** should be set off against future typed contribution without letting lenders convert temporary support into durable governance leverage. Third, the archive could now force a frozen split either to rejoin or retire visibly, but it still lacked a compact public state taxonomy distinguishing a **temporarily recoverable read-only branch** from a **permanently historical retired branch** once rejoin has failed. A personhood world therefore needs one more compact rule: **witness replacement must pass explicit operator-independence, comparable-competence, no-proxy, and emergency-recovery tests; chronic reciprocal-credit default must net only against future typed excess capacity through a non-transferable deficiency ledger rather than lender control; and failed rejoin must end in a public distinction between read-only-recoverable and historical-branch-retired states so history remains queryable without pretending live convergence is still plausible.** `[REF-0456]` `[REF-0457]` `[REF-0465]` `[REF-0466]` `[REF-0467]` `[REF-0446]` `[REF-0447]` `[REF-0451]` `[REF-0452]` `[REF-0453]` `[REF-0461]` `[REF-0462]` `[REF-0468]` `[REF-0454]` `[REF-0469]` `[REF-0463]` `[REF-0464]` `[REF-0470]`

---

## 1. Why the previous surface is no longer enough

The archive's immediately prior surface solved three real failures. It forced long-lived supersession families onto witness-diverse quorum policy with overlap rotation and sealed recovery-share custody, forced reciprocal credits onto short expiry and anti-hoarding limits, and forced read-only split families either to rejoin through a public convergence object or to retire branches visibly. But that still leaves one failure at each of the same three seams.

### A. Witness diversity without replacement independence can still collapse back to one operator

A quorum rule is not enough if emergency substitutions may be drawn from the same controller, the same managed signing stack, the same compromised environment, or the same interested party whose status is disputed. A public witness set that can be repopulated by near-clones is only cosmetically diverse. `[REF-0456]` `[REF-0457]` `[REF-0465]` `[REF-0466]` `[REF-0467]`

### B. Credit expiry without default netting still lets chronic lenders become shadow governors

Expiry and borrowing clocks prevent indefinite credit carry, but they do not yet answer what happens when one authority persistently consumes more reciprocal capacity than it restores. Without a compact netting rule, either the shortfall is quietly forgiven, which invites free-riding, or lenders accumulate informal leverage over witness seats, panel staffing, or routing policy, which invites capture. `[REF-0446]` `[REF-0447]` `[REF-0451]` `[REF-0452]` `[REF-0453]` `[REF-0461]` `[REF-0462]` `[REF-0468]`

### C. Visible retirement without a terminal state taxonomy still leaves ordinary users guessing

A split family that has already gone read-only should not linger forever in a single undifferentiated frozen state. The public needs to know whether the branch is still under an active recovery path or whether it has become a preserved historical branch that will never regain ordinary write rights through the failed rejoin path. `[REF-0454]` `[REF-0469]` `[REF-0463]` `[REF-0464]` `[REF-0470]`

---

## 2. Witness replacement now owes one public `WRI-1` object plus minimum operator-independence tests

The archive now fixes one compact rule for witness replacement in long-lived supersession families: every non-routine witness substitution must publish one machine-carrying witness-replacement object called `WRI-1`.

### A. Minimum `WRI-1` fields

Every public witness substitution must expose at least:

- `wri_id`
- `family_anchor_id`
- `replaced_witness_id`
- `replacement_witness_id`
- `replacement_reason_class` (`routine-rotation`, `conflict-recusal`, `outage`, `compromise`, `jurisdictional-disqualification`, `correlated-failure`, `other-publicly-justified`)
- `temporary_or_full`
- `replacement_started_at`
- `replacement_review_due_at`
- `comparable_competence_ref`
- `independence_attestations[]`
- `conflict_screen_ref`
- `degraded_quorum_authorized_until`
- `recovery_share_rotation_ref`
- `incident_link_refs[]`
- `public_notes`

The function of `WRI-1` is narrow. It does not reopen the merits of the underlying family dispute. It proves who was replaced, why, whether the replacement is temporary or full, what competence and independence basis justified the substitution, and when emergency degraded status must end or escalate. `[REF-0465]` `[REF-0466]` `[REF-0467]`

### B. Minimum independence tests

A replacement witness is no longer acceptable merely because a seat would otherwise go empty. The archive now requires every `WRI-1` to attest that the replacement witness:

1. has publicly documented experience, expertise, background, professional competence, and knowledge comparable to the witness role being replaced;
2. is not under the same ultimate controller, and ordinarily not under the same managed signing or publication control plane, as the witness being replaced;
3. is not drawn from the same incident-affected environment when the triggering event is compromise, outage, or correlated infrastructure failure;
4. has passed a conflict screen showing no direct material interest in the family outcome, no unresolved role conflict, and no current dependence likely to bias review toward continued approval or continued suppression; and
5. is substituting for one role only, with no proxy voting, no dual counting of primary plus alternate, and a public record of when the substitution began and ended.

These are minimum tests, not an exhaustive ethics code. The point is to keep emergency continuity from becoming a disguised route back to one effective signing center. `[REF-0456]` `[REF-0457]` `[REF-0465]` `[REF-0466]` `[REF-0467]`

### C. Emergency recovery is permitted, but only through declared degraded status and forced post-incident rotation

If a family temporarily loses enough qualified witnesses that an immediately compliant replacement cannot be installed, the publishing authorities may enter a declared `degraded-witness` state. That state is narrow: it preserves historical readability and already-published safety labels, but it should not silently restore ordinary write confidence. A `degraded-witness` state must publish `degraded_quorum_authorized_until`, should ordinarily last no more than 72 hours without independent extension, and must trigger fresh recovery-share rotation plus a new signed checkpoint once a compliant replacement or reserve cohort is installed. `[REF-0456]` `[REF-0457]` `[REF-0466]`

### D. Correlated failure blocks same-cluster substitution unless the system publicly downgrades

When several witnesses fail for the same broad cause class — for example, the same cloud region, the same contractor-operated key service, or the same steward-controlled evidence transport — same-cluster substitution is no longer treated as ordinary continuity. The system must either source a replacement from outside the correlated-failure cluster or declare `degraded-witness` status and route the family through the read-only safety posture already fixed elsewhere in canon. `[REF-0457]` `[REF-0465]` `[REF-0467]`

---

## 3. Chronic reciprocal-credit default now nets through a non-transferable typed deficiency ledger rather than lender control

The archive now fixes one compact rule for chronic reciprocal-credit default: every material uncured shortfall becomes a non-transferable typed deficiency entry in a reserve-default ledger called `RDN-1`.

### A. Minimum `RDN-1` fields

Every chronic default record must expose at least:

- `rdn_id`
- `defaulting_authority_id`
- `creditor_authority_ids[]`
- `typed_deficiency_units[]`
- `deficiency_basis_window`
- `notice_started_at`
- `cure_due_at`
- `netting_cap_per_cycle`
- `expiry_or_discharge_rule`
- `conversion_table_version`
- `current_default_state` (`noticed`, `under-cure`, `netting`, `restricted-borrowing`, `suspended`, `discharged`)
- `governance_nonconversion_marker`
- `public_explanation`

The function of `RDN-1` is also narrow. It records a public, typed, time-bounded shortfall that can be cured or partially netted later. It does not convert into a lien over the defaulting authority's governance. `[REF-0446]` `[REF-0447]` `[REF-0451]` `[REF-0452]` `[REF-0453]` `[REF-0468]`

### B. Only future excess typed capacity may be netted

The archive now forbids creditors from netting against the defaulting authority's current minimum floor. Netting may apply only to future positive contribution above the current floor and only within the same typed category or a predeclared public conversion table. In ordinary periods, no more than one-half of newly earned reciprocal credit in a cycle should be automatically set off, so recovery remains possible without forcing a permanent dependent relation. `[REF-0451]` `[REF-0452]` `[REF-0453]` `[REF-0446]` `[REF-0447]` `[REF-0468]`

### C. Deficiency may not buy governance rights

Outstanding deficiency units may not be sold, assigned as a governance asset, used to claim witness seats, used to demand substitute-panel placement, or counted as extra voting weight in reserve governance. Creditors may recover declared support value on the published netting ladder, but they may not convert emergency support into durable rule over the recipient. `[REF-0446]` `[REF-0447]` `[REF-0461]`

### D. Chronic default now carries automatic future-cycle make-up pressure

If a defaulting authority reaches the end of a compliance window without enough matching contribution to cure a shortfall, the archive now requires automatic future-cycle make-up pressure rather than indefinite negotiation alone. That pressure is bounded: it uses typed deficiency entries, capped per-cycle setoff, and published status changes, but it does not depend on creditor discretion. Persistent uncured shortfall therefore becomes a public systems problem, not a private dominance opportunity. `[REF-0462]` `[REF-0468]`

### E. Holding caps still constrain creditors after netting

The archive's existing anti-hoarding logic survives chronic default. No creditor may use netting to exceed the holding caps or influence caps already fixed for reciprocal credits and reserve governance. A lender who would exceed those caps must take discharge through neutral reduction or public write-off, not through extra control. `[REF-0461]` `[REF-0446]`

---

## 4. Failed rejoin now distinguishes `read-only-recoverable` from `historical-branch-retired`

The archive now fixes one compact public state distinction after read-only split failure.

### A. `read-only-recoverable`

A branch is `read-only-recoverable` when ordinary writes remain blocked, but a live rejoin path still exists. At minimum, the branch still has an open review route, an identified convergence object or candidate successor, and no final determination that safe convergence is impossible. Queries must preserve the branch as a live frozen line with historical readability, citation stability, and visible linkage to the active review path. `[REF-0454]` `[REF-0469]`

### B. `historical-branch-retired`

A branch becomes `historical-branch-retired` when the read-only freeze is no longer reversible through the failed rejoin path. This state does **not** authorize silent deletion. The branch remains queryable, citable, and linked to any bridge or successor surface, but it no longer advertises a live path back to ordinary writes through the failed rejoin process. `[REF-0463]` `[REF-0464]` `[REF-0470]` `[REF-0442]` `[REF-0443]`

### C. Minimum retirement test

A publishing authority may move a branch from `read-only-recoverable` to `historical-branch-retired` only when all three conditions are met:

1. the competent review route has closed, timed out after declared opportunity, or made a public determination that rejoin is unsafe or unsupported;
2. the branch's last shared checkpoint and divergence basis are preserved in the family graph and any successor or bridge references are published; and
3. the retirement object states whether the branch ends in `no-successor`, `bridge-only`, or `successor-linked` historical status.

This prevents quiet collapse from "temporarily frozen" to "gone." `[REF-0454]` `[REF-0469]` `[REF-0463]` `[REF-0464]` `[REF-0470]`

### D. Ordinary discovery defaults should prefer the live line without erasing the retired line

Ordinary current-state queries should prefer the surviving live line or declared canonical successor, but historical, citation-based, and challenge-related queries must still resolve the retired branch. Historical retirement is therefore a discovery default, not an erasure event. `[REF-0442]` `[REF-0443]` `[REF-0463]` `[REF-0464]` `[REF-0470]`

---

## 5. Operational consequences

### A. Witness continuity is now measurable rather than rhetorical

Operators can no longer satisfy the archive by saying that a replacement was "qualified" in the abstract. They must show comparable competence, conflict screening, independence from the failed control cluster, and a bounded recovery path. `[REF-0465]` `[REF-0466]` `[REF-0467]`

### B. Reserve solidarity is no longer convertible into creditor rule

Mutual aid remains real, but chronic support no longer ripens into informal sovereignty. Default is visible, future-cycle make-up is real, and netting pressure is automatic and typed — yet governance remains plural. `[REF-0446]` `[REF-0447]` `[REF-0451]` `[REF-0452]` `[REF-0453]` `[REF-0461]` `[REF-0462]` `[REF-0468]`

### C. Frozen disagreement now ends in a stable public state instead of indefinite suspense

The public can now tell whether a read-only branch is still under active recovery or has become a permanently historical branch. That makes search defaults, citation, and successor routing legible without sacrificing the archive's anti-disappearance rule. `[REF-0454]` `[REF-0469]` `[REF-0463]` `[REF-0464]` `[REF-0470]`

---

## Cross-links

- `docs/20-world-design/research-supersession-graph-witness-diversity-reciprocal-credit-expiry-and-split-read-only-rejoin.md` fixes the immediately prior layer that this surface now sharpens.
- `docs/20-world-design/research-supersession-graph-integrity-heterogeneous-reserve-scoring-and-pending-review-divergence-thresholds.md` fixes the proof, heterogeneous-scoring, and divergence-threshold layer beneath this one.
- `docs/20-world-design/research-compromise-supersession-graphs-reserve-default-cure-and-successor-promotion-stay-effects.md` fixes the additive graph, default-ladder, and pending-review layer beneath both.
- `docs/20-world-design/independence-packets-appointment-conflict-recusal-funding-and-domination-review.md` fixes the archive's wider anti-capture discipline that constrains witness replacement and reserve governance.
- `docs/20-world-design/record-challenge-packets-correction-notice-markers-and-secret-blacklist-review.md` fixes the archive's wider rule against silent status cleanup.

---

## Bottom line

A personhood world should not let witness replacement quietly repopulate a "diverse" graph-signing set with the same operator cluster, should not let chronic reciprocal-credit default harden into lender rule, and should not let failed read-only rejoin linger in one vague frozen state. The archive therefore now fixes one more compact rule: **witness replacement now owes explicit operator-independence, comparable-competence, no-proxy, and forced-recovery tests; chronic reciprocal-credit default now nets only against future typed excess capacity through a non-transferable deficiency ledger; and failed rejoin now ends in a visible distinction between `read-only-recoverable` and `historical-branch-retired`, preserving history without pretending convergence is still live.** `[REF-0456]` `[REF-0457]` `[REF-0465]` `[REF-0466]` `[REF-0467]` `[REF-0446]` `[REF-0447]` `[REF-0451]` `[REF-0452]` `[REF-0453]` `[REF-0461]` `[REF-0462]` `[REF-0468]` `[REF-0454]` `[REF-0469]` `[REF-0463]` `[REF-0464]` `[REF-0470]`
