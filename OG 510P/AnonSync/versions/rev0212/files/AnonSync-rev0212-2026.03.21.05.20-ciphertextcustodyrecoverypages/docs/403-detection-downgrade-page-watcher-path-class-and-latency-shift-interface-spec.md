# Detection downgrade page — watcher, path class, and latency shift interface spec

## Purpose

The archive already has change-detection coverage and remote-volume notification-confidence work.
What it still lacked was one explicit page for the moment the operator asks:

> why did this subject stop being near-real-time, what exactly caused the downgrade, and how much worse did the latency become?

Current official Resilio docs make this seam concrete.
They still say Linux watcher exhaustion can force discovery into manual or periodic rescans, that some storages and deep trees weaken notifications, that disabling notifications is a real power-user posture, and that a Windows service UNC workaround can keep a path usable while losing immediate file-update notifications.
That should compile to one ordinary page.

## Core decision

AnonSync must expose one first-class **Detection downgrade** page whenever the current freshness basis became weaker than its stronger supported posture.

## Fixed page order

1. **Downgrade verdict**
2. **Cause chain**
3. **Latency shift**
4. **Affected scope**
5. **Repair ladder and receipt**

### 1) Downgrade verdict

Show:

- `detection_downgrade_page_id`
- current subject / bind scope
- `from_basis_class`
- `to_basis_class`
- downgrade class (`watcher-budget`, `path-class-limit`, `notifications-disabled`, `execution-seat-path-mismatch`, `mixed`, `unknown`)
- strongest honest summary

The operator must be able to answer:

> what stronger posture did we lose, and what weaker posture are we on now?

### 2) Cause chain

Show:

- direct triggering evidence
- whether the root cause is host budget, path/storage class, explicit policy, or runtime-seat change
- any relevant subordinate causes
- whether the product is merely inferring or actually observing the cause

This section must make it ordinary to answer:

> did the environment degrade, did policy deliberately narrow, or did the current runtime seat lose visibility?

### 3) Latency shift

Show:

- prior best/worst-case notice classes
- current best/worst-case notice classes
- whether restart is now part of the real freshness path
- whether current publication promises must be weakened

This section exists so `degraded` does not stay abstract.
The user should see the concrete before/after latency class.

### 4) Affected scope

Show:

- whether the downgrade applies to one path, one bind, one subtree family, or the whole subject
- known unaffected siblings
- whether remote publication, local browsing, or destructive review truth is the main thing weakened

### 5) Repair ladder and receipt

Actions may include:

- `raise watcher budget`
- `restore native path class`
- `re-enable notifications`
- `switch execution seat or bind`
- `accept periodic-only coverage`

The receipt must preserve:

- pre/post basis class
- pre/post latency class
- repaired scope
- remaining blind spots

## Public object

### Detection downgrade page

Fields:

- `detection_downgrade_page_id`
- `subject_ref`
- `bind_ref` nullable
- `from_basis_class`
- `to_basis_class`
- `downgrade_classes[]`
- `cause_rows[]`
- `pre_latency_class`
- `post_latency_class`
- `affected_scope_rows[]`
- `repair_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. from → to basis
3. downgrade class
4. post-downgrade worst case
5. next repair action

Example:

```text
NAS/photos     live-notify → periodic-rescan     watcher-budget     up to 10m     Increase watcher budget
```
