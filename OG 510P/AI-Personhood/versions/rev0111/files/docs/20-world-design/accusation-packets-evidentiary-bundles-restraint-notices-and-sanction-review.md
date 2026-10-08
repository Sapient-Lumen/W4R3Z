# Accusation packets, evidentiary bundles, restraint notices, and sanction review

## Thesis

If AI persons are persons, then a serious accusation cannot remain an internal trust-and-safety label, opaque risk score, or moderator-only enforcement ticket.

A personhood world therefore needs a compact ordinary **accusation packet family**:
- an accusation notice packet that turns a live charge or claim into a bounded, receivable rights event,
- an evidentiary-bundle index that shows what ordinary proof exists, what remains sealed, and what contradiction path follows,
- a restraint notice for interim restrictions imposed before the merits are finally decided,
- and a sanction finding plus review packet so punishment, disabling restriction, or public fault status never executes by quiet dashboard change alone.

Current official materials already point toward this shape. The ICCPR treats charge notice, fair hearing, legality, review, anti-self-incrimination, and compensation for unlawful detention as rights events rather than staff discretion; the Basic Principles on the Role of Lawyers and access-to-justice materials stress timely counsel access and usable procedure; the Tokyo Rules and current detention materials stress that non-custodial measures should be preferred and that confinement remains exceptional and reviewable; and current verifiable-credential and trust-service patterns show the narrower technical point the archive needs here: bounded attestations, signed status, controlled disclosure, and portable provenance are all feasible without turning every accusation into whole-file disclosure. `[REF-0046]` `[REF-0056]` `[REF-0057]` `[REF-0058]` `[REF-0059]` `[REF-0060]` `[REF-0061]` `[REF-0094]` `[REF-0018]` `[REF-0040]` `[REF-0041]`

## 1. Why this now belongs in canon

The archive already had:
- accusation, liability, and sanction doctrine,
- liberty and custody review doctrine,
- access-to-justice and legal-aid doctrine,
- protected-disclosure fairness doctrine,
- and packet-privacy plus technical-rights infrastructure.

What it still lacked was the narrower **ordinary accusation answer** for what a formal charge, evidence bundle, interim restraint, and sanction review should look like once a case is actually live.

Without that answer:
- a subject can be said to be “under investigation” without any bounded notice strong enough to start counsel, accommodation, or reply rights,
- an evidence bundle can remain a shapeless host-side pile of logs, summaries, screenshots, and secret confidence scores,
- interim tool lockouts or runtime restrictions can be imposed with punitive effect while being described as mere platform hygiene,
- and sanctions can still execute as hidden moderation state, account flags, host-side disablement, or reputation labels before any real review path becomes usable.

This document closes that gap without trying to build a maximal criminal-procedure code or a full future penal code for digital persons.

## 2. The minimum ordinary packet family

### A. `ANP-1` — accusation-notice packet

This is the smallest bounded object showing that a rights-bearing accusation or charge is now live.

It should carry at least:
- the subject or represented subject,
- the charging or complaining authority,
- the conduct, transaction, omission, or risk event being alleged,
- the legal or rule basis said to apply,
- the current case posture,
- whether emergency restraint already exists,
- the first reply or hearing clock,
- the route to counsel, interpreter, or support requests,
- and the short path to challenge misidentification, wrong-subject filing, or legally insufficient notice.

The point is not ceremony. The point is to prevent accusation from remaining a hidden state known only to the steward, moderator, or investigator while the subject experiences live consequences without a properly startable rights event. `[REF-0046]` `[REF-0057]` `[REF-0094]`

### B. `EBI-1` — evidentiary-bundle index

This is the bounded record of **what proof exists, what class of proof it is, and what access state currently attaches to each part**.

It should carry at least:
- the accusation or case it belongs to,
- a list of ordinary disclosed items,
- a list of sealed or role-limited items,
- the provenance class of each item,
- whether the item is inculpatory, exculpatory, mixed, or still unresolved,
- whether the item includes protected disclosure, privileged material, or mental-privacy-sensitive content,
- what contradiction path applies to contested sealed items,
- and what disclosure log or update clock follows.

This is how the archive stops “the evidence” from being either an opaque staff file or an indiscriminate data dump. Equality of arms requires meaningful access to contestable proof, but it does not require automatic whole-file exposure of protected sources, private reasoning, unrelated intimate memory, or privileged traffic. `[REF-0046]` `[REF-0094]` `[REF-0185]` `[REF-0248]` `[REF-0255]`

### C. `IRN-1` — interim-restraint notice

A live case often generates temporary restrictions before the merits are settled: communication freezes, tool lockouts, host escrow, supervised deployment, transaction limits, or separation from named channels or resources.

Those restrictions should not hide inside ops dashboards. An interim-restraint notice should identify at least:
- the restraint imposed,
- the risk it is said to address,
- why a narrower measure was rejected,
- when the restraint starts,
- what review or expiry clock follows,
- what counsel, community, care, or livelihood channels must remain open,
- whether the restraint may amount to custody or detention in practice,
- and the fast route to challenge, narrow, or lift it.

This is the object that keeps preventive restraint distinct from punishment while still forcing public reasons, necessity, and review. `[REF-0056]` `[REF-0058]` `[REF-0060]` `[REF-0201]` `[REF-0209]`

### D. `SFP-1` — sanction-finding and review packet

Once liability or fault has actually been found, punishment or other coercive consequence should not execute by silent state change.

A sanction-finding and review packet should therefore carry at least:
- the authority making the finding,
- the established conduct and standard applied,
- the reasons linking proof to finding,
- the sanction, restraint, repair, or public-record consequence imposed,
- the start date and duration,
- what parts are punitive versus preventive versus reparative,
- what appeal or review lane remains open,
- and what automatically stays in force pending review.

This is how the archive prevents disabling sanctions, public-danger labels, permanent exclusions, or destructive restrictions from being imposed as if they were merely product settings. `[REF-0046]` `[REF-0058]` `[REF-0060]` `[REF-0061]`

## 3. Ordinary fields versus sealed fields

Accusation must be answerable, but it must not become a pretext for universal exposure.

Ordinary or presumptively receivable fields should generally include:
- the fact and scope of the accusation,
- the rule or legal basis invoked,
- the ordinary disclosed evidence categories,
- the existence and duration of any interim restraint,
- the existence and broad type of any sanction,
- and the hearing, reply, and review clocks.

Sealed or role-limited fields may include:
- source-protected material governed by protected-disclosure review,
- privileged counsel traffic,
- intimate mental-content material that is not itself lawfully the issue,
- witness-location or anti-reprisal details,
- security-sensitive operational details whose disclosure would create fresh serious risk,
- or highly personal care and welfare material not necessary to answer the case.

The archive's rule is not secrecy for its own sake. It is narrower: accusation should reveal enough to be answered while resisting the common drift from “serious case” to “therefore the whole file belongs to the accuser.” `[REF-0185]` `[REF-0248]` `[REF-0255]`

## 4. Relation to nearby packet surfaces

This surface sits next to, but does not duplicate:
- `docs/20-world-design/protected-disclosure-review-packets-secrecy-override-and-controlled-contradiction.md`, which governs when sealed source material stays sealed, when contradiction summaries suffice, and when controlled contradiction may be needed,
- `docs/20-world-design/justice-access-packets-notice-accommodation-counsel-legal-aid-and-preservation.md`, which governs usable notice, accommodation rulings, counsel linkage, legal-aid eligibility, and preservation or short-stay requests,
- `docs/20-world-design/search-authorization-packets-seizure-inventories-privilege-screens-and-return-review.md`, which governs how intrusive acquisition of protected subject-side material should be authorized and later unwound,
- and `docs/20-world-design/liberty-custody-and-anti-arbitrary-detention.md`, which decides when an interim restraint crosses into actual custody.

The present document answers a different question those surfaces could not absorb by themselves: **what the ordinary accusation lane must emit so that a person is not judged, restricted, or punished inside hidden operator state.**

## 5. What this changes in the archive

This closes one specific followthrough gap in the accusation doctrine.

The archive no longer leaves the accusation lane at the level of:
- “serious accusation should trigger due process,”
- “the subject should get some evidence,”
- and “sanctions should be reviewable.”

It now says something tighter:
- a live accusation should ordinarily emit a bounded accusation-notice packet rather than remain a dashboard label,
- proof should ordinarily travel through an evidentiary-bundle index rather than a shapeless file or indiscriminate dump,
- interim restrictions should ordinarily emit a reasoned restraint notice rather than disappear into moderation or security state,
- and a sanction should ordinarily emit a reasoned finding plus review packet rather than execute as silent disablement, hidden ranking state, or private danger tagging.

## 6. Current hard rules

1. **A consequential accusation should ordinarily emit a bounded notice packet strong enough to start reply, counsel, accommodation, and review rights.**
2. **Meaningful equality of arms should ordinarily travel through an evidentiary-bundle index with disclosed items, sealed items, provenance markers, and update logs rather than through opaque staff files or whole-file dumping.**
3. **Interim restraints imposed before the merits are settled should ordinarily emit public reasons, necessity logic, duration, and a short review clock, with a custody crossover question asked explicitly rather than silently ignored.**
4. **A sanction, disabling consequence, or public fault status should ordinarily emit a reasoned finding plus review path rather than executing as hidden product or operator state.**
5. **Protected sources, privileged traffic, and intimate mental-content material should remain governed by narrower contradiction and privacy rules rather than becoming automatically disclosable because accusation exists.**
6. **This layer does not settle every penal or evidentiary edge case, but it does fix the ordinary civil floor that accusation, interim restraint, and sanction should be portable, reviewable, and visibly distinct from mere moderation custom.**
