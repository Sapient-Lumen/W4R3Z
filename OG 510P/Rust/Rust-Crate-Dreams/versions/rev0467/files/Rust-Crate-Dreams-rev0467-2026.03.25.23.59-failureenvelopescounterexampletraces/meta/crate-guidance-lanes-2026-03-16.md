# Crate guidance/supportiveness lane boundaries — 2026-03-16

This note exists to keep the archive honest now that Rust has stable compiler hooks for crate-authored diagnostics and the vision-doc work explicitly asks for more **supportive interfaces** from crates.

## The main split

A crate can now influence parts of the compiler’s error surface.
That does **not** mean every adjacent ecosystem-support problem belongs in the same crate.

## Lane 1: receiver-facing crate guidance packs

**Proposal:** `P-0512 Crate Guidance Pack Kit`

This crate should own:

- common failure-path declarations,
- observed compile-time guidance receipts,
- recovery recipe manifests,
- guidance fixture checks,
- and support-surface diffs across releases.

The central question is:

> “When a user hits a common failure path in this crate, what guidance and next-step recipe do we actually provide?”

## Lane 2: task-first crate choice

**Proposal:** `P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit`

This crate should own:

- task profiles,
- candidate imports,
- ranking/selection packs,
- and starter-set decisions.

The central question is:

> “Which crate should I reach for in the first place?”

This is upstream of `P-0512`. Guidance packs should help after a user has chosen a crate.

## Lane 3: producer-side capability contracts

**Proposal:** `P-0510 Crate Capability Contract & Interop Profile Kit`

This crate should own:

- machine-readable support claims,
- interop export maps,
- profile conformance reports,
- and capability diffs.

The central question is:

> “What does this crate claim to support, and what evidence do we have for that claim?”

That is different from `P-0512`, which is about **failure recovery and user guidance**.

## Lane 4: shared ecosystem interop profiles

**Proposal:** `P-0511 Crate Interop Profile Pack Kit`

This crate should own:

- shared ecosystem profile packs,
- pairwise compatibility reports,
- behavioral probes,
- and migration-hazard receipts.

The central question is:

> “What does it mean for crates to fit the same library boundary, and do they?”

That is different from `P-0512`, which is about helping a human recover from misuse or mismatched assumptions.

## Lane 5: generic diagnostic rendering

**Proposal:** `P-0004 Diagnostic Kit`

This crate should own:

- renderer data models,
- terminal/JSON renderers,
- and generic diagnostic presentation APIs.

The central question is:

> “How should diagnostics be represented and rendered?”

That is different from `P-0512`, which is about **what guidance exists**, not how it is painted.

## Lane 6: docs portals and recipe browsing

**Proposals:** `P-0049 cargo-doc-portal`, future cookbook/recipe surfaces if added later

These crates should own:

- documentation navigation,
- local/offline portals,
- and broader docs browsing surfaces.

The central question is:

> “How do people discover and browse guidance and docs?”

That is different from `P-0512`, which is about a verified, machine-readable guidance pack attached to a crate.

## Working rule

When a future pass touches crate supportiveness, it must state explicitly whether the new value is about:

1. **which crate to choose**,
2. **what a crate claims to support**,
3. **what ecosystem profile a crate fits**,
4. **what guidance a chosen crate gives when users fail**,
5. **how diagnostics are rendered**,
6. or **how docs are browsed**.

Do not let the archive flatten these into one vague “supportive ecosystem tooling” bucket.
