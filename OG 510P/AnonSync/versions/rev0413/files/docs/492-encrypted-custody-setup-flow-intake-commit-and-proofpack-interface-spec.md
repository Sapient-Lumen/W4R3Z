# Encrypted custody setup flow: intake, commit, and proofpack interface spec

## Purpose

`487` through `490` define the key page-level truths for encrypted target admission, ciphertext custody, recovery prerequisites, and encrypted-Archive ceilings.
What still remained under-owned was the full reviewed sequence that ties those truths together.

This page exists to answer one ordinary operator question:

> am I setting up ordinary shared sync, or am I intentionally creating an encrypted-custody node with stricter admission, stricter capability ceilings, and an explicit future-recovery burden?

## Core decision

Every creation or join flow that intends to land **ciphertext-only custody** must pass through one first-class **Encrypted custody setup flow**.
That flow owns:

- lane classification
- destination-seat posture
- encrypted target admission
- recovery-material attestation
- final commitment receipt

The product must not reduce this to a generic `share`, `connect`, or `paste key` ritual.

## Fixed review order

Every encrypted-custody setup flow must render the same sections in the same order:

1. custody intent and lane classification
2. destination seat posture
3. target admission
4. capability and recovery consequence preview
5. commitment receipt and proofpack

### 1) Custody intent and lane classification

Show:

- source subject / share under review
- destination seat and host
- chosen lane (`ordinary-share`, `ordinary-preseed-reuse`, `linked-device reconnect`, `encrypted-custody`)
- strongest reason for the classification
- strongest branch-sensitive warning

The operator must be able to answer: **what kind of intake is this really?**

Rules:

- `encrypted-custody` must remain visibly distinct from ordinary pre-populated merge or reconnect
- a generic non-empty-target warning is never sufficient to classify the lane
- key lane and seat posture both participate in classification

### 2) Destination seat posture

Show:

- seat name and host
- identity cohort and whether the seat is linked
- current seat mode (`disconnected`, `connected`, `synced`, `unknown`)
- whether encrypted custody is admissible on this posture
- whether the seat already carries conflicting live attachment for the same subject family

Verdicts:

- `ready for encrypted custody`
- `review required before encrypted custody`
- `ordinary seat posture detected`
- `conflicting attachment blocked`

The operator must be able to answer: **is this destination seat in the right posture for opaque custody or not?**

### 3) Target admission

This step links directly to `487`.
Show:

- chosen target path
- hygiene verdict
- same-lineage residue verdict
- projected side effects
- strongest blocker if one exists

Admissible outcomes:

- `fresh encrypted landing`
- `reviewed same-lineage reuse`
- `ordinary dirty target blocked`
- `mixed target blocked`
- `path proof insufficient`

The operator must be able to answer: **what will happen to this path if I commit?**

### 4) Capability and recovery consequence preview

This step compiles `488`, `489`, and `490` into one pre-commit consequence preview.

Show:

- ciphertext capability ceiling
- plaintext ceiling
- onward-share ceiling
- recovery rung now
- encrypted-Archive replay ceiling
- exact materials still missing, if any

Required one-line claims:

- `this seat stores ciphertext only`
- `this seat cannot produce plaintext in ordinary flow`
- `future recovery is prepared / partially prepared / not yet prepared`
- `encrypted Archive here is not live restore authority`

The operator must be able to answer: **what powers am I buying, and what burdens am I accepting?**

### 5) Commitment receipt and proofpack

On commit, emit one durable receipt with:

- source subject
- destination seat
- lane classification
- seat-posture verdict
- target-admission verdict
- ciphertext capability ceiling
- recovery rung at commit time
- next review links
- proofpack identifier

The proofpack is a portable summary bundle, not a raw export dump.
It should preserve just enough structured truth to support later rereview, successor handoff, or escalation.

The operator must be able to answer: **what exactly did we review and accept when this encrypted node was created?**

## Primary actions

Allowed action rows:

- `Continue as encrypted custody`
- `Switch to ordinary share/join review`
- `Fix seat posture`
- `Choose another target`
- `Prepare recovery materials first`
- `Stop without creating custody`

Action labels must preserve branch truth.
The product must never hide a lane switch behind a generic `Back`.

## Compact review rail contract

A trustworthy compact rail should preserve the following order:

1. lane
2. seat posture
3. target admission
4. recovery posture
5. strongest next action

Example:

- `Encrypted custody · Linked seat currently disconnected · Fresh encrypted landing · Recovery materials not yet attested · Prepare materials before commit`

## Acceptance criteria

This spec is satisfied when:

- encrypted custody cannot be created without one explicit lane classification
- linked-device `Disconnected` posture and key-lane facts are reviewed before commit
- target-path semantics and recovery-preparation semantics are reviewed in the same flow
- the final receipt proves whether a real encrypted-custody node was created, not just that a key was pasted
