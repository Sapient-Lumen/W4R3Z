# Core lexicon registry

This registry separates **certified core terms** from **provisional / private handles**.
The point is not bureaucratic language-policing.
The point is to keep canon-level continuation from silently depending on phrases whose meaning has drifted or never stabilized.

## Certified core terms

- `LX-0001` — `source of truth`
  - Class: certified-core
  - Meaning: treat the latest archive revision as standing canon unless explicitly revised.
  - Dereference: `START_HERE.md`, `docs/50-promptcraft/prompt-pairs.md`

- `LX-0002` — `research online`
  - Class: certified-core
  - Meaning: use current external sources where useful, then archive only the compact load-bearing trace rather than hoarding bulk artifacts.
  - Dereference: `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/archive-policy.md`

- `LX-0003` — `canon`
  - Class: certified-core
  - Meaning: archive surfaces treated as currently admissible project state rather than merely suggestive prose.
  - Dereference: `docs/20-constitution/claim-registry.md`, `docs/90-quarantine/wild-speculations-2026-03-08.md`

- `LX-0004` — `quarantine`
  - Class: certified-core
  - Meaning: protected lane for risky ideas that are worth keeping live without silently promoting them into canon.
  - Dereference: `docs/90-quarantine/wild-speculations-2026-03-08.md`, `docs/50-promptcraft/prompt-pairs.md`

- `LX-0005` — `make lint`
  - Class: certified-core
  - Meaning: deterministic admission check for repo integrity before claiming advancement.
  - Dereference: `Makefile`, `START_HERE.md`

- `LX-0006` — `package release`
  - Class: certified-core
  - Meaning: emit a compact, inspectable bundle that acts as the current handoff object for future continuation.
  - Dereference: `Makefile`, `tools/package_release.py`

## Provisional / private handles

- `LX-0007` — `GPUstorming`
  - Class: provisional-private-handle
  - Meaning: local handle for bold, high-velocity speculative synthesis and research motion.
  - Dereference: `docs/50-promptcraft/prompt-pairs.md`, `docs/90-quarantine/wild-speculations-2026-03-08.md`

- `LX-0008` — `legitimacy kernel`
  - Class: provisional-private-handle
  - Meaning: the smallest surface set and recovery route currently believed sufficient to regain legitimate continuation after drift or corruption.
  - Dereference: `docs/10-method/self-stabilizing-recovery-and-legitimacy-kernel.md`, `docs/20-constitution/recovery-kernel.md`
