# REQUEST-RESULT-SHAPE-TEST

This note tests response result shape after rev0054.

rev0052 kept requests item-level.
rev0053 quarantined operator aliases.
rev0054 made ordinary requests exchange-scoped.
The remaining ambiguity is absence:
when an optional item is explicitly requested in this exchange and does not appear,
is silence enough?

## Question

Should requested-but-absent optional items be represented by:
- silence
- existing exposure class only
- a full manifest of every requested item
- or a compact item-level result envelope

The archive needs accountability without accidentally creating a protocol-wide error system.

## Source pattern

The source base points to a middle answer.

- NTPv5 extension fields use concrete item identity. A server is generally expected to echo request extension fields unless the field specification says otherwise or the server does not support them. When fields are excluded, the draft uses padding to preserve request/response length symmetry, and a client may interpret absence of an expected extension as lack of support.
- NTPv5 also keeps failures compact where needed: authentication failure has a small header flag rather than a general workflow error object.
- Roughtime goes further in the opposite direction. It deliberately provides no mechanism for reporting malformed requests, unsupported versions, or unknown server-key selectors back to the client, partly because unauthenticated error signaling can be abused.
- PTP profile material separates ordinary timing exchange from profile/configuration/management choices. A profile can require, permit, forbid, or ignore behavior without implying that every timing packet needs a rich per-option error report.

So silence is sometimes legitimate,
but once the archive creates an explicit exchange-scoped request surface,
complete silence for an acknowledged result-capable exchange becomes too ambiguous.

## Candidate pressure test

### 1. Silence only

Silence is the smallest representation.
It also preserves useful security behavior at invalid or unauthenticated protocol edges.

But silence alone fails inside a valid request/response exchange because it cannot distinguish:
- the responder did not understand the item
- the responder understands it but cannot surface it
- the responder cannot currently know the value
- the responder intentionally did not include it in this exchange
- the requester used a stale local alias expansion
- or the response path lost an optional field

After rev0054, the request is one-shot.
That makes this ambiguity more expensive: there is no standing request state to inspect later.

### 2. Full requested-item manifest

A full manifest would echo every requested item with `present` or a negative result.
That is too much for the current archive.

Returned item content is already the success signal.
A full manifest would duplicate successes, increase response size, and create a new consistency problem when the item is present but the manifest disagrees.

### 3. Negative-only item results

A negative-only result is the smallest accountable shape.

Current sketch:

```text
request_result:
  item: traceability_posture
  result: unavailable | unknown | omitted
  reason: optional existing tiny reason, only where a profile needs it
```

This is not a packet grammar.
It is an architectural shape.

## Current archive rule

The archive adopts a **negative-only item-level result envelope** for explicitly requested optional items.

Rules:

1. **Presence is success.**
   If the requested item appears in the response, no separate `present` result is needed.

2. **Negative results are item-level.**
   Results name explicit item names such as `traceability_posture`, `sync_dimension`, or `boundary_context`.
   They do not name aliases, bundles, or operator presets.

3. **The base negative vocabulary is tiny.**
   - `unavailable` — the responder knows this boundary cannot surface the item.
   - `unknown` — the responder cannot honestly determine the item value or support state now.
   - `omitted` — the item was not returned in this exchange without asserting durable unavailability or unknownness.

4. **No generic `denied` yet.**
   Access-control denial is too policy-heavy and security-sensitive for the base timing exchange vocabulary.
   A demanding authenticated profile may define a specific policy result later.
   Until then, denial-like behavior is either profile/configuration behavior, local assessment, or a narrow authenticated extension.

5. **`unsupported` folds into `unavailable`.**
   The archive does not need both terms at this layer.

6. **Silence still has legitimate homes.**
   Silence remains acceptable for:
   - unrequested items
   - invalid requests
   - unauthenticated or unauthenticatable error edges
   - profile-forbidden request mechanisms
   - legacy or non-result-capable exchanges
   - responder behavior whose profile explicitly says absence means unsupported

The result envelope is therefore not universal.
It is a compact accountability surface for cases where the exchange already has explicit request/result semantics.

## Placement

The result envelope is **response-adjacent**, not part of minimal `TimeState`.

If the request was carried on the wire and the response has an authenticated claim container,
the negative result should be protected by the same response integrity boundary when feasible.
Otherwise a malicious path could remove an item and invent or alter the absence explanation.

Local assessed state may record:
- which item was requested
- which item appeared
- which negative result was received
- and what consequence followed

But the negative result itself is not a new core timing field.
It is request accounting.

## Consequences for current items

### `traceability_posture`

If requested and not returned,
the responder should report `unavailable`, `unknown`, or `omitted` when the exchange supports item results.
The requester must not preserve a stronger traceability-dependent applicability claim merely because the item was requested.

### `sync_dimension`

If the dimension is profile-declared, no request result is needed.
If it is only requestable/echoed for clarity and is absent after request,
the same negative result rule applies.

### `boundary_context`

This is the cleanest use case for negative results.
An operator may ask for boundary explanation and receive:
- the context itself
- `unavailable`
- `unknown`
- or `omitted`

That is enough to prevent a UI from silently implying that no boundary action occurred.

## Non-upgrade rule

A negative result cannot strengthen semantics.

If an alias expanded to three explicit item requests and one item returns `unknown`,
the alias summary may not display the combined preset as satisfied.
If a bundle-like profile expectation is partly satisfied,
item-level results remain the accountable record.

## Reduction result

The archive does **not** add:
- a full requested-item manifest
- alias-level result status
- bundle-level result status
- a general error taxonomy
- a generic access-denial vocabulary
- or a persistent result state

It adds only this semantic rule:

```text
requested optional item absent + result-capable response => negative item result
```

That is small enough to keep.

## What this still does not settle

This note does not decide:
- whether `omitted` ever needs mandatory reasons
- whether profile conformance needs a compact local marker
- what exact encoding would carry results in a concrete protocol
- how a future lease/subscription surface would aggregate repeated negative results

## rev0056 closure

rev0056 answers the required/default absence question:
if a concrete profile requires/defaults an item and the response omits it, the response is not full-profile-satisfying by default, and local assessed state must downgrade hook-dependent consequences.

This is deliberately separate from the rev0055 optional request result envelope.

## Next useful move

Test whether profile satisfaction needs a compact local marker such as `satisfied | fallback | unsatisfied`, or whether profile validation can remain implicit.
