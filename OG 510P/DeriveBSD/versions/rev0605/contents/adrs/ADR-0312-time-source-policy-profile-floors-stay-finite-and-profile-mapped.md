# ADR-0312: Time-source policy profile floors stay finite and profile-mapped

- Status: Accepted
- Date: 2026-03-23

## Context

`adrs/ADR-0058-trustworthy-time-posture-by-profile.md` already fixed the large product-shape posture:
DeriveBSD does not treat trustworthy time as ambient daemon folklore.

`adrs/ADR-0292-time-requirement-degraded-time-response-stays-explicit-and-proof-bundle-bound.md` then fixed the next workflow boundary:
if time is degraded, the requirement object itself must say whether the workflow denies, repairs, breakglasses, or may continue only with an exact proof bundle.

But `docs/266-open-questions-and-risk-register.md` still left one implementation-blocking seam open:

> what exact `time-source-policy` floor should each product shape compile to, and when does Roughtime stop being an optional nice-to-have?

Without that narrower decision, "authenticated time" still drifts in practice:

- fleet hosts relax into one public NTS server plus hope
- workstations and laptops inherit server-class quorum settings that are too brittle for normal mobility
- general-purpose systems quietly make RTC drift and weak fallback the real baseline
- factory/regulatory systems blur the line between their steady-state policy and their separate signed offline-time bootstrap story

The archive already has the right object for this cut:

- `time-source-policy` already carries source set, quorum, and bootstrap constraints
- `time.source.policy.diff` already makes policy relaxation reviewable
- product profiles already carry the higher-level posture strings

What was missing was one explicit, finite mapping from those posture strings to concrete reviewable floors.

## Decision

1. **`time-source-policy` floors are now profile-mapped and finite.**
   The archive no longer leaves quorum/skew/bootstrap floors open-ended by profile.

2. **A (`fleet_host`) steady-state policy floor is now:**
   - at least **three authenticated sources** configured
   - at least **one `nts` source and one `roughtime` source** present
   - `quorum.min_sources >= 2`
   - `quorum.max_skew_ms <= 50`
   - `quorum.require_vendor_diversity = true`
   - bounded RTC bootstrap is allowed only as a narrow bridge:
     - `bootstrap.allow_rtc = true`
     - `bootstrap.max_rtc_age_sec <= 300`
     - `bootstrap.max_forward_jump_ms <= 1000`
     - `bootstrap.max_backward_jump_ms = 0`

3. **B (`workstation`) steady-state policy floor is now:**
   - at least **two authenticated sources** configured
   - at least **one `nts` source** present
   - `quorum.min_sources >= 1`
   - `quorum.max_skew_ms <= 200`
   - `quorum.require_vendor_diversity = false`
   - RTC bootstrap stays visibly bounded rather than server-tight:
     - `bootstrap.allow_rtc = true`
     - `bootstrap.max_rtc_age_sec <= 86400`
     - `bootstrap.max_forward_jump_ms <= 60000`
     - `bootstrap.max_backward_jump_ms <= 1000`

4. **C (`general_os`) steady-state policy floor is now:**
   - at least **one authenticated `nts` source** configured
   - `quorum.min_sources >= 1`
   - `quorum.max_skew_ms <= 1000`
   - `quorum.require_vendor_diversity = false`
   - explicit broader compatibility bootstrap remains allowed, but still bounded:
     - `bootstrap.allow_rtc = true`
     - `bootstrap.max_rtc_age_sec <= 604800`
     - `bootstrap.max_forward_jump_ms <= 300000`
     - `bootstrap.max_backward_jump_ms <= 5000`

5. **D (`appliance_factory`) steady-state production policy floor is now:**
   - at least **three authenticated sources** configured
   - at least **one `nts` source and one `roughtime` source** present
   - `quorum.min_sources >= 2`
   - `quorum.max_skew_ms <= 50`
   - `quorum.require_vendor_diversity = true`
   - `bootstrap.allow_rtc = false`

6. **D's signed offline-time/bootstrap story remains a separate lane, not a hidden relaxation of steady-state `time-source-policy`.**
   `offline-bounded-bootstrap-signed-time-or-authenticated-quorum` still stands, but the signed/offline token path is not represented as a quiet RTC relaxation inside the ordinary production `time-source-policy` floor.

7. **Example policies are now normative profile-floor examples.**
   The archive carries concrete examples for A/B/C/D and a guardrail that checks the floor mechanically.

## Consequences

- The product-profile trustworthy-time postures now compile to one finite implementation floor instead of an unbounded policy space.
- Fleet/factory systems no longer get to call one authenticated source "quorum enough".
- Workstations no longer inherit fleet-tight RTC/bootstrap and skew assumptions that would make normal mobility miserable.
- General-purpose systems keep explicit viability, but the fallback remains bounded and reviewable.
- Factory/regulatory environments keep the crucial distinction between steady-state production policy and separate signed offline bootstrap authority.
- `time.source.policy.diff` becomes more useful because relaxations now have a sharper baseline to compare against.

## Why this is narrow enough

This ADR does **not** settle:

- the final signed offline-time token envelope or approval ceremony
- workstation trusted-UI wording / alert cadence
- fleet-wide escalation heuristics when sources disagree for long periods
- backend/daemon choice (`chronyd`, `ntpsec`, `ntpd-rs`, etc.)

It only closes the smallest remaining implementation-shaped loophole that blocked trustworthy-time from becoming a concrete profile-aware spec surface.
