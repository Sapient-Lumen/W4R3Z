# 257 — Supply chain, procurement, and vendor transparency as evidence surfaces

**Track:** Shared (cross-cutting)

This document defines **minimal, publishable evidence surfaces** for **software/hardware supply chain risk** in election systems *without* dumping sensitive configurations or operational details.

It is written to be **useful for election officials and labs**, and **safe to publish** (privacy-first; anti-weaponization).

---

## Why this exists

Even if your Election Day procedures are strong, **upstream compromise** (vendor build pipeline, updates, components, service providers) can undermine the integrity of the whole stack.

We want a publishable posture that answers:

- *What did you buy / install / update, and when?*
- *What did you demand from vendors (and what did they provide)?*
- *What do you do when a component is vulnerable or replaced?*
- *How do observers verify you did “the basics” without getting a map for sabotage?*

---

## External anchors (cite-first, do not bundle)

These are **anchors**, not requirements, and they evolve. Prefer the authoritative sources:

- NIST **SSDF** (SP 800-218 v1.1; and draft revision work). (NIST SP 800-218: xref: nist_sp800_218_final_html ; draft rev: xref: nist_sp800_218_r1_ipd_html)
- CISA **SBOM** guidance (including the 2025 “Minimum Elements” draft and hub). (CISA SBOM hub: xref: cisa_sbom ; 2025 Minimum Elements: xref: cisa_2025_minimum_elements_software_bill_materials_sbom ; PDF: xref: cisa_2025_08_2025_cisa_sbom_minimum_elements)
- SLSA **v1.2** (supply-chain levels + provenance model). (SLSA spec v1.2: xref: slsa_spec_v1_2 ; announcement: xref: slsa_blog_2025_11_announce_slsa_v1_2)
- EAC **Voting System Test Laboratories (VSTL)** program (and related manuals). (EAC VSTL program: xref: eac_voting_equipment_voting_system_test_laboratories_vstl ; VSTL program manual PDF: xref: eac_testingcertification_vstl_program_manual_version_3_0)
- NIST NVLAP Voting System Testing LAP context (HAVA §231 lineage). (NIST NVLAP Voting System Testing LAP: xref: nist_nvlap_voting_system_testing_lap)

---

## Design principles

1. **Hashes, attestations, and inventories over raw artifacts**
   - Publish **digests + provenance** (see `256`) rather than configs, binaries, or network diagrams.

2. **Evidence is about *process* and *coverage*, not “trust me”**
   - Publish what you demanded, what you received, and what you verified.

3. **No “crowbar artifacts”**
   - Do not publish anything that materially increases an attacker’s capability (e.g., service credentials, network topology, exploitable configuration detail).

4. **Separate “public proof” from “controlled-access evidence”**
   - Public pack: minimal, digest-first.
   - Controlled pack: available under lawful/role-appropriate access (see `253`).

---

## Minimal publishable artifacts (templates)

These are small, structured artifacts you can publish per **procurement**, **installation**, and **update**.

### 1) Vendor Transparency Packet (VTP)

A digest-first statement of what you demanded from vendors and what you received.

**Fields (minimum):**
- `vendor_id`, `product_line`, `version_scope`
- `sbom_present`: yes/no + `sbom_digest` (if yes)
- `provenance_present`: yes/no + `provenance_digest` (if yes)
- `vulnerability_disclosure_contact`: public channel (not individual PII)
- `support_window`: dates + policy URL
- `independent_testing_reference`: e.g., EAC certification / VSTL testing citation (where applicable)
- `attester_role`: “jurisdiction procurement officer” / “CISO” / etc.
- `signed_statement_digest` (if you publish a signed statement)

**Notes:**
- SBOMs may be sensitive. You can publish **SBOM digests** and controlled-access paths rather than full contents.

### 2) Component Inventory Snapshot (CIS)

A minimal “what is installed” list for the jurisdiction at a point in time.

**Fields (minimum):**
- `snapshot_time`
- `asset_classes`: e.g., EMS, scanners, BMDs, e-pollbooks, ENR, supporting servers
- For each class: `count`, `model_family`, `firmware_version_range`, `baseline_digest`
- `inventory_digest`
- `scope_note`: what is excluded (and why)

**Publishable proof:** CIS + digest; do not include serial numbers if that increases targeted threat risk.

### 3) Provenance & Build Assurance Attestation (PBAA)

A small statement that the jurisdiction requires and verifies build provenance.

**Fields (minimum):**
- `provenance_scheme`: “SLSA v1.2 provenance” (or equivalent)
- `verification_method`: “signature verification + digest match” (non-operational wording)
- `verified_by_role`
- `provenance_digest`
- `build_inputs_disclosed`: yes/no (and controlled-access reference if yes)

### 4) Vulnerability Handling Record (VHR)

A publishable record that a vulnerability affecting a component was tracked and closed without disclosing exploit paths.

**Fields (minimum):**
- `advisory_id` (CVE or vendor identifier)
- `affected_scope`: high-level scope tags (EMS / e-pollbook / etc.)
- `decision`: “mitigate / patch / replace / accept”
- `decision_time`, `closure_time`
- `public_statement_digest` (if published)
- `evidence_links`: hashes to CCP/SUP/EPDR artifacts in `256`

### 5) Decommission & Replacement Attestation (DRA)

When systems are replaced or removed.

**Fields (minimum):**
- `asset_class`, `count`
- `reason_code`: lifecycle / security / failure
- `sanitization_policy_ref` (policy citation; avoid operational detail)
- `inventory_before_digest`, `inventory_after_digest`
- `witnesses`: role count (not names)

---

## Procurement clauses (tight, adoptable)

This section is intentionally short: it provides *what to demand*, not a legal template.

Minimum demands for software-bearing election components:

- **SBOM availability** (at least controlled access) + a stable SBOM identifier/digest. (CISA SBOM hub: xref: cisa_sbom ; 2025 Minimum Elements PDF: xref: cisa_2025_08_2025_cisa_sbom_minimum_elements)
- **Secure development practices** attestation aligned to SSDF (and evidence available on request). (NIST SP 800-218: xref: nist_sp800_218_final_html)
- **Build provenance** attestation (SLSA provenance or equivalent). (SLSA spec v1.2: xref: slsa_spec_v1_2)
- **Vulnerability disclosure** channel + patch timelines + end-of-support policy.
- **Update transparency**: update packets and change-control artifacts compatible with `256`.

---

## Stop conditions (anti-weaponization)

Do **not** publish:

- Network diagrams, IP ranges, firewall rules, credentials, remote-access procedures.
- Per-device serial numbers if that enables targeted intimidation or theft.
- Full SBOM contents if it materially increases targeting (publish digests + controlled access instead).
- Detailed vulnerability exploitation notes, step-by-step testing against live systems.

If a request pushes you here, route through `253` (public records + access bounds) and/or `249` (safe red-teaming).

---

## How this connects to the rest of the stack

- Use `256` for baselines, updates, emergency patches, and drift: the **Supply Chain artifacts link into the hash ladder**.
- Use `252` for ENR snapshot packs and `237`/`251` for canvass and resolution lifecycles.
- Use `246` to write an assurance claim like: “Supply-chain transparency evidence is present and reviewable.”

---

## Minimal checklist (one page)

A jurisdiction can publish the following quarterly (or per major update) without bloat:

1. CIS (inventory snapshot) + digest
2. VTP (vendor transparency packet) per component family
3. PBAA (provenance attestation) for any updates received
4. VHR entries for advisories encountered in the period
5. DRA entries for decommissioned/replaced assets

That’s enough for outside verifiers to see **coverage**, **change**, and **responsiveness** without handing attackers a blueprint.
