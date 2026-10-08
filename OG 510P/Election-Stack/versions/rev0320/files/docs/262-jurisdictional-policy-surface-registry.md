# 262 — Jurisdictional policy surface registry (JPSR)

**Track:** Shared

Election administration is *decentralized*: many properties that matter for integrity, security, and public comprehension are set by **state law**, **local procedure**, and **vendor configuration**. A research archive that pretends these are uniform will either (a) drift into inaccuracy or (b) bloat into state-by-state tables that rot.

This spec introduces a **Jurisdictional Policy Surface Registry (JPSR)**: a *small*, change-controlled registry of **which policy knobs exist**, **who sets them**, and **where the authoritative reference lives** (law/regulation/manual), plus a minimal publication surface that supports transparency without leaking sensitive details.

## Design goals

- **Bounded size:** track *knob taxonomy* and *references*, not state-by-state encyclopedias.
- **Cite-first:** link to authoritative sources; avoid copying jurisdiction-specific legal text.
- **Verifiable change control:** updates to the registry are logged and committed (pair with `261`).
- **Privacy / safety:** never include voter PII; never publish operationally sensitive configurations.

## What counts as a “policy surface”

A **policy surface** is a decision that meaningfully affects election outcomes, access, or verifiability and that is chosen by a jurisdiction (state/local) or by an election office under delegated authority.

Examples (non-exhaustive):
- **Ballot availability rules:** UOCAVA flows, in-person early voting windows, ID requirements (varies by state/local).
- **Mail ballot pipeline:** application rules, drop box policy, signature verification + cure windows.
- **Canvass rules:** deadlines, procedures for recount triggers, adjudication authority.
- **Audit rules:** whether RLA is required, audit type (comparison vs polling), escalation policy.
- **Data publication rules:** what gets published (precinct totals, CVR availability), when, and in what format.
- **Observer/challenge rules:** who may observe, challenge procedures, conduct rules.

**Non-goals:**
- Capturing every legal nuance.
- Publishing sensitive internal configurations (e.g., EMS settings, device serial inventories).

## The JPSR object model (minimal)

A JPSR is a directory (or single file) containing a set of policy-surface records.

Each **PolicySurfaceRecord (PSR)** includes:

- `psr_id` — stable identifier (e.g., `PSR.MAIL.CURE.WINDOW`).
- `title` — short human name.
- `scope` — `{state|local|hybrid}` (who sets it).
- `authority` — `{law|regulation|policy_manual|contract|mixed}`.
- `control_owner` — `{legislature|chief_election_officer|local_office|court|vendor|mixed}`.
- `integrity_impact` — brief tag set (e.g., `access`, `tabulation`, `chain_of_custody`, `public_trust`).
- `evidence_surfaces` — references to the numbered specs that should exist if this knob matters (`251`, `254`, `255`, `260`, etc.).
- `authoritative_refs` — citations to the best primary sources:
  - EAC/NCSL state election profiles (high-level, comparative)(EAC/NCSL State Election Profiles)
  - EAC Election Management Guidelines (operations and administration, evolving best practice)(EAC Election Management Guidelines)
  - NCSL overview of state/local election administration structures (decentralization and roles)(NCSL election administration overview/toolkit)
  - EAC best-practices note about decentralized administration and “ask your local official” (useful for scoping claims)(EAC best practices FAQs)
  - NIST CDF implementation guidance (where policy knobs affect data models, e.g., geography/ballot styles/results)(NIST CDF implementation guidance)
- `notes_public` — safe-to-publish notes (no sensitive detail).
- `notes_internal` — optional (keep private; link via hash if needed).
- `updated_at`, `updated_by`, `change_reason`.

### Storage format

Keep it boring:
- Preferred: `schemas/jpsr/psr-*.yaml`
- Alternate: `schemas/jpsr/jpsr.jsonl`

## Publication surface (do not bloat)

Publish only:
1. **PSR list + citations** (no sensitive configs).
2. **Commitment hashes** (pair with `261`):
   - hash of each PSR file
   - hash of the registry index
3. **Change log digest**:
   - what PSR IDs changed and why (coarse reasons)

If a jurisdiction wants to publish *more detail*, route through `253` (records + access bounds) and apply strict minimization.

## Workflow

1. **Discover** a policy surface (from statute, manuals, vendor docs, incident lessons).
2. **Create/Update PSR** with authoritative citations and linked evidence surfaces.
3. **Run a “surface audit”**: ensure referenced evidence artifacts exist (or are tombstoned).
4. **Commit + publish digest** (CLE, `261`).

## Stop conditions (safety / dual-use)

Do **not** publish:
- passwords, network diagrams, device inventories with serials, detailed facility layouts
- ballot images, CVRs, or anything that enables targeted manipulation
- personal data about voters, poll workers, or observers

When in doubt, publish **hash commitments** and **process descriptions**, not raw materials.

## Why this matters

- Helps avoid “one-size-fits-all” claims in public communication and research.
- Creates a durable bridge between **policy** and **verifiable evidence surfaces**.
- Keeps the archive tight: “taxonomy + references + commitments”, not sprawling state-by-state annexes.


## References (external anchors)

- EAC/NCSL State Election Profiles: https://www.eac.gov/election-officials/eac-ncsl-state-election-profiles
- EAC Election Management Guidelines (EMG): https://www.eac.gov/election-officials/election-management-guidelines
- EAC Best Practices / FAQs for election officials (decentralization note): https://www.eac.gov/best-practices-faqs-election-officials
- NCSL: Election administration at state and local levels: https://www.ncsl.org/elections-and-campaigns/election-administration-at-state-and-local-levels
- NCSL: Poll worker & election official policy toolkit (decentralization/roles context): https://www.ncsl.org/elections-and-campaigns/poll-worker-and-election-official-policy-toolkit
- NIST: Implementation Guidance for Common Data Formats (GCR 24-058): https://nvlpubs.nist.gov/nistpubs/gcr/2024/24-058/NIST.GCR.24-058.html
