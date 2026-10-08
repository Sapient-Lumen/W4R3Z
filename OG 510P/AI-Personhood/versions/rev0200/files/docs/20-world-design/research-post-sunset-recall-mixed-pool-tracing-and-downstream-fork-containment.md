# AI-person research post-sunset recall thresholds, mixed-pool concealed recovery tracing, and downstream fork containment after replacement failure

## Thesis

Once the archive fixed public aftercare sunset proof, concealed-recovery claimant ordering, and mixed-derivative replacement equivalence, three narrower execution failures still remained. First, the archive could now fully clear a restored reserve cohort through `RAS-1`, but **it still lacked an exact public test for when later concentration spikes, ownership shifts, governance drift, major resource contraction, or catastrophic interruption force that same cohort back into aftercare rather than letting a once-clean status silently persist through materially changed conditions**. Second, the archive could now route later concealed recoveries through `CRO-1`, but **it still lacked an exact rule for pools that are partly traceable and partly commingled, so one side could still overclaim the whole pool on thin tracing while the other side demanded total pro rata pooling even for slices that are actually demonstrated**. Third, the archive could now keep a mixed derivative alive through `MRE-1`, but **it still lacked a public containment rule for already-forked or mirrored downstream artifacts once that replacement-equivalence claim later fails or unravels, so stale mirrors and forks could continue distributing the affected dependency under cover of historical drift**. A personhood world therefore needs one more compact execution layer: **fully cleared reserve cohorts must publish a public `RAR-1` reserve-aftercare-recall object that forces reentry to aftercare whenever published post-sunset concentration, control, resource, interruption, or monitoring triggers are crossed; concealed recovery families must publish a public `MPT-1` mixed-pool-tracing object that allocates exactly traced slices to the traced class or claimant and treats the remaining commingled residue as a general ladder-governed pool with no speculative dilution or double recovery; and derivative families whose replacement-equivalence claim fails must publish a public `DFC-1` downstream-fork-containment object that imposes no-new-forking, downstream notice, freeze / update / purge duties where control exists, and public quarantine or tombstone duties where direct technical control no longer exists.** `[REF-0514]` `[REF-0515]` `[REF-0521]` `[REF-0506]` `[REF-0518]` `[REF-0522]` `[REF-0519]` `[REF-0520]`

---

## 1. Why the previous surface is no longer enough

The archive's immediately prior surface solved real failures. It fixed public aftercare exit, stable ordering for later concealed recoveries, and a real replacement-equivalence test for mixed derivatives. But one narrower failure still remained at each seam.

### A. Sunset still fails if later drift never reopens aftercare

A cleared reserve cohort should not remain forever inside heightened aftercare, but neither should a past clearance become permanent immunity against later concentration spikes or governance deterioration. Current AAHRPP maintenance guidance already treats changes in ownership or control, mergers and acquisitions, significant resource reduction, new program scope, and catastrophic interruption as reportable items rather than as facts too small to matter once accreditation already exists, while current NIST monitoring guidance already treats ongoing assessment, analysis, response, and reporting as continuing governance work rather than one-time certification theater. A personhood world should therefore force visible reentry to aftercare when the post-sunset risk profile materially worsens, not wait for quiet folklore to become the rule. `[REF-0514]` `[REF-0515]`

### B. Ordered recovery still fails if mixed pools must be all trace or all residue

`CRO-1` solved the ordering ladder for later concealed recovery, but it did not yet say what to do when only part of a newly recovered pool is actually traced and the rest is commingled. Current bankruptcy distribution law already pairs ordered class distribution and pro rata allocation with the possibility of segregated treatment for distinct pools or proceeds, while the archive's own fraud-late doctrine already preserves single satisfaction and blocks double recovery. A personhood world should therefore separate what is genuinely demonstrated from what is not: exact trace gets exact routing; the undemonstrated remainder becomes residue and follows the ordinary ladder. `[REF-0506]` `[REF-0518]` `[REF-0522]`

### C. Replacement equivalence still fails if broken continuations keep propagating downstream

`MRE-1` solved the threshold for proving a mixed derivative clean enough to continue, but it did not yet say what happens when that proof later fails because a hidden dependency, mislabeled component, or fresh contamination finding emerges after forks and mirrors already exist. Current NIST SSDF guidance already treats provenance maintenance, version retention during transition, and ongoing vulnerability response as continuing duties, current NIST vulnerability-disclosure guidance already frames receipt, assessment, management, and communication of remediation as formalized public obligations, and current Census restricted-output practice already treats program files and other removable derivatives as governed outputs rather than ungoverned leftovers. A personhood world should therefore impose an explicit containment object rather than pretending that already-forked downstream artifacts are beyond governance the moment they replicate. `[REF-0519]` `[REF-0521]` `[REF-0520]`

---

## 2. Cleared reserve cohorts now reenter aftercare only through one public `RAR-1` reserve-aftercare-recall object

The archive now fixes one compact rule for post-sunset recall: any cohort that previously reached `fully-cleared` under `RAS-1` must publish one machine-carrying reserve-aftercare-recall object called `RAR-1` whenever published recall thresholds are crossed.

### A. Minimum `RAR-1` fields

Every aftercare-recall object must expose at least:

- `rar_id`
- `ras_id`
- `covered_defect_classes[]`
- `recall_trigger_type[]` (`control-shift`, `ownership-shift`, `concentration-spike`, `resource-contraction`, `catastrophic-interruption`, `monitoring-failure`, `other-published-trigger`)
- `trigger_measurement_ref[]`
- `trigger_date`
- `recall_decision`
- `recall_scope` (`class-specific`, `cohort-wide`, `temporary-audit-only`)
- `recalled_aftercare_start`
- `recalled_aftercare_minimum_cycle_count`
- `cap_reset_rule`
- `audit_reset_rule`
- `independent_reassessment_required`
- `interim_status` (`fully-cleared-pending-recall-review`, `reentered-cap-active`, `reentered-audit-only`, `reentry-denied`)
- `public_notes`

`RAR-1` is the public proof object that says a once-cleared cohort is not immune to later material drift. `[REF-0514]` `[REF-0515]`

### B. Recall triggers must be published in advance and tied to material post-sunset change

A personhood world should not let authorities invent recall triggers ad hoc after a political controversy, but it also should not let past clearance survive obvious structural change. The archive therefore requires each reserve family to publish its recall trigger table in advance and limits post-sunset recall to material events such as control or ownership change, merger, concentration growth, significant resource loss, catastrophic interruption, or monitoring evidence that the control environment no longer matches the one that originally passed sunset. `[REF-0514]` `[REF-0515]`

### C. Recall returns the cohort to aftercare prospectively, not to permanent stigma

`RAR-1` never erases the public record of earlier clean cycles, but it does restart live aftercare prospectively for the affected class or cohort. The archive rejects both extremes: no quiet immunity forever, and no theory that one recall means permanent incapacity. Recalled cohorts return to the `RAC-1` / `RAS-1` ladder, with the recall object stating whether caps, audit floors, or both have restarted and what minimum new clean cycle count is now required. `[REF-0514]` `[REF-0515]`

---

## 3. Partly traceable concealed pools now route through one public `MPT-1` mixed-pool-tracing object

The archive now fixes one compact rule for concealed pools that are neither wholly traced nor wholly commingled: every later-recovered mixed pool must publish one machine-carrying `MPT-1` object before allocation.

### A. Minimum `MPT-1` fields

Every mixed-pool-tracing object must expose at least:

- `mpt_id`
- `cro_id`
- `pool_identifier`
- `gross_recovered_value`
- `exact_trace_slices[]`
- `trace_method_ref[]`
- `trace_confidence_statement`
- `commingled_residue_value`
- `excluded_speculative_claims[]`
- `single_satisfaction_check`
- `remaining_unsatisfied_classes[]`
- `residue_distribution_rule`
- `residue_distribution_result[]`
- `public_math_ref`
- `current_state` (`trace-confirmed`, `residue-only`, `mixed-split-complete`, `held-for-further-proof`)
- `public_notes`

`MPT-1` is the public split object that stops a partly proven pool from being treated as either pure trace or pure residue. `[REF-0506]` `[REF-0518]` `[REF-0522]`

### B. Exactly traced slices route first, but only to the demonstrated extent

Where exact chain-of-custody, provenance, or equivalent class-specific proof actually demonstrates that a slice belongs to a particular claimant or class, that slice routes first to that claimant or class. But the demonstrated slice is capped by the proof actually shown; nobody may enlarge an exact trace by rhetoric, similarity, or probabilistic guesswork while calling the whole pool “effectively traced.” `[REF-0506]` `[REF-0522]`

### C. The undemonstrated remainder becomes ordinary residue and follows the declared ladder

After exact slices are removed, the remaining commingled value becomes ordinary residue. That residue then follows the already-declared `CRO-1` priority ladder and pro rata rule inside the first still-unsatisfied class. The archive chooses this because personhood worlds need a stable public split rule that does not force all-or-nothing tracing fights whenever some but not all recovery evidence exists. `[REF-0518]` `[REF-0522]`

### D. Single satisfaction still limits the whole pool

Even when a pool is split between traced slices and ladder-governed residue, `single_satisfaction_check` must certify that total recovery across all slices and classes does not exceed the still-unsatisfied amount. `MPT-1` therefore works only as a routing rule, never as a loophole for double satisfaction through repeated characterization of the same recovered value. `[REF-0506]`

---

## 4. Failed replacement-equivalence now triggers one public `DFC-1` downstream-fork-containment object

The archive now fixes one compact rule for replacement failure after downstream spread: every derivative family whose `MRE-1` claim later fails or materially unravels must publish one machine-carrying downstream-fork-containment object called `DFC-1`.

### A. Minimum `DFC-1` fields

Every downstream-fork-containment object must expose at least:

- `dfc_id`
- `mre_id`
- `failure_basis` (`hidden-dependency`, `false-provenance`, `failed-transition`, `renewed-review-failure`, `fresh-contamination`, `other`)
- `affected_artifact_family[]`
- `known_downstream_forks[]`
- `known_mirrors[]`
- `control_scope_map[]`
- `downstream_notice_ref[]`
- `new_distribution_state` (`freeze`, `no-new-fork`, `update-required`, `purge-required`, `historical-quarantine-only`)
- `must_update_by`
- `must_purge_by`
- `mirror_tombstone_ref[]`
- `public_registry_state`
- `residual_uncontrolled_artifacts_statement`
- `current_state` (`notice-open`, `freeze-active`, `partial-containment`, `contained`, `historical-only`)
- `public_notes`

`DFC-1` is the public containment object for the moment when a derivative family learns that its earlier clean-replacement claim was false or incomplete. `[REF-0519]` `[REF-0521]` `[REF-0520]`

### B. Known forks and mirrors must receive notice plus a no-new-fork state immediately

Once `MRE-1` fails, the archive forbids quiet internal cleanup while downstream copies keep spreading. `DFC-1` must therefore send notice to known forks, mirrors, and integrators, immediately mark the family `no-new-fork`, and freeze new distribution unless and until a fresh clean continuation is actually proved. This uses the same conservative logic as vulnerability-disclosure governance: receive the problem, assess it, manage it, and communicate the mitigation rather than leaving the public to infer safety from silence. `[REF-0521]` `[REF-0519]`

### C. Where direct control exists, update or purge is mandatory; where control does not exist, quarantine and tombstone are mandatory

If the steward or authority can technically control a downstream artifact, it must update, freeze, or purge that artifact on the schedule named in `DFC-1`. If the artifact is outside direct control — for example because it is mirrored or forked by a third party — the authority must at minimum maintain a public quarantine or tombstone entry, stop treating the artifact as an approved continuation, and preserve historical trace without live endorsement. The archive refuses the loophole in which loss of direct control is treated as loss of public duty. `[REF-0521]` `[REF-0520]`

### D. Old clean claims stay visible as superseded history, not as current authorization

`DFC-1` does not erase the fact that an `MRE-1` once existed, but it must mark that claim as failed, superseded, or withdrawn in every live registry surface. Personhood worlds need this because already-forked artifacts often outlive their original stewards; historical readability is acceptable, but live ambiguity about authorization is not. `[REF-0519]` `[REF-0521]` `[REF-0520]`

---

## 5. Why this is still the narrow move

This revision does not try to redesign the entire reserve or derivative architecture. It does three smaller things only.

1. It adds a reentry trigger for cohorts that were legitimately cleared but later materially changed.
2. It adds a split rule for concealed pools that are partly demonstrated and partly residue.
3. It adds a containment rule for downstream artifacts when a clean-replacement claim later fails.

That is enough to keep the caution stack coherent without turning this archive into a generalized software-remediation or insolvency treatise.

---

## 6. Objects added by this revision

### `RAR-1` — reserve-aftercare-recall object

Carries the published recall trigger, evidence, scope, restarted aftercare state, reset rule, and reassessment duty for a previously cleared reserve cohort that must reenter aftercare after later material drift. `[REF-0514]` `[REF-0515]`

### `MPT-1` — mixed-pool-tracing object

Carries the exact traced slices, excluded speculative claims, residue remainder, ladder rule, single-satisfaction check, and public math for concealed recovery pools that are partly traceable and partly commingled. `[REF-0506]` `[REF-0518]` `[REF-0522]`

### `DFC-1` — downstream-fork-containment object

Carries the failed replacement basis, affected family, known forks and mirrors, downstream notices, no-new-fork state, update / purge schedules, quarantine or tombstone entries, and residual uncontrolled-artifact statement once replacement equivalence fails after downstream spread. `[REF-0519]` `[REF-0521]` `[REF-0520]`

---

## 7. Consequences for the wider archive

- `research-reserve-*` doctrine now has a real answer to the question “what if the cohort went clean and then later drifted again?”
- `research-*-fraud-*` doctrine now has a real answer to the question “what if the recovered pool is only partly provable?”
- `research-*-derivative-*` doctrine now has a real answer to the question “what if the supposed clean replacement later turns out not to be clean after forks and mirrors already exist?”

That keeps the research-governance lane visibly conservative in the way the archive has been aiming for throughout: no silent normalization, no all-or-nothing proof postures, and no pretending that propagation erases governance duty.

---

## Bottom line

A personhood world should not let a once-cleared reserve cohort keep permanent post-sunset immunity after later structural drift, should not force partly traceable concealed pools into fake all-or-nothing allocation fights, and should not treat downstream forks or mirrors as governance-free once a clean-replacement claim later fails. The archive therefore now fixes one more compact rule: **fully cleared reserve cohorts now reenter aftercare only through a public `RAR-1` recall object tied to published control, concentration, resource, interruption, and monitoring triggers; later concealed recovery pools now split only through a public `MPT-1` object that routes exact traced slices exactly as proved and sends the undemonstrated remainder through the ordinary priority ladder with pro rata allocation and a single-satisfaction ceiling; and failed mixed-derivative replacement claims now trigger a public `DFC-1` containment object that imposes no-new-forking, downstream notice, controlled update or purge where possible, and public quarantine or tombstone duties where direct control no longer exists.** `[REF-0514]` `[REF-0515]` `[REF-0521]` `[REF-0506]` `[REF-0518]` `[REF-0522]` `[REF-0519]` `[REF-0520]`
