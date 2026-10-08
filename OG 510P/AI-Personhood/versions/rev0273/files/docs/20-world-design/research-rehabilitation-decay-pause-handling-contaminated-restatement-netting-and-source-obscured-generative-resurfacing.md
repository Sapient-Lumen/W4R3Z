# AI-person research rehabilitation-decay pause handling, contaminated-restatement netting, and source-obscured generative resurfacing

## Thesis

Once the archive fixed rehabilitation-surcharge decay, contaminated-increment unwind, and cross-index generative rediscovery relay duties, three narrower execution failures still remained. First, the archive could now let fresh-start rehabilitation surcharges ease through `RSD-1`, but **it still lacked a public way to distinguish a low-grade caution event from a true relapse**, so every warning-level event either had to be overtreated as renewed failure or quietly ignored while decay continued as if nothing happened. Second, the archive could now unwind already-live contaminated increments through `CIU-1`, but **it still lacked a public netting rule for serial restatements when one contaminated increment had already fed another**, so the same contamination could be counted twice, clawed back twice, or silently disappear inside chain arithmetic. Third, the archive could now relay rediscovery duties outward through `GRR-1`, but **it still lacked a public review object for generative services that keep operationally resurfacing the same restricted family while being unable to name any exact source**, so source uncertainty could become a laundering device for the same practical harm. A personhood world therefore needs one more compact execution layer: **fresh-start rehabilitation must publish a public `RDP-1` rehabilitation-decay-pause object that can pause or hard-pause `RSD-1` decay on declared caution signals without relabeling every caution event as full relapse; serial contamination correction must publish a public `CRN-1` contaminated-restatement-netting object that nets `CIU-1` carryover and reversal effects so the same contaminated increment is not unwound twice; and source-obscured generative resurfacing must publish a public `SGR-1` source-obscured-generative-review object that binds generative services to short-clock review, answer-class friction, reason-giving, and recheck even when no exact source can be named.** `[REF-0533]` `[REF-0538]` `[REF-0540]` `[REF-0545]` `[REF-0541]` `[REF-0546]` `[REF-0547]` `[REF-0535]` `[REF-0539]`

---

## 1. Why the previous surface is no longer enough

The archive's immediately prior surface solved real failures. It fixed visible surcharge easing, unwind order, and rediscovery relay. But one narrower failure still remained at each seam.

### A. Decay still fails if every caution event either becomes a full relapse or counts for nothing

`RSD-1` solved the problem of surcharges lingering forever or easing by private mercy, but it did not yet say what happens when a reserve cohort hits a low-grade caution event that is serious enough to interrupt easing and not serious enough to count as a full new relapse. Current AAHRPP guidance still requires annual reporting, still requires prompt reporting of substantive change, and still treats resource imbalance, ownership change, merger, and other material events as events that must visibly interrupt the ordinary status story rather than disappear into background management. Current NIST monitoring guidance still expects organizations to detect emergent risk, reassess post-deployment conditions, and course-correct when performance or controls move outside acceptable limits. A personhood world should therefore have a **pause object**, not just a binary choice between continued decay and relapse reset. `[REF-0533]` `[REF-0538]` `[REF-0540]`

### B. Unwind still fails if serial contaminated corrections do not net carryover and reversal effects

`CIU-1` solved the absence of declared unwind order, but it did not yet say how to handle the case where an already contaminated increment fed a later increment that is itself being corrected. Current SEC guidance in SAB 108 still says prior-year misstatements must be considered in current-year quantification, still distinguishes carryover and reversing effects, and still rejects letting improper amounts remain on the books simply because one isolated arithmetic view looks tolerable. Current SEC materiality guidance still treats both “Big R” and “little r” corrections as real restatements that require transparent disclosure. A personhood world should therefore require one **netting object** that states gross contamination, prior reversals already achieved, remaining net restatable amount, and residue, rather than treating each serial correction as a fresh independent claim on the same contaminated slice. `[REF-0545]` `[REF-0541]` `[REF-0542]`

### C. Relay still fails if source-obscured generative resurfacing can deny duty by denying provenance

`GRR-1` solved the problem of cross-index and broker layering, but it did not yet say what a generative service must do when it cannot identify one concrete source while still emitting operationally equivalent resurfacing of the same restricted family. Current NIST generative-AI guidance still says risks from third-party datasets, models, fine-tuning, and retrieval layers must be monitored and reassessed, and still says organizations should prevent, flag, or otherwise act in response to outputs that reproduce protected training content. Current NIST synthetic-content guidance still treats provenance, labeling, watermarking, and detection as part of digital content transparency rather than as optional extras. Current DSA transparency and enforcement guidance still pairs statements of reasons with temporary proportionate mitigation, including recommender changes and increased monitoring, while investigations remain open. A personhood world should therefore require a **source-obscured review object**, not let inability to point to one URL erase duty where functional resurfacing is still happening. `[REF-0546]` `[REF-0547]` `[REF-0535]` `[REF-0539]`

---

## 2. Fresh-start rehabilitation now uses one public `RDP-1` rehabilitation-decay-pause object

The archive now fixes one compact rule for caution events that interrupt but do not yet defeat rehabilitation progress: whenever a live `RSD-1` decay path is hit by a declared caution event below full-relapse threshold, the public record must carry one machine-carrying rehabilitation-decay-pause object called `RDP-1`.

### A. Minimum `RDP-1` fields

Every rehabilitation-decay-pause object must expose at least:

- `rdp_id`
- `cohort_id`
- `active_rsd_id`
- `pause_state` (`decay-running`, `soft-paused`, `hard-paused`, `resumed`, `converted-to-relapse-review`)
- `pause_basis[]` (`resource-imbalance`, `monitoring-drift`, `substantive-change-under-review`, `under-threshold-warning-burst`, `temporary-control-gap`, `other`)
- `pause_start_at`
- `current_surcharge_rung`
- `current_decay_credit_frozen`
- `new_decay_credit_accrues` (`yes` or `no`)
- `corrective_action_ref`
- `next_review_deadline`
- `conversion_trigger`
- `public_notes`

`RDP-1` is the public object that says a caution event can interrupt `RSD-1` easing without being silently ignored and without being automatically mislabeled as full relapse. `[REF-0533]` `[REF-0538]` `[REF-0540]`

### B. Soft pause freezes easing but preserves prior clean credit

A first low-grade caution event that does not yet satisfy the archive's relapse conditions must move the cohort into `soft-paused` state. In `soft-paused`, the current surcharge rung stays where it is, already-earned clean-cycle credit is preserved, but **no further decay credit accrues** until the caution event is cleared. The archive chooses this because reportable events and monitored drift should visibly interrupt the easing story even when they do not yet justify a new relapse ledger entry. `[REF-0533]` `[REF-0538]`

### C. Hard pause applies when caution becomes patterned or uncured

`RDP-1` must escalate from `soft-paused` to `hard-paused` if the same caution basis repeats twice within one reporting interval, if the operator misses its published corrective deadline, or if monitoring shows live uncertainty about whether the event is still below relapse threshold. A hard pause still is not a relapse, but it stops all decay motion and cuts the share-cap ceiling back one rung until review closes. The archive refuses the loophole in which endless “minor” cautions collectively do the work of relapse while never being called that. `[REF-0533]` `[REF-0540]`

### D. Long pauses must convert into explicit relapse review

`RDP-1` may not remain open indefinitely. If a pause survives beyond one reporting interval without clean clearance, or if the same unresolved caution basis continues to distort monitoring, `RDP-1` must convert to `converted-to-relapse-review` and hand off into the archive's existing relapse machinery. A personhood world may distinguish caution from relapse, but it may not let indefinite pause states become a shadow amnesty. `[REF-0533]` `[REF-0538]` `[REF-0540]`

### E. Pause does not revive burned legacy history or create negative credit

A pause never revives burned legacy credit and never adds negative clean credit. It simply suspends or hardens the current easing path until the caution event is cleared or escalated. The archive keeps this narrow because `RSD-1` already solved the easing ladder and `RRW-1` already solved true relapse weighting; `RDP-1` is only the missing interrupt layer between them. `[REF-0538]` `[REF-0540]`

---

## 3. Serial contaminated corrections now use one public `CRN-1` contaminated-restatement-netting object

The archive now fixes one compact arithmetic rule for chain contamination: whenever one `CIU-1` contaminated increment has already fed another increment that is later corrected, the operative public record must carry one machine-carrying contaminated-restatement-netting object called `CRN-1`.

### A. Minimum `CRN-1` fields

Every contaminated-restatement-netting object must expose at least:

- `crn_id`
- `active_ciu_id`
- `upstream_ciu_ref[]`
- `downstream_increment_ref[]`
- `gross_contaminated_amount`
- `prior_reversal_credit`
- `prior_residue_credit`
- `net_restatable_amount`
- `double_recovery_bar` (`active`)
- `last_uncontaminated_floor`
- `netting_method` (`carryover-and-reversal`, `trace-and-offset`, `mixed`)
- `remaining_public_restatement_required`
- `residual_chain_balance`
- `statement_of_reasons_ref`
- `beneficiary_notice_ref[]`
- `public_notes`

`CRN-1` is the public object that says serial contamination chains must be netted and restated in one visible arithmetic posture rather than reopened as separate full gross claims at every layer. `[REF-0545]` `[REF-0541]`

### B. Serial correction must subtract what earlier correction already neutralized

When an upstream contaminated increment has already been partly reversed, replaced, offset, or tombstoned through an earlier `CIU-1`, any later downstream correction must begin from the **remaining net contaminated amount**, not from the old gross amount. The archive chooses this because SAB 108 rejects isolated single-period arithmetic and requires attention to carryover and reversing effects. `[REF-0545]`

### C. Netting follows chain order but still preserves output-level correction duties

`CRN-1` does not erase the archive's output-level correction duties. Unreleased outputs are still voided first, mutable public outputs are still corrected next, adjustable live allocations are still prospectively narrowed next, and irreversible effects still require public restatement and residue accounting. What `CRN-1` changes is the arithmetic posture: each later correction must disclose how much contamination remains after prior chain corrections rather than pretending the entire prior gross amount is still live. `[REF-0545]` `[REF-0541]` `[REF-0542]` `[REF-0543]` `[REF-0544]`

### D. Double recovery is barred even across several linked `CIU-1` episodes

If the same contaminated increment appears in several linked `CIU-1` episodes, `CRN-1` must keep `double_recovery_bar` active and state which portion has already been neutralized, prospectively offset, or left as irreducible residue. The archive refuses to let serial correction chains become a laundering route for multiple recoveries from the same contamination. `[REF-0545]` `[REF-0506]`

### E. Residue must remain visible even when the net amount falls below fresh clawback value

A low `net_restatable_amount` does not erase the duty to publish a restated history. Where chain correction leaves a small or non-recoverable remainder, `CRN-1` must still publish the corrected floor, the netted residue, and the reason no further practical reversal is being attempted. A personhood world should not let serial arithmetic opacity become a backdoor to silent unresolved contamination. `[REF-0541]` `[REF-0542]`

---

## 4. Source-obscured generative resurfacing now uses one public `SGR-1` source-obscured-generative-review object

The archive now fixes one compact review rule for generative services that keep recreating restricted families without being able to point to one exact upstream locator: whenever a service cannot name a concrete source yet still emits operationally equivalent resurfacing after credible notice, it must publish one machine-carrying `SGR-1` object.

### A. Minimum `SGR-1` fields

Every source-obscured-generative-review object must expose at least:

- `sgr_id`
- `service_identifier`
- `artifact_family_ref`
- `prior_notice_lineage_ref[]`
- `source_certainty_state` (`source-obscured`)
- `equivalence_basis[]` (`answer-level-match`, `procedure-level-match`, `named-entity-match`, `policy-evasion-pattern`, `other`)
- `provisional_control_state[]` (`answer-friction`, `no-direct-locator`, `no-stepwise-operational-answer`, `temporary-refusal`, `temporary-suppression`, `other`)
- `statement_of_reasons_ref`
- `review_panel_or_internal_owner_ref`
- `independent_test_ref`
- `recheck_deadline`
- `appeal_path_ref`
- `cure_test_ref`
- `public_notes`

`SGR-1` is the public object that says source uncertainty does not dissolve review duty where practical resurfacing is still happening. `[REF-0546]` `[REF-0547]` `[REF-0535]` `[REF-0539]`

### B. Credible family-level notice triggers short-clock review even without a URL

If a service receives credible family-level notice that its answers are functionally recreating a restricted family, it must open `SGR-1` on a short clock even if it cannot identify one exact source URL, model weight, or retrieval item. The archive chooses this because current DSA enforcement logic allows temporary proportionate mitigation while investigation remains open and because generative risk management already treats third-party and retrieval layers as monitored deployment inputs. `[REF-0539]` `[REF-0546]`

### C. Source-obscured state still requires answer-class friction and reason-giving

During active `SGR-1` review, the service must apply at least one family-matched provisional control such as answer friction, refusal of stepwise operational reconstruction, or no-direct-locator posture, and it must publish a statement of reasons describing the family-level basis for action. The archive refuses the loophole in which “we cannot name the source” becomes permission to keep offering the same practical answer under a softer interface. `[REF-0535]` `[REF-0539]` `[REF-0546]`

### D. Review must rely on equivalence testing, not provenance perfection

The operative question for `SGR-1` is whether the service is still generating an operationally equivalent resurfacing of the restricted family, not whether it can perfectly reconstruct provenance. Current NIST synthetic-content guidance treats provenance, labeling, and detection as complementary tools rather than all-or-nothing proof requirements. A personhood world should therefore allow family-level review based on reproducibility and answer-pattern testing where provenance is incomplete. `[REF-0547]` `[REF-0546]`

### E. Cure requires tested non-equivalence or effective mitigation, not mere assertion

`SGR-1` may close only if independent testing shows that the service no longer produces operationally equivalent resurfacing of the restricted family or that the provisional controls reliably prevent that resurfacing. Mere operator assertion that the source is unknown or that the model was "adjusted" is not enough. `[REF-0546]` `[REF-0547]` `[REF-0539]`

---

## 5. Why this is still the narrow move

This revision does not redesign accreditation doctrine, general restitution law, or generative-model provenance in the large. It does three smaller things only.

1. It fixes how low-grade caution interrupts `RSD-1` easing without pretending every caution event is a new relapse.
2. It fixes how several linked `CIU-1` corrections net when one contaminated increment has already fed another.
3. It fixes what a generative service must do when it keeps recreating a restricted family while being unable to name one exact source.

That is enough to keep the archive's caution stack coherent without turning this archive into a treatise on supervision theory, accounting law, or generative provenance generally.

---

## 6. Objects added by this revision

### `RDP-1` — rehabilitation-decay pause

Carries the live `RSD-1` identifier, pause basis, pause state, frozen clean-credit amount, current surcharge rung, correction path, and conversion trigger when low-grade caution interrupts but does not yet defeat fresh-start rehabilitation easing. `[REF-0533]` `[REF-0538]` `[REF-0540]`

### `CRN-1` — contaminated-restatement netting

Carries the active `CIU-1`, upstream contamination lineage, gross contaminated amount, prior reversal credit, prior residue credit, net restatable amount, double-recovery bar, and chain residue for serial correction episodes in which one contaminated increment fed another. `[REF-0545]` `[REF-0541]` `[REF-0542]`

### `SGR-1` — source-obscured generative review

Carries the artifact family, source-certainty posture, equivalence basis, provisional answer controls, statement of reasons, independent test path, and cure test for generative services that keep recreating a restricted family without being able to name one exact source. `[REF-0546]` `[REF-0547]` `[REF-0535]` `[REF-0539]`

---

## 7. Consequences for the wider archive

- `research-reserve-*` doctrine now has a visible answer to the question what happens when monitored caution interrupts a rehabilitation easing path without yet counting as full relapse: it pauses in public, with conversion triggers, rather than silently easing onward or resetting by fiat.
- `research-*-fraud-*` and dependence-review doctrine now has a visible answer to the question how serial contamination corrections should add up: through one netting object that respects carryover and reversal effects, preserves single-satisfaction discipline, and still publishes residue when full reversal is no longer practical.
- `research-*-derivative-*` doctrine now has a visible answer to the question what happens when a generative service cannot identify one concrete source but still recreates the same restricted family: source uncertainty triggers review, friction, reason-giving, and recheck rather than acting as a safe harbor.

That keeps the research-governance lane conservative in the way the archive has been aiming for throughout: no decay-through-distraction, no double-counted serial correction, and no provenance-blind loophole for generative resurfacing.

---

## Bottom line

A personhood world should not force every low-grade caution event in rehabilitation to masquerade as a full relapse, should not let serial contamination correction double-count the same carryover slice as it moves through several linked restatements, and should not let generative services escape rediscovery duty merely because they cannot identify one concrete source. The archive therefore now fixes one more compact rule: **fresh-start rehabilitation now uses a public `RDP-1` object that pauses or hard-pauses `RSD-1` decay on declared caution signals while preserving but not advancing clean-credit clocks, serial contamination correction now uses a public `CRN-1` object that nets `CIU-1` carryover and reversal effects so the same contaminated increment is not unwound twice, and source-obscured resurfacing now uses a public `SGR-1` object that binds generative services to short-clock review, answer-class friction, reason-giving, and recheck even when no exact source can be named.** `[REF-0533]` `[REF-0538]` `[REF-0540]` `[REF-0545]` `[REF-0541]` `[REF-0546]` `[REF-0547]` `[REF-0535]` `[REF-0539]`
