# Publish-session end conditions and no-auto-resume posture boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

`net.publish.session` already says temporary sharing stays local-first, relay-backed,
and audience-explicit.
The remaining ambiguity is about lifetime:

> does a temporary publish session end when the initiating context ends,
> or can it quietly come back after restart because some daemon or config remembered it?

If the archive leaves that implicit, “temporary share” degrades into restart-persistent tunnel folklore.
See `adrs/ADR-0154-publish-session-end-conditions-and-no-auto-resume-posture.md`.

## The hard decision

A relay-backed publish session must carry explicit end conditions,
and it must not auto-resume.

That posture now lives in `net.publish.session.lifecycle` and records:

- `end_conditions` — the conditions that automatically terminate the share
- `resume_policy` — what must happen after interruption or restart
- `post_end_access_posture` — what stale copied/share handles are allowed to do after the share is over
- `post_end_management_return_posture` — what a surviving trusted-UI return path or management deep link is allowed to do if followed after the share is over

Today the archive keeps that answer deliberately small but explicit:
`resume_policy = new-session-with-fresh-authority`, `post_end_access_posture = explicit-ended-or-fresh-share`, `post_end_management_return_posture = exact-ended-state-if-followed`, and `terminal_end_condition` whenever `ended_at` is present.`
A later share may be recreated, but it must produce a **new** `net.publish.session`
with fresh authority evidence instead of silently reusing the old one. Material outward surface change now also means a new session with a new `session_id` and fresh `authority.lease_id` instead of silently repointing the old bounded share; see `docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md`. And once the old share ends, a copied URL, browser-history entry, or remembered relay handle must either resolve as explicitly ended/expired/revoked or force a fresh share instead of dropping into a generic launcher or successor session; see `docs/598-publish-session-post-end-access-stays-fail-closed.md`. That explicit ended state should also preserve the exact bounded end-condition class through `lifecycle.terminal_end_condition` rather than flattening lease expiry, manual revoke, local-service loss, session end, or host reboot into one generic terminal label; see `docs/603-publish-session-ended-states-stay-terminal-cause-exact.md`. It also should not reappear under a remembered public hostname or reserved relay domain as if the name itself were durable authority.

## Required end conditions

Every publish session must now include:

- `lease-expiry`
- `manual-revoke`
- `local-service-unavailable`
- `host-reboot`

So even the most permissive B/C temporary share is still:

- time-bounded,
- explicitly revocable,
- tied to the local service still existing,
- and reboot-cleared.

## Authority-bound end conditions

The authority lane that created the share also adds a required ending:

- `trusted-ui` → `initiating-user-session-end`
- `support-session` → `support-session-end`
- `operator-session` → `operator-session-end`
- `maintenance` → `maintenance-window-end`

This keeps the share aligned with the bounded authority context that justified it. The reserved `maintenance` lane now also stays digest-empty with respect to the existing consent/policy/operator/support joins, so `maintenance-window-end` does not quietly sit on top of borrowed placeholder evidence; see `docs/590-publish-session-maintenance-triggers-stay-digest-empty.md`.
A support-session share should not outlive the support session, and ADR-0159 now requires that share to carry the exact `authority.support_session_digest` instead of leaving the support context implicit.
A workstation preview started from a trusted UI should not survive logout and come back later as a stealth background endpoint.

## Product-shape posture

### A — fleet host

Temporary publish sessions remain exceptional.
They must still be reboot-cleared and fresh-authority-only.
Anything expected to survive restart belongs on the durable `net.listen.*` lane.

### B — workstation

The ergonomic share path stays relay-backed,
but the share is now clearly **session-shaped**:
visible, revocable, reboot-cleared, and unable to auto-resume from remembered relay config.
That is the line that stops “share this preview” from turning into an always-on tunnel habit, even if someone wants to keep reusing a non-`session-scoped` public hostname.

### C — general OS

The same default applies.
Admin/developer compatibility flows may still publish temporarily,
but durable publication must graduate onto brokered ingress instead of hiding inside relay persistence knobs.

### D — appliance factory / regulatory

Shipped posture remains off restart-persistent temporary sharing.
Lab and maintenance publish sessions, if used at all, remain exceptional, bounded, and reboot-cleared.

## Why this matters for coherence

Current relay ecosystems make both temporary testing flows and persistent service publication easy.
That is useful, but it is exactly why DeriveBSD needs the boundary in the evidence model itself.
Without it, the archive would say “temporary” while implementations quietly inherit daemon/service persistence semantics from provider tooling.

By naming end conditions directly, forcing fresh-authority recreation, and keeping stale share handles fail-closed after end, `net.publish.session` becomes concrete enough for trusted UI, support bundles, policy review, and implementation without having to standardize a specific relay vendor.

## Related docs

- `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md`
- `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md`
- `docs/286-inbound-listen-broker-and-firewall-leases.md`
- `docs/460-inbound-listen-posture-by-profile.md`
- `docs/249-lease-registry-and-cross-lane-revocation.md`

Last updated: 2026-03-20r334

For the canonical current-stack map over the recent `docs/593-*` through `docs/603-*` tightening cluster, see `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full companion list.

## Related

- `docs/602-publish-session-post-end-management-return-stays-lease-exact-ended.md`

- `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md`
