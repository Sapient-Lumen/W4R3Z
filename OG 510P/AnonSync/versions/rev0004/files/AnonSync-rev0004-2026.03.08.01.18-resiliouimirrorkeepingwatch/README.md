# AnonSync

AnonSync is a long-horizon project archive for building a privacy-preserving, peer-to-peer file synchronization tool in the spirit of Resilio Sync, but designed around **Tor** and **I2P** from the start.

This repository is intentionally scaffolded as an **archive-first engineering repo**:
- green-by-default hygiene
- machine-readable project state
- schema-validated metadata
- LLM-safe runbooks and must-reads
- context-pack generation for future turns
- discovery/service checks for local transport dependencies
- explicit architectural boundaries so the repo can evolve over hundreds of revisions without losing coherence

## Current state

This revision is still a **design-stage archive**, but several product and performance defaults are now fixed and should be treated as canon unless deliberately superseded.

## Design stance in this revision

1. **The user experience is a sealed appliance.**
   End users should not need to understand or manually operate Tor, I2P, SAM, control ports, or tunnel plumbing.
2. **Bundled runtimes are the product posture.**
   The application will eventually present as one product, even if implementation begins as a supervised multi-process bundle.
3. **I2P is bundled through `i2pd`, not Java I2P.**
   I2P integration begins at a SAM seam, but the user does not manage the router.
4. **Tor starts with the latest stable tor daemon, not Arti.**
   Arti remains a future migration path, not a present dependency.
5. **Invite-only sharing is canonical.**
   LAN discovery is on by default, but discovery signals must be scoped to invite-derived rotating tokens, not long-lived share identifiers.
6. **AnonSync should imitate Resilio's folder model, permissions, placeholders, and operational posture where practical.**
7. **File watching is acceleration, not authority.**
   Correctness depends on durable indexing plus scheduled rescans.
8. **Performance should be profile-driven, not hand-wavy.**
   Explicit profiles, bounded discovery, direct-send fast paths, and local-state discipline now have machine-readable skeletons.
9. **UI is now a first-class workstream.**
   Desktop and mobile should converge on a shared local-web product surface and intentionally track Resilio's main view, share flow, preference split, and placeholder model where practical.
10. **Resilio research is now an archive practice, not a one-off analogy.**
   Product-facing revisions should revisit current Resilio docs and relevant change-log items before making major UX claims.

## Repository map

- `MUST_READ_FIRST.md` — canonical reading order
- `AGENTS.md` — operating instructions for future LLM and human editors
- `PROJECT_CHARTER.md` — project scope and guardrails
- `ROADMAP.md` — staged plan
- `docs/architecture/` — architecture notes and system shape
- `docs/decisions/` — durable, numbered design decisions
- `docs/research/` — upstream notes and must-reads
- `docs/runbooks/` — repeatable operational procedures
- `docs/context/` — short-form continuity material
- `schemas/` — JSON Schemas for repo metadata and config skeletons
- `metadata/` — machine-readable current repo state
- `config/` — machine-readable archive defaults for profiles and discovery policy
- `scripts/` — validation, context-pack generation, release, and service checks
- `crates/` — Rust workspace skeleton
- `.github/workflows/ci.yml` — CI skeleton

## Quick start

Python tooling:
```bash
python scripts/validate_repo.py
python scripts/generate_context_pack.py
python scripts/discovery_service_check.py --config discovery/service-targets.yaml
```

Rust workspace intent:
```bash
cargo test --workspace
```

## Working conventions

- Prefer additive changes over rename churn.
- Update `metadata/project-state.json` when project facts change.
- Regenerate the context pack after meaningful repo edits.
- Keep must-read docs compact and current.
- When unsure, preserve continuity over novelty.
- Do not casually reopen settled defaults without adding a decision note.
- Treat config skeletons as canon-adjacent scaffolding: real enough to validate, not yet product-final.

## Immediate next priorities

1. Define the folder capability / invite object and its serialization rules.
2. Draft LAN beacon token semantics and rotation windows.
3. Turn the new profile and discovery skeletons into benchmarked defaults.
4. Specify runtime supervision for bundled tor + bundled `i2pd`.
5. Draft the shared UI information architecture and first screen flows.
6. Draft the local index, placeholder, and rescan model.
