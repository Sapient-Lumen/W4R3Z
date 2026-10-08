# Research notebook — rev0151

## Research question

What counterweight should an adaptive hidden-world engine add to delayed commitment so that it can remain flexible without falsely claiming that every resolution was fixed in advance?

Rev0151 answers with a deliberately narrow primitive: **salted fair-play precommitment seals with externally retainable receipts**.

## 1. Retcon planning needs an asymmetric brake

Gwern’s June 2026 proposal treats hidden world state as temporary, periodically infers a revised latent story-world from the player-observed transcript, compresses it, and continues. That architecture directly attacks premature commitment and railroading. It also creates a fairness problem: a system can choose the secret after seeing the investigation and then manufacture an elegant retrospective explanation.

Source:

- Gwern Branwen, [“Better Fiction via Retcon Planning”](https://gwern.net/blog/2026/llm-retcon), 2 June 2026.

The design inference for Lacuna is asymmetric rather than absolutist:

- witnessed events, disclosures, and depended-upon physical premises should acquire custody;
- unused interpretations and many latent causes should remain revisable;
- selected hidden decisions should be optionally precommittable when the experience promises fair play.

A universal precommitment requirement would merely recreate the brittle simulation Gwern is trying to escape. A complete absence of precommitment makes “I planned it all along” unverifiable. The useful boundary is **selective rigidity**.

## 2. Narrative fair play is not reducible to surprise or coherence

Wagner, Keydar, and Abend formalize detective-fiction fair play as an agreement about the range of possible resolutions and distinguish pre-revelation expectations from post-resolution hindsight. Their revised May 2026 paper reports that LLM-generated stories can produce surprise or coherence, while the balance associated with fair play remains difficult; surprise and coherence do not collapse into one latent quality.

Sources:

- Eitan Wagner, Renana Keydar, and Omri Abend, [“The Challenge and Reward of Fair Play in Narrative”](https://arxiv.org/abs/2507.13841), arXiv:2507.13841, v2, 12 May 2026.
- [HTML version](https://arxiv.org/html/2507.13841v2).

This matters because a cryptographic seal can establish only a tiny prerequisite of fair play: the revealed answer is the answer bound by one earlier digest. It cannot establish that:

- the reader had access to sufficient evidence;
- the candidate range was honestly communicated;
- the answer was inferable but non-obvious;
- clue presentation was stable;
- the resolution is coherent or satisfying.

Rev0151 therefore names the feature a **fair-play seal**, not a fair-play proof. The receipt’s nonclaims are part of the protocol, not documentation garnish.

A future evaluation layer should combine at least:

1. commitment continuity;
2. clue exposure chronology;
3. pre-reveal posterior distribution over candidates;
4. post-reveal coherence;
5. counterfactual action sensitivity;
6. player-facing disclosure integrity.

## 3. Salted hashes are a practical commitment primitive, with limits

RFC 9901’s security discussion for selective-disclosure JWTs explains why a salt must be cryptographically random, sufficiently long, and fresh: without high-entropy hidden input, an observer can enumerate a low-entropy claim space and compare hashes. It recommends at least 128 random bits for the salt. It also frames the desired hash properties in commitment language: computational hiding, second-preimage resistance, and preferably collision resistance.

Source:

- IETF, [RFC 9901: Selective Disclosure for JSON Web Tokens](https://www.rfc-editor.org/rfc/rfc9901.html), November 2025, especially Sections 9.3 and 9.4.

Rev0151 uses a fresh 256-bit nonce for each seal. The larger value is inexpensive and leaves comfortable margin. The nonce remains in the external opening until reveal.

The construction is still not a formal general-purpose commitment scheme with a negotiated security proof. It is a domain-separated salted SHA-256 commitment to a bounded JSON value. Its practical assumptions include:

- nonce secrecy before reveal;
- adequate operating-system randomness;
- SHA-256 preimage and second-preimage resistance;
- exact canonical serialization;
- honest retention of the earlier receipt or external anchor.

It does not protect a secret after the opening file is copied, logged, or sent to a model.

## 4. Canonicalization is part of the security boundary

RFC 8785 exists because hashing or signing structured JSON requires an invariant byte representation. It builds JCS from I-JSON constraints, deterministic property sorting, and ECMAScript primitive serialization.

Source:

- Anders Rundgren, Bret Jordan, and Samuel Erdtman, [RFC 8785: JSON Canonicalization Scheme (JCS)](https://www.rfc-editor.org/rfc/rfc8785.html), June 2020.

A June 2026 individual Internet-Draft for selective disclosure in Agent Action Capsules similarly combines salted hashes, SHA-256, and JCS. It is useful evidence that current agent-provenance work is converging on deterministic structured commitments, but it is explicitly a work in progress with no IETF standards standing.

Source:

- Steven Mih, [“Selective Disclosure Profile for Agent Action Capsules”](https://datatracker.ietf.org/doc/html/draft-mih-scitt-agent-action-capsule-sel-disc-00), Internet-Draft, published 19 June 2026, expires 21 December 2026.

Rev0151 intentionally does **not** claim RFC 8785 compliance. Lacuna currently uses Python’s deterministic JSON emitter with sorted keys, compact separators, UTF-8, and no NaN, plus a stricter payload profile that excludes floats and bounds integers. That is stable within this executable and test suite, but it is not a complete JCS implementation.

Design consequences:

- the scheme identifier must name the exact serialization profile;
- a future JCS implementation should receive a new scheme identifier rather than silently changing v1;
- the opening schema excludes floats and unsafe integers;
- Unicode normalization is not performed, so exact code points remain significant;
- test vectors should be published before encouraging independent implementations.

## 5. An internal hash chain is not external non-equivocation

RFC 9162 explains how Merkle consistency proofs establish that an earlier tree is a prefix of a later append-only tree. Sigstore’s Rekor documentation emphasizes that transparency requires not just an append-only verifiable structure but monitoring for consistency and identity. Sigstore’s security documentation also notes that long-term timestamp confidence depends on monitoring; current timestamp documentation identifies specific caveats around internal clocks and what is actually committed into the log.

Sources:

- IETF, [RFC 9162: Certificate Transparency Version 2.0](https://www.rfc-editor.org/rfc/rfc9162.html), December 2021, Section 2.1.4.
- Sigstore, [“Rekor: Auditing the Public Instance”](https://docs.sigstore.dev/logging/overview/).
- Sigstore, [“Security Model”](https://docs.sigstore.dev/about/security/).
- Sigstore, [“Timestamps”](https://docs.sigstore.dev/cosign/verifying/timestamps/).

Lacuna’s event chain detects internal mutation when the verifier and database remain within the assumed trust boundary. It does not prevent the host from producing two internally valid forks and showing one to each player.

The receipt design follows an important transparency-log lesson without pretending to be a transparency log:

- isolate a stable commitment receipt core;
- compute an independently retainable digest over it;
- make later lifecycle changes leave that digest unchanged;
- state that a verifier must retain or externally anchor the digest;
- avoid calling the local `recorded_at` a trusted timestamp.

Future stronger options include:

- signed receipts from a campaign host key;
- co-signatures from one or more player witnesses;
- posting receipt digests to a public transparency service;
- a campaign-wide Merkle tree with inclusion and consistency proofs;
- threshold custody for opening material.

Those are intentionally external in rev0151.

## 6. The right unit is an opening, not a paragraph of lore

A single opaque “canon paragraph” would recreate multiple problems:

- accidental leakage of unrelated secrets;
- no stable typed identity for the committed proposition;
- all-or-nothing reveal;
- ambiguous serialization;
- poor auditability;
- pressure to treat the whole paragraph as truth.

Rev0151 commits to one bounded JSON payload under one `seal_id`. A payload can reference existing stable claim or character IDs, but the opening remains semantically inert until ordinary operations use it.

That lets a campaign seal different kinds of promise separately:

- the culprit;
- the method;
- a random seed;
- an allowed ending set;
- a continuity invariant;
- a hidden-choice mapping.

It also makes selective future evolution possible. A later Merkle scheme could commit to many leaves and reveal them independently without changing the v1 whole-opening scheme.

## 7. Secret custody should not belong to the narrator model

A privileged director model can be prompt-injected, can overfit to the current scene, and can accidentally expose its context. Giving it authority to prepare, reveal, or void seals would collapse the distinction between authoring the answer and proving prior commitment.

Rev0151 therefore excludes seal lifecycle operations from `lacuna.turn-proposal.v2`, even under a director grant. The model may reason about visible receipts; the administrative host controls opening custody.

This follows least-authority design:

- ordinary player-facing turns receive audience operations;
- director turns receive hidden-world operations but not seal custody;
- explicit host/CLI entrances operate seals;
- the opening file never needs to enter model context before reveal.

A future multi-agent planner should still preserve this boundary. “The director model” is not equivalent to “the campaign principal.”

## 8. Phase separation prevents one specific vacuity

A seal cannot be created and revealed in the same atomic change-set. The origin event must already belong to a committed change receipt.

This prevents the weakest possible abuse: constructing the digest and opening together at reveal time and then presenting the digest as a prior commitment.

It does not prove meaningful temporal distance. The host may create in one transaction and reveal in the next. Stronger campaign policy may require:

- receipt delivery before session start;
- an external timestamp or witness;
- a minimum ledger sequence gap;
- one or more clue disclosures between seal and reveal;
- a sealed clue graph rather than only a culprit.

Lacuna keeps those as policy rather than hard-coding one genre’s pacing rule into the kernel.

## 9. Receipt stability is a protocol invariant

An early implementation mistake made the receipt core include live lifecycle fields such as `status`. That would have changed the supposedly anchorable digest at reveal—the exact opposite of what a receipt is for.

Rev0151 separates:

- immutable `receipt_core`, containing origin seal metadata and event envelope;
- current `seal`, `opening`, and `resolution` views;
- `current_head`, which necessarily advances with the cube.

Tests assert that `receipt_sha256` and the complete core remain identical before and after reveal. This is a small example of a broader rule:

> Audit artifacts must hash the facts whose continuity they claim, not the latest convenient representation of those facts.

## 10. Resulting Lacuna design position

The researched architecture is neither pure retcon planning nor a fixed-world simulator:

- maintain multiple candidate worlds;
- distinguish observation, report, belief, hypothesis, and commitment;
- preserve unknowns rather than closing them automatically;
- make revisions and consequence repairs leave lineage;
- optionally bind selected hidden decisions with salted seals;
- keep seal openings outside the model and cube until reveal;
- require external retention for claims against a hostile host;
- evaluate fair play separately from cryptographic continuity.

The result is a more honest answer to Gwern’s proposal: **late-bind what may remain plastic; precommit what the experience explicitly promises was fixed; record which is which.**

## Open research questions

1. Should Lacuna add a Merkle seal scheme for independently revealable leaves?
2. How should a seal refer to a candidate set without leaking its size or identifiers?
3. Can clue-disclosure events be bound to a sealed solution graph while preserving player-specific visibility?
4. What external witness protocol is simple enough for tabletop use?
5. Should campaign policy support a minimum sequence gap or required intervening disclosures?
6. How can a test distinguish causal agency from a host merely assigning retrospective significance?
7. Can fair-play metrics use the surviving candidate-world posterior before reveal without trusting one model as both author and judge?
8. How should threshold or multi-party opening custody work for adversarial game formats?
9. When is voiding a seal legitimate design retirement, and when is repeated voiding evidence of cherry-picking?
10. Should signed receipts identify a human author, a campaign process, or merely a host key?
