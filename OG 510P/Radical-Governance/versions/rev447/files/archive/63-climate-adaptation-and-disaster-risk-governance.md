# Climate Adaptation & Disaster Risk Governance (Auditable Resilience Planning + Triggers)

**Purpose:** make disaster/climate risk governance accountable so protection and recovery aren’t allocated by discretion or status.

**Person served:** A person in a hazard‑exposed place who needs risk baselines, trigger rules, and recovery decisions that are timely, fair, and contestable.

**From-below:** This turns resilience into trigger‑based plans you can monitor, so adaptation isn’t perpetually postponed until after the next disaster.

**EXP pointer:** counters `EXP-02` (Waiting), `EXP-04` (Error), and `EXP-01` (Opacity) in disaster aid / evacuation / recovery pipelines (see `98-persons-path-and-accessibility-invariants.md`).

**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations: receipting, time bounds, and continuity of records. (See `07` MVF; `80` Phase −1; `98`; `31`; `101-claude-rev142-normative-requirements.md` (NR-13).)

**Assistance & representation:** publish assisted/oral paths (incl. interpretation) and who can act on behalf of someone; name independent advocates where conflict risk is high (see `98`, `36`, `47`, `82`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).
**Join constraints:** cross‑scope joins/IDs/data sharing MUST name an empowered use‑path + corrective action (per `70`), stay purpose‑limited/minimized, and provide a narrow fallback when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-14).)
**Authority:** rights‑affecting orders/aid determinations MUST be issued as `DRR-*` with a binding contestation lane (`AL-*`) and duty-to-respond follow‑through (`36`, `32`, `55`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** protect reporters/complainants (corruption, abuse, unsafe shelter, price gouging) with safe filing + anti‑retaliation monitoring + interim protections (`83`, `77`, `98`); include at least one degraded/offline safe channel (no personal device required) and publish a privacy‑safe chilling indicator (`03` IPM‑4). (See `101-claude-rev142-normative-requirements.md` (NR-08).)
**Mercy / interim protection:** for evacuations/closures/aid interruptions, define an auditable exception/waiver path (`85`) and stay/interim relief triggers when delay/error creates high harm (`82`, `36`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)
**Proof burdens:** publish required evidence + least‑burdensome alternatives; enable “once‑only” retrieval of state‑held facts; adverse outcomes MUST cite `RC-*` + an `AL-*` lane (`47`, `44`, `52`, `36`). When no category fits, accept the filing and route to measurable “edge review” (authorized human adjudication + reasoned receipt) (see `47-...`, `82-...`, `12-...`). (See `101-claude-rev142-normative-requirements.md` (NR-06, NR-10).)

**Problem class:** climate impacts and hazards are **non-stationary**, cross-boundary, and distributional; disaster response fails when prevention, preparedness, and reconstruction are *not governed as a continuous pipeline*.

**Design goal:** make resilience a **joinable, auditable workflow**: risk baselines → thresholds/triggers → prevention & adaptation investments → preparedness/response → recovery → learning.

**This memo is intentionally minimal.** It composes existing interfaces: releases (`REL-*`), rules (`RULE-*`), decision receipts (`DRR-*` + `RC-*`), assets (`AST-*`), services (`SRV-*`), compacts (`CMP-*`), emergency episodes (`EMR-*`), oversight follow‑through (`OFR-*`), and remedy (`AL-*`).

**Anchors:** Sendai DRR targets/priorities ([BIB-UNDRR-SENDAI-2015]); climate impacts/adaptation synthesis ([BIB-IPCC-AR6-WG2-2022]); adaptation planning and climate-risk assessment standards ([BIB-ISO-14090], [BIB-ISO-14091]); practical community resilience planning ([BIB-NIST-CRPG-1190]); mainstream risk screening for projects/policies ([BIB-WB-CDR-SCREENING]).

## Kernel anchors (do not repeat)
- Person-facing invariants: `98-persons-path-and-accessibility-invariants.md` (incl. non‑digital/non‑reading options), service journeys `47-...`, remedy lanes `36-...` / `08-...`.
- Protective legibility + adoption dynamics: `99-protective-legibility-and-adoption-dynamics.md` (transparency ≠ accountability; identify who loses discretion / who gains contestation capacity).
- Publication integrity (no silent edits; “as‑of” access): `53-...` and `31-...` where relevant.
- Emergency exceptions + reconstruction decisions: `23-...` / `24-...` (prevent “disaster” from laundering corruption).
- Compacts across natural systems: `19-...` / `81-...` (shared measurement + dispute lanes).

## Named tensions (design must surface these)
- Rapid protective action vs contestability/due process (especially evacuations, closures, aid eligibility).
- Risk-map transparency vs displacement/property-value shocks and safety/security concerns.
- Central coordination vs local autonomy (who decides retreat vs rebuild).
- Speed of reconstruction vs safety/learning (build-back-better vs political impatience).
- Scarcity triage vs equity (who gets relief first and why).

---

## A) Non-negotiables (always-on)
1) **No “silent hazard maps”:** hazard and vulnerability baselines MUST publish as versioned `REL-*` with method notes + revision logs + “as‑of” access (`51-...`).
2) **Triggers are rules, not vibes:** any threshold that changes enforcement, spending, eligibility, or evacuation posture MUST be written as `RULE-*` and cite the `REL-*` series used (and uncertainty/limits).
3) **Receipts for risk acceptance:** discretionary “risk acceptance” (e.g., letting a facility operate beyond baseline, deferring known mitigations) MUST emit `DRR-*` with time-bounded expiry + cited evidence + remedy lane.
4) **Build-back-better is a constraint:** reconstruction decisions SHOULD default to *no rebuild in known high-risk zones* unless an explicit, reviewable risk-acceptance `DRR` is issued.
5) **Distributional accounting:** resilience plans MUST publish who bears costs/risks and who benefits; displacement risk and equity impacts are first-class.
6) **Compacts are the default for natural systems:** watersheds/airsheds/evacuation corridors/coastal zones → `CMP-*` with shared measurement and a dispute lane.

7) **Resilience orders and relief are person-facing.** Evacuation/closure/shelter eligibility and disaster aid determinations MUST be communicated so an affected person can understand and act (comprehension test + navigation duty), and MUST include at least one non-digital path when connectivity is disrupted. Relief services SHOULD publish service standards (ack/first contact/decision + tail waits) and interim protections where stakes are high, and SHOULD inventory proof burdens + include a residual/no‑category‑fit route for chaotic documentation and displacement cases. (`98-persons-path-and-accessibility-invariants.md`, `82-...`, `61-...`, `47-...`, `08-...`; `101-claude-rev142-normative-requirements.md` (NR-05, NR-06, NR-10).)

---

## B) Minimum Viable Resilience & DRR Governance Spine (MVRDGS)

### B1) Public artifacts (what must be joinable)
- **Risk baseline releases:** canonical `REL-*` releases for:
  - hazard layers/series (flood/heat/fire/storm/seismic where relevant),
  - exposure (population, critical facilities),
  - vulnerability proxies (housing quality, access constraints),
  - and a *clear revision policy* (how models change over time).

- **Trigger rubric (`RULE-*`):** a published table mapping **thresholds** → **actions** (alerts, inspections, closures, evacuation orders, subsidy triggers, price-gouging enforcement posture, etc.).
  - Every trigger row cites: `REL-*` input(s), decision owner (Unit ID), and the `AL-*` contestation lane.

- **Resilience plan releases (`REL-*`):** the plan itself is a versioned release with:
  - prioritized risk scenarios,
  - asset/service dependencies (link to `AST-*` and `SRV-*` for `ESS-1` services),
  - mitigation/adaptation portfolio (projects, codes, land-use actions),
  - and a monitoring cadence.

- **Investment + retrofit pipeline:** resilience-related capex and maintenance commitments are discoverable via budget/execution `REL-*` and joinable to `AST-*` and `PROG-*` entries (so promises can be audited). For major works, use stage-gated capex governance (see `97-public-investment-and-capital-project-governance.md`).

- **Preparedness + response playbooks:** operational playbooks may be partially sensitive, but existence metadata MUST be public: owning Unit ID, scope, revision date, and activation authority. Playbooks SHOULD specify non-digital publication channels (radio/bulletin/physical notices) for critical orders when connectivity fails. If activation changes rights, it MUST link to `RULE-*` + be logged as `DRR`/`EMR` where exceptional.

- **Recovery & reconstruction ledger:** large recovery programs (housing, schools, lifelines) SHOULD be logged as `PROG-*` with a linked `EVAL-*` window and published “build-back-better” criteria.

- **Relief service standards:** disaster assistance, shelter placement, and compensation programs that gate access to housing/health MUST be modeled as `SRV-*` entries with published service standards / minimum guarantees where essential, and denials as `DRR-*` receipts with usable remedy lanes. (`82-...`, `47-...`, `98-persons-path-and-accessibility-invariants.md`, `08-...`)

### B2) Decision typing (legitimacy routing)
- **High-distributional, long-horizon choices** (managed retreat, major corridor relocations, cross-neighborhood flood defenses): route through deliberation (`DEC-2`) with a duty-to-respond (`ENG-*`), and publish the scenario evidence pack as `REL-*`.
- **Technical baselines** (model updates, hazard map revisions): publish as `REL-*` with method notes; if the change materially alters eligibility/enforcement posture, issue a `DRR` that cites the rule impacts and the appeal lane.
- **Operational activations** (alerts, evacuations, closures): log as `DRR-*` (and as `EMR-*` episodes if emergency authority is invoked); link to the trigger rubric and the baselines used.

### B3) Typical failure modes → countermeasures
- **“Model laundering”** (changing baselines to justify politically convenient outcomes) → publish diffs + independent review; require a `DRR` when rule consequences change.
- **Preparedness theater** (plans without exercises, inventories, or funding) → require drills with after-action artifacts and follow-through in OFRR (`OFR-*`).
- **Risk dumping** (exporting flood/heat/fire risks to poorer districts or downstream neighbors) → distributional accounting + compact obligations + enforceable dispute lanes.
- **Rebuild entrenchment** (repeatedly rebuilding in hazard zones) → default no‑rebuild policy with explicit exception receipts and sunset re-evaluations.

---

## C) Scope patterns (micro-local → global)
Use the **scope assignment test** (`54-...`) when baselines, corridors, or financing spill over boundaries.

- **Micro-local:** preparedness groups, neighborhood cooling networks, community monitoring, mutual aid readiness (see `24-...`).
- **Municipal:** land-use and building-code enforcement; infrastructure maintenance; `ESS-1` service continuity (see `62-...`, `48-...`, `47-...`).
- **Regional / watershed / bioregion:** shared hazard baselines, evacuation corridors, and joint investment planning via `CMP-*` (see `19-...`, `11-...`).
- **National:** national risk baselines; funding + insurance backstops; regulator oversight; mandatory screening for major public investment.
- **Supranational:** harmonize standards and support cross-border baselines; coordinate mutual aid and shared funds; enforce anti-leakage where relevant.
- **Global:** climate adaptation targets and reporting frameworks (Paris/GGA), plus disaster-risk governance norms and financing; measurement comparability is a global public good.

Anchor: UNFCCC global goal on adaptation / UAE Framework context ([BIB-UNFCCC-GGA]).

---

## D) Reason code starter set (`RC-DRR-*`)
Use these in `DRR-*` for resilience, adaptation, and disaster-risk decisions so outcomes are comparable.

- `RC-DRR-001` **Trigger threshold met** — action taken under a published trigger rubric (must cite `RULE-*` row + `REL-*` inputs).
- `RC-DRR-002` **Trigger threshold not met** — request to activate an action denied because published thresholds were not met (cite the same).
- `RC-DRR-003` **Risk acceptance approved (time-bounded)** — deviation from baseline approved with compensating controls and expiry/review date.
- `RC-DRR-004` **Risk reduction investment prioritized** — project prioritized under a published risk-reduction rubric (publish scoring summary via `REL-*`).
- `RC-DRR-005` **No‑rebuild / retreat decision** — relocation or no‑rebuild policy applied under a published rubric with remedy lane.

---

## E) Where this plugs in
- Ecological commons + compacts: `11-commons-and-ecological-governance.md`, `19-compacts-and-cooperative-governance.md`
- Emergency powers + EMR: `23-emergency-governance-and-exceptions.md`, `45-emergency-measures-register.md`
- Assets and lifelines: `48-asset-and-infrastructure-register.md`, `59-critical-infrastructure-and-cyber-resilience-governance.md`
- Services and continuity floors: `47-service-catalog-and-access-journeys-register.md`
- Land-use and housing as risk levers: `62-land-and-housing-governance.md`
- Releases and method disputes: `51-release-registry.md`, `26-epistemic-infrastructure-and-public-knowledge.md`
- Oversight follow-through: `55-oversight-findings-and-response-register.md`
