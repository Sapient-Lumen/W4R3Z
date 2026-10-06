# Trustworthy-time posture by profile

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, supply-chain, operability  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt  

DeriveBSD already models secure time as evidence.
What this doc decides is narrower and more important for coherence:
**what is the default trustworthy-time posture in each product shape?**

This is intentionally **not** a daemon-selection doc.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0058-trustworthy-time-posture-by-profile.md`
- time discipline as evidence: `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`
- LKGT / authenticated time lane: `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`
- practical backends: `docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`
- time-source drift review: `docs/438-time-source-policy-diff-as-review-surface.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

Every system that avoids deciding its time-authority posture ends up deciding it through drift:

- expiry-sensitive checks get waived during incidents,
- offline sites quietly normalize “just set the clock somehow”,
- workstation UX hides degraded time until updates or certificates fail mysteriously,
- and compatibility environments silently redefine the security baseline for stricter product shapes.

DeriveBSD already says evidence, freshness, attestation, and rollback windows matter.
That only means anything if the archive fixes the **default authority model for time** instead of leaving it to daemon defaults and human memory.

## Product-shape defaults

| Profile | `time_authority` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `authenticated-quorum-lkgt-required-noninteractive` | Authenticated time with LKGT monotonicity is the default for expiry-sensitive gates; degraded state is receipted, not interactively waived. |
| B (`workstation`) | `authenticated-preferred-visible-degraded-state-sensitive-ops-gated` | Authenticated time is preferred; degraded time is visible in trusted UI; sensitive actions gate or ask for repair instead of silently trusting weak time. |
| C (`general_os`) | `authenticated-preferred-explicit-fallback` | Authenticated time stays preferred, but manual/legacy fallback remains an explicit compatibility lane. |
| D (`appliance_factory`) | `offline-bounded-bootstrap-signed-time-or-authenticated-quorum` | Offline/bootstrap time must be bounded and evidentiary: signed/operator time tokens or authenticated quorum, not “ignore time because airgap”. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## Cross-profile invariants

Regardless of profile:

- expiry/freshness-sensitive operations do not silently downgrade to ambient unauthenticated time
- degraded time is visible in receipts and monitor surfaces
- LKGT monotonicity remains part of the anti-rollback story whenever trustworthy time gates are in scope
- offline/bootstrap allowances are bounded and explicit rather than hidden operator folklore
- time-source posture changes remain reviewable through signed policy + diff surfaces

## What this fixes by profile

### A) Secure fleet host (`fleet_host`)

Default: `authenticated-quorum-lkgt-required-noninteractive`

- Fleet hosts treat secure time as a control-plane dependency, not an advisory nicety.
- Authenticated/quorum posture and LKGT are part of the default gating story for expiry-sensitive operations.
- If the host is degraded, that fact is receipted and policy-derived rather than resolved through click-through prompts.

### B) Secure workstation (`workstation`)

Default: `authenticated-preferred-visible-degraded-state-sensitive-ops-gated`

- The user should be able to tell when time trust is degraded.
- Sensitive actions (updates, signature/expiry-sensitive admin flows, some key operations) should gate or ask for repair rather than silently proceeding on weak time.
- This keeps “your clock is wrong” from becoming a forensic mystery or a silent security bypass.

### C) General-purpose OS (`general_os`)

Default: `authenticated-preferred-explicit-fallback`

- Authenticated time remains the preferred Derive-managed path.
- Compatibility/manual fallback stays explicit and reviewable.
- General OS can remain viable on messy networks and old habits without silently weakening the stricter A/B/D defaults.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `offline-bounded-bootstrap-signed-time-or-authenticated-quorum`

- Offline/bootstrap time is part of the product story, not an exception hidden in runbooks.
- Signed time tokens, authenticated local quorum, or similarly bounded authority lanes are acceptable; ambient Internet dependency is not required.
- “Ignore expiry during offline maintenance” is not an acceptable default.

## What this does *not* decide

Still open:

- exact quorum/min-source/skew defaults by class
- the final signed offline-time token envelope and approval flow
- how much RTC drift is tolerated before forcing operator repair
- workstation UI wording, alert cadence, and how aggressive sensitive-op gating should be
- monitor/escalation behavior when sources disagree or disappear for long periods

That work stays implementation-level.
This doc only fixes the product-default boundary so the archive can keep converging without drifting.

## Design cue from current systems

A few lessons are stable:

- NTS is the boring modern baseline for authenticated NTP client/server time.
- Roughtime is useful as a fast authenticated sanity oracle and for misbehavior evidence, not necessarily as a full replacement for NTP discipline.
- Operationally, offline and unstable environments still need an explicit time story or expiry/freshness checks collapse into “temporarily ignore security.”

DeriveBSD should steal those lessons, not inherit ambient unauthenticated time folklore.

Last updated: 2026-03-06r197
