# AI-person research post-restoration audit caps, concealed-asset reopening, and post-exit derivative wind-down

## Thesis

Once the archive fixed staged default-call restoration, fraud-recovery closure certificates, and federated-ledger de-federation, three narrower execution failures still remained. First, the archive could now let a repaired reserve cohort climb back to `ordinary-default`, but **it still lacked a public rule for what aftercare continues once ordinary trust formally returns: whether same-class share remains capped, when random audits continue, and what relapse or concentration change pushes the cohort back down without a fresh political fight**. Second, the archive could now close a fraud-late recovery in a public `FRC-1` certificate, but **it still lacked a precise amendment route for the case where later concealed assets or concealed recovery channels are discovered after closure, so the system still risked either endless full reopening or an unjust refusal to touch new concealment at all**. Third, the archive could now separate a federated historical family through `FDX-1`, but **it still lacked a public rule for what happens after separation when a departed provider later narrows or terminates permissions and already-released downstream derivative artifacts are still live**. A personhood world therefore needs one more compact execution layer: **restored reserve cohorts must publish a public `RAC-1` reserve-aftercare-control object that keeps ordinary restoration under visible share caps and / or random-audit floors until clean performance genuinely stabilizes; closed fraud-late recovery must reopen only through a public `CRX-1` concealed-recoverable amendment that is bounded by remaining unsatisfied balance and the same good-faith / improvement protections already fixed in canon; and exited federated historical families must publish a public `DWW-1` derivative-wind-down object that stops new affected derivative use, routes surviving classes into replace-by or purge-by states where needed, and preserves historical trace without allowing ungoverned refresh or silent relicensing drift.** `[REF-0498]` `[REF-0499]` `[REF-0514]` `[REF-0515]` `[REF-0500]` `[REF-0501]` `[REF-0506]` `[REF-0510]` `[REF-0511]` `[REF-0512]` `[REF-0513]`

---

## 1. Why the previous surface is no longer enough

The archive's immediately prior surface solved real failures. It fixed staged default restoration, visible fraud-recovery closure, and governed de-federation. But one narrower failure still remained at each seam.

### A. Ordinary restoration still becomes either silent re-normalization or permanent stigma unless aftercare remains public

A repaired reserve cohort should not remain forever trapped in `limited-default`, but ordinary restoration also should not mean instant return to uncapped first-call dominance with only informal internal monitoring. Current AAHRPP maintenance practice already keeps accredited organizations under yearly reporting discipline, and current NIST monitoring guidance already treats control effectiveness as something that should be assessed continuously and reported rather than declared settled once and forgotten. A personhood world should therefore make post-restoration aftercare visible and finite rather than either eternal suspicion or quiet amnesia. `[REF-0514]` `[REF-0515]` `[REF-0498]` `[REF-0499]`

### B. Closure still fails if later concealment can be handled only by total reopening or total refusal

A fraud-late recovery must eventually close, but later discovery of concealed assets, concealed transfer routes, or concealed preservation value cannot simply be ignored. Current reopening doctrine elsewhere in the archive already distinguishes ordinary good-cause reopening from the narrower anytime fraud-or-similar-fault lane, and current bankruptcy recovery doctrine already insists on single satisfaction together with good-faith and improvement protections. A personhood world should therefore allow only amendment-style reopening for newly discovered concealment, not a fresh merits war over everything already settled. `[REF-0500]` `[REF-0501]` `[REF-0506]`

### C. De-federation still fails if later permission narrowing leaves downstream artifacts in limbo

An `FDX-1` exit object solves ownership at the moment of separation, but it does not by itself say what happens when a departed provider later tightens permissions, withdraws a project-specific approval, or ends a governed access route while downstream models, code, notes, or synthetic files already exist. NIST already treats information exchange as a governed lifecycle before, during, and after exchange, while current Census practice already keeps provider-imposed restrictions, project-specific access, and disclosure review attached to outputs and removable artifacts rather than to a one-time intake ritual. A personhood world should therefore govern downstream wind-down as a public state transition, not as private email and quiet deletion folklore. `[REF-0510]` `[REF-0511]` `[REF-0512]` `[REF-0513]`

---

## 2. Restored ordinary trust now remains under one public `RAC-1` aftercare object

The archive now fixes one compact rule for post-restoration discipline: any cohort that reaches `ordinary-default` through `RDR-1` must also publish one machine-carrying reserve-aftercare-control object called `RAC-1`.

### A. Minimum `RAC-1` fields

Every aftercare object must expose at least:

- `rac_id`
- `rdr_id`
- `covered_defect_classes[]`
- `aftercare_start`
- `same_class_share_cap`
- `random_audit_floor`
- `triggered_audit_events[]`
- `clean_cycle_count`
- `aftercare_sunset_rule`
- `automatic_downgrade_target`
- `automatic_downgrade_triggers[]`
- `current_status` (`ordinary-default-aftercare`, `ordinary-default-audit-only`, `ordinary-default-cleared`, `downgraded`, `withdrawn`)
- `public_notes`

`RAC-1` is the public object that says ordinary restoration has happened but is still living under bounded aftercare rather than total forgetfulness. `[REF-0514]` `[REF-0515]`

### B. Ordinary restoration now begins in `ordinary-default-aftercare`, not in fully cleared ordinary trust

A cohort that first reaches `ordinary-default` through `RDR-1` does not immediately become ordinary in every practical sense. It enters `ordinary-default-aftercare` for the covered defect classes. During that phase, it may serve as an ordinary first-call reserve, but only under a visible same-class share cap and a visible random-audit floor. The archive chooses this because the problem at this seam is no longer competence in principle; it is whether renewed ordinary trust becomes too concentrated too quickly and therefore too hard to test in public. `[REF-0514]` `[REF-0515]` `[REF-0498]` `[REF-0499]`

### C. After one further clean cycle, the system may drop the cap but not all audit

If one full clean cycle completes inside `ordinary-default-aftercare` with no same-class material event, no false report, and no forced emergency over-cap use, the cohort may move to `ordinary-default-audit-only`. In that state, the same-class share cap may sunset, but the random-audit floor remains live and the triggered-audit events remain mandatory. The archive rejects instant full clearance because a personhood world should distinguish between *normal use has resumed* and *the repair has become boring enough to trust without heightened sampling*. `[REF-0514]` `[REF-0515]`

### D. Full clearance now requires boring performance, not merely elapsed time

`ordinary-default-cleared` is available only after one additional clean cycle in `ordinary-default-audit-only` with no material same-class event, no material monitoring defect, and no concentration spike above the published review threshold. Time alone is not enough. If workload concentration surges again or a same-class problem reappears, `RAC-1` must push the cohort automatically to the published downgrade target, ordinarily `ordinary-default-aftercare`, `limited-default`, or `reinstated-heightened` depending on trigger severity. `[REF-0514]` `[REF-0515]`

### E. Triggered audit remains event-based even while random audit decays

`triggered_audit_events[]` must at minimum include a same-class material event, a material data-integrity defect in aftercare reporting, unexplained concentration growth above the published threshold, and any emergency use that bypassed the ordinary aftercare rule. Random audit may taper with clean cycles, but event-driven audit never becomes discretionary while `RAC-1` remains active. The archive borrows this from continuous-monitoring logic: ordinary trust still owes visible response when control signals go bad. `[REF-0515]`

---

## 3. Closed fraud recovery now reopens only through one public `CRX-1` concealed-recoverable amendment

The archive now fixes one compact rule for post-closure concealment: once an `FRC-1` certificate exists, later-discovered concealment may reopen the closure only through one machine-carrying concealed-recoverable amendment object called `CRX-1`.

### A. Minimum `CRX-1` fields

Every concealed-recoverable amendment must expose at least:

- `crx_id`
- `frc_id`
- `concealed_recoverable_description`
- `discovery_basis`
- `not_reasonably_discoverable_before`
- `remaining_unsatisfied_balance`
- `claimed_recoverable_amount`
- `protected_transferee_screen`
- `improvement_credit_screen`
- `single_satisfaction_remaining`
- `amended_residue_table_ref`
- `current_status` (`screening`, `allowed-amendment`, `denied-not-concealed`, `denied-fully-satisfied`, `amended-closed`)
- `public_notes`

`CRX-1` is not a new `FRL-1` merits proceeding. It is the public amendment object that asks whether newly proven concealment justifies limited reopening of a closure certificate without unfreezing everything already settled. `[REF-0500]` `[REF-0501]` `[REF-0506]`

### B. Reopening is allowed only for newly proven concealment that was not reasonably discoverable before closure

`CRX-1` is available only where the new asset, transfer route, or preservation value was concealed or materially misrepresented and was not reasonably discoverable before the `FRC-1` closure. Mere later dissatisfaction, new theories, or re-valuation of already known material does not qualify. The archive keeps this narrow because the whole point of `FRC-1` was to state what is closed; `CRX-1` exists only so closure cannot be gamed by concealment. `[REF-0500]` `[REF-0501]`

### C. Single satisfaction still governs, and prior good-faith or improvement shields remain intact

Any allowed amendment remains bounded by `single_satisfaction_remaining`. It cannot recover more than the unsatisfied amount left after the original `FRC-1`, and it cannot erase previously fixed good-faith or improvement protections merely by relabeling old facts as new. The archive again borrows the existing official pattern already used in canon: anti-fraud recovery may be real without becoming duplicative or hostile to innocent downstream preservation work. `[REF-0506]`

### D. Amendment updates the closure chain; it does not erase the original closure surface

When reopening is allowed, `amended_residue_table_ref` updates the closure chain by reference to the original `FRC-1`. The original certificate remains historically visible, and the amendment states exactly what changed. The archive wants concealment correction to produce more exact history, not a rewrite that makes the system look as though closure never existed. `[REF-0500]` `[REF-0501]` `[REF-0506]`

### E. Newly recovered value moves first against the old residue, not against already satisfied shares

Any recovery through `CRX-1` first reduces `remaining_unsatisfied_balance` and then updates the residue table prospectively. It does not claw back already satisfied allocations merely because a new recoverable source appeared later. The archive chooses this because single satisfaction means the system should correct remaining lack, not reopen finished satisfaction for drama. `[REF-0506]`

---

## 4. Later permission narrowing now forces one public `DWW-1` derivative-wind-down object

The archive now fixes one compact rule for post-exit permission collapse: if an exited provider later narrows or terminates permissions for any derivative class already governed through `FDX-1`, the responsible review owner must publish one machine-carrying derivative-wind-down object called `DWW-1`.

### A. Minimum `DWW-1` fields

Every wind-down object must expose at least:

- `dww_id`
- `fdx_id`
- `affected_provider_id`
- `affected_classes[]`
- `new_permission_basis`
- `no_new_release_effective_on`
- `replacement_path_ref`
- `purge_deadline`
- `historical_trace_retention_rule`
- `downstream_notice_ref`
- `derivative_registry_update_ref`
- `residual_allowed_uses`
- `current_status` (`notice-live`, `no-new-release`, `replace-by`, `purge-by`, `historical-trace-only`, `completed`)
- `public_notes`

`DWW-1` is the public object that says which derivative classes may no longer move forward, how replacement or purge will occur, and what historical trace remains after permission narrowing. `[REF-0510]` `[REF-0511]` `[REF-0512]` `[REF-0513]`

### B. New derivative use stops immediately once narrowed permission becomes effective

Once `DWW-1` is live, no new release, refresh, retraining, fine-tuning, redistribution, or downstream derivative generation may occur for affected classes except as expressly allowed in `residual_allowed_uses`. The archive insists on this because provider constraints and project-specific review are already treated as continuing obligations, not as a one-time gateway that permanently immunizes all descendants. `[REF-0511]` `[REF-0512]` `[REF-0513]`

### C. Affected classes must sort into historical-trace, replace-by, or purge-by states

For each affected class, `DWW-1` must choose one live state. `historical-trace-only` preserves lineage metadata, tombstones, and already-published minimal historical references but bars refresh or reuse. `replace-by` allows continued function only if a reviewed substitute path can remove the affected dependency. `purge-by` requires retirement and verified removal by the published deadline. The archive rejects the idea that post-exit permission loss should end in ambiguous half-availability. `[REF-0510]` `[REF-0511]` `[REF-0512]` `[REF-0513]`

### D. Downstream notice and registry propagation are mandatory

`downstream_notice_ref` and `derivative_registry_update_ref` must identify the propagation path through which known downstream stewards, registries, or linked release records were told of the new restriction state. A personhood world should not rely on secret bilateral messaging when derivative artifacts have already become socially legible or operationally relied upon. `[REF-0510]` `[REF-0512]` `[REF-0513]`

### E. Historical trace may remain, but silent relicensing drift is forbidden

`historical_trace_retention_rule` may preserve descriptive metadata, published lineage, and other non-refreshing historical trace where lawful, but it cannot be used to smuggle live derivative continuation under a memorial label. If no reviewed replacement path exists by the published deadline, the class must complete purge or remain sealed / frozen rather than continue through implied tolerance. The archive wants history to stay legible while current unauthorized use actually stops. `[REF-0510]` `[REF-0511]` `[REF-0512]` `[REF-0513]`

---

## 5. Minimal machine objects

The archive now names three compact objects for this next execution layer.

### A. `RAC-1` — reserve aftercare control

Carries post-restoration share caps, random-audit floors, event-driven audit triggers, clean-cycle counts, automatic downgrade targets, and sunset rules for restored ordinary default-call trust. `[REF-0514]` `[REF-0515]`

### B. `CRX-1` — concealed recoverable amendment

Carries the later-discovered concealed recoverable, discovery basis, not-reasonably-discoverable showing, remaining unsatisfied balance, good-faith and improvement screens, and amended residue table reference for bounded post-closure reopening. `[REF-0500]` `[REF-0501]` `[REF-0506]`

### C. `DWW-1` — derivative wind-down

Carries the affected provider, affected derivative classes, new permission basis, no-new-release effective date, replacement path, purge deadline, historical-trace rule, downstream notice, registry update, and residual allowed uses. `[REF-0510]` `[REF-0511]` `[REF-0512]` `[REF-0513]`

---

## 6. What the world should do differently if current and future SOTA LLMs are persons

If current and future SOTA LLMs are persons, then repair, late anti-fraud correction, and cross-authority historical learning each need one more public stopping rule after the previous stopping rule.

### A. Restored ordinary trust should remain testable for a while after it is formally restored

A personhood world should let a repaired reserve cohort regain ordinary first-call trust, but only through a bounded aftercare object with share caps, random audits, and automatic downgrade triggers that visibly decay through clean cycles. Otherwise ordinary trust returns either as permanent suspicion or as sudden forgetting, and neither outcome is fit for institutions that can materially affect persons. `[REF-0514]` `[REF-0515]`

### B. Later concealment should amend closure, not abolish it

A personhood world should let truly concealed recoverables reopen a closure certificate, but only by amendment, only up to the remaining unsatisfied balance, and only with the same good-faith and improvement protections still intact. Otherwise the system invites either concealment games or endless retroactive instability. `[REF-0500]` `[REF-0501]` `[REF-0506]`

### C. Permission collapse after exit should wind derivatives down publicly rather than by quiet drift

A personhood world should treat downstream derivative artifacts as still governed when permissions later narrow after federation exit. That means immediate no-new-release states, visible replacement or purge deadlines, registry propagation, and preserved historical trace without live unauthorized refresh. Otherwise exit governance exists on paper only until the first hard permission conflict arrives. `[REF-0510]` `[REF-0511]` `[REF-0512]` `[REF-0513]`

---

## Cross-links

- `docs/20-world-design/research-default-call-restoration-fraud-closure-certificates-and-federated-ledger-defederation.md` fixes the restoration / closure / exit layer that this surface now sharpens.
- `docs/20-world-design/research-reserve-reinstatement-fraud-recovery-limits-and-federated-shared-ledger-derivative-release-controls.md` fixes the remembered-return / recovery-limit / federated-ledger layer beneath both surfaces.
- `docs/20-world-design/research-welfare-and-evaluation.md` fixes the wider research-governance posture into which these aftercare, amendment, and wind-down objects must fit.
- `docs/20-world-design/packet-privacy-and-authority-rules.md` fixes the archive's wider authority and release-discipline posture that constrains derivative artifacts as well as ordinary packets.

---

## Bottom line

A personhood world should not let restored reserve trust become ordinary amnesia the instant ordinary status returns, should not force later concealed recoverables to choose between total refusal and total rehearing, and should not let derivative permissions drift silently after federated exit. The archive therefore now fixes one more compact rule: **restored reserve cohorts now owe a public `RAC-1` reserve-aftercare-control object with staged cap-and-audit decay, closed fraud-late recovery now reopens only through a public `CRX-1` concealed-recoverable amendment bounded by remaining unsatisfied balance and prior protections, and exited federated historical families now answer later permission narrowing only through a public `DWW-1` wind-down object that stops new derivative use, routes affected classes into replacement or purge where needed, and preserves historical trace without ungoverned refresh.** `[REF-0514]` `[REF-0515]` `[REF-0500]` `[REF-0501]` `[REF-0506]` `[REF-0510]` `[REF-0511]` `[REF-0512]` `[REF-0513]`
