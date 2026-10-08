# Supranational Governance (Unions / Confederations / Cross-Border Regimes)

**Purpose:** make cross‑border authority **auditable and contestable**: a person harmed by a treaty/union regime can trace conferral, rules, and decisions and reach a usable dispute/complaint path.

See `14-scope-ladder.md` for the cross-scope map (what belongs where), `70-interoperability.md` for join-keys, and `71-interface-obligations-by-scope.md` for what each scope MUST publish.


## Kernel anchors (do not repeat)
- **Global + cross-border interfaces:** `60-global.md` (coordination, legitimacy, and capture risks).
- **Compacts/cooperation:** `19-compacts-and-cooperative-governance.md` (joinable obligations; exit/renewal discipline).
- **Competence map:** `34-competence-ledger-and-mandate-registry.md` (who claims authority).
- **Records + remedy:** `31-...`, `08-...` + ALR `36-...` (contestability across borders where feasible).
- **Protective legibility:** `99-protective-legibility-and-adoption-dynamics.md` (transparency can be used as leverage or targeting).
- Person-facing access + representation duty (treaty regimes still need usable contestation paths): `98-persons-path-and-accessibility-invariants.md`.

## Named tensions (design must surface these)
- **Sovereignty vs coordination:** shared problems require joint action without erasing local legitimacy.
- **Technocracy vs consent:** expertise matters; decisions still need reasons + contestability.
- **Uniformity vs pluralism:** allow functional equivalents where they protect the governed.
- **Transparency vs diplomacy/safety:** disclose enough to constrain power; log exceptions when secrecy is necessary.

## Scope card (one-screen)
- **Typical scale / unit types:** confederation / union of states (treaty-based; competence by conferral).
- **Owns (and nothing else):** cross-border coordination where member action fails (market rules, shared standards, joint funds, shared courts/arbitration).
- **Does not own:** general policing/force; unconstrained taxation; domestic constitutional identity absent explicit conferral.
- **MVG (minimum viable government):** conferral ledger + subsidiarity/proportionality discipline; dual legitimacy (citizens + members); independent court/arb; compliance ladder (`81`).
- **Interfaces:** publish competence ledger + mandates (`34`); funding rules; dispute outcomes; waivers/derogations (`85`).
- **Person-facing invariants:** where this scope issues rights/service determinations, require **comprehension-tested receipts/notices**, **no-wrong-door** routing, and **safe remedy** (incl. representation) (`98-persons-path-and-accessibility-invariants.md`, `08-...`, `36-...`).
- **Top failure modes:** democratic deficit, capture by strong members, regulatory overreach, weak enforcement (TM-2, TM-3, TM-8).

## What this level must own (and nothing else)
- rights baselines and guardrails for cross-border coercion (extradition, policing cooperation)
- limited, enumerated competences where cross-border coordination is essential
- mutual recognition + minimum standards for rights, safety, and integrity (use `STD-*` IDs/PSR where technical; see `27-standards-and-technical-governance.md`)
- dispute resolution for treaty/compact compliance
- shared infrastructure and market rules where scale economies dominate

## Minimum Viable Government (MVG)

**Baseline:** treat the regime as a **compact** with explicit conferral/subsidiarity rules, a competence ledger, published rulemaking dockets, and auditable accounts (`IOP-1`; `70-interoperability.md`).

**Supranational-specific minimums**
- treaty of conferral + proportionality publication (mature example: see [BIB-TEU-A5]).
- dual-legitimacy channel (states + people) and a court/arbitration path with enforceable remedies (`DEC-1`, `LAW-2`).
- mutual recognition only with minimum rights/safety/integrity standards and auditability (`IOP-2`, `IOP-7`; see `70-interoperability.md`).
- small shared budget with consolidated public accounts + audit + fiscal risk disclosure (`CAP-2/3`; `ACC-1`).
- complaint/remedy path for cross-border harms (incl. mutual recognition failures) that satisfies the **Person’s Path**: comprehension‑tested notices/receipts, no‑wrong‑door routing (do not require people to understand the regime), and safe filing/representation where risks are high (`LAW-5`; see `08-...`, `36-...`, `98-persons-path-and-accessibility-invariants.md`).
- cross-border mobility regimes (asylum cooperation, visas, readmission/returns where authorized): express gateway criteria as `RULE-*` and require portable `DRR-*` receipts + `AL-*` lanes for status-affecting actions; log custody/return operations as `ENF-*` joined to authorizing `DRR-*`; use `CMP-*` compacts for burden-sharing and information-sharing limits (see `67-migration-and-mobility-governance.md`).
- ADS/automation governance where cross-border decisions rely on systems: register + reason codes + human review (`IOP-5`; see `06-digital-and-algorithmic-governance.md`).
- cross-border data sharing only under an explicit rights baseline (purpose limitation + remedy) with DPR cross-references in relevant decisions/compacts (`LAW-8`, `IOP-1`; see `33-data-protection-and-personal-data-governance.md`).

## Ideal institutional stack (bounded)
### A) Dual legitimacy, not faux-federalism
- **Council of states** (governments) for high-sovereignty questions.
- **Parliament/assembly of people** for market rules, budgets, and oversight.
- Clear “who decides what” ledger (competence ledger) (see `70-interoperability.md`).

### B) Compliance system with graduated responses (menu)
Use the **least coercive** mechanism that reliably changes behavior, and always preserve due process (`LAW-*`).

Common tools (often combined):
- **Reporting + peer review** (learning + pressure; low coercion). Example global model: see [BIB-UN-UPR].
- **Administrative enforcement** (infringement proceedings; fines/penalties where authorized).
- **Conditional finance** (funding tied to measurable obligations; avoid discretionary patronage).
- **Dispute settlement with remedies** (court/arbitration; potentially authorized retaliation). Canonical template: see [BIB-WTO-DSU].
- **Market-access hooks** (mutual recognition or access conditioned on baseline standards; publish exceptions and audits).
- **Transparency scoreboards** (public comparability; “name-and-explain” with evidence packs).

Hard constraint: never rely on punishment without a clear path to compliance, review, and remedy.

### C) Small fiscal capacity with hard rules
- limited shared budget for: cross-border infrastructure, research, crisis response.
- strict audit, open contracting, and public accounts.


## Interfaces (how this plugs into states and localities)

Supranational regimes are “joinable” only if domestic implementation is legible.

- **Conferral is auditable:** competence ledger entries cite the conferring instrument (`RULE-*` / treaty) and publish proportionality/subsidiarity reasoning as `DRR-TYPE: SCOPE` where mandates shift (see `54-...`).
- **Mutual recognition stays contestable:** recognition decisions (and refusals) emit `DRR-*` with `RC-*` reason codes and an `AL-*` lane; publish exceptions/derogations as rules or releases (`RULE-*` / `REL-*`) rather than informal practice.
- **Finance is joinable:** shared funds use `TRF-*` transfers and `REL-*` accounts; conditionality is explicit and appealable (see `35-...`, `18-...`).
- **Compliance is reviewable:** infringement/dispute actions open or cite `OFR-*` entries and publish outcomes; sanctions/listings preserve due process and appealability (`LAW-5`, `36-...`).

## Top failure modes + countermeasures
- **Competence creep:** hard conferral + proportionality publication + sunset clauses (`70-interoperability.md`).
- **Democratic deficit:** strengthen people’s channel (deliberation + oversight) (`DEC-2`, `OPEN-1`).
- **Uneven rule-of-law compliance:** rule-of-law checklists + conditionality (`LAW-4`, `CAP-3`).
- **Member-state backsliding / entrenchment:** publish a common method for rule-of-law and election integrity assessment, trigger graduated responses (funding, peer review, legal action), and preserve individual remedy paths (`TM-14`, `LAW-4`, `DEC-5`).
- **Rights laundering via cross-border data sharing:** require typed sharing agreements/compacts, DPR join-keys, and an enforceable remedy path for affected people (`TM-15`; `LAW-8`; `IOP-1`).

## Success metrics (minimal set)
Use metric IDs from `03-metrics-and-evidence.md` packs where possible; keep ≤10 total.
- cross-border dispute resolution time (median + 90p) [LRR-4] (and docket/backlog where applicable) [LRR-5]
- compliance rates with reporting/verification (local add-on; define per regime)
- market fairness + corruption risk: procurement competitiveness [IPM-2], concentration watch [IPM-3], disclosures/protections [IPM-4]
- legitimacy: participation breadth [LRR-1], trust/fairness [LRR-2], decision transparency coverage [LRR-8]