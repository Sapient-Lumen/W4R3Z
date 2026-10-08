# Operational truth splits

GlassTTY should avoid collapsing different kinds of truth into one vague success story.

## Why this matters

Browser-native AI systems are full of partial signals:
- a submit button can animate without a real turn starting
- a toast can claim success while durable state never changes
- a route can look stable while SPA history has moved underneath us
- a support record can sound confident while evidence is stale

The repo should therefore preserve multiple truths instead of flattening them.

## Canonical truth splits

### 1. Runtime truth
What the process/runtime layer knows.
Examples:
- extension/service worker present or not
- native host connected or not
- broker socket reachable or not
- CLI request sent or rejected

This truth belongs in diagnostics, doctor, readiness, and transport artifacts.

### 2. Navigation truth
What browser location and route continuity actually did.
Examples:
- URL before and after an action
- route hint before and after an action
- hash/query/path deltas
- push/replace/back/forward restoration behavior
- modal or overlay takeover without route change

This truth belongs in the `navigation` state family and browser-history witnesses.

### 3. Action truth
What GlassTTY attempted and what result it can honestly claim.
Examples:
- write attempted vs not attempted
- submit activated vs could not be activated
- result `ok` / `no-op` / `blocked` / `failed` / `unknown`
- reason and evidence refs

This truth belongs in `action_outcome`.

### 4. State truth
What the surface currently exposes as structured state.
Examples:
- composer editability
- generation status
- latest-turn partial/completed status
- receiver ambiguity

This truth belongs in state-family payloads and should preserve uncertainty.

### 5. Evidence truth
What durable artifacts exist for later inspection.
Examples:
- state snapshots
- support bundles
- route/history witnesses
- drift comparisons
- release-gate artifacts

This truth belongs in the evidence ledger and support captures.

### 6. Support truth
What the project is allowed to claim publicly.
Examples:
- `claude × composer-write × chromium-live = experimental`
- `chatgpt × latest-turn-read × chromium-live = investigated`

Support truth must be derived from evidence truth and scoped by lane/workflow, not inferred from optimism.

## Rules

1. Do not let runtime truth stand in for workflow truth.
2. Do not let transient UI cues stand in for durable state truth.
3. Do not let navigation truth disappear just because the route is SPA-driven.
4. Do not let support truth outrun evidence truth.
5. When truths disagree, report the disagreement instead of choosing the flattering one.

## Example

A `turn-submit` run can honestly report all of the following at once:
- runtime truth: native connection healthy
- navigation truth: route unchanged, overlay appeared
- action truth: submit attempted, result `unknown`
- state truth: generation cue briefly visible, latest assistant turn not yet confirmed
- evidence truth: toast screenshot and state snapshot captured
- support truth: insufficient for promotion without a durable post-submit turn/state artifact

That is better than a vague “submit probably worked.”
