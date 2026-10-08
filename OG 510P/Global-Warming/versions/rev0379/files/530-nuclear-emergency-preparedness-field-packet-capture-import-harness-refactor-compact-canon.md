# 530 — Nuclear Emergency Preparedness Field Packet Capture, Import Harness, and Finding Clock Refactor — Compact Canon

Revision: **rev0323**  
Scope: **REAL_BVPS_PUBLIC_ONLY remains public-context-only. No real Beaver Valley readiness or unreadiness claim is made.**

## Why this revision exists

Rev0322 created an exercise evidence escrow ledger. The remaining near-term failure is more concrete: people can agree that evidence is needed and still fail to capture it in a form the cube can import. Screenshots, revised templates, public-meeting notes, hotwash summaries, and recollections are not enough once raw logs and evaluator observations decay.

Rev0323 therefore adds a **field packet capture and import harness**. It turns the high-risk exercise artifacts into packet templates, required fields, chain-of-custody rules, sensitive-annex/public-surrogate routing, public-meeting transcript fields, a 90/120-day AAR clock, a validator, and SQLite views that expose open capture debt.

## Non-negotiable rule

**A packet can be accepted for adjudication only; it cannot auto-close readiness.**

A packet needs a hash, owner, timestamp, scope, original artifact pointer, sensitive-annex split, public surrogate, verifier, retest/CAP state when applicable, counterevidence path, and public-claim gate. Public context, public schedules, public meeting remarks, reactor-status pages, KI pages, public ETE tables, and brochures can route or reopen evidence demands. They cannot close local readiness evidence.

## New proof route

`escrow slot → field packet template → capture assignment → packet manifest → validator → adjudication board → CAP/retest/verifier → public claim gate`

## Operational focus

Rev0323 prioritizes artifacts that are easiest to lose and hardest to reconstruct:

- raw alert logs and CAP/IPAWS/EAS/WEA acknowledgments;
- PAD/PAR authority decisions and release-sequence timestamps;
- JIC, press, KI, farmer/producer, school, language-access, and accessibility message bundles;
- AFN dispatch, school/LTC/hospital movement, route-control, CRC/decon, field-monitoring, ingestion sampling, dosimetry, mass-care, and reception-center records;
- evaluator raw observations, controller deviations, hotwash notes, preliminary finding statements, CAP owners, retest evidence, closure-board minutes, and public-claim board minutes;
- EN58200 EOF non-regression evidence and exercise-day proof that emergency response facility workarounds were tested, not merely described.

## What changed from rev0322

Rev0322 answered: *what evidence must not disappear?*  
Rev0323 answers: *what is the exact packet shape, field-level acceptance rule, owner assignment, and rejection path?*

The revision adds:

1. an 18-row field packet template catalog;
2. a field-level packet specification for alerting, public information, transport, medical, ingestion, worker, mass-care, evaluator, CAP/retest, EN58200, and public-meeting packets;
3. a 44-row minute-zero capture assignment map tied back to rev0322 escrow slots;
4. a 40-test packet-intake validator;
5. public-meeting and 90/120-day AAR clock tables;
6. chain-of-custody, redaction, retention, and silent-loss default rules;
7. a schema-lag correction audit fixing the stale `cube/schema.json` revision surface;
8. a scoped SQLite mirror with zero public-context-to-local-closure leaks.

## Claim scope

The package does not assert Beaver Valley is ready, unready, green, safe, passed, failed, certified, or closed. It says only that public exercise context exists, that capture deadlines are imminent, and that local or anonymized evidence packets are required before any readiness claim can be made.
