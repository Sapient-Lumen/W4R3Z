# 159. Proof obligations ledger (what must be provable)

**Track:** Shared


This is the “what must be provable” counterpart to the hazard register.

It answers: **what claims would we stake legitimacy on, and what evidence must exist to support them?**

## 159.1 Canonical ledger (drift control)

The **canonical** list of proof obligations lives in:
- `../artifacts/proof_obligations/proof-obligations.csv`

This doc is intentionally **non-exhaustive**: it explains how to *use* proof obligations, without duplicating the full list (which tends to drift).

## 159.2 How to read a proof obligation

Each proof obligation (PO) should be treated as:
- a **publicly checkable promise** (not internal intent),
- tied to **evidence artifacts** (schemas, registries, example packets, checklists),
- with an explicit **verification lane** (tooling, drill, tabletop, audit cadence),
- and, where possible, mapped to the archive’s **catastrophe ordering** via the hazard register.

Operationally: if a PO fails, you should be able to point to a concrete artifact that says *what failed, when, and under what contract*.

## 159.3 Typical PO categories (illustrative)

These are *buckets*, not the full list:

- **Record integrity (Track A core)**
  - inclusion and no-false-recording (receipt/state machine)
  - no undetected equivocation (split-view detection)
  - election parameter immutability (EPB/ballot definition commitments)

- **Publication integrity and dispute readiness (Track A core)**
  - content-addressed results + audience parity
  - court-ready evidence bundles and retention
  - time-bounded evidence publication (PublicationContract + suppression proofs)

- **Verification ecosystem robustness (Track A inspections)**
  - anti-grinding challenge selection
  - suppression proofs and monitor accountability
  - governance surfaces that must be legible to outsiders (e.g., witness/monitor sets)

- **North Star (Track C)**
  - device attestability + endorsement/reference value transparency
  - build/provenance completeness and reproducibility evidence

## 159.4 What to do next

For each PO in the CSV ledger:
- assign an owner,
- confirm the evidence artifacts exist (and are receipted/gossiped where required),
- define a drill/test lane and cadence,
- and record compatibility/freeze implications (ADRs if needed).
