# Start here (read-order + “what this project is about”)

> "Assume humans compromise systems, build evidence that survives it, and maximize the odds of justified eudaimonia for the innocent, future generations of humans and AI, and all agents who might possibly be able to change the course of history appropriately."
>
> *(This is intentionally “squishy.” Do not sanitize it into false precision. Treat uncertainty as a first-class citizen and pursue justice as optimistically as we can.)*

This archive is a **research + engineering spec pack** for an election **transparency and evidence stack**.

It is deliberately split into **three tracks** so we can pursue an ambitious North Star without confusing
what is deployable today.

- **Track A — Deployable Core:** evidence infrastructure that can wrap paper/BMD/in-person workflows.
- **Track B — Remote Return / Hard-mode Research:** constrained experiments, with explicit non-claims.
- **Track C — North Star:** “fully electronic voting in its best imaginable form” — attestable devices,
  transparent manufacturing/provenance, and a verification ecosystem hardened against capture.

If you're maintaining or extending this archive, read:
- `docs/166-scope-and-claims-contract.md` (what we assert)
- `docs/167-non-claims-and-boundaries.md` (what we do *not* assert yet)
- `docs/183-archive-stewardship-and-long-horizon-plan.md` (A2→A3 trajectory + how to change things safely)


## Recent additions (v40–v42)

- **Evidence envelopes + packets** (anti‑drift packaging): `docs/173-canonical-evidence-envelopes-and-packets.md`
- **Deterministic canonicalization + signing rules** (JCS): `docs/176-canonicalization-and-signing-rules-for-evidence-envelopes.md`
- **Observer kit walkthrough** (offline verification): `docs/177-observer-kit-offline-verification-walkthrough.md`
- **Envelope kind registry** (small, stable API surface): `docs/178-envelope-kind-registry.md`
- **Evidence API surface** (what verifiers must implement): `docs/179-evidence-api-surface.md`
- **Receipts + gossip attachments** (anti-selective disclosure): `docs/180-receipts-and-gossip-attachments.md`

Earlier high‑leverage additions:
- Public randomness kernel for seeded sampling: `docs/168-public-randomness-beacons-and-seeded-sampling.md`
- Endorsement/reference-value transparency (North Star anti‑capture): `docs/169-endorsement-and-reference-value-transparency.md`
- Supply‑chain provenance profile (SLSA + in‑toto): `docs/170-slsa-and-intoto-provenance-profile.md`

If you ever worry “are we backing away from the full stack?”, the answer is **no**:
the archive is organizing the full stack into *tracks* so claims remain honest and auditable.

## Archive scope without archive bloat

This archive is **full‑stack in design scope**, but **size‑disciplined**:

- Do **not** embed third‑party PDFs or external works wholesale.
- Prefer citations + short excerpts (only when necessary) + pinned sources (`evidence/lock/`).
- Prefer original synthesis as **schemas, checklists, drills, and proof obligations**.

The primary reader is an **LLM maintainer**. Start with the claims contract:
- `166-scope-and-claims-contract.md`
- `167-non-claims-and-boundaries.md`

## Entry points (by track)
- **Track A:** `track-a/README.md`
  - Quick: `track-a/BUNDLE.md`
  - Release gate: `track-a/MVR_CHECKLIST.md`
- **Track B:** `track-b/README.md`
  - Quick: `track-b/BUNDLE.md`
- **Track C:** `track-c/README.md`
  - Quick: `track-c/BUNDLE.md`

## Global read order (15–30 minutes)
1. `154-project-scope-and-track-map.md`
2. `166-scope-and-claims-contract.md` + `167-non-claims-and-boundaries.md`
3. `00-design-goals.md`
4. `01-threat-model.md`
5. `04-transparency-log.md` + `23-witness-gossip-and-cross-checkpointing.md`
6. `159-proof-obligations-ledger.md` + `164-proof-obligations-registry.md`
7. `160-generated-canonical-spec-contract.md`
8. Pick a track readme and follow the suggested deep dives.

## If you are maintaining this archive
Start with `150-maintainer-bootstrap-and-change-protocol.md`.

## Canonical evidence packaging (new)
- Evidence envelopes + packet layout: `docs/173-canonical-evidence-envelopes-and-packets.md`
- Coverage accounting deliverable: `docs/174-coverage-accounting-and-representativeness.md`
- Publication compliance coverage: `docs/187-publication-compliance-and-coverage.md`

## Offline verification starting point
If you're an independent observer, start with:
- `docs/177-observer-kit-offline-verification-walkthrough.md`
- example packets:
- `artifacts/examples/evidence_packet_minimal/` (suppression report + required attachments)
- `artifacts/examples/evidence_packet_enr_receipted/` (ENR update + required attachments)
- `artifacts/examples/evidence_packet_publication_compliance_minimal/` (TriggerEvents + PublicNotice + publication coverage)
- reference checker: `tools/observer_verify_packet.py`