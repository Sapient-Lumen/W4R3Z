# ViewFS living archive

**North star:** see [`docs/00-meta/charter.md`](docs/00-meta/charter.md).

Revision notes: [`CHANGELOG.md`](CHANGELOG.md).

This repo is a **living archive** for designing **ViewFS**, a capability-native storage and namespace substrate for SlopOS built around four pillars:
- immutable-first object storage,
- capability handles,
- explicit per-process views,
- portal-mediated imports/exports.

This archive is intentionally **design-phase first**. It records guardrails, lessons, open questions, and staged build order before heavy implementation lock-in.

## How to navigate
0. Mile-high map: [`docs/00-meta/trajectory-map.md`](docs/00-meta/trajectory-map.md)
0.5 Editing runbook: [`docs/00-meta/llm-runbook.md`](docs/00-meta/llm-runbook.md)
1. Threat model assumptions: [`docs/10-threat-model/assumption-registry.md`](docs/10-threat-model/assumption-registry.md)
2. Assurance framing: [`docs/20-assurance/`](docs/20-assurance/)
3. Architecture: [`docs/30-architecture/`](docs/30-architecture/)
4. Shell / terminal ideas: [`docs/70-shell/shell-terminal-ideas.md`](docs/70-shell/shell-terminal-ideas.md)
5. Inspirations mapped to ViewFS: [`docs/90-inspirations/inspirations-mapped.md`](docs/90-inspirations/inspirations-mapped.md)
6. Proposal track: [`rfcs/`](rfcs/)

## Archive discipline
- Cite with REF-IDs; register internal artifacts as EVID-IDs.
- Prefer editing existing docs over spraying new files.
- Keep Phase 1 claims narrow. Explicit non-claims live in [`docs/20-assurance/non-claims.md`](docs/20-assurance/non-claims.md).
- Keep mutable external sources reviewable through [`docs/00-meta/external-source-head-register.md`](docs/00-meta/external-source-head-register.md).

## Current thesis
ViewFS should **not** begin as “our ext4.”

The first viable slice is:
1. immutable object store,
2. handle-based object model,
3. explicit process view root,
4. portal import/export seams,
5. path compatibility as a subordinate membrane.
