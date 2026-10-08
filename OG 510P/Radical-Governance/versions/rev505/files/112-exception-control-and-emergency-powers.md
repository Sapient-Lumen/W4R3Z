# Exception Control & Emergency Powers (Design so crises don’t become regimes)

**Stack relation:** use `286-emergency-powers-stack-and-exit-governance-guide.md` for the canonical route across the emergency / exception cluster. This memo is the generic exception-control kernel; `23` is the broad system frame; `165` is the canonical emergency-powers rails layer; `186` is the narrower declaration / renewal / sunset companion; `234` is the public-health operating specialization; `332` is the scope-design neighbor for which levels should directly hold emergency or force authority at all.

**Purpose:** enable fast response while making *exception* costly, time-bounded, reviewable, and reversible.

**Core claim:** emergency power is a **temporary interface** with strict invariants—not a blank check. Treat it like a controlled “override” with hard locks.

## Minimal protocol: the Four Locks

1. **Scope lock**
 - Define the *harm model* and allowed measures; forbid drift (“mission creep”).
 - Publish what is *not* authorized.
 - Any new measure requires a new authorization (not “interpretation”).

2. **Time lock**
 - Short initial duration; renewal requires an explicit vote/decision and updated justification.
 - Auto‑sunset for all delegated powers and special procedures.
 - Renewal must cite: outcomes, harms, alternatives tried, and why normal law can’t handle it.

3. **Oversight lock**
 - Continuous **judicial review** (standing rules widened; fast-track).
 - Independent audit/inspector access to records + procurement + detention/force (if relevant).
 - Public reporting cadence (minimum weekly/biweekly for major emergencies).

4. **Reversibility lock**
 - Every exceptional measure must have an exit ramp: conditions for rollback + what data proves it.
 - “No permanent infrastructure by stealth”: exceptional data systems and surveillance must be dismantled or re-authorized under normal law.

(International baseline: derogations/limitations must be necessary, proportionate, non-discriminatory, and consistent with non-derogable rights. See [BIB-HRC-GC29], [BIB-SIRACUSA].)

## Exceptions ledger (the safety valve you can *see*)

A public **Exceptions Ledger** makes deviations legible and contestable, including emergency procurement and administrative shortcuts.

**Ledger entry (minimum fields):**
- Unique ID; issuing authority; legal basis; start/end; scope; affected population.
- Measure type (restriction, spending, procurement, data access, detention, etc.).
- Justification + alternatives considered.
- Safeguards: oversight hooks; appeal path; data retention; compensation/remedy.
- Observables: indicators used to justify continuation; intended rollback trigger.
- Links: Decision Receipt (`106`), after-action report, audits, court rulings.

## Guardrails for high-risk exception types

**Emergency procurement**
- Default to open contracting transparency *even when fast*: publish vendors, unit prices, conflicts, changes, and delivery status.
- Pre-authorize “fast lanes” (framework contracts; prequalified vendors) to reduce sole-source abuse.
- Require post-hoc competitive rebid or independent value-for-money audit within a fixed window.
- Tie to: `110-budget-procurement-integrity.md`.

**Information powers (surveillance/data)**
- Least-intrusive first; strict purpose limitation; retention caps; independent access logs.
- Publish aggregate stats; ban cross-purpose reuse without fresh authorization.
- Tie to: `06-digital-and-algorithmic-governance.md`.

**Movement/assembly restrictions**
- Set clear metrics; publish review intervals; provide exemptions + non-digital access paths.
- Require impact assessment for inequity; provide mitigation (income support, services).
- Tie to: `98-persons-path-and-accessibility-invariants.md`.

**Coercion and detention**
- No “black sites”: custody rules stay on; inspection access remains.
- Fast judicial review; counsel access; medical screening.
- Tie to: SAFE primitives in `02` and `05-public-safety-and-coercion.md`.

## After-action learning (close the loop)

Within a fixed deadline after sunset:
- Publish an after-action report: what worked, what failed, rights impacts, corruption risks realized, and recommended statutory fixes.
- Run `107` test suite (esp. capture, contestability, coercion safety).
- Convert repeated emergency measures into normal-law instruments with full safeguards—or prohibit them.

## Failure modes (and the corresponding circuit breakers)

- **Drift:** measure scope expands → trigger: automatic re-authorization requirement + court review.
- **Time theft:** serial renewals without new evidence → trigger: shorter renewal windows + mandatory independent audit.
- **Procurement capture:** concentrated awards, repeated sole-source → trigger: freeze + independent review + forced rebid.
- **Data creep:** emergency data used for unrelated enforcement → trigger: purge + penalties + oversight escalation.
- **Suppressed contest:** blocked standing/slow courts → trigger: emergency standing expansion + mandatory deadlines.

(Comparative constitutional guidance and COVID-era emergency governance lessons: [BIB-VENICE-COVID-EMERGENCY-2020].)

## Minimal metrics

- Time under exception (days) by measure type; renewal count; scope changes.
- % exceptions with published ledger entries within 72h.
- Procurement concentration (top vendor share) and variance vs benchmarks.
- Court/appeal throughput and time-to-decision during emergency.
- Rollback compliance rate (measures retired on schedule).
