# Archive maintenance

GlassTTY treats the release archive as durable memory for future human and LLM sessions.

## Goals

- keep the zip self-describing
- reduce drift between code and docs
- make the next session fast to orient
- leave behind explicit evidence of what was and was not proven

## Minimal end-of-session ritual

1. Update `STATUS.md` with what is now real and what is still unproven.
2. Update `TASKS.md` so the next session has a sharp target.
3. Update `CHANGELOG.md` with the material changes in the new rev.
4. Refresh `ARCHIVE_MANIFEST.json`.
5. Cut a new `GlassTTY-rev####-...zip`.

## Manifest helper

Refresh the archive manifest with:

```bash
./scripts/refresh-archive.py \
  --root "$PWD" \
  --archive-name GlassTTY-rev0006-2026.03.07.12.34-example-summary-codename \
  --revision 6 \
  --summary 'session storage, persistent target tabs, context menus, CLI text mode'
```

The helper keeps the machine-readable manifest in sync with the current repo shape and counts.

The packager now treats the output archive name as authoritative when that name looks like a real GlassTTY revision. That means the finished zip root can stay correct even if you are working from a copied or stale-basename worktree — but `verify-package.py` should still be run so manifest/root drift becomes a hard failure instead of a hidden handoff surprise.

## LLM-first files

These should stay trustworthy and current:

- `README.md`
- `STATUS.md`
- `MEMORY.md`
- `DECISIONS.md`
- `TASKS.md`
- `.llm/SESSION_START.md`
- `.llm/SESSION_END.md`

## Rule of thumb

Prefer one explicit sentence in a memory file over ten implied facts scattered through code.


## Validation retention

The main release archive should stay lean. Keep JSON/Markdown proof, verifier output, and audit summaries in the repo, but do not carry forward redundant validation `.zip` / `.patch` blobs in normal handoff packages unless you explicitly need a forensic package.

- default slim handoff: `bash scripts/package-release.sh "$PWD" /tmp/GlassTTY.zip`
- forensic handoff with validation binaries: `GLASSTTY_PACKAGE_INCLUDE_VALIDATION_BINARIES=1 bash scripts/package-release.sh "$PWD" /tmp/GlassTTY-fat.zip`
- quick size diagnosis: `python scripts/archive-audit.py --pretty`
