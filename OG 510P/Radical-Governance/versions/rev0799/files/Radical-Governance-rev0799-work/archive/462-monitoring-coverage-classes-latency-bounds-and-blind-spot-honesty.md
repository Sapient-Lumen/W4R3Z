# 462 — Monitoring coverage classes, latency bounds, and blind-spot honesty

## One-line thesis

Public-AI monitoring should declare which events are observed directly, which are only reconciled later, which require manual discovery, and what blind spots or latency bounds remain, so “we monitor it” does not hide partial visibility.

## Why this matters

Consequential public-AI operators often say they monitor systems in production. That statement is too coarse to govern anything.

Some signals are captured on every event. Some are sampled. Some appear only after periodic reconciliation. Some arrive only if a user complains, an operator notices, or a manual export is run. Some disappear when a dependency fails, a quota fills, a connector is rate-limited, or a log source was never enabled in the first place. Yet many governance surfaces still flatten all of that into one reassuring phrase: monitoring is in place.

The archive already treats complaints, appeals, override telemetry, incidents, and public case logs as monitoring inputs. What it still lacked was one note forcing teams to say **how complete and how immediate** that visibility actually is. The archive should therefore treat monitoring coverage and latency as first-class governance facts.

## Pattern pack

### 1. Inventory monitored event families and their sources

Operators should be able to name at least the major monitored families, such as:

- user-facing decisions or notices,
- model outputs and abstentions,
- overrides and escalations,
- complaints and appeals,
- privileged actions,
- retrieval or source-selection events,
- model or policy changes,
- incident and stop events,
- and record-preservation failures.

For each family, the system should identify its actual source or sources.

### 2. Assign explicit coverage classes

A useful minimum vocabulary is:

- `direct` — captured on occurrence,
- `sampled` — only some events are captured,
- `reconciled` — truth arrives later through periodic comparison or batch import,
- `manual-only` — discovery depends on human action,
- `unknown` — the institution cannot currently prove coverage.

Institutions may use richer vocabularies, but they should not collapse these meanings.

### 3. Publish latency bounds and fallback paths

For each important signal, the archive should say:

- expected observation latency,
- whether latency is event-driven or periodic,
- what fallback path exists if the primary path fails,
- and what operator action can refresh truth sooner.

A signal that will only become visible after a nightly reconciliation should not be represented as immediate monitoring.

### 4. Surface degradation and budget conditions that widen blind spots

Monitoring truth can degrade because of:

- storage or retention exhaustion,
- rate limits,
- sampling caps,
- connector or integration failure,
- disabled log sources,
- inaccessible external systems,
- or scope exclusions that leave whole event families unseen.

Those conditions should be visible as governance facts, not only as troubleshooting details.

### 5. Keep not-yet-seen and not-observable separate

The archive should distinguish between:

- an event family that has not happened recently,
- an event family that would be seen only after reconciliation,
- and an event family the institution cannot currently observe.

Silence is not the same as visibility.

### 6. Route weak coverage to the next honest action

When monitoring is partial, the system should say what comes next:

- enable or repair the source,
- run a reconciliation or rescan,
- narrow the claim being made,
- increase review sampling,
- add a complaint or operator-report channel,
- or pause stronger assurances until coverage improves.

The next honest action belongs on the same surface as the coverage claim.

### 7. Make public and internal claims respect coverage reality

Public system cards, incident updates, executive dashboards, and approval reviews should not claim comprehensive oversight when key signal families remain sampled, delayed, manual-only, or unknown. Monitoring claims should be scoped to the visibility that actually exists.

## Guardrails

- Do not equate “some logging exists” with comprehensive monitoring.
- Do not hide delayed reconciliation behind real-time language.
- Do not treat absent events as proof that the event family is observable and currently quiet.
- Do not bury monitoring blind spots in engineering runbooks only.
- Do not let degraded coverage leave approval, launch, or incident surfaces looking fully green.

## Failure modes

- **monitor theater**: the institution claims full monitoring with only partial signal coverage.
- **false immediacy**: delayed or batch-discovered events are spoken of as real-time observations.
- **blind-spot denial**: unobservable event families disappear from reports instead of being marked unknown.
- **degradation silence**: quotas, connector failures, or disabled sources quietly widen monitoring gaps.
- **silence laundering**: no recent events is mistaken for reliable visibility into those events.

## Practical tests

A coverage-honest monitoring regime passes when it can answer yes to all of the following:

1. Are major monitored event families and their sources explicitly inventoried?
2. Does each family carry a coverage class such as direct, sampled, reconciled, manual-only, or unknown?
3. Are latency bounds and fallback paths visible for important signals?
4. Do degraded coverage conditions surface as governance facts rather than hidden troubleshooting details?
5. Do public and internal status claims narrow themselves to the visibility that actually exists?

## Compression rule for the archive

If an institution says **we monitor this system** but cannot also say **what we see directly, what we learn late, what we only learn manually, and where the blind spots still are**, then it is still letting **partial visibility impersonate oversight**.
