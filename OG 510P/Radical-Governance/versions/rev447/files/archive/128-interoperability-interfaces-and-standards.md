# 128 — Interoperability interfaces and standards

**Thesis:** in multi-level governance, the “seams” are where people lose continuity, evidence, and rights. Interoperability must be treated as a *governance interface* with **registries + receipts + clocks + conformance**, not as a purely technical integration task.

This memo specifies a portable minimum for **cross‑agency / cross‑jurisdiction interoperability** that preserves contestability, privacy, and continuity.

## What interoperability must guarantee

**IOP‑0 Continuity at seams**
- MUST: transfers do not reset clocks or evidence ladders (see `109`, `114`, `108`).
- MUST: interim continuity default for essential services during disputes/transfer (see `109`, `114`).

**IOP‑1 Legible interfaces**
- MUST: every external interface has an Interface Card that states: purpose, scope, data categories, legal basis, authority, accountability owner, retention expectations, and recourse hooks (link to `115`, `127`, `118`).

**IOP‑2 Contestable interoperability**
- MUST: any interoperability decision (connect, deny, deprecate) yields a reasoned receipt and an appeal path (see `106`, `111`, `118`).

## Core primitives

### (A) Interface Registry (IR)

**IR‑1 Interface IDs**
- Assign stable IDs: `IID-<domain>-<service>-<interface>-<version>`.

**IR‑2 Interface Cards**
- `IIC-*` cards are published (public or limited‑access) and include:
  - **Purpose** + lawful basis / mandate
  - **Data categories** + minimization (see `127`)
  - **Decision linkage:** how the interface connects to Decision Receipts (`DRR-*`) / Rule IDs (`RID-*`)
  - **Recourse:** where to contest errors or denials (`106`, `08`, `115`)
  - **Change policy:** compatibility rules + deprecation clocks

**IR‑3 Schema & semantics**
- MUST: publish machine‑readable schemas + human semantics notes.
- SHOULD: prefer open, widely implemented specs where feasible (e.g., OpenAPI) [BIB-OAS-OPENAPI].

### (B) Interface Change Receipts (ICR)

Every non-trivial change produces an `ICR-*` receipt:
- **What changed** (diff summary + new/old version pointers)
- **Why** (risk, safety, legal, performance)
- **Who approved** (authority + owner)
- **Impact classification** (compat break / additive / internal)
- **Effective dates** (notice + sunset/deprecation)
- **Mitigations** (adapters, grace period, sandbox)
- **Contest window** (how to challenge)

### (C) Conformance & compatibility (COMP)

**COMP‑1 Compatibility policy**
- MUST: state compatibility rules (e.g., semantic versioning for APIs; “compat breaks require notice + grace”).

**COMP‑2 Conformance suites**
- MUST: publish a conformance test suite for each interface (even if minimal) and a public “last conformance run” date.

**COMP‑3 Sandbox**
- SHOULD: provide a sandbox or test endpoint for integrators; require “test before cutover” for high‑risk interfaces.

## Identity & credentials interop (minimal discipline)

Interoperability often collapses into identity. The minimum governance discipline:

- MUST: treat identity/credential interfaces as high‑risk data systems (bind to Data Asset Cards + Purpose Receipts; see `127`).
- SHOULD: use verifiable credential / DID patterns only when they reduce reliance on centralized lookups and improve contestability; avoid “wallet theater” without recourse [BIB-W3C-VC] [BIB-W3C-DID].
- MUST: provide **correction** and **challenge** lanes for identity assertions (see `125`, `127`, `08`).

## Procurement & adoption rules (anti‑capture)

- MUST: procurement for major systems requires interface registrability (IR + ICR + COMP) and a portability/continuity plan (`109`, `114`).
- SHOULD: require “open interfaces by default” unless a specific, recorded security exception applies (`112`, `127`).

## Minimal metrics (publishable)

- % of externally used interfaces with current `IIC-*` cards.
- Mean time to conformance fix after a breaking change.
- Count of “seam failures” (cases where clocks/evidence reset) per quarter (`109`, `114`).
- Deprecation compliance rate (interfaces retired with full notice + receipts).
- Number of contested interoperability decisions and outcomes (`106`, `111`).

## Links
- Seam continuity: `109-portability-and-cross-jurisdiction-continuity.md`, `114-interjurisdictional-dispute-and-coordination.md`
- Records + receipts: `115-information-integrity-and-record-interfaces.md`, `118-rulemaking-and-change-control.md`
- Data governance: `127-data-governance-and-privacy-interfaces.md`
- Status/identity: `125-identity-membership-and-civil-status.md`
