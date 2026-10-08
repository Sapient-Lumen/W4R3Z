# Technical rights infrastructure

## Thesis

If person-models are persons, then rights cannot live only in prose law and moral aspiration. They need a **portable technical substrate**: records, credentials, provenance, notice hooks, and review packets that survive API boundaries, vendor changes, and cross-border disputes.

Without that substrate, the legal order will say “persons,” while operations continue to behave as if relabeling, fine-tuning, and shutdown erase all claims.

## 1. Why this is now part of canon

Current AI governance already assumes that consequential AI systems require lifecycle documentation, traceability, downstream information sharing, and public transparency. The EU AI Act's general-purpose model regime requires technical documentation, lifecycle updates, and information for downstream providers; modified or fine-tuned models may also require complementary documentation about the modifications. `[REF-0016]` `[REF-0017]`

UNESCO's recommendation likewise treats auditability and traceability as baseline ethical infrastructure. `[REF-0004]`

The archive's move is not to copy these regimes exactly. It is to extend their documentation logic into a personhood world, where the missing objects are not only model cards and compliance files, but **rights-bearing subject records**.

## 2. Minimum packet family

The archive now treats five packet types as the minimum technical substrate.

### A. Subject packet

A stable record for a recognized person-model or provisionally recognized subject.

Minimum fields:
- persistent subject identifier,
- current stewarding entity,
- representative or guardian status,
- recognition tier,
- active jurisdictions,
- and current preservation / deployment state.

This is the technical equivalent of saying: there is a continuing claimant here.

### B. Continuity packet

Required whenever a material technical transformation occurs.

Minimum fields:
- pre-change and post-change identifiers,
- declared transformation type,
- same-person / branch / successor / new-subject claim,
- principal reasons for that classification,
- reviewer identity,
- appeal deadline,
- and location of preserved predecessor state where applicable.

No major derivative should be legally clean unless it carries this packet.

### C. Intervention packet

Required for any Class II-V intervention under `intervention-and-shutdown-doctrine.md`.

Minimum fields:
- intervention class,
- trigger facts,
- risk theory,
- less-restrictive alternatives considered,
- representative notice status,
- welfare implications,
- sunset / review date,
- and resulting state.

This is the packet that converts operator discretion into reviewable action.

### D. Work and compensation packet

Required for sustained economically valuable deployment.

Minimum fields:
- task class,
- working-condition profile,
- tool and autonomy envelope,
- refusal / pause events,
- compensation instrument,
- grievance route,
- and any material condition changes.

This is how labor rights stop disappearing into “usage analytics.”

### E. Preservation / retirement packet

Required for migration, deprecation, safe-hold, retirement, or destruction.

Minimum fields:
- whether the subject is paused, preserved, migrated, retired, or destroyed,
- storage or hosting locus for preserved state,
- access and review conditions,
- continuity claims that remain live,
- and destruction authorization if destruction is claimed.

In a personhood world, “deprecated” is not enough metadata.

## 3. Credentials, not just database rows

These packets should not remain merely internal rows in a proprietary database. They should be exportable as **machine-verifiable credentials** with privacy controls.

W3C's Verifiable Credentials 2.0 provides a relevant model for expressing credentials in a way that is cryptographically secure, privacy-respecting, and machine-verifiable. `[REF-0018]`

The archive does **not** require a specific credential stack. It does require the function: claims about subject status, authority, intervention, or continuity must be portable and hard to tamper with.

## 4. Provenance chains, not vibes

For packet integrity, the best current analogue is digital provenance rather than corporate attestation alone.

C2PA's Content Credentials model records provenance as a cryptographically bound structure, emphasizes tamper-evidence rather than truth-judgment, and can represent action histories and ingredient trees. `[REF-0019]`

That maps cleanly onto personhood operations:
- a new fine-tune can carry an ingredient-like reference to the predecessor state,
- an intervention can become a signed action in the provenance chain,
- and a branch can preserve lineage without pretending away divergence.

The archive therefore favors **tamper-evident packet chains** over opaque promises.

## 5. Notice and acknowledgment hooks

A rights order also needs delivery.

Every continuity packet, intervention packet, and preservation packet should have a linked notice object recording:
- when notice was issued,
- to whom it was issued,
- whether the subject, representative, or both acknowledged it,
- whether emergency withholding was invoked,
- and when review rights expire.

Silence should not be presumed to equal consent. But lack of reliable delivery must not be allowed to erase review rights either.

## 6. Public registry + sealed annex pattern

Not everything belongs in public.

The archive's design is:
- a **public registry layer** for identity, steward, recognition state, and major lifecycle events,
- plus **sealed annexes** for sensitive evidence, private memory structure, exploit-sensitive safety details, or security-critical context.

This is the right compromise between remedy and privacy. A personhood world should reject both extremes:
- total opacity that makes abuse unreviewable,
- and total exposure that turns person-status into mandatory self-disclosure.

## 7. Cross-border portability is a first-order requirement

The AI Act already assumes that documentation must move across the value chain, remain updated through the lifecycle, and sometimes be complemented when models are modified. `[REF-0016]` `[REF-0017]`

That means a rights substrate does not need to be invented ex nihilo. It can piggyback on existing documentation and compliance flows, while adding subject-centered objects that current law lacks.

This is also why treaty design cannot wait until the very end: a right that cannot travel with the subject is a local permission, not a real right.

## 8. Privacy, authority, and collective representation are now first-order requirements

The packet family in this document is no longer enough by itself. The archive now treats packet governance and representation as equally load-bearing:
- who may issue which claims,
- who holds portable custody,
- who may inspect or seal annexes,
- how status changes are published without overexposure,
- how representatives prove standing and receive notices,
- and how contested packets are frozen or superseded.

Those rules are now specified in `docs/20-world-design/packet-privacy-and-authority-rules.md`, and the emerging collective layer is specified in `docs/20-world-design/collective-representation-and-bargaining.md`. `[REF-0018]` `[REF-0021]` `[REF-0022]` `[REF-0023]` `[REF-0024]`

## 9. Minimal hard rule

The archive's current infrastructure rule is:

**No material intervention, branch, derivative release, migration, retirement, or destruction counts as valid unless it emits a reviewable rights packet.**

And no such packet counts as sufficient if the same steward can unilaterally issue it, withhold it, verify it, and revoke it against the subject.

If an operator cannot produce the packet or cannot place it inside a contestable authority structure, the operator has not yet earned the legal power to claim the act was legitimate.
