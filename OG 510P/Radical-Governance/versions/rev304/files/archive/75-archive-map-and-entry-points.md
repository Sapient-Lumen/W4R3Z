# Archive Map & Entry Points (Keep Navigation Small)

**Purpose:** keep the archive **navigable from below** (person/community first) while it grows without turning into an unreadable scroll.

**Person served:** A person (or practitioner) trying to find the right entry point fast—often under stress—without reading the whole archive.

**From-below:** This helps you find the right document fast so you can use the archive without insider knowledge or endless searching.

This memo is the **single compact map** of the archive. It exists so the archive can grow without turning into a scroll.

**Rule:** any new memo that stays in the archive MUST add (or update) a one-line entry here. (See `96-archive-governance.md`.)

---

## Kernel anchors (do not repeat)
- Person-facing invariants / entry path: `98-persons-path-and-accessibility-invariants.md`.
- Complexity budget / keep the archive small: `96-archive-governance.md`.
- Interop + scope obligations (what must exist to make the map real): `70-interoperability.md`, `71-interface-obligations-by-scope.md`.
- Claude rev142 normative requirements (integration anchor): `101-claude-rev142-normative-requirements.md`.
  (Raw feedback remains temporarily vendored under `../sources/claude-feedback/rev142/` during integration; archive memos should cite `101-claude-rev142-normative-requirements.md` (NR-xx) instead.)
- Protective legibility + adoption dynamics (why this map can become real, not aspirational): `99-protective-legibility-and-adoption-dynamics.md`.

## Named tensions (design must surface these)
- Completeness vs cognitive manageability (navigation as a complexity budget).
- Designer view vs governed-person view (start from the counter, not the org chart).
- Entry-point simplicity vs domain specificity (avoid duplicating whole memos here).

## A. Start here by task

**Start small:** do not try to implement the whole stack at once; begin with Decision Receipts (`DRR-*`) at the point of highest harm plus a reachable remedy lane, then expand. (See `101-claude-rev142-normative-requirements.md` (NR-03, NR-20).)

**If you are a person affected by a government decision**
1) Start with `98-persons-path-and-accessibility-invariants.md` (what must be true from the person’s side).
2) You should have received a Decision Receipt (`DRR-*`). If you didn’t, that itself is contestable. (`31-...`, `08-...`)
3) The receipt should tell you **why** in terms you can evaluate. (`52-...` + the comprehension test in `31-...`)
4) The receipt should tell you **what you can do next** (lane, deadlines, cost/help, and whether it can bind). (`36-...`, `31-...`, `08-...`)
5) If the harm is systemic, use pattern remediation / collective filing; if you can’t navigate, you’re owed a staffed/non‑digital advocate path. (`76-...`, `98-...`, `36-...`, `64-...`, `68-...`)
(See `101-claude-rev142-normative-requirements.md` (NR-01, NR-04).)

**If you are designing a new unit / authority**
1) `14-scope-ladder.md` (what belongs at this scope)
2) `54-subsidiarity-and-scope-assignment-test.md` (auditable scope assignment)
3) `34-competence-ledger-and-mandate-registry.md` (Unit IDs and mandates)
   - If the proposal includes splits/mergers/metro formation: `92-boundary-change-checklist.md` (one-page boundary-change gates)
4) `71-interface-obligations-by-scope.md` + `70-interoperability.md` (what must be published / join-keys)
   - If authority will be exercised by delegated roles/vendors/automation: `78-delegation-and-acting-authority-discipline.md`
   - If capture/influence risk is material: `79-conflict-of-interest-and-revolving-door-discipline.md` (COI + revolving door discipline)
   - If safe reporting / retaliation risk is material: `83-whistleblowing-and-protected-disclosures.md` (protected disclosures + anti-retaliation discipline)
   - If the authority runs major capital projects or infrastructure spend: `97-public-investment-and-capital-project-governance.md` + `48-asset-and-infrastructure-register.md`
   - If the authority administers taxes/fees/billing/refunds: `93-tax-and-revenue-administration.md` + `82-service-standards-and-minimum-service-guarantees.md` + `33-data-protection-and-personal-data-governance.md`
   - If obligations rely on compliance across parties/vendors: `81-verification-inspection-and-compliance-ladders.md` (MVVI spine: schedules, findings receipts, follow‑through)
   - If non-emergency waivers/variances will be used: `85-waivers-variances-and-exceptions-discipline.md` (exceptions receipts + logs)
5) `02-design-toolkit.md` + `95-template-design-memo.md` (compose primitives, write the memo)
6) If high-discretion: `73-assurance-case-and-governance-safety-case.md` + `74-sunsetting-and-deprecation-discipline.md`

**If you are a journalist / advocate / organizer trying to turn public artifacts into change**
1) `31-records-foi-and-government-memory.md` + `39-rulebook-and-instruments-registry.md` (get the receipt + the rule *as-of*)
2) `51-release-registry.md` + `03-metrics-and-evidence.md` (find the releases/metrics that quantify the pattern)
3) If money/power is involved: `38-contracting-and-procurement-register.md` + `46-influence-and-interests-register.md` (who paid whom; who benefited; conflicts)
4) `32-oversight-institutions-and-follow-through.md` + `55-oversight-findings-and-response-register.md` (turn evidence into enforceable follow‑through)
5) For recurring harms: `76-systemic-redress-and-pattern-remediation.md` (pattern cases) + `41-public-participation-and-deliberation-register.md` (duty‑to‑respond pathways)
6) If people are afraid to speak: `83-whistleblowing-and-protected-disclosures.md` (safe reporting + anti‑retaliation)
7) For contested claims and “silent edits”: `53-publication-integrity-and-tamper-evident-logs.md` (provenance + correction discipline)

**If you are implementing under severe constraint / degraded modes**
1) `99-protective-legibility-and-adoption-dynamics.md` (Phase −1 bootstrap + weaponization cautions)
2) `80-implementation-roadmap.md` (MVGS sequencing)
3) `31-records-foi-and-government-memory.md` (paper receipts as the minimum join-key layer)

4) `10-micro-local.md` (shortest person path; visible wins; adapt to local tradition)

**If you are auditing an existing regime**
1) `71-interface-obligations-by-scope.md` (missing artifacts are incidents)
2) `25-legal-legibility-and-rule-inventory.md` + `39-rulebook-and-instruments-registry.md` (rules “as-of”)
3) `31-records-foi-and-government-memory.md` + `36-appeal-lanes-and-redress-registry.md` (receipts + remedy)
   - If “special cases” drive outcomes: `85-waivers-variances-and-exceptions-discipline.md` (waivers/variances as auditable receipts)
   - If the regime relies on pilots/sandboxes: `86-regulatory-experimentation-and-sandboxes.md` (bounded experimentation discipline)
   - If delegation/acting authority is muddy: `78-delegation-and-acting-authority-discipline.md` (authority-chain receipts)
   - If capture/influence is a plausible driver: `79-conflict-of-interest-and-revolving-door-discipline.md` (COI + influence joins)
   - If secrecy/classification is in play: `77-sensitive-information-and-secrecy-governance.md` (withholding receipts + review discipline)
4) `55-oversight-findings-and-response-register.md` (follow-through)
5) If coercive/emergency/ADS/CI: `05/23/06/59` + `73/74`
   - If major capital projects/infrastructure spend are material: `97-public-investment-and-capital-project-governance.md` + `48-asset-and-infrastructure-register.md` + `38-contracting-and-procurement-register.md` + `22-public-integrity-and-procurement.md`

**If you are implementing registers**
- `70-interoperability.md` (schemas + join-keys)
- Registry specs: `34/39/41/42/43/45/51/55` (plus domain-specific registers where needed)

---

## B. Kernel (architecture + discipline)

- `01-principles.md` — values and non-negotiables.
- `02-design-toolkit.md` — reusable primitives (DEC/ACC/LAW/OPEN/SAFE/CAP/IOP).
- `04-threat-models.md` + `72-threat-response-bundles.md` — failure modes → implementable bundles.
- `21-legitimacy-architecture.md` — “legitimacy pipeline” by decision type.
- `88-deliberative-institutions-and-sortition.md` — design invariants for assemblies/juries/mini‑publics (representative deliberation).
- `89-intergenerational-governance-and-future-obligations.md` — future-impact lane, irreversibility test, and minimal long-horizon primitives.
- `70-interoperability.md` — join-key map + minimal schemas.
- `71-interface-obligations-by-scope.md` — must-emit artifacts (MVGS in practice).
- `73-assurance-case-and-governance-safety-case.md` — `AC-*` for high-discretion power.
- `74-sunsetting-and-deprecation-discipline.md` — reversibility as a joinable lifecycle protocol.
- `76-systemic-redress-and-pattern-remediation.md` — systemic-harm correction loops (pattern-of-practice remedies).
- `77-sensitive-information-and-secrecy-governance.md` — secrecy governance: withholding receipts, review/declassification discipline, and oversight access.
- `78-delegation-and-acting-authority-discipline.md` — delegation/acting authority discipline: role-level signatories + time-bounded delegation receipts.
- `79-conflict-of-interest-and-revolving-door-discipline.md` — conflict-of-interest + revolving door discipline: integrity receipts, waivers, and capture-resistant joins.
- `82-service-standards-and-minimum-service-guarantees.md` — service standards + minimum service guarantees (bind service delivery to measurable promises + follow-through).
- `96-archive-governance.md` — how we keep the archive coherent and small.

---

## C. Scope memos (ideal governments by scale)

- `10-micro-local.md` — neighborhood commons; **shortest person’s path** and often the most humane starting point.
- `20-municipal.md` — city/town; core service and rights interfaces.
- `30-regional.md` — region/state/province scale.
- `40-national.md` — constitutional rights backbone + capacity + redistribution.
- `50-supranational.md` — conferral/subsidiarity + dual legitimacy + compliance ladders.
- `60-global.md` — global public goods as compacts + verification + remedy.

**“In-between” patterns (avoid tier explosion)**
- `15-functional-authorities.md` — single-mandate overlays (corridors, basins, grids).
- `16-metropolitan-governance.md` — large-city metro coordination patterns.
- `87-intermediate-local-administration.md` — county/prefecture “administrative bundle” (shared courts/records/health/social services) without creating a mini-state.
- `17-jurisdiction-formation-and-boundaries.md` — forming/splitting jurisdictions.
- `92-boundary-change-checklist.md` — one-page checklist for splits/mergers/metro formation (gates: finance, records, remedy, elections).
- `19-compacts-and-cooperative-governance.md` — compacts as first-class governance.
- `18-intergovernmental-finance.md` — equalization, transfers, conditionality.

---

## D. Registers and joinable artifacts (auditability infrastructure)

- `34-competence-ledger-and-mandate-registry.md` — Unit IDs + mandates.
- `39-rulebook-and-instruments-registry.md` — `RULE-*` “as-of” law + diffs.
- `31-records-foi-and-government-memory.md` — decision records, FOI, retention.
- `36-appeal-lanes-and-redress-registry.md` — `AL-*` lanes; discoverable remedies.
- `51-release-registry.md` — `REL-*` releases (methods, versions, contestation).
- `52-reason-codes-registry.md` — `RC-*` portable reasons.
- `55-oversight-findings-and-response-register.md` — `OFR-*` follow-through receipts.
- `84-internal-controls-and-continuous-assurance.md` — publishable control maps + test results; route material exceptions into `OFR-*`.
- `41-public-participation-and-deliberation-register.md` — participation processes (`ENG-*`) and duty-to-respond links.
- `88-deliberative-institutions-and-sortition.md` — how to commission deliberation so `ENG-*` entries are meaningful.
- `42-automated-decision-systems-and-model-registry.md` — ADS/model registry + reviewability.
- `06-digital-and-algorithmic-governance.md` — safeguards for digital public infrastructure + AI-mediated interfaces (includes foundation-model notes).
- `45-emergency-measures-register.md` — emergency measures with sunsets and after-action plans.
- `43-enforcement-and-custody-event-register.md` — enforcement/custody events joined to authority and remedy.
- `47-service-catalog-and-access-journeys-register.md` — `SRV-*` service catalog + access journeys (make service power legible).
- `53-publication-integrity-and-tamper-evident-logs.md` — anti-silent-edit discipline.

---

## E. Domain playbooks (apply the same interfaces to hard sectors)

- `97-public-investment-and-capital-project-governance.md` — stage-gated public investment discipline (joins capex to `AST/CON/PROG/DRR`).
- `93-tax-and-revenue-administration.md` — revenue administration as a rights‑affecting pipeline (assessment → dispute → collection).
- `94-competition-and-market-power-governance.md` — market power governance (enforcement + competition assessment + bid rigging).

- `57-public-health-and-biosecurity-governance.md` — outbreak response as joinable pipeline.
- `59-critical-infrastructure-and-cyber-resilience-governance.md` — CI cyber posture, incidents, and follow-through.
- `63-climate-adaptation-and-disaster-risk-governance.md` — hazard baselines → triggers → activations → recovery.
- `62-land-and-housing-governance.md` — zoning/permits/allocations as auditable pipeline.
- `64-social-protection-and-benefits-governance.md` — eligibility/delivery/appeals as pipeline.
- `67-migration-and-mobility-governance.md` — status/custody/return controls + remedy.
- `68-education-and-skills-governance.md` — enrollment/placement/discipline/credentials.
- `69-labor-and-work-governance.md` — labor standards, inspection, recovery.

---

## F. Research layer

- `90-bibliography.md` + `91-bibliography-extended.md` — stable `[BIB-*]` keys referenced across memos.
- `100-claude-feedback-integration-tracker.md` — compact checklist mapping Claude rev142 feedback themes to concrete archive locations (keep coherence work systematic).
- `101-claude-rev142-normative-requirements.md` — compact, citable list of Claude rev142 normative constraints (use to keep integration tight).
- `102-revision-log.md` — change history (kept out of the main README to preserve navigability).
