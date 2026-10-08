# Interjurisdictional Dispute & Coordination (Cross-scope)

**Cross-stack note:** use `305-interjurisdiction-compacts-authority-routing-and-cross-border-dispute-guide.md` for the canonical route across the inter-jurisdiction / compacts / authority-routing / cross-border-dispute family. This memo is the live inter-authority dispute-lane / anti-ping-pong specialization; `17` handles boundary and map change; `19` handles compacts; `197` handles overlapping sovereignty and multi-level design; `219` handles shared-service operations; `221` is the authority-routing substrate; `230` handles cross-border legal recognition and conflict-of-laws; and `296` remains the person-status / continuity neighbor.

**Purpose:** settle overlaps, conflicts, and spillovers between jurisdictions/agencies **without** making the governed person pay the cost of institutional warfare.

**Person served:** A person or community caught between two (or more) authorities—each claiming the other is responsible—who needs continuity, a single accountable lane, and a timely binding resolution.

**From-below:** This prevents “ping‑pong governance” by forcing a receipted dispute lane, interim protection, and a binding result with named enforcement hooks.

**EXP pointer:** `EXP-02` (Waiting), `EXP-06` (Ping‑pong), `EXP-01` (Opacity) — see `98-persons-path-and-accessibility-invariants.md`.

**Material floor (one sentence):** this protocol MUST function with paper forms, phone, and in‑person escalation; no accounts or cross‑system identity links required to invoke. (See `98`, `31`, `70`, `101-claude-rev142-normative-requirements.md` (NR-13).)

---

## Core concept: Coordination Receipt + Interim Continuity

When jurisdictional conflict is present (or alleged), the system MUST produce:
- **A Coordination Receipt (`CRD-*`)**: a single case handle that binds the parties into one visible lane.
- **Interim continuity default:** the person’s access/benefit/safety MUST NOT lapse **because** authorities disagree about scope, venue, or funding, unless a specific, reviewable harm exception is published and appealable. (See `109-portability-and-cross-jurisdiction-continuity.md`, `108-service-standards-and-time-budgets.md`.)

---

## Minimal spec (obligations)

### DR-1: Detect and label a scope conflict
- Any worker/system that detects a cross‑boundary conflict MUST label the case `SCOPE-CONFLICT` and issue `CRD-*` within **1 business day**.
- `CRD-*` MUST include: parties, asserted scopes, what is at stake, interim continuity rule, next deadline, and the contact point for each party. (Receipt semantics: `31-records-foi-and-government-memory.md`.)

### DR-2: Single accountable front door (no ping‑pong)
- The person MUST have **one** filing point that is responsible for driving the inter‑authority process, even if it is not the final venue.
- If the person filed with the “wrong” authority, the receiver MUST forward and remain accountable until the `CRD-*` lane is accepted by a lead. (See `109` transfer‑of‑file rule.)

### DR-3: Interim protection / non‑reset defaults
- During the dispute, apply **provisional continuity**: preserve access and status quo protections; do not reset evidence or restart clocks.
- Any deviation MUST be accompanied by (a) a reason code `RC-*`, (b) a time‑bounded order, and (c) an immediate appeal lane `AL-*`. (See `52-reason-codes-registry.md`, `36-appeal-lanes-and-redress-registry.md`, `85-waivers-variances-and-exceptions-discipline.md`.)

### DR-4: Binding decision in bounded time
- The lane MUST define a **binding decider** for each conflict class (e.g., joint board, ombuds, court, arbitration panel, statutory coordinator).
- Default deadline: **30 days** for ordinary cases; **7 days** for high‑harm classes; **24–72 hours** for imminent safety classes.
- If deadline is missed: trigger an automatic **escalation + interim protection extension** and publish the miss in the Exceptions/Delay ledger. (See `104-governance-control-loops.md`, `108-service-standards-and-time-budgets.md`, `112-exception-control-and-emergency-powers.md` (Exceptions Ledger pattern).)

### DR-5: Cost/funding disputes cannot block service
- If the dispute is about **who pays**, service MUST proceed under a **“pay now, reconcile later”** rule with a reconciliation ledger entry.
- Parties MAY create balancing transfers, but MUST NOT make the person re‑apply or re‑prove eligibility.

### DR-6: Enforcement hooks (what happens if a party refuses)
The protocol MUST specify at least one enforcement hook per party class:
- **Administrative:** mandatory senior sign‑off + public non‑compliance flag.
- **Financial:** withholding/offsetting transfers or conditional funding.
- **Legal:** contempt/mandamus or statutory compliance order.
- **Operational:** substitution (another authority temporarily executes the duty) with back‑charge.
(See `55-oversight-findings-and-response-register.md`, `97-public-investment-and-capital-project-governance.md`.)

### DR-7: Publication, privacy, and protective legibility
- Publish *aggregate* conflict metrics and resolution times by class; do not publish personally identifying case details by default. (See `99-protective-legibility-and-adoption-dynamics.md`.)
- The `CRD-*` lane MUST support confidential filing and protected representation. (See `83-whistleblowing-and-protected-disclosures.md`.)

---

## Conflict classes (starter table)

- **Venue conflicts:** which court/tribunal/agency hears the case.
- **Scope overlaps:** two authorities regulate the same actor/domain.
- **Spillovers/externalities:** upstream decisions harm downstream jurisdictions.
- **Resource disputes:** funding, staffing, capacity allocation.
- **Data/identity conflicts:** incompatible records or identifiers (must not block access).

---

## Minimal metrics (for `107` test suite)

- % cases labeled `SCOPE-CONFLICT` that receive `CRD-*` within 1 day.
- Median time to binding resolution by class; tail (p90/p95).
- % disputes where interim continuity prevented lapse (should be ~100% except published exceptions).
- Non‑compliance rate by party; enforcement hook activation counts.
- Person‑reported “ping‑pong” incidence (survey/complaint tag).

---

## References (citation keys)
- `[BIB-UN-CHARTER-ART33]` (pacific settlement obligation pattern).
- `[BIB-ICJ-STATUTE]` (judicial settlement as a backstop).
- `[BIB-OECD-MLG-HUB-2026]` (multi‑level governance coordination / spillovers).
