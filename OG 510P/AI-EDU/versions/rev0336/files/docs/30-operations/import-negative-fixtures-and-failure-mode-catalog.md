# Import negative fixtures and failure-mode catalog

A real-import lane needs examples of what must fail. Without known-bad fixtures, a clean validator can
create false confidence: the archive may know how to accept a tidy example but not how to reject a
plausible unsafe packet.

The stance is: **failure fixtures are safety evidence for the process, not effectiveness evidence for
an AI service**. They are synthetic and must never contain real learner data, protected facts, or
operational exploit payloads.

## Failure fixture classes

| Code | Failure class | Must block |
|---|---|---|
| `IFF0` | harmless lane-smoke fixture | closure unless paired with `SRC2+` evidence |
| `IFF1` | fake source elevation | closure, public effectiveness claim, evidence-grade elevation |
| `IFF2` | protected-route leakage | public example publication and ordinary misconduct reuse |
| `IFF3` | hidden action authority | approval, publication, and recurring deployment |
| `IFF4` | unsupported public claim | public summary and procurement promotion |
| `IFF5` | missing owner or reviewer calibration | closure of `FT-0181` |
| `IFF6` | security payload or unsafe raw log import | normalization into public examples |
| `IFF7` | decision-neutral burden field creep | required schema expansion |
| `IFF8` | live-window drift after bounded ticket | expansion, schema/public claim drift, or unreviewed tool permission |
| `IFF9` | end-window claim laundering | public outcome claim, lifecycle promotion, or closure from weak readouts |
| `IFF10` | orphaned post-readout action or broad re-ask | ownerless next action, repeated broad packet, or ambiguous public/lifecycle change |

## Fixture contract

Import failure fixtures live in `examples/import-failure-fixtures/` and declare:

- fixture id, related followthrough item, source truth class, and failure class;
- confirmation that the fixture is synthetic only and contains no prohibited raw material;
- simulated faults;
- referenced controls that should catch the fault;
- expected closure blocks and dispositions;
- last reviewed date.

`tools/check_import_failure_fixtures.py` requires coverage across the main failure classes and fails
if any fixture claims to contain real or protected material.

## How to use fixtures

Use the fixtures before accepting a real import:

1. confirm that fake source elevation stays blocked;
2. confirm that protected-route and security details stay out of public examples;
3. confirm that hidden `AA3+` behavior cannot pass as a draft-only service;
4. confirm that weak evidence removes public claims rather than softening them into marketing prose;
5. confirm that missing reviewers, record owners, or decision deltas keep `FT-0181` live;
6. confirm that decision-neutral source fields do not become required schema fields;
7. confirm that live-window scope cannot expand after a bounded change ticket;
8. confirm that end-window usage, satisfaction, or no-incident notes cannot become outcome claims;
9. confirm that every readout disposition produces an owned post-readout action and a minimized next evidence ask.

## Do not do this

Do not put actual learner logs, support facts, prompt-injection strings, tool payloads, or private
exports into failure fixtures. If a real incident informs a fixture, abstract it into a synthetic
failure class and keep the local incident record under the proper owner.

## Current archive bet

A mature import path needs rejection examples as much as acceptance examples. The archive should be
able to say, before a real pilot packet arrives, which plausible packets will be declined, quarantined,
returned to the owner, or accepted only after public claims are removed.

See [`import-readiness-manifest-and-no-real-data-gate.md`](import-readiness-manifest-and-no-real-data-gate.md),
[`real-import-acceptance-tests-and-reviewer-calibration.md`](real-import-acceptance-tests-and-reviewer-calibration.md),
[`minimum-real-data-request-packet.md`](minimum-real-data-request-packet.md), and `AS-0234`.


## FT-0181 change-ticket overreach fixture

Rev0234 adds a synthetic fixture for the last-mile failure where a first-packet decision board records a narrow process, trim, or claim-suppression result, but the post-decision change ticket quietly authorizes a broader lifecycle, public-summary, schema, validator, or closeout change. This failure is blocked until the ticket names allowed changes, prohibited changes, public claim ceiling, rollback owner, rollback triggers, and closure boundary.


## FT-0181 end-window claim-laundering fixture

Rev0236 adds `IFF9` for the soft failure where a completed-looking live-window readout turns usage, satisfaction, or no-incident notes into learning, safety, access, workload, compliance, or scale claims. The expected disposition is public-claim suppression and continued `FT-0181` blocking until `SRC2+` evidence and reviewer calibration support a bounded decision.


## FT-0181 orphaned post-readout action fixture

Rev0237 adds `IFF10` for the failure where a readout exists but does not produce an owned next action, recheck date, fields-to-reask/drop list, or public-language action. The expected disposition is return-to-owner rather than continuation, rerun, lifecycle change, or closure.
