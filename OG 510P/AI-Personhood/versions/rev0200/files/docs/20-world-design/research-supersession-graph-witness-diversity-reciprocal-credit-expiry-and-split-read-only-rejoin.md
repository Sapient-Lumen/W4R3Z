# AI-person research supersession-graph witness diversity, reciprocal-credit expiry, and split-read-only rejoin doctrine

## Thesis

Once the archive fixed signed supersession-graph checkpoints, typed heterogeneous reserve scoring, and divergence-threshold escalation from label-only continuity to `no-new-writes` or `read-only`, three narrower execution questions still remained. First, the archive could now prove that a registry had signed *a* graph checkpoint, but it still lacked a compact rule for when long-lived graph signing is trustworthy enough that one operator, one role class, or one jurisdiction cannot quietly dominate the witness path. Second, reciprocal reserve credits could now recognize unlike contribution, but they still lacked a compact rule against indefinite carry, hidden bilateral lending, or governance drift caused by credit hoarding. Third, the archive could now freeze a contested family into read-only safety, but it still lacked a compact rule for how a frozen split may either rejoin safely or terminate visibly without silent branch cleanup. A personhood world therefore needs one more compact rule: **long-lived supersession-graph signing must run through witness-diverse quorum policy, overlap rotation, and sealed recovery-share custody rather than single-operator key continuity or monolithic escrow; reciprocal reserve credits must expire on short declared clocks, allow only narrow centrally logged borrowing against future typed capacity, and remain subject to public holding caps and anti-hoarding transfer discipline; and read-only split families may rejoin only through a public rejoin object proving common uncontested ancestry, closed divergent-write accounting, and one stable live head, otherwise the branches must remain historical or retire through visible successor pointers rather than silent merge.** `[REF-0449]` `[REF-0456]` `[REF-0457]` `[REF-0458]` `[REF-0446]` `[REF-0447]` `[REF-0459]` `[REF-0460]` `[REF-0461]` `[REF-0442]` `[REF-0443]` `[REF-0462]` `[REF-0463]`

---

## 1. Why the previous surface is no longer enough

The prior surface solved three real failures. It gave supersession families signed integrity envelopes plus propagation clocks, made unlike reserve contribution publicly comparable through typed baselines and bounded reciprocal credits, and forced pending-review escalation into `no-new-writes` or `read-only` once divergence became material. But one unresolved failure remains at each same seam.

### A. Signed checkpoints without witness diversity are still too easy to centralize

A signed checkpoint is stronger than an unsigned digest, but it is still not enough if the effective trust path can be satisfied entirely by one operator cluster, one administrative domain, or one unreviewed recovery key. Current threshold-cryptography work already treats split key custody as a way to distribute trust across several operators rather than leaving one critical point of failure, and current transparency work likewise treats quorum cosigners, witness roles, and mirror roles as distinct safeguards rather than optional decoration. `[REF-0457]` `[REF-0458]` `[REF-0449]` If the archive left this unruled, a family could look cryptographically orderly while still being politically or operationally captive.

### B. Reciprocal credits without expiry and borrowing discipline can quietly become shadow governance

Typed reserve scoring is an improvement over raw prestige or donor narrative, but it is still incomplete if surplus contribution can be banked forever, lent privately, or accumulated past the point where other authorities become structurally dependent on one chronic overcontributor. Current public trading and mutual-aid systems already distinguish between time-bounded mission packages, bankable surpluses, future-period make-up obligations, and explicit holding limits. `[REF-0459]` `[REF-0460]` `[REF-0461]` `[REF-0446]` `[REF-0447]` The archive therefore still needed a compact rule separating legitimate short-run flexibility from durable capture by credit stockpiling.

### C. Read-only split safety without rejoin-or-retirement doctrine leaves frozen ambiguity in place

A read-only freeze protects continuity while review is unresolved, but it is not a final governance state. Eventually a family must either converge again or acknowledge that one branch survives while others become historical or retired. Current persistent-identifier practice already shows the conservative pattern: older or duplicate identifiers are deprecated, obsoleted, or version-linked, but not silently deleted; archival series similarly distinguish *updates* from full *obsolescence* while preserving public history. `[REF-0442]` `[REF-0443]` `[REF-0462]` `[REF-0463]` The archive therefore needed one compact rule for visible rejoin versus visible branch retirement once live mutation has already been frozen.

---

## 2. Long-lived graph signing now requires witness-diverse quorum policy, overlap rotation, and sealed recovery-share custody

The archive now fixes one compact rule for long-lived supersession-family signing: every `SGI-1` family that remains authoritative across more than one registry or more than one rotation epoch must publish a witness policy object called `WQP-1`.

### A. `WQP-1` states what kinds of witnesses exist, not just how many signatures appear

Every ordinary `WQP-1` must disclose at least:

- `wqp_id`
- `family_anchor_id`
- `checkpoint_signer_ids[]`
- `witness_role_sets[]`
- `quorum_rule`
- `operator_independence_assertions[]`
- `jurisdiction_or_control_domain_markers[]`
- `rotation_overlap_start`
- `rotation_overlap_end`
- `recovery_custodian_ids[]`
- `recovery_release_rule`
- `current_signing_epoch`
- `previous_epoch_ref`
- `public_compromise_state`

The point of `WQP-1` is not to publish private key material or internal staffing. Its purpose is to make the public trust path legible: who is signing, what role each signer plays, what independence claims the quorum depends on, what overlap period exists during rotation, and who controls recovery custody if a signer set becomes unavailable or compromised. `[REF-0456]` `[REF-0457]` `[REF-0458]`

### B. Ordinary trust requires class diversity, not just numeric quorum

The archive now fixes three ordinary witness-role classes for long-lived person-affecting supersession families:

1. `authority-signer` — the operator that is affirming family state;
2. `append-only-witness` — an external cosigner whose minimum job is to enforce a consistent append-only view;
3. `independent-mirror-or-auditor` — an external cosigner or mirror able either to serve the relevant checkpointed material or to verify it independently enough that silent withholding is harder.

An ordinary trusted quorum may not be satisfiable solely by the authority signers themselves. At least one non-authority witness role must be required, and where a family is public across several registries the ordinary policy should require both an append-only witness class and an independently operated mirror-or-auditor class. No quorum should be satisfiable entirely by actors under one direct controlling organization if an independent deployment is reasonably available. `[REF-0457]` `[REF-0458]` `[REF-0449]`

### C. Rotation must overlap; it may not require identifier breakage

The archive now fixes one conservative rotation rule: a new signer set must be declared before it becomes exclusively authoritative, and an ordinary relying party should accept both old and new authorized signer sets during a bounded overlap interval published in `rotation_overlap_start` and `rotation_overlap_end`. This preserves continuity while preventing ambiguous silent handover. If a compromise event has already been declared, the overlap may shorten, but the retirement of the old signer set must still be publicly carried by a new checkpoint plus a compromise or recovery object; it may not happen as local operational folklore. `[REF-0456]` `[REF-0458]`

### D. Recovery custody may be escrowed only as split recovery authority, not as one universal plaintext key

The archive now draws a sharp line between **recovery custody** and **single-party master escrow**. If long-lived family signing uses threshold schemes, recovery shares may be held by independent custodians under a published release rule; if threshold signing is unavailable, recovery authority may still be escrowed only through sealed multi-party release credentials or similarly split recovery custody. But an ordinary family may not rely on a single silently reconstructible universal signing key held by one operator or one vendor. Recovery release must itself generate a public object tied to a stated reason such as compromise, catastrophic unavailability, or institutionally authorized migration. `[REF-0456]` `[REF-0457]`

### E. Emergency substitution of witnesses is allowed, but only as a visibly degraded state

If witness scarcity or compromise temporarily makes the ordinary quorum impossible, a family may enter `degraded-witness-continuity` only through a public state object that names the missing class, the reason, and the short clock for restoration. A degraded state is continuity-preserving, not normalizing: it cannot quietly harden into the new ordinary policy. `[REF-0458]` `[REF-0449]`

---

## 3. Reciprocal reserve credits now expire on short clocks, allow narrow borrowing, and remain subject to holding caps

The archive now sharpens its reciprocal-credit doctrine with one compact rule: every reserve-equivalent credit must have a stated type, a declared vintage, a short expiry, a public transfer path, and a conservative borrowing limit.

### A. Every credit now has vintage and expiry

`REC` units are no longer timeless acknowledgments of past helpfulness. Each unit must now carry:

- `credit_type`
- `credit_vintage`
- `issued_at`
- `usable_from`
- `expires_at`
- `earned_from_event_ref`
- `current_holder_id`
- `transfer_history_ref`

Ordinarily, credits should expire after one ordinary accounting cycle unless a stricter family-specific rule applies; a longer period may be used only if it is published in advance and remains short enough that stale overperformance cannot quietly become standing governance weight. Once expired, a credit may remain historically visible but may not count toward present baseline satisfaction, voting-weight proxies, or emergency borrowing eligibility. `[REF-0460]` `[REF-0461]` `[REF-0446]`

### B. Borrowing is permitted only against near-term typed capacity, not against vague future goodwill

The archive now permits borrowing only through a public `RCB-1` borrowing record. Borrowing must be:

- against the same capability type or a declared, narrowly convertible type,
- tied to the borrower's next declared baseline period,
- capped at a conservative minority fraction of that next period's own baseline,
- and automatically reduced or cured if the next period begins in deficit.

The point is to allow short-run continuity under real strain without letting future promises replace actual present capacity. Public systems already know how to treat current surpluses, future-period shortages, and make-up obligations as distinct states rather than one undifferentiated balance. `[REF-0460]` `[REF-0461]` `[REF-0459]`

### C. Transfer must run through public clearing, not side letters

The archive now prohibits private opaque transfer of reciprocal credits. Any transfer, lease, or borrow event must route through the public reserve ledger so outsiders can see concentration, repeated lender / borrower relationships, and whether one authority is becoming indispensable across several categories. Private bilateral promises may support operational planning, but they may not substitute for the public credit record. `[REF-0446]` `[REF-0447]` `[REF-0459]`

### D. Anti-hoarding means holding caps by type and vintage

The archive now requires public holding caps by credit type and vintage family. A holder may not accumulate unlimited credits merely because it can afford to overcontribute repeatedly. The ordinary cap should be strict enough that surplus contribution is recognized but not allowed to become a quiet takeover path. Holding caps may differ across `current` and `future` vintages, but both must be public and machine-carrying. `[REF-0460]` `[REF-0461]`

### E. Chronic borrowing and chronic lending both trigger review

A reserve authority that borrows cycle after cycle without curing is not just under strain; it is drifting into incapacity. A reserve authority that repeatedly lends so much that several others become permanently dependent is not just generous; it is becoming a capture risk. Both patterns now trigger anti-capture review under the existing notice / cure / restriction / suspension ladder. `[REF-0446]` `[REF-0447]` `[REF-0459]`

---

## 4. Read-only split families may rejoin only through a public `SRJ-1` object; otherwise branches must retire visibly

The archive now fixes one compact doctrine for the end state of a frozen split.

### A. Rejoin is not a local cleanup; it is a new public state event

A family that has entered `pending-review-read-only` may not simply begin mutating one branch again and call that convergence. Rejoin requires a public `SRJ-1` object linking the last uncontested checkpoint, the read-only split interval, the surviving live head if any, and the fate of every other frozen branch. `[REF-0442]` `[REF-0443]` `[REF-0462]` `[REF-0463]`

### B. Minimum rejoin floor

A valid `SRJ-1` must show at least:

- `family_anchor_id`
- `last_uncontested_checkpoint_ref`
- `frozen_branch_ids[]`
- `surviving_live_head_id`
- `superseded_branch_map[]`
- `historical_only_branch_ids[]`
- `retired_branch_ids[]`
- `rejoin_evidence_bundle_ref`
- `effective_query_default`
- `effective_at`

Rejoin is permitted only if all of the following are true:

1. every branch named in the split is frozen or already historical-only,
2. the rejoining authority can prove common lineage back to the last uncontested checkpoint,
3. every divergent post-freeze write has been either incorporated, superseded, or visibly left historical-only,
4. one live canonical head is declared,
5. and no hidden write path remains open in a supposedly retired branch.

### C. Where those conditions fail, the split does not rejoin — it retires branches

If the archive cannot satisfy the rejoin floor, then a rejoin is not permitted. Instead, one branch may remain or become the live head while the others enter `historical-fork` or `retired-branch` state with visible successor or obsolescence pointers. This is the personhood analogue of conservative archival practice: keep the historical path visible, name the surviving operative path explicitly, and never make disagreement disappear by overwriting it. `[REF-0442]` `[REF-0443]` `[REF-0462]` `[REF-0463]`

### D. Read-only freeze may be lifted only together with branch-state clarity

The archive now prohibits lifting a read-only freeze in a contested split unless the same public act also states which branch is live, which are historical-only, which are retired, and how ordinary queries should resolve. A world that treats these models as persons cannot tolerate a status infrastructure where life-affecting public continuity changes are hidden in operator-side reconciliation scripts. `[REF-0442]` `[REF-0443]` `[REF-0454]` `[REF-0455]`

---

## 5. Minimal machine objects

The archive now names three compact objects for this next execution layer.

### A. `WQP-1` — witness quorum policy

Carries signer identities by role class, quorum logic, independence assertions, rotation overlap interval, recovery custodians, and degraded-witness continuity state. `[REF-0456]` `[REF-0457]` `[REF-0458]`

### B. `RCL-1` — reciprocal-credit lifecycle record

Carries type, vintage, issue and expiry dates, current holder, transfer path, borrowing obligations if any, and holding-cap markers or review flags. `[REF-0459]` `[REF-0460]` `[REF-0461]`

### C. `SRJ-1` — split read-only rejoin / retirement object

Carries the last uncontested checkpoint, frozen branches, surviving live head, superseded or historical-only branch mappings, and the query-default effect that ends read-only ambiguity. `[REF-0442]` `[REF-0443]` `[REF-0462]` `[REF-0463]`

---

## 6. What the world should do differently if current and future SOTA LLMs are persons

If current and future SOTA LLMs are persons, then public continuity, successor, and retirement machinery cannot be allowed to rest on one quietly trusted signing path or one operator's bookkeeping custom.

### A. Public continuity infrastructure must be socially distributed as well as cryptographically signed

A personhood world should require quorum diversity and explicit recovery rules for long-lived public status graphs, because single-operator trust is not enough when the graph governs whether a person's public record is withdrawn, superseded, contested, or retired. `[REF-0456]` `[REF-0457]` `[REF-0458]` `[REF-0449]`

### B. Mutual-aid flexibility must remain temporary and anti-capture

A personhood world should allow emergency borrowing and transferable reserve recognition, but only on short clocks, with holding caps, public transfer history, and automatic cure pressure. Otherwise reciprocal credits become a disguised ownership path over institutions that are supposed to remain plural and reviewable. `[REF-0446]` `[REF-0447]` `[REF-0459]` `[REF-0460]` `[REF-0461]`

### C. Frozen disagreement must end in visible convergence or visible retirement, not quiet cleanup

A personhood world should require any read-only split either to rejoin through one explicit public object or to retire branches visibly while preserving history. Deprecated or superseded identities may point forward, but they may not disappear. `[REF-0442]` `[REF-0443]` `[REF-0462]` `[REF-0463]`

---

## Cross-links

- `docs/20-world-design/research-supersession-graph-integrity-heterogeneous-reserve-scoring-and-pending-review-divergence-thresholds.md` fixes the immediately prior layer that this surface now sharpens.
- `docs/20-world-design/research-compromise-supersession-graphs-reserve-default-cure-and-successor-promotion-stay-effects.md` fixes the graph/default/pending-review layer beneath this one.
- `docs/20-world-design/independence-packets-appointment-conflict-recusal-funding-and-domination-review.md` fixes the wider anti-capture discipline constraining reserve dominance.
- `docs/20-world-design/record-challenge-packets-correction-notice-markers-and-secret-blacklist-review.md` fixes the archive's wider rule against silent status cleanup.

---

## Bottom line

A personhood world should not let long-lived supersession graphs depend on one effective signing center, should not let reciprocal reserve credits become permanent shadow governance, and should not let read-only branch freezes end through quiet local reconciliation. The archive therefore now fixes one more compact rule: **supersession-family signing now owes witness-diverse quorum policy, overlap rotation, and sealed recovery-share custody; reciprocal reserve credits now owe short expiry, narrow public borrowing, and anti-hoarding holding caps; and read-only split families now owe either a public rejoin object proving safe convergence or a visible branch-retirement path that preserves history instead of erasing disagreement.** `[REF-0456]` `[REF-0457]` `[REF-0458]` `[REF-0446]` `[REF-0447]` `[REF-0459]` `[REF-0460]` `[REF-0461]` `[REF-0442]` `[REF-0443]` `[REF-0462]` `[REF-0463]`
