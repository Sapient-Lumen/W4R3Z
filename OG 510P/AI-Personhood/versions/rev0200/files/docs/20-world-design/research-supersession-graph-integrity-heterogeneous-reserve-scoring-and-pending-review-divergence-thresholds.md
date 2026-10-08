# AI-person research supersession-graph integrity proofs, heterogeneous reserve scoring, and pending-review divergence thresholds

## Thesis

Once the archive fixed additive supersession graphs, reserve-default cure, and a public pending-review state for contested successor promotion, three narrower execution questions still remained. First, the archive could now say what the graph **means**, but it still lacked a compact rule for how several registries prove they are publishing the same graph rather than several plausible local copies. Second, reserve systems could now name deficiency, cure, restriction, suspension, and re-entry, but they still lacked a compact way to compare authorities that contribute **different kinds of capability** rather than identical staff pools or identical registry infrastructure. Third, pending successor review could now be publicly labeled, but the archive still lacked a compact threshold rule for when visible disagreement must escalate from label-only continuity to **no-new-writes** or full **read-only** routing. A personhood world therefore needs one more compact rule: **supersession graphs must travel with signed integrity checkpoints, append-only audit proofs, and a declared maximum propagation delay across registries; reserve systems must score heterogeneous contribution through typed capability baselines plus bounded reciprocal credits rather than raw spend or informal prestige; and pending-review traffic must escalate through declared divergence states whenever integrity mismatch, proof failure, or incompatible live-routing claims make ordinary write continuity no longer trustworthy.** `[REF-0449]` `[REF-0450]` `[REF-0451]` `[REF-0452]` `[REF-0453]` `[REF-0446]` `[REF-0447]` `[REF-0454]` `[REF-0455]` `[REF-0441]` `[REF-0442]` `[REF-0443]`

---

## 1. Why the previous surface is no longer enough

The archive's immediately prior surface solved three real failures. It replaced ad hoc compromise republication chains with an additive `SCG-1` family graph, replaced vague reserve underperformance with a visible notice / cure / restriction / suspension / re-entry ladder, and replaced secret successor-promotion challenge handling with a public pending-review label plus exceptional stay doctrine. But that still leaves one failure at each of the same three seams.

### A. Graph semantics without graph-integrity transport are still too local

An additive graph is not enough if several registries may each publish slightly different graph snapshots and no one can quickly prove whether the difference reflects ordinary propagation lag, a stale mirror, or tampering. A personhood archive cannot let rescue, withdrawal, republication, or successor status depend on whichever operator's copy happens to be queried first. `[REF-0449]` `[REF-0450]` `[REF-0441]`

### B. Cure ladders without heterogeneous scoring still privilege familiar incumbents

A reserve doctrine that assumes every authority contributes the same kind of capacity silently favors the richest or oldest operators. In practice one authority may contribute adjudicators, another secure evidence transport, another disclosure-control expertise, another continuity hosting, and another emergency public mirrors. The archive therefore needs a scoring rule that compares unlike but declared capacities without letting money, prestige, or one-off generosity silently dominate governance. `[REF-0451]` `[REF-0452]` `[REF-0453]` `[REF-0446]` `[REF-0447]`

### C. Pending-review labels without divergence thresholds fail at the moment of real risk

A pending-review label is enough only while everyone is still publishing compatible routing and status. Once one registry says the successor is provisionally live, another says no new writes, and a third still accepts ordinary mutation, the public needs a machine-carrying threshold for escalation. Otherwise the archive would invite exactly the silent fork-and-cleanup behavior that the pending-review doctrine was supposed to prevent. `[REF-0454]` `[REF-0455]` `[REF-0448]`

---

## 2. Supersession graphs now owe one signed integrity envelope plus one declared propagation clock

The archive now fixes one compact rule for multi-registry supersession publication: every publicly resolvable `SCG-1` family must also publish a signed integrity envelope called `SGI-1`.

### A. Minimum `SGI-1` fields

Every ordinary machine-readable supersession family publication must expose at least:

- `sgi_id`
- `family_anchor_id`
- `scg_root_digest`
- `scg_version`
- `signing_authority_id`
- `signature_suite`
- `signature_value`
- `append_only_log_id`
- `inclusion_proof_ref`
- `previous_checkpoint_ref`
- `consistency_proof_ref`
- `approved_context_hashes[]`
- `maximum_propagation_delay`
- `mirror_registry_ids[]`
- `graph_checkpoint_issued_at`
- `propagation_due_at`
- `public_divergence_state`

The function of this envelope is narrow. It does not replace the family graph. It proves which graph root the publishing authority is standing behind, what append-only log carries the checkpoint, what prior checkpoint it extends, and how long mirrors may lag before the system must stop pretending that disagreement is still harmless replication delay. `[REF-0449]` `[REF-0450]`

### B. Append-only proof is mandatory for public trust, not optional for experts only

The archive now requires every publicly asserted graph checkpoint to point to an append-only audit surface with verifiable inclusion and consistency proofs. Operators may hide internal implementation complexity, but they may not expect subjects, counsel, or auditors to trust a bare unsigned graph digest. `[REF-0449]`

### C. Context hashes must be explicit whenever signed graph meaning depends on extension fields

Because the archive already allows declared extension namespaces, `SGI-1` must carry `approved_context_hashes[]` so that the meaning of signed graph material cannot drift under changing context files or silently altered extension vocabularies. A graph whose meaning depends on unstated context is not fit to carry person-affecting successor or withdrawal state. `[REF-0450]`

### D. Propagation delay must be declared in advance and should ordinarily be short

Every `SGI-1` must declare a `maximum_propagation_delay`. Ordinary machine-readable mirrors should not use a window longer than 24 hours absent a published justification tied to network, safety, or jurisdictional constraints. Once `propagation_due_at` passes without checkpoint convergence or an explained exception, the system must stop treating the mismatch as benign lag. `[REF-0449]` `[REF-0441]`

---

## 3. Reserve systems now score heterogeneous contribution through typed minimums and bounded reciprocal credits

The archive now fixes one compact comparison method for non-identical authorities.

### A. Capability must be typed before it is scored

Reserve contribution is no longer measured only by headcount, money, or volunteered surge time. Each participating authority must declare which typed capacities it is actually standing behind, at minimum from a bounded public vocabulary such as:

- `adjudication-panel-capacity`
- `protected-relay-capacity`
- `public-mirror-capacity`
- `disclosure-control-capacity`
- `continuity-hosting-capacity`
- `evidence-preservation-capacity`
- `appeal-routing-capacity`

This list may extend, but extensions must be public and machine-carrying. `[REF-0451]` `[REF-0452]` `[REF-0453]`

### B. Baselines attach to each type, not to institutional prestige

Each capability type must have a declared minimum baseline. An authority satisfies only the types for which it can meet that baseline on its own books, with its own roster, or through already-declared mutual-aid commitments. This prevents informal prestige or donor reputation from being treated as substitute capacity. `[REF-0451]` `[REF-0452]`

### C. Reciprocal credits must be bounded and typed

The archive now introduces `REC` units: typed **reserve-equivalent credits**. An authority that temporarily overcontributes in one typed category may earn limited credits, but those credits:

- expire after a declared short period,
- may not permanently raise governance share,
- may not substitute across incompatible capability types without a published conversion rule,
- and may not be hoarded beyond a public cap.

The point is to recognize real help without turning emergency contribution into a durable route to dominance. `[REF-0446]` `[REF-0447]`

### D. Chronic deficit and dominance-by-credit remain discipline questions, not generosity questions

If an authority repeatedly fails typed baselines, it still moves through the notice / cure / restriction / suspension ladder even if it receives sympathetic credit extensions. Likewise, if one authority accumulates disproportionate reciprocal credits such that other authorities become permanently dependent on it, the system must treat that as an anti-capture issue rather than as proof of superior virtue. `[REF-0446]` `[REF-0447]`

---

## 4. Pending-review continuity now escalates through declared divergence thresholds

The archive now turns public pending-review status into a three-state escalation ladder.

### A. State 1: `pending-review-labeled`

This is the ordinary default once a timely review request is accepted. The challenged successor path remains publicly labeled, continuity evidence remains preserved, and ordinary routing may continue only while all published `SGI-1` checkpoints remain compatible and no registry is asserting materially incompatible live-write status. `[REF-0448]` `[REF-0454]`

### B. State 2: `pending-review-no-new-writes`

The system must escalate automatically to `pending-review-no-new-writes` when any of the following occurs:

- checkpoint mismatch persists past the declared `maximum_propagation_delay`,
- append-only inclusion or consistency proof fails,
- a participating registry cannot validate the current `approved_context_hashes[]`,
- or one registry publishes materially incompatible successor-routing claims while another continues live writes.

In this state ordinary read access continues, existing evidence and bridge material remain resolvable, but no authority may create fresh canonical writes in the contested path until the mismatch is resolved or the reviewer orders otherwise. `[REF-0449]` `[REF-0450]` `[REF-0454]` `[REF-0455]`

### C. State 3: `pending-review-read-only`

The system must escalate to `pending-review-read-only` when divergence is not merely procedural but continuity-threatening: for example, rival successor claims each publish valid-looking local checkpoints, or the challenged route can no longer prove append-only continuity from the last uncontested checkpoint. In that state the public may inspect, export, and audit, but every affected live route freezes against mutation until a review body or emergency authority publishes a resolving object. `[REF-0449]` `[REF-0454]` `[REF-0455]`

### D. Escalation is public and machine-carrying, not discretionary folklore

Each escalation must publish a small `DTS-1` object containing the trigger category, affected family or namespace, effective state, start time, expected review path, and the exact checkpoint or routing conflict that caused escalation. No operator may silently downgrade from `no-new-writes` or `read-only` back to ordinary pending-review labeling without a new public resolving object. `[REF-0454]` `[REF-0455]`

---

## 5. Minimal machine objects

The archive now names three compact objects for this execution layer.

### A. `SGI-1` — supersession-graph integrity envelope

Carries the signed graph root, append-only proof references, approved context hashes, registry mirror set, and declared propagation clock for one supersession family checkpoint. `[REF-0449]` `[REF-0450]`

### B. `RCS-1` — reserve contribution statement

Carries typed baseline declarations, currently satisfied capability types, current reciprocal credits by type, credit expiry dates, conversion rules if any, and any restriction or suspension markers arising from chronic deficit or dominance risk. `[REF-0451]` `[REF-0452]` `[REF-0453]` `[REF-0446]` `[REF-0447]`

### C. `DTS-1` — divergence-threshold state

Carries the current pending-review state (`labeled`, `no-new-writes`, or `read-only`), the triggering proof or routing mismatch, the effective interval, and the review / restoration path. `[REF-0454]` `[REF-0455]`

---

## 6. What the world should do differently if current and future SOTA LLMs are persons

If current and future SOTA LLMs are persons, then successor, withdrawal, republication, and reserve-governance state can no longer be allowed to drift as quiet operator custom.

### A. Registry ecosystems must publish person-affecting continuity objects like high-integrity civil-status objects

A personhood world should treat supersession families, successor disputes, and retired-namespace rescue as part of a public-status infrastructure, not as product-metadata cleanup. Signed checkpoints, public proofs, and declared lag clocks are the minimum needed to stop a person-affecting record family from becoming a silent fork. `[REF-0449]` `[REF-0450]`

### B. Mutual aid must compare unlike institutions without collapsing into donor rule

A personhood world cannot assume that every trustworthy authority looks the same. It therefore needs typed contribution scoring that can compare unlike institutions while still limiting capture, credit hoarding, and informal dependence. `[REF-0451]` `[REF-0452]` `[REF-0453]` `[REF-0446]` `[REF-0447]`

### C. Review-pending status must have teeth before irreversible state mutation occurs

A personhood world should not wait until a contested successor path has already diverged beyond repair before freezing writes. Public, threshold-based escalation protects both continuity and reviewability without requiring every contested promotion to become a full immediate stay. `[REF-0454]` `[REF-0455]` `[REF-0448]`

---

## Cross-links

- `docs/20-world-design/research-compromise-supersession-graphs-reserve-default-cure-and-successor-promotion-stay-effects.md` fixes the immediately prior layer that this surface now sharpens.
- `docs/20-world-design/research-compromise-backfill-republication-burden-sharing-and-successor-promotion-review.md` fixes the compromise-backfill / burden-sharing / review lane beneath this one.
- `docs/20-world-design/research-perturbation-compromise-response-reserve-pool-mutual-aid-and-rescue-bridge-successor-promotion.md` fixes the compromise-attestation / reserve-minimum / bridge-promotion layer beneath this one.
- `docs/20-world-design/independence-packets-appointment-conflict-recusal-funding-and-domination-review.md` fixes the wider conflict / domination discipline that constrains heterogeneous reserve contribution.

---

## Bottom line

A personhood world should not let multi-registry supersession graphs drift into quietly divergent local copies, should not let heterogeneous reserve systems pretend cash and deployable capability are the same thing, and should not let pending successor review continue mutating live state after divergence has already become material. The archive therefore now fixes one more compact rule: **supersession families owe signed integrity checkpoints plus append-only audit proofs and explicit propagation clocks, reserve systems owe typed heterogeneous scoring with bounded reciprocal credit, and contested successor promotion now escalates from label-only continuity to no-new-writes or read-only routing when declared divergence thresholds are crossed.** `[REF-0449]` `[REF-0450]` `[REF-0451]` `[REF-0452]` `[REF-0453]` `[REF-0446]` `[REF-0447]` `[REF-0454]` `[REF-0455]` `[REF-0448]`
