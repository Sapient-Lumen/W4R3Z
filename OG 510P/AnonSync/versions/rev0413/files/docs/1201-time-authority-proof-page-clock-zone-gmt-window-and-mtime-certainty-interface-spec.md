# Time authority proof page — clock, zone, GMT window, and mtime certainty

## Purpose

Prove how much trust the product can honestly place in modification-time-based chronology right now.
This page exists because `newer` is only meaningful if time authority is explicit.

## The page must answer

1. Are peer clocks and time zones currently trusted?
2. What is the allowed max peer-time delta?
3. Is Sync comparing disk mtimes, database-preserved mtimes, or an uncertain mixture?
4. Is change detection based on normal filesystem notifications, manual touch, or later rescan?
5. What proof grade does the present chronology claim deserve?

## Core fields

### A. Clock posture

Represent exactly one:

- **Trusted clocks / trusted zones**
- **Minor drift observed, still within window**
- **Exceeds allowed window**
- **Timezone likely wrong**
- **Unknown / peer not recently measured**

### B. Allowed window

Always render the actual configured threshold and its source.
Default posture may be shown as `600 seconds`, but the page must publish the effective value rather than assume it.

### C. Mtime authority basis

Represent exactly one:

- disk mtime authoritative
- disk mtime failed, database-retained mtime in play
- detection pending rescan
- detection forced by manual touch
- mixed / uncertain basis

### D. Proof grade

Represent exactly one:

- **Strong chronology proof**
- **Usable but caveated**
- **Blocked until time fixed**
- **Blocked until detection recomputed**
- **Archive rollback still needs runtime witness**

## Required explanations

### Manual touch explanation

The page must say that `touch` or equivalent manual mtime change can force Sync to notice a change, but it does not independently prove authorship or business correctness.

### Database-mtime explanation

When disk mtime cannot be assigned faithfully and a database fallback posture exists, the page must explain that on-disk timestamps may no longer be sufficient witness for later operator reasoning.

### Mobile symptom explanation

When time skew is severe enough to block transfer, the page should explain any surface-specific symptom such as an empty mobile list.

## Required warnings

- `Chronology truth is suspended until peer time is corrected.`
- `Disk timestamps may not be the real authority on this subject.`
- `Touch/rescan can restore observation without proving which edit should win.`
- `A trusted clock is weaker than a trusted chronology verdict when offline-return rules apply.`

## Required outputs

- clock posture
- effective max-diff setting
- mtime authority basis
- proof grade
- next action required to raise proof grade

