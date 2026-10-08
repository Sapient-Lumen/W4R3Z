# Contributing

## Ground rules

- Keep changes coherent and reviewable.
- Update docs and metadata in the same revision when facts change.
- Preserve repository continuity.
- Do not add opaque generated files unless they are reproducible.

## Required checks

```bash
python scripts/validate_repo.py
python scripts/generate_context_pack.py
```

Recommended when Rust toolchain is available:

```bash
cargo fmt --all --check
cargo test --workspace
```

## Commit/revision hygiene

- Mention the revision in the changelog.
- Explain why a change exists, not only what changed.
- Prefer ADR-style notes for irreversible decisions.

## Documentation style

- Keep must-read docs short.
- Prefer tables and bullets only when they clarify.
- Use stable filenames.
- Track canonical upstream references in `metadata/link-registry.json`.
