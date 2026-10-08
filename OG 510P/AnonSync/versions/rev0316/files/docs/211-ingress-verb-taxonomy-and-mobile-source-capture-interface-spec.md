# Ingress verb taxonomy and mobile source-capture interface spec

## Purpose

The archive already had offer/claim, snapshot-send, and capture-ingest language.
What it still lacked was one explicit contract for another common interface failure:

> too many entry verbs that all sound like `add` or `share` even though they create different subject kinds, rights, and retention promises.

Current official Resilio docs make this seam sharper than a generic menu-layout complaint.
They still say Android exposes `Send file`, `Create folder`, `Add backup`, `Scan QR code`, and `Enter a key or link` from one `+` menu.
They still say mobile initiation can mean creating a new folder or adding an existing folder from the filesystem on Android, while Android file-manager guidance separately warns users to use `Send via Sync` instead of `Add to Sync` when they want to ship a pack of files.
They also still say backup is a distinct workflow whose desktop side keeps copies even after source-side deletion and whose destination has read-only posture.

That is all useful capability.
It is still not a good verb contract.
Operators should not need support lore to tell whether they are creating a live collaborative subject, adopting an existing tree, shipping a bounded snapshot, or attaching a capture-only source.

## Core decision

AnonSync should expose a fixed ingress verb taxonomy.
Every entry action must declare, before apply:

- what kind of subject it creates or joins
- what the source of truth is
- whether downstream edits are live, bounded, or prohibited
- what source-side deletion means later

## Why this matters

Current Resilio docs still reveal four interface mistakes AnonSync should not clone:

- one `+` cluster mixes collaboration, backup, receipt, and bounded send under adjacent verbs
- external file-manager verbs can look deceptively similar while creating different outcomes
- `backup` sounds storage-like but still creates a share with its own rights and lifecycle
- operators can still end a flow with the wrong subject kind merely because the verb family was overloaded

AnonSync should therefore keep one stronger rule:

> every ingress verb must state its subject kind and authority shape before bytes move.

## Fixed review order

Every ingress action should render the same sections in the same order:

1. **Source material**
2. **Subject kind**
3. **Authority and retention**
4. **Carrier and destination**

### 1) Source material

This section should show:

- whether the source is a single file, selected pack, existing folder, or recurring capture source
- whether the material already belongs to another subject
- whether the action is packaging, binding, or merely offering

The operator must be able to answer: **what material am I acting on?**

### 2) Subject kind

This section should show one of:

- live collaborative subject
- adopted existing subject
- bounded snapshot handoff
- capture-only ingest source
- receipt/claim of external subject

The operator must be able to answer: **what kind of thing will exist after I confirm this?**

### 3) Authority and retention

This section should show:

- who may mutate upstream
- whether downstream edits return live, by reviewed replacement, or never
- what happens if the source later deletes content
- whether landed bytes on the sink persist after source-side cleanup

The operator must be able to answer: **what authority and retention rules come with this verb?**

### 4) Carrier and destination

This section should show:

- whether the action uses QR, link, local handoff, or direct bind
- whether the destination chooses a root now or later
- whether a linked device, named sink, or ordinary recipient is expected

The operator must be able to answer: **where does this go, and how will the recipient experience it?**

## Main surface

AnonSync should keep verbs visibly separate, for example:

- `Create live subject`
- `Adopt existing folder`
- `Send bounded snapshot`
- `Attach capture source`
- `Claim incoming subject`

The product must not collapse those into one `Add` family and hope the later steps teach the difference.

## Object model implications

AnonSync should add or strengthen these objects:

- `ingress_intent`
- `source_material_claim`
- `subject_kind_review`
- `authority_shape_notice`
- `ingress_receipt`

Suggested fields for `ingress_intent`:

- `intent_id`
- `source_material_type`
- `subject_kind`
- `authority_shape`
- `retention_floor`
- `carrier`
- `destination_class`

## Event language

Use explicit phrases such as:

- `created live subject from new folder`
- `adopted existing folder as subject root`
- `sent bounded snapshot; no live mutation return`
- `attached capture source with sink retention floor`
- `claimed incoming subject via portable offer`

Avoid vague lines such as:

- `added`
- `shared`
- `synced`

## CLI shape

Example commands:

```text
anonsync create subject --path <dir>
anonsync adopt folder --path <dir>
anonsync send snapshot --files <paths>
anonsync attach capture-source --path <dir> --sink <seat>
anonsync claim incoming --artifact <offer>
```

The CLI must keep the same verb taxonomy as the local web UI.

## Failure and edge cases

### External file-manager invocation

If the system receives an intent from another app or file manager, it must still stop at the same subject-kind review before commit.

### Backup-like source with no linked sink yet

The product should say `capture source prepared; sink delivery pending`, not masquerade as completed collaboration.

### Multi-file package from mobile

The product should classify it as bounded snapshot unless the operator explicitly chooses to create a live subject.

## The non-clone reason

This is another clean example of why AnonSync should not merely copy Resilio's surface.
Current official Resilio docs still spread real semantic differences across adjacent mobile verbs and external file-manager advice.
AnonSync should instead keep one ingress taxonomy where subject kind, authority shape, and retention promise are named up front.
