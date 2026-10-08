# Effect-provenance contract sheet page — result class, origin class, actor basis, and mechanism

## Purpose

Give the operator one first surface for any serious `why did this become this way?`, `who caused this state?`, `did this actually change bytes?`, or `why did the old version come back?` dispute.
The page must stop the product from collapsing **current result**, **origin class**, **actor basis**, **mechanism**, and **publication authority** into one vague activity line.

## The page must answer

1. What result class is visible right now?
2. What origin class most strongly explains that result?
3. Whose authority or seat posture supplied that origin?
4. Did bytes change, names change, policy change, or only detection state change?
5. Which stronger sentence is blocked?

## Core model

### A. Result class

Represent exactly one current class:

- **Ordinary published update**
- **Source-healed revert**
- **Delete restored from source**
- **Old path reappeared**
- **Local-only survivor**
- **Manual replayed older bytes**
- **Notice refreshed without proven new content**
- **Origin unresolved**

### B. Origin class

Represent exactly one current class:

- **Direct local publish**
- **Direct remote publish**
- **Derived source cascade**
- **Linked-family default cascade**
- **Automatic source-heal**
- **Encrypted hard-wire follow behavior**
- **Manual archive replay**
- **Detection induction only**
- **Origin unresolved**

### C. Actor-basis class

Represent exactly one current class:

- **Self seat**
- **Named peer seat**
- **Parent source seat**
- **Linked family controller**
- **Automatic runtime / standing policy**
- **Manual operator replay**
- **Actor unresolved**

### D. Mechanism class

Represent exactly one current class:

- **Content mutation publish**
- **Delete-follow / restore**
- **Rename replay / old-name return**
- **Permission or posture cascade**
- **Archive extraction and republish**
- **Detection induction via mtime / size change**
- **Mixed mechanism requires review**
- **Mechanism unresolved**

### E. Publication-authority class

Represent exactly one current class:

- **Published to peers**
- **Applied locally but not published**
- **Reapplied from source authority**
- **Replayed manually with publish attempted**
- **Detection state changed only**
- **Publication authority unresolved**

### F. Proof class

Represent exactly one current class:

- **Documented role behavior**
- **Visible current posture option**
- **Seat-class hard-wire**
- **Parent-source derivation**
- **Runtime witness**
- **Manual operator act**
- **Mixed proof**
- **Proof unresolved**

## Required warnings

The page must warn when:

- `restored` is being over-read as `manually recovered` when the result is actually source-heal or delete-follow;
- `updated now` is being over-read as fresh authorship when a `touch` or similar induction only refreshed notice;
- a result looks local but actually came from a parent-source cascade or linked-family default;
- an encrypted seat looks like a backup author when its current state actually reflects delete-following plus hard-wired RO behavior;
- manual replay of older bytes is being over-read as ordinary chronology-winning content;
- a local-only survivor is being mistaken for shared truth.

## Required blocked stronger sentences

The page must explicitly refuse to imply any of these unless separately proven:

- `this peer authored the bytes we now see`
- `this revert was manual rather than automatic`
- `this restored file proves durable recovery authority`
- `this newly noticed file changed content now`
- `this state came from direct grant rather than inherited or hard-wired behavior`
- `this visible result alone proves shared convergence`

## Fixed page order

1. **Target and current result**
2. **Origin class now**
3. **Actor basis and authority**
4. **Mechanism breakdown**
5. **Publication consequence**
6. **Proof basis and blocked sentence**

## Compact output

The page must produce:

- `result_class`
- `origin_class`
- `actor_basis`
- `mechanism_class`
- `publication_authority`
- `proof_class`
- `blocked_stronger_sentence`
