# /etc config diff as a first-class drift surface (OSTree + etcupdate lessons)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, supply-chain, operability
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt, Bundles, Adapter→Shadow→Replace

Most systems treat `/etc` as “where configuration lives”, and then quietly accept the two failure modes:

1) *Drift is invisible*: you can’t reliably answer “what changed?” across upgrades.
2) *Drift is contagious*: local edits leak into the next generation in ad‑hoc ways.

DeriveBSD already wants **typed drift surfaces** and **review funnels** (`docs/395-drift-bundles-and-review-summaries.md`).
This doc makes `/etc` drift part of that contract.

## Lesson to steal

- OSTree’s `ostree admin config-diff` treats `/etc` as a *diffable surface* against a default/derived base.  
  Reference: https://ostreedev.github.io/ostree/man/ostree-admin-config-diff.html
- FreeBSD’s `etcupdate(8)` exists because upgrading base systems requires a disciplined `/etc` merge story.  
  Reference: https://man.freebsd.org/cgi/man.cgi?query=etcupdate&sektion=8

DeriveBSD shouldn’t replicate these tools verbatim; it should translate the *shape*:
**/etc changes must be representable as a single diff artifact that can be gated and exported.**

## DeriveBSD direction

### 1) Treat the generation’s `/etc` as a derived tree

For a given generation, the “base `/etc`” is derived from:
- the generation Plan,
- policy modules,
- and config transactions (`docs/218-configuration-transactions-and-receipts.md`).

That base tree has a digest and (optionally) a store path.

### 2) Treat local edits as an explicit overlay (not ambient mutation)

Local edits happen (incidents, breakglass, emergency SSH hardening, time fixes).
We don’t forbid them; we **contain** them:

- represent local edits as a **small overlay** that is:
  - explicit (created via a config transaction),
  - reviewable (diffable),
  - and *killable by policy*.

This keeps “local state” from silently becoming “the system”.

### 3) Emit a typed `/etc` drift diff artifact

Introduce a single, stable diff surface:

- `etc.config.diff` (schema: `spec/etc.config.diff.schema.json`, example: `spec/examples/etc.config.diff.json`)

This is a content-addressed, immutable artifact that compares:
- **base**: derived `/etc` for the generation
- **live**: the active `/etc` root (base + any overlays + runtime mutations)

The artifact carries:
- added/removed/changed entries (path + digest + minimal metadata)
- summary counts + optional `risk_flags` (e.g., `ssh-config-changed`)

### 4) Wire it into the review funnel

- Drift bundles: include `etc.config.diff` when `/etc` drift is non-empty.
- Incident bundles: include the latest `etc.config.diff` (bounded, redactable, digest-only).
- Promotion gates (optional): policy can require review when certain paths drift (ssh, auth, trust roots).

### 5) Adapter lane for existing systems (killable)

For systems that currently rely on `/etc` merges:

- implement a Tier E adapter that can:
  - ingest an “old world” `/etc` delta using `etcupdate`-style diffs,
  - translate it into an overlay object,
  - and emit `etc.config.diff` so reviewers see the drift surface in DeriveBSD terms.

Interop follows Adapter → Shadow → Replace (`docs/402-adapter-lanes-and-strangler-discipline.md`).

## Why this belongs in Base

Even when a profile chooses an immutable or ephemeral-root posture (`docs/423-persist-sets-and-ephemeral-root.md`), `/etc` remains a high-leverage mutation surface.
Making `/etc` drift **visible, typed, and gateable** prevents a common “slow erosion” failure mode where determinism and provenance degrade over time.

See also:
- `docs/218-configuration-transactions-and-receipts.md`
- `docs/395-drift-bundles-and-review-summaries.md`
- `docs/216-incident-snapshots-and-support-bundles.md`
- `docs/195-deterministic-redaction-transforms.md`

Last updated: 2026-02-27r152
