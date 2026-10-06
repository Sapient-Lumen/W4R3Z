# SlopOS / TriKEM hygiene extraction

This doc records what DelayBasin imports from the uploaded SlopOS and TriKEM archives.

## Reusable stack extracted

1. **Start-here + runbook surface**
   - A maintainer/LLM should be able to recover the project quickly without reading the entire repo.

2. **Mile-high trajectory surface**
   - A short, stable map prevents local edits from redefining the whole project by accident.

3. **Stable registries**
   - Claims, invariants, open questions, and prompt pairs get ids and canonical homes.

4. **Drift gates**
   - Lint should check discovery wiring and revision sanity, not only syntax.

5. **Release packaging**
   - The repo state should be packageable into a named revision artifact.

6. **Promptcraft evolution**
   - Prompt changes are part of the method and should be archived as such.

## What we are *not* copying directly

DelayBasin is not an OS-spec repo and not a cryptographic implementation repo.
Therefore we do **not** inherit:
- large architecture/schema forests,
- protocol-specific evidence lanes,
- code/toolchain matrices beyond what the method itself needs.

## What we *are* preserving

- functional hygiene,
- compact discovery surfaces,
- explicit open questions,
- tight revision discipline,
- packageable state,
- and the idea that external structure can shape later continuation.
