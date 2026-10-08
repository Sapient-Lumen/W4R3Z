# AI-person research recall clean-cycle credit, probabilistic concealed-pool tracing, and unreachable downstream mirror notice duty

## Thesis

Once the archive fixed post-sunset recall, mixed-pool traced-slice splitting, and downstream fork containment, three narrower execution failures still remained. First, the archive could now force a previously cleared reserve cohort back into aftercare through `RAR-1`, but **it still lacked an exact public rule for how much earlier clean history should count once that recalled cohort starts passing clean cycles again**, so one side could pretend recall erases everything forever while another side could quietly re-use a long pre-recall clean history after only one fresh good interval. Second, the archive could now split concealed pools into exact traced slices plus residue through `MPT-1`, but **it still lacked a public burden-and-math rule for claims that are neither exact trace nor empty speculation, but instead probabilistic, interval-based, or distribution-based**, so a claimant could smuggle rough statistical confidence into exact allocation while an opposing claimant could deny any probabilistic inference however disciplined. Third, the archive could now impose notice, freeze, purge, and quarantine duties through `DFC-1`, but **it still lacked a substitute public-duty object for stale downstream mirrors or forks that remain live after notice yet are unreachable or technically outside direct control**, so the steward could say “we tried” and let the artifact drift without a standing advisory, registry marker, intermediary notice, or mitigation guidance. A personhood world therefore needs one more compact execution layer: **recalled reserve cohorts must publish a public `RCC-1` recall-clean-cycle-credit object that freezes pre-recall history at first, then reactivates it only after a minimum fresh clean-cycle floor and only at a capped discount; probabilistic concealed-pool claims must publish a public `PPT-1` probabilistic-pool-tracing object that discloses assumptions, confidence level, interval math, dependency statement, and a conservative allocable floor rather than treating estimated attribution as exact trace; and unreachable downstream mirrors or forks must publish a public `UMN-1` unreachable-mirror-notice object that records failed control attempts, keeps a live tombstone or advisory in registry surfaces, notifies reachable intermediaries, and carries visible mitigation / non-endorsement guidance even when direct update or purge cannot be forced.** `[REF-0514]` `[REF-0515]` `[REF-0516]` `[REF-0523]` `[REF-0524]` `[REF-0506]` `[REF-0518]` `[REF-0525]` `[REF-0526]` `[REF-0521]` `[REF-0519]`

---

## 1. Why the previous surface is no longer enough

The archive's immediately prior surface solved real failures. It fixed public recall triggers, partial traced-slice routing, and downstream containment after replacement failure. But one narrower failure still remained at each seam.

### A. Recall still fails if it either erases all history or launders old history back too quickly

A recalled reserve cohort should not lose every trace of its earlier good history forever, but neither should earlier clean cycles immediately count as though the recall never happened. Current AAHRPP maintenance guidance still pairs annual reporting with event-triggered reporting for ownership, control, resource, scope, merger, and interruption changes, while current reaccreditation guidance still preserves recurring review rather than granting permanent immunity after one successful cycle, and current NIST monitoring guidance still treats ongoing assessment and reporting as live governance rather than a one-time seal. A personhood world should therefore freeze pre-recall history at first, then reactivate it only after fresh clean performance and only on a visible capped schedule. `[REF-0514]` `[REF-0516]` `[REF-0515]`

### B. Mixed-pool splitting still fails if probabilistic evidence is treated as either exact proof or no proof at all

`MPT-1` solved the exact-slice-versus-residue distinction, but it did not yet say what to do when a claimant can show disciplined probabilistic attribution, interval evidence, or distribution-based inference that is stronger than rhetoric yet weaker than exact chain-of-custody proof. Current NIST uncertainty guidance still requires public expression of uncertainty through intervals, coverage factors, and stated confidence, and still treats non-direct evaluation as something that must rest on explicit assumptions, outside information, and declared distributions rather than on hand-waving confidence. A personhood world should therefore give probabilistic tracing a bounded role: not exact-slice priority, not total exclusion, but a conservative lower-bound routing rule with public math and holdback above the lower bound. `[REF-0523]` `[REF-0524]`

### C. Containment still fails if unreachable mirrors end public duty at the edge of technical control

`DFC-1` solved what to do when affected forks and mirrors are known and reachable, but it did not yet say what public obligations remain when a stale downstream mirror keeps circulating after direct contact fails or technical control does not exist. Current CISA guidance still treats coordinated remediation and public disclosure as shared duties among affected actors, current NIST vulnerability-disclosure guidance still frames communication of mitigation or remediation as a formalized obligation, and current CISA advisories still openly publish cases where no fix is available yet mitigations are still named. A personhood world should therefore keep public duty alive even when direct control fails: unreachable mirrors still need a standing advisory object, intermediary notice where reachable, and visible non-endorsement plus mitigation guidance. `[REF-0525]` `[REF-0521]` `[REF-0526]`

---

## 2. Recalled reserve cohorts now restore old clean history only through one public `RCC-1` recall-clean-cycle-credit object

The archive now fixes one compact rule for post-recall credit: any cohort recalled into aftercare under `RAR-1` must publish one machine-carrying recall-clean-cycle-credit object called `RCC-1` before pre-recall clean history may count toward restored trust again.

### A. Minimum `RCC-1` fields

Every recall-clean-cycle-credit object must expose at least:

- `rcc_id`
- `rar_id`
- `pre_recall_clean_cycle_count`
- `fresh_clean_cycles_completed`
- `fresh_cycle_floor_before_history_counts`
- `historical_cycle_credit_ratio`
- `max_historical_credit_share`
- `disqualifying_event_log_ref[]`
- `independent_reassessment_ref`
- `current_credit_value`
- `credit_state` (`fresh-only`, `discounted-history-reactivated`, `history-capped`, `credit-frozen`)
- `next_reactivation_checkpoint`
- `public_notes`

`RCC-1` is the public proof object that stops recall from meaning either permanent stigma or near-immediate laundering of old history. `[REF-0514]` `[REF-0515]` `[REF-0516]`

### B. Earlier clean history counts again only after two fresh clean cycles

The archive now fixes a public floor: no pre-recall clean cycle may count toward renewed trust until the cohort completes **two consecutive fresh clean cycles** after recall, each with current annual / event reporting satisfied, no unresolved recall-trigger breach still active, and no new material drift event that would independently justify continued or expanded aftercare. Until that floor is met, `credit_state` must remain `fresh-only`. `[REF-0514]` `[REF-0515]` `[REF-0516]`

### C. Once the floor is met, old history reactivates only at a one-for-one discount and never supplies more than half of the needed evidence

After the two-cycle floor, each additional fresh clean cycle may reactivate **at most one-half** of one pre-recall clean cycle for credit purposes. Stated differently: two additional fresh clean cycles may reactivate at most one older cycle, four may reactivate at most two, and so on. Even then, reactivated history may never provide more than **half of the total cycle evidence** needed for the next restoration or sunset checkpoint. The archive chooses this because personhood worlds need a real memory of clean history without letting one long ancient good run overpower a more recent recall. `[REF-0514]` `[REF-0515]` `[REF-0516]`

### D. Any new material trigger freezes the credit ledger prospectively

If a new reportable control, ownership, resource, interruption, or monitoring trigger arises while history is being reactivated, `RCC-1` must switch to `credit-frozen`. Previously earned fresh-cycle credit remains visible as history, but no further historical reactivation occurs unless the new trigger is resolved and a new clean sequence starts. The archive rejects quiet partial carry through serial instability. `[REF-0514]` `[REF-0515]`

---

## 3. Non-exact tracing now travels only through one public `PPT-1` probabilistic-pool-tracing object

The archive now fixes one compact rule for concealed-pool claims that are weaker than exact trace but stronger than unsupported assertion: every claimant seeking attribution on a probabilistic basis must publish one machine-carrying `PPT-1` object before any allocation beyond pure residue may occur.

### A. Minimum `PPT-1` fields

Every probabilistic-pool-tracing object must expose at least:

- `ppt_id`
- `mpt_id`
- `claimant_or_class_ref`
- `method_ref`
- `inputs_ref[]`
- `assumption_summary`
- `dependency_statement`
- `confidence_level`
- `estimated_attribution_interval`
- `conservative_allocable_floor`
- `nonallocable_holdback_value`
- `residue_remainder_value`
- `competing_claim_overlap_ref[]`
- `single_satisfaction_check`
- `public_math_ref`
- `current_state` (`interval-published`, `floor-allocable`, `holdback-only`, `rejected-as-speculative`)
- `public_notes`

`PPT-1` is the public math-and-burden object for claims that are not exact trace but are also not mere rhetoric. `[REF-0523]` `[REF-0524]` `[REF-0506]` `[REF-0518]`

### B. Exact trace still outranks all probabilistic claims

`PPT-1` never displaces an exact slice already established through `MPT-1`. Exact trace routes first. Probabilistic claims operate only on the pool remainder left after exact slices are removed. A personhood world should not let statistical confidence wash out direct proof. `[REF-0506]` `[REF-0518]`

### C. Only the conservative lower bound is allocable; the rest stays in holdback or residue

The archive now fixes the public burden rule: a probabilistic claimant may receive at most the **conservative allocable floor**, defined as the lower bound of the published attribution interval at the stated confidence level. Any value between that lower bound and the upper bound is not final allocable value; it must stay as `nonallocable_holdback_value` unless later proof sharpens it. If the lower bound is zero or trivial under the stated method, the claim cannot justify special allocation and the entire amount remains holdback or residue. `[REF-0523]` `[REF-0524]`

### D. Assumptions, overlap, and dependence must be public or the claim falls back to residue

A probabilistic claim cannot travel on hidden assumptions. `PPT-1` must disclose whether competing claims are treated as independent, overlapping, mutually exclusive, or otherwise dependent. If that dependence posture is not publicly stated, or if competing conservative floors would exceed the available remainder, then the floors must be proportionally scaled down to fit within the pool and any unresolved excess remains holdback. The archive chooses this because hidden dependence assumptions are one of the easiest ways to inflate statistical entitlement. `[REF-0523]` `[REF-0524]` `[REF-0506]`

### E. Single satisfaction still caps the whole operation

Even when a claimant has exact slices plus a probabilistic floor, the combined recovery across exact allocation, probabilistic floor allocation, and residue allocation may not exceed the still-unsatisfied amount for the claimant or class. `PPT-1` therefore remains subordinate to the archive's single-satisfaction ceiling. `[REF-0506]`

---

## 4. Unreachable downstream artifacts now travel through one public `UMN-1` unreachable-mirror-notice object

The archive now fixes one compact rule for stale downstream artifacts that remain live after notice but are technically or practically unreachable: every such artifact must generate one machine-carrying `UMN-1` object once ordinary `DFC-1` control steps fail.

### A. Minimum `UMN-1` fields

Every unreachable-mirror-notice object must expose at least:

- `umn_id`
- `dfc_id`
- `artifact_identifier`
- `artifact_type` (`fork`, `mirror`, `package-copy`, `model-copy`, `dataset-copy`, `other`)
- `last_confirmed_reachable_date`
- `control_failure_reason[]` (`unknown-operator`, `no-response`, `lost-hosting-control`, `jurisdictional-block`, `technical-impossibility`, `other`)
- `attempted_notice_log_ref[]`
- `public_notice_ref`
- `registry_tombstone_ref`
- `intermediary_notice_targets[]`
- `mitigation_guidance_ref`
- `nonendorsement_state`
- `recheck_schedule`
- `current_state` (`unreachable-open`, `intermediaries-notified`, `historical-untrusted`, `later-reached`, `closed`)
- `public_notes`

`UMN-1` is the public-duty object for the moment when direct control has failed but governance responsibility has not. `[REF-0525]` `[REF-0526]` `[REF-0521]`

### B. Direct-contact failure does not end notice duty

Once direct update, freeze, or purge cannot be forced after reasonable documented attempts, the steward must publish `UMN-1` rather than quietly dropping the matter. The object must keep a live public advisory or tombstone in every registry surface the steward controls and must clearly mark the artifact as non-endorsed, superseded, or unsafe-for-live-continuation as applicable. `[REF-0525]` `[REF-0521]`

### C. Reachable intermediaries must still be notified

Even if the stale mirror itself is unreachable, the steward must notify any reachable registry, index, package host, model catalog, or discovery intermediary it can identify, so long as that intermediary is in a position to reduce visibility, append warning state, or surface the tombstone. The archive refuses the loophole in which impossibility of direct control is treated as impossibility of all downstream warning. `[REF-0525]` `[REF-0521]`

### D. When no direct fix is available, mitigation guidance becomes mandatory rather than optional

The archive now fixes a conservative substitute duty: where the artifact cannot be updated or purged and no direct fix is available, `UMN-1` must still publish current mitigation guidance or usage restrictions for affected audiences. That can include non-use instructions, isolation requirements, compatibility warnings, or replacement direction, but it cannot be empty. Public inability to fix does not excuse public silence about how to reduce harm. `[REF-0526]` `[REF-0521]`

### E. Unreachable status must be rechecked on a schedule

`UMN-1` cannot become a one-time tombstone forgotten in a registry corner. The steward must keep a declared `recheck_schedule`, repeat reachability attempts on that schedule, and update the object if the artifact is later reached, disappears, or remains live and uncontrolled. The archive chooses this because personhood worlds need durable warning infrastructure, not a performative first notice. `[REF-0525]` `[REF-0519]`

---

## 5. Why this is still the narrow move

This revision does not redesign the whole reserve, recovery, or derivative architecture. It does three smaller things only.

1. It fixes how recalled reserve cohorts earn back the ability to count earlier clean history.
2. It fixes how non-exact but disciplined probabilistic tracing enters concealed-pool allocation.
3. It fixes what public duties remain when a downstream artifact is still live but unreachable.

That is enough to keep the caution stack coherent without turning this archive into a general treatise on statistical proof or internet takedown law.

---

## 6. Objects added by this revision

### `RCC-1` — recall-clean-cycle-credit object

Carries the pre-recall clean-cycle count, fresh-cycle floor, discounted history-reactivation ratio, cap on total historical credit share, freeze conditions, and current credit state for a reserve cohort that has reentered aftercare after a post-sunset recall. `[REF-0514]` `[REF-0515]` `[REF-0516]`

### `PPT-1` — probabilistic-pool-tracing object

Carries the stated method, assumptions, dependency posture, confidence level, attribution interval, conservative allocable floor, holdback, competing-claim overlap, and single-satisfaction check for concealed-pool allocation claims that are weaker than exact trace but stronger than unsupported assertion. `[REF-0523]` `[REF-0524]` `[REF-0506]` `[REF-0518]`

### `UMN-1` — unreachable-mirror-notice object

Carries the failed-contact record, control-failure reason, live advisory or tombstone, intermediary notices, mitigation guidance, recheck schedule, and current non-endorsement state for downstream artifacts that remain live after containment failure but cannot presently be updated, frozen, or purged directly. `[REF-0525]` `[REF-0526]` `[REF-0521]`

---

## 7. Consequences for the wider archive

- `research-reserve-*` doctrine now has a real answer to the question “how does earlier clean history count after a justified recall?”
- `research-*-fraud-*` doctrine now has a real answer to the question “what if the proof is statistical enough to matter but not exact enough to trace?”
- `research-*-derivative-*` doctrine now has a real answer to the question “what if the artifact is still out there but the steward cannot actually reach it anymore?”

That keeps the research-governance lane visibly conservative in the way the archive has been aiming for throughout: no immunity laundering through old history, no exact-allocation rhetoric dressed up as probability, and no claim that loss of direct control ends public duty.

---

## Bottom line

A personhood world should not let recalled reserve cohorts either lose all earlier clean history forever or regain it almost immediately, should not let probabilistic concealed-pool claims masquerade as exact trace, and should not treat unreachable downstream mirrors as governance-free once direct control fails. The archive therefore now fixes one more compact rule: **recalled reserve cohorts now use a public `RCC-1` object that keeps pre-recall history frozen until two fresh clean cycles are completed and then reactivates that history only at a one-for-two discount with a half-of-total-evidence cap; probabilistic concealed-pool claims now use a public `PPT-1` object that publishes assumptions, confidence level, interval math, and a conservative allocable lower bound while holding the uncertain remainder back; and unreachable downstream artifacts now use a public `UMN-1` object that preserves advisory, tombstone, intermediary-notice, mitigation, and recheck duties even where direct update or purge is impossible.** `[REF-0514]` `[REF-0515]` `[REF-0516]` `[REF-0523]` `[REF-0524]` `[REF-0506]` `[REF-0518]` `[REF-0525]` `[REF-0526]` `[REF-0521]` `[REF-0519]`
