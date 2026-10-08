# 178 — Envelope kind registry (the evidence API surface)

**Track:** Shared

This archive uses `EvidenceEnvelope` as the canonical wrapper for publishable evidence.
To keep the archive **small, coherent, and mechanically verifiable**, we treat the set
of allowed `EvidenceEnvelope.kind` values as a **registry**, not an ad‑hoc string.

The registry is the archive’s “wire protocol”: verifiers can implement support for a
small, stable set of kinds and still understand most of the archive.

## 178.1 Naming convention

Kinds MUST follow:

- `hfv.<domain>.<type>` with lowercase ASCII, digits, and underscores.
- Examples: `hfv.coverage.report`, `hfv.inspection.suppression_report`.

## 178.2 Canonical kind registry

The canonical registry lives at:

- `artifacts/registries/envelope-kinds.csv`

Each entry binds:

- `kind` → a **default payload schema** (under `schemas/`)
- track association (`A` / `B` / `C` / `Shared`)
- stability (`core` vs `experimental`)

## 178.2b Attachment requirements registry

Some kinds require supporting materials to prevent **selective disclosure** (receipts, gossip summaries, etc.).
Those requirements are declared in:

- `artifacts/registries/envelope-attachment-requirements.csv`

This keeps the verifier surface small: verifiers can implement a single attachment mechanism and still get strong anti-suppression properties.


## 178.3 Extension policy (keep research creative without drifting)

This project is intentionally creative and research‑heavy, but we still need a drift firewall.

- New kinds MAY be introduced for experiments.
- However, **bundled / curated releases** (Track A MVR and all `track-*/BUNDLE.md`) MUST only include kinds that are registered in `envelope-kinds.csv`.

Adding a new kind requires:
1. adding a row to `envelope-kinds.csv`
2. adding or referencing a payload schema in `schemas/`
3. updating the relevant bundle(s)
4. (recommended) an ADR if the kind changes semantics or introduces new trust assumptions

## 178.4 Why this exists

Without a registry, long-lived archives “die” by string drift:
different authors invent near-duplicate kinds, verifiers can’t keep up, and the
evidence ecosystem becomes selectively interpretable.
