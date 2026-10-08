# Recovery material, custody, and continuity-bundle spec

## Purpose

The archive already had recovery commands, bundle objects, state-root transition rules, and a clear refusal to treat cloning as the real recovery story.
What it still lacked was one public contract for a more operational question:

> what recovery material exists right now, what workflow is it sufficient for, what hidden dependencies remain, and what continuity claims will or will not survive if this bundle is later consumed?

This document answers that question.
It exists so AnonSync does not recreate the same failure mode visible in existing sync products, where recovery truth is reconstructed from storage paths, saved keys, database continuity, service-profile lore, and support-only CLI ritual.

## Resilio-derived motivation

Current Resilio docs still distribute recovery truth across several separate surfaces:

- cloning the application state is explicitly unsupported
- the storage folder contains configuration, auxiliary settings, and share databases, and moving it depends on config-mode knowledge
- one WebUI-password reset path deletes settings files from the storage folder, resets global preferences, and duplicates the device in `My devices`, while another path injects credentials through config mode
- encrypted-folder recovery works only if the operator saved the RW/RO keys and did not remove the encrypted folder from Sync so the original database continuity remains
- local decrypt on an encrypted node requires the secret, encrypted folder path, output path, and the database path, with the docs even pointing operators to logs to find the right database name
- device replacement and service-profile moves can also change which storage root is active, which changes what recovery material is even available locally

Those are useful support notes.
They are not one durable recovery-material contract.

## Core rule

Recovery material is explicit state.
Bundle format, custody class, workflow sufficiency, hidden dependency, continuity claim, invalidation cause, and later consumption outcome are separate public facts.
They may be related.
They may not collapse into one intuition such as “I copied the app state”, “I still have the key somewhere”, or “the encrypted backup probably works”.

## Public objects

### Recovery posture

A first-class summary of current recovery readiness for one subject or workflow family.

Fields:

- `recovery_posture_id`
- `subject_ref`
- `workflow_scope[]` (`encrypted-offline-decrypt`, `device-replacement`, `grant-reconciliation`, `identity-rotation`, `state-root-rebind`)
- `current_bundle_refs[]`
- `sufficiency_state` (`sufficient`, `partial`, `blocked`, `stale`, `unknown`)
- `custody_state` (`portable`, `split-secret`, `daemon-bound`, `mixed`)
- `hidden_dependencies[]`
- `invalidated_by[]`
- `last_verified_at` nullable
- `next_review_at` nullable

### Recovery bundle

A portable, inspectable export of recovery prerequisites for one workflow.
It may carry wrapped secrets, metadata, continuity manifests, or only proofs that certain material remains daemon-bound.

Fields:

- `recovery_bundle_id`
- `bundle_type` (`encrypted-offline-decrypt`, `device-replacement`, `grant-reconciliation`, `identity-rotation`, `state-root-rebind`)
- `subject_ref`
- `created_at`
- `custody_class` (`portable-secret`, `portable-metadata-only`, `daemon-bound-proof`, `split-secret-plus-metadata`)
- `contains_keys`
- `contains_wrapped_secrets`
- `contains_metadata`
- `contains_continuity_manifest`
- `db_dependency` (`none`, `optional`, `required`)
- `continuity_claims[]`
- `invalidated_at` nullable
- `superseded_by` nullable
- `sufficiency_status` (`unknown`, `sufficient`, `partial`, `insufficient`)
- `verification_findings[]`
- `encrypted`
- `format_version`

### Recovery receipt

A durable record proving that recovery posture changed, a bundle was verified or consumed, or continuity was explicitly narrowed.

Fields:

- `recovery_receipt_id`
- `action` (`export-bundle`, `verify-bundle`, `invalidate-bundle`, `consume-bundle`, `replace-device`, `rotate-identity`, `revoke-device`, `import-recovered-bytes`)
- `bundle_ref` nullable
- `subject_refs[]`
- `workflow_scope[]`
- `continuity_delta`
- `dependency_findings[]`
- `created_at`

## Rules

1. **Exportability is not sufficiency.**  
   A bundle can exist and still be partial, stale, or daemon-bound for important steps.

2. **Recovery is workflow-specific.**  
   “Can recover” is too vague. Offline decrypt, device replacement, grant reconciliation, and identity rotation each need separate truth.

3. **Custody must be explicit.**  
   Portable secret material, metadata-only manifests, split-secret workflows, and daemon-bound proofs are meaningfully different operator postures.

4. **Invalidation must be first-class.**  
   Identity rotation, state-root replacement, share retirement, grant-model drift, or policy changes can all weaken older recovery material. Operators should see that directly.

5. **Bundle consumption must not silently restore authority.**  
   Recovering bytes, replacing a device, and reviving old grants are different actions. A recovered payload or replacement plan should say exactly what continuity it claims and what it does not.

6. **Offline recovery remains a real product feature.**  
   When sufficient bundle material exists, recovery should not require a surviving daemon just because the healthy-path export lived behind one.

7. **Receipts matter as much as exports.**  
   Operators need durable proof of what was exported, verified, invalidated, or consumed, not just a file on disk.

## CLI contract

Minimal commands:

```text
anonsync recover posture show
anonsync recover posture show --share vault
anonsync recover bundle export --type encrypted-offline-decrypt --share vault --output ./vault.arb
anonsync recover bundle export --type device-replacement --device laptop-01 --output ./laptop-01.arb
anonsync recover bundle show ./vault.arb
anonsync recover bundle verify ./vault.arb
anonsync recover receipt show rcr_01J...
anonsync recover decrypt-replica --input /srv/encrypted-vault --bundle ./vault.arb --output ./vault-restored
```

These commands should answer:

- what workflows are presently sufficient, partial, blocked, or stale
- whether a bundle is portable, split-secret, or still daemon-bound in an important way
- which continuity claims the bundle would support if later consumed
- what receipt proves export, verification, invalidation, or consumption

## Workbench contract

The workbench should expose a `Recovery` page distinct from both `System State` and `History`.
Its job is not to replace the daemon API.
Its job is to answer:

- what recovery posture exists right now for important shares, devices, and roots
- which bundles are current, stale, invalidated, or superseded
- what continuity each bundle could preserve
- what hidden dependencies still remain before the operator is under stress

The page should support:

- filtering bundles by workflow, custody class, and sufficiency state
- exporting or re-verifying a bundle without leaving the workbench
- jumping from a degraded recovery posture to the specific missing dependency or invalidation cause
- inspecting receipts for bundle export, verification, invalidation, replacement, and recovery-byte import
- comparing portable recovery posture against daemon-bound posture before maintenance or hardware replacement

## Design tests

The model is not explicit enough if any of the following remains true:

- the operator still needs to read logs to learn whether a bundle depends on a database path
- a bundle can be “successful” yet leave continuity or authority consequences implicit
- replacement and encrypted-byte recovery still look like the same action
- identity rotation or state-root replacement can silently invalidate earlier recovery material
- later audit cannot prove which bundle was current when an operator prepared for disaster

## Outcome

A mature AnonSync surface should let an operator move from `can I recover this?` to `for which workflow?` to `with what custody and hidden dependencies?` to `what continuity would survive if I consumed this bundle?` without leaving the shared public model.
That is what this document locks in.
