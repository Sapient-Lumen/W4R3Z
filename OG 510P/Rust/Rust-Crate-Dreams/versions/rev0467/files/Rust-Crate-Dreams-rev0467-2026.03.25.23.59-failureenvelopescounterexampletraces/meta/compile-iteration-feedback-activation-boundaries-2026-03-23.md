# Compile Iteration Feedback Kit — activation boundary notes (2026-03-23)

**P-0537** now needs an explicit boundary note so future revisions do not flatten edit scope, patch route, state continuity, activation, and stale-code residency into one fake result.

## Distinct from patch eligibility

`patch-eligibility.report` answers **what route is theoretically available for this edit**.

`activation-boundary.report` answers **when fresh code actually takes effect after that route runs**.

A patch may be eligible and even applied while activation is still delayed until the next hot entrypoint or manual handoff boundary.

## Distinct from reload surface

`reload-surface.report` answers **what visible surface was updated**.

`activation-boundary.report` answers **when logic-level freshness is actually live on relevant call paths**.

A surface can appear updated while old code still remains reachable through stored callbacks, trait objects, or in-flight frames.

## Distinct from state continuity

`state-continuity.contract` answers **what state survives, resets, migrates, or is out of scope**.

`activation-boundary.report` answers **when fresh code becomes active**.

`stale-code-risk.report` answers **what old code/identity routes may still linger even if some state was preserved**.

A bundle can truthfully say “state survived” while still being unable to claim that every call edge now hits fresh code.

## Distinct from restart fallback

`fallback-restart.plan` answers **what deterministic recovery path exists when a live takeover is not honest enough**.

`stale-code-risk.report` answers **why restart may still be required even after a reload-looking event**.

## What later passes must not do

Do not compress these into statements like:
- “hot reload worked,”
- “the code is live,”
- “state was preserved,”
- or “no restart needed.”

Those can each hide different truths about:
- route availability,
- activation timing,
- stale-code reachability,
- rebinding obligations,
- and explicit handoff requirements.
