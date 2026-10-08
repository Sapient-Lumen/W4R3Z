# Jurisdiction Graph and Authority Routing

**Problem:** In polycentric systems, people and implementers often cannot answer a basic question quickly and correctly:

> **Which public body is responsible for *this* obligation, *here*, *right now*, and how do I appeal?**

When the answer is unclear, accountability collapses, services degrade, and capture becomes easier.

This memo defines a compact **Jurisdiction Graph** and an **Authority Router**: a minimal, publishable mapping that makes responsibility legible across overlapping scopes, compacts, delegations, and shared services.

## Invariants

1) **Single-responsible endpoint (SRE):** for any *case type* in any *place*, there must be exactly one accountable endpoint (an office, tribunal, or service owner) even if multiple bodies contribute.

2) **Escalation is computable:** every endpoint has a clear, versioned path for appeal, review, and emergency escalation (`8`, `76`, `195`).

3) **Authority is time-bounded and signed:** delegations, acting authority, and emergency substitutions must have an explicit start/end, legal basis, and audit trail (`78`, `186`).

4) **Spillovers are declared:** cross-border externalities must be routed to a joint body, compact, or higher scope with explicit burden-sharing (`19`, `182`, `197`; see [BIB-OSTROM-POLYCENTRIC-2010], [BIB-OECD-MLG-REFORMS-2017]).

## The Jurisdiction Graph (JG)

A **Jurisdiction Graph** is a public, versioned dataset describing:

- **Nodes:** public bodies (including tribunals, regulators, functional authorities, shared-service entities).
- **Edges:** legal/operational relationships (delegation, shared services, conditional transfer, joint enforcement, data stewardship, appeal).
- **Scopes:** the geographic/functional domain each node covers.
- **Case types:** the set of obligations/services that can be routed.

### Minimal schema (do not overbuild)

- `node_id` (stable)
- `node_name`
- `scope` (geo + functional)
- `case_type` (controlled vocabulary)
- `sre_endpoint` (service owner + contact)
- `legal_basis` (reference, not pasted)
- `edge_type` (delegate/shared/appeal/joint/etc.)
- `edge_conditions` (trigger, thresholds)
- `effective_from` / `effective_to`
- `appeal_to` (pointer)
- `audit_key` (proof trail pointer)

Implementation note: publish as **DCAT**-discoverable data (`70`; [BIB-W3C-DCAT-3]) and maintain provenance (`73`; [BIB-W3C-PROV-O]). If identity binding is needed, use verifiable credentials for attestations and office-holding claims ([BIB-W3C-VC2]).

## Authority Router (AR)

The **Authority Router** is the rule layer that answers routing queries.

Inputs:
- `case_type`
- `location`
- `timestamp`
- `attributes` (optional: risk tier, vulnerability, emergency flag)

Outputs:
- `responsible_endpoint` (SRE)
- `supporting_bodies` (non-SRE contributors)
- `rights_notice` (how to contest, deadlines)
- `appeal_path` (step-by-step)
- `evidence_requirements` (minimal)
- `service_slo` (if applicable; `82`, `189`)

### Routing precedence rules (defaults)

1) **Local-first** if the case is local and capabilities are met (`54`, `176`).
2) **Functional authority** if specialization reduces failure risk (`15`, `197`).
3) **Shared service** if it is operationally centralized but locally accountable (`87`, `189`).
4) **Compact/joint body** for spillovers or corridors (`19`, `182`).
5) **Upward migration** on declared scope failure or emergency (`177`, `186`).

## Anti-capture and integrity hooks

- Require a public **relationship registry** of delegations, compacts, and shared-service arrangements (graph edges must be public by default; secrecy is exception-governed; `77`, `187`).
- Attach **conflict-of-interest** and **lobbying influence** disclosures to nodes and critical edges (`79`, `181`).
- Publish a quarterly **routing anomaly report**: where SRE assignment changed, where appeals spiked, where emergency routing became routine (`183`, `184`).

## Tests

- **T-AR-1 (Uniqueness):** for every `(case_type, location, time)` the router returns exactly one SRE.
- **T-AR-2 (Appeal completeness):** every SRE has a computable appeal path.
- **T-AR-3 (Edge integrity):** every edge has basis, dates, and audit trail.
- **T-AR-4 (Spillover routing):** cases with declared spillovers route to a joint body/compact/higher scope.

## Why this belongs in the archive

The archive already specifies *what* good governance requires (interfaces, scope assignment, compacts, redress). The Jurisdiction Graph + Authority Router makes those requirements **operationally legible**, reducing the gap between normative design and day-to-day accountability.
