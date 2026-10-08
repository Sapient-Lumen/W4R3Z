# REQUEST-LIFETIME-TEST

This note tests request lifetime after rev0053.

rev0052 kept shared requests item-level.
rev0053 quarantined operator aliases outside the shared machine-facing surface.
The remaining question is lifecycle:
does an explicit item request persist?

## Question

Should the optional item-level request list be interpreted as:
- one-shot per exchange
- sticky across a session or association
- profile-fixed by configuration

The archive needs a rule small enough to keep the request surface honest without adding a subscription system by accident.

## Source pattern

The current source pattern splits the candidates.

- NTPv5 forms a fresh client request on each poll with the needed extension fields, keeps basic server operation free of client-specific state, and handles unsupported or unknown request material at the item/extension level. Interleaved mode has cross-poll cookie/timestamp machinery, but that is measurement machinery, not a general rule that optional visibility requests persist.
- Roughtime binds each response to a nonce-bearing request. TCP can carry multiple outstanding requests, but the tags in each request remain the accountable request contents.
- NTS separates key establishment from later time packets and deliberately keeps required server-side state out of the ordinary synchronization path by using client-carried cookies.
- PTP shows the contrasting pattern: where persistent transmission behavior is wanted, it becomes an explicit profile/signaling mechanism; a profile can also forbid that mechanism and choose defaults instead.

So deployed timing patterns support three different lifecycle homes:
- per-exchange request content
- explicit leased/signaled service
- profile/configuration default

They do **not** support silently reusing one ordinary request list for all three.

## Candidate pressure test

### 1. One-shot / exchange-scoped

This is the smallest default.

A request list means:
include these named items in this exchange if they are requestable and available.

Strengths:
- no hidden server obligation
- no cancellation grammar
- no stale profile or alias persistence
- no extra state recovery rule after restart, path change, or authentication change
- item-level exposure and result accounting remain local to the exchange

Weakness:
- clients that want the same optional items repeatedly must repeat the explicit item list

That weakness is acceptable.
Repeating a short item list is cheaper than inventing implicit state.

### 2. Sticky / session-scoped

Sticky behavior is attractive for dashboards, monitoring sessions, and high-rate profile flows.
But as a default interpretation it creates too much hidden machinery.

A sticky request immediately asks unanswered questions:
- what starts the sticky state
- what cancels it
- what expires it
- whether it survives restart, failover, source change, or profile change
- whether it is bound to identity, address, transport, authentication context, or association
- what happens when one requested item becomes `unknown` or `unavailable`
- how logs distinguish current requests from inherited old requests
- whether local operator aliases accidentally persist as server-facing obligations

Those questions are not minor implementation details.
They change the governance semantics of the request surface.

### 3. Profile-fixed

Profile-fixed visibility is real, but it is not a request lifetime.

If omission of an item would be misleading under a profile, that item belongs in the exposure class `required` or in profile-default export behavior.
It should not be modeled as a request that happened to stick.

This preserves the archive's earlier split:
- profile defaults say what a profile must surface
- request lists ask for optional requestable items
- operator aliases are local conveniences that expand before exchange

## Current archive rule

The ordinary shared request list is **exchange-scoped by default**.

A request list applies only to the exchange or response transaction in which it is carried.
To receive an optional item repeatedly, a participant must repeat the explicit item name, rely on a profile-required default, or use a future explicit leased/subscription mechanism if one earns itself.

The archive should not add:
- a `sticky` bit
- an implied session preference
- alias persistence
- or profile-fixed behavior disguised as a remembered request

## Explicit lease exception

A future sticky surface may still be legitimate.
But it must be explicit and profiled, not inferred.

A leased/subscription surface would need at least:
- explicit item names
- explicit duration, expiry, or renewal rule
- cancellation or expiry behavior
- identity / association binding
- restart and failover behavior
- item-level result reporting on each delivery
- a non-upgrade rule when one item becomes `unknown` or `unavailable`
- no shared operator alias names

That is already more than the current archive needs.
So the lease stays a future extension candidate, not the default meaning of a request list.

## Consequences for current hooks

### `traceability_posture`

If profile-required, it appears by default.
If requestable, it is requested per exchange.
A remembered traceability request must not let old evidence look current.

### `sync_dimension`

If profile-declared, it is profile/default state first.
If echoed only for clarity, request it per exchange.
Sticky echoing adds little and risks making profile changes invisible.

### `boundary_context`

This is the strongest candidate for repeated requests because operators may watch boundary explanation over time.
Even here, one-shot remains the right default:
explanatory context is most dangerous when stale.
A future monitoring profile can define a lease if repeated explanation becomes operationally necessary.

## Logging rule

Logs may record a local operator preference or alias annotation.
The accountable machine-facing record is still the explicit item list used in each exchange.

For repeated local display preferences, tools can repeat the expansion automatically.
They should not claim the remote side has a persistent request unless an explicit lease exists.

## Reduction result

The archive keeps one flat request list and gives it one default lifetime:

```text
request_scope: exchange
```

This is a semantic rule, not a new packet field.
No new grammar is needed yet.

## What this still does not settle

This note does not decide:
- what exact promotion bar would justify a future lease/subscription surface
- how repeated negative results would be summarized in such a future surface
- whether profile satisfaction needs a compact local marker

## rev0055 follow-on

rev0055 resolves this note's response-result frontier.

The ordinary exchange-scoped request list now has negative-only item accounting:
- returned requested content is success
- absent requested optional items may return `unavailable`, `unknown`, or `omitted`
- silence remains valid at unrequested, invalid, unauthenticated, profile-forbidden, legacy, and non-result-capable edges

This strengthens the rev0054 lifetime rule because each exchange can stand on its own without hidden request state.

## rev0056 follow-on

rev0056 resolves this note's required/default absence frontier.

Profile-required/default absence is profile-nonconforming by default and locally downgrade-triggering.
That result remains separate from ordinary request lifetime: a required/default item is owed by the profile boundary, not by remembered request state.

## Next useful move

Test the profile-conformance marker.
