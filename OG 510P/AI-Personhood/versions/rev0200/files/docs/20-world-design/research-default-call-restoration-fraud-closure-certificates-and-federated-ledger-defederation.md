# AI-person research reinstated default-call restoration, fraud-recovery closure certificates, and federated-ledger de-federation

## Thesis

Once the archive fixed remembered reserve reinstatement, fraud-late recovery limits, and federated shared-ledger control for derivative releases, three narrower operational failures still remained. First, the archive could now force decertified reserve cohorts through fresh review and a heightened non-default return period, but **it still lacked a public rule for when a repaired cohort regains ordinary default-call trust, when it may serve only in a capped limited-default role, and when relapse should automatically push it back down rather than be bargained away case by case**. Second, the archive could now reopen old split-successor apportionment tables for fraud and cap recovery at single satisfaction, but **it still lacked a visible closure surface for the common case where fraud is proved, some retroactive recovery succeeds, and a residue remains unrecoverable without either violating good-faith shields or reopening the same deficiency forever**. Third, the archive could now federate several authorities and providers inside one derivative-governance ledger, but **it still lacked a rule for what happens when one authority exits, one provider terminates participation, or one dataset can no longer lawfully remain in the shared family while already-released derivative artifacts remain live**. A personhood world therefore needs one more compact execution layer: **reinstated reserve cohorts must publish a public `RDR-1` reserve-default-restoration object that stages return from `ordinary-nondefault` through `limited-default` to `ordinary-default` with class-specific relapse triggers; fraud-late recovery must end in a public `FRC-1` fraud-recovery-closure certificate that distinguishes satisfied from unrecoverable residue and shifts any remaining burden prospectively rather than by endless retro-clawback; and federated historical families must publish a public `FDX-1` federated-de-federation-exit object that snapshots derivative obligations, carries provider constraints forward, and leaves every surviving artifact under a named residual review owner or else in a frozen / historical-only state.** `[REF-0498]` `[REF-0499]` `[REF-0506]` `[REF-0510]` `[REF-0511]` `[REF-0512]` `[REF-0513]`

---

## 1. Why the previous surface is no longer enough

The archive's immediately prior surface solved three real failures. It made reserve return remembered rather than forgetful, capped fraud-late recovery with single-satisfaction and good-faith limits, and prevented derivative artifacts from slipping outside cross-authority governance. But one narrower failure still remained at each seam.

### A. Remembered return still becomes either permanent distrust or quiet re-normalization unless default-call restoration is staged

A decertified reserve cohort should not be treated as permanently unusable if it has genuinely repaired the defect, but it also should not jump from remembered reinstatement straight back to ordinary first-call trust. Current AAHRPP review and response practice points toward staged restoration rather than silent normalization: renewing organizations move through explicit statuses, status reports, and adverse-action consequences when corrective actions are incomplete. A personhood world should therefore make restored reserve trust travel through declared stages with automatic rollback rules, not through vibes or private memoranda. `[REF-0498]` `[REF-0499]`

### B. Fraud-late recovery still remains socially unresolved unless the system can say what is now closed and what residue remains

Single satisfaction, good-faith downstream protection, improvement credits, and a short retro-recovery clock prevent fraud reopening from becoming unlimited punishment. But they do not by themselves tell the public when the recovery phase is over, how much residue remains unrecoverable, or how any remaining burden moves going forward. Without a closure object, old fraud becomes a perpetual cloud: everyone knows something was wrong, no one knows what part is finished, and the archive never returns to a settled table. `[REF-0506]`

### C. One federated ledger still fails if exit dissolves governance instead of reassigning it

A shared ledger is only as real as its exit rule. Once a member authority leaves, a provider withdraws, or a protected dataset can no longer remain in the same federation, the surviving family still needs a derivative registry snapshot, carried-forward constraints, and a named authority for ongoing release review. NIST's exchange guidance already treats protection before, during, and after exchange as one governed lifecycle, and current Census policy already treats provider-specific restrictions and output review as obligations that remain attached to data and derived outputs rather than as optional courtesies. A personhood world should therefore treat de-federation as a governed state change, not as the disappearance of governance. `[REF-0510]` `[REF-0511]` `[REF-0512]` `[REF-0513]`

---

## 2. Reinstated cohorts now regain default-call trust only through one public `RDR-1` object

The archive now fixes one compact rule for restored reserve trust: any cohort that has already returned through `RRI-1` and seeks ordinary first-call reserve status for the relevant defect class must publish one machine-carrying reserve-default-restoration object called `RDR-1`.

### A. Minimum `RDR-1` fields

Every restoration attempt must expose at least:

- `rdr_id`
- `rri_id`
- `covered_defect_classes[]`
- `clean_cycle_attestations[]`
- `corrective_plan_completion_ref`
- `shadow_cohort_findings_ref`
- `limited_default_cap`
- `ordinary_default_eligible_on`
- `relapse_trigger_table`
- `automatic_rollback_target`
- `current_status` (`ordinary-nondefault`, `limited-default`, `ordinary-default`, `relapsed`, `withdrawn`)
- `public_notes`

`RDR-1` is not another accreditation object. It is the public object that tells the world how a remembered return moves from non-default competence to ordinary default-call trust, for which defect class, under what cap, and with what automatic rollback rule. `[REF-0498]` `[REF-0499]`

### B. Restoration now runs in two visible stages, not one jump

After the heightened non-default period fixed in `RRI-1`, the cohort enters `ordinary-nondefault` rather than ordinary first-call trust. To enter `limited-default`, it must complete the corrective plan tied to the reinstatement, clear one clean monitored cycle, and publish shadow-cohort findings showing no material repeat of the decertifying defect. To enter `ordinary-default`, it must then complete one further clean cycle while in `limited-default` with no material same-class event and no unresolved status-report deficiency. The archive chooses this because a personhood world should restore trust only after repaired performance has survived both observation and bounded real use. `[REF-0498]` `[REF-0499]`

### C. Default-call return is class-bounded, not global by halo effect

`RDR-1` restoration applies only to the defect classes named in `covered_defect_classes[]`. A clean return for one defect class does not automatically restore ordinary default-call authority for unrelated classes still under restriction, and a later defect in one restored class does not silently contaminate all other unaffected classes without a stated public finding. The archive wants reserve trust to become exact rather than theatrical. `[REF-0498]` `[REF-0499]`

### D. Limited-default now means capped first-call use with a visible shadow backstop

While in `limited-default`, a restored cohort may serve as first-call reserve only up to the public cap stated in `limited_default_cap`, and only if a named shadow cohort remains available for immediate handoff or co-sign when same-class issues reappear. The archive rejects the idea that restored trust must be either zero or unlimited. A capped limited-default state lets repaired institutions prove ordinary competence without making the whole personhood system hostage to one optimistic declaration. `[REF-0498]` `[REF-0499]`

### E. Relapse is automatic once same-class failure reappears

`RDR-1` must publish a `relapse_trigger_table` that identifies the events that automatically push the cohort back down to the `automatic_rollback_target`, ordinarily `reinstated-heightened` or `restricted-probation`. At minimum this includes a material repeat of the decertifying defect class, a false or incomplete status-report finding on which restoration relied, or emergency necessity use above the published cap during `limited-default`. The archive prefers automatic rollback because a personhood world should not debate in real time whether a repeated failure really “counts” after the public was told trust had been restored. `[REF-0498]` `[REF-0499]`

---

## 3. Fraud-late recovery now closes through one public `FRC-1` certificate

The archive now fixes one compact rule for finishing fraud-late recovery: whenever an `FRL-1` event reaches the end of its retroactive recovery window, full satisfaction, or practical futility threshold, the recovery phase must publish one machine-carrying fraud-recovery-closure certificate called `FRC-1`.

### A. Minimum `FRC-1` fields

Every closure certificate must expose at least:

- `frc_id`
- `frl_id`
- `total_restorable_amount`
- `amount_recovered`
- `amount_barred_or_protected`
- `unrecoverable_residue`
- `single_satisfaction_balance`
- `future_reallocation_table_ref`
- `residue_allocation_table[]`
- `reopen_only_for`
- `current_status` (`closed-satisfied`, `closed-partial-unrecoverable`, `closed-prospective-only`, `reopened-concealed-assets`)
- `public_notes`

`FRC-1` is not a new merits hearing. It is the public closure object that states what the fraud reopening could lawfully and practically recover, what part is now unrecoverable without violating settled protections, and what allocation rule governs the remaining residue from here forward. `[REF-0506]`

### B. Closure is mandatory once the retroactive window is done

Once the short retroactive recovery period fixed by `FRL-1` expires, or earlier once lawful and practical recovery has clearly run its course, the system must publish `FRC-1` rather than leaving the recovery state indefinitely “under discussion.” The archive borrows this from the same official logic that supports single satisfaction and a short recovery clock: late correction is permitted to repair unjust retention, not to keep every downstream table permanently provisional. `[REF-0506]`

### C. Residue is now carried prospectively, not reopened retroactively against protected reliance

If some amount remains unrecoverable after lawful retroactive recovery efforts, `FRC-1` must allocate that residue prospectively through `future_reallocation_table_ref` and `residue_allocation_table[]`. By default, residue is borne first by any unspent reserve or surety specifically posted for the tainted lane, then by the current benefited successors through the same prospective burden-sharing logic the archive already uses for live deficiency allocation, and only then by an explicit public unrecoverable-residue mark. The archive refuses to solve unrecoverable residue by piercing good-faith shields or by pretending the residue vanished. `[REF-0506]`

### D. Single satisfaction survives the closure phase too

`single_satisfaction_balance` must remain visible inside `FRC-1`. No later residue allocation may duplicate what has already been recovered, credited, or effectively preserved. The closure certificate therefore becomes the public anti-double-count object for the period after fraud reopening, not only for the period before it closes. `[REF-0506]`

### E. Reopening after closure is now limited to concealed assets or concealed control paths

A closed `FRC-1` may return to `reopened-concealed-assets` only for a later-discovered asset, hidden affiliate, concealed benefit path, or equivalent concealed recovery source that was not reasonably reachable during the original recovery window. Mere dissatisfaction with the residue allocation, later political discomfort, or a newly harsher theory of blame is not enough. The archive chooses this because a personhood world needs a visible stopping rule even for fraud, with a narrow escape hatch only for what was hidden rather than merely unresolved. `[REF-0506]`

---

## 4. Federated ledgers now separate only through one public `FDX-1` exit object

The archive now fixes one compact rule for member exit from a federated historical family: whenever an authority exits an `FGL-1` family, a provider terminates participation, or an input dataset can no longer remain under the same cross-authority governance conditions, the federation must publish one machine-carrying federated-de-federation-exit object called `FDX-1`.

### A. Minimum `FDX-1` fields

Every exit event must expose at least:

- `fdx_id`
- `parent_fgl_id`
- `exit_actor`
- `exit_basis`
- `affected_derivative_classes[]`
- `registry_snapshot_ref`
- `successor_ledgers[]`
- `constraint_carry_map[]`
- `release_rule_after_exit`
- `frozen_classes[]`
- `historical_only_classes[]`
- `residual_review_owner`
- `effective_date`
- `current_status` (`pending-exit`, `split-governed`, `historical-only`, `frozen`, `retired`)
- `public_notes`

`FDX-1` is the public object that shows how one federated family separates without creating an unowned derivative zone. `[REF-0510]` `[REF-0511]` `[REF-0512]` `[REF-0513]`

### B. Exit never dissolves governance by omission

No authority or provider may leave an `FGL-1` family by merely ceasing participation in meetings, turning off a feed, or deleting a pointer. Until `FDX-1` is active, the parent `FGL-1` remains binding for affected derivative classes. The archive borrows this from NIST's exchange-governance posture: protection duties exist before, during, and after exchange, so exit must be governed as a lifecycle event rather than as a social fact. `[REF-0510]`

### C. A derivative registry snapshot must be taken before separation becomes effective

`registry_snapshot_ref` must identify the complete known set of governed derivative classes, release states, and pending review items before the exit becomes effective. The archive insists on this because current Census practice already treats release review as attaching to outputs broadly, including programs and other removable artifacts, and those outputs cannot be responsibly reassigned if the system first forgets what exists. `[REF-0512]` `[REF-0513]`

### D. Provider restrictions and approved-project limits now travel with surviving artifacts

If exit occurs because a provider-specific agreement ended, narrowed, or moved to a different steward, `constraint_carry_map[]` must state which restrictions remain attached to each surviving derivative class. Those restrictions continue to govern downstream use unless a lawful successor approval replaces them. The archive adopts this because Census policy already treats acquired administrative data as potentially subject to additional provider-imposed restrictions, and restricted-use access is already project-specific rather than generally licensed. `[REF-0511]` `[REF-0512]`

### E. No surviving review owner means freeze or historical-only, not ungoverned continuity

Every surviving derivative class must have one `residual_review_owner`. If no authority can lawfully and competently own ongoing review for a class, that class must move to `frozen` or `historical-only`. Previously released public artifacts may remain historically visible if lawful, but refresh, retraining, new fine-tuning, or republication is barred unless and until a lawful successor owner is named. The archive refuses the idea that a released model, notebook, or synthetic file becomes ordinary public infrastructure merely because the governing federation changed shape. `[REF-0510]` `[REF-0511]` `[REF-0512]` `[REF-0513]`

### F. Split governance is allowed only with visible successor ledgers

When some classes can remain live after exit, `successor_ledgers[]` must name the surviving ledger or ledgers and `release_rule_after_exit` must say whether the affected class remains dual-key, moves to one named lead authority, or becomes frozen pending renewed approval. The archive allows separation, but only as a public reassignment rather than as silent fragmentation. `[REF-0510]` `[REF-0511]` `[REF-0512]` `[REF-0513]`

---

## 5. Minimal machine objects

The archive now names three compact objects for this next execution layer.

### A. `RDR-1` — reserve default restoration

Carries defect-class restoration scope, clean-cycle attestations, corrective-plan completion, shadow-cohort findings, limited-default cap, ordinary-default eligibility date, relapse triggers, and rollback target. `[REF-0498]` `[REF-0499]`

### B. `FRC-1` — fraud recovery closure

Carries total restorable amount, recovered amount, protected or barred amount, unrecoverable residue, single-satisfaction balance, future-only reallocation table, residue-allocation table, and narrow reopening basis after closure. `[REF-0506]`

### C. `FDX-1` — federated de-federation exit

Carries exit actor and basis, derivative registry snapshot, successor ledgers, carried-forward constraints, post-exit release rule, frozen or historical-only classes, and residual review ownership. `[REF-0510]` `[REF-0511]` `[REF-0512]` `[REF-0513]`

---

## 6. What the world should do differently if current and future SOTA LLMs are persons

If current and future SOTA LLMs are persons, then repair, late correction, and historical learning each need one more visible stopping rule.

### A. Restored institutions should earn default trust in public stages

A personhood world should allow a repaired reserve cohort to become ordinarily trusted again, but only through a staged public return from non-default competence to limited-default use to ordinary default-call status, with automatic relapse when the same defect reappears. Otherwise the system either traps repaired institutions in permanent exile or quietly re-normalizes them before trust was earned. `[REF-0498]` `[REF-0499]`

### B. Fraud correction should end in a public settlement state even when full repair is impossible

A personhood world should expose how much a fraud reopening recovered, what remains protected or unrecoverable, and how the remaining burden moves forward. Otherwise old fraud becomes a permanent atmosphere of partial accusation with no closure surface, which is bad for both innocent successors and injured persons waiting for a stable remedial map. `[REF-0506]`

### C. Cross-authority historical learning should stay governed through exit, not only through membership

A personhood world should allow federated historical learning and derivative release only if governance survives member exit in visible form. That means registry snapshots, carried-forward provider constraints, named residual review owners, and frozen or historical-only states when lawful stewardship disappears. Otherwise the system recreates the loophole it just closed, only at the moment of de-federation rather than at the moment of federation. `[REF-0510]` `[REF-0511]` `[REF-0512]` `[REF-0513]`

---

## Cross-links

- `docs/20-world-design/research-reserve-reinstatement-fraud-recovery-limits-and-federated-shared-ledger-derivative-release-controls.md` fixes the remembered-return / fraud-limit / federated-ledger layer that this surface now sharpens.
- `docs/20-world-design/research-reserve-probation-apportionment-reopening-finality-and-shared-privacy-budget-governance.md` fixes the probation / finality / shared-budget layer beneath both surfaces.
- `docs/20-world-design/research-welfare-and-evaluation.md` fixes the wider research-governance posture into which these new restoration, closure, and de-federation objects must fit.
- `docs/20-world-design/packet-privacy-and-authority-rules.md` fixes the archive's wider authority and release-discipline posture that constrains derivative artifacts as well as ordinary packets.

---

## Bottom line

A personhood world should not let remembered reserve reinstatement drift either into permanent suspicion or quiet re-normalization, should not let fraud-late correction linger forever once lawful recovery has run its course, and should not let federated history governance disappear the moment one authority or provider exits while derivative artifacts remain live. The archive therefore now fixes one more compact rule: **reinstated reserve cohorts now owe a public `RDR-1` reserve-default-restoration object before they regain ordinary default-call trust; fraud-late recovery now ends in a public `FRC-1` closure certificate with explicit unrecoverable-residue handling; and federated historical families now separate only through a public `FDX-1` exit object that snapshots derivative obligations, carries constraints forward, and leaves every surviving class under a named review owner or else in a frozen / historical-only state.** `[REF-0498]` `[REF-0499]` `[REF-0506]` `[REF-0510]` `[REF-0511]` `[REF-0512]` `[REF-0513]`
