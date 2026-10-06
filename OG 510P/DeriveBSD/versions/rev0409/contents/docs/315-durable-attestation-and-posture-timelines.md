# Durable attestation + posture timelines (turn attestation into audit, not a point-in-time check)

Many attestation deployments behave like a *spot check*:
- a verifier asks for evidence
- it returns “pass/fail”
- the system forgets almost everything

That is not how real incident response works.
What teams want in practice is **retroactive audit**:
- *when did posture change?*
- *what did the verifier see?*
- *what did we allow based on that posture?*

Keylime has popularized the idea of **durable attestation**: keeping attestation results as a time series so security becomes auditable, not ephemeral.

This doc explains how to bake that shape into DeriveBSD using objects we already have.

Related:
- Evidence + reference + receipts: `docs/226-platform-posture-and-attestation-results-as-evidence.md`
- Measured boot ergonomics: `docs/313-boot-manifests-and-eventlog-replay.md`
- Attester lifecycle: `docs/314-attester-provisioning-and-key-lifecycle-receipts.md`
- Event journal + segments: `docs/215-structured-event-log-as-evidence.md`, `spec/event.segment.schema.json`
- Export governance: `docs/251-export-policies-and-support-bundle-portal.md`

## The core idea

Treat posture as a **timeline** that can be queried and bundled:

- inputs: `boot.attestation`, runtime measurement evidence (optional)
- reference: `attestation.reference`
- output: `attestation.receipt`

Instead of only keeping “latest”, retain a bounded chain.

## Minimal mechanics (day 0)

### 1) Chain attestation receipts

Add an optional timeline link to `attestation.receipt`:
- `timeline.chain_id` (e.g., host-id + reference scope)
- `timeline.seq` (monotonic counter)
- `timeline.prev_receipt_digest`

This makes “receipt deletion” detectable *within the local evidence store*, even without a public transparency log.

### 2) Emit typed events for transitions

When a new receipt arrives:
- write an `attestation-event` into the structured journal
- include coarse reason codes
- update the “current posture snapshot” pointer for the host
- keep identity provenance digest-bound too, so timeline queries can explain AK rotation or motherboard replacement by following the joined `attester.provision.receipt` rather than a registrar side table

This lets ops ask: “show me the posture transitions around this incident id”.

### 3) Retention is budgeted

Durability can become privacy-toxic if we keep everything forever.
So durable attestation must respect the existing posture/evidence budgets:
- keep only N receipts or T days by default
- allow policy to retain more for high-assurance hosts
- export only through explicit bundle plans and export policy

## Why this is a greenfield-worthy ecosystem feature

Durable attestation unlocks workflows that otherwise require bespoke vendor platforms:
- “What did the verifier think right before the outage?”
- “Did we silently start accepting a weaker reference policy?”
- “Which secret grants were issued while posture was degraded?”

It also composes naturally with DeriveBSD’s evidence spine:
- receipts can be referenced by change receipts
- receipts can be attached to incident bundles
- receipts can be monitored by witness/monitor lanes

## Non-goals (v1)

- making the receipt chain globally auditable by default (optional transparency log integration can come later)
- forcing a single verifier implementation

References (context only):
- Keylime measured boot workflow + replay model: https://keylime.readthedocs.io/en/latest/user_guide/use_measured_boot.html
- “Durable attestation” framing: https://next.redhat.com/2023/04/25/keylimes-durable-attestation-makes-security-auditable/

Last updated: 2026-03-21r374
