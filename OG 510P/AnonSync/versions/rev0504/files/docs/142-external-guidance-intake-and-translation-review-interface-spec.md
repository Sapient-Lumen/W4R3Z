# External guidance intake and translation review interface spec

## Purpose

The archive now says that:

- deeper diagnostics must be approved as bounded probes
- outward disclosure must be reviewed as recipient-specific escalation packets
- remediation must be modeled as typed, reversible, evidence-linked recipes

What still remained under-specified was the status of **instructions that come from outside the product**.
In practice operators often receive advice from:

- official docs
- community forum posts
- issue threads
- a teammate
- a vendor reply
- a network administrator
- copied shell commands or config snippets

That advice can be useful, but it is not automatically trustworthy, complete, safe, reversible, or even applicable to the current incident.
This document defines the interface contract for **external guidance intake** and **translation review** before any such advice becomes an AnonSync action.

It is complemented by `249-external-guidance-source-boundary-fetch-snapshot-and-frozen-review-basis-interface-spec.md`, which keeps live source locator, fetched snapshot, exact reviewed basis, and later drift checks separate.

## Core rule

External advice must enter the product as an untrusted guidance object.
It may inform a remediation recipe, probe plan, or escalation packet, but it must not become a runnable action until the product has translated it into typed local objects and shown what remained ambiguous or unsupported.

## Why this needs its own spec

Current Resilio docs are one strong example of why this boundary matters.
Their official support material can recommend things like:

- enable debug logging
- enlarge log size by editing local state while Sync is stopped
- change power-user preferences
- add predefined hosts
- adjust port forwarding or firewall behavior
- stop Sync and run `iperf3`
- inspect storage folders or dump locations directly

That is often useful advice.
But it is still external prose that the operator must interpret and apply correctly.
AnonSync should not ask the operator to transpose external instructions into ad hoc local changes.
It should ingest the guidance, classify each step, reject unsupported parts, and present a typed translation review before anything is approved.

## Public objects

### External guidance intake object

A durable record of one outside instruction set or recommendation.

Suggested fields:

- `external_guidance_intake_id`
- `incident_ref`
- `source_kind` (`official-doc`, `forum-post`, `support-reply`, `teammate-note`, `admin-instruction`, `copied-command-block`, `unknown`)
- `source_locator`
- `source_authenticity_confidence`
- `ingested_at`
- `raw_guidance_excerpt`
- `machine_parse_state` (`unparsed`, `partially-parsed`, `fully-parsed`, `rejected`)
- `translation_state` (`draft`, `reviewed`, `approved`, `rejected`, `superseded`)

### Guidance clause row

One extracted statement or action clause from the external advice.

Suggested fields:

- `guidance_clause_row_id`
- `clause_index`
- `clause_text`
- `clause_kind` (`observation`, `diagnostic-step`, `product-action`, `environment-change`, `external-tool-step`, `disclosure-request`, `assumption`, `rollback-hint`)
- `applicability_state` (`applicable`, `partially-applicable`, `not-applicable`, `unknown`)
- `safety_state` (`safe-if-translated`, `needs-human-review`, `blocked`, `unsupported`)
- `translation_target_kind` nullable (`remediation-recipe`, `diagnostic-probe`, `escalation-packet`, `note-only`)

### Translation row

One typed local object derived from a clause.

Suggested fields:

- `translation_row_id`
- `source_clause_ref`
- `target_object_kind`
- `target_object_ref` nullable
- `translation_confidence`
- `lost_meaning_summary`
- `added_local_constraints_summary`

### Unsupported residue row

One part of the advice that could not be safely translated.

Suggested fields:

- `unsupported_residue_row_id`
- `residue_kind` (`ambiguous-command`, `unsafe-global-change`, `unsupported-platform-step`, `unverifiable-assumption`, `unknown-side-effect`, `outbound-disclosure-request`)
- `summary`
- `required_manual_review`

## Fixed inspection order

Every guidance-intake surface should preserve this order:

1. **Where this advice came from**
2. **What the source is asking for**
3. **What can be translated safely**
4. **What was rejected, narrowed, or left ambiguous**
5. **Which local objects would be created**
6. **Approve translations, keep as notes, or reject intake**

### 1) Where this advice came from

The product should show the source kind, locator, and authenticity confidence.
Examples:

- `Official vendor help-center article`
- `Community forum post by unknown user`
- `Teammate message with copied shell commands`

### 2) What the source is asking for

This section should preserve the original intent without pretending it is already safe.
Examples:

- `Enable deeper logging and reproduce the issue`
- `Open/forward the listening port`
- `Add a direct host override`
- `Run external path measurement while the sync service is stopped`

### 3) What can be translated safely

This is where the product turns prose into typed local objects.
Examples:

- create a `diagnostic_probe_plan` for a 10-minute elevated log window
- create a `remediation_recipe` for a reversible direct-host override
- create an `external_escalation_packet` draft for requested evidence

### 4) What was rejected, narrowed, or left ambiguous

This section is mandatory.
It should state things like:

- `the source suggests a global config edit; narrowed to incident-bounded recipe review`
- `the source assumes platform-specific file paths that do not match this runtime`
- `the source asks for full logs; translated to redaction-reviewed packet only`
- `the source does not provide a rollback path`

### 5) Which local objects would be created

The product should show the concrete result of approval:

- one remediation recipe
- one diagnostic probe plan
- one escalation packet draft
- one note-only residue item

### 6) Approve translations, keep as notes, or reject intake

The operator should be able to:

- `Approve translated objects`
- `Approve only note capture`
- `Reject unsupported advice`
- `Send to manual review`

## Public rules

### Rule 1 — external advice is never self-executing

No copied command or official instruction becomes a runnable action on intake.

### Rule 2 — translation must add local safety constraints, not erase them

If the source advice is broader than the local incident requires, the translation must narrow it.

### Rule 3 — unsupported residue must stay visible

The product must not silently drop ambiguous or unsafe instructions.
It should list what could not be translated and why.

### Rule 4 — authenticity and applicability are separate judgments

An official source can still be inapplicable to this incident or runtime.
A low-confidence source may still contain one safely translatable observation.

### Rule 5 — disclosure requests become packet drafts, not uploads

Any outside request for logs, dumps, paths, or config snapshots must route through the escalation-packet review flow.

### Rule 6 — translation must preserve proof obligations

If advice implies a test or change, the resulting local object must still include the after-action proof check.

## Dense row contract

A dense intake row should preserve these labels in this order:

- `Source`
- `Requested move`
- `Applicable?`
- `Translated to`
- `Rejected residue`
- `Needs review`
- `State`

## Example prompts

- `Is this official advice actually applicable here?`
- `Which parts of this copied instruction turned into real local objects?`
- `What did the product refuse to translate?`
- `Did this source ask for disclosure, or only for a local probe?`
- `What proof would still be required after following the translated advice?`

## Anti-goals

- no paste-and-pray command execution
- no automatic trust just because the source is official
- no silent narrowing or silent dropping of risky instructions
- no unreviewed conversion of disclosure requests into uploads
- no freeform troubleshooting notes that bypass recipe, probe, or packet objects
