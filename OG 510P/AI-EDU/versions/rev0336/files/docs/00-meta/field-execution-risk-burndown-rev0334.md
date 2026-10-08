# Field execution risk burndown — rev0334

| Risk | Prior state | rev0334 change | Remaining test |
|---|---|---|---|
| Local result becomes a paperwork dead end | the router stopped after a result receipt but did not map the owner decision | router now reads `MICRO-PILOT-RESULT.json` and exposes decision-specific next action | a real owner-reviewed result must drive a bounded local action or stop |
| Repeat/continue becomes cumulative pseudo-evidence | repeated cycles could be appended informally to the same packet | repeat and continue require a fresh packet, fresh owner plan, and no pooling/trend claim | a second cycle must start as a new local feasibility packet, not as evidence accumulation |
| Escalation becomes hidden authority | `escalate-to-pilot-review` could sound like accepted evidence or deployment approval | escalation now stops the local lane and names a separate future gate with design/privacy/custody requirements | any real escalation must enter a distinct accepted route before import or public claim |
| Retirement vanishes into a completed artifact | `retire` was just a value in the result receipt | retire now explicitly stops the local line unless a new discovery conversation identifies a different problem | operators must not keep refining a retired packet because the paperwork exists |
| Control growth displaces field work | the defect could have spawned another review registry | reused the existing result recorder, router, generated templates, and docs | next change should follow a field event or reproducible hot-path defect |

## Current unblocker

Hold one real discovery conversation, complete one local owner plan, run at most one feasibility cycle,
and record only aggregate dated rows. If a result exists, obey the decision-follow-through map. Do not
treat a decision-follow-through map as evidence that learning improved or that `FT-0181` can close.
