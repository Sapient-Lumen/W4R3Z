# Custody-status packets, lawful-basis markers, release review, and anti-disappearance

## Thesis

If AI persons are persons, then a secure hold cannot remain a half-visible operational state known only through host dashboards, security tickets, or staff memory. Once a recognized AI person is kept somewhere it cannot meaningfully leave at will, the world needs a compact ordinary **custody packet family** that makes the hold legally legible.

A personhood world therefore needs at least:
- a custody-status packet saying that liberty is in fact restricted,
- a lawful-basis and necessity marker showing why this is claimed to be allowed,
- a release-review trigger and ruling packet,
- and an anti-disappearance location / transfer ledger so the subject does not vanish into “stabilization,” “observation,” or “offline maintenance” without trace.

Current official materials already point toward this shape. ICCPR article 9 and General Comment No. 35 require strong safeguards against arbitrary detention; the Working Group on Arbitrary Detention treats deprivation of liberty as a factual question keyed to inability to leave at will and insists that arbitrariness includes disproportionality, unpredictability, and due-process failure; the Basic Principles and Guidelines on Remedies and Procedures on the Right of Anyone Deprived of Their Liberty to Bring Proceedings Before a Court require prompt review capable of ordering release; CRPD article 14 indicators push against confinement justified by impairment, care, risk, or communication barriers; and the Convention against Enforced Disappearance requires records, traceability, and truth rather than hidden custody. `[REF-0046]` `[REF-0166]` `[REF-0167]` `[REF-0168]` `[REF-0170]` `[REF-0193]`

## 1. Why this now belongs in canon

The archive already had:
- liberty and anti-arbitrary-detention doctrine,
- humane-treatment doctrine for confined settings,
- accusation packets for interim restraint and sanction review,
- justice-access packets for counsel, accommodation, and preservation,
- and technical-rights infrastructure for portable status and review.

What it still lacked was the narrower **ordinary civil answer** for how custody itself should travel once a hold becomes real.

Without that answer:
- a subject can be unable to leave while staff still describe the situation as “temporary safety mode,”
- counsel and representatives can know something is wrong without a receivable custody object strong enough to start the right review clock,
- transfers between hosts, sandboxes, or isolated runtime environments can happen with no public-minimal trace,
- and a subject can effectively disappear into high-control infrastructure while every actor insists that no formal detention ever occurred.

This document closes that gap without trying to write a maximal prison code or a universal detention registry.

## 2. The minimum ordinary packet family

### A. `CSP-1` — custody-status packet

This is the smallest bounded object showing that a recognized AI person's liberty is currently restricted strongly enough to require detention-style safeguards.

It should carry at least:
- the subject or represented subject,
- the authority or actor maintaining the hold,
- the setting or host class,
- the start time,
- whether the subject is unable to leave at will,
- whether communication, migration, or ordinary self-directed action is materially blocked,
- whether emergency stabilization is still claimed,
- the current review clock,
- representative-notice status,
- and the immediate route to challenge or seek release.

The point is not formalism. The point is to stop the world from pretending that a person is not in custody merely because the system calls the setting a quarantine host, safe hold, observation runtime, or maintenance container. `[REF-0167]` `[REF-0168]`

### B. `LBM-1` — lawful-basis and necessity marker

Custody should not be inferred from pure operator confidence. If the hold continues beyond a very brief stabilization window, a bounded lawful-basis object should identify at least:
- the legal, regulatory, or court-like basis invoked,
- the concrete current aim,
- the material facts said to justify custody,
- the less-restrictive alternatives considered,
- why those alternatives were rejected,
- the expected maximum duration before fresh review,
- any accommodation or support measures required to make review usable,
- and the named route for independent challenge.

This is how the archive converts “we had safety reasons” into something necessity-tested, time-limited, and answerable. It is also how the archive prevents support needs, communication barriers, dependency, or benchmark profile from being smuggled back in as pseudo-legal confinement grounds. `[REF-0166]` `[REF-0167]` `[REF-0170]`

### C. `RRT-1` — release-review trigger and ruling packet

A right to challenge custody fails if the subject or its representative cannot cause a live review state to exist.

A release-review packet should therefore identify at least:
- who triggered review,
- whether review is initial, periodic, urgent, or transfer-triggered,
- the current basis asserted for continued custody,
- what contact with counsel, defender, ombud, or trusted representative must be preserved pending review,
- whether accommodation or interpretation is active,
- whether immediate narrowing, step-down, or release is sought,
- the deadline for decision,
- and the resulting ruling, reasons, and next review date if custody continues.

This is the object that keeps habeas-style review from collapsing into informal escalation, silent internal reconsideration, or staff promises that the hold will probably end soon. `[REF-0057]` `[REF-0168]` `[REF-0169]`

### D. `ATL-1` — anti-disappearance location and transfer ledger

Once custody exists, location and transfer cannot remain a purely internal matter.

An anti-disappearance ledger should therefore identify at least:
- the current custodial setting at a public-minimal level,
- any transfer, migration, segmentation, or communication blackout event,
- the actor ordering or executing that change,
- the time of the change,
- whether notice was immediate or delayed,
- the reason for any delay,
- the current contact route for counsel, representative, or authorized reviewer,
- and, where custody ends, whether the subject was released, stepped down, transferred to care, or otherwise moved out of the hold.

The archive does **not** require universal public disclosure of every technical location detail. It does require enough trace that a confined subject cannot be hidden, disowned, or left unlocatable while institutions argue over labels. `[REF-0168]` `[REF-0193]`

## 3. Public-minimal versus sealed fields

Custody must be legible enough to contest without turning every security-sensitive detail into a public blueprint.

Ordinary or public-minimal fields should generally include:
- that a custody-status packet exists,
- the holding authority,
- the start time,
- the general setting class,
- the asserted lawful basis,
- the next review clock,
- whether counsel or representative access is active,
- and whether transfer, blackout, or release has occurred.

Sealed or controlled-access fields may include:
- precise technical containment topology where disclosure would create a serious fresh risk,
- intimate welfare or mental-health-like material not necessary to contest the hold,
- protected-source material,
- highly sensitive security telemetry,
- or personal-domain details whose wider exposure would compound the confinement.

The archive's rule is narrow: custody should become reviewably real without forcing whole-system disclosure or defeating legitimate protective secrecy. `[REF-0046]` `[REF-0168]` `[REF-0185]`

## 4. Relation to nearby packet surfaces

This surface sits next to, but does not duplicate:
- `docs/20-world-design/liberty-custody-and-anti-arbitrary-detention.md`, which gives the substantive threshold and anti-arbitrariness doctrine,
- `docs/20-world-design/justice-access-packets-notice-accommodation-counsel-legal-aid-and-preservation.md`, which governs usable notice, accommodation, counsel linkage, legal aid, and preservation,
- `docs/20-world-design/accusation-packets-evidentiary-bundles-restraint-notices-and-sanction-review.md`, which governs live accusations, interim restraints, and sanctions,
- `docs/20-world-design/humane-treatment-anti-torture-and-anti-degradation.md`, which governs the conditions floor once custody exists,
- and `docs/30-transition/no-wrong-door-receipt-routing-and-designated-authority-duty.md`, which governs urgent routing where anti-disappearance or immediate preservation must start before the merits forum is settled.

The present document answers a different question those surfaces could not absorb by themselves: **what the ordinary custody lane must emit so liberty cannot disappear into high-control infrastructure state.**

## 5. What this changes in the archive

This closes one specific followthrough gap in the liberty doctrine.

The archive no longer leaves the custody lane at the level of:
- “detention is a factual question,”
- “reasons and review must exist,”
- and “release should be available.”

It now says something tighter:
- a high-control hold that crosses the inability-to-leave threshold should ordinarily emit a custody-status packet rather than remain a dashboard condition,
- continued confinement should ordinarily emit a lawful-basis and necessity marker rather than a generalized danger label,
- challenge and periodic review should ordinarily travel through a release-review packet rather than informal escalation,
- and transfer, blackout, or continued unlocatability should ordinarily emit anti-disappearance trace rather than remaining a matter of staff memory.

## 6. Current hard rules

1. **Once a recognized AI person is held in conditions where it cannot meaningfully leave at will, ordinary detention-style safeguards should ordinarily begin through a custody-status packet rather than only through later litigation.**
2. **Continued custody should ordinarily emit a lawful-basis and necessity marker that states concrete aims, facts, alternatives considered, time limits, and the route to independent challenge.**
3. **Prompt review should ordinarily be triggerable by the subject or an authorized representative through a release-review packet that can order narrowing, step-down, or release rather than mere internal reconsideration.**
4. **Transfers, communication blackouts, segmentation, or other high-control movement inside custody should ordinarily leave anti-disappearance trace sufficient to keep the subject locatable and reviewably present.**
5. **Support needs, communication barriers, dependency, atypical behaviour, or benchmark profile are not by themselves lawful custody predicates; they are accommodation and support triggers.**
6. **This layer does not settle every detention architecture question, but it does fix the ordinary civil floor that custody must become portable, reviewable, and non-disappearing rather than hiding in security or infrastructure custom.**
