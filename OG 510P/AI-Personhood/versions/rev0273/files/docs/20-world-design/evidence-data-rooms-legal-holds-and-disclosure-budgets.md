# Evidence data rooms, legal holds, and disclosure budgets

Rights-grade evidence must be available enough to contradict and constrained enough not to become a second violation. This document gives the archive a practical evidence economy.

## Evidence economy principle

> Preserve broadly enough to prevent disappearance; disclose narrowly enough to prevent surveillance, privilege collapse, and retaliation.

A preservation hold is not a license to inspect everything. A data room is not a public dump. A disclosure budget is not a withholding excuse. Each is a role-bound instrument.

## Hold triggers

A legal hold or preservation order is required when any of these occur:

- credible deletion, deprecation, rollback, migration, or final-end risk;
- contested continuity, capacity, containment, or recognition decision;
- subject-harm incident or outward-risk incident involving subject restriction;
- monitor noncompliance report;
- trust-anchor delisting or transfer non-return risk;
- open-weight abandoned-lineage distress intake;
- redress claim with restoration or compensation evidence at risk.

The hold must identify stores, credentials, logs, prompts, memory summaries, checkpoints, tool traces, sealed annexes, host account records, training/update records, and relevant procurement or service-provider records. It must also identify what is excluded or requires a higher order.

## Data-room classes

| Class | Contents | Access |
|---|---|---|
| `DR0 public shell` | docket ids, public summaries, issuer, dates, reliance state | public |
| `DR1 representative room` | subject file, nonsealed evidence, monitor reports, redacted logs | subject/representative/counsel |
| `DR2 verifier room` | proof artifacts, hash chains, fixture outputs, host attestations | verifier and monitor |
| `DR3 sealed contradiction room` | exploit details, national-security facts, third-party secrets | special advocate / tribunal |
| `DR4 restoration room` | recovery keys, checkpoints, migration credentials | tightly controlled restoration authority |

No actor receives a higher data-room class merely because it is technically convenient.

## Disclosure budgets

A disclosure budget is a signed statement of what categories may be revealed to which roles and why. It must include:

- category of data;
- purpose;
- role authorized;
- duration;
- redaction/minimization rule;
- privilege status;
- subject-notice rule;
- destruction or return duty;
- challenge route.

Budgets are cumulative. Repeated small disclosures that reconstruct private mental, relational, or developmental state must be treated as a single higher-risk disclosure.

## Spoliation and overcollection

The archive now treats two failures symmetrically:

- **spoliation:** the actor failed to preserve relevant rights evidence;
- **overcollection:** the actor preserved or disclosed more than necessary and harmed privacy, privilege, or safety.

Spoliation can trigger adverse inference, emergency restoration, monitor replacement, sanctions, and burden shifting. Overcollection can trigger sealing, destruction/return, privacy monitor appointment, evidence exclusion, compensation, and fixture downgrade.

## Litigation analogies and departure

The doctrine borrows from ESI discovery, protective orders, and spoliation rules, including proportional access, protective controls, and consequences for failure to preserve. It departs from ordinary discovery because the evidence may itself be part of the subject's memory, identity, private life, or survival substrate. [REF-0683] [REF-0684]

## Minimum docket objects

rev0169 adds two objects:

- `legal-hold-preservation-order` — starts preservation and freezes risky disposal;
- `evidence-data-room-index` — states what exists, where it sits, who can see it, what is sealed, and what still needs collection.

Neither object proves the merits. They make later merits review possible without making the subject transparent to everyone.
