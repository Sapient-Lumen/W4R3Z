# AGENTS

This repository is designed for repeated LLM and human iteration over a long time horizon.

## Default operating sequence

1. Read `MUST_READ_FIRST.md`.
2. Read `metadata/project-state.json`.
3. Read `docs/context/current-brief.md`.
4. Read the latest section of `CHANGELOG.md`.
5. Make the smallest coherent set of changes.
6. Update docs + metadata together.
7. Run:
   - `python scripts/validate_repo.py`
   - `python scripts/generate_context_pack.py`
8. If the repo content changed materially, update `CHANGELOG.md`.

## Non-negotiables

- Do not invent project history.
- Do not rename top-level files casually.
- Do not duplicate canonical facts across many files without a reason.
- Keep machine-readable metadata aligned with prose docs.
- Keep external links canonical and tracked in `metadata/link-registry.json`.
- Prefer appending ADRs or notes over rewriting history out of existence.
- Respect settled product defaults unless a new decision explicitly supersedes them.
- Do not expose transport/router complexity to the imagined noob user in product-facing design docs.
- Do not add "adaptive" behavior without also stating what is measured, bounded, and overrideable.
- When changing product UI, invite flows, placeholder behavior, or product defaults, revisit the current Resilio docs and change log first.

## What counts as a material change

- scope changes
- threat model changes
- protocol or architecture changes
- provider API changes
- packaging strategy changes
- trust or key management changes
- changing invite, discovery, placeholder, permission, mobile, or performance-profile defaults
- adding or removing major docs, crates, scripts, or machine-readable config skeletons

## When context is thin

If chat context is limited, trust the repository over memory. Start from:
- `docs/context/current-brief.md`
- `context-packs/anonsync-context-pack.md`
- `metadata/project-state.json`
- `docs/decisions/`

## Release/archive discipline

Release archives should follow the pattern:

`AnonSync-rev####-YYYY.MM.DD.HH.MM-codename.zip`

The codename should be memorable, lowercase, and stable for that revision.
