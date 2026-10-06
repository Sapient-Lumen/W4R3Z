# Time-source policy profile floors stay finite and profile-mapped

**Tier:** A (Core)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt

`docs/468-trustworthy-time-posture-by-profile.md` already fixed the product-level trustworthy-time posture.
`docs/702-time-requirement-degraded-response-stays-explicit-and-proof-bundle-bound.md` then fixed what reviewed workflows may do when time is degraded.

This page closes the remaining implementation seam:

> what concrete `time-source-policy` floor does each product shape compile to?

DeriveBSD now treats that answer as a **finite profile-mapped floor**, not as per-deployment folklore.

See also:
- ADR: `adrs/ADR-0312-time-source-policy-profile-floors-stay-finite-and-profile-mapped.md`
- profile defaults: `docs/468-trustworthy-time-posture-by-profile.md`
- backend wiring: `docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`
- LKGT / proof-bundle lane: `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`
- drift review surface: `docs/438-time-source-policy-diff-as-review-surface.md`
- schema: `spec/time.source.policy.schema.json`
- examples:
  - `spec/examples/time.source.policy.fleet_host.json`
  - `spec/examples/time.source.policy.workstation.json`
  - `spec/examples/time.source.policy.general_os.json`
  - `spec/examples/time.source.policy.appliance_factory.json`

## Accepted boundary

### 1) The floor is on `time-source-policy`, not hidden in daemon defaults

The reviewed source set, quorum, and bootstrap posture live on signed `time-source-policy` objects.
Daemon choice still matters operationally, but it is not where A/B/C/D policy truth lives.

### 2) A (`fleet_host`) and steady-state D (`appliance_factory`) now require authenticated mixed-source quorum

For A and for D's **connected steady-state production policy**:

- configure at least **three authenticated sources**
- include at least **one `nts` source and one `roughtime` source**
- require `quorum.min_sources >= 2`
- require `quorum.max_skew_ms <= 50`
- require `quorum.require_vendor_diversity = true`

This is the archive's concrete answer to "when does Roughtime stop being optional?"
It is mandatory in the stricter fleet/factory floors because it provides a second authenticated shape for sanity checking and misbehavior evidence instead of leaving all trust concentrated in one NTS path.

### 3) B (`workstation`) now gets a mobility-shaped authenticated floor

For B:

- configure at least **two authenticated sources**
- include at least **one `nts` source**
- require `quorum.min_sources >= 1`
- require `quorum.max_skew_ms <= 200`
- keep `quorum.require_vendor_diversity = false`

This avoids importing fleet/factory brittleness into laptops and intermittently connected devices while still making authenticated time the normal reviewed path.
When only one source is reachable, the workstation can still be `synced`; when multiple sources disagree, reviewed degraded-time policy still decides what sensitive operations may do.

### 4) C (`general_os`) keeps viability explicit, but bounded

For C:

- configure at least **one authenticated `nts` source**
- require `quorum.min_sources >= 1`
- require `quorum.max_skew_ms <= 1000`
- keep `quorum.require_vendor_diversity = false`

This is not a "trust whatever time you got" posture.
It is the smallest authenticated reviewed floor that keeps broad compatibility viable without pretending C should inherit the same assumptions as A or D.

### 5) RTC bootstrap posture is now profile-shaped too

#### A (`fleet_host`)

- `bootstrap.allow_rtc = true`
- `bootstrap.max_rtc_age_sec <= 300`
- `bootstrap.max_forward_jump_ms <= 1000`
- `bootstrap.max_backward_jump_ms = 0`

A may use RTC only as a narrow bridge into authenticated time; it does not get a broad convenience bootstrap lane.

#### B (`workstation`)

- `bootstrap.allow_rtc = true`
- `bootstrap.max_rtc_age_sec <= 86400`
- `bootstrap.max_forward_jump_ms <= 60000`
- `bootstrap.max_backward_jump_ms <= 1000`

B needs a real mobility/suspend/resume story, but it still keeps the bridge bounded and reviewable.

#### C (`general_os`)

- `bootstrap.allow_rtc = true`
- `bootstrap.max_rtc_age_sec <= 604800`
- `bootstrap.max_forward_jump_ms <= 300000`
- `bootstrap.max_backward_jump_ms <= 5000`

C keeps explicit broader compatibility, but the bounds still exist and can still be diffed/gated.

#### D (`appliance_factory`)

- `bootstrap.allow_rtc = false`

For D, the ordinary production `time-source-policy` must not silently turn RTC into the real authority.
If D needs offline bootstrap, that remains a **separate signed-time / approved maintenance lane**, not a quiet weakening of the steady-state production floor.

### 6) Signed offline time is separate from steady-state production policy

This is the hardest small cut in this page.
D already allowed `offline-bounded-bootstrap-signed-time-or-authenticated-quorum` at the product level.
The archive now makes that precise:

- the **steady-state production** `time-source-policy` floor stays strict and RTC-free
- the **offline signed-time bootstrap** story is separate, explicitly approved, and remains outside the ordinary connected `time-source-policy` example

That keeps factory/regulatory systems from laundering an emergency/bootstrap allowance into their ambient production baseline.

## Profile floor table

| Profile | Minimum configured authenticated sources | Required protocol mix | `min_sources` floor | `max_skew_ms` ceiling | `require_vendor_diversity` | RTC bootstrap floor |
|---|---:|---|---:|---:|---|---|
| A (`fleet_host`) | 3 | at least 1 `nts` + 1 `roughtime` | 2 | 50 | true | allowed, `max_rtc_age_sec <= 300`, `max_forward_jump_ms <= 1000`, `max_backward_jump_ms = 0` |
| B (`workstation`) | 2 | at least 1 `nts` | 1 | 200 | false | allowed, `max_rtc_age_sec <= 86400`, `max_forward_jump_ms <= 60000`, `max_backward_jump_ms <= 1000` |
| C (`general_os`) | 1 | at least 1 `nts` | 1 | 1000 | false | allowed, `max_rtc_age_sec <= 604800`, `max_forward_jump_ms <= 300000`, `max_backward_jump_ms <= 5000` |
| D (`appliance_factory`) | 3 | at least 1 `nts` + 1 `roughtime` | 2 | 50 | true | steady-state production policy keeps `allow_rtc = false` |

## Why these numbers are worth fixing

- NTS stays the boring authenticated client/server time baseline rather than a custom DeriveBSD protocol.
- chrony remains a practical BSD-first implementation anchor for that lane.
- Roughtime remains useful as an authenticated sanity/misbehavior-evidence companion instead of a full NTP/NTS replacement.

The exact numbers are conservative enough to be reviewable and strict enough to stop the archive from calling any authenticated source set "good enough" by mood.

## What this page does not decide

Still open:

- the exact signed offline-time token envelope and approval flow
- workstation trusted-UI wording / alert cadence
- fleet-wide monitor/escalation behavior when authenticated sources disagree for long periods
- backend implementation choice and packaging details

Those stay implementation-level.
This page only fixes the concrete profile-aware `time-source-policy` floor.

## Related docs

- `adrs/ADR-0312-time-source-policy-profile-floors-stay-finite-and-profile-mapped.md`
- `docs/468-trustworthy-time-posture-by-profile.md`
- `docs/702-time-requirement-degraded-response-stays-explicit-and-proof-bundle-bound.md`
- `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`
- `docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`
- `docs/438-time-source-policy-diff-as-review-surface.md`
- `docs/308-time-monitors-and-lie-detection.md`
- `spec/time.source.policy.schema.json`
- `spec/examples/time.source.policy.fleet_host.json`
- `spec/examples/time.source.policy.workstation.json`
- `spec/examples/time.source.policy.general_os.json`
- `spec/examples/time.source.policy.appliance_factory.json`

Last updated: 2026-03-23r453
