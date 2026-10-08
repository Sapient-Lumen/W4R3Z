# Bundle substrate note — 2026-03-09

This pass exists to resist a quiet archive failure mode:

> every promising crate emits `*.somethingbundle.zip`, but each one smuggles in a different container grammar.

That is portfolio drift, not portfolio strength.

## Main judgment

The archive now has enough bundle-first proposals that **P-0256 Evidence Bundle Core Kit** should be treated as a likely substrate proposal, not just another isolated idea.

The repo should increasingly distinguish four layers:

1. **Container substrate** — deterministic packing, redaction, signing, diffing, explainable verification.
2. **Domain profile** — MQTT, Cargo, conformance, debugging, verification, or other domain semantics.
3. **Runner/suite layer** — how cases execute and how results are collected.
4. **Review/assurance layer** — how imported evidence gets turned into broader claims or change-impact packs.

## Stack mapping in this archive

### Layer 1 — container substrate
- **P-0256 Evidence Bundle Core Kit**

### Layer 2 — domain profiles
- protocol/interop kits
- build/debug evidence kits
- local-first sync bundles
- any domain-specific `*.Xbundle.zip` contract

### Layer 3 — runner/suite layer
- **P-0264 Rust Conformance Harness Toolkit**

### Layer 4 — review/assurance layer
- **P-0485 Verification Campaign Workbench Kit**
- **P-0503 Assurance Case Workbench Kit**

## Practical rule for future proposal passes

When a future proposal wants a portable bundle artifact, it should say explicitly which of these it is doing:

1. reusing a shared container substrate,
2. defining only a domain profile,
3. adding runner/suite semantics,
4. or adding review/assurance semantics above imported evidence.

Do **not** let proposals silently do all four at once unless that breadth is central to the point of the crate.

## Naming guidance

A bundle-first proposal should keep these concepts separate:

- **container core**: shared bundle rules
- **profile**: domain meaning
- **report**: generated explanation or diff
- **attestation**: signed claim payloads
- **review pack**: human-facing rendered summary

## Minimum shared fields every bundle-first proposal should think about

- profile identifier and version
- subject/artifact digests
- deterministic path and timestamp rules
- redaction policy and redaction receipt
- explainable verification report
- machine-readable diff surface
- explicit boundary between raw artifacts and normalized projections

## When not to route through P-0256

Do not force every crate through a bundle substrate when the value is elsewhere.
Examples:

- pure algorithm crates
- narrow runtime adapters with no portable artifact need
- crates whose output is already a stable standard artifact and does not need extra packaging

## Why this matters for repo hygiene

This repo is partly a memory system for future humans and LLMs.
If every proposal invents its own half-specified bundle grammar, the archive will look richer than it really is.

A stronger archive is one where more proposals clearly say:

- **what layer they own**,
- **what layer they reuse**,
- and **what artifact they hand to another person**.

## Sources

- https://github.com/in-toto/attestation/blob/main/spec/README.md
- https://github.com/in-toto/attestation/blob/main/spec/v1/envelope.md
- https://slsa.dev/provenance/v1
- https://datatracker.ietf.org/doc/html/rfc8949
- https://www.rfc-editor.org/rfc/rfc9052.html
