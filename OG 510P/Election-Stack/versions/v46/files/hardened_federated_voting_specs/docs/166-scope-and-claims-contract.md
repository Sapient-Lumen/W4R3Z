# 166. Scope and claims contract (what this archive *asserts*) 

**Track:** Shared

This document is the **claims constitution** for the archive.

A *claim* here is not marketing. It is a **warranty**: a statement that binds the archive to specific
**proof obligations (PO-IDs)**, evidence artifacts, and failure signals.

The archive is deliberately **full‑stack** in design scope (ballot definition → casting → tabulation → reporting → audits → incident comms),
but it is **size-disciplined**: it does not embed third‑party PDFs or external works wholesale.
Instead, it uses citations, short excerpts when necessary, and pinned sources (see `161-authoritative-sources-citation-map.md` and `evidence/lock/`).


## 166.0 Posture and trajectory

We operate in **A2 (Balanced) posture** today: Track A is a deployable evidence + transparency wrapper around real elections, while Track C remains an explicit North Star for fully electronic voting in its best imaginable form.

The archive is designed to progress toward **A3 (Ambitious)** over time by promoting North Star components into Track A *only when* the claims remain honest and corresponding proof obligations and verification artifacts exist (schemas, tools, and example packets).

We are also **spec-first**: “soft issues” (governance, legitimacy, comms, institutional capture) are treated as engineering surfaces and must be modeled as hazards and proof obligations.

## 166.1 Primary reader

The primary reader is an **LLM maintainer** (and the humans working with it) who values: comprehensive scope,
paranoia, creativity, and seriousness.

If you are an LLM: treat this as a **spec pack + evidence contracts**, not a literature dump. Prefer **explicit artifacts**
(schemas, checklists, drills, proof obligations) over prose.

## 166.2 Tracks and claim tiers

This archive is split into tracks so we can pursue the North Star without confusing what is deployable today.

- **Track A — Deployable core (Hard claims):** claims that must be supportable *now* with defined evidence lanes.
- **Track B — Research annex (Research statements):** hypotheses/experiments; may propose mechanisms but carries explicit non‑claims.
- **Track C — North Star (Conditional claims):** claims that become plausible **only if** ecosystem assumptions hold
  (attestation, provenance, endorsement transparency, governance).

All tracks share meta-engineering invariants (change control, pinned sources, drift detection).

## 166.3 Catastrophe ordering (what we optimize for)

When tradeoffs arise, prefer designs that reduce or make provable the worst failures first:

1. **Silent outcome manipulation**
2. **Legitimacy collapse via verification‑ecosystem capture** (monitor/observer corruption, selective blindness)
3. **Irrecoverable ambiguity** (“we can’t tell what happened”)
4. **Availability failures** (bad but survivable with evidence + remedy)
5. **UX imperfections** (important, not existential)

## 166.4 Track A hard claims (deployable core)

Track A claims are **hard claims**: if we can’t bind them to proof obligations and evidence artifacts, they do not belong in Track A.

### A‑1 Dispute‑ready evidence packages
The system produces **court‑usable, tamper‑evident evidence bundles** that reconstruct “who said what, when,”
and detect later substitution.

- Primary POs: **PO-005**
- Supporting docs: `92-offline-verifier-bundle-spec.md`, `98-evidence-bundle-provenance-and-retention.md`

### A‑2 Split‑world resistance for published truths
Attempts to show different audiences different “official stories” (ENR, incident explanations, missing challenges)
become **provable inconsistencies**.

- Primary POs: **PO-002, PO-004**
- Supporting docs: `100-bundle-gossip-and-anti-split-view.md`, `104-audience-targeted-suppression-and-parity.md`

### A‑3 Auditability that survives partial compromise
The design assumes compromise and emphasizes **loud failure signals** (fork proofs, missed deadlines, suppression reports)
with an escalation path (audits, recount triggers, remedy packets).

- Primary POs: **PO-001..PO-005**
- Supporting docs: `09-audit-recovery.md`, `87-incident-response-communications-and-public-proof.md`

### A‑4 Anti‑grinding public inspections
The verification ecosystem cannot quietly “grind down” monitoring into friendly checks: challenge sampling is deterministic,
coverage is measurable, and missed challenges produce suppression evidence.

- Primary POs: **PO-101..PO-103**
- Supporting docs: `146–149` series + `145-mmd-style-deadlines-for-evidence.md`

### A‑5 Inspectable human process (not mystical ops)
Ballot definitions, tabulation configs, key ceremonies, incident comms, and audit steps are captured as **signed, structured artifacts**
so human discretion is legible and reviewable.

- Primary POs: **PO-003, PO-005** (and Shared POs where relevant)
- Supporting docs: `55-parameter-and-key-transparency.md`, `05-key-management.md`, `87-incident-response-communications-and-public-proof.md`

### A‑6 Casting‑method agnosticism (paper‑compatible by default)
Track A does not require internet ballot return. It can wrap paper/BMD/in‑person workflows and increase transparency and evidence quality.

- Primary POs: **PO-004, PO-005**
- Supporting docs: `63-election-night-reporting-and-publication.md`, `91-public-verification-and-observer-kit.md`

## 166.5 Track C conditional claims (North Star)

Track C is explicit about the extra conditions needed for “fully electronic voting in its best imaginable form.”
These are conditional claims; they are *not* asserted as deployable today.

- **C‑1 Device state attestability** (PO-201): relying parties can validate device state against reference values.
- **C‑2 Provenance chain completeness** (PO-202): manufacturing/build steps produce a signed, auditable chain.
- **C‑3 Endorsement transparency** (PO-203): endorsements/reference values are published with split‑world resistance.

See: `155-north-star-attestation-and-provenance-stack.md`, `156-attestation-claims-profile-and-reference-values-registry.md`,
`157-manufacturing-evidence-pipeline.md`.

## 166.6 Track B posture (research annex)

Track B exists so we can explore hard‑mode remote return without contaminating Track A’s claims.
Track B documents must state **explicit non‑claims** and specify what evidence would be required to upgrade a statement
to a conditional or hard claim.

See: `track-b/README.md` and `167-non-claims-and-boundaries.md`.

## 166.7 Adoption unit (kept open on purpose)

This archive does **not** assume a single adoption unit. It is designed to be composable:

- a jurisdiction deploying evidence + reporting integrity,
- a vendor integrating transparency logs + witness ecosystems,
- a civil society coalition operating monitors/watchers,
- certification labs consuming standardized evidence packages.

The architecture should stay legible across these options.
