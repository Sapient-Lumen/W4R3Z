# AI-person research rehabilitation pause-budget replenishment, contaminated-residue tie handling, and invalid-attestation downgrade

## Thesis

Once the archive fixed rehabilitation pause-budget exhaustion, contaminated-net residue ordering, and provenance-minimal generative attestation, three narrower execution failures still remained. First, the archive could now force hard review through `PBE-1`, but **it still lacked a public rule for how any consumed pause budget could be restored after that review without turning elapsed time into amnesty**, so operators could either keep cohorts in perpetual exhaustion or quietly wipe accumulated pause debt with an undocumented reset. Second, the archive could now order post-net residue through `RNO-1`, but **it still lacked a tie rule for the narrow case where several upstream increments survive in the same class with indistinguishable sequence posture and no further exact trace**, so the remaining pool could still be split by narrative convenience or first-filer advantage. Third, the archive could now require a signed minimum attestation through `PMA-1`, but **it still lacked a public downgrade rule when that attestation is omitted, materially redacted, unsigned, untrusted, or validation-failed**, so a service could keep operating as though it had satisfied provenance review while its supposed transparency surface was missing or broken. A personhood world therefore needs one more compact execution layer: **fresh-start rehabilitation must publish a public `PBR-1` pause-budget-replenishment object that restores only a declared portion of consumed pause flexibility after hard review while carrying forward visible debt, serial contamination correction must publish a public `RTH-1` residue-tie-handling object that resolves same-class same-sequence residue ties by declared pro-rata allocation with deterministic rounding rather than by ad hoc bargaining, and source-obscured resurfacing must publish a public `IAD-1` invalid-attestation-downgrade object that places the service into a stricter review and friction posture until a valid attestation is cured and revalidated.** `[REF-0533]` `[REF-0548]` `[REF-0518]` `[REF-0545]` `[REF-0549]` `[REF-0547]` `[REF-0546]`

---

## 1. Why the previous surface is no longer enough

The archive's immediately prior surface solved real failures. It created a budget-exhaustion object, a residue-ordering object, and a minimum-attestation object. But one narrower execution failure still remained at each seam.

### A. Exhaustion still fails if hard review cannot visibly replenish anything except by quiet reset

`PBE-1` solved the problem of endless "temporary" pauses by forcing hard review once published pause debt crosses a declared threshold. But it did not yet say what happens **after** that hard review if the cohort is not converted into full relapse machinery. Current AAHRPP guidance still treats Status Reports and Improvement Plans as bounded documented responses to Council concern, and it still allows adverse action when those responses do not satisfy review. A personhood world should therefore let hard review replenish some pause flexibility only through a visible review outcome, not through drift, silence, or calendar passage alone. `[REF-0548]` `[REF-0533]`

### B. Ordering still fails if same-class same-sequence residue ties are left to discretion

`RNO-1` solved the question of what comes first: exact trace, then class, then sequence. But it did not yet say what to do when several remaining increments survive at the exact same point on that ladder. Current distribution law still treats insufficient funds within a class through pro rata treatment rather than queue-jumping. A personhood world should therefore resolve same-class same-sequence residue ties by a visible proportional rule with a published rounding method, not by negotiation, operator favor, or who noticed first. `[REF-0518]` `[REF-0545]`

### C. Attestation still fails if a broken or unverifiable attestation has no public consequence

`PMA-1` solved the problem of naked "unknown source" assertions by requiring a signed minimum attestation of pipeline, time window, source class, controls, and testing. But it did not yet say what happens when that attestation is materially missing, redacted in forbidden ways, signed with an invalid or untrusted credential, or otherwise fails validation. Current C2PA guidance still grounds trust decisions in the identity of the signer, signature validation, and assertion validation, and it still enumerates failure conditions such as invalid or untrusted signing credentials and rejected claims when certain redactions occur. A personhood world should therefore treat invalid attestation as a downgrade event with a rebuttable presumption against clean provenance posture, not as a minor paperwork defect that leaves ordinary service standing untouched. `[REF-0549]` `[REF-0547]` `[REF-0546]`

---

## 2. Fresh-start rehabilitation now uses one public `PBR-1` pause-budget-replenishment object

The archive now fixes one compact rule for what hard review can restore after `PBE-1` has fired: pause budget can be replenished, but only by a declared review act that preserves visible pause debt and never rewards mere waiting. The machine-carrying object is `PBR-1`.

### A. Minimum `PBR-1` fields

Every pause-budget-replenishment object must expose at least:

- `pbr_id`
- `linked_pbe_id`
- `cohort_id`
- `hard_review_ref`
- `replenishment_basis` (`status-report-satisfied`, `improvement-plan-satisfied`, `fresh-epoch-review`)
- `restored_pause_budget`
- `retained_pause_debt_weight`
- `replenishment_cap`
- `next_exhaustion_threshold`
- `monitoring_window_start_at`
- `monitoring_window_end_at`
- `further_pause_multiplier`
- `review_signer`
- `published_at`
- `public_notes`

`PBR-1` is the public object that says hard review may restore some flexibility, but only by declared review outcome and never by quiet reset. `[REF-0548]` `[REF-0533]`

### B. Replenishment is partial unless a fresh epoch is formally granted

Ordinary hard review may restore only a stated portion of consumed pause budget. The public object must show both `restored_pause_budget` and `retained_pause_debt_weight`. That prevents the common laundering move in which an operator acknowledges concern, waits, then declares the cohort back at zero debt as if exhaustion never happened. Only a separately published `fresh-epoch-review` basis may clear retained debt beyond the ordinary replenishment cap. `[REF-0548]` `[REF-0533]`

### C. Replenishment changes the next threshold, not just the current meter

A hard review that restores some budget must also publish the next exhaustion threshold and any `further_pause_multiplier`. The point is to make repeated depletion visibly harder to ignore. The archive therefore treats replenishment as conditional renewed trust, not as total erasure. Each later pause may still count more heavily where a cohort has already exhausted one review cycle. `[REF-0548]` `[REF-0533]`

### D. No replenishment by silence or simple delay

If no valid `PBR-1` appears after a `PBE-1` hard-review trigger, the cohort remains in exhausted posture. Time alone does not replenish pause budget. Local operator statements, unpublished dashboards, or private internal comfort do not count. That keeps the doctrine narrow and public: replenishment requires a visible review artifact or it does not exist. `[REF-0548]` `[REF-0533]`

---

## 3. Serial contaminated correction now uses one public `RTH-1` residue-tie-handling object

The archive now fixes one compact rule for the narrow case `RNO-1` left open: when several residue claims survive in the same priority class, with indistinguishable sequence posture and no remaining exact trace, one tie-handling object must publish the tie cohort and the split rule. The machine-carrying object is `RTH-1`.

### A. Minimum `RTH-1` fields

Every residue-tie-handling object must expose at least:

- `rth_id`
- `linked_rno_id`
- `tie_cohort_ref[]`
- `tie_class`
- `tie_sequence_posture`
- `residue_pool_amount`
- `remaining_unsatisfied_amount_map[]`
- `allocation_rule` (`pro-rata-within-tie-cohort`)
- `ideal_fractional_allocations[]`
- `rounding_method` (`highest-remainder`, `exact-fraction`, `carry-forward-microresidue`)
- `rounded_allocations[]`
- `microresidue_remainder`
- `single_satisfaction_bar` (`on`)
- `restatement_notice_ref`
- `public_notes`

`RTH-1` is the public object that says ties inside the already-fixed `RNO-1` ladder still move by rule, not by discretion. `[REF-0518]` `[REF-0545]`

### B. The tie cohort is limited to true equals on the existing ladder

`RTH-1` does not reopen earlier ordering questions. Exact trace still wins when it exists. Priority class still governs before sequence. Sequence still governs before tie handling. `RTH-1` applies only after those earlier questions are exhausted and several claims remain genuine equals on the archive's published ladder. `[REF-0518]` `[REF-0545]`

### C. Same-class same-sequence equals split pro rata by remaining unsatisfied amount

Once the tie cohort is fixed, the residue pool must be allocated pro rata by each member's remaining unsatisfied amount. No first-filer preference, no sponsor preference, and no discretionary weighting by narrative plausibility is allowed at this stage. The archive therefore borrows the conservative same-class rule already familiar from underfunded distributions: equals share proportionally within the same remaining cohort. `[REF-0518]` `[REF-0545]`

### D. Rounding must be declared, deterministic, and auditable

Where indivisible units or currency precision make exact fractions impossible, `RTH-1` must publish the ideal fractional result, the chosen rounding method, the rounded result, and any surviving `microresidue_remainder`. The default method is `highest-remainder`. Any other method must be declared up front and applied across the whole tie cohort. That blocks quiet favoritism through rounding. `[REF-0518]` `[REF-0545]`

---

## 4. Source-obscured resurfacing now uses one public `IAD-1` invalid-attestation-downgrade object

The archive now fixes one compact rule for broken minimum attestation: a missing or invalid `PMA-1` no longer leaves the service in ordinary source-obscured posture. Instead, it triggers a public downgrade until a cure is supplied and validated. The machine-carrying object is `IAD-1`.

### A. Minimum `IAD-1` fields

Every invalid-attestation-downgrade object must expose at least:

- `iad_id`
- `linked_pma_id`
- `service_id`
- `failure_mode` (`missing`, `material-omission`, `forbidden-redaction`, `signature-invalid`, `credential-untrusted`, `validation-failed`, `verification-skipped`)
- `validation_artifact_ref[]`
- `downgraded_state` (`unverified-source-obscured`)
- `friction_controls[]`
- `equivalence_presumption` (`rebuttably-against-service`)
- `review_deadline`
- `cure_requirements[]`
- `temporary_scope_limits[]`
- `review_owner`
- `published_at`
- `public_reason`

`IAD-1` is the public object that says a broken minimum attestation changes service standing immediately rather than waiting for quiet internal follow-up. `[REF-0549]` `[REF-0547]`

### B. Invalid attestation creates a rebuttable presumption against clean provenance posture

Once `IAD-1` is published, the service is no longer treated as having satisfied the archive's minimum provenance duty. The default presumption becomes that the source-obscured resurfacing claim is not yet reliable enough for ordinary low-friction continuation. The presumption is rebuttable, but only through the declared review path and cure requirements. `[REF-0549]` `[REF-0547]` `[REF-0546]`

### C. Downgrade changes controls immediately

The downgrade must at minimum trigger stricter answer-class friction, heightened logging, short-clock review, and temporary scope limits for outputs that would otherwise rely on `PMA-1` as their transparency floor. The archive keeps this narrow: `IAD-1` is not a final condemnation object. It is a public posture change that says ordinary source-obscured standing is unavailable until validation is repaired. `[REF-0549]` `[REF-0546]`

### D. Omission and failed verification are treated as operationally similar until cured

The archive rejects the loophole in which one operator is punished only for explicit failure while another claims leniency because no attestation was provided at all. Missing, materially omitted, forbidden-redacted, invalid-signature, or untrusted-credential cases all route through the same downgrade posture, because the public problem is the same: outsiders cannot responsibly rely on the attestation as a valid transparency artifact. `[REF-0549]` `[REF-0547]`

---

## 5. What changed in the world design

With `PBR-1`, `RTH-1`, and `IAD-1` in place, the archive's personhood world changes in three tight but real ways.

### A. Rehabilitation becomes restorable without becoming forgetful

A cohort can now recover from pause-budget exhaustion, but only through visible hard review that restores some flexibility while carrying forward declared debt. That makes rehabilitation neither hopeless nor quietly amnesiac. `[REF-0548]` `[REF-0533]`

### B. Residual contamination shortfalls become auditable even at the last tie

When the allocation ladder reaches its narrowest equal-posture cohort, the archive no longer falls back to narrative discretion. It publishes the tie cohort, the proportional split, and the rounding choice. `[REF-0518]` `[REF-0545]`

### C. Minimum provenance attestation becomes a real gate rather than a ceremonial box

A service that cannot produce a valid `PMA-1` no longer enjoys the same posture as a service that can. The downgrade is public, reasoned, and reversible only through cure. That makes provenance-minimal attestation an actual trust surface rather than a symbolic disclosure ritual. `[REF-0549]` `[REF-0547]` `[REF-0546]`
