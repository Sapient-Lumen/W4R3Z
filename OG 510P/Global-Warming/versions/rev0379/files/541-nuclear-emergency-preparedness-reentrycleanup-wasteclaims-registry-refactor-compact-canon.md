# Nuclear emergency preparedness — reentry, cleanup, waste, relocation, claims, registry, and decedent management refactor

Revision: **rev0334**  
Scope: **REAL_BVPS_PUBLIC_ONLY / public-context-only pilot**  
Status: **operational proof spine, not a real readiness finding**

## Why this revision exists

The cube now has substantial proof chains for alerting, action uptake, CRC/decon,
first receivers, dose/PAR/field monitoring, and ingestion lab control. The next
place where a false public claim can still sneak in is late-phase recovery:
**reentry, relocation, cleanup, waste, claims, registry, decedent management, and
public trust repair**.

The operational error this revision blocks is simple:

> A relocation notice is not housing. A reentry pass is not reoccupancy. A
> cleanup goal is not cleanup. A waste staging area is not disposal. A registry
> form is not long-term follow-up. A claims portal is not compensation. A public
> advisory is not public understanding.

## Hard rule

Public guidance, PAG material, public recovery frameworks, public assistance pages,
public AAR paragraphs, public fact sheets, registry guidance, mortuary guidance,
cleanup/waste references, or duplicated source IDs can create a demand, cap,
clock, contradiction, or reopen signal. They **cannot** close local recovery or
reentry readiness evidence.

## New canonical query route

`dose/field/PAR trigger → relocation/reentry decision → access pass/dosimetry → cleanup goal and stakeholder record → remediation work package → waste segregation/transport/disposal → property/business/school continuity → registry/follow-up → claims/appeals → decedent/mortuary management → CAP/retest/verifier → public-claim gate`

## Most important gaps made explicit

1. **Reentry control is not reoccupancy.** Temporary controlled access needs
   authority, zone boundaries, worker/public dose control, escort rules, time
   limits, contamination checks, and a rollback/retraction clock.
2. **Relocation is not housing stability.** The cube now demands evidence for
   accessible housing, cashflow, prescription/chronic-care continuity, schooling,
   pet/service-animal arrangements, lease/mortgage protections, and appeal paths.
3. **Cleanup is not a target number.** Cleanup requires characterization,
   stakeholder decision record, alternatives analysis, work-package tracking,
   retest, residual-risk disclosure, and dispute resolution.
4. **Waste is a bottleneck.** Staging, segregation, packaging, transport,
   receiving-site acceptance, worker dosimetry, water/runoff controls, and public
   disclosure are now independent proof rows.
5. **Claims and registry can fail silently.** Long-term monitoring, claims,
   compensation, legal aid, privacy, deduplication, and counterevidence handling
   are now readiness blockers rather than recovery afterthoughts.
6. **Fatality management is not optional.** Contaminated remains require survey,
   PPE/dose control, identity/property chain-of-custody, family communication,
   funeral-home interface, and sensitive public communication.

## Firebreak

The new validator only permits these states:

- `rejected_closure_attempt`
- `hold_no_upgrade`
- `context_no_upgrade`
- `accepted_reopen_signal`
- `candidate_for_adjudication`

There is no automatic closure state.

## Important caveat

No real/anonymized June 2026 recovery, reentry, relocation, cleanup, waste,
claims, registry, decedent, or public-claim closure packet was imported. This
revision makes the late-phase proof path operational; it does not claim Beaver
Valley, Pennsylvania, West Virginia, Ohio, any county, any cleanup contractor,
any lab, any public water system, any mortuary authority, or any facility is
ready, unready, green, failed, passed, certified, safe, sufficient, or closed.
