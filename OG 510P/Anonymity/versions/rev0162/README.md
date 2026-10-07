# rev0162 reading guide

## Identity

- Bundle: `Anonymity-rev0162-2026.03.05.01.08-contactsurfaceid-schemaexcerpt-pinrule-topaz.zip`
- SHA-256: `9f71ed89426d49aa727729c6c34de6f24a2cd0a13558b6d6dbba39e1273e945c`
- ZIP contents: 224 files and 78 explicit directory entries; 18,803,977 uncompressed file bytes.
- Snapshot date comes from the filename and source front matter, not an independently authenticated timestamp.

## What to read

Paths are relative to this snapshot.

1. [SERIES_INDEX.tex](files/SERIES_INDEX.tex) for the family map and revision summary; [SERIES_INDEX.pdf](files/SERIES_INDEX.pdf) is a preserved rendering.
2. The opening rev162 entry in [PATCH_NOTES.md](files/PATCH_NOTES.md).
3. [synthesis/paper12_receipt_line_items_schema/paper.tex](files/synthesis/paper12_receipt_line_items_schema/paper.tex) for the contact-surface identity field and schema extension discussion.
4. [synthesis/paper17_worked_example_receipt_interlock/paper.tex](files/synthesis/paper17_worked_example_receipt_interlock/paper.tex), its [README.md](files/synthesis/paper17_worked_example_receipt_interlock/README.md), and [artifacts/](files/synthesis/paper17_worked_example_receipt_interlock/artifacts/) for the worked receipt example.
5. [synthesis/paper30_deployed_surfaces_control_plane/paper.tex](files/synthesis/paper30_deployed_surfaces_control_plane/paper.tex) for the distinction between deployment state and per-contact semantic surfaces.

The featured change gives the per-contact semantic interface its own digest identity and separates it from longer-lived deployment state. These are historical source claims. Later rev0900 corrections must be consulted before reusing anonymity or observation-budget claims from this snapshot.

## Structure

Paper families are top-level directories rather than children of `series/`. The snapshot contains 67 TeX files, 67 PDFs, three Python files, one shell helper, 30 JSON files, and LaTeX build byproducts. A “source-only” phrase in the index should not be read literally as a file-format inventory.

## Integrity caveat

The original ZIP hash matches the expected intake hash. All member CRCs and path checks pass. The 224-entry [MANIFEST.json](files/MANIFEST.json) lists every file exactly once, but only 223 of its 224 digest claims match.

Its sole mismatch is its own self-entry:

- Declared: `666d631003d79e852cd3dea2e62e30cb0f68b858fc85029324e2579d14fe8646`
- Actual: `bdcb06af50234225c97417d74d052205b7690f1be8c02b08f8d973b171177e35`

This intake preserves the discrepancy. It does not rewrite the manifest or claim to know precisely how the self-entry became stale.

## Limits and rights

No standalone license or notice file was found. No reuse license is inferred. No uploaded tools or TeX were executed. Static PDF inspection found no selected active-action indicators, but that is not a full PDF security guarantee. Original bytes, including historical reports and build byproducts, are retained.

