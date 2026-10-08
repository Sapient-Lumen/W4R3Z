# Crate knowledge pack — material basis, export policy, and excerpt-lineage plan (2026-03-22)

This note deepens **P-0536 Crate Knowledge Pack Kit** around one product question:

> when a maintainer says “this is the compact pack you should trust for support, search, or assistant-grade crate understanding”, what exact materials, redaction rules, and exported excerpts should another engineer be able to review?

## Main judgment

**P-0536** is strongest when it models three receiver-facing truths separately:

1. **material basis** — exactly which hosted/local/versioned/floating docs materials fed the pack;
2. **export policy** — which source classes, redaction rules, and manual-review gates were applied for a given consumer profile;
3. **excerpt lineage** — which exact fragments ended up in the exported slice and from which source-material IDs they came.

Do not flatten those into one fake “assistant context” or “crate docs bundle” story.

## Why this matters now

Fresh official docs now make the missing layer unusually concrete:

- docs.rs explicitly hosts rustdoc JSON and downloadable rustdoc archives;
- rustdoc JSON may have older `format_version`s and docs.rs only started hosting it on 2025-05-23;
- docs.rs shorthand URLs intentionally float across semver ranges and `latest`;
- docs.rs build docs make README rules, target defaults, cross-compilation posture, and sandbox behavior concrete;
- docs.rs downloads carry all-target archives but with static-root and invocation-specific asset caveats;
- Cargo/rustdoc still describe JSON output as experimental/nightly substrate;
- and ecosystem guidance still points toward compact, domain-aware handoff artifacts rather than one giant tutorial surface.

That means a worthy crate here should no longer stop at “we imported rustdoc JSON and some docs pages”.
It should export a reviewable material/import policy and exact excerpt lineage.

## New first-class artifacts

### 1. `material-basis.receipt.json`

Records the exact documentation materials that fed a pack or slice.

Suggested fields:
- `crate`
- `profile`
- `materials[]`
  - `id`
  - `kind` (`rustdoc_json`, `docsrs_html`, `docsrs_download_archive`, `readme`, `book_page`, `example_source`, `release_summary`, `manual_local_material`)
  - `authority` (`authoritative`, `imported`, `inferred`, `manual_review_required`)
  - `location`
  - `version_selector` (`exact`, `semver_range`, `latest`, `workspace_head`, `local_unpublished`)
  - `resolved_version`
  - `target`
  - `format_version`
  - `compression`
  - `caveats[]`
- `notes[]`

Questions it answers:
- Did this pack rely on an exact docs.rs version, a floating `latest`, or a local unpublished tree?
- Was rustdoc JSON actually available for this release?
- Did the slice rely on docs.rs-hosted HTML, a downloaded archive, README text, or some combination?
- Which caveats (static-root-path, missing toolchain assets, absent hosted JSON) remain active?

### 2. `export-policy.receipt.json`

Records the rules that shaped a public or machine-consumable export.

Suggested fields:
- `crate`
- `profile`
- `allowed_source_kinds[]`
- `excluded_source_kinds[]`
- `redaction_rules[]`
- `pinning_policy`
- `hosted_vs_local_precedence`
- `manual_review_gates[]`
- `public_export_posture`
- `notes[]`

Questions it answers:
- Is the export allowed to use floating docs.rs URLs at all?
- Are local/internal notebooks or support playbooks excluded from public packs?
- Does hosted docs.rs win over local unpublished materials, or vice versa?
- What conditions force the export into `manual_review_required`?

### 3. `excerpt-lineage.report.json`

Records which exact fragments entered a compact slice.

Suggested fields:
- `crate`
- `profile`
- `excerpts[]`
  - `id`
  - `kind` (`item_docs_excerpt`, `readme_excerpt`, `example_snippet`, `tutorial_excerpt`, `notes_excerpt`)
  - `source_material_id`
  - `applies_to[]`
  - `authority`
  - `selection_basis`
  - `notes[]`
- `omitted_classes[]`
- `manual_review_zones[]`

Questions it answers:
- Which exact item docs or example snippets were exported?
- Which material-basis IDs did they come from?
- Were they maintainer-canonical, imported, or inferred?
- Which excerpt classes were omitted from the slice?

## Product stance

The `0.1` crate should stay bundle-first:

- **not** a hosted search product,
- **not** a retrieval engine,
- **not** a prompt generator,
- **not** a full offline docs portal.

It should instead give another engineer one pack they can audit.

## Adoption shape

A good `0.1` workflow now looks like:

1. import rustdoc JSON / docs.rs presence / docs.rs download metadata / maintainer-declared docs roots;
2. record the exact **material basis**;
3. compute API/docs/example/visibility artifacts as before;
4. apply a declared **export policy** for `support_triage`, `assistant_context`, `public_api_minimal`, or another standard profile;
5. emit **excerpt lineage** for the resulting slice;
6. package all of that into a portable `knowledge-pack.manifest`.

## Worked boundary examples to keep straight

- **Floating docs.rs latest URL** is acceptable for casual browsing, but not equivalent to a pinned review surface.
- **Absent docs.rs rustdoc JSON** for an older release is not a silent omission; it is a material-basis gap.
- **Docs.rs download archive** is a valuable offline import, but not equivalent to a self-contained offline-doc package because static assets and invocation-specific assets still have caveats.
- **A support slice** can be useful and compact while still excluding internal playbooks and publishing explicit excerpt lineage.

## Keep P-0536 separate from

- **P-0051** rustdoc JSON generation / compatibility
- **P-0472** docs.rs parity / hosted-vs-local build truth
- **P-0476** docs debt / docs-coverage review
- **P-0455** doctest extraction / execution truth
- search ranking, embedding strategy, assistant UX, and model behavior

## Working rule for future passes

When the archive next touches **P-0536**, prefer:

1. material-basis receipts,
2. export-policy receipts,
3. excerpt-lineage reports,
4. portable pack manifests,
5. and explicit manual-review gates.

Do not spend the next pass on a docs portal, answer bot, or retrieval UX unless it clearly escapes those responsibilities.
