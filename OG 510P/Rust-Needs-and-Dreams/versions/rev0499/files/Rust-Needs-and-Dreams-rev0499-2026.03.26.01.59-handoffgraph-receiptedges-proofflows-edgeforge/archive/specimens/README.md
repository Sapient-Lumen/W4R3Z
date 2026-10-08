## Current note (rev0488)
The repo now also has a first **top-band kernel artifact schema pack** under `schemas/top-band-v0/`.
That means the archive now separates five practical machine-facing layers cleanly:
- contracts as **surface commitments**;
- witnesses as **example exercised outputs**;
- fixtures as **replayable scenario inputs and expected checks**;
- schemas as **machine-validatable artifact families**;
- and live packets as **current verdict artifacts**.

This new schema pack exists because example payloads and fixture cards were no longer enough on their own: the repo needed a way to detect structural drift in the first JSON families instead of only prose drift.


## Current note (rev0486)
The repo now has a first **kernel contract witness corpus** under `specimens/kernel-contract-witnesses-v0/`.
That means the archive now separates four practical example layers cleanly:
- shared-envelope specimens as **grammar examples**;
- review-packet specimens as **filled-out verdict examples**;
- live packets as **current verdict artifacts**; and
- contract witnesses as **example exercised outputs for already-earned kernels**.

This new corpus exists because contract notes alone still left too much room for future editors to re-imagine emitted artifacts and negative-state posture from prose.

## Current note (rev0482)
The repo now also has a first **live current decision-packet corpus** under `packets/top-band-v0/`.
That means the archive now separates three things cleanly:
- specimen packets as **grammar examples**;
- dossiers as **current working cards**; and
- live packets as **current verdict artifacts**.

## Current note (rev0480)
The repo now has a first **review-packet specimen corpus**:
- `review-packets-v0/build-state-evidence.advance.example.md`
- `review-packets-v0/debug-acceptance.deepen.example.md`
- `review-packets-v0/navigation-defaults.hold.example.md`
- `review-packets-v0/package-intake.advance.example.md`

That means the archive now has a tiny concrete answer to “what should a real top-program packet actually look like when filled out?” instead of relying only on packet theory.
It also adds **source-candor discipline** so future revisions keep imported evidence, inference, missing proof, and refused larger forms visibly separate.

## Current note (rev0431)
The repo now has a first **portfolio-envelope specimen corpus**:
- `portfolio-envelope-v0/build-state-evidence-pack.example.json`
- `portfolio-envelope-v0/semantic-context-pack.example.json`
- `portfolio-envelope-v0/build-state-diff.example.json`
- `portfolio-envelope-v0/migration-public-api-verify.example.json`
- `portfolio-envelope-v0/package-intake-brief.example.json`
- `portfolio-envelope-v0/lineage-receipt.example.json`

That means the archive now has a tiny concrete answer to “what should an honest shared pack/brief/diff/verify/lineage family actually look like?” instead of relying only on prose notes.

As of rev0431, these positive examples are also paired with a checker and negative fixtures, so the archive can now prove both what should pass and what should fail.

# Specimen corpus

This directory holds the archive's **reference specimens** for shared portfolio grammar.

Why this directory exists:
- `design/portfolio-artifact-conventions-2026Q1.md` says what shared honesty grammar should exist;
- `design/portfolio-consumer-routing-2026Q1.md` says how weaker views should stay weaker;
- `design/portfolio-reference-specimens-2026Q1.md` says why a specimen corpus matters;
- this directory shows a **tiny concrete set of examples** future humans, validators, and LLM edits can inspect.

Current corpus:
- `portfolio-envelope-v0/build-state-evidence-pack.example.json`
- `portfolio-envelope-v0/semantic-context-pack.example.json`
- `portfolio-envelope-v0/build-state-diff.example.json`
- `portfolio-envelope-v0/migration-public-api-verify.example.json`
- `portfolio-envelope-v0/package-intake-brief.example.json`
- `portfolio-envelope-v0/lineage-receipt.example.json`
- `review-packets-v0/build-state-evidence.advance.example.md`
- `review-packets-v0/debug-acceptance.deepen.example.md`
- `review-packets-v0/navigation-defaults.hold.example.md`
- `review-packets-v0/package-intake.advance.example.md`

Review rule:
- if shared envelope or routing rules change materially, refresh the affected specimen in the same revision;
- if a new specimen is added, update `meta/SPECIMEN_CORPUS_PROTOCOL.md` and this README in the same revision;
- if a specimen is intentionally illustrative rather than realistic, say so in the file body.


Validation rule:
- `python tools/check_portfolio_envelope_contract.py` should pass before a shared-grammar or specimen refresh is treated as complete;
- negative fixtures for common honesty failures live in `fixtures/portfolio-envelope-v0/`;
- and passing examples plus failing examples should evolve together.


Non-goal:
- these specimens do **not** replace seam-specific canonical packs or live evidence.
They are **examples of honest shape**, not live operational truth.
