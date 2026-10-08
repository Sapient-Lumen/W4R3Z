# Pinning workflow for external sources (sha256 without bundling)

**Track:** Shared

This doc is the **practical maintainer workflow** for converting an unpinned lockfile entry
(`sha256 = ""`) into a pinned one, **without** committing third‑party bytes into this repo.

Related:
- `151-authoritative-sources-and-lockfile.md` (why the lockfile exists)
- `191-external-source-lockfile-playbook.md` (what to add to the lockfile)
- `228-external-source-pin-exemptions.md` (what to do when you *cannot* pin right now)

## Decision rule (what gets pinned)

- **Prefer pinning stable bytes** (PDFs, RFC text files, versioned drafts, versioned specs).
- For **mutable HTML** pages, either:
  - cite as `xref:` with `pin_exemption="mutable"`, or
  - switch to a stable, versioned representation (e.g., a PDF, a dated snapshot, or a standards text file) and pin that.

If you cannot obtain the bytes (403/robots/licensing), use `pin_exemption="blocked"` and record the constraint in `note` (tight).

## Minimal workflow

### 0) Confirm the citation role

- **Normative** references should be `source: <id>` (requires sha256 pin).
- **Informative** references may be `xref: <id>` (may be unpinned, but must carry explicit triage fields).

If a doc is Track A and a reference is normative, **do the pin work** before merging.

### 1) Fetch + hash the bytes locally

Use the maintainer helper:

```bash
python3 tools/pin_external_source.py <source_id>
```

This:
- reads `evidence/lock/external-sources.toml`
- fetches the `url` for `<source_id>`
- prints the computed sha256 and basic response metadata

### 2) Patch the lockfile (no bytes committed)

When the printed sha256 looks sane, write it back:

```bash
python3 tools/pin_external_source.py <source_id> --write
```

The tool updates only the lockfile entry:
- sets `sha256 = "<hex>"`
- removes `pin_exemption` and `review_by` (pinned entries must not carry triage fields)
- updates `retrieved` to “today” (unless `--no-update-retrieved`)

### 3) Regenerate generated indexes

```bash
python3 scripts/gen_external_sources_index.py
```

### 4) Run the release gate

```bash
python3 scripts/release_gate.py
```

## Failure modes (keep them explicit, keep them small)

- **The bytes changed unexpectedly:** treat as `mutable` unless you can locate a stable, versioned artifact.
- **403 / robots / licensing:** use `pin_exemption="blocked"` and keep a short note describing the constraint.
- **Drafts:** prefer versioned draft artifacts (the version is part of the citation) and pin those.

## Size discipline

- Do **not** add downloaded PDFs / HTML snapshots to the repo.
- The lockfile should carry only: `id`, `url`, `retrieved`, `sha256` (or triage fields), short `tags`, and a tight `note`.
