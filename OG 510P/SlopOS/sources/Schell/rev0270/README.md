Current head: **rev0269** — toolchain manifests, import drift, and execution guards. Read `TOOLCHAIN-EXECUTION-MANIFEST.json`, `docs/80-terminal/toolchain-execution-ledger-v0.json`, and `docs/80-terminal/import-dependency-drift-gauntlet-v0.json` before treating any green lint/package/envelope result as citeable. Green remains non-authorizing.

# Schell rev0268

## Current head — rev0266

The current head adds release-custody and package-rebuild humility to the memory-authority proof stack.  It introduces a source-tree content hash manifest, release custody ledger, and package reproducibility gauntlet so the delivered archive can be checked as a package rather than merely trusted because a source tree once passed lint.

Current bundle: `Schell-rev0266-2026.05.26.00.31-releasecustody-packagehashes-rebuildcontracts-obsidianforge.zip`

Read first:

1. `START_HERE.md`
2. `PACKAGE-CONTENTS-MANIFEST.json`
3. `docs/80-terminal/release-custody-ledgers-package-hashes-and-handoff-fences.md`
4. `docs/80-terminal/release-custody-ledger-v0.json`
5. `docs/80-terminal/package-reproducibility-gauntlet-rebuild-scopes-and-byte-identity-humility.md`
6. `docs/80-terminal/package-reproducibility-gauntlet-v0.json`
7. `docs/80-terminal/memory-authority-spine-v0.json`
8. `docs/80-terminal/cube-audit-refactor-ledger-v0.json`
9. `docs/80-terminal/retention-forgetting-board-v0.json`

This is still a proof-surface archive.  It is not a SLSA generator, in-toto layout, Sigstore signing flow, transparency log, reproducible-build guarantee, CI pipeline, compliance report, public proof packet, deletion adapter, helper runtime, terminal UI, shell grammar, or SlopOS portal adapter.
