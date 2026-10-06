# ADR-0058: Trustworthy-time posture by profile

- **Status:** Accepted
- **Date:** 2026-03-06

## Context

DeriveBSD already has a serious **trustworthy-time lane** on paper:
`docs/142-trustworthy-time-roughtime.md` makes LKGT a real anti-rollback primitive,
`docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md` treats time discipline as evidence,
`docs/283-trustworthy-time-nts-roughtime-and-lkgt.md` defines the policy objects,
and `docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md` sketches practical BSD-friendly backends.

What the archive still lacked was the **product-shape default** for time authority.
Without that, different deployments quietly normalize incompatible and unsafe habits:

- A quietly falls back to unauthenticated time during incidents until expiry checks become ceremonial.
- B cannot tell whether degraded time is a background detail or a user-visible reason to pause sensitive actions.
- C cannot tell whether manual/legacy fallback is an accepted compatibility lane or an unreviewed drift path.
- D risks air-gapped or regulated workflows bypassing freshness/expiry entirely because offline bootstrap was never bounded as a product decision.

We do **not** need to choose one daemon, one NTS provider, or one monitor implementation here.
We do need a stable, checkable answer to:

- when authenticated time is required vs merely preferred,
- where LKGT monotonicity is part of the default security posture,
- how degraded or offline bootstrap is surfaced,
- and which product shapes are allowed explicit compatibility fallback instead of silently weakening expiry-sensitive gates.

## Decision

We define trustworthy-time posture as a **profile-shaped default** and thread it into `spec/examples/product.profiles.json` under the stable `time_authority` knob.

Cross-profile guardrail:
- expiry/freshness-sensitive operations must never silently downgrade to ambient unauthenticated time,
- degraded time must be visible in receipts and, where humans exist, visible in trusted UX,
- LKGT monotonicity remains part of the default anti-rollback story whenever a profile depends on trustworthy time for gates,
- and offline/bootstrap allowances must be bounded and explicit rather than ad-hoc operator folklore.

### A) `fleet_host`

Default posture: `authenticated-quorum-lkgt-required-noninteractive`

- Fleet hosts require authenticated time for expiry-sensitive gates by default.
- Quorum/LKGT posture is part of the normal control-plane story, not an optional hardening mode.
- Degraded state is non-interactive and receipted rather than solved by interactive prompt-clicking.

### B) `workstation`

Default posture: `authenticated-preferred-visible-degraded-state-sensitive-ops-gated`

- Workstations prefer authenticated time by default.
- Degraded time must be visible in the trusted UI.
- Expiry-sensitive actions should gate, explain, or ask for repair rather than silently trusting ambient unauthenticated time.

### C) `general_os`

Default posture: `authenticated-preferred-explicit-fallback`

- Authenticated time remains the preferred Derive-managed path.
- Legacy/manual/compatibility fallback may exist only as an explicit, reviewable lane.
- Compatibility fallback must not silently redefine stricter A/B/D defaults.

### D) `appliance_factory`

Default posture: `offline-bounded-bootstrap-signed-time-or-authenticated-quorum`

- Factory/regulatory shapes must support bounded offline bootstrap instead of assuming live Internet time.
- Signed/operator-provided time tokens or authenticated quorum are acceptable authority lanes when policy allows.
- “Ignore time because the site is offline” is out of bounds as a default operational story.

## Consequences

- Product profiles now carry a stable `time_authority` default.
- `tools/check_product_profiles.py` must enforce this boundary so the archive cannot silently drift back toward unauthenticated incident-time folklore, invisible degraded workstation state, or unbounded offline-time bypass in regulated/factory lanes.
- Risk item 16 narrows from a product-default question to implementation detail: exact quorum values, signed-time token format, RTC bounds, UI/alert semantics, and monitor behavior.

## Non-goals

- Choosing one chrony/ntpsec/ntpd-rs implementation path.
- Freezing exact quorum numbers, skew tolerances, or alert thresholds.
- Defining the final signed offline-time token envelope or operator workflow here.
