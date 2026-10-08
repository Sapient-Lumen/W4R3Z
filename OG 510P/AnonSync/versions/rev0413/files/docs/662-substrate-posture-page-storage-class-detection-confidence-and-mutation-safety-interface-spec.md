# Substrate posture page — storage class, detection confidence, and mutation safety interface spec

## Purpose

This page answers one ordinary question:

> what kind of storage substrate is under this share right now, and what is the strongest honest sentence the product may say about promptness, safety, and ordinary connected behavior on it?

The page exists because `connected`, `mounted`, `online`, and `safe for ordinary concurrent use` are not interchangeable.
The operator needs one direct statement of substrate truth before they trust ordinary share language.

## Core decision

Every managed share/path pair must render one first-class **Substrate posture** page whenever substrate class, notification behavior, locking behavior, or writer topology can materially change the safety or timeliness contract.
The page owns:

- substrate class now
- change-detection basis now
- lock and retry posture now
- out-of-band writer risk now
- strongest safe sentence for this share on this substrate now

## Primary layout

The page always renders the same regions in the same order:

1. posture strip
2. substrate identity card
3. detection-confidence card
4. mutation-safety matrix
5. remedy and migration card
6. receipts

### 1) Posture strip

Show:

- share label
- local path
- substrate class: `local-native`, `local-removable`, `network-mounted`, `nas-local`, `virtualized`, `unknown`
- protocol family if known: `posix-local`, `ntfs-local`, `smb`, `nfs`, `fuse`, `other`, `unknown`
- connected-sentence grade: `ordinary`, `degraded`, `guarded`, `unsafe`, `blocked`
- one honest next action

### 2) Substrate identity card

This card publishes:

- how the substrate was identified
- whether the path is local to the runtime or mounted through another protocol layer
- whether other access channels are expected to touch the same bytes
- whether the current topology is single-writer, coordinated multi-writer, or mixed-writer
- whether the product trusts the path as a normal managed substrate, a degraded substrate, or an unsafe substrate

The operator must be able to answer: **what kind of storage world is this really?**

### 3) Detection-confidence card

This card publishes:

- active change-detection basis: `fs-notify`, `hybrid`, `scheduled-rescan`, `manual-rescan`, `unknown`
- expected detection promptness band
- why stronger promptness is unavailable if degraded
- whether notifications are absent by substrate limitation, by configuration, or by runtime failure
- whether stale or delayed appearance should be expected on this seat

The operator must be able to answer: **how quickly and confidently are changes discovered here?**

### 4) Mutation-safety matrix

Render rows for these capability families:

- local edits through managed path
- remote arrivals onto this substrate
- concurrent same-file edits by local applications
- locking and retry behavior
- out-of-band access channel safety
- placeholder/materialization safety if applicable
- rename/move semantics if applicable

For each row show:

- current grade: `ordinary`, `degraded`, `guarded`, `unsafe`, `blocked`, `unknown`
- main evidence basis
- strongest safe sentence
- stronger forbidden sentence

### 5) Remedy and migration card

This card publishes:

- least-strong remedy that improves safety without changing share identity
- whether delay tuning, retry tuning, or review-only degradation is enough
- when mixed-writer topology must be removed rather than tuned
- when substrate migration is the least dishonest answer
- whether the current substrate can ever become ordinary or remains permanently guarded

### 6) Receipts

Link to:

- latest substrate admission review
- latest mutation-channel evidence page
- latest substrate-risk receipt

## Required fields

### `share_substrate_posture`

- `share_ref`
- `path_ref`
- `substrate_class`
- `protocol_family`
- `runtime_locality`
- `writer_topology`
- `detection_basis`
- `detection_promptness_band`
- `lock_behavior_grade`
- `mixed_writer_risk_grade`
- `connected_sentence_grade`
- `strongest_safe_sentence`
- `stronger_forbidden_sentence`
- `last_evaluated_at`

## Honest outputs

The page may conclude:

- `This share is connected on a network-mounted SMB path with scheduled-rescan detection. Strongest safe sentence: connected, but promptness is degraded and out-of-band mixed-writer access is not trusted.`
- `Lock behavior is guarded. Sync can detect locked files here, but the locking application is not attributable from product evidence alone.`
- `This topology is unsafe for ordinary collaboration because unmanaged writers can reach the same bytes outside the share protocol.`

It may not collapse these states into `connected`, `healthy`, or `synced normally`.
