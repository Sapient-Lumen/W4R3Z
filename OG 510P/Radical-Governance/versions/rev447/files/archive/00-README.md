# Radical Governance Archive (Working Draft)

**Purpose:** orient readers to the archive’s theory of change, navigation, and non‑negotiable person-facing floors (so the rest stays from‑below).

**Person served:** Any person subjected to a government decision who needs power to be visible, reasoned, and correctable without insider status.

**From-below:** This guide helps you navigate and contest the archive so it stays accountable to people affected by governance—not just to its authors.

**Last updated:** **rev447** — 2026.03.06

- **rev447:** converted two persistent overlap hotspots into explicit bridge stacks instead of risky flattening — added `283-justice-and-redress-stack-routing-guide.md` and `284-deliberation-stack-binding-and-legitimacy-guide.md`, marked the relevant memos with stack-relation notes, and refreshed the navigation surface so readers can tell front doors from rails from infrastructure.
- **rev446:** repaired active stale internal references introduced by earlier merges/canonicalizations, added `282-reference-integrity-and-canonical-link-remediation.md` to distinguish live paths from intentional legacy labels, and substantially upgraded `176-ideal-governance-by-scope-synthesis.md` with a stronger scope-assignment framework grounded in multi-level governance, metropolitan coordination, disaster-risk governance, and DPI/state-capacity research.
- **rev445:** tightened the semantic merge into a more stable canonical structure — narrowed `278` so it no longer duplicates `276`, added `280` as the archive-wide systems index / memo-attachment guide, added `281` as a ranked semantic-dedupe backlog, and refreshed the navigation surface so future merges have clearer homes.
- **rev444:** added `279-governance-systems-map.md` to give the archive a canonical ten-system conceptual spine and attached the worked-example subsystem to the Institutional Learning System.
- **rev441:** performed a deeper semantic merge pass — added `273` canonical overlap map + `274` worked-example/domain crosswalk; clarified sibling roles for near-duplicate clusters (whistleblowing, DPI, emergency powers, constitutional change, deliberation, public health, public integrity) and tightened example-first navigation.
- **rev439:** merged the rev380 worked-example layer into the rev438 line as appended memos `235..270`, restored example-first navigation, and added `271` as a legacy-number crosswalk so older citations to `143..178` still resolve.
- **rev438:** added **public health preparedness & response rails** (`234`) — threat register, triggers, evidence packets, bounded emergency powers, scarcity allocation, cross-jurisdiction compacts, and communications-correction discipline.
- **rev437:** added **Policing & use-of-force governance rails** (`233`) — public ranked force policy, force-event receipts + dashboards, independent serious-harm investigation lane, and early-warning discipline/decertification.
- **rev436:** added **Corrections & incarceration governance** (`232`) — places-of-detention registry, inspection + deaths-in-custody oversight, segregation bounds, complaint lanes, and reentry continuity.
- **rev435:** added **Supreme Audit Institutions + Public Accounts rails** (`231`) — SAI independence, unrestricted access, publish-by-default audits, and closed-loop remediation via PAC hearings.
- **rev434:** added **cross-border conflict-of-laws rails** (`230`) — Jurisdiction Packet + cross-border SRE routing, bounded recognition/refusal reasons, and seam continuity duties.
- **rev432:** added **public integrity system architecture** (`226`) + **prosecutorial/disciplinary integrity rails** (`227`) — System–Culture–Accountability stack, enforcement observability, anti-interference tripwires.

## What this is really about

This is a design specification for **lived contestability**: power over people must be visible, reasoned, and correctable in ways ordinary people can actually use.

Governance, at its core, is what we do about the fact that we must live together and will not always agree; this archive’s bet is that contestable power is the least‑bad alternative to domination, abandonment, or violence. (See `01-principles.md` “Living together constraint”.)

Seen whole, this archive is three things at once: a **technical specification** (interfaces and join‑keys), a **moral argument** (what power owes), and an **act of care** (precision designed for the worst day a person has with authority). (See `01-principles.md` and `96-archive-governance.md` “Language note”.)

It is an attempt to write down—precisely, and with adversarial assumptions—what it would mean for people to govern themselves without forcing the harmed to beg for legibility.

The archive’s moral argument lives in the precision: specs are ethics in executable form, designed for the worst day a person has with power. (See `96-archive-governance.md` “Language note”; and `101-claude-rev142-normative-requirements.md` (NR-01, NR-18).)

**Merge note:** where the archive now contains near-duplicate-looking memos, use `273-semantic-merge-resolution-and-canonical-paths.md` to find the canonical starting point before pruning anything, and use `274-worked-example-to-domain-crosswalk.md` to jump from case traces back into the thematic memos.

**Citations:** evidence anchors use `[BIB-*]` keys (`90-bibliography.md`). Claude rev142 normative constraints are summarized in `101-claude-rev142-normative-requirements.md`; new writing SHOULD cite `101` (or its canonical internal anchors) rather than vendored feedback files.

**Language note:** the archive uses RFC‑style normative terms (MUST/SHOULD/MAY) to make obligations testable across institutions. This is **not** a claim of neutrality or institutional civility: the MUSTs are claims about what power owes the governed. When in doubt, prefer plain speech in each memo’s **Purpose** line and tie mechanisms to concrete harms prevented (see `02-design-toolkit.md` “Normative language (spec semantics)” and `95-template-design-memo.md`).

## Where to start

If you want something humane and implementable:
- **Micro‑local** governance where the person’s path is shortest: `10-micro-local.md`
- **Person’s path** invariants (make the interfaces real): `98-persons-path-and-accessibility-invariants.md`
- For high‑risk power, use an **assurance case** spine: `73-assurance-case-and-governance-safety-case.md`
- **If you learn best from examples:** start with `235-worked-examples-and-trace-walkthroughs.md`, use `237-worked-example-quick-reference-and-training-drills.md` for fast routing, then use `244-worked-example-atlas-and-retrieval-index.md`, the identity-continuity layer (`264..266`) when the problem is really “same person, wrong record,” or the place-continuity layer (`267..270`) when the right person exists but the wrong place is doing the damage.
- **Don’t try to implement the whole archive at once.** Start with a receipt at the point of highest harm (coercive contact, benefit cutoff, detention, eviction) that states what happened, why, and the next step; then iterate outward. (See `80-implementation-roadmap.md` Phase −1/0 and `98-persons-path-and-accessibility-invariants.md`.)
- **If you can only ship one thing:** a portable Decision Receipt (`DRR-*`) plus a reachable remedy lane (`AL-*`) with a deadline and interim protection where needed. (`31-...`, `36-...`, `82-...`)

## Preconditions and limits

**Protective legibility (don’t pretend transparency is enough):** legibility protects the governed when it comes with:
- **independent enforcement capacity** (courts/auditors/ombuds with teeth),
- **organized countervailing power** (unions, civil society, independent media) that can use the evidence,
- **low‑cost, low‑risk remedy** that compels relief (`08-...`, `36-...`, `98-persons-path-and-accessibility-invariants.md`), and
- **credible exit options** where feasible (mobility, alternative providers, jurisdictional competition).
See `99-protective-legibility-and-adoption-dynamics.md` and `32-oversight-institutions-and-follow-through.md`.

**Material floor (direction‑of‑travel):** these structures require basics: **revenue**, **staff capacity**, **safety**, and **time/literacy** on the person’s side. Where those are absent, start with Phase −1 “receipt‑first” bootstraps and treat capacity building as governance, not an optional add‑on (`80-implementation-roadmap.md`, `09-public-service-and-state-capacity.md`, `98-persons-path-and-accessibility-invariants.md`).

## Core architectural move

This archive treats governance as an **information system with defined interfaces**: authority must emit **joinable public artifacts** (receipts + registers) so power is legible and contestable across scopes.

- **Decisions emit receipts:** rights- or resource‑affecting acts produce a `DRR-*` that cites `RULE-*` (as‑of), portable reason codes (`RC-*`), any material releases (`REL-*`), and the remedy lane(s) (`AL-*`).
- **Money emits traces:** budgets, contracts, transfers, and execution publish joinable releases (`REL-*`) so “who paid whom for what” is auditable.
- **Absence is a signal:** missing required artifacts are governance incidents (auditable and appealable), not “nothing happened.”
- **Subsidiarity becomes auditable:** scope/mandate assignments are logged as `DRR-TYPE: SCOPE` with explicit scope tests (`IOP-10`).

## What this archive adds

- **Integration + operational specificity:** joins sectoral standards (rights, fiscal, digital, coercion) into one interoperable stack and specifies what artifacts must be emitted (**protocols**, not just high‑level guidance).
- **Adversarial design + scale‑free composability:** assumes strategic abuse and keeps primitives reusable from micro‑local to global.
- **Joinable artifacts as the unit of accountability:** receipts + registers that can be audited across agencies and over time (including “absence as a signal”).
- **Person‑side invariants:** accessibility, navigation duty, delay‑as‑harm, collective redress, and representation duty (`98-persons-path-and-accessibility-invariants.md`).
- **Protective legibility & adoption dynamics:** when transparency helps vs harms, and what to ship first under constraint (`99-protective-legibility-and-adoption-dynamics.md`, `80-...`).
- **Bibliography as evidence docket (contextualizable):** `[BIB-*]` keys act like a joinable evidence docket—readers can trace recommendations to primary anchors and adapt across contexts (`90-bibliography.md`, `91-bibliography-extended.md`).
## Theory of change (and limits)

Legibility reduces information asymmetry and lowers the cost of contestation, raising the expected cost of capture/abuse. It is **necessary but not sufficient**.

Treat the archive’s person‑path descriptions as **testable hypotheses**, not as knowledge: they should be field‑tested against lived experience and corrected by people who know what these situations feel like. (See `03-metrics-and-evidence.md` (field validation) and `98-persons-path-and-accessibility-invariants.md`; also `101-claude-rev142-normative-requirements.md` (NR-04).)

**Minimum conditions (when legibility becomes accountability):**
- **Artifact discipline + enforceability:** missing receipts/registers trigger incidents and someone has authority to compel production/correction (`31`, `36`, `32`).
- **Independent enforcement capacity:** oversight and adjudication can bind, not just recommend (`32`, `36`).
- **Material floor:** clerks, translation/navigation, safety, and subsistence/time exist to use the interfaces (`07`, `09`, `98`).
- **Accessible remedy:** low-cost, low-risk channels exist *at the moment of harm* (`08`, `36`, `98`).

## Navigation (keep it small)

If you’re here for **“ideal government by scope”**, start with `14-scope-ladder.md` and then read the scope memos (`10/20/30/40/50/60`) plus the in‑between patterns (`15/16/17/19`) (and `92` when boundaries change).

**Start here (core kernel):**
- `01-principles.md` (values + guardrails)
- `02-design-toolkit.md` (reusable primitives)
- `14-scope-ladder.md` (ideal government by scale)
- `54-subsidiarity-and-scope-assignment-test.md` (auditable scope tests)
- `70-interoperability.md` (join‑keys + interface contracts)
- `71-interface-obligations-by-scope.md` (what each scope MUST emit)
- `75-archive-map-and-entry-points.md` (single compact map + entry points)

**Archive maintenance (how to keep it coherent):**
- `96-archive-governance.md` (density rules + refactor discipline)
- `126-llm-archive-operator-protocol.md` (LLM editing discipline + amnesia resistors)
- `271-worked-example-legacy-number-crosswalk.md` (resolve rev380 worked-example citations after the renumbered merge)
- `272-merge-integrity-audit-rev380-rev438.md` (what was checked in the merge; why the graft is structurally safe)

**Operations primitives (when building real systems):**
- `31-records-foi-and-government-memory.md` (receipts + memory)
- `125-identity-membership-and-civil-status.md` (status as power: CSR receipts + evidence ladders + continuity for essentials)
- `127-data-governance-and-privacy-interfaces.md` (DATA/PDR/ALR/SHR/COR: purpose limitation, access/sharing logs, correction lane)
- `128-interoperability-interfaces-and-standards.md` (IR/IIC/ICR/COMP: interface registry, change receipts, conformance policy; seam continuity)
- `132-mandates-and-jurisdiction-scope-integrity.md` (Mandate Cards + delegation/scope-change receipts; overlap/gap register)
- `129-public-sphere-and-epistemic-infrastructure.md` (PSIL/AR/ECR: incident ledger, amplification transparency, correction propagation)
- `36-appeal-lanes-and-redress-registry.md` (contestability)
- `82-service-standards-and-minimum-service-guarantees.md` (timeliness + dignity)
- `108-service-standards-and-time-budgets.md` (deadline triggers + time budgets + backlog integrity)
- `140-queues-and-prioritization-integrity.md` (QPI: Queue Cards + position/priority receipts; bounded overrides; seam-safe transfers; clocked remedies)
- `141-delegation-and-representation-integrity.md` (DLR/DVR/DRR + RMR: bounded delegation, revocation clocks, conflict joins)
- `142-metrics-and-indicators-integrity.md` (MIC/MCR/MUR: purpose-bounded metrics, change control, and joinable metric use receipts)

- `137-critical-infrastructure-and-utilities-integrity.md` (USC/OER/PRR + restoration clocks; outage accountability)
- `139-risk-and-safety-assurance-governance.md` (SCC/SACR/RRE/IRR: safety cases that renew; incident loop; no silent operation outside envelope)
- `146-ai-assurance-and-public-sector-ai-ops.md` (AIS/AICC/AICR/AIIR: AI as governance infrastructure; no silent model swaps; incident learning; procurement boundary clauses)
- `138-public-investment-and-capital-projects-integrity.md` (PC/SGR/CCR-PI/BRR: stage gates + change-control + benefits realization; anti-capture megaproject discipline)
- `135-taxation-and-revenue-integrity.md` (TRR/TAR/TPR/TRF: revenue rule registry + replayable receipts; clocks + complexity budgets)
- `136-land-housing-and-commons-integrity.md` (PCR/CCR + LDR/HAR/DRP: land-use/housing receipts; displacement continuity; complexity budgets)
- `134-legibility-and-complexity-budgets.md` (publish CB/PPB budgets; trigger circuit breakers when exceeded)
- `133-evaluation-and-learning-integrity.md` (EPR/EFR/PIRR/DUR + Learning Register: make reforms reversible and provable)
- `113-appointments-and-tenure-integrity.md` (personnel power: acting-role limits + contestable appointments/removals)
- `120-conflicts-of-interest-and-influence-integrity.md` (ICIP: disclosures + recusals + influence footprint + revolving-door controls)
- `130-audit-and-inspection-integrity.md` (APR/AFR/MRR/FTL: oversight receipts + clocks + follow-through)
- `131-compliance-and-sanctions-integrity.md` (CSIP: sanction ladder + CFR case receipts + proportionality/review checks)
- `123-association-and-collective-power.md` (protected association lane + collective filings + clocked negotiation responses)
- `118-rulemaking-and-change-control.md` (rule changes as versioned power: diffs + effective dates + contest windows + rollback)
- `124-constitutional-amendment-and-entrenchment.md` (foundational change control: APP/CCR gates + anti-bundle + review + replay)
- `122-intergenerational-and-future-protection.md` (FIS/SRR: long-term impact trace + automatic review + intergenerational standing)
- `119-selection-and-sortition-integrity.md` (verifiable randomness + draw receipts for panels, audits, lotteries)- **rev429:** added war powers receipts + governance drills rails (`222`, `223`).
