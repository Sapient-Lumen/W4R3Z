# Supervision posture v0

Purpose: pin a first-phase meaning for Steward supervision.

## Posture
1. **Component-rooted, user-space supervision**
   - Steward supervises explicit component roots identified by `cid`, not raw PIDs, shell jobs, cgroups, or host process subtrees.
2. **Supervised services stay foreground and directly accountable**
   - A supervised component presents a directly accountable runtime root to Steward.
   - Phase 1 does not standardize self-daemonizing, double-fork, or “the real service escaped elsewhere” lifecycle patterns.
3. **Deterministic bounded stop → kill**
   - Portable lifecycle control is: request cooperative stop, wait bounded grace, then escalate to termination.
   - Signal names, jobspecs, pidfds, and job objects are implementation detail, not public Steward semantics.
4. **Restart is bounded and explicit**
   - Restart policy is manifest-bounded; no hidden infinite retry loops.
   - Cooldown / backoff details may vary by implementation, but crash-loop behavior must remain bounded and explainable.
5. **Restart replays manifest + activation only**
   - Restart cannot widen route sets or resurrect undeclared authority.
6. **No host-global service-manager DSL in v0**
   - Steward may eventually gain more planning or orchestration surfaces, but revision 2 still refuses to turn supervision into a giant all-in-one admin language.
7. **Compatibility remains sealed**
   - Host service managers may exist beneath a compat membrane, but their control surfaces do not become Steward's native contract.

## Phase-1 non-goals
- generic process inventory or watch APIs;
- portable pidfd or job-object control;
- process-tree targeting;
- adopting arbitrary foreign host processes into Steward lifecycle;
- portable support for self-daemonizing services as the normal supervision model.

## Adjacent docs
- `design-principles-v0.md`
- `component-manifest-schema-v0.md`
- `activation-posture-v0.md`
- `readiness-posture-v0.md`
- `quiesce-posture-v0.md`

## References
- REF-LAUNCHD-JOBS
- REF-DAEMONTOOLS-SUPERVISE
- REF-RUNIT-OVERVIEW
- REF-ERLANG-OTP-SUPERVISOR
- REF-SOLARIS-SMF-RESTARTER
- REF-S6-RC-WHY
