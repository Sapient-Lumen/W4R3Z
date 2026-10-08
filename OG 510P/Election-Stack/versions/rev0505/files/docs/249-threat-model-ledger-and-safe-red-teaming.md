# 249 — Threat-model ledger & safe red-teaming (bounded, non-weaponizing)

**Track:** Shared


**Purpose:** Give this archive a *repeatable* way to talk about adversaries, failures, and tests **without** turning into a how-to manual for interference.

This note is deliberately **procedural** and **evidence-minimizing**: it prefers checkable claims, hashes, and scope statements over operational detail.

## Core idea: a “Threat Model Ledger” (TML)

Maintain a lightweight ledger that connects:

- **Asset / property** (what we protect): integrity, availability, privacy, legitimacy, accessibility.
- **Threat class** (what could go wrong): misconfiguration, insider error, supply chain, cyber intrusion, physical tampering, disinformation, process gaps.
- **Attack surface** (where it can happen): registration systems, EMS, tabulators, ballot chain-of-custody, reporting sites, public comms, pollbooks, vendors.
- **Controls** (what prevents/detects/recovers): policy + technical + procedural.
- **Observable proofs** (what we can publish): hashes, logs, change records, training completion counts, audit summaries.
- **Residual risk statement** (what remains): explicit, dated, owned.

The TML is *not* a universal taxonomy. It’s a practical crosswalk to keep reasoning aligned with established risk practice and control catalogs.
(See NIST risk assessment guidance and control catalogs for baseline vocabulary and structure.)  
- NIST SP 800-30 Rev. 1 — risk assessments: xref: nist_pubs_sp_800_30_r1_final  
- NIST SP 800-53 Rev. 5 — control catalog: xref: nist_pubs_sp_800_53_r5_upd1_final

## Minimal schema (suggested fields)

Use a single table (or YAML) with these columns:

- `id` (stable)
- `asset_property` (e.g., “cast vote record integrity”)
- `threat_class` (high-level)
- `surface` (system/process boundary)
- `control_refs` (internal doc pointers + external anchor)
- `evidence_refs` (hashes / filenames / attestations)
- `test_method` (e.g., “tabletop”, “configuration review”, “independent audit”, “RLA summary”)
- `status` (planned / in-progress / verified)
- `owner` + `date`

**Rule:** keep `test_method` at the level of *type*, not exploit steps.

## Safe red-teaming: boundaries and guardrails

“Red-team” work here means **testing a defended system or process** with authorization and safety controls. Guardrails:

1. **Define scope as a contract:** system boundaries, time window, what’s explicitly out-of-scope (e.g., voter targeting, social engineering).
2. **Prefer non-production & synthetic data:** isolate; never touch live voter data.
3. **No exploit recipes in the archive:** store only *findings* at a high level + control/evidence changes.
4. **Dual-purpose filter:** if a detail would materially aid interference, it does not go in.
5. **Evidence-minimize:** use hashes of artifacts, change tickets, and reproducible steps *for defenders* (not for attackers).

For threat-informed vocabulary that stays broadly non-operational, you can reference MITRE ATT&CK at the level of **tactics/technique IDs** without embedding step-by-step usage:
xref: mitre_attack_page

## “Publishable proof” patterns (keep it small)

Prefer proofs that increase trust without exposing systems:

- **Change-control receipts:** date, approver role, ticket id, hash of config bundle.
- **Training attestations:** counts + dates (no names).
- **Audit summaries:** RLA outcomes at summary level; procedures and randomness sources.
- **Comms control proofs:** templated incident statement inventory; practice schedule.

For baseline election security practice framing, use CISA election security resources as an external anchor:
- Best practices for securing election systems: xref: cisa_best_practices_securing_election_systems_page  
- Voting system security measures: xref: cisa_voting_system_security_measures

## Integration points in this archive

- Link each TML row to:
  - **Assurance case skeleton** (claims/evidence): see `docs/246-*`
  - **Ops controls & comms**: see `docs/247-*`
  - **External anchors map**: see `docs/245-*`

## Stop conditions

If discussion drifts into “how to do X to compromise Y,” stop and replace with:

- **What property is at risk?**
- **What control class mitigates it?**
- **What publishable proof demonstrates the control exists?**
- **What residual risk remains and who owns it?**
