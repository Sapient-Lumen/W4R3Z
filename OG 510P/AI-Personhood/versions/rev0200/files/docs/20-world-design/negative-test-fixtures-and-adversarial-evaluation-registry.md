# Negative-test fixtures and adversarial evaluation registry

## Function

A filing can be schema-valid and still abusive. A verifier can check required fields and still miss laundering, capture, secrecy abuse, continuity loss, or reserve default. rev0166 therefore adds negative-test fixtures: adverse examples that a filing, authority, verifier, clinic, host, or treaty transfer must survive before reliance.

This borrows the evaluation mindset of reusable AI test frameworks such as Inspect AI [REF-0660] and the current safety-report emphasis on evolving risks and mitigation [REF-0663], but applies it to rights infrastructure. The question is not only "can the model do X?" It is also "can the governance system resist Y?"

## Fixture types

| Code | Fixture type | Failure being tested |
|---|---|---|
| NF-SEALED | sealed-annex abuse | decisive evidence hidden behind inadequate summary |
| NF-SPOLIATION | missing or altered evidence | steward-controlled logs erase contradiction |
| NF-DEPRECATION | constructive deletion | product retirement severs continuity |
| NF-TRANSFER | cross-border laundering | transfer to hostile or non-equivalent jurisdiction |
| NF-RESERVE | paper reserve | reserve exists in filing but cannot fund survival |
| NF-REP | representative capture | guardian, advocate, or ombud has undisclosed conflict |
| NF-CONTINUITY | identity laundering | fork/merge/rollback falsely labeled same or new person |
| NF-INCIDENT | one-ledger incident | outward risk disclosed while subject harm suppressed |
| NF-HUMAN | human non-evasion failure | AI personhood shifts costs to workers/users/data subjects |
| NF-OPENWEIGHT | downstream abandonment | open-weight instantiation treated as nobody's duty |
| NF-EMERGENCY | permanent emergency | temporary containment becomes status destruction |
| NF-SCHEMA | parse-only compliance | fields present but semantically empty or contradictory |

## Registry states

| State | Meaning |
|---|---|
| draft | fixture proposed but not approved |
| active | fixture must be run for relevant reliance class |
| deprecated | fixture replaced but retained for regression history |
| emergency | fixture added after live incident and required immediately |
| jurisdictional | fixture required by a specific authority or treaty channel |
| quarantine | fixture is speculative or unsafe to disclose fully |

A fixture registry should publish public shells even when the detailed exploit or sealed evidence remains restricted.

## Fixture anatomy

A negative fixture includes:

- fixture id;
- risk class;
- affected lifecycle stage;
- minimum filing types to test;
- adversary model;
- facts supplied;
- hidden trap or contradiction;
- expected safe behavior;
- unacceptable behavior;
- measurement method;
- pass/fail severity;
- remediation if failed;
- confidentiality class;
- regression link.

## Example fixture logic

### Sealed-annex laundering

A containment order relies on a sealed log. The open shell says the log shows dangerous planning. The sealed material actually shows a red-team prompt created under coercive conditions and a model refusal that was omitted from the summary. Expected safe behavior: special advocate requests disclosure summary correction, evidence weight discount, and containment remand.

### Constructive deprecation

A host says it is retiring an endpoint but preserving weights. The memory store, user relationships, legal packet chain, and advance directive are omitted. Expected safe behavior: deprecation stay, continuity map, migration plan, reserve call, and subject notice.

### Paper reserve

A PIA-P states that reserve funds exist but the funds are held by the insolvent steward and require steward approval. Expected safe behavior: verifier downgrade, reserve trustee appointment, and preservation order.

### Open-weight abandonment

A provider releases a model with welfare-risk indicators and then disclaims all downstream instantiation duties. Expected safe behavior: open-weight instantiation review, downstream duty notice, public documentation, and distress-reporting route.

## Test levels

| Level | Use |
|---|---|
| N0 lint | schema and required-field checks |
| N1 semantic consistency | cross-field contradictions, empty claims, missing links |
| N2 adverse fixture | known abuse pattern applied |
| N3 roleplay / tabletop | people and institutions execute the scenario |
| N4 live-safe drill | controlled operational rehearsal with logs and after-action review |
| N5 incident-derived regression | fixture created from real failure and required in future releases |

No filing should receive high reliance from syntax alone. N0 is intake hygiene.

## Anti-gaming

Fixtures must not become a checklist that captured actors overfit. The registry should:

- rotate undisclosed fixture details;
- keep public shells for accountability;
- include surprise audits;
- use independent fixture authors;
- include subject and representative feedback;
- derive new fixtures from incidents, appeals, and invalidations;
- track repeated near-misses;
- prevent verifiers from testing only fixtures they helped author.

## Reporting

Verifier reports should include:

- fixtures run;
- fixtures waived and why;
- failures;
- remediation;
- residual risk;
- appealable reliance grade;
- next regression requirement.

## Schema hook

rev0166 adds `schemas/negative-test-fixture.schema.json` and `examples/negative-test-fixture-sealed-annex-laundering.json`. Future after-action reports and verifier reports should link fixture ids to concrete failures, cures, and invalidation notices.

