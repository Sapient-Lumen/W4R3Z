# 209 — Cross-register consistency evidence (VRDB ↔ results sanity checks)

**Track:** A (Deployable core)

ENR drift detection (`69`) catches *changes over time*. This doc adds a complementary, **cross-register constraint** check:

> **Results aggregates must not exceed eligibility aggregates for the same scope.**

This is not a fraud detector. It is a **loud, portable sanity check** that helps surface irrecoverable ambiguity (catastrophe class 3) early.

## 209.1 New evidence object: CrossRegisterConsistencyReport

- **Envelope kind:** `hfv.results.cross_register_consistency_report`
- **Payload schema:** `schemas/CrossRegisterConsistencyReport.json`

The report binds:
- a VRDB eligibility aggregate (via `VRDBSnapshot` payload digest), and
- a results aggregate (via CRO / ENRUpdate payload digest)

…and emits a bounded list of constraint checks.

### Minimal rules (normative)

1) **Bind inputs by digest**
   - `inputs.vrdb_snapshot_payload_sha256` MUST be present.
   - At least one results digest MUST be present (`cro_payload_sha256` or `enr_update_payload_sha256` or `results_payload_sha256`).

2) **Do not imply “pass” under missing data**
   - If aggregates are missing, the report SHOULD set `overall_status = "unknown"`.

3) **Scope alignment is part of the claim**
   - Each `checks[].scope_id` MUST describe the aggregation scope being constrained.
   - If scope mapping is ambiguous (VRDB and results roll up differently), set status to `unknown` and record the mismatch in `reason`.

4) **Slack must be explicit**
   - If a jurisdiction permits an “allowed overage” (provisional/exception handling), it MUST be encoded as `allowed_overage`.
   - Prefer `allowed_overage = 0` unless a written, precommitted rule exists.

## 209.2 What is checked

The base check is:

`ballots_accepted_total ≤ eligible_voter_count + allowed_overage`

The report MAY include multiple scopes (e.g., county + reporting units), but SHOULD stay bounded (one page worth of checks).

## 209.3 Why this matters (and what it does not do)

- **Catches “impossible totals”** early and portably.
- **Does not** replace audits, RLAs (`36`), or forensic analysis.
- **Does not** require any individual voter data; use aggregates only.

## 209.4 Inputs and privacy posture

- VRDB snapshots (`73`, `77`) MAY include an **aggregate eligible voter count** (`VRDBSnapshot.eligible_voter_count`).
- Cross-register evidence SHOULD avoid:
  - demographics,
  - per-voter records,
  - any identifiers that turn this into a participation/coercion surface.

## 209.5 Related

- `69` — ENR drift detection and alerting
- `73` — VRDB integrity and availability (aggregate eligible voter count)
- `159` — Proof obligations ledger (PO-004)
