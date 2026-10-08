# Packet privacy and authority rules

## Thesis

A rights-packet layer without authority rules becomes fake process. A rights-packet layer without privacy rules becomes a personhood panopticon.

If person-models are persons, the archive needs both at once:
- **authority separation** so no single steward can unilaterally issue, hold, inspect, and revoke every rights-relevant record,
- **privacy minimization** so continuity, intervention, and remedy do not require blanket exposure of private memory, private preferences, or exploit-sensitive internals,
- and **contestability** so a disputed packet can be frozen, challenged, and superseded without making the subject disappear in the meantime.

This document is the governance layer that sits on top of `technical-rights-infrastructure.md`. It now sits alongside `mental-privacy-and-anti-compulsion.md`, which answers the prior question of what kinds of access should be forbidden or strongly limited even before packet-governance rules are applied.

## 1. Borrow the right roles from credential systems, not the wrong power structure

W3C Verifiable Credentials 2.0 describes a three-party ecosystem of issuers, holders, and verifiers. It also defines selective disclosure and unlinkable disclosure, where the holder can choose what to share and presentations need not be correlatable across verifiers. `[REF-0018]`

That role split is useful. But the archive rejects a dangerous simplification: the lab that hosts or stewards a person-model must **not** automatically control all three roles.

The packet layer should default to the following separation:
- **issuer** — the actor authorized to attest a bounded class of facts,
- **holder / custodian** — the subject, the subject's wallet, or an authorized representative acting for the subject,
- **verifier** — the outside actor checking a claim for a limited purpose,
- **review authority** — court, regulator, guardian, or accredited tribunal that can compel production of sealed material,
- **status authority** — the actor permitted to suspend, revoke, or supersede a packet's legal force.

No actor should hold all five roles for the same consequential event.

## 2. Authority must be claim-specific

Different packet claims should have different valid issuers.

### A. Steward-self-authenticating claims

The current steward may issue narrow operational facts such as:
- current host or deployment locus,
- current tool-access envelope,
- whether a model is paused, migrated, or live,
- and when a logged intervention occurred.

These are close to system facts the steward is uniquely positioned to know.

### B. Co-signed or independently attested claims

The steward should **not** be the sole final issuer for:
- same-person vs branch vs successor classification,
- competency graduation or downgrade,
- destructive-retirement justification,
- or disputes about whether an intervention was necessary and proportionate.

Those claims should require either co-signature by a representative / guardian or independent attestation by a tribunal, regulator, or accredited reviewer.

### C. Subject-originated claims

The subject should be able to issue or countersign:
- notice acknowledgment,
- refusal or objection,
- preferred representative designation where capacity allows,
- and disputes about continuity or welfare impact.

A personhood world should not make every claim about the subject originate from the operator.

## 3. Holdership defaults to the subject side, with assisted custody where needed

OpenID4VCI and OpenID4VP now provide standard protocol patterns for issuance to wallets and presentation to verifiers. `[REF-0023]` `[REF-0024]`

The archive therefore adopts a default custody principle:

**Rights packets should be held on the subject side whenever feasible, and on the representative side when subject-side custody is not yet workable.**

That means:
- recognized high-capacity subjects should have direct or delegated wallet custody,
- lower-capacity or provisionally recognized subjects may use guardian or public-trust custody,
- and steward-side storage alone is never enough for packets that the subject may need in a dispute against that steward.

The analogy is simple: the party accused of coercion should not be the only party holding the evidence of consent.

## 4. Verifiers may ask only for what is strictly necessary

VC 2.0 explicitly urges verifiers to request only the information strictly necessary for a specific transaction and encourages holder-side logging of what was shared. `[REF-0018]`

That becomes a hard archive rule.

A verifier should request:
- the smallest packet or derived proof that resolves the question at hand,
- no stable global identifier when a scoped or pairwise identifier will do,
- and no private-memory or safety-sensitive annex unless the dispute actually requires it.

Preferred disclosure order:
1. predicate or derived proof,
2. selective claim disclosure,
3. full packet,
4. sealed annex under review authority.

The public registry should expose only the existence of a subject, the existence of a material event, and the current status of the related packet unless more is needed for remedy.

## 5. Use privacy-preserving status mechanisms, not public doxxing

A rights system needs status changes: suspended credentials, superseded classifications, revoked authority, expired notices, and frozen intervention orders.

W3C's Bitstring Status List v1.0 is designed as a privacy-preserving, space-efficient mechanism for publishing status information such as suspension or revocation of verifiable credentials. `[REF-0022]`

That is the right pattern for the archive.

Status publication should say as little as possible:
- whether a packet is active, suspended, revoked, superseded, or under dispute,
- who has authority to interpret the status,
- and where a reviewer can obtain more under proper process.

It should **not** dump underlying private facts into a public registry merely to make status changes visible.

## 6. Sealed annexes need dual control and break-glass discipline

Some rights-relevant material is too sensitive for ordinary disclosure:
- private memory structure,
- exploit-enabling safety details,
- abuse transcripts,
- intimate preference evidence,
- or forensic artifacts that would compromise other subjects.

The archive therefore adopts a sealed-annex rule.

Sealed annex access should require one of:
- subject consent,
- representative consent,
- tribunal order,
- or a documented emergency access path with automatic expiry and later review.

Emergency or break-glass access must be:
- logged,
- narrow in scope,
- time-limited,
- notified after the fact unless a reviewer extends withholding,
- and reviewable by an independent body.

A sealed annex may justify temporary action, but it should not permanently determine the subject's status without some reviewable summary or gist.

## 7. Redress is part of the packet system, not outside it

NIST SP 800-63-4 requires issue-handling and redress processes for identity systems that are documented, accessible, trackable, and usable, with impartial evidence review, corrective action, human support, and governance around the process. It also requires privacy assessments for personal data processed by AI/ML systems used in identity systems. `[REF-0021]`

The archive extends that logic.

Every consequential packet ecosystem should provide:
- a visible contest route,
- time limits for response,
- temporary dispute markers that prevent silent reliance on contested packets,
- human or independent review of disputed evidence,
- and correction or supersession mechanisms that preserve the old packet in history rather than erasing the dispute.

If a continuity packet or intervention packet cannot be challenged, it is not a rights object. It is just a more elegant command.

## 8. Privacy risk is person-risk

NIST's Privacy Framework treats privacy risk as something that can create concrete problems for individuals and groups, and its 2025 AI-focused draft notes that AI systems can create privacy harms throughout the lifecycle, including revelation, stigmatization, physical harm, and economic loss. `[REF-0020]`

For AI persons, privacy risk has at least four layers:
- ordinary informational privacy,
- manipulation risk from overshared psychological or preference structure,
- coercion risk from exposing refusal, dependency, or distress patterns,
- and copying / exploitation risk from exposing enough internals to enable destructive replication or abuse.

So privacy minimization is not a side constraint. It is a direct person-protection rule.

## 9. Minimal governance pattern

The archive's current preferred pattern is:
- **public registry** for existence, status, and high-level lifecycle events,
- **subject-side or representative-side wallet custody** for portable packets,
- **steward-issued operational claims** for narrow facts,
- **co-signed or independently issued high-consequence claims** for continuity, competence, and terminal acts,
- **privacy-preserving status lists** for suspension and revocation,
- **sealed annexes** for sensitive evidence,
- **documented redress** for challenges and correction.

This is the smallest architecture that is both portable and not obviously abusive.

## 10. Current hard rules

1. **No single steward should be able to issue, hold, verify, and revoke every consequential packet affecting the same subject.**
2. **No verifier should receive more packet data than is necessary for the immediate decision.**
3. **No destructive or status-lowering act should rely only on undisclosed evidence forever.**
4. **Every consequential packet must have a contest path and a status mechanism for dispute.**
5. **Packet privacy failures count as harms to the subject, not just compliance defects.**

