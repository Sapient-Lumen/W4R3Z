# Firmware inventory diff as a drift surface (make platform posture reviewable)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, supply-chain, operability
**Patterns:** Registry→Diff→Gate, Bundles

DeriveBSD already treats firmware as part of the platform contract:
we can emit privacy-safe inventories (`fw.inventory.receipt`) and stage/apply firmware updates and UEFI variable writes as planned operations.

The missing review surface is: **what changed in platform posture over time**.
Without a diff object, operators fall back to ad-hoc comparisons, and the highest-risk changes (Secure Boot trust roots, dbx rollouts, “mystery firmware updates”) regress to folklore.

This doc introduces a single, stable diff artifact that makes platform drift **gateable** and **exportable**.

## The artifact: `fw.inventory.diff`

`fw.inventory.diff` compares two firmware inventory receipts (by digest) and produces a compact, deterministic diff surface:

- added/removed components (when inventory coverage changes)
- changed components (version/build changes)
- Secure Boot posture changes (digest-first summary diffs)
- a small set of `risk_flags` suitable for review UI and policy gates

Schema: `spec/fw.inventory.diff.schema.json`  
Example: `spec/examples/fw.inventory.diff.json`

### Why a diff object (instead of “just emit inventory again”)

Inventory receipts answer *what is true now*.
Diffs answer *what changed and why should I care*.

A good platform posture workflow needs both:

- **Receipts** (`fw.inventory.receipt`) for durable truth and bundling.
- **Diffs** (`fw.inventory.diff`) for review ergonomics, alerting, and gates.

## Where it plugs in

### 1) Drift bundles (one review attachment)

A firmware inventory diff is a natural drift surface:

- attach `fw.inventory.diff` to `drift.bundle` when firmware/UEFI steps ran,
- or when inventory changed between two generations.

This keeps “platform drift” visible alongside `/etc` drift, closure diffs, authority diffs, and trust-boundary diffs.

See: `docs/395-drift-bundles-and-review-summaries.md`.

### 2) Hardware/platform evidence spine

Firmware posture is part of “hardware truth” evidence. Diffs are optional, but high leverage for fleets and regulated appliances.

See: `docs/229-evidence-spine-overview.md`, `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`.

### 3) Policy gates

Policy can require a diff in high-assurance lanes:

- firmware updates (`fw.update.plan` present)
- Secure Boot database mutation (`uefi.var.set.plan` touches `db/dbx`)
- measured boot / verifier lanes where firmware is a constraint

Gates can be simple at first:

- fail promotion if `risk_flags` includes `trust-roots-changed` without required approvals
- require explicit acknowledgement if `risk_flags` includes `bootchain-changed` (BIOS/UEFI version changes)

## Privacy and stability rules

- Diffs inherit the inventory lane’s privacy posture: **no raw serials by default**.
- Secure Boot changes are represented by **digests** (pk/kek/db/dbx), not raw blobs.
- The diff surface is intentionally small and deterministic: it is a review attachment, not a data lake.

## References (prior art and primitives)

- Firmware/UEFI as evidence lane: `docs/221-firmware-updates-as-artifacts.md`, `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`
- fwupd / LVFS (inventory + capsule reality): https://fwupd.org/ and https://lvfs.readthedocs.io/en/latest/intro.html
- FreeBSD UEFI variable tooling (Secure Boot posture via digests): https://man.freebsd.org/efivar

Last updated: 2026-02-27r152
