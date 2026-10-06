# Support-bundle contract and timeline-first handoff

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, reproducibility, isolation  
**Patterns:** Plan→Apply→Receipt, Capsule, Bundles compose drift surfaces  

DeriveBSD already has incident bundles, timelines, bundle plans, payload manifests, and build receipts.
What this doc decides is narrower and more useful for implementation:
**what is the official support handoff contract, and what must be present for a bundle to count as explainable instead of “some bytes we zipped up”?**

This is intentionally **not** a full collector or UI spec.
It is a small contract decision.

See also:
- ADR: `adrs/ADR-0071-support-bundle-contract-and-timeline-first-handoff.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- incident timelines: `docs/419-incident-timelines-as-derived-artifacts.md`
- bundle plans and deterministic exports: `docs/253-bundle-plans-and-deterministic-exports.md`
- evidence spine: `docs/229-evidence-spine-overview.md`
- export boundary posture: `docs/466-export-boundary-posture-by-profile.md`
- typed safe-open intake profile: `docs/502-support-bundle-intake-typed-plan-and-receipt-shapes.md`

## Why this needs a hard decision

Most systems eventually have all the right pieces somewhere:
logs, crash reports, support bundles, ticket uploads, and human incident notes.
The pain comes from the missing contract between those pieces.

Without an official handoff contract:

- a support bundle can exist without a human-readable orientation surface,
- a timeline can exist without being attached to the bytes support actually sees,
- selection/redaction can happen without a stable plan object,
- and payload bytes can travel without a deterministic member listing.

DeriveBSD already has enough structure to stop treating this as folklore.
The archive should say, explicitly, what a real support handoff contains.

## The official support handoff contract

A support handoff is a small bundle of typed evidence objects.
The canonical set is:

1. **`incident.timeline`** — the one-page human orientation surface.
2. **`incident.bundle`** — the metadata envelope for trigger, host, scope, included evidence, and payload.
3. **`bundle.plan`** — the deterministic selection + redaction/export-transform plan.
4. **`bundle.payload.manifest`** — the stable member listing for the produced payload bytes.
5. **`bundle.build.receipt`** — the plan→bytes binding for the payload that was built.

If the bundle is actually shared outside the trust boundary, add:

6. **`export.receipt`** — what was exported under which policy.
7. optional `consent.receipt`, `transport.receipt`, and `export.transparency.entry` digests when the lane provides them.

When packet troubleshooting escalates to stronger `packet.capture.normalized` export, the bundle contract stays digest-first: the stronger chain must carry typed `transport.receipt` evidence and may not count a local `file` destination as completed handoff (`docs/516-packet-capture-strong-export-transport-boundary.md`). Final stronger handoff now also requires typed `transport.acceptance.receipt` evidence, so the archive can distinguish “sent” from `recipient-accepted` (`docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md`). That recipient-side closure is now digest-confirming too, so `acceptance.remote_artifact_digest` must echo the same normalized artifact rather than merely a visible attachment handle (`docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md`). The same stronger chain is now remote-object-continuous too, so `transport.receipt.result.remote_id`, `transport.acceptance.receipt.acceptance.remote_reference`, and `export.receipt.adapter.remote_id` stay on the same remote object id instead of drifting across multiple ticket attachments (`docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`). The same stronger chain is now remote-validator-continuous too, so `transport.receipt.result.remote_validator`, `transport.acceptance.receipt.acceptance.remote_validator`, and `export.receipt.adapter.remote_validator` stay on the same remote validator instead of collapsing the stronger handoff back to object id alone (`docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md`). The same stronger chain is now remote-protection-shaped too, so `transport.acceptance.receipt.acceptance.remote_protection` and `export.receipt.adapter.remote_protection` stay on the same remote protection posture instead of calling any accepted upload durable evidence by implication (`docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md`). The same stronger chain is now remote-locator-continuous too, so `transport.receipt.result.remote_locator`, `transport.acceptance.receipt.acceptance.remote_locator`, and `export.receipt.adapter.remote_locator` stay on the same remote locator instead of leaving later evidence retrieval to portal folklore (`docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md`). Later support/regulatory follow-up now also uses typed `transport.reverification.receipt` metadata-only reverification, so the same accepted remote validator / protection posture / locator can be re-checked with `body_downloaded = false` instead of another packet-body download or portal screenshots (`docs/525-packet-capture-strong-export-remote-reverification-boundary.md`). The same stronger chain is now destination-bound too, so the approved case/recipient tuple cannot silently drift between approval and the eventual external handoff (`docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md`).

This is a **contract**, not a giant subsystem.
If tooling cannot yet build every piece automatically, these are still the objects the design is aiming to emit.

## Canonical payload format

The canonical payload format for official support bundles is **`tar.zst`**.

Why:

- it matches the archive’s existing deterministic-export posture,
- it keeps member order and compression policy explicit in one lane,
- and it avoids quietly redefining the support contract around whatever GUI tool happens to speak `zip` best.

`zip` remains allowed as a **compatibility adapter** for recipients or ticket systems that require it.
That path is real, but it is not the canonical contract.

## Timeline-first by default

The incident timeline is the default **one-page orientation surface** for a support bundle.

That means:

- official bundle plans should include a timeline by default,
- `incident.bundle` should carry the timeline digest when present,
- `bundle.build.receipt` should bind the timeline digest along with the payload and bundle metadata,
- and the payload manifest should normally include the timeline member alongside `incident.bundle` metadata.

The intent is simple: the first thing a responder opens should be the story, not a directory listing.

Packet-capture evidence follows the same instinct: the official handoff can carry `packet.capture.session` / `packet.capture.summary` digests and, when stronger imported artifacts were involved, the matching packet-capture import/redaction receipt digests. Raw packet bytes remain a stronger separate export action rather than a default bundle member, and proof-bound stronger exports now use typed `supporting_evidence` joins back to that packet-capture chain (`docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md`, `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`). When those stronger packet bytes do leave the system, the action also needs explicit consent evidence rather than a background uploader path (`docs/515-packet-capture-strong-export-approval-evidence-boundary.md`).

Trust-view activation now follows the same rule too: official handoff may carry the canonical `pki_trust_bundle_digest`, the matching `pki_trust_bundle_apply_receipt_digests` when trust-view activation changed or matters to the incident, and `pki_issue_receipt_digests` when responders need exact PKI issuance / renewal / install / revoke proof. That keeps reviewed trust roots, exact served trust-view proof, and exact PKI issuance / renewal / install / revoke proof on the typed bundle contract instead of pushing support back toward renderer-specific trust dumps, CA dashboards, ACME logs, or control-plane folklore (`docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md`, `docs/624-incident-bundles-carry-trust-bundle-apply-proof-by-digest.md`, `docs/638-incident-bundles-carry-pki-issuance-proof-by-digest.md`).

Storage integrity now follows the same rule too: official handoff may carry `storage_pool_inventory_digest`, `storage_health_snapshot_digest`, and `storage_scrub_receipt_digests` when degraded pools, repaired corruption, or integrity-verification outcomes changed or matter to the incident story. That keeps bounded pool posture, current storage-health state, and exact scrub / repair proof on the typed bundle contract instead of pushing support back toward `zpool status` transcripts, dashboard screenshots, or ticket prose (`docs/225-storage-health-and-scrubbing-as-evidence.md`, `docs/635-incident-bundles-carry-storage-scrub-proof-by-digest.md`).

Remote-assistance participation now follows the same rule too: official handoff may carry `support_session_digests` when brokered helper sessions changed or matter to the incident story. That keeps support-session proof on the typed bundle contract instead of pushing support back toward helper dashboards, ticket notes, or chat archaeology (`docs/291-remote-assistance-sessions-as-evidence.md`, `docs/627-incident-bundles-carry-support-session-proof-by-digest.md`).

Temporary-authority context now follows the same rule too: official handoff may carry `lease_snapshot_digest` when responders need one typed answer to what temporary authority was still live at capture time. That keeps live-authority context on the typed bundle contract instead of pushing support back toward bastion dashboards, control-plane screenshots, operator memory, or chat archaeology (`docs/249-lease-registry-and-cross-lane-revocation.md`, `docs/252-lease-envelope-and-cross-lane-joins.md`, `docs/636-incident-bundles-carry-lease-snapshot-authority-context-by-digest.md`).

Secret state/action proof now follows the same rule too: official handoff may carry `secret_snapshot_digest` and `secret_receipt_digests` when responders need one typed answer about safe current credential posture and which exact secret actions materially participated. That keeps secret-state/action proof on the typed bundle contract instead of pushing support back toward provider dashboards, ticket notes, or screenshots (`docs/223-secrets-and-key-management-as-evidence.md`, `docs/637-incident-bundles-carry-secret-state-and-action-proof-by-digest.md`).

Measured-posture proof now follows the same rule too: official handoff may carry `boot_attestation_digest`, `attestation_reference_digest`, and `attestation_receipt_digests` when responders need one typed answer about what exact measured-boot evidence the host produced, what verifier/reference scope judged it, and what verifier judgments materially participated. That keeps measured posture on the typed bundle contract instead of pushing support back toward verifier dashboards, portal screenshots, or ticket prose (`docs/226-platform-posture-and-attestation-results-as-evidence.md`, `docs/639-incident-bundles-carry-attestation-proof-by-digest.md`).

## Safe-open intake path

The handoff contract now has a matching intake rule:
foreign support bundles should enter through the safe-open intake path (`content.import.plan` / `content.import.receipt`) and preview timeline-first metadata in a disposable no-network compartment before deeper payload inspection. This is the official timeline-first preview posture for foreign support bundles.
The **typed support-bundle intake shapes** are now pinned by `spec/content.import.support-bundle.plan.schema.json` and `spec/content.import.support-bundle.receipt.schema.json`, and they stay constrained profiles of the **generic `content.import.*` lane** rather than a second import subsystem.
`zip` remains a compatibility adapter for external systems that require it, but canonical intake stays aligned to the generic lane and the canonical `tar.zst` handoff.
That keeps the handoff objects as foreign evidence, not ambient host authority.
See `docs/498-safe-open-support-bundle-intake-and-repro-boundary.md` and `docs/502-support-bundle-intake-typed-plan-and-receipt-shapes.md`.

## Redaction and dump posture

The default support-handoff posture is **metadata-first**.

- structured snapshots, event segments, event-seal receipt digests when continuity proof matters, timelines, policy decisions, and receipts are the baseline,
- raw coredumps / kernel dumps / memory-heavy captures remain **off by default**,
- and any expansion into dump-heavy bundles must be explicit in `bundle.plan` and visible in `bundle.build.receipt` / export receipts.

This keeps support bundles useful without turning them into ambient secret harvesters.

## Minimal invariants

A bundle that claims to be an official support handoff should satisfy these invariants:

- the selection + transform logic is represented by `bundle.plan`
- the produced bytes are bound by `bundle.build.receipt`
- the payload members are explained by `bundle.payload.manifest`
- the human orientation surface is `incident.timeline`
- bounded `event_segments` stay separate from `event_seal_receipt_digests`, so support handoff can say both which window is in scope and what exact seal proof covered it
- `boot_bless_receipt_digests` give official support handoff a typed place for boot-assessment/finalization proof, so the bundle can say which exact `boot.bless.receipt` participated when health-gated finalization or rollback mattered
- trustworthy-time action proof stays distinct too: `time_source_inventory_digest` captures source posture, `time_sync_snapshot_digest` captures current sync state, and `time_sync_receipt_digests` say which exact `time.sync.receipt` participated when clock correction, source failover, or degraded sync mattered
- storage integrity proof stays distinct too: `storage_pool_inventory_digest` captures bounded pool posture, `storage_health_snapshot_digest` captures current health state, and `storage_scrub_receipt_digests` say which exact `storage.scrub.receipt` participated when integrity verification, repair, or degraded-pool recovery mattered
- temporary-authority context proof stays distinct too: `lease_snapshot_digest` captures what temporary authority was still live at capture time, instead of making support infer it from side dashboards or operator memory
- secret-state/action proof stays distinct too: `secret_snapshot_digest` captures safe current secret posture while `secret_receipt_digests` say which exact secret actions materially participated, instead of making support infer the story from provider dashboards, ticket notes, or screenshots
- measured-posture proof stays distinct too: `boot_attestation_digest` captures the exact measured-boot evidence, `attestation_reference_digest` captures the verifier/reference scope, and `attestation_receipt_digests` capture the exact verifier judgments, instead of making support infer the story from verifier dashboards, portal screenshots, or ticket prose
- metadata and payload are linked by digest, not filenames or shell logs
- crossing a trust boundary goes through `export.policy` / `export.receipt`, not “scp the tarball” folklore

## What this fixes

### A) Fleet host

- Rollback and health-gate incidents gain a stable handoff artifact instead of a bag of local logs.
- Timelines become part of the normal operational evidence story, not a postmortem afterthought.

### B) Workstation

- A user-visible support flow can show the timeline and bundle scope before export.
- The user can share something understandable without ambient support agents or hidden uploads.

### C) General-purpose OS

- The support contract stays local-first and toolable without assuming a central support backend.
- Compatibility adapters stay possible without redefining the default bundle contract.

### D) Appliance / factory / regulatory

- The production handoff stays deterministic, redacted, and offline-friendly.
- The bundle can travel through approved transfer lanes without losing its human summary or plan→bytes evidence.

## What this does **not** decide

Still open:

- the exact UI for previewing timelines before export,
- the exact heuristic for bundle-min selection,
- the exact resource/backend policy for reproduction inside disposable workspaces.

Those are follow-on implementation or design items.

## Design cue from current systems

A few ecosystem lessons are stable:

- support bundles are useful when they are standardized and bounded,
- structured diagnostics are better than grep-only folklore,
- metadata-first crash handling beats “ship the dump and hope”,
- and telemetry/export posture must respect data minimization rather than assuming more bytes are always better.

DeriveBSD should steal those lessons while keeping the collector backend, UI, and recipient transport replaceable.

restore apply proof now follows the same rule too: official handoff may carry `restore_receipt_digests` when recovery or stronger replacement apply changed the incident story. That keeps the typed support contract able to prove which exact restore apply participated instead of pushing support back toward backend-specific restore-job logs, ticket notes, or shell archaeology.

Support-session proof now follows the same rule too: official handoff may carry `support_session_digests` when remote assistance participated in the incident. That keeps the typed support contract able to prove which exact remote-assistance session participated instead of pushing support back toward helper dashboards, ticket notes, or chat archaeology.

operator-session proof now follows the same rule too: official handoff may carry `operator_session_digests` when privileged operator access participated in the incident. That keeps the typed support contract able to prove which exact operator session participated instead of pushing support back toward bastion dashboards, ticket notes, or shell archaeology.

breakglass authority proof now follows the same rule too: official handoff may carry `breakglass_receipt_digests` when emergency access participated in the incident. That keeps the typed support contract able to prove which exact `breakglass.receipt` participated instead of pushing support back toward rescue-shell folklore, operator memory, or ticket notes.

firmware/platform drift proof now follows the same rule too: official handoff may carry `fw_inventory_diff_digest` when reviewed firmware/platform drift participated in the incident. That keeps the typed support contract able to prove which exact `fw.inventory.diff` participated instead of pushing support back toward screenshots or dashboard comparisons.

Boot-assessment/finalization proof now follows the same rule too: official handoff may carry `boot_bless_receipt_digests` when health-gated finalization or rollback participated in the incident. That keeps the typed support contract able to prove which exact `boot.bless.receipt` participated instead of pushing support back toward loader counters, greenboot status text, or updater prose.

firmware-update proof now follows the same rule too: official handoff may carry `fw_update_receipt_digests` when staged or applied firmware-change outcomes participated in the incident. That keeps the typed support contract able to prove which exact `fw.update.receipt` participated instead of pushing support back toward updater dashboards, helper stdout, or ticket notes.

UEFI-variable mutation proof now follows the same rule too: official handoff may carry `uefi_var_set_receipt_digests` when BootOrder, Secure Boot, db/dbx, or capsule-intent mutation participated in the incident. That keeps the typed support contract able to prove which exact `uefi.var.set.receipt` participated instead of pushing support back toward ticket notes, raw efivar dumps, or helper stdout.

trustworthy-time action proof now follows the same rule too: official handoff may carry `time_sync_receipt_digests` when clock steps, source failover, or degraded sync materially participated in the incident. That keeps the typed support contract able to prove which exact `time.sync.receipt` participated instead of pushing support back toward daemon logs, monitor dashboards, or raw protocol transcripts.

storage integrity proof now follows the same rule too: official handoff may carry `storage_scrub_receipt_digests` when integrity verification, repair, or degraded-pool recovery materially participated in the incident. That keeps the typed support contract able to prove which exact `storage.scrub.receipt` participated instead of pushing support back toward `zpool status` transcripts, dashboard screenshots, or ticket prose.

temporary-authority context proof now follows the same rule too: official handoff may carry `lease_snapshot_digest` when live temporary authority materially participated in or shaped the incident. That keeps the typed support contract able to prove what temporary authority was still live at capture time instead of pushing support back toward bastion dashboards, control-plane screenshots, operator memory, or chat archaeology.

Last updated: 2026-03-21r369