# 15 — Export and retention checklist

Use this checklist before a local assessed state crosses a boundary or becomes a retained record.

## Core state

- Does `timestate.interval.earliest <= timestate.interval.latest`?
- Is `timescale` explicit?
- Is `freshness` interpretable by the receiver or profile?
- Is `regime` one of the shared regime labels?
- Is `source_posture` compact and not pretending to be a full source roster?
- Is `applicability` scoped by the relevant profile when profile conformance is exported?

## Profile assessment

- Is `assessed_profile` present wherever `profile_conformance` is exported?
- Is profile reference strength sufficient for the boundary?
- Are required/default profile items present?
- If `profile_conformance = fallback`, is the fallback target label in the profile map?
- If fallback was caused by a boundary transition, is `boundary_context` present when required?

## Retention/current policy

- Is `assessment_time` present for retained/detached assessments?
- Does the profile reference include a digest where exact reconstruction matters?
- Is historical conformance preserved rather than rewritten?
- Is `policy_acceptance` added when current policy acceptance matters?
- If current policy rejects or cannot resolve the profile, is actionability non-actionable or unknown?

## Discovery/request

- Are requested items returned as values or explicit negative item results?
- Are local aliases expanded before shared exchange?
- Are ordinary requests treated as exchange-scoped unless a profile or lease says otherwise?

## Non-upgrade guard

Any missing hook, unknown boundary action, stale profile, unresolved digest, or relay restatement may preserve or weaken applicability. It must not silently strengthen it.
