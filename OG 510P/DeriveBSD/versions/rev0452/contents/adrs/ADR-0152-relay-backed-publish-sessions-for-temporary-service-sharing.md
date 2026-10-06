# ADR-0152: Relay-backed publish sessions for temporary service sharing

- Status: Accepted
- Date: 2026-03-19

## Context

Risk 54 left one practical but expensive gap open:
DeriveBSD already makes inbound exposure brokered and profile-shaped, but it still lacked
one **blessed answer** for the common B/C workflow of "share this local service for a demo,
a webhook callback, or a short support handoff".

Without that answer, real users drift toward shadow workflows:

- reverse tunnels,
- developer SaaS relays,
- ad-hoc public listeners,
- or one-off firewall edits that never make it back into review surfaces.

Those patterns are especially dangerous because they blur together three different things:

1. the local act of listening,
2. the temporary act of publishing that local service to some remote audience,
3. and the provider-specific transport used to carry that publication.

If those stay collapsed, B and C lose their ergonomic path and quietly bypass the broker,
while A and D inherit workstation/developer tunnel folklore that should never become a
production authority model.

## Decision

1. DeriveBSD introduces a typed **`net.publish.session`** envelope for temporary,
   relay-backed publication of a local service.

2. `net.publish.session` is **not** the same thing as ordinary inbound exposure.
   The blessed publish/share path starts from a local-only service boundary
   (`loopback-only` or `broker-held-loopback`) and publishes it through an explicit relay/
   transport path.

3. `net.listen.policy`, `net.listen.grant`, and `net.listen.receipt` remain the
   authoritative lane for **durable inbound exposure** on the host/network surface.
   `net.publish.session` is a bounded session lane layered on top for temporary sharing.

4. `net.publish.session` must join four evidence classes:
   - the local listener evidence (`listen_receipt_digest`),
   - the publishing authority evidence (`consent_receipt_digest`, `policy_decision_digest`,
     `operator_session_digest`, or `support_session_digest` as appropriate),
   - the relay/transport evidence (`transport_policy_digest`, `transport_receipt_digest`),
   - and the visible/reviewable session envelope (`session_id`, endpoint hints, expiry, notes).

5. `net-listen-receipt` stays **summary-shaped**.
   It records what was exposed and how, not every later connection or tunnel transcript.
   Per-connection detail belongs in service logs, diagnostics, or support bundles when needed,
   not in the baseline exposure receipt.

6. Product-shape posture is fixed as follows:
   - **B (`workstation`)**: relay-backed publish sessions are an allowed ergonomic lane,
     but they must be trusted-UI-visible, leased, and revocable.
   - **C (`general_os`)**: relay-backed publish sessions are also allowed, including
     explicit admin/developer flows, but they stay bounded and receipted instead of ambient.
   - **A (`fleet_host`)**: relay-backed publish sessions are not the normal service-publication
     model; use them only for exceptional support/breakglass style workflows.
   - **D (`appliance_factory`)**: relay-backed publish sessions are out of bounds for shipped/
     production posture; any maintenance/lab use must stay explicit and non-default.

7. Relay providers remain **adapter territory**.
   DeriveBSD standardizes the contract (`net.publish.session` + `transport.*` evidence),
   not a specific vendor tunnel protocol or hosted service.

## Consequences

- B/C gain a coherent way to do demos, webhook testing, and temporary sharing without opening
  public listeners or normalizing shadow tunnels.
- A/D keep their stricter ingress model instead of quietly inheriting developer tunnel habits.
- The archive now has one answer to "was this public service a durable published endpoint or a
  short-lived share session?".
- Transport/provider choices remain killable adapters governed by `transport.policy` rather than
  hard-coded platform authority.

## Why this is narrow enough

This ADR does **not** pick a provider, a tunnel protocol, or a hosted relay product.
It only fixes the archive-level boundary:

- temporary service sharing is relay-backed and receipted,
- durable non-loopback exposure remains the listen-broker lane,
- baseline exposure receipts stay summary-shaped,
- and B/C ergonomics do not become A/D production defaults.
