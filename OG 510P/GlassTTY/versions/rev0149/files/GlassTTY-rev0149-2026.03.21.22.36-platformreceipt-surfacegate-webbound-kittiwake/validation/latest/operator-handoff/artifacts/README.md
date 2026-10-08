# GlassTTY

GlassTTY is a local-first control plane for browser-native AI systems.

The repo began by proving a practical idea: a live browser tab can be bridged to a terminal workflow without hiding the browser, scraping credentials, or pretending an unofficial HTTP API exists. The next stage is larger and now explicit. GlassTTY is a generic shell, structured state plane, evidence plane, support plane, and operator/agent surface for multiple AI web apps.

## Official browser surfaces

These surfaces are first-class targets in the repo canon:

- Claude
- ChatGPT
- Google AI Studio
- Grok
- Kimi
- GLM / Z.ai (`https://chat.z.ai/`)

“Official” means the repo should actively:
- keep a surface profile for the site
- keep a living support record for its workflows
- collect evidence for what currently works
- detect and classify drift
- speak precisely about what is implemented versus planned

## Product direction

GlassTTY should become all of the following at once:

- a **common local shell** for browser-only AI tools
- a **structured browser state API** instead of ad hoc readouts
- a **fixture and drift lab** that detects surface change early
- a **support and QA system** that leaves durable proof for each claim
- a **human-piloted by default, agent-capable by design** execution layer so a local/private LLM can safely drive visible browser workflows

## Core shape

GlassTTY now has seven durable layers:

1. **Surface adapters**
   - Site-specific knowledge for Claude, ChatGPT, AI Studio, Grok, Kimi, Z.ai, and future surfaces.
2. **Generic bridge**
   - Extension, native host, broker, CLI, and transport contracts that stay adapter-neutral.
3. **Workflow contract**
   - Shared workflow names, success conditions, evidence expectations, and failure language.
4. **Structured state**
   - Readable machine-facing state families such as session, surface, navigation, receiver, composer, generation, conversation, turn, diagnostics, support, evidence, and action outcome.
5. **Evidence and drift**
   - Fixtures, support bundles, baselines, ledgers, diffs, release-gate artifacts, and next-action guidance.
6. **Support truth**
   - Living support records, promotion rules, release gates, lane scope, and workflow-tier claims.
7. **Operator and agent control**
   - Human-triggered commands, side-panel actions, approval gates, policy-bound agent loops, and stop conditions.

## What is real today

This repo already contains a meaningful live bridge foundation:

- Chromium-first MV3 extension
- Python native host and local broker
- side-panel operator surface
- probe and doctor surfaces
- fixture-lab and fixture capture tooling
- packaging, validation, and handoff/archive discipline
- durable ledgers for smoke, validation, readiness, operator handoff, and operator attempt evidence
- a real Claude-oriented adapter lane

## What is newly improved in rev0132

This revision keeps the rev0131 source-authority boundary and makes it time-aware:

- a **review-age policy** inside `SUPPORT-SOURCE-LOCK.json` so approved authority can become stale explicitly instead of being trusted forever
- stale-review reporting in the **support-source baseline** so future sessions can see when a source lock or approved source needs to be rechecked online
- publish-gate integration so publication now asks not only “is there approved authority?” but also “is that authority still current under the repo’s review policy?”
- refreshed current product anchors for **Grok**, **Kimi**, and **Z.ai** so the lock points at direct contemporary web/product surfaces rather than broader or older homes

The theme is still the same: do not flatten distinct truths into one vague “latest enough” story when queue state, publication eligibility, citable support state, archive identity, payload integrity, source authority, and source freshness are separate operational questions.

## What this revision is

This revision is a **docs, doctrine, truth-surface, and operator-tooling overhaul**. It does not claim that all listed surfaces already work. It does claim that the repo now gives future implementers a clearer operating model, vocabulary, migration plan, support-truth framework, promotion logic, and bounded autonomy story.

Read in this order:

1. `STATUS.md`
2. `ROADMAP.md`
3. `TASKS.md`
4. `TASK_QUEUE.md`
5. `PROJECT_MAP.md`
6. `DECISIONS.md`
7. `docs/repo-canon.md`
8. `docs/design-principles.md`
9. `docs/canon-keys.md`
10. `docs/workflow-model.md`
11. `docs/workflow-catalog.md`
12. `docs/workflow-acceptance-checklists.md`
13. `docs/state-api.md`
14. `docs/state-contracts.md`
15. `docs/operational-truth-splits.md`
16. `docs/browser-history-witness.md`
17. `docs/transient-cues-and-durable-outcomes.md`
18. `docs/control-plane-report.md`
19. `docs/install-receipt.md`
20. `docs/support-surface-snapshot.md`
21. `docs/opening-contract.md`
22. `docs/truth-surface-register.md`
23. `docs/truth-surface-warnings.md`
24. `docs/refresh-truth-surfaces.md`
25. `docs/revision-receipt.md`
26. `docs/validation-artifact-inventory.md`
27. `docs/support-bundle-manifest.md`
28. `docs/support-bundle-queue.md`
29. `docs/published-support-surface.md`
30. `docs/support-bundle-transition.md`
31. `docs/support-publish-gate.md`
32. `docs/approved-source-hierarchy.md`
33. `docs/support-source-baseline.md`
34. `docs/release-manifest.md`
35. `docs/operator-startup.md`
36. `docs/adapter-model.md`
34. `docs/support-truth.md`
35. `docs/support-record-template.md`
36. `docs/support-record-lifecycle.md`
37. `docs/drift-program.md`
38. `docs/drift-triage-playbook.md`
39. `docs/evidence-and-ledgers.md`
40. `docs/evidence-ledger-schema.md`
41. `docs/feature-traceability.md`
42. `docs/agent-policy-model.md`
43. `docs/autonomy-ladder.md`
44. `docs/implementation-program.md`
45. `docs/repo-transition-plan.md`

## Current implementation truth

Claude remains the most mature real adapter lane in the codebase today. The other official surfaces are now part of the project canon and seeded planning surface, but they still need concrete adapters, workflow proof, and release-gate evidence before GlassTTY can claim parity.

That distinction matters: the repo should think bigger immediately while continuing to speak precisely about what is implemented, evidenced, designed, planned, and speculative.
