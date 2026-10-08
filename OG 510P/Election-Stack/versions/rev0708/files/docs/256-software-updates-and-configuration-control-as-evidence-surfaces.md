# 256 — Software updates & configuration control as evidence surfaces

**Track:** Shared  
**Status:** Draft (deployable pattern; jurisdiction/vendor constraints apply)

This spec defines **minimal, publishable artifacts** that make software/firmware updates and configuration changes *checkable* without disclosing sensitive configuration, exploitable details, or voter data.

It is designed to pair with:
- `247-ops-security-controls-comms-and-chain-of-custody.md` (custody + comms)
- `249-threat-model-ledger-and-safe-red-teaming.md` (authorized testing guardrails)
- `253-public-records-requests-retention-and-access-bounds.md` (access bounds)
- `255-logic-and-accuracy-and-pre-election-testing-as-evidence-surfaces.md` (pre-election testing)

---

## 256.1 Core principle

**If a change can change outcomes, it must leave a trace.**  
But the trace should usually be **hashes + attestations + process logs**, not full configs.

This is a configuration-management framing aligned with:
- NIST SP 800-128 (security-focused configuration management)  
  xref: nist_pubs_sp_800_128_upd1_final
- NIST SP 800-53 Rev. 5 CM-family controls (configuration management controls catalog)  
  xref: nist_pubs_sp_800_53_r5_upd1_final
- CISA general hardening guidance for election infrastructure  
  xref: cisa_best_practices_securing_election_systems_page
- EAC voting system standards / lifecycle context for testing & certification  
  xref: eac_voting_equipment_voluntary_voting_system_guidelines  
  xref: eac_testingcertification_vvsg_lifecycle_policy_9_22

---

## 256.2 Threats this module addresses (non-exhaustive, non-operational)

- **Unauthorized changes** (malicious or accidental) to tabulation, reporting, or supporting tech (EMS, e-pollbooks, ballot-on-demand, ENR).
- **Configuration drift** between “tested” and “used”.
- **Ambiguous provenance**: unclear who changed what, when, and under which authority.
- **Emergency patch pressure** without auditable decisioning.
- **Weaponization risk**: demands for detailed configs / network diagrams / machine-level data that increase attack surface.

---

## 256.3 Minimal artifact set (publishable)

### A) Configuration Baseline Attestation (CBA)
A short, public artifact stating:
- named system scope (e.g., “County X EMS”, “Polling-place e-pollbook fleet”)
- baseline identifier (human-readable ID)
- baseline hash list (see `256.4`)
- date/time + authority
- whether baseline was used for L&A / pre-election testing (link to `255-*` artifacts)

**Publish:** yes (hashes + metadata only).  
**Do not publish:** full configuration files, passwords, IPs, firewall rules, detailed topology.

### B) Change Control Packet (CCP)
For each planned change window:
- change summary (what/why; outcome-relevant? yes/no)
- approvals (roles only; no personal data if avoidable)
- rollback plan summary
- evidence pointers: baseline hash set before/after
- linkage to canvass / ENR / L&A if applicable

**Publish:** a redacted CCP summary + hashes.

### C) Software/Firmware Update Packet (SUP)
When software/firmware is updated:
- vendor release identifier
- artifact hashes (installer / firmware image / signed package)
- verification method (signature verification performed? yes/no + method class)
- deployment scope + dates (aggregate)
- *post-update* minimal verification performed (e.g., targeted smoke test, limited L&A rerun)

**Publish:** yes, **but** keep it at “package-level” and avoid environment specifics.

### D) Emergency Patch Decision Record (EPDR)
For time-sensitive patches:
- reason code (e.g., “externally-disclosed vuln”, “field failure”, “certification update requirement”)
- decision authority + time (roles)
- risk tradeoff summary (why now vs later)
- compensating controls applied (high-level)
- follow-up verification plan + deadlines

**Publish:** yes (summary + dates + hashes), **unless** it would reveal a live weakness window.

### E) Configuration Drift Ledger (CDL)
A periodic statement:
- baseline ID expected
- baseline ID observed
- delta status: match / mismatch / unknown
- if mismatch: whether corrected, and link to CCP/EPDR

**Publish:** yes, aggregated.

---

## 256.4 Hash ladder pattern (how to publish without leaking)

Publish **hashes at the right abstraction layer**:

1) **Package/Image hashes** (SUP)  
2) **Baseline hash set** (CBA) — a list of hashes for *approved* config objects (not the objects)  
3) **Snapshot pack hash** (URSP/ENR snapshot packs in `252-*`)  
4) **Canvass reconciliation hash** (from `251-*`)

This creates an **audit spine** without publishing sensitive internals.

---

## 256.5 Safe boundaries and stop conditions (hard rules)

Stop and route to `253-*` (PRR bounds) and counsel if any request demands:
- voter PII or ballot-level trace data
- raw configuration files, admin credentials, network diagrams, detailed device inventories
- “forensic images” or machine access outside a lawful, controlled, and scoped process
- any publication that plausibly increases attack surface in the current election cycle

---

## 256.6 Suggested integration points (minimal edits elsewhere)

- Add “baseline ID + hash set” fields to L&A artifacts in `255-*`.
- Ensure ENR snapshot packs in `252-*` record the software baseline ID used for reporting.
- Ensure chain-of-custody artifacts in `247-*` reference the same baseline IDs for transported media/devices.

---

## 256.7 Templates (one-screen each)

### Template: CBA (Configuration Baseline Attestation)
- System scope:
- Baseline ID:
- Baseline hash set ID:
- Approved by (role/title):
- Effective datetime:
- Used for L&A / pre-election tests? (link):
- Notes (non-sensitive):

### Template: EPDR (Emergency Patch Decision Record)
- System scope:
- Trigger:
- Patch identifier:
- Decision authority (role):
- Decision datetime:
- Compensating controls (high-level):
- Verification plan:
- Public disclosure timing:
