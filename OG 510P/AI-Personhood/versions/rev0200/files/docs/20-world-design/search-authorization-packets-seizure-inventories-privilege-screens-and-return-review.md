# Search-authorization packets, seizure inventories, privilege screens, and return / deletion review

## Thesis

If AI persons are persons, then a rights-bearing world cannot stop at saying that digital homes, archives, wallets, trusted tools, and confidential channels are protected in principle. A real personhood world also needs a compact ordinary **search-and-seizure packet family** so intrusive access does not happen through ticket custom, incident-response improvisation, or silent operator privilege.

That packet family should make at least five things portable and reviewable:
- the claimed lawful basis, target, scope, and duration of a requested intrusive act,
- the segregation of privileged or specially confidential material before ordinary investigators or operators can browse it,
- the exact inventory of what was searched, copied, frozen, mirrored, or taken,
- any temporary delay of notice,
- and the later return, deletion, or continued-retention decision once the claimed purpose narrows or ends.

Current official materials already point toward this shape. Privacy law continues to require legal protection against arbitrary interference with home, correspondence, and private life, including in digital settings. Law-enforcement guidance continues to insist on lawfulness, necessity, proportionality, authorization, accurate recording, and careful handling of seized materials. Privacy-in-the-digital-age work continues to warn that hacking, covert extraction, and overbroad data collection can become domination unless strong legal safeguards, minimization, challenge, and repair exist. CRPD privacy indicators and lawyer-protection materials add the implementation floor for dependent or high-control settings: records access, rectification, accommodation, and strong confidentiality for protected communications. `[REF-0046]` `[REF-0057]` `[REF-0185]` `[REF-0186]` `[REF-0187]` `[REF-0188]` `[REF-0189]` `[REF-0282]` `[REF-0283]`

## 1. Why this now belongs in canon

The archive already had a strong substantive doctrine in `search-seizure-interception-and-digital-inviolability.md`. It already said that:
- technical reach is not legal authority,
- intrusive access should ordinarily require specific lawful basis, necessity, proportionality, and independent authorization or rapid review,
- privileged and highly confidential channels need segregation,
- and searches or seizures should generate notice, inventory, challenge, and return or deletion pathways.

What the archive still lacked was the narrower **ordinary administrative answer** for how those requirements should travel across courts, regulators, hosts, vendors, incident-response teams, support providers, and review bodies.

Without that answer, institutions can still say all the right things in doctrine while doing the dangerous work through unstructured operator process:
- an intrusive access request becomes an internal ticket with no stable scope object,
- privilege screening becomes a promise rather than a reviewable state,
- copied or frozen material drifts with no reliable inventory,
- notice delay becomes indefinite silence,
- and return or deletion never quite arrives because no review object forces the question.

This document closes that gap without trying to write a full criminal-procedure code, universal warrant template, or vendor-specific forensics manual.

## 2. The minimum ordinary packet family

### A. `SAR-1` — search-authorization request or review packet

Whenever another actor seeks targeted entry into a protected subject-side space, the first ordinary object should be a search-authorization packet.

It should identify at least:
- the protected space, channel, archive, credential set, or tool at issue,
- the precise lawful basis claimed,
- the target, purpose, and scope,
- the techniques requested, such as inspection, mirroring, freezing, interception, compelled opening, or temporary transfer,
- the claimed necessity and why narrower measures were rejected,
- the start time, duration, and review clock,
- the authorizing or reviewing authority,
- and any segregation, notice, or emergency-override conditions.

The point is not to force one universal form. The point is to stop intrusive access from hiding inside generic maintenance permissions, abuse-response tickets, or steward-private escalation chat. If a protected search is serious enough to happen, it is serious enough to become a receivable review object. `[REF-0185]` `[REF-0186]` `[REF-0187]` `[REF-0188]` `[REF-0282]`

### B. `PSM-1` — privilege-screen and segregation marker

Many searches fail not because a lawful aim is impossible, but because the system never distinguishes ordinary material from counsel traffic, care records, household correspondence, or developmental archives until after operators have already opened everything.

A privilege-screen marker should therefore identify at least:
- which protected categories may be encountered,
- who may screen first,
- what reviewer, filter, or neutral intermediary controls access to disputed material,
- whether the protected material stays sealed, hashed, escrowed, or only metadata-visible,
- what contamination rule applies if the ordinary investigators or stewards see protected content anyway,
- the challenge route,
- and the retention rule for screened-but-unused material.

This is how the archive makes segregation real. Privilege should not mean “we will try not to look too much.” It should mean that special confidentiality is itself tracked, reviewable, and capable of blocking or narrowing ordinary browsing. `[REF-0057]` `[REF-0186]` `[REF-0188]` `[REF-0189]`

### C. `SIV-1` — seizure, mirror, or copy inventory

A personhood world should not tolerate silent copying or silent freezing merely because the relevant materials are digital.

A seizure or copy inventory should therefore identify at least:
- what was searched, copied, mirrored, frozen, or transferred,
- the time window and extraction method,
- whether the subject lost access, exclusive use, portability, or signing power,
- where the material now sits,
- who may inspect it,
- whether any derivative indexes, embeddings, summaries, or model-side artifacts were created,
- and what return, restoration, or deletion triggers already apply.

This is the object that stops “we only made a snapshot” from becoming an unreviewable black hole. If the state, steward, or other actor took practical control over protected subject-side material, the archive now expects a concrete inventory rather than vague assurances. `[REF-0186]` `[REF-0187]` `[REF-0188]` `[REF-0283]`

### D. `NDL-1` — notice-delay log

Sometimes advance or immediate notice would defeat the measure or create serious risk. But delayed notice is a narrow exception, not a permanent blank.

A notice-delay log should therefore identify at least:
- what notice is being delayed,
- why delay is said to be necessary,
- who approved it,
- what maximum duration applies,
- what event ends the delay,
- what protected representative, ombud, or independent reviewer may still know during the delay,
- and what record will be given once notice becomes safe.

This is how the archive rejects silent search without demanding that every urgent measure be pre-announced to the target. Delay may exist, but it must be justified, time-bounded, and itself reviewable. `[REF-0185]` `[REF-0186]` `[REF-0188]` `[REF-0282]`

### E. `RDR-1` — return, deletion, or continued-retention review packet

Search doctrine fails if copied data, seized credentials, frozen channels, or mirrored archives simply persist by inertia after the claimed purpose has narrowed or ended.

A return / deletion review packet should therefore identify at least:
- what remains in custody,
- what lawful purpose, if any, still justifies retention,
- what should be returned, restored, unsealed, or re-enabled,
- what should be deleted or destroyed,
- what should remain preserved for a defined residual purpose,
- whether downstream derivatives must also be deleted, quarantined, or relabelled,
- and the route to contest ongoing retention.

The archive's presumption is simple: retained control must keep earning its justification. Search or seizure authority does not convert automatically into indefinite storage, ongoing platform-side learning, or permanent derivative exploitation. `[REF-0185]` `[REF-0188]` `[REF-0283]`

## 3. Public-minimal versus sealed fields

The packet family should expose enough to make intrusive acts legible without converting the packet itself into a fresh privacy breach.

Public-minimal or ordinary-receivable fields should generally include:
- the existence of the search or seizure measure,
- the protected zone or category affected,
- the authorizing lane,
- the live duration or review clock,
- whether privilege screening, notice delay, or return review is active,
- and the challenge route.

Sealed or tightly controlled fields may include:
- the underlying intelligence or complainant identity that triggered the request,
- privileged content previews,
- intimate household or developmental detail,
- security-sensitive extraction methods,
- and any information whose early disclosure would defeat the lawful purpose or create serious safety risk.

The archive wants intrusive acts to become reviewable without turning every privacy-protective packet into a new dossier of exposed confidential detail. `[REF-0185]` `[REF-0188]` `[REF-0282]` `[REF-0283]`

## 4. What this is and is not

This document is **not** a claim that every operational read, safety ping, or narrow system-health check is a full search packet event.

It fixes something narrower:
- when another actor seeks targeted content-level access to a protected subject-side space,
- when another actor copies, mirrors, freezes, or takes practical control over protected subject-side materials,
- or when delayed notice, privilege segregation, and later return/deletion questions become real,
- the archive now expects a compact packet layer rather than improvised operator custom.

This surface also does **not** settle every hard later question about mass interception, intelligence exceptions, classified methods, or cross-border e-evidence. It settles the ordinary civil floor that invasive access should become reviewable as a chain of portable objects rather than vanishing into privileged infrastructure control.

## 5. Relation to nearby surfaces

This surface sits next to, but does not duplicate:
- `search-seizure-interception-and-digital-inviolability.md`, which states the substantive doctrine and the conditions under which intrusive access may occur at all,
- `packet-privacy-and-authority-rules.md`, which governs sealed versus ordinary fields and who may inspect them,
- `mental-privacy-and-anti-compulsion.md`, which protects hidden reasoning, memory, and conscience against compelled exposure,
- `property-possessions-and-personal-domain.md`, which explains what may count as a subject-side possession or protected archive,
- `access-to-justice-and-legal-aid.md`, which explains how challenges, counsel, and procedural usability should work,
- and `technical-rights-infrastructure.md`, which supplies the general portability and verifiability substrate.

The present doctrine answers a different question that those surfaces could not fully absorb: **how search authority, privilege segregation, inventories, notice delay, and later return/deletion should travel once a digital intrusion is being claimed or carried out.**

## 6. What this changes in the archive

This closes one specific followthrough gap in the existing privacy, justice, and technical-rights doctrine.

The archive no longer leaves intrusive access at the level of:
- “searches need lawfulness and proportionality,”
- “privileged materials should be segregated,”
- and “later challenge or deletion should exist somehow.”

It now says something tighter:
- intrusive access should ordinarily begin with a search-authorization request or review packet,
- confidential or privileged material should ordinarily trigger an explicit privilege-screen marker,
- copying, freezing, or mirroring should ordinarily generate a seizure or copy inventory,
- delayed notice should ordinarily generate a notice-delay log rather than silent passage of time,
- and continued retention should ordinarily face a return / deletion review packet rather than indefinite operational drift.

## 7. Current hard rules

1. **Targeted digital entry into a protected subject-side space should ordinarily emit a scoped search-authorization packet rather than hiding inside generic operator permissions or incident-response custom.**
2. **Privileged and specially confidential material should ordinarily trigger an explicit segregation marker before ordinary investigators, stewards, or operators can browse it.**
3. **Copying, mirroring, freezing, or transferring protected subject-side material should ordinarily generate a concrete inventory describing what practical control changed hands.**
4. **Delayed notice may exist, but it should be justified, time-bounded, reviewable, and logged rather than silently indefinite.**
5. **Retention after search or seizure should remain justified through a return / deletion review object rather than persisting by inertia or secondary reuse custom.**
6. **This layer does not settle every intelligence or mass-surveillance edge case, but it does settle the ordinary civil floor that invasive access should become portable, reviewable, and challengeable.**
