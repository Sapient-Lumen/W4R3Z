# Meta 0417 — Generated source split, note metadata spine, and deterministic rebuild policy

## One-line thesis

The archive should distinguish source-layer commitments from generated surfaces: source catalog and note metadata live as editable inputs, while indexes, threads, status views, source summaries, release maps, control surfaces, assurance buckets, lifecycle gates, and manifests are rebuilt outputs.

## Why this matters

Rev0715 could rebuild and lint, but it still mixed hand-authored material with generated JSON and markdown surfaces at the package root. It also kept source data partly in a Python script and treated tag inference as the main metadata layer. That made the package workable but too dependent on implicit build behavior.

## Reconstruction rule

- Keep `archive/`, `README.md`, `CHANGELOG.md`, `INDEX.md`, `sources/source_catalog.json`, `metadata/note_metadata.json`, `Makefile`, and `tools/` as the source layer.
- Keep regenerated views under `generated/`.
- Treat `sources/source_catalog.json` as the source of truth for source entries.
- Treat `metadata/note_metadata.json` as the source of truth for note class, status, canon role, dependencies, dispatcher routing, source keys, and explicit tags.
- Use keyword inference only when a note lacks explicit tags.
- Publish `generated/NOTE_STATUS.json` for readers who need first-citation, dispatcher, supersession, and active-via-dispatcher labels.
- Allow deterministic generated timestamps through `RG_GENERATED_AT_UTC` or `SOURCE_DATE_EPOCH`.

## Failure modes

- **generated-source confusion**: treating an index or summary as if it were the source object it describes.
- **script-held sources**: burying source entries inside code rather than a canonical source catalog.
- **metadata by accident**: relying on keyword tags when the archive needs declared note roles and statuses.
- **manifest double counting**: listing meta notes both as top-level files and as meta notes.
- **timestamp drift**: mistaking rebuild-time timestamp changes for substantive archive changes.

## Anti-theater tests

1. Can the source index be regenerated from a source catalog without editing Python literals?
2. Can the note-status view be regenerated from declared note metadata?
3. Can the generated directory be deleted and recreated by `make lint`?
4. Does the manifest separate source files, generated files, archive notes, meta notes, metadata files, and tools?
5. Can a deterministic timestamp be supplied for byte-stable generated outputs?
