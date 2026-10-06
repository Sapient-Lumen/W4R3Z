# Persist sets + ephemeral root (impermanence) (Registry → Diff → Gate)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, operability, isolation
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt  

DeriveBSD’s “immutable generations” posture stays coherent only if **persistence is explicit**.
Otherwise the system slowly re-invents ambient mutable state (“just edit /etc”, “just keep /var forever”) and loses the ability to explain or reproduce what happened.

This doc introduces a single stable diff surface for “what is allowed to persist”:

- `persist.set.registry` — a typed registry describing **persistent mounts** and **persistent path binds** for a generation.

The registry is intentionally boring:
- **diffable** (review “what can survive an upgrade”)  
- **gateable** (policy can forbid persistence classes per profile)  
- **exportable** (support bundles can include it as a small orientation surface)

Files:
- Schema: `spec/persist.set.registry.schema.json`
- Example: `spec/examples/persist.set.registry.json`

## Why persist sets (not “mutable /etc folklore”)

Two ecosystems keep relearning the same lesson:

- **Image-mode systems** need a crisp model of what mutates across upgrades (`/etc`, `/var`, app state).
- **Reproducible systems** need a crisp model of what is *not* derivable (operator secrets, logs, per-host identity).

DeriveBSD should treat persistence the same way it treats authority:
**declare it, compile it, diff it, and receipt it.**

Pattern mapping (`docs/397-pattern-catalog.md`):
- **Registry → Diff → Gate:** persistence rules live in a registry and are reviewed as diffs.
- **Broker → Lease:** persistent volumes are accessed via leased handles, not ambient mounts.
- **Plan → Receipt:** activation emits receipts describing which persistence model was applied.

## What a persist set describes

A `persist.set.registry` is compiled for a generation and contains (at minimum):

1) **Persistent mounts** (datasets/zvols)
- e.g. a dedicated `/persist` dataset, or explicit `/var` and `/home` datasets.

2) **Persistent path binds** (opt-in directories inside an ephemeral root)
- e.g. bind `/etc/ssh` and `/var/db` from `/persist/...` into an otherwise derived root.

3) **Ephemeral root posture (optional, profile-controlled)**
- whether the root filesystem is treated as *discardable* (“impermanence”) and only the persist set survives.

This is a *policy surface*, not just a layout hint.
Different product shapes can set different defaults **without forking**:
- **A (secure fleet host):** strongly prefers ephemeral root + minimal persist set.
- **B (secure workstation):** supports ephemeral root, but may allow larger persisted user areas.
- **C (general-purpose OS):** may default to mutable roots, but still benefits from explicit persist sets for explainability.
- **D (appliance/regulatory):** may require strict, audited persistence classes (and may forbid ephemeral roots if regulations require explicit retention).

## Evidence and operator UX

Persist sets must show up in the evidence spine as “orientation facts”, not an audit afterthought:

- Activation should emit an `activate.receipt` (or equivalent) that includes:
  - the `persist.set.registry` digest
  - whether **ephemeral root mode** was enabled
  - the list of mounted persistent datasets (by digest/id)

- Support/incident bundles should include the registry (small, safe-by-default), so incidents can answer:
  - “what was supposed to persist?”
  - “what *did* we bind into the root?”

- Drift review should treat persist-set diffs as a **first-class drift surface**:
  - “new persisted path added” is an *authority-class* change (it increases data retention and often expands attack surface).

## Prior art (steal the lesson, not the branding)

- NixOS “impermanence” module (explicit persistence lists + discardable root): https://github.com/nix-community/impermanence
- “Erase your darlings” (practical stateless roots on ZFS): https://grahamc.com/blog/erase-your-darlings
- OSTree `config-diff` (diff /etc vs defaults; operational drift visibility): https://ostreedev.github.io/ostree/man/ostree-admin-config-diff.html
- systemd-tmpfiles (declare volatile/persistent paths; lifecycle rules): https://www.freedesktop.org/software/systemd/man/latest/systemd-tmpfiles.html

## Non-goals (keep the core small)

- This does **not** mandate a single filesystem layout.
- This does **not** require ephemeral roots for every profile.
- This does **not** replace `statedb` or state migration artifacts; it complements them by defining the *persistence boundary*.

See also:
- State datasets + migrations: `docs/217-state-datasets-and-migrations-as-evidence.md`
- Drift bundles and review summaries: `docs/395-drift-bundles-and-review-summaries.md`
- ZFS boot environments as generations: `docs/404-zfs-boot-environments-as-system-generations.md`
