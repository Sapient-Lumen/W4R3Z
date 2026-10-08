# Kernel interface contract protocol (rev0485)

## Why this protocol exists
The archive now has kernel briefs and slice-0 plans for the top band.
Those notes say **what should be built** and **what should land first**, but they still leave too much room for drift in command names, emitted artifacts, schema family boundaries, and negative-state posture.
This protocol exists so future revisions stop collapsing “honest first milestone” into “everyone can imagine the same interface from prose alone”.

## When to use this protocol
Use this protocol when the question is any of:
- what command or file surface a top-band kernel should expose first;
- what schema families or receipt families belong in the first implementation;
- what counts as a stable import versus an optional experimental import;
- what unsupported or partial states must be preserved as first-class artifacts;
- what compatibility posture should govern contract0.

Do **not** use this protocol merely to rerank candidates, promote a new frontier, or hide packet/kernel/slice changes inside surface prose.

## Minimum required moves
A kernel-interface-contract revision must:
1. Name the governing live packet, kernel brief, and slice note.
2. State why the contract is being fixed now instead of left implicit.
3. Separate public surfaces, inputs, emitted artifacts, and imported seams.
4. Separate stable imports from optional experimental imports.
5. State versioning posture for contract0 and how unknown fields/new receipts should be handled.
6. Keep negative states, unsupported states, and ambiguous states visible as first-class receipts.
7. Refuse at least one tempting wider protocol or hosted-service expansion.
8. State what evidence would justify contract widening or stabilization.

## Required fields
Every kernel interface contract should contain:
- identity
- contract scope
- public surfaces
- required inputs
- emitted artifact families
- stable imports
- optional experimental imports
- versioning and compatibility posture
- negative states / receipts
- proving-ground invocation
- refused expansions
- exit criteria

## Refusal rules
A contract note must refuse:
- treating unstable prototype data as a stable promise;
- hiding partial or mixed-output behavior behind “best effort” parsing language;
- using hosted services when local-first receipts are enough;
- and contractizing candidates that are still in `hold` because the blocker is stewardship rather than interface shape.

## Default interpretation
When this protocol is active:
- the broad rank remains unchanged;
- live packets decide whether the candidate is `advance`, `deepen`, or `hold`;
- kernel briefs decide the first honest repo shape;
- slice notes decide the first bounded milestone;
- and kernel interface contracts decide the first explicit machine-facing surface that milestone must honor.
