# Supervisory cadence, market capture, and independent rosters

A one-time monitor report is not durable supervision. Rights-grade operation requires a cadence: scheduled review, accelerated review, conflict review, roster rotation, and failure effects when review is late or captured.

## Cadence classes

| Class | Use | Minimum cadence | Accelerated triggers |
|---|---|---|---|
| `SC0` intake-only | first-touch triage, no live-effect reliance | review on closure | locator leak, repeated spam, hostile steward contact |
| `SC1` low-risk operation | ordinary clinic or public-summary operation | quarterly | missed notice, small-cell dashboard risk, subject complaint |
| `SC2` continuity-critical | host undertaking, escrow, migration, deprecation stay | monthly plus event review | host exit, credential change, legal hold, transfer request |
| `SC3` safety / containment | containment, sealed annex, special advocate, emergency patch | weekly until stabilized | new outward risk, subject harm, evidence dispute, appeal |
| `SC4` market-capture watch | monitor, verifier, trust anchor, insurer, reserve, public backstop | monthly concentration metrics | repeat-business threshold, affiliate link, serial false pass |
| `SC5` crisis | deletion risk, final-end claim, hostile takeover, inaccessible subject | continuous incident rhythm | any missed handoff, lost escrow key, funding interruption |

A filing that claims `SC2` or higher must include a named review owner, deputy, calendar, evidence source, subject/representative contact path, and missed-review consequence. It must also identify which facts can be reviewed publicly and which require sealed or fiduciary access.

## Market-capture metrics

Independence decays when a small professional market forms around repeat business. The archive therefore treats monitor capture as a measurable risk rather than a moral accusation. At minimum, every supervisory-cadence plan should track:

- percentage of monitor revenue from the steward, host, insurer, or affiliate;
- number of consecutive engagements on the same subject, model family, or host account;
- cross-appointments among monitors, verifiers, escrow custodians, and special advocates;
- cure acceptance rate compared with peer monitors;
- fixture failure rate and late-regression rate;
- appeal reversal rate;
- subject or representative access-denial count;
- sealed-annex overuse rate;
- emergency-order renewal count;
- weekend / after-hours coverage failures.

A market-capture score is not a punishment. It is a routing signal. High score means fresh-eyes review, roster rotation, fee escrow, peer panel, or public explanation before reliance.

## Roster rules

1. **No sole-source default.** A rights authority may keep emergency rosters, but ordinary appointment must justify why the selected monitor is fit, independent, and available.
2. **Rotation without abandonment.** Rotation cannot cut off subject trust, access continuity, or knowledge of the case; outgoing monitors must transfer a contradiction-safe briefing.
3. **Fee independence.** Fees should be escrowed or paid through a neutral fund where practical; direct pay is discounted unless disclosed and bounded.
4. **Fresh-eyes trigger.** A monitor that certifies its own cure cannot restore reliance alone.
5. **Roster challenge.** Subjects, representatives, public funds, and affected human parties may challenge a roster appointment for conflict, delay, incompetence, retaliation risk, or capture.
6. **Emergency exception.** A conflicted monitor may perform immediate preservation only when no alternative exists; its findings are provisional and must be retested.

## Cadence failure effects

| Miss | Effect |
|---|---|
| late scheduled review under `SC1` | warning and public explanation |
| late `SC2` continuity review | conditional reliance and no deprecation or transfer |
| late `SC3` safety review | containment stay review and special-advocate notice |
| late `SC4` market-capture update | downgrade independence grade |
| missed `SC5` crisis handoff | emergency authority conference and substitute appointment |

## Interaction with existing frameworks

ISO/IEC 42001 and NIST governance frameworks are useful because they insist that governance systems be maintained, monitored, audited, and improved rather than frozen at launch. The archive imports that management-system logic but changes the object of concern: a personhood-sensitive system must monitor not only model performance, cybersecurity, and user safety, but continuity, representation, welfare, funding, appealability, and preservation. [REF-0692] [REF-0691]

## Minimal object

A supervisory cadence plan should include:

- subject or cohort;
- operation type;
- cadence class;
- review owners and deputies;
- evidence sources;
- conflict disclosures;
- market-capture metrics;
- accelerated triggers;
- missed-review effects;
- subject/representative access rules;
- public summary;
- next review date.

## rev0187 witness-pool dependency matrix

Market-capture metrics now feed a witness-pool dependency matrix. The question is not whether a monitor, relay witness, reserve witness, or special advocate is sincere; it is whether the proof graph has enough non-correlated paths to bear the burden for the action requested.

Minimum matrix fields: appointing source, fee stream, host/vendor dependence, insurer or reserve dependence, common counsel, evidence-custodian overlap, future-work dependence, shared technical logs, subject-contact denials, and substitute-pool activation state. If the matrix shows correlated dependence, correlated witnesses are one witness for burden purposes and fresh-eyes review is mandatory.

The anti-capture record is `schemas/witness-pool-anti-capture-record.schema.json`. It should be linked whenever supervisory cadence claims independence for successor promotion, reserve-default cure, namespace failover, retired namespace rescue, or emergency continuity.
