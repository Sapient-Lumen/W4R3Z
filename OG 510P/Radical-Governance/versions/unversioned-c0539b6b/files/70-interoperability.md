# Interoperability (How Scopes Plug Together)

Governance fails at boundaries. This memo defines a small set of *interfaces* so polycentric systems can behave like one system when needed.

## 0) The competence ledger (public jurisdiction map)
Every level maintains a public “competence ledger”:
- what it can decide,
- what it must coordinate,
- what it cannot do,
- who can overrule it and under what conditions.

## 1) Escalation ladder (subsidiarity protocol)
A standard escalation template:
1. local attempt + documented rationale  
2. municipal coordination attempt  
3. regional compact / arbitration  
4. national review (rights, externalities, funding)  
5. supranational/global only when scale/effects demand it  

Higher levels MUST publish:
- scale/effects or rights justification,
- proportionality argument,
- sunset/review plan.

Subsidiarity/proportionality anchor: TEU Article 5 — https://eur-lex.europa.eu/LexUriServ/LexUriServ.do?uri=CELEX:12008M005:EN:HTML

## 2) Money interface (mandates ↔ revenue ↔ transfers)
- publish a cross-scope balance sheet: mandates, revenues, transfers, liabilities
- transfers SHOULD be formula-based and predictable (`CAP-5`; see `07-fiscal-and-budgetary-governance.md`)
- transfer design anchor: World Bank *Intergovernmental Fiscal Transfers: Principles and Practice* https://openknowledge.worldbank.org/entities/publication/141ce28b-a090-5310-9f25-88fe04bde211
- crisis funding SHOULD be trigger-based (disaster, unemployment, outbreak)
- off-book entities MUST be consolidated or disclosed (`CAP-2/3` discipline)


## 3) Ecological commons interface (OPEN-6)
Across boundaries (watersheds/airsheds/migration of harms), require:
- an explicit **ecological budget** object (metric, ceiling/floor, baseline, allocation rule, revision rule)
- shared registries (permits/emissions/discharges/protected areas) with stable IDs where feasible
- joint monitoring + shared enforcement clauses inside compacts (avoid “paper cooperation”)
- leakage controls (comparable measurement; no mutual recognition without auditability)
- dispute clause + emergency coordination protocol for acute ecological events (fires, floods, contamination)

Anchor set: SEEA accounts https://unstats.un.org/unsd/envaccounting/seearev/seea_cf_final_en.pdf ;
UNECE Water Convention https://unece.org/DAM/env/water/pdf/watercon.pdf ;
Paris Agreement https://unfccc.int/sites/default/files/english_paris_agreement.pdf ;
CBD GBF https://www.cbd.int/doc/decisions/cop-15/cop-15-dec-04-en.pdf .
See also: `11-commons-and-ecological-governance.md`.

## 4) Data interface (schemas + privacy + audit logs)
- common schemas for budgets, procurement, and service performance
- privacy-by-design: minimization, role-based access, audit logs
- procurement schema anchor: Open Contracting Data Standard — https://standard.open-contracting.org/

## 5) Identity & recognition interface (IOP-6)
- define the **minimum identity objects** used across scopes: person ID (where lawful), household/entity IDs, and document IDs
- publish rules for **status decisions** (citizenship/residency/eligibility) and their appeal paths (`LAW-5`)
- portability SHOULD include: benefits eligibility proofs, education/professional credentials, and civil-status extracts
- cross-border document authentication SHOULD prefer standard mechanisms (e.g., Apostille) over bespoke legalization
- digital credentials (if used) SHOULD be standards-based and auditable; avoid vendor-locked wallets
See: `12-identity-and-recognition.md`.


## 6) Coercion interface (force, detention, investigation)
- define who can detain/use force at each scope, under what standards (`SAFE-*`)
- mutual aid requires: standardized reporting, independent investigations for serious incidents, and audit trails (`SAFE-2/5`)
- cross-border cooperation MUST include rights baselines and remedy paths (`LAW-5`, `LAW-2/3`; see `08-remedy-and-grievance.md`)

## 7) Mutual recognition interface (portability with minimum standards)
- default: recognize other jurisdictions’ licenses/credentials/judgments
- exceptions: minimum rights/safety/integrity standards not met (documented)
- build portability for benefits and educational/professional records
- **regulated markets/utilities:** recognition SHOULD require baseline rulemaking transparency + appeal rights (`CAP-7`, `LAW-5`) to avoid “race to the bottom” (see `13-regulation-utilities-and-soes.md`)
- regulators SHOULD use compacts for cooperation (shared standards, joint investigations, confidentiality rules, and dispute channels) (`IOP-1`)
## 8) Compact interface (IOP-1)
Compacts MUST include:
- scope and competence boundaries
- funding and contribution formulas
- metrics + reporting cadence
- dispute process + appeal path
- exit clause + transition plan

## 9) Intergovernmental dispute resolution
- standing arbitration / administrative court system for compact disputes, funding disputes, and competence conflicts
- clear escalation to constitutional courts at national/supranational levels (`LAW-2/3`)

## 10) Digital infrastructure interface (IOP-4)
Where shared digital systems exist (identity, registries, benefits):
- publish governance rules and auditability requirements
- avoid vendor lock-in via open standards and exit clauses
- treat core systems as public infrastructure, not merely IT

## 11) Automated decision interface (IOP-5)
When decisions cross boundaries (benefits portability, sanctions lists, eligibility determinations):
- require a shared **system register** field set (purpose, legal basis, versioning, appeal path)
- require portable **reason codes** and an explicit human-review escalation ladder
- prohibit “black box” mutual recognition in high-stakes contexts without auditability


## 12) Remedy interface (portable appeals)
When a decision touches multiple scopes (benefits portability, policing cooperation, mutual recognition, global listings):
- MUST: publish which body can **stop** the harm, which can **review**, and which can **enforce**
- MUST: a clear escalation ladder with deadlines and evidence-preservation rules
- SHOULD: shared reason-code taxonomy so appeals can travel across systems (`IOP-5`)
