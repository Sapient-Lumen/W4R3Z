# Product profiles as compilation targets (A–D, no forks)

**Tier:** A (Core meta-doc)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, isolation, supply-chain, operability
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt  

DeriveBSD must stay viable for multiple product shapes **without splitting the project** into forks or incompatible workflows.

This doc makes the product shapes first-class and **checkable**.

## Identifiers and aliases

Profiles have **canonical ids** for tooling and artifacts, and **letter aliases** (A–D) for human discussion.

- Canonical ids live in: `spec/examples/product.profiles.json`
- Letter aliases live in: `spec/product.profile_aliases.json`

Current mapping:

| Alias | Canonical id | Meaning |
|---|---|---|
| A | `fleet_host` | secure fleet host |
| B | `workstation` | secure workstation |
| C | `general_os` | general-purpose OS |
| D | `appliance_factory` | appliance factory / regulatory |

Tools should accept either form but normalize to canonical ids.

## Why profiles must be an artifact

Without explicit profiles, “A–D viability” becomes a human promise and slowly drifts as new features land.
The archive already has good anti-drift machinery (patterns, tiers, adapters). Profiles complete the loop:

- **tiers** answer: *how central is this?*
- **profiles** answer: *for whom is this default?*

## The four product shapes

- **A) fleet host**: minimal, rollbackable control plane that runs signed workloads at scale
- **B) workstation**: human-facing UI with portal-mediated access and ergonomic permission flows
- **C) general OS**: developer-friendly, broad software availability via bounded adapters
- **D) appliance factory/regulatory**: golden images, offline updates, strict gates, long-term rebuildability

## The profile artifact

See:

- schema: `spec/product.profiles.schema.json`
- example: `spec/examples/product.profiles.json`

This file is intended to be *small* and stable: defaults, required invariants, forbidden-by-default lanes, and notes.

## How to use profiles in this archive

When adding or revising a feature:

1. **Declare tier** (A/B/C/D/E) — see `docs/401-v0-cutline-and-feature-tiers.md`
2. **Declare profile applicability** (A/B/C/D)
3. If the feature is not universal:
   - implement it as a **profile default** or **optional lane** (Tier C/D/E),
   - and ensure policy/gates make it off-by-default where appropriate.

A compatibility bridge that is only needed for C (general OS) is an **adapter lane**, not core.

## Suggested repo checks (lightweight)

To keep profiles real, not aspirational:

- `tools/check_discovery.py` checks:
  - top version wiring (`CHANGELOG.md`, `README.md`, `docs/110-juicy-os-lessons.md`, `docs/00-index.md`)
  - that new “must-read” docs exist and are linked from `docs/00-index.md`

- `tools/gen_context_pack.py` prints a compact, deterministic “state of the archive” block (version, must-read set, profiles summary, open questions).

Profiles should remain **one file**; tools should remain small and fast.
