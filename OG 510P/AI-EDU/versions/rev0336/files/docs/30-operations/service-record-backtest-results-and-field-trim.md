# Service-record backtest results and field trim

This surface pressure-tests the rev0212 claim matrix, construct crosswalk, and
pilot packet against synthetic service records. The point is not to pretend
synthetic cases are field evidence. The point is to find which fields changed
decisions before the archive asks busy implementers to use the packet.

## Backtest cases

| Case | Decision pressure | Result |
|---|---|---|
| algebra hint tutor | task gains might be mistaken for learning gains | claim-family separation was necessary; keep delayed retention / transfer field |
| writing feedback assistant | revision quality might be mistaken for authorship proof | construct / disclosure fields were necessary; keep independent proof field |
| teacher planning assistant | time saved might hide review and correction labor | workload field changed the decision; keep total-labor accounting |
| advising / navigation assistant | fast answers might become record-changing advice | action authority and record-owner fields changed the decision; keep both |
| accessibility support | support traces might be treated as misconduct metadata | protected-route separation changed the decision; keep support/misconduct boundary |
| capped agentic workflow | convenience might expand into excessive agency | security posture and action ceiling changed the decision; keep red-team / rollback fields |
| assessment-adjacent marking support | rubric consistency might be mistaken for validity | validity, contestability, and human-final fields changed the decision; keep all |

## Fields that changed decisions

| Field | Why it stays |
|---|---|
| explicit non-use | stops pilots from expanding by convenience |
| claim families tested | prevents task evidence from becoming learning, equity, or validity evidence |
| evidence grade at launch | tells teams which public claims are still unmade |
| action authority | distinguishes advice, draft, queue, write, and decision power |
| memory class | prevents support continuity from becoming hidden profiling |
| construct / CE posture | preserves what the task is meant to measure |
| protected route | separates accessibility and accommodation support from ordinary suspicion |
| security posture | catches prompt injection, excessive agency, data leakage, and rollback readiness |
| human fallback | prevents service failure from becoming learner fault |
| stop triggers | makes narrowing or retirement normal rather than exceptional |
| renewal date | prevents pilot status from becoming indefinite production |
| public claim to remove | blocks evidence laundering at renewal |

## Fields to keep optional or compress

| Field | Treatment |
|---|---|
| long narrative problem statement | compress to one service-problem line plus owner |
| detailed vendor feature list | keep in the service-BOM, not every pilot packet |
| exhaustive metric list | keep only metrics tied to active claim families |
| full legal analysis | reference named compliance floor; keep detailed advice outside the packet |
| full security report | keep red-team result and residual risk in packet; store full report elsewhere |
| full accessibility file | keep protected-route owner and non-misuse rule; store confidential facts separately |

## Field added by backtest

The synthetic cases exposed one missing line:

```text
Public claim to remove if evidence stays weak:
```

Without that line, renewal packets tend to ask only whether to continue the
service, not what public story must shrink. The field has been added to the
renewal posture through this surface and should be backfilled into future
service-record schemas.

## Backtest decisions by case

| Case | Decision after backtest |
|---|---|
| algebra hint tutor | continue only if transfer / retention does not weaken; no scale learning claim yet |
| writing feedback assistant | keep optional; prohibit scoring, accusation, and detector-like use |
| teacher planning assistant | approve at `AA2` if review labor is counted and copyright/source checks exist |
| advising / navigation assistant | cap at `AA1-AA2`; record-changing advice requires owner confirmation |
| accessibility support | approve only through protected owner and non-misuse boundary |
| capped agentic workflow | allow sandbox or reversible queue action only; no durable write authority |
| assessment-adjacent marking support | human-final only; evidence may support moderation aid, not autonomous marking |

## Closeout

This resolves `FT-0173` for synthetic back-testing. It does not close the need
for real-world back-tests. That work is now narrower: collect actual pilot
records, compare them against the synthetic decisions, and remove or add fields
based on observed implementation burden.

See
[`../20-governance/claim-family-evidence-matrix.md`](../20-governance/claim-family-evidence-matrix.md),
[`../40-assessment/construct-family-crosswalk-for-proof-profiles.md`](../40-assessment/construct-family-crosswalk-for-proof-profiles.md),
[`ai-pilot-packet-and-filled-examples.md`](ai-pilot-packet-and-filled-examples.md),
[`../20-governance/ai-service-security-red-team-and-agentic-tool-boundaries.md`](../20-governance/ai-service-security-red-team-and-agentic-tool-boundaries.md),
and `B08`, `B11`, `B13`, `B17`, `B275`, `B279`, `B280`, `B281`.

## Rev0214 realistic record-set backtest

The second backtest used three realistic service records rather than prose-only synthetic cases:

| Record | What it tested | Decision pressure exposed |
|---|---|---|
| `examples/service-records/advising-navigation-assistant.json` | advising / navigation with public-route and record-owner adjacency | `AA2` cap, no-deadline-loss fallback, stale-source expiry, and correction route changed the decision |
| `examples/service-records/accessibility-support-record.json` | accessible-format and language-access support through protected route | protected memory rail, non-misuse boundary, and support/misconduct separation changed the decision |
| `examples/service-records/capped-agentic-reminder-workflow.json` | draft-only agentic workflow below durable write authority | rollback, prompt-injection testing, false-reminder review, and staff burden changed the decision |

The realistic records confirmed that the field added in rev0213 should remain mandatory:

```text
Public claim to remove if evidence stays weak or expires:
```

They also exposed four fields that should be validated, not merely suggested:

| Field | Why it became checkable |
|---|---|
| evidence expiry date | public claims otherwise outlive the tested context |
| early-expiry triggers | micro-changes can invalidate a claim before the calendar date |
| maximum allowed authority | decision ceilings can diverge from actual workflow power |
| public-summary allowed | internal records should not leak into user-facing notices by default |

The backtest still does not count as field evidence. It closes the design question of whether the
schema can carry realistic records. It opens the narrower implementation question of importing
actual pilot records when available.

See
[`machine-readable-service-record-schema-and-validator.md`](machine-readable-service-record-schema-and-validator.md)
and `tools/check_service_records.py`.
## Rev0215 follow-on backtest

The realistic service-record set now includes a K-12/minors hint-tutor sandbox plus
`publication_and_adapters` provenance fields. The backtest keeps these fields because they changed
review behavior: they prevent realistic examples from being read as field evidence, force
sector-adapter review, and prevent raw public summaries from being published without a redaction
profile.

The backtest still does not close the real-record question. `FT-0181` remains open until at least one
`SRC2` or stronger local pilot record is normalized and produces a decision-delta note.
