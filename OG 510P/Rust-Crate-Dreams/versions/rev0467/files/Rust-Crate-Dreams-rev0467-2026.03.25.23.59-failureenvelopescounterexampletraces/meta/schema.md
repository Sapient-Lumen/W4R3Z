# Archive Schema (lightweight)

Each proposal file should begin with front matter like:

```yaml
id: P-0001
title: Cargo Snapshot — reproducible offline mirrors
status: idea | draft | prototyping | alpha | stable | archived
domains: [cargo, supply-chain, enterprise]
last_reviewed: 2026-02-28
evidence:
  - https://example.com/source
needs:
  - Who hurts?
  - Why now?
risks:
  - What could kill adoption?
```

Then sections:

- Problem
- Users & user stories
- Prior art (and why it’s insufficient)
- Design goals / non-goals
- Architecture & API sketch
- Security / safety model
- Maintenance & governance plan
- Milestones (0.1 / 0.2 / 1.0)
- Open questions
- Sources (URLs)


## Artifact bundle conventions (recommended)

When a proposal introduces a shareable artifact (e.g., `*.quicbundle.zip`), it should specify:

- **Bundle name** and purpose
- **Required top-level files** (at minimum `report.json` and `input/`)
- **Redaction defaults** (what is removed by default)
- **Schema versioning** (a `schema_version` field inside `report.json`)
- **Determinism expectations** (which outputs must be stable across runs)

Keep bundle schemas minimal and evolvable; prefer “additive fields” with explicit version bumps.
