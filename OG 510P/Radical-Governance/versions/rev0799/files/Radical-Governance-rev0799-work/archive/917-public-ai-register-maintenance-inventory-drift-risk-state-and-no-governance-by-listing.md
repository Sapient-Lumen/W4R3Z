# 917 — Public AI register maintenance, inventory drift, risk state, and no governance by listing

## One-line thesis

A public AI inventory, algorithmic-transparency register, or high-risk-system database is a truth-maintenance waist, not an authorization instrument: listing, absence, stale status, or machine-readable neatness should never by itself prove lawful, safe, deployed, retired, or governed use.

## Why this matters

Public AI registers are becoming the default visible surface for administrative AI. That is useful, but risky. A register can be current, machine-readable, and still incomplete; it can list a use case that is only planned; it can omit sensitive or exempt uses; it can lag after a system is paused or decommissioned; it can hide the difference between a commercial off-the-shelf license count and a deployed agency workflow; it can describe a model family but not the operative version; and it can state risk category without exposing the impact assessment, monitoring, incident, or redress evidence that would make the category contestable.

The failure is not that public registers are theater. They are necessary. The failure is **register sovereignty**: treating an inventory row as if it were deployment authority, due-process notice, risk acceptance, procurement proof, public explanation, monitoring evidence, or redress. The archive needs a case form that keeps the register useful while refusing to let it replace the stronger records that public power requires.

## Pattern pack

### 1. Split the register state before reading the row

Every AI inventory row should be read as a state label, not as a conclusion. At minimum, split:

| State | Question |
| --- | --- |
| candidate / exploration | Is the agency only testing possible use, researching, or procuring access? |
| in development | Is the tool being built, configured, evaluated, or integrated without public-facing or official decision use? |
| pilot | Is it live for a bounded group, geography, program, or staff role with rollback and monitoring? |
| deployed | Is it actually influencing service delivery, enforcement, eligibility, payment, triage, guidance, or records? |
| paused | Has use been stopped pending policy, compliance, incident, staffing, or mission review? |
| withdrawn / decommissioned | Did a prior listing end, and what happened to records, contracts, models, data, notices, and affected users? |
| sensitive / exempt | Is the use withheld for lawful reasons, and does an oversight lane still test it? |
| consolidated commercial use | Is the row a license-category rollup rather than a specific agency workflow? |

A row that fails to name its state should not be cited as proof that the system is live. A missing row should not be cited as proof that there is no AI use.

### 2. Treat the register as a pointer bundle

A register row should point to the stronger surfaces it cannot itself replace:

- legal or policy authority;
- program owner and accountable official;
- procurement / contract or internal-build basis;
- system-of-record, data, model, and vendor lineage;
- risk classification and why it changed;
- impact assessment, privacy, civil-rights, accessibility, security, and human-review records;
- monitoring metrics, incident route, and complaint / redress route;
- lifecycle state, last review, next review, and decommissioning receipt.

A register that lacks links or stable identifiers may still be a disclosure artifact, but it should not be used as the operational governance record.

### 3. Separate public completeness from internal completeness

Public registers often exclude or aggregate some records. That can be legitimate. But the internal inventory should still be reconcilable by auditors and responsible officials. The minimum reconciliation question is: for every public omission, is there a lawful reason, an internal owner, a review clock, and a protected oversight route?

The dangerous states are:

- **public empty / internal active**: public sees nothing while internal use affects people;
- **public row / internal stale**: the published row survives after ownership, model, contract, or use changes;
- **public aggregate / operational specific**: a consolidated COTS row hides a consequential workflow;
- **public high-impact count / unsupported category**: risk labels appear without the assessment basis;
- **public retired / residual live**: a tool is said to be withdrawn while derived data, model output, case files, or contracts continue to matter.

### 4. Make versioning and update clocks part of the register

Public AI registers need version discipline closer to source-code and regulatory-document discipline than ordinary webpages. The record should preserve:

- date published, date last updated, and reporting period;
- row-level stable identifier;
- agency source URL and central aggregation URL;
- old value, new value, and reason for material row changes;
- lifecycle-state transition receipts;
- source-health state for the register itself;
- known gaps and exempt-use counts where law allows;
- machine-readable export and data dictionary.

A CSV without row history is only a snapshot. A snapshot is useful, but a snapshot cannot explain why a person encountered the system last month or why a published high-impact count changed.

### 5. Require use-case specificity

The same model or vendor product can be harmless in one use and high-risk in another. A register row should therefore describe the public function, actor, data flow, affected population, output role, and consequence class. “AI tool,” “chatbot,” “fraud detection,” “document summarization,” or “case prioritization” is not enough.

The governance unit is not the model name. It is the **use case in context**: who uses it, on what data, for what purpose, with what authority, what output role, what human review, what affected-party route, and what fallback.

### 6. Do not score transparency by row count alone

More rows can mean more transparency, more AI adoption, better classification, looser definitions, or duplicated / trivial entries. Fewer rows can mean less AI use, missed reporting, consolidation, exemptions, or reporting failure. Register quality should therefore be scored by paired measures:

- coverage against internal inventories and procurement records;
- timeliness against update clocks;
- row-level specificity and machine readability;
- high-impact / risk-label substantiation;
- lifecycle-state accuracy;
- linked assessment / monitoring / redress evidence;
- incident and retirement traceability;
- public comprehension and oversight use.

A register with fewer but precise rows can be stronger than a large list that cannot be reconciled to deployments.

### 7. Watch for procurement and platform laundering

Agency AI use can enter through cloud services, commercial suites, analytics platforms, case-management vendors, fraud tools, identity providers, translation tools, summarizers, and staff copilots. Procurement artifacts and platform configurations should therefore feed the inventory. Otherwise the register will miss the place where AI became operational: a licensed feature, a vendor update, a plug-in, a model-hosting service, or a configuration flag.

The archive should use the supplier-dependency and platform-migration notes whenever an AI register row has a vendor, SaaS, cloud, data-platform, or model-provider dependency.

### 8. Use public registers as audit triggers

A public register is not the whole audit, but it is a powerful trigger. Pick a row and ask:

1. Is this row still live?
2. What changed since it was first published?
3. Which records prove the lifecycle state?
4. Which people or decisions can it affect?
5. Where is monitoring and incident evidence?
6. Where can an affected person or oversight body contest the effect?

If a row cannot answer those questions, the repair is not to delete the register. The repair is to thicken the row’s pointers, clocks, and reconciliation trail.

## Findings table

| Risk | Bad shortcut | Repair |
| --- | --- | --- |
| inventory listing | row treated as authorization | link to authority, risk acceptance, owner, and deployment approval |
| missing row | absence treated as non-use | reconcile public, internal, procurement, and exempt inventories |
| stale row | old status treated as current | row-level update clock and material-change history |
| high-impact label | risk category treated as self-proving | impact-assessment basis and monitoring evidence |
| COTS rollup | license category hides workflow | specific use-case and affected-function map |
| paused / retired tool | disappearance treated as repair | decommissioning, residual-data, contract, and affected-user receipt |
| machine-readable CSV | neat table treated as governance | stable IDs, data dictionary, source-health, and linked evidence |
| sensitive exemption | secrecy becomes invisibility | protected oversight lane and public aggregate where lawful |

## Failure modes

- **Inventory sovereignty**: the register row becomes the whole governance case.
- **Absence laundering**: officials or critics infer non-use from public silence without internal reconciliation.
- **Row-count theater**: growth or decline in rows is celebrated without checking definitions, lifecycle state, duplicates, or omissions.
- **High-impact label laundering**: risk classification appears without the evidence that supports or challenges it.
- **COTS blur**: consolidated commercial use hides the specific workflow where consequence happens.
- **Stale deployment drift**: a public row stays frozen while model, vendor, data, ownership, or legal use changes.
- **Retirement by webpage**: a row disappears but data, outputs, case files, contracts, or users remain affected.
- **Public/internal split**: sensitive, R&D, law-enforcement, or exempt uses escape all visible and protected oversight.
- **No affected-person route**: the public can see a row but cannot tell whether it affected them or how to challenge it.

## Anti-theater tests

1. Pick one public AI inventory row. Can the agency prove lifecycle state, owner, authority, and current use?
2. Pick one high-impact or rights-facing row. Can the agency show the risk-classification basis, monitoring, incident, and redress record?
3. Pick one missing or exempt use. Can an auditor reconcile why it is not publicly listed and who reviews it?
4. Pick one consolidated commercial row. Can it be decomposed into actual agency workflows and consequence classes?
5. Pick one row changed since last year. Can the diff show what changed, when, why, and who approved it?
6. Pick one paused or decommissioned tool. Can the archive show residual-data, output, contract, and affected-user closure?
7. Pick one register export. Does it have stable row IDs, a data dictionary, dates, source URLs, and machine-readable fields?
8. Pick one public-facing chatbot, staff copilot, risk score, fraud tool, biometric tool, or case-triage system. Does the row point to the stronger case packet rather than standing alone?
9. Pick one agency with no reported use. Can that statement be reconciled against procurement, license, cloud, data-platform, and pilot records?
10. Pick one affected person. Could they tell whether a listed use might have shaped their guidance, payment, eligibility, enforcement, or case handling?

## Reconstruction instruction

Use this note with `857`, `876`, `879`, `887`, `901`, `910`, and the new public AI register tests whenever a public AI inventory, transparency record, high-risk AI database, agency AI page, or public COTS rollup is cited. The working rule is: **no governance by listing**. A register is a route into evidence, not a substitute for evidence.

## Sources

Source anchors include the 2025 U.S. Federal Agency AI Use Case Inventory, OMB M-25-21, GAO reviews of generative AI management, SBA AI reporting, and IRS AI inventories, the UK Algorithmic Transparency Recording Standard, and the EU AI Act high-risk AI database provisions. Exact source keys are registered in `sources/source_keys.json` and attached through `sources/source_catalog.json`.
