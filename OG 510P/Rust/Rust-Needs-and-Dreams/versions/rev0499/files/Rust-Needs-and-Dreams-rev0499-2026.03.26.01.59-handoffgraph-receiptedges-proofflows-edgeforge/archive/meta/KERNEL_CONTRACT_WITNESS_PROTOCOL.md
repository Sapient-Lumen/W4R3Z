
# Kernel contract witness protocol (rev0486)

## Why this protocol exists
The archive now has contract0 notes for the top-band kernels.
Those notes say what commands, files, schemas, and receipts a first implementation should honor.
They still leave room for drift in one important place: what a real emitted artifact or rendered receipt is supposed to look like when exercised.

This protocol exists so future revisions stop answering that question with prose alone.

## When to use this protocol
Use this protocol when the question is any of:
- what example output should anchor a contract0 surface,
- what example files should be kept for a kernel that already has a contract note,
- what negative-state posture should be visible in example artifacts,
- what stable-only versus unstable-enhanced example difference should be demonstrated,
- or what specimen/witness bundle should future implementations compare against.

Do **not** use this protocol merely to rerank candidates, widen slice scope, or pretend a witness example is live evidence.

## Minimum required moves
A contract-witness revision must:
1. Name the governing live packet, kernel brief, slice note, and contract note.
2. State why a witness layer is needed instead of only prose.
3. Keep the witness corpus bounded to candidates that already earned contract0.
4. Include at least one emitted artifact example and one negative/partial-state posture per witness family.
5. Keep stable-only and optional experimental imports visibly distinguishable when both appear.
6. Say what the example is allowed to prove and what it is not allowed to prove.
7. Refuse at least one larger portal, hosted-service, or standardization leap.
8. Update `specimens/README.md`, `meta/SPECIMEN_CORPUS_PROTOCOL.md`, and `meta/LATEST_REVISION_FILESET.md` in the same revision.

## Required fields for a witness note
Every contract witness note should include:
- identity
- governing packet / kernel / slice / contract references
- invocation shape
- example files
- truth preserved
- negative or partial-state posture
- refused wider interpretations
- refresh trigger

## Corpus rules
The first witness corpus should prefer:
- one witness bundle per already-earned top-band kernel,
- a tiny number of example files per bundle,
- and explicit pairing between a witness note and its example artifacts.

Avoid:
- creating many near-duplicate examples,
- using witness files as if they were proving-ground evidence,
- or adding witness bundles for `hold` candidates.

## Refusal rules
A contract witness revision must refuse:
- upgrading unstable Cargo experiments into stable promises,
- hiding yellow/red states from rendered examples,
- treating alternate-registry posture as if it were crates.io by default,
- treating illustrative adopter evidence as universal validation,
- and expanding the corpus merely because more example files would look impressive.

## Default interpretation
When this protocol is active:
- live packets decide present-tense verdict posture;
- kernel briefs decide first honest repo shape;
- slice notes decide the first bounded milestone;
- contract notes decide the first explicit machine-facing surface;
- and contract witness packs decide what that surface should **look like in exercised example form**.
