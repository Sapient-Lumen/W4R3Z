# ARCHIVE INDEX

## Root surfaces

| Path | Purpose |
|---|---|
| `README.md` | One-paragraph project description and commitments. |
| `START_HERE.md` | Shortest human re-entry path. |
| `AGENTS.md` | Compact derivative wrapper for future maintainers/LLMs. |
| `CHANGELOG.md` | Revision history. |
| `REVISION_RECEIPT.json` | Compact statement of what changed and why it counted. |
| `RELEASE-MANIFEST.json` | Packaging metadata written at bundle time. |
| `ASSUMPTION_LEDGER.json` | Live assumptions that still support canon. |
| `FOLLOWTHROUGH_QUEUE.json` | Honest remainder work that should not disappear. |
| `FOREIGN_PRESSURE_LEDGER.json` | Explicit imports from the reference datacubes. |
| `context-pack.json` | Small machine-readable re-entry packet. |
| `Makefile` | Lint, context-pack, and release commands. |

## Canon docs

| Path | Role |
|---|---|
| `docs/00-meta/charter.md` | Defines the archive's north star and scope. |
| `docs/00-meta/llm-runbook.md` | Working rules for future passes. |
| `docs/00-meta/trajectory-map.md` | Current priority map and linked open questions. |
| `docs/00-meta/bibliography.md` | External sources and short relevance notes. |
| `docs/10-core/design-principles.md` | Canonical design rules for education with AI. |
| `docs/10-core/minimal-ai-literacy-spine.md` | Minimal age-banded progression for student and teacher AI literacy. |
| `docs/10-core/reference-model.md` | The archive's current system blueprint. |
| `docs/20-governance/evidence-and-procurement.md` | Evidence thresholds, guardrails, and procurement rules. |
| `docs/20-governance/accommodation-aware-disclosure-and-accessibility.md` | Two-channel rule for separating pedagogical disclosure from protected accessibility/accommodation routing, plus a procurement accessibility floor. |
| `docs/20-governance/open-question-registry.md` | Live unresolved questions. |
| `docs/30-operations/phased-adoption-roadmap.md` | Sequenced institutional rollout path. |
| `docs/30-operations/subject-embedded-exemplar-kernel.md` | Compact cross-subject routines that instantiate the literacy spine and proof-of-learning logic. |
| `docs/30-operations/course-level-ai-use-grammar.md` | Minimal shared syntax for task modes, disclosure levels, proof expectations, and anti-surveillance constraints. |
| `docs/30-operations/lifelong-public-ai-learning-stack.md` | Four-node public stack for lifelong AI learning beyond ordinary course shells. |
| `docs/30-operations/minimum-public-entitlement-and-handoff-standard.md` | Cross-node minimum standard for entry, warm handoff, learner-controlled portability, and recognition-before-duplication across the public stack. |
| `docs/30-operations/portable-public-learning-packet-and-recognition-profile.md` | Three-rail packet schema plus typed recognition defaults for public cross-node transfer. |
| `docs/30-operations/sector-defaults-for-public-ai-learning-recognition.md` | Sector-by-sector defaults for when public AI-learning claims should mean continuity, waiver, review, or formal credit. |
| `docs/30-operations/standing-equivalency-lists-and-review-governance.md` | Rules for who can publish standing recognition lists, how entries qualify, how they expire, and how omission routes to manual review rather than silent denial. |
| `docs/30-operations/standing-list-publication-profile-and-recency-windows.md` | Tiny machine-readable publication profile plus family-specific recency windows for standing-list entries. |
| `docs/30-operations/standing-recognition-exception-profile-and-local-overrides.md` | Bounded grammar for publishing partial equivalencies, local overrides, and manual-review triggers without collapsing into hidden discretion or giant policy code. |
| `docs/30-operations/appeal-feedback-and-standing-list-maintenance.md` | Privacy-light rule for learning from appeals, disagreement, and false matches through aggregate maintenance signals rather than centralized learner dossiers. |
| `docs/30-operations/public-maintenance-history-and-trust-signals.md` | Thin public history/profile for publishing state changes, dates, reason families, scope impact, and action hints without raw counts or learner-level traces. |
| `docs/30-operations/partner-consumption-and-grandfathering-rules.md` | Default action grammar for how partner systems should consume maintenance signals and when settled uses should be grandfathered rather than reopened. |
| `docs/30-operations/in-flight-teach-out-and-substitute-equivalent-rules.md` | Teach-out, successor-substitution, challenge, and substitute-equivalent protections for learners already in motion when a standing rule changes midstream. |
| `docs/30-operations/documented-reliance-and-burden-thresholds.md` | Compact evidence-and-burden grammar for deciding when midstream route changes create stronger protection duties rather than ordinary updated-route treatment. |
| `docs/40-assessment/authentic-assessment-and-proof-of-learning.md` | High-level assessment redesign under ubiquitous AI. |
| `docs/40-assessment/proof-of-learning-bundles.md` | Compact default bundle patterns by age band and subject family. |

## Quarantine

| Path | Role |
|---|---|
| `docs/90-quarantine/speculations-2026-03-22.md` | Bold but not yet canonical claims about the long-run shape of schooling with AI. |

## Tooling

| Path | Role |
|---|---|
| `tools/run_lint_suite.py` | Runs all archive checks. |
| `tools/check_required_surfaces.py` | Ensures required surfaces exist. |
| `tools/check_links.py` | Checks local markdown links. |
| `tools/check_json.py` | Validates JSON surfaces. |
| `tools/check_receipt_sync.py` | Checks revision sync between root surfaces. |
| `tools/gen_context_pack.py` | Generates `context-pack.json`. |
| `tools/package_release.py` | Creates the release zip and manifest. |
