# Compile Iteration Feedback Kit — activation and stale-code plan (2026-03-23)

The compile-iteration lane now needs a sharper answer than “the edit reloaded” or “the patch succeeded.”
The missing receiver-facing layer is:

1. **activation boundary** — when does fresh code actually take effect?
2. **stale-code risk** — what old code or old identity assumptions may still remain reachable?

## Why the existing bundle is not enough

The current bundle already carries:
- edit scope,
- patch eligibility,
- reload surface,
- fast-path barriers,
- state continuity,
- restart fallback,
- latency budget.

That is strong, but it still leaves a dangerous ambiguity.
A team can truthfully say:
- the edit was patch-eligible,
- the dylib was swapped,
- some state persisted,
- and the loop stayed fast,

while still failing to answer:
- whether fresh code is live on every relevant call path,
- whether activation only happens at a specific annotated entrypoint,
- whether old function pointers or trait objects can keep calling old code,
- whether continuity came from serialize/deserialize handoff rather than live in-place continuity,
- and whether identity-sensitive systems must be rebound.

## Artifact additions

### `activation-boundary.report.json`

Should answer:
- when fresh code becomes reachable;
- whether activation is global, entrypoint-gated, reload-hook-gated, or restart-only;
- whether old frames may continue until return;
- whether manual handoff is required before honest activation can be claimed.

Suggested key fields:
- `activation_class`
- `activation_trigger`
- `stale_frames_can_continue`
- `activation_scope_notes`
- `manual_review_reasons`

### `stale-code-risk.report.json`

Should answer:
- what old code/data/identity routes may remain alive after reload;
- whether rebinding or re-registration is required;
- whether explicit serialization/deserialization handoff exists;
- whether identity-sensitive systems (e.g. `TypeId` keyed stores) are exposed.

Suggested key fields:
- `residency_class`
- `risk_routes`
- `requires_explicit_rebinding`
- `explicit_handoff_available`
- `mitigation_routes`
- `manual_review_reasons`

## Initial proving grounds

1. **Chaud entrypoint activation** — hot code only becomes active when a `#[chaud::hot]` function is called.
2. **hot-lib-reloader reload events** — “about to reload” / “reloaded” hooks enable explicit handoff rather than magic continuity.
3. **stored call routes** — function pointers and trait objects can keep old code alive after reload.
4. **identity-sensitive stores** — `TypeId`-keyed systems invalidate simple “same state kept running” claims.
5. **portable bundle separation** — patch route, continuity, activation, and stale-code risk remain distinct files.

## Doctor rules to add

Reject or downgrade claims such as:
- “reloaded” when activation is only at the next annotated entrypoint;
- “state preserved” when continuity depended on explicit serialization/handoff;
- “new code active” when stored function pointers or trait objects can still route to old code;
- “same state continued” when `TypeId`/identity-sensitive systems require rebinding.

## What a worthy crate should provide other people

It should give another engineer one compact answer to four different questions:

1. **Did the edit stay on a fast path?**
2. **Did fresh code actually become active yet?**
3. **What old code may still survive or stay reachable?**
4. **Was continuity live, migrated, rebound, or only recoverable by restart?**

That is meaningfully more useful than another watch-loop wrapper or a vague “supports hot reload” badge.
