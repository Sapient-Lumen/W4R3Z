# Detection posture page — watcher coverage, rescan cadence, and manual-probe contract interface spec

## Purpose

The archive already had route posture, measurement planning, and instrumentation planning.
What it still lacked was one fixed page for another ordinary question:

> before we judge lateness, what observation posture was this subject actually under?

AnonSync should therefore model change discovery as a first-class **detection posture page**.
The product must never force the operator to infer freshness from `connected`, `running`, or vague expectations of immediacy.

## Core decision

Every serious delay or stale-view claim must preserve five truths before freshness judgment:

1. active detection planes
2. expected latency budget
3. known blind-window causes
4. manual-probe affordances
5. policy that would count as abnormal delay

## Fixed review order

1. **Subject and storage scope**
2. **Notification coverage posture**
3. **Rescan cadence posture**
4. **Manual probe contract**
5. **Known blind-window causes**
6. **Abnormal-delay threshold**

## 1) Subject and storage scope

Show:

- folder / subject under review
- incident or investigation id
- storage class or mount style if relevant
- whether posture is global, per-folder, or pair-specific

The operator must be able to answer:

> what exact subject does this detection posture belong to?

## 2) Notification coverage posture

Publish notification posture as explicit states, not hopeful assumptions:

- notifications expected and currently healthy
- notifications expected but degraded
- notifications unsupported for this storage shape
- notifications exhausted by watcher limits
- notifications intentionally not relied on

Also show the strongest basis available, such as platform capability, watcher budget, recent warning, or explicit configuration.

## 3) Rescan cadence posture

State the declared rescan contract in plain language, for example:

- `scheduled rescan every 10 minutes`
- `scheduled rescan widened for sleep preservation`
- `scheduled rescan disabled; only notifications/manual probe remain`
- `manual rescan is primary fallback`

Also show whether restart changes this posture.

## 4) Manual probe contract

The page must show what a manual rescan means here:

- verification only
- acceptable recovery rung
- last viable discovery plane
- prohibited because it would distort the incident

This prevents the operator from confusing `click rescan` with a neutral observation in all cases.

## 5) Known blind-window causes

List explicit contributors, such as:

- watcher exhaustion
- unsupported mount/filesystem notifications
- deliberately widened `folder_rescan_interval`
- zero automatic rescan posture
- paused or schedule-limited transfer context
- runtime posture designed to preserve disk sleep

## 6) Abnormal-delay threshold

State the threshold where the product is allowed to say:

- `still within expected discovery latency`
- `freshness weak; blind window still open`
- `delay exceeds declared detection budget`

## Compact rendering obligations

Any compact card for detection posture must still preserve:

- subject scope
- active detection plane summary
- expected latency budget
- blind-window label
- abnormal-delay threshold sentence

## Anti-clone rule

Do not clone workflows where the operator learns only from scattered FAQ prose that this subject was not under real-time observation in the first place.

## Receipt consequence

Every later coverage review or freshness review must link back to the exact detection-posture version it is judging.
