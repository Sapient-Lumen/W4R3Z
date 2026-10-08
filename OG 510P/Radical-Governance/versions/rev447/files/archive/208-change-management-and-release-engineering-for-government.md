# Change Management & Release Engineering for Government (CHG-* + REL-* + PIR-*)

**Purpose:** make policy, service, data, and algorithm changes **legible, reviewable, reversible, and learnable**—so governance can move fast **without** silent breakage, rights violations, or “nobody knows who approved this.”

**Person served:** (1) a person affected by a change who needs **clear notice + reason + remedy**, and (2) an operator/public servant who must ship change safely under scrutiny.

**Core idea:** treat governance change as an **operational discipline** (like safety‑critical engineering): every meaningful change has a *packet*, a *receipt*, a *release note*, monitoring, and a post‑implementation review—joined to authority and remedy.

---

## A. Invariants (non‑negotiable)

1. **No silent swaps:** material changes must publish an “as‑of” delta and a receipt. (Pairs with `53-publication-integrity-and-tamper-evident-logs.md` and `39-rulebook-and-instruments-registry.md`.)
2. **Reversibility is designed, not wished:** every change declares a rollback class and plan (including “cannot roll back” + compensation plan).
3. **Notice is part of the change:** affected people get notice that is *timely, understandable, and actionable* (including remedy paths).
4. **Change joins to authority:** each change links to its legal basis / mandate and the accountable owner.
5. **Learning is mandatory:** every material change has a PIR (post‑implementation review) with public findings when safe.

---

## B. What counts as a “change”?

A change is **material** if it alters any of:

- eligibility, obligations, or enforcement intensity
- benefit levels, taxes, fees, or time budgets
- decision logic (human or automated), thresholds, scoring, or ranking
- required evidence / data fields / identity proofs
- service access paths, defaults, or error/appeal behavior
- surveillance, data sharing, retention, or disclosure posture
- procurement/vendor role, model/data versions, or outsourcing boundary

If it’s material: **CHG‑packet required**.

---

## C. Artifacts (small, standardized, joinable)

### CHG-* Change Packet (the unit of review)
Minimum fields:

- **CHG-ID**, owner, scope, affected services (`SRV-*`), and authority link (mandate / legal basis).
- **Delta summary:** what changes, for whom, and why (plain language + technical).
- **Rights/risk screen:** human rights / equity / due process / privacy / safety (links to AIA or equivalent where relevant).
- **Rollback class** (R0–R4) + rollback plan:
  - **R0:** config/content revert
  - **R1:** policy parameter revert
  - **R2:** partial rollback + compensations
  - **R3:** cannot rollback quickly (migration required) + containment
  - **R4:** irreversible (requires Harder Path / constitutional‑level controls)
- **Monitoring plan:** what will be watched (SLOs, error budgets, harm signals).
- **Remedy readiness:** what appeal lanes (`AL-*`) apply; interim protection if needed.
- **Comms plan:** notice text, channels, translation, accessibility.
- **Stakeholder touchpoints:** consultation/deliberation link(s) when required (`ENG-*`).
- **Implementation plan:** deployment steps + owners + time window.

### REL-* Release Note (the unit of public legibility)
- what changed (human readable)
- effective date/time and “as-of” pointers
- known risks/limits
- where to get help / contest / appeal
- how to verify the current rule or version

(See `51-release-registry.md`.)

### PIR-* Post‑Implementation Review (the unit of learning)
- did the change achieve intent?
- incidents/harms and mitigations
- who was impacted (distributional view)
- what needs rollback/repair
- what future controls/tests must be added

(Pairs with `207-sunset-review-and-rollback-rails.md`.)

---

## D. Governance lanes (normal vs emergency)

### Normal lane (default)
1. draft CHG packet
2. screening + required reviews (privacy, equity, safety, legal)
3. publish pre‑notice where appropriate
4. stage deployment (pilot/canary where possible)
5. publish REL note
6. monitor + respond
7. PIR within fixed window

### Emergency lane (bounded)
Used only when *not changing* would likely cause greater harm. Requirements:

- explicit emergency justification and expiry
- **narrowest viable change**
- accelerated review + after‑action PIR
- mandatory sunset/review trigger inserted immediately

(Align with `112-exception-control-and-emergency-powers.md` and `45-emergency-measures-register.md`.)

---

## E. Anti‑capture and integrity gates

A CHG packet must be blocked (or forced into a harder path) when:

- it increases discretion without audits/receipts
- it weakens remedies, notice, or contestability
- it expands surveillance/data sharing without strong necessity/proportionality and firewalls
- it bundles unrelated changes (“Christmas tree” packages)
- it removes publishable metrics or tamper‑evident logs
- it creates vendor lock‑in or opaque third‑party control

See also: `163-integrity-stack-anti-corruption-rails.md`, `179-open-contracting-and-procurement-rails.md`, and `181-influence-lobbying-transparency-and-integrity-rails.md`.

---

## F. How this plugs into the archive’s interfaces

- **Rules:** `RULE-*` pointers and diffs (`39-rulebook-and-instruments-registry.md`).
- **Reasons:** reason codes (`52-reason-codes-registry.md`) and decision receipts.
- **Remedy:** appeal lanes (`36-appeal-lanes-and-redress-registry.md`, `172-administrative-justice-complaints-ombuds-mesh.md`).
- **Services:** service catalog + access journeys (`47-service-catalog-and-access-journeys-register.md`).
- **Algorithms:** model/ADS registry + no‑silent‑swap (`42-automated-decision-systems-and-model-registry.md`, `191-algorithmic-systems-registry-and-audit-rails.md`).
- **Observability:** publishable control loops (`104-governance-control-loops.md`, `183-governance-observability-and-public-audits.md`).

---

## G. Tests (add to the governance test suite)

- **T3.x Change packet completeness:** Every material change has CHG‑ID, delta, authority, rollback class, monitoring plan, remedy readiness, and comms plan.
- **T3.x No silent swap:** the public can determine the current version/rule “as of now” and see what changed.
- **T3.x Rollback realism:** rollback class matches system constraints and includes compensation where needed.
- **T3.x Emergency lane bounded:** emergency changes have expiry + PIR + inserted sunset/review.

