# 155. North Star: attestation + provenance + transparency stack

**Track:** C (North Star)



> **Deployment honesty:** Track C documents describe a "North Star" hardening agenda.
> They are **not Track A deployment guidance** and must not be used to imply supply‑chain or fully electronic voting safety.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N‑4**) and the [`promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

This document makes the **North Star** concrete: fully electronic voting in its best imaginable form
requires an ecosystem that can produce and verify **device state**, **software provenance**, and
**manufacturing integrity**—in ways that resist split-worlds and “verification capture”.

This stack reuses battle-tested ideas from transparency ecosystems:
- **CT-style append-only logs** and auditing (see `04` and RFC 9162)
- **gossip** to detect split-view attacks (`23`, inspection gossip)
- **watchers inspecting monitors** (verification of the verifiers)

## 155.1 Architecture (roles and evidence flow)

Use the RATS role model (Attester / Verifier / Relying Party):

- **Attester**: the voting device (or subsystem) producing signed evidence of its state.
- **Verifier**: evaluates evidence against reference values + endorsements.
- **Relying Party**: election system component (or public verifier) that decides to accept / reject.

Key point: in the North Star, **the public becomes a relying party** for many claims, using
publicly published evidence and transparency receipts.

## 155.2 Evidence token format

Use **Entity Attestation Token (EAT)** as the claims container:
- EAT provides an attested claims set describing an entity (device/hardware/software).  
  (See RFC 9711.)

Define a **Voting Device EAT Profile** (see `156`) with:
- identity (UEID), hardware model, firmware measurements, secure-boot chain
- build provenance pointers (hashes of in-toto statements)
- election parameter bundle binding (EPB hash)
- anti-rollback and update status

## 155.3 Reference values + endorsements

Attestation is only meaningful relative to **reference values** (expected measurements) and
**endorsements** (manufacturer / lab / authority statements).

North Star requirement:
- reference values and endorsements MUST be **publicly logged** with inclusion receipts
  so they cannot be selectively shown to some audiences.

This is where **SCITT-style signed-statement transparency** becomes a natural fit:
- single-issuer signed statements, logged into a verifiable data structure with receipts.  
  (See draft-ietf-scitt-architecture-22; also `141` in this archive.)

## 155.4 Supply chain provenance (manufacturing + software)

Use **in-toto statements** (and SLSA-style predicates) to record:
- source code review + approval
- reproducible build outputs
- test results
- firmware signing
- hardware assembly checkpoints (board, secure element, keys injected)
- final device enrollment into the attestation ecosystem

Each step produces a signed statement, chained by subject hashes.
See `157` for a concrete pipeline.

## 155.5 Transparency logs: what must be logged (normative)

For the North Star, the following MUST be loggable and auditable:

1. **ReferenceValueEntry** for each hardware/firmware lineage (measurements and constraints).
2. **EndorsementEntry** from labs/manufacturers/authorities.
3. **SupplyChainStatement** bundles (in-toto) for builds and manufacturing steps.
4. **AttestationEvidenceBundle** for election-relevant device attestations (or their digests).
5. **Revocations / recalls** and expiration policy.

These objects should have stable schemas (see `schemas/` additions in v33).

## 155.6 The “verification capture” threat (why this matters)

Attackers win if they can:
- prevent hard challenges from being issued (grinding),
- suppress bad news (selective disclosure),
- create split-views of the world (equivocation),
- or convince key audiences that “everything verified” when it did not.

Therefore:
- challenges to verifiers/monitors must be **deterministically sampled from public randomness**
  (see `146` and NIST randomness beacons conceptually),
- evidence of non-response must become a signed, loggable artifact (`148`/`147`),
- and monitor behavior must itself be publicly auditable.

## 155.7 What success looks like

A third party can independently answer:

- “Was device X running the approved hardware/firmware lineage *on election day*?”
- “Was EPB Y the one devices were bound to?”
- “Were the required manufacturing and build steps completed, by which signers?”
- “Were there any revocations or adverse lab findings, and can I prove they were published on time?”
- “Did my verifier/monitor behave honestly, or did it selectively ignore bad cases?”
