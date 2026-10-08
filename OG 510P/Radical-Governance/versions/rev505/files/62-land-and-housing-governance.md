# Land & Housing Governance (Auditable Planning + Permissioning)

**Stack relation:** use `298-land-housing-commons-and-value-capture-routing-guide.md` for the canonical route across the land / housing / commons / value-capture cluster. This memo is the broad housing, planning, and permitting front door; `136` is the parcel / housing / commons integrity layer; `150` is the stewardship / anti-speculation institutional-carrier specialization; `198` is the land-uplift / externalities / value-capture fiscal specialization.

**Purpose:** make land/housing power (title, zoning, eviction, subsidies) traceable and contestable where harms are acute.

**Person served:** A tenant, home‑seeker, or neighborhood resident affected by zoning, permitting, and allocation decisions who needs clear rules, usable reasons, and a real appeal path.

**From-below:** This makes planning and permitting traceable so housing and land decisions can’t be captured or arbitrarily denied in silence.

**EXP pointer:** counters `EXP-02` (Waiting), `EXP-01` (Opacity), and `EXP-05` (Fear) by requiring receipted permits/enforcement and safe contestation in housing/land decisions (see `98-persons-path-and-accessibility-invariants.md`).

**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations: receipting, time bounds, and continuity of records. (See `07` MVF; `80` Phase −1; `98`; `31`; `101-claude-rev142-normative-requirements.md` (NR-13).)

**Assistance & representation:** publish staffed/oral/offline paths (incl. interpretation) and who can act on behalf of someone (advocate/authorized representative); allow third‑party/collective filing where harms are collective or the person can’t safely file; disclose conflict/consent rules (see `98`, `36`, `47`, `41`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).
**Authority:** permitting, code enforcement, and eviction/allocative decisions must issue `DRR-*` and name a binding review lane with time limits and interim protections where displacement risk exists (`29`, `36`, `66`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** tenants/complainants need safe reporting and redaction discipline; monitor chilling in code enforcement and permitting complaints (`83`, `77`, `03`); include at least one degraded/offline safe channel (no personal device required) and publish `03` IPM‑4. (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed, a timely challenge is pending, or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)
**As-of & corrections:** decisions and receipts MUST state the as‑of basis (rules, data, releases) and MUST propagate corrections (reopen/undo downstream holds/penalties when upstream records change); do not strand people in stale status. (See `31-records-foi-and-government-memory.md`, `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-07, NR-15).)
**Proof burdens:** in housing/land determinations (eligibility, allocation, eviction, enforcement), disclose evidentiary standards + allocation; prefer least-burdensome proof and “once-only” retrieval of state-held facts; adverse outcomes cite `RC-*` + `AL-*` (`44`, `47`, `52`, `36`). When no category fits, accept the filing and route to measurable “edge review” (authorized human adjudication + reasoned receipt) (see `47-...`, `82-...`, `12-...`). (See `101-claude-rev142-normative-requirements.md` (NR-06, NR-10).)
**Join constraints:** cross‑scope joins/IDs/data sharing MUST name an empowered use‑path + corrective action (per `70`), stay purpose‑limited/minimized, and provide a narrow fallback when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-14).)


**Problem class:** land is fixed; housing is a high-stakes basic need; land-use decisions are **capture-prone** and create long-lived distributional effects.

**Design goal:** treat land-use and housing policy as an **auditable pipeline** (plans → rules → permits → delivery → impacts) so supply, affordability, displacement, and ecological constraints are *governable objects* rather than opaque bargaining.

**This memo is intentionally minimal.** It composes existing interfaces: PRR (`RULE-*`), decision receipts (`DRR-*`), approvals (`PAR`), participation (`ENG-*`), influence (`INT/INF`), assets (`AST-*`), subsidies (`GRT/TEX`), and remedy (`AL-*`).

**Anchors:** tenure governance norms ([BIB-FAO-VGGT-2012]); diagnostic dimensions ([BIB-WB-LGAF]); reform agenda and comparative housing lessons ([BIB-OECD-HOUSING-REFORM-2024]); land value capture toolbox ([BIB-LINCOLN-LVC-US]).

## Kernel anchors (do not repeat)
- Person-facing invariants: `98-persons-path-and-accessibility-invariants.md` (incl. non‑digital/non‑reading options), service journeys `47-...`, remedy lanes `36-...` / `08-...`.
- Protective legibility + adoption dynamics: `99-protective-legibility-and-adoption-dynamics.md` (transparency ≠ accountability; identify who loses discretion / who gains contestation capacity).
- Publication integrity (no silent edits; “as‑of” access): `53-...` and `31-...` where relevant.
- Participation is not legitimacy by itself: use contestable artifacts + binding hooks (`41-...`, `32-...`).
- Coercion boundary: displacement-by-enforcement and unsafe housing orders join to `05-...` / `43-...`.

## Named tensions (design must surface these)
- Local control vs regional equity/supply (who bears burdens of exclusion).
- Transparency of planning records vs retaliation/privacy (tenants, complainants, small landlords).
- Speed of approvals vs capture/due process (fast lanes can become favoritism).
- Code enforcement vs displacement harm (safety vs homelessness risk).
- Property value politics vs right-to-housing / anti‑displacement obligations.

---

## A) Non-negotiable constraints (always-on)
1) **No “map magic”:** zoning / plan maps MUST be versioned and queryable “as-of” (publish as `REL-*` releases with diffs + changelogs; see `51-...`, `53-...`).
2) **Rule traceability:** binding land-use instruments MUST be inventoried in the PRR with stable IDs and instrument kind (use `PLAN`, `BYLAW`, `REG`, `ORDER`, etc.; see `39-...`).
3) **Receipts for discretion:** variances, rezones, exceptions, and high-impact permits MUST emit `DRR-*` (reasons + cited `RULE-*`/`REL-*` + `AL-*` lane) and be logged in `PAR` (`29-...`).
4) **Capture controls:** material planning decisions MUST join to influence and interests disclosures where relevant (`46-...`) and publish sponsor/meeting logs.
5) **Remedy is real:** affected parties can discover and use an appeal lane (`AL-*`) with time bounds; interim protection rules SHOULD exist where displacement risk is high (`08-...`, `36-...`).
5a) **Person’s path:** notices/receipts for high-harm housing decisions (permit denials affecting habitability, code enforcement leading to displacement, eviction/condemnation orders where applicable) MUST satisfy comprehension + accessibility invariants and include a safe navigation path to remedy and accommodation. Permitting and enforcement journeys SHOULD be expressed as `SRV-*` entries with proof-burden inventories and a residual/no‑category‑fit route when the person’s situation doesn’t match the form. (See `47-...`; `101-claude-rev142-normative-requirements.md` (NR-05, NR-06, NR-10).) Treat displacement-by-enforcement as coercion where relevant (`05-...`, `43-...`, `98-persons-path-and-accessibility-invariants.md`).
6) **Distributional + ecological accounting:** plans and rule changes MUST publish an impact summary (housing units by type/affordability, displacement risk, infrastructure load, ecological limits) and the method used (as `REL-*`).

---

## B) Minimum Viable Land & Housing Governance Spine (MVLHGS)

### B1) Public artifacts (what must be joinable)
- **PRR inventory:** the binding land-use instrument set (plans, zoning/bylaws, overlays, fee schedules, exactions) with **as-of** lookup. (`39-...`)
- **Zoning/plan releases:** the authoritative map/text published as `REL-*` with methods + revision logs + diffs (do not silently overwrite). (`51-...`, `53-...`)
- **Permit/variance log:** approvals and exceptions logged in `PAR` keyed to address/parcel + instrument IDs; decisions emit `DRR-*` and link to `AL-*`. (`29-...`, `31-...`)
- **Housing pipeline dashboard:** regular `REL-*` releases for:
 - permitted units (by type), started, completed,
 - affordability mix (price bands or %AMI where used),
 - backlog/queue stats for approvals (publish **tail** wait shares; delay-as-harm; see `101-claude-rev142-normative-requirements.md` (NR-05)),
 - displacement/eviction risk indicators where lawful.
- **Public land & assets:** public landholdings and housing-related assets in AIR (`AST-*`) with coarse location + status (surplus/held/leased) and disposition rules. (`48-...`)
- **Subsidies & tax expenditures:** all housing-related grants, vouchers, abatements, and inclusionary offsets in `49-...` with joinable recipient IDs (`EID`) and project references.

### B2) Decision typing (legitimacy routing)
- **Major plan/zoning rewrites** (citywide upzoning, corridor plans, greenbelt changes): require a legitimacy pipeline that includes **deliberation** (`DEC-2`) and a duty-to-respond logged as `ENG-*` (see `21-...`, `41-...`).
- **Site-specific rezonings / large variances:** administrative route allowed only if:
 - criteria are in `RULE-*`,
 - decision emits `DRR-*` with reasons and cited impacts,
 - conflicts are disclosed (`INT/INF`),
 - and an `AL-*` lane exists.
- **Routine permits** (by-right): prioritize speed + predictability; publish queue metrics and standard refusal reasons.

### B3) Typical failure modes to design against
- **Variance laundering:** repeated “exceptions” create a shadow zoning regime. Mitigation: publish variance rates by area + rule ID; trigger oversight when thresholds exceeded (`OFR-*`).
- **Displacement externalization:** benefits privatized; costs pushed to renters/low-income households. Mitigation: publish displacement risk + mitigation commitments; time-bounded review triggers.
- **Infrastructure veto / hidden scarcity:** capacity constraints used opaquely to block housing. Mitigation: publish infrastructure load assumptions and backlog estimates as `REL-*` with method notes; link to AIR condition grades.
- **Developer capture:** decision pathways dominated by insider access. Mitigation: meeting logs + revolving-door controls + influence register joins; random audits of approvals.

---

## C) Boundary rules (metro/regional spillovers)
Land and housing decisions generate spillovers (commuting, emissions, water, labor mobility). Use the **scope assignment test** (`54-...`) when:
- housing targets/constraints materially export costs to neighbors,
- infrastructure corridors cross boundaries,
- or exclusionary zoning creates regional inequity.

Prefer **compacts** (shared targets + measurement + enforcement hooks) over new layers (`19-...`, `16-...`, `70-...`). Use `RC-SCOPE-*` when recording the assignment decision.

---

## D) Reason code starter set (`RC-LH-*`)
Use these in `DRR-*` for approvals/denials/conditions to make outcomes comparable and auditable.

- `RC-LH-001` **By-right approval** — meets published criteria; issued under as-of `RULE-*`.
- `RC-LH-002` **Capacity constraint (published)** — denial/condition due to a published infrastructure or ecological limit (must cite `REL-*` method + threshold).
- `RC-LH-003` **Variance/exception criteria unmet** — exception request fails the published test; cite the criteria and missing element.
- `RC-LH-004` **Affordability / inclusionary condition applied** — condition imposed under a cited `RULE-*` (publish calculation method).
- `RC-LH-005` **Displacement mitigation required** — approval conditioned on mitigation/relocation plan under a cited rubric.
- `RC-LH-006` **Conflict-of-interest remediation** — decision paused/invalidated due to conflict disclosure failure (cite `INT-*` rule).

---

## E) Where this plugs in
- Municipal land-use minimums: `20-municipal.md`
- Permissioning / approvals register: `29-permissioning-and-approvals.md`
- Influence / interests joins: `46-influence-and-interests-register.md`
- Assets and public land: `48-asset-and-infrastructure-register.md`
- Subsidies and tax expenditures: `49-grants-subsidies-and-tax-expenditures-register.md`
- Ecological limits + commons: `11-commons-and-ecological-governance.md`
