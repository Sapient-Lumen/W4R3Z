# Conflict of Laws and Cross‑Border Dispute Rails

**Cross-stack note:** use `305-interjurisdiction-compacts-authority-routing-and-cross-border-dispute-guide.md` for the canonical route across the inter-jurisdiction / compacts / authority-routing / cross-border-dispute family. This memo is the cross-border recognition / conflict-of-laws / dispute specialization; `221` is the authority-routing substrate; `114` handles domestic inter-authority ping-pong and interim continuity; `19` handles compacts; `197` handles overlapping sovereignty and federal design; and `296` remains the person-status / continuity neighbor when the seam is mainly about recognition of valid proof or status.

**Problem:** When a dispute or obligation crosses borders (people, firms, data, assets), systems routinely fail in three predictable ways:

1) **Ping‑pong:** each jurisdiction claims the other is responsible.
2) **Trap doors:** rights and remedies disappear at the seam (no enforceable lane).
3) **Weaponized jurisdiction:** powerful parties exploit forum shopping, delay, or non-recognition.

This memo defines a minimal, publishable set of **rails** that make cross‑border obligations legible, contestable, and enforceable without requiring a single world government.

## Scope

This memo targets *cross‑border civil / commercial* and *administrative coordination* interfaces:

- Civil/commercial judgments and interim measures.
- Arbitration awards (where used) and court oversight.
- Cross‑border insolvency coordination.
- Administrative cooperation for licensing/credentials/status continuity (ties to `203`, `211`, `212`).

Criminal mutual legal assistance and extradition require separate safeguards; reference only.

## Invariants (non‑negotiable)

1) **No wrong door across borders:** A person must be able to file in *one* place and receive a routing receipt that identifies a **single-responsible endpoint (SRE)** for cross‑border coordination (`195`, `221`).

2) **Continuity at seams:** Pending status/benefits/rights must not lapse while jurisdictions coordinate. If coordination time exceeds a public clock, a **temporary protective status** is granted (`109`, `189`).

3) **Jurisdiction is stated as a packet:** Every cross‑border decision must publish a compact **Jurisdiction Packet**: basis, connecting factors, notice/service method, translation availability, and contest lane. (Do not paste statutes; reference them.)

4) **Recognition baseline + refusal reasons are bounded:** If a matter is within a recognized framework, recognition/enforcement is the default; refusals must be receipted and appealable.

5) **Human-rights floor overrides:** No cross‑border recognition/enforcement may produce outcomes that violate the system’s declared rights floor (see `98`, `209`, `204`, `205`).

## The Jurisdiction Packet (JP)

Every cross‑border decision or enforcement request issues a JP with:

- `JP-id` (stable)
- `matter_type` (controlled vocabulary)
- `requested_action` (recognize/enforce/interim relief/coordinate)
- `origin_forum` + `target_forum`
- `connecting_factors` (e.g., domicile, place of performance, asset location)
- `legal_basis_refs` (treaty / statute / rulebook pointers)
- `notice_service` method and proof
- `language_access` offer (translation / interpretation)
- `contest_lane` (where + deadline + cost/help)
- `continuity_duty` statement + clock
- `enforcement_mode` (if any) + proportionality checks

Implementation note: treat JP as a first‑class receipt object (`31`, `53`, `115`).

## The Cross‑Border Router (XBR)

Extend `221`’s Authority Router with a cross‑border layer:

- Resolve the **SRE** for cross‑border coordination.
- Identify the applicable framework(s):
 - judgments recognition/enforcement (`[BIB-HCCH-JUDGMENTS-2019]`, EU example: `[BIB-EU-BRUSSELSI-1215-2012]`)
 - choice of court (`[BIB-HCCH-CHOICE-OF-COURT-2005]`)
 - arbitration (`[BIB-UNCITRAL-ML-ARB-1985-2006]`, `[BIB-UN-NY-ARB-1958]`)
 - insolvency coordination (`[BIB-UNCITRAL-ML-CBI-1997]`)
- Emit a public **routing receipt**: why this SRE, why this framework, what the person can do next.

### Default precedence (anti‑weaponization)

1) **Protective continuity** first (stop rights cliffs).
2) Apply the **most specific** applicable framework.
3) If multiple apply, choose the one with **strongest due‑process guarantees** and lowest coercion.
4) If no framework applies, fall back to a published **comity policy** with bounded refusal reasons and appeal.

## Anti‑abuse controls

- **Forum shopping detector:** publish an anonymized quarterly report of cross‑border disputes where forum choice appears outcome‑determinative (trigger review of connecting‑factor rules).
- **Delay tax:** if a party prolongs cross‑border coordination beyond thresholds, impose cost shifting unless justified.
- **Non‑recognition as a red flag:** repeated refusal by a forum triggers a diplomatic/oversight review (treat as system risk; `183`).

## Tests (add to `107`)

- **T0.6 — Cross‑border no ping‑pong:** For any cross‑border matter, the system returns one SRE and issues a JP with continuity duty and contest lane.
- **T3.20 — Recognition/refusal is bounded:** Refusals cite one of a bounded list of reasons and provide an appeal lane with a public clock.
- **T3.21 — Seam continuity holds:** rights/status do not lapse during cross‑border coordination; temporary protection activates when clocks breach.

## Why this belongs in the archive

Many governance failures are not “local” failures—they are seam failures. A jurisdiction graph without a conflict‑of‑laws lane still allows accountability to evaporate at borders. This memo turns cross‑border coordination into an interface with receipts, clocks, and bounded discretion.
