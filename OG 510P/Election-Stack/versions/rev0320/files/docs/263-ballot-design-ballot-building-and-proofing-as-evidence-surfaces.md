# 263. Ballot design, ballot building, and proofing as evidence surfaces

**Track:** Shared


Ballot design and ballot building are *high-leverage* integrity points: small layout / ordering / language errors can produce
systematic voter mistakes, disputes, and recount pain. This doc defines **publishable, privacy-first evidence surfaces**
for ballot production that improve checkability **without** releasing sensitive internal configuration or voter data.

This is intentionally *bounded*: it is not a state-by-state requirements table. Pair with `262-jurisdictional-policy-surface-registry.md`
to link jurisdiction-specific “knobs” (rotation rules, contest order, required notices, etc.) to the evidence surfaces below.

## Goals

- Make ballot production **auditable by outsiders** (candidates, parties, observers, press, courts) using a small set of artifacts.
- Provide a **change-controlled chain** from authoritative contest definitions → ballot styles → proofs → approvals → final print/export.
- Avoid leaking sensitive internals (EMS configuration, precinct targeting, adversary-relevant details) and avoid publishing voter PII.

## Non-goals / stop conditions

Stop and escalate to counsel / security review if a request would:
- publish **ballot style→precinct mappings** at a granularity that enables targeted disruption,
- disclose **internal EMS configuration** (screens, exports, credentials, network paths),
- publish any **voter-level data** (including identifiers embedded in proof annotations).

When responding to public records requests, route through `253-public-records-requests-retention-and-access-bounds.md`.

## External anchors (cite-first)

- **EAC Ballot Building Quick Start Guide** (practical checklist + common error classes).
- **EAC Effective Designs / election design guidelines** (layout, typography, instructions).
- **NIST VTS 100-4 (2025)** on legibility and verification of summary-style printed ballots (BMD summaries).

## Minimal publishable artifacts

These artifacts are designed to be publishable (or publishable as digests) without exposing sensitive configuration.

### 1) Authoritative contest definition digest (ACDD)

**What:** A signed digest (hash) of the authoritative contest definition input set:
- contest list, candidate names, ballot measures, districting references, required notices, language versions.

**Publish:** A hash + metadata (scope, election date, jurisdiction, version). Optionally publish a redacted “human-readable digest”
that contains *only* contest text and ordering (no precinct/style mapping).

**Why:** Establishes an immutable anchor so later “ballot proof” disputes can be checked against the input set.

### 2) Ballot style manifest digest (BSMD)

**What:** A digest of the *set* of ballot styles (not their precinct assignments), including:
- style identifiers,
- contests included,
- language variants,
- paper size / format classes,
- device modality classes (hand-marked, BMD summary, etc.).

**Publish:** Hash + counts (e.g., “42 styles, 6 language variants”). Do **not** publish precinct mappings.

### 3) Ballot proof packet (BPP)

**What:** The bounded bundle used for proofing:
- rendered proofs (PDF) for each style,
- proofing checklist,
- issue log (with stable reason codes),
- fix confirmations.

**Publish (preferred):**
- a **Proof Packet Digest** (hash of the packet),
- an **Issue Summary Table** (aggregate, no sensitive mappings),
- optionally a subset of proofs for public contests (if allowed and safe).

### 4) Proof approval ledger (PAL)

**What:** An append-only ledger of approvals:
- who approved (role, not personal name if sensitive), when, what was approved (hash),
- approval scope (style set, language, device class),
- explicit statement of what *was not* approved (e.g., “no precinct mapping review”).

**Publish:** PAL entries as hashes + role labels + timestamps.

### 5) Print/export release attestation (PERA)

**What:** A final attestation that the printed/exported ballots match the approved proofs:
- print vendor / facility identity (as allowed),
- production run identifiers,
- hash references to the proof packet and approvals.

**Publish:** PERA digest + counts (ballots printed by style class), and a redaction note for any restricted fields.

## Workflow (tight)

1. Produce ACDD from authoritative sources (contest list, legal notices, translations).
2. Generate BSMD from the style set *without* precinct mapping disclosure.
3. Generate BPP and run proofing with multi-person review (independent eyes).
4. Close issues via issue log; regenerate BPP until stable.
5. Record approvals in PAL (hash-linked).
6. Produce PERA linking to the approved hashes.

## Interfaces with other Election Stack modules

- **Change control:** link ACDD/BSMD/BPP hashes into `256-software-updates-and-configuration-control-as-evidence-surfaces.md`.
- **Public commitments:** publish PAL + PERA digests via `261-public-commitments-and-transparency-logs-for-election-evidence.md`.
- **Accessibility & language access:** ensure proofs cover accessibility instructions and language variants (`248-*`).
- **Adjudication & voter intent:** ballot design decisions directly affect adjudication rates (`254-*`).

## Minimal metrics to publish (aggregate)

- number of styles, languages, and device classes,
- number of proofing rounds,
- number of issues found (by category), and number resolved before print/export,
- number of late changes after first proofing (with reason codes).

These metrics help outsiders reason about process quality without requiring sensitive access.


## Primary anchors

- [EAC — Ballot Building Quick Start Guide (PDF)](https://www.eac.gov/sites/default/files/electionofficials/QuickStartGuides/Ballot_Building_EAC_Quick_Start_Guide_508.pdf)
- [EAC — Quick Start Guides index](https://www.eac.gov/election-officials/quick-start-guides)
