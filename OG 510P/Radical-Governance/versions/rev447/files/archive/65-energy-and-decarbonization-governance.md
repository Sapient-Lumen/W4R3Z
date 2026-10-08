# Energy & Decarbonization Governance (Auditable Mitigation Pipeline)

**Purpose:** make energy transition decisions auditable and just so decarbonization doesn’t become hidden extraction.

**Person served:** A household paying energy bills and breathing the air near energy infrastructure who needs decarbonization decisions that are fair, reliable, and contestable.

**From-below:** This makes decarbonization commitments measurable and reviewable so plans don’t become endless announcements without delivery.

**EXP pointer:** counters `EXP-02` (Waiting), `EXP-01` (Opacity), and `EXP-04` (Error) in permitting, subsidy, and essential-service shutoff decisions (see `98-persons-path-and-accessibility-invariants.md`).

**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations: receipting, time bounds, and continuity of records. (See `07` MVF; `80` Phase −1; `98`; `31`; `101-claude-rev142-normative-requirements.md` (NR-13).)

**Assistance & representation:** publish assisted/oral paths (incl. interpretation) and who can act on behalf of someone; name independent advocates where conflict risk is high (see `98`, `36`, `47`, `82`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).

**Join constraints:** cross‑scope joins/IDs/data sharing MUST name an empowered use‑path + corrective action (per `70`), stay purpose‑limited/minimized, and provide a narrow fallback when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-14).)
**Authority:** rights‑affecting tariffs/shutoffs/subsidy/permitting outcomes MUST be issued as `DRR-*` with a binding contestation lane (`AL-*`) and oversight follow‑through (`36`, `32`, `55`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** protect complainants/whistleblowers (billing disputes, shutoff threats, capture/corruption) with safe filing + anti‑retaliation monitoring + interim protections (`83`, `77`, `98`); include at least one degraded/offline safe channel (no personal device required) and publish a privacy‑safe chilling indicator (`03` IPM‑4). (See `101-claude-rev142-normative-requirements.md` (NR-08).)
**Mercy / interim protection:** where essential service interruption creates high harm, define hardship/waiver paths and interim protection/stay triggers (e.g., during disputes, missed standards, extreme weather) (`82`, `36`, `85`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)
**Proof burdens:** publish required evidence + least‑burdensome alternatives; once‑only retrieval of state‑held facts; adverse outcomes cite `RC-*` + a contestation lane (`47`, `44`, `52`, `36`). When no category fits, accept the filing and route to measurable “edge review” (authorized human adjudication + reasoned receipt) (see `47-...`, `82-...`, `12-...`). (See `101-claude-rev142-normative-requirements.md` (NR-06, NR-10).)

**Problem class:** decarbonization is infrastructure + industrial policy + distribution at once. Failures cluster around **lock‑in**, **capture**, unreliable or gamed measurement, and affordability backlash.

**Design goal:** treat mitigation as a **joinable pipeline**: emissions & energy baselines → targets/carbon budgets → policy instruments → delivery (permits, markets, subsidies, procurement) → monitoring & verification → correction and learning.

**This memo is intentionally minimal.** It composes existing interfaces: releases (`REL-*`), rules (`RULE-*`), standards (`STD-*`), decision receipts (`DRR-*` + `RC-*`), assets/infrastructure (`AST-*`/`INF-*`), services (`SRV-*`), programs & evaluation (`PROG-*`/`EVAL-*`), procurement & transfers (`CON-*`/`GRT-*`/`TEX-*`), emergency episodes (`EMR-*`), oversight follow‑through (`OFR-*`), remedy (`AL-*`), and compacts (`CMP-*`).

**Anchors:** Paris Agreement obligations/architecture ([BIB-PARIS]); mitigation assessment and pathways ([BIB-IPCC-AR6-WG3-2022]); energy transition pathway benchmark ([BIB-IEA-NETZERO-2023]); inventory accounting standards ([BIB-GHGPROTOCOL-CORP], [BIB-ISO-14064-1-2018]).

## Kernel anchors (do not repeat)
- Person-facing invariants: `98-persons-path-and-accessibility-invariants.md` (incl. non‑digital/non‑reading options), service journeys `47-...`, remedy lanes `36-...` / `08-...`.
- Protective legibility + adoption dynamics: `99-protective-legibility-and-adoption-dynamics.md` (transparency ≠ accountability; identify who loses discretion / who gains contestation capacity).
- Publication integrity (no silent edits; “as‑of” access): `53-...` and `31-...` where relevant.
- Regulation/utility governance + shutoff constraints: `13-...` and person’s path `98-persons-path-and-accessibility-invariants.md`.
- Critical infrastructure security posture: `59-...`.

## Named tensions (design must surface these)
- Reliability vs decarbonization speed (blackouts can kill; delays can also kill).
- Affordability vs investment/cost recovery (ratepayer backlash vs underbuild).
- Transparency vs security (grid data, critical facilities).
- Rapid transition vs just transition (distributional politics of winners/losers).
- Central planning vs market mechanisms (capture risks in both directions).

---

## A) Non-negotiables (guardrails)

1) **No targets without an auditable baseline.** Publish methods + coverage + revisions (`REL-*`) before binding targets.
2) **Lock‑in discipline for long‑lived assets.** Major energy assets must disclose lifecycle emissions assumptions, decommissioning / retrofit options, and stranded‑asset risk in the decision receipt.
3) **Affordability and distribution are first‑class constraints.** Tariff/rebate/subsidy designs publish incidence analysis and protections for vulnerable households.
4) **Reliability is explicit.** Reliability risk acceptance and load‑shedding rules must be logged (time‑bounded) with oversight follow‑through.
5) **Offsets and removals are governed, not vibes.** If used, they require pinned standards (`STD-*`), registries, and disclosure of durability and double‑counting controls.

6) **Essential service, no silent shutoffs.** Disconnections, load shedding, and ratepayer determinations are person-facing decisions; notices MUST meet the comprehension test and include a usable remedy/assistance path. Essential electricity/heating/cooling access SHOULD be modeled as `SRV-*` with service standards and minimum guarantees for vulnerable households; assistance/hardship programs SHOULD minimize and inventory proof burdens and include a residual/no‑category‑fit route (human adjudication + receipted reasons) when documentation fails. (`13-...`, `82-...`, `47-...`, `98-persons-path-and-accessibility-invariants.md`, `08-...`; `101-claude-rev142-normative-requirements.md` (NR-05, NR-06, NR-10).)

## B) Minimal public artifacts (the “must emit” set)

### B1) Inventory & baseline releases (`REL-*`)
- `REL-TYPE: INVENTORY` — national/regional/sector inventories and energy balances.
- MUST include: method, boundary, coverage gaps, uncertainty notes, revision log, and data provenance pointer (where legal).

### B2) Target / budget instruments (`RULE-*` + `STD-*`)
- `RULE-TYPE: TARGET` — targets, carbon budgets, sector caps, performance standards.
- MUST cite: baseline `REL-*`, measurement standard `STD-*`, and review cadence.

### B3) Instrument execution (`DRR-*` receipts)
Major actions emit decision receipts that join across scopes:
- permitting siting/expansion (generation, transmission, pipelines, storage),
- interconnection queues and curtailment policy,
- auctions, feed‑in tariffs, capacity markets, carbon pricing,
- subsidy awards / tax credits / public finance commitments.
- disconnection/arrears relief determinations and billing dispute decisions for essential utility service (where governed).

### B4) Delivery tracking (`REL-*`, `PROG-*`, `EVAL-*`)
- `PROG-*` entries for transition programs (retrofits, fleet turnover, industrial upgrades).
- `REL-TYPE: MRV` releases for progress tracking and compliance (aggregated where necessary).
- `EVAL-*` commitments for major programs and market designs.

### B5) Integrity + remedy (`OFR-*`, `AL-*`)
- Oversight findings and corrective actions are joinable (`OFR-*`).
- Appeal lanes (`AL-*`) must exist for: ratepayers/consumers, landholders, communities affected by siting, and regulated entities (time‑bounded).

For essential service disputes (billing errors, disconnection, outage compensation), the default posture is **interim protection** while a timely review is pending, to prevent irreversible hardship from correctable errors. (`82-...`, `98-persons-path-and-accessibility-invariants.md`, `08-...`)

## C) Trigger rubric (when the pipeline must fire)

An energy/mitigation action MUST produce the artifacts above when it:
- sets or materially changes targets, pricing, or standards,
- authorizes or funds a long‑lived asset with lock‑in risk,
- changes reliability rules (curtailment, load shedding, emergency fuel switching),
- awards material subsidies/tax expenditures, or
- imposes compliance obligations or penalties.

## D) Scope assignment (where each layer fits)

Use the scope test (`54-subsidiarity-and-scope-assignment-test.md`) and log the docket (`DRR-TYPE: SCOPE`):
- **Micro‑local / municipal:** building codes, electrification readiness, local procurement, neighborhood retrofits, local siting hearings.
- **Metropolitan / regional:** grid planning, interconnection queue governance, transit and freight corridors, air basins.
- **National:** economy‑wide targets, pricing frameworks, industrial standards, major finance and equalization.
- **Supranational / global:** cross‑border markets, standards harmonization, accounting alignment, and climate finance (via compacts and treaty regimes).

## E) Common failure modes (and the minimal counter‑moves)

- **Greenwashing / metric gaming:** pin `STD-*`; require “as‑of” queries; publish revision logs (`REL-*`).
- **Capture in permitting/markets:** publish queue rules, auction rules, and conflict‑of‑interest joins; require `DRR-*` receipts for material deviations.
- **Backlash via affordability:** require published incidence analysis and automatic protections; track disconnections/arrears as metrics.
- **Reliability scapegoating:** log emergency episodes (`EMR-*`) and require after‑action corrective plans (`OFR-*`).

**Reason codes:** use `RC-ET-*` for core mitigation decision reasons (see `52-reason-codes-registry.md`).
