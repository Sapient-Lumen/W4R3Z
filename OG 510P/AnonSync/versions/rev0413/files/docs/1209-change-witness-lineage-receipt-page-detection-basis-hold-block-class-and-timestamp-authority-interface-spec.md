# Change-witness lineage receipt page — detection basis, hold/block class, and timestamp authority

## Purpose

After any serious detection, waiting, or timestamp-downgrade event, a later operator must be able to answer:

> how did the product actually learn about this change, was publication intentionally held or truly blocked, what timestamp authority was in force, and what stronger sentence was explicitly rejected?

This receipt exists so change evidence does not dissolve into restart/touch folklore.

## Receipt fields

### Identity

- `receipt_id`
- `subject_ref`
- `path_ref`
- `created_at`

### Detection basis

- `change_witness_class` (`live`, `periodic_rescan`, `manual_rescan`, `manual_touch`, `uncertain`)
- `watcher_health` (`healthy`, `degraded`, `exhausted`, `unknown`)
- `rescan_dependence` (`none`, `periodic`, `manual`, `startup-only`)

### Publication posture

- `publication_posture` (`ready`, `quiescence_hold`, `lock_blocked`, `waiting_recheck`, `already_published`)
- `delay_profile_ref` nullable
- `recheck_interval_seconds` nullable
- `next_advance_trigger`

### Timestamp authority

- `timestamp_authority_class` (`aligned`, `retrying_write_failure`, `database_only`, `degraded_other`)
- `disk_mtime_truth_grade`
- `authoritative_time_source`

### Claim ceiling

- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `reopen_conditions[]`

## Required behavior

The receipt must be emitted whenever:

- the product relies on rescan rather than live events for a meaningful change claim
- manual touch or manual rescan materially changed observation confidence
- a file entered quiescence hold or lock blockade during a relevant publication window
- timestamp authority diverged from disk-visible mtime in a way that changes row honesty

## Forbidden simplifications

The receipt must never flatten the event into:

- `file updated`
- `sync delayed`
- `locked`
- `rescanned`
- `mtime issue fixed`

unless the structured witness, posture, and authority fields remain inspectable alongside that summary.
