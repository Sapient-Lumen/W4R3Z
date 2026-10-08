# Freshness basis page — live notify, periodic, manual, and startup discovery interface spec

## Purpose

The archive already has change-detection coverage, host cadence, completeness confidence, and work-phase language.
What it still lacked was one ordinary page for the simpler question:

> when the product says a subject is `up to date`, what basis actually supports that claim right now?

Current official Resilio docs make this seam concrete.
They still say synchronization starts only after change detection, that filesystem notifications are fastest when they work, that scheduled rescan runs every 600 seconds by default and on Sync start, that the rescan interval can be changed to zero, and that manual rescan is an ordinary product action.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Freshness basis** page for every subject and every bind with materially different detection posture.

The page exists to answer five things in one place:

1. what mechanism most recently made this subject fresh enough to claim `current`
2. what weaker mechanism would notice the next unseen change if live detection fails
3. what worst-case notice delay currently applies
4. what blind spots still survive under the current basis
5. what stronger basis could be restored next

## Fixed page order

1. **Current basis verdict**
2. **Discovery channels in force**
3. **Latency envelope**
4. **Blind spots and trust floor**
5. **Stronger-basis actions**

### 1) Current basis verdict

Show:

- `freshness_basis_page_id`
- subject / bind scope
- current `basis_class` (`live-notify`, `live-notify-degraded`, `periodic-rescan`, `startup-rediscovery-only`, `manual-rescan-only`, `mixed`, `unknown`)
- strongest honest summary
- last basis-changing event time

The operator must be able to answer:

> what mechanism currently makes the `fresh enough` claim true?

### 2) Discovery channels in force

Show:

- filesystem notifications enabled / disabled / unsupported / degraded
- scheduled rescan enabled / disabled and interval
- startup rediscovery enabled / disabled
- manual rescan available / required / unavailable
- whether path class or execution seat weakens any channel

The page must make it ordinary to answer:

> if a new local change lands five seconds from now, which channel is expected to notice it first?

### 3) Latency envelope

Show:

- best-case discovery latency class
- worst-case discovery latency class
- whether restart is part of current discovery reality
- whether current latency is subject-wide or only this bind/path family

The page must not hide a ten-minute worst case behind a generic `watching for changes` line.

### 4) Blind spots and trust floor

Show:

- watcher-exhausted subtrees
- storage/path classes with weak or absent notifications
- any zero-rescan or manual-only posture
- whether the current basis is strong enough for browsing only, routine sync trust, or destructive review

This section should answer:

> what sort of claim is still honest under the current basis — browsing, routine trust, or not-yet-destructive trust?

### 5) Stronger-basis actions

Actions may include:

- `Restore live notifications`
- `Increase watcher budget`
- `Re-enable periodic rescan`
- `Move to a better-supported bind`
- `Run one manual rescan now`
- `Accept current latency floor`

Each action must preview the new basis class and the strongest honest post-action claim.

## Public object

### Freshness basis page

Fields:

- `freshness_basis_page_id`
- `subject_ref`
- `bind_ref` nullable
- `basis_class`
- `best_case_notice_class` (`subsecond`, `seconds`, `minutes`, `restart-bound`, `manual-only`, `unknown`)
- `worst_case_notice_class`
- `notifications_state` (`healthy`, `degraded`, `disabled`, `unsupported`, `unknown`)
- `periodic_rescan_interval_sec` nullable
- `startup_rediscovery_state` (`enabled`, `disabled`, `unknown`)
- `manual_rescan_state` (`available`, `recommended`, `required`, `unavailable`)
- `blind_spot_rows[]`
- `trust_floor` (`browse-safe`, `routine-safe`, `destructive-review-required`, `unknown`)
- `stronger_basis_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. subject / path
2. basis class
3. worst-case notice class
4. trust floor
5. next stronger action

Example:

```text
Media/RAW     periodic-rescan     up to 10m     destructive-review-required     Restore live notifications
```

## Non-goals

This page does **not** prove that transfer finished, remote peers fetched the bytes, or hashes are already final.
It proves only the current **freshness basis** for noticing local change.
