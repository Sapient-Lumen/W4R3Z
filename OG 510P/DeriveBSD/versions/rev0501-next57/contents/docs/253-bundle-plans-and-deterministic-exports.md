# Bundle plans + deterministic exports

DeriveBSD’s evidence model works best when operators can:
- export a **minimal** bundle (only what explains the story)
- apply **deterministic transforms** (redaction)
- prove *exactly* what was shared (receipt)

We already have:
- causality graphs (`docs/246-causality-graphs-and-minimal-evidence-bundles.md`)
- deterministic redaction transforms (`docs/195-deterministic-redaction-transforms.md`)
- incident bundle metadata (`docs/216-incident-snapshots-and-support-bundles.md`)
- export policies + export receipts (`docs/251-export-policies-and-support-bundle-portal.md`)

The missing glue is a typed plan object describing **selection + transforms**, and typed outputs that bind that plan to concrete bytes.

## Official support handoff defaults

DeriveBSD now treats `bundle.plan`, `bundle.payload.manifest`, and `bundle.build.receipt` as part of the **official support handoff contract** together with `incident.timeline` and `incident.bundle`.
See: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`.

The default posture is:

- canonical payload format: **`tar.zst`**
- timeline-first support handoff: official bundle plans should include `incident.timeline` by default
- `bundle.build.receipt` should bind the `incident.timeline` digest when one is packaged
- `zip` remains an explicit compatibility adapter, not the canonical contract

## `bundle.plan`

A `bundle.plan` is a reproducible manifest for creating an exported bundle:

When packet troubleshooting participated, the official include surface is explicit: `packet_capture_sessions`, `packet_capture_summaries`, `packet_capture_import_receipts`, and `packet_capture_redaction_receipts`. That keeps packet evidence in typed selectors instead of raw packet blobs as default support-bundle members.

When trust-view activation or exact certificate action proof matters, the official include surface is explicit there too: `pki_trust_bundle`, `pki_trust_bundle_apply_receipts`, and `pki_issue_receipts` / `pki_issue_receipt_digests`. That keeps reviewed trust roots, served trust-view proof, and exact PKI issuance/renewal/install/revoke proof on typed selectors instead of renderer-specific trust dumps, CA dashboards, ACME logs, or ticket prose.

When remote assistance matters, the official include surface is explicit there too: `support_sessions` plus `support_session_digests`. That keeps remote-assistance participation on typed selectors instead of collector-private notes, helper dashboards, or ticket prose.

When firmware/platform drift matters, the official include surface is explicit there too: `firmware_inventory_diff` / `fw_inventory_diff_digest`. That keeps reviewed firmware/platform drift on typed selectors instead of screenshots, dashboard comparisons, or ticket prose.

When firmware-update stage/apply outcomes matter, the official include surface is explicit there too: `firmware_update_receipts` / `fw_update_receipt_digests`. That keeps firmware-update participation on typed selectors instead of updater dashboards, helper stdout, or ticket prose.

When firmware trust-root or boot-variable mutation matters, the official include surface is explicit there too: `uefi_var_set_receipts` / `uefi_var_set_receipt_digests`. That keeps Secure Boot, BootOrder, and capsule-intent mutation on typed selectors instead of raw efivar dumps, helper stdout, or ticket prose.

When health-gated finalization matters, the official include surface is explicit there too: `boot_bless_receipts` / `boot_bless_receipt_digests`. That keeps boot-assessment/finalization proof on typed selectors instead of loader counters, greenboot status text, or updater prose.

When measured posture matters, the official include surface is explicit there too: `boot_attestation` / `boot_attestation_digest`, `attestation_reference` / `attestation_reference_digest`, and `attestation_receipts` / `attestation_receipt_digests`. That keeps exact measured-boot evidence, verifier/reference scope, and verifier judgment on typed selectors instead of verifier dashboards, portal screenshots, or ticket prose.

When storage-integrity-shaped incidents matter, the official include surface is explicit there too: `storage_pool_inventory` / `storage_pool_inventory_digest`, `storage_health_snapshot` / `storage_health_snapshot_digest`, and `storage_scrub_receipts` / `storage_scrub_receipt_digests`. That keeps pool posture, current storage-health state, and exact scrub / repair proof on typed selectors instead of `zpool status` transcripts, dashboard screenshots, or ticket prose.

When trustworthy-time actions matter, the official include surface is explicit there too: `time_source_inventory` / `time_source_inventory_digest`, `time_sync_snapshot` / `time_sync_snapshot_digest`, and `time_sync_receipts` / `time_sync_receipt_digests`. That keeps current time posture and exact clock-discipline proof on typed selectors instead of daemon logs, monitor dashboards, or raw protocol transcripts.
When temporary-authority context matters, the official include surface is explicit there too: `lease_snapshot` / `lease_snapshot_digest`. That keeps current live-authority context on typed selectors instead of bastion dashboards, control-plane screenshots, operator memory, or chat archaeology.

When secret-shaped incidents matter, the official include surface is explicit there too: `secret_snapshot` / `secret_snapshot_digest` and `secret_receipts` / `secret_receipt_digests`. That keeps safe current secret posture plus exact secret action proof on typed selectors instead of provider dashboards, screenshots, or ticket prose.

- what trigger/time window motivated it
- which causal graph(s) it is based on
- which include knobs were enabled
- which redaction transform was applied
- which export policy was used

Tooling can then:
- create a bundle payload deterministically
- emit a single export receipt that cites the plan

See: `spec/bundle.plan.schema.json`.

## `bundle.payload.manifest` (new)

A `bundle.payload.manifest` is a deterministic, stable-ordered member listing for the produced payload.

It exists so operators (and verifiers) can answer:
- **“What members were in these bytes?”**
- **“Which evidence objects do these members correspond to?”** (optional `source` pointers)

This manifest is *metadata evidence* and is safe to include alongside the payload digest in support workflows.

See: `docs/448-bundle-payload-manifest-as-evidence-artifact.md`, `spec/bundle.payload.manifest.schema.json`.

## `bundle.build.receipt`

A `bundle.build.receipt` binds:
- the input `bundle.plan` digest,
- the produced payload digest,
- and the corresponding `incident.bundle` metadata digest

Optionally, it also binds:
- the produced `bundle.payload.manifest` digest (member listing)

…so reviewers can answer: **“Which plan produced these bytes, and what was inside?”** without chasing logs.

This receipt is the preferred “one object” to attach to:
- incident/support bundles (as metadata evidence)
- optional event-seal proof joins for bounded event windows (`event_seal_receipts` / `event_seal_receipt_digests`)
- export receipts (as the build provenance for what was exported)

See: `spec/bundle.build.receipt.schema.json`.

## Why this matters

Without a plan + typed outputs, operators end up with "bundle scripts".
Scripts are hard to review, and they don’t compose well with policy or explainability.

A plan object:
- is diffable in review (and can emit `bundle.plan.diff` as a stable review surface when plan templates drift)
- can be generated by tools, but still becomes evidence
- supports `bundle-min` as a first-class operation

A payload manifest:
- makes the bundle content queryable without unpacking bytes
- enables deterministic “re-export the same member set” workflows

A build receipt:
- makes bundle generation explainable and replayable
- makes “what we exported” auditable without trusting local logs

## Workflow sketch

1) `derive bundle plan --trigger fault:<id> --min`
- selects a time window
- selects causal graph digest(s)
- selects allowed include toggles
- chooses a redaction transform from export policy

2) `derive bundle build --plan <digest>`
- produces payload digest
- produces a `bundle.payload.manifest` listing members and their digests (including `incident.timeline` metadata by default for official support bundles)
- produces/updates `incident.bundle` metadata that references the plan, `incident.timeline` digest when present, and `event_seal_receipt_digests` when seal proof is part of the bounded event-window handoff
- emits `bundle.build.receipt` that cites:
  - plan digest
  - payload digest
  - incident.bundle digest
  - incident.timeline digest (recommended default)
  - payload manifest digest (recommended)
  - applied transform/policy digests (when relevant)

3) `derive export --policy <digest> --artifact <bundle>`
- requests a lease (portal/breakglass)
- exports via adapter
- emits `export.receipt` that references `bundle.build.receipt` (preferred)
  - may also reference `bundle.plan`, `consent.receipt`, `transport.receipt`, and `export.transparency.entry` digests (optional but high-value)

## Composition with privacy

A plan + manifest + build receipt makes privacy and compliance workable:
- the **policy** chooses allowed include knobs
- the **plan** records what was selected
- the **manifest** records what members were produced
- the **build receipt** records what was produced (binding digests)
- the **export receipt** records what was actually shared


See also: `docs/441-bundle-plan-diff-as-review-surface.md`.

- Optional restore apply proof joins for a recovery-shaped incident use `restore_receipts` / `restore_receipt_digests`.
- `incident.bundle` metadata may carry `restore_receipt_digests` when recovery evidence is part of the recovery-shaped incident.
- Optional support-session proof joins for a remote-assistance-shaped incident use `support_sessions` / `support_session_digests`.
- `incident.bundle` metadata may carry `support_session_digests` when remote-assistance evidence is part of the remote-assistance-shaped incident.

- Optional temporary-authority-context joins for a temporary-authority-shaped incident use `lease_snapshot` / `lease_snapshot_digest`.
- `incident.bundle` metadata may carry `lease_snapshot_digest` when evidence about what temporary authority was still live at capture time is part of the temporary-authority-shaped incident.
- Optional secret state/action proof joins for a secret-shaped incident use `secret_snapshot` / `secret_snapshot_digest` and `secret_receipts` / `secret_receipt_digests`.
- `incident.bundle` metadata may carry `secret_snapshot_digest` + `secret_receipt_digests` when safe current secret posture and exact secret action evidence are part of the secret-shaped incident.
- Optional operator-session proof joins for an operator-access-shaped incident use `operator_sessions` / `operator_session_digests`.
- `incident.bundle` metadata may carry `operator_session_digests` when privileged operator evidence is part of the operator-access-shaped incident.
- Optional breakglass authority proof joins for a breakglass-shaped incident use `breakglass_receipts` / `breakglass_receipt_digests`.
- `incident.bundle` metadata may carry `breakglass_receipt_digests` when emergency-access authority evidence is part of the breakglass-shaped incident. The first-class proof stays `breakglass_receipt_digests`; `extra[]` is supplementary rather than a replacement when richer adapter/runtime investigation material also needs to travel (`docs/711-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md`). For that richer supplementary material, prefer receipt-first on matching redaction/export/transport evidence digests rather than raw external attachment handles (`docs/712-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md`). Do not let those supplementary receipt chains float without the governing authority record: keep at least one matching `breakglass.receipt` digest in the same portable story (`docs/713-breakglass-supplementary-adapter-side-evidence-stays-authority-anchored-when-portably-carried.md`). Keep the portable story artifactized too: exported artifacts and typed handling receipts may travel, but live console URLs, copied `ConsoleEntryCommand` values, `WebSocketEndpoint` strings, virtual-media image locators, and session tokens do not (`docs/714-breakglass-supplementary-adapter-side-evidence-stays-artifactized-and-off-live-control-locators.md`). Keep the same portable story payload-anchored too: carry at least one passive artifact digest or accepted case-object proof so exported supplementary breakglass evidence does not devolve into receipt-only transport archaeology (`docs/715-breakglass-supplementary-adapter-side-evidence-stays-payload-anchored-when-portably-carried.md`). If the payload anchor takes the accepted-case-object lane, keep it object-exact too: preserve the exact accepted remote attachment/object/message-part identity instead of treating the parent case/ticket/container as if it were the payload itself (`docs/716-breakglass-supplementary-accepted-case-object-proof-stays-object-exact-when-portably-carried.md`). If the adapter can also see a revision/version/generation/ETag-like validator for that same accepted object, keep the accepted-case-object lane, keep it validator-pinned when visible too on the same accepted object revision/version token rather than leaving later review to object-latest portal semantics (`docs/717-breakglass-supplementary-accepted-case-object-proof-stays-validator-pinned-when-visible.md`). If the adapter can also see a protection/retention/hold posture for that same accepted object, keep the accepted-case-object lane remote-protection-shaped when visible too on the same accepted object posture instead of quietly treating any accepted portal object as durable evidence by implication (`docs/718-breakglass-supplementary-accepted-case-object-proof-stays-remote-protection-shaped-when-visible.md`). Keep that visible posture exact to the same accepted object revision/version too; ambient case/container/bucket policy is context only rather than a substitute for object-exact protection proof (`docs/719-breakglass-supplementary-accepted-case-object-proof-keeps-visible-remote-protection-exact-to-the-same-object-revision.md`). If the adapter can also see a redacted/non-secret passive locator for that same accepted object revision/version, keep the accepted-case-object lane remote-locator-continuous on that same locator too instead of falling back to parent case/container browse URLs or portal clicking; live control locators remain forbidden (`docs/720-breakglass-supplementary-accepted-case-object-proof-stays-remote-locator-continuous-when-visible.md`). If the adapter can later metadata-check that same accepted object revision/version without re-downloading the body, keep metadata-only reverification when visible too on typed `transport.reverification.receipt` with `reverification.body_downloaded = false` rather than screenshots or body-download folklore (`docs/721-breakglass-supplementary-accepted-case-object-proof-stays-metadata-only-reverifiable-when-visible.md`).
- Optional firmware/platform drift proof joins for a firmware/platform-drift-shaped incident use `firmware_inventory_diff` / `fw_inventory_diff_digest`.
- `incident.bundle` metadata may carry `fw_inventory_diff_digest` when reviewed firmware/platform drift evidence is part of the firmware/platform-drift-shaped incident.
- Optional firmware-update proof joins for a firmware-update-shaped incident use `firmware_update_receipts` / `fw_update_receipt_digests`.
- `incident.bundle` metadata may carry `fw_update_receipt_digests` when staged/applied firmware-update evidence is part of the firmware-update-shaped incident.
- Optional UEFI-variable mutation proof joins for a firmware/trust-root-shaped incident use `uefi_var_set_receipts` / `uefi_var_set_receipt_digests`.
- `incident.bundle` metadata may carry `uefi_var_set_receipt_digests` when BootOrder, Secure Boot, db/dbx, or capsule-intent mutation evidence is part of the incident.
- Optional boot-assessment proof joins for a boot-assessment-shaped incident use `boot_bless_receipts` / `boot_bless_receipt_digests`.
- `incident.bundle` metadata may carry `boot_bless_receipt_digests` when health-gated finalization or rollback evidence is part of the boot-assessment-shaped incident.
- Optional attestation posture proof joins for a posture/admission-shaped incident use `boot_attestation` / `boot_attestation_digest`, `attestation_reference` / `attestation_reference_digest`, and `attestation_receipts` / `attestation_receipt_digests`.
- `incident.bundle` metadata may carry `boot_attestation_digest` + `attestation_reference_digest` + `attestation_receipt_digests` when measured-boot evidence, verifier scope, and verifier judgments are part of the posture/admission-shaped incident.
- Optional storage-integrity proof joins for a storage-integrity-shaped incident use `storage_pool_inventory` / `storage_pool_inventory_digest`, `storage_health_snapshot` / `storage_health_snapshot_digest`, and `storage_scrub_receipts` / `storage_scrub_receipt_digests`.
- `incident.bundle` metadata may carry `storage_scrub_receipt_digests` when exact integrity-verification evidence is part of the storage-integrity-shaped incident.

Last updated: 2026-03-23r452
