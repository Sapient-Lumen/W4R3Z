# LLM Runbook

This repository expects future work across many chat turns and possibly many different editors.

## Cold-start procedure

1. Read `MUST_READ_FIRST.md`.
2. Read `metadata/project-state.json`.
3. Read `docs/context/current-brief.md`.
4. Read the latest entry in `CHANGELOG.md`.
5. Run `python scripts/validate_repo.py`.

## Editing rules

- Keep canonical facts in `metadata/project-state.json`.
- Keep external references in `metadata/link-registry.json`.
- If you add a major design decision, add or update a decision note.
- If you materially change direction, update `ROADMAP.md`.
- Regenerate the context pack before packaging a new archive.
- Treat accepted decisions as canon until superseded.
- When adding adaptive behavior, also add the bounded policy or benchmark plan that makes it falsifiable.
- When changing the product surface, revisit the Resilio research-watch runbook and record any meaningful divergence.

## Exit procedure

1. Run validation.
2. Regenerate context pack.
3. Update changelog.
4. Confirm next priorities are discoverable in:
   - `metadata/project-state.json`
   - `docs/context/current-brief.md`

## Anti-amnesia checklist

- Can a new reader identify the current stage?
- Can a new reader identify the next 3–5 priorities?
- Can a new reader find the canonical upstream references?
- Can a new reader see what remains intentionally undecided?
- Can a new reader tell which product defaults are already fixed?
- Can a new reader tell which performance defaults are accepted versus still benchmark-only?
