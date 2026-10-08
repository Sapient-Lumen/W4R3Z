# Diagnostic evidence, redaction, and support-bundle spec

## Purpose

The archive already treats reports, receipts, recovery bundles, state roots, and attention as first-class operator state.
What it still lacked was one durable public contract for a more operational question:

> when something is wrong, what evidence are we collecting, for which incident, at what diagnostic depth, with what redaction posture, and what exactly left the local machine?

This document answers that question.
It exists so AnonSync does not recreate a common sync-product failure mode where serious troubleshooting depends on hidden storage paths, ad hoc debug toggles, manual log scavenging, crash-dump rituals, and vague “send us your logs” flows.

## Resilio-derived motivation

Current Resilio docs still distribute diagnostics across several separate support rituals:

- enabling debug logging lives in advanced preferences, tray-menu gesture, or by writing `debug.txt` with `FFFFFFFF` into the storage folder
- logs are collected only after reproducing the issue for a while, and the operator is told to attach `sync.log` files or use a support form with extra narrative context
- the storage folder itself changes with config mode, service user, and platform, so the place where logs, configs, and databases live is part of the troubleshooting ritual
- crash reports, mini-dumps, and core dumps use platform-specific manual collection paths and OS-specific steps
- the support section separately groups iperf, log-size tuning, debug logs, crash dumps, and NAS core-dump steps
- for Resilio Sync v3, direct technical support is not available, which makes self-service diagnostics even more important

Those are useful support instructions.
They are not one trustworthy diagnostic-evidence contract.

## Contrast point from Syncthing

Syncthing is useful here not because AnonSync should copy it blindly, but because its docs show a cleaner direction:

- a dedicated support-bundle endpoint exists as first-class debug surface
- file-specific diagnostics exist as explicit API calls
- event, system-log, and log-level surfaces are separate inspectable resources

That is closer to the shape AnonSync should want: diagnostics as supported public state, not scavenger-hunt lore.

## Core rule

Diagnostic depth, collected evidence, redaction posture, local retention, and export/seal are separate public facts.
They may be related.
They must not collapse into one vague action like `send logs`.

## Public objects

### Diagnostic incident

A durable troubleshooting object for one problem statement or investigation window.
This exists so evidence collection is attached to an explicit incident instead of becoming a pile of files near the daemon.

Fields:

- `diagnostic_incident_id`
- `subject_refs[]`
- `headline`
- `reason_code`
- `incident_kind` (`connectivity`, `transfer-slow`, `path-binding`, `projection`, `storage-pressure`, `conflict`, `crash`, `performance`, `unknown`)
- `opened_from` (`report`, `workbench`, `cli`, `api`, `auto-health-trigger`)
- `diagnostic_depth` (`baseline`, `elevated`, `trace`, `forensics`)
- `requested_evidence_classes[]` (`events`, `recent-logs`, `per-file-diagnostics`, `route-state`, `policy-explanation`, `transfer-samples`, `crash-dumps`, `system-status`, `config-summary`)
- `redaction_profile_ref`
- `retention_policy`
- `status` (`open`, `collecting`, `awaiting-redaction-review`, `sealed`, `expired`, `closed`)
- `opened_at`
- `last_collected_at` nullable
- `closed_at` nullable

### Evidence bundle

A reviewed, inspectable collection of incident-linked diagnostic material.
This exists so operators can answer what the bundle contains before anything is exported, shared, or deleted.

Fields:

- `evidence_bundle_id`
- `incident_ref`
- `collection_scope`
- `diagnostic_depth`
- `included_classes[]`
- `excluded_classes[]`
- `redaction_profile_ref`
- `redaction_findings[]`
- `contains_sensitive_paths`
- `contains_peer_identifiers`
- `contains_secret_material` boolean
- `secret_handling` (`none-present`, `auto-redacted`, `manually-redacted`, `blocked-unsealed`)
- `event_window`
- `size_bytes`
- `retention_until` nullable
- `seal_state` (`staged`, `reviewed`, `sealed`, `exported`, `destroyed`)
- `export_targets[]`
- `created_at`

### Redaction profile

A named rule set describing how evidence is trimmed, tokenized, or blocked before sealing/export.
This exists so privacy-preserving defaults stay explicit rather than becoming magical best effort.

Fields:

- `redaction_profile_id`
- `name`
- `path_policy` (`full`, `basename-only`, `tokenized`, `blocked`)
- `peer_identity_policy` (`full`, `stable-token`, `role-only`, `blocked`)
- `address_policy` (`full`, `subnet-only`, `tokenized`, `blocked`)
- `secret_policy` (`block`, `auto-redact`, `manual-review-required`)
- `config_policy` (`summary-only`, `diff-safe`, `full-redacted`)
- `retention_default`
- `mutable` (`built-in`, `operator`, `incident-local`)
- `created_at`

### Evidence receipt

A durable record proving that diagnostic depth changed, a bundle was collected, redaction was reviewed, a bundle was sealed/exported, or staging material was destroyed.

Fields:

- `evidence_receipt_id`
- `incident_ref`
- `bundle_ref` nullable
- `action` (`open-incident`, `raise-depth`, `lower-depth`, `collect-bundle`, `review-redaction`, `seal-bundle`, `export-bundle`, `destroy-staging`, `close-incident`)
- `before_summary`
- `after_summary`
- `actor_ref`
- `created_at`

## Rules

1. **Incidents own evidence collection.**  
   Logs, traces, file diagnostics, and dumps should not be gathered as orphaned artifacts whenever possible.

2. **Diagnostic depth is explicit and temporary.**  
   Raising log depth or trace verbosity must record scope, reason, and expiry instead of silently lingering after the incident ends.

3. **Collection scope is inspectable before export.**  
   The operator should be able to see classes, time windows, sensitive-content findings, and redaction posture before sealing or sharing a bundle.

4. **Redaction policy is separate from evidence value.**  
   “Useful enough for diagnosis” and “safe enough to export” are related but different claims.

5. **Export is not the same as retention.**  
   A bundle may be sealed locally, exported elsewhere, retained for some time, or destroyed immediately after use. Each of those is explicit state.

6. **Crash handling is part of the same model.**  
   Crashes, dumps, and per-file diagnostics should land inside the same incident/evidence grammar instead of forcing a side path of platform-specific support lore.

7. **Headless parity matters here too.**  
   Linux-first and service-first deployments must be able to inspect, collect, seal, and destroy evidence without relying on a richer desktop shell.

## CLI contract

Minimal commands:

```text
anonsync diagnostic incident list
anonsync diagnostic incident open --subject share:media --kind transfer-slow
anonsync diagnostic incident show dgi_01J...
anonsync diagnostic depth set dgi_01J... --to elevated --for 30m
anonsync evidence bundle collect --incident dgi_01J... --classes events,recent-logs,transfer-samples --plan
anonsync evidence bundle show evb_01J...
anonsync evidence bundle seal evb_01J...
anonsync evidence receipt show evr_01J...
```

These commands should answer:

- what problem this incident is about
- which diagnostic depth is active now and when it expires
- what evidence classes were or were not collected
- what redaction profile is in force and what sensitive-content findings remain
- what receipt proves that a bundle was sealed, exported, or destroyed

## Workbench contract

The workbench should expose a `Diagnostics` page distinct from `Health`, `Reports`, and `System State`.
It should support:

- listing open incidents by subject, reason, depth, and collection status
- opening a reviewed evidence drawer that previews contents before sealing/export
- filtering bundles by seal state, sensitive-content findings, or retention horizon
- temporarily raising or lowering diagnostic depth with explicit expiry and receipts
- jumping from an incident to its backing report, transfer explanation, file diagnostic, or crash detail

## Report-language integration

The shared report language should support at least these families:

- `diagnostic-scope` — what would be collected and why
- `redaction-gap` — what still requires review or blocking before seal/export
- `event-gap` — when event continuity or log coverage is too thin for a strong diagnostic claim

These reports should behave like any other report-backed finding: severity, freshness, scope, and safe next step stay explicit.

## Design tests

The model is not explicit enough if any of the following remains true:

- the operator still has to remember hidden storage paths to know where evidence lives
- raising debug depth does not leave a receipt or expiry
- one surface can export a bundle that another surface cannot preview or redact-review
- crashes and per-file diagnostics still fall into a separate support ritual with no shared incident object
- exported evidence cannot later be audited for scope, redaction profile, or destruction state

## Outcome

A mature AnonSync surface should let the operator move from `something is wrong` to `open incident` to `collect reviewed evidence` to `seal/export/destroy with receipts` without leaving the public model or re-learning platform-specific support ritual.
That is what this document locks in.
