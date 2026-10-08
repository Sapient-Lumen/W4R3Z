# MUST READ FIRST

This file exists to reduce project amnesia.

Read these in order before making non-trivial changes:

1. `README.md`
2. `PROJECT_CHARTER.md`
3. `ROADMAP.md`
4. `metadata/project-state.json`
5. `docs/context/current-brief.md`
6. `docs/runbooks/llm-runbook.md`
7. `docs/research/must-reads.md`
8. `docs/decisions/0001-bundled-runtime-product-posture.md`
9. `docs/decisions/0002-invite-and-lan-discovery.md`
10. `docs/decisions/0003-sync-detection-and-mobile-defaults.md`
11. `docs/decisions/0004-performance-profiles-and-adaptation.md`
12. `docs/decisions/0005-ui-surface-and-resilio-research-practice.md`
13. `docs/architecture/0005-ui-surface.md`
14. `docs/research/2026-03-08-resilio-ui-and-change-practice.md`
15. `docs/runbooks/resilio-research-watch.md`
16. `AGENTS.md`

## Repo invariants

- The archive must remain understandable to a future reader with no chat history.
- The repo must maintain a machine-readable project state.
- The sync core must remain transport-agnostic.
- I2P and Tor integrations must be isolated behind provider boundaries.
- The product posture is fully bundled and noob-safe.
- LAN discovery is on by default but invite-scoped.
- Performance adaptation must remain bounded, profile-driven, and measurable.
- Product/UI changes that claim to be Resilio-like should be grounded in current documented Resilio behavior.
- Hygiene checks must be cheap enough to run often.
- Every revision must preserve continuity notes for the next revision.

## Before editing

- Read the current brief.
- Read the latest changelog entry.
- Run validation before and after edits.
- Do not silently change project direction without updating project state, roadmap, and decisions.
