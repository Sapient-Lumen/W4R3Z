# Encrypted target admission page: empty root, F-key reuse, and archive side effects interface spec

## Purpose

This page answers:

> is this chosen target actually safe for ciphertext landing, and what exact side effects follow if it is empty, dirty, or already contains bytes from the same encrypted lineage?

The page exists because ordinary `connect to this folder` truth is not enough for opaque custody.
A ciphertext-only node has stricter admission semantics than an ordinary pre-populated merge.

## Core rule

Every encrypted-custody bind must pass through one first-class **Encrypted target admission** page before the product writes or indexes there.
That page owns:

- key lane in use
- target hygiene verdict
- same-lineage residue handling
- explicit side effects
- receipt

## Primary layout

The page always renders the same regions:

1. admission verdict
2. target hygiene card
3. lineage residue card
4. expected side-effects card
5. receipt and next review

### 1) Admission verdict

Show:

- verdict label: `empty-and-safe`, `same-lineage-reuse`, `dirty-ordinary-blocked`, `mixed-uncertain-review`, `blocked`
- target path and host seat
- key lane (`encrypted-key`, `linked-disconnected encrypted intake`, `unknown`)
- strongest honest one-line summary
- safest next action

The operator must be able to answer: **may I land ciphertext here honestly or not?**

### 2) Target hygiene card

Show:

- whether the path exists already
- whether it is empty
- whether ordinary plaintext or unrelated files are present
- whether hidden service residue already exists
- how the hygiene verdict was learned (`scan`, `operator assertion`, `imported state`, `unknown`)
- strongest caveat

Rules:

- ordinary unrelated non-empty directories do not get silently accepted
- the product must never imply that ignored existing files were meaningfully adopted
- empty is not the same verdict as `contains same-lineage ciphertext already`

### 3) Lineage residue card

Show:

- whether prior bytes encrypted with the same F-key / encrypted lineage are present
- whether re-sync and Archive movement are expected
- projected extra-space effect
- whether the product can prove same-lineage versus merely suspect it

The operator must be able to answer: **is this harmless reuse, extra-space churn, or a real dirty-path problem?**

### 4) Expected side-effects card

Show:

- bytes that will be indexed immediately
- bytes that will be ignored
- bytes that may be re-synced and moved to Archive
- non-effects: no plaintext adoption, no magical decryption, no silent merge with unrelated content
- strongest follow-on review link

The operator must be able to answer: **what exactly changes if I commit this bind?**

### 5) Receipt and next review

After acceptance, emit a receipt preserving:

- target path
- key lane used
- hygiene verdict
- lineage residue verdict
- projected Archive side effect
- next review link to **Ciphertext custody**

## Honest outputs

This page may conclude:

- `Fresh empty directory · safe for ciphertext landing`
- `Directory contains same-lineage ciphertext residue · accept only with Archive-growth warning`
- `Directory contains unrelated files · blocked for encrypted admission`
- `Target lineage uncertain · inspect before bind`

It may not flatten all of these into one generic `Connect anyway` outcome.

## Rules

### Rule 1 — encrypted admission is not ordinary pre-populated merge

Do not reuse the same page contract used for ordinary existing-folder connection.
The target hygiene semantics are materially different.

### Rule 2 — ignored unrelated files are still operator truth

If files will be ignored rather than adopted, the page must say so plainly.
Ignored bytes are not harmless just because the product leaves them alone.

### Rule 3 — same-lineage reuse must forecast Archive cost

If reuse can cause re-sync and Archive growth, that cost belongs on the admission page, not in later storage folklore.

### Rule 4 — key lane belongs on the page

The operator should not have to remember later whether this node was admitted by encrypted key, linked intake, or another lane.

## Non-clone reason

Current official Resilio docs are commendably candid that encrypted-node admission is stricter than ordinary folder connection, and that same-F-key residue has real Archive side effects.
But that truth still lives as caveats inside the encrypted-folder article and contrasts awkwardly with ordinary pre-populated-folder guidance.
AnonSync should instead expose one Encrypted target admission page where hygiene, lineage residue, and side effects stay adjacent.
