# Package lane page — platform, architecture, and maintenance owner interface spec

## Purpose

The archive already had install-to-ready, control entry, and release-channel guidance.
What it still lacked was one ordinary page for the simpler question:

> which package or install lane belongs to this host, what maintenance system owns future updates, and what exact stop/start ritual preserves continuity for this lane?

Current official Resilio docs make this seam concrete.
They still differentiate manual binaries, repository packages, service installs, custom-storage launches, and multiple platform/architecture package families.
That is useful truth.
It should not be learned only from install guides.

## Core decision

AnonSync must expose one first-class **Package lane** page for every seat and install plan.

The page exists to answer five things in one place:

1. which install lane this seat currently uses or plans to use
2. which platform/architecture packages are compatible
3. who owns future updates for this lane
4. which continuity-preserving stop/start ritual applies
5. whether switching lanes is a harmless maintenance choice or a cutover risk

## Fixed page order

1. **Current lane verdict**
2. **Host compatibility rows**
3. **Maintenance ownership**
4. **Lane-switch consequence**
5. **Safe next actions**

### 1) Current lane verdict

Show:

- `package_lane_page_id`
- seat or plan scope
- current `lane_verdict` (`matched`, `matched-with-review`, `mismatched`, `legacy-lane`, `unknown`)
- strongest honest summary
- last inspection time

The operator must be able to answer:

> what install lane owns this seat right now?

### 2) Host compatibility rows

Show rows for:

- platform
- architecture
- package family
- install lane (`manual-binary`, `repo-managed`, `service-managed`, `container-image`, `vendor-package`, `custom-launch`)
- path / storage assumptions

Each row must say whether the lane is supported, merely detectable, or legacy-only.

### 3) Maintenance ownership

Show:

- who performs updates (`package-manager`, `app-installer`, `manual-replace`, `vendor-firmware`, `operator-script`, `unknown`)
- who owns service start/stop
- where continuity-critical parameters live
- whether default update instructions are safe for this lane

This section must keep `download newer binary` from impersonating the right answer for every seat.

### 4) Lane-switch consequence

Show:

- whether switching lanes preserves storage root, config root, and service identity
- whether a lane switch changes maintenance owner
- whether a lane switch needs export/reimport
- whether a lane switch widens or narrows support guarantees

The page must answer:

> is changing install lane just maintenance, or is it a real cutover?

### 5) Safe next actions

Actions may include:

- `Stay on current lane`
- `Review lane switch`
- `Open install target`
- `Open upgrade gate`
- `Export lane receipt`
- `Document custom launch contract`

Each action must preview what continuity assumptions it preserves.

## Public object

### Package lane page

Fields:

- `package_lane_page_id`
- `seat_ref` nullable
- `plan_ref` nullable
- `current_lane`
- `host_compatibility_rows[]`
- `maintenance_owner`
- `lane_switch_findings[]`
- `safe_next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. seat
2. current lane
3. maintenance owner
4. strongest lane risk
5. next least-surprising action

Example:

```text
desk-linux-01     repo-managed     package-manager     custom storage contract present     Export lane receipt
```

## Non-goals

This page does **not** replace release-family eligibility or cohort skew review.
It proves only **which install lane is in force and what maintenance/cutover truth follows from that lane**.
