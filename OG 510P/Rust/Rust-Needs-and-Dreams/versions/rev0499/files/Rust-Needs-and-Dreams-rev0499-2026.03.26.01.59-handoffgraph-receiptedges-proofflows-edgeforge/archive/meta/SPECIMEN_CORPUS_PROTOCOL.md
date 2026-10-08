
## Current corpus (rev0486)
Kernel contract witness specimens:
11. `specimens/kernel-contract-witnesses-v0/build-state-pack.witness.md`
12. `specimens/kernel-contract-witnesses-v0/build-state-pack.build-session-pack.example.json`
13. `specimens/kernel-contract-witnesses-v0/build-state-pack.build-diff.example.json`
14. `specimens/kernel-contract-witnesses-v0/build-state-pack.build-doctor-note.example.md`
15. `specimens/kernel-contract-witnesses-v0/debug-acceptance-matrix.witness.md`
16. `specimens/kernel-contract-witnesses-v0/debug-acceptance-matrix.debug-session-pack.example.json`
17. `specimens/kernel-contract-witnesses-v0/debug-acceptance-matrix.debug-tuple-card.example.json`
18. `specimens/kernel-contract-witnesses-v0/debug-acceptance-matrix.debug-replay-result.example.json`
19. `specimens/kernel-contract-witnesses-v0/package-intake-review-kit.witness.md`
20. `specimens/kernel-contract-witnesses-v0/package-intake-review-kit.intake-receipt.example.json`
21. `specimens/kernel-contract-witnesses-v0/package-intake-review-kit.waiver-receipt.example.json`
22. `specimens/kernel-contract-witnesses-v0/package-intake-review-kit.incident-drill-report.example.json`
23. `specimens/kernel-contract-witnesses-v0/safety-critical-readiness-cards.witness.md`
24. `specimens/kernel-contract-witnesses-v0/safety-critical-readiness-cards.readiness-card.example.json`
25. `specimens/kernel-contract-witnesses-v0/safety-critical-readiness-cards.readiness-pack.example.json`
26. `specimens/kernel-contract-witnesses-v0/safety-critical-readiness-cards.readiness-diff.example.json`

These witness specimens are not live evidence. They are bounded example outputs for kernels that already earned contract0, added so future revisions do not reconstruct emitted artifact shape from prose.

# Meta: Specimen Corpus Protocol (rev0430)

## Purpose
Use this protocol when the repo is changing the **shared examples** that demonstrate its portfolio grammar.
This protocol is **not** the same as:
- candidate triage for new seams;
- pilot scorecards;
- evidence-renewal verdicts;
- or consumer-routing cards for live artifacts.

It exists for the narrower question:
> what specimen files should the archive maintain so future humans, tools, and LLM edits have a concrete model of honest packs, briefs, diffs, verify receipts, and lineage receipts?

Read with:
- `design/portfolio-reference-specimens-2026Q1.md`
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/portfolio-consumer-routing-2026Q1.md`
- `specimens/README.md`

## Current corpus (rev0480)
Shared-envelope specimens:
1. `specimens/portfolio-envelope-v0/build-state-evidence-pack.example.json`
2. `specimens/portfolio-envelope-v0/semantic-context-pack.example.json`
3. `specimens/portfolio-envelope-v0/build-state-diff.example.json`
4. `specimens/portfolio-envelope-v0/migration-public-api-verify.example.json`
5. `specimens/portfolio-envelope-v0/package-intake-brief.example.json`
6. `specimens/portfolio-envelope-v0/lineage-receipt.example.json`

Review-packet specimens:
7. `specimens/review-packets-v0/build-state-evidence.advance.example.md`
8. `specimens/review-packets-v0/debug-acceptance.deepen.example.md`
9. `specimens/review-packets-v0/navigation-defaults.hold.example.md`
10. `specimens/review-packets-v0/package-intake.advance.example.md`

## Required specimen truths
Every serious specimen should make these things obvious:

1. **Specimen identity**
   - `schema_family`
   - `specimen_role`
   - seam name
   - specimen version or era if relevant

2. **Honesty spine**
   - subject
   - scope
   - authority
   - freshness
   - partiality
   - imports
   - attachments
   - lineage
   - handoff

3. **Routing posture**
   - who may consume the example artifact
   - what decisions it is allowed to drive
   - what truths were preserved
   - what truths were intentionally omitted
   - where the consumer must escalate

4. **Compatibility posture**
   - whether the specimen demonstrates format-sensitive imports
   - whether parser or schema drift matters
   - whether the example is intentionally partial or fallback-only

5. **Non-authoritative status**
   - specimens are examples of grammar
   - they are not live operational truth
   - they do not replace seam-specific canonical notes

## When to update the corpus
Update the specimen corpus when one of these is true:
- the shared envelope fields materially changed;
- consumer-routing rules changed enough that current brief examples are dishonest;
- verify or lineage rules changed enough that current specimens would teach the wrong habit;
- a new seam joined the core portfolio and cannot be understood well without an example;
- or an old specimen is now misleading because upstream substrate changed too much.

Do **not** update the corpus merely because one sentence in a note changed.
Prefer specimen updates only when the example itself would now teach the wrong thing.

## Preferred moves
Prefer, in order:
1. refreshing an existing specimen that became misleading;
2. improving the README or protocol around the current corpus;
3. adding one missing role specimen (for example diff or verify) if the corpus lacks that role;
4. widening to one additional seam only after the current core roles are covered.

Avoid turning the corpus into a giant registry of every seam and every variant.

## Standard review sequence
1. Re-read `meta/CANONICAL_WORKING_SET.md`.
2. Re-read `design/portfolio-artifact-conventions-2026Q1.md`.
3. Re-read `design/portfolio-consumer-routing-2026Q1.md`.
4. Re-read `design/portfolio-reference-specimens-2026Q1.md`.
5. Decide whether the change is:
   - no specimen impact,
   - specimen refresh,
   - new specimen role,
   - widened seam coverage,
   - packet-specimen refresh,
   - or specimen retirement/replacement.
6. If specimens changed, update `specimens/README.md`, mirror copies under `archive/`, and regenerate `meta/ARCHIVE_MANIFEST.md` in the same revision.

## Minimum anti-cheating rules
- A specimen must never silently claim stronger authority than its role allows.
- A specimen must never omit partiality/freshness just to look cleaner.
- A routed-brief specimen must never be allowed to impersonate a canonical pack.
- A verify specimen must show bounded stronger claims, not universal truth.
- A lineage specimen must keep parent/child relations explicit.
- If a revision changes shared grammar but leaves the corpus untouched, it must say **why no specimen changed**.

## Hygiene rule for LLMs
When an LLM or assistant needs to draft a new shared artifact example for this repo, it should:
- start from the nearest specimen;
- preserve the specimen's honesty spine;
- rename only seam-specific payload sections as needed;
- and explicitly say when the result is illustrative rather than canonical.

If it cannot do that, it should not invent a new shared grammar from scratch.
