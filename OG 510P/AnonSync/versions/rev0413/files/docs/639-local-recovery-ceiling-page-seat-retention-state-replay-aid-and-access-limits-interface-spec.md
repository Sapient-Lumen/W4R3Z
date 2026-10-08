# Local recovery ceiling page — seat retention state, replay aid, and access limits interface spec

## Purpose

This page owns the next question after Archive policy or recovery witness scope is in doubt:

> from this exact seat and surface, what is the strongest recovery or replay help I can honestly claim right now?

This page exists so `Archive on`, `history available`, or `Use Archive` never stand in for actual local recovery power.

## Core decision

Any seat/surface combination where recovery or replay help varies by platform, path class, or control surface must expose one first-class **Local recovery ceiling** page.

## Fixed page order

1. **Ceiling verdict strip**
2. **Seat-local witness classes**
3. **Access limits**
4. **Replay assistance summary**
5. **Other-witness map**
6. **Safe language**

### 1) Ceiling verdict strip

Show:

- seat and surface in scope
- current recovery ceiling
- strongest safe sentence

Example verdicts:

- `Direct local Archive recovery available on this seat`
- `Retention exists but access is hidden-path only here`
- `No direct local Archive access on this surface; use another witness seat`
- `Archive disabled here; local recovery ceiling is none`

### 2) Seat-local witness classes

For each witness class show whether it is present here now:

- `prior-version-bytes`
- `deleted-item-bytes`
- `rename-replay-aid`
- `copy-replay-aid`
- `none`

Also show:

- retention horizon
- strongest local access method
- whether the class is future-only or currently populated

### 3) Access limits

Show:

- platform/path caveats
- surface caveats (desktop UI, WebUI, hidden-path only, unavailable)
- whether current storage location blocks Archive operation
- whether restore from here is direct, manual-only, indirect, or unavailable

### 4) Replay assistance summary

Show whether this seat can still help avoid re-download for:

- rename replay
- copy replay
- restore replay

Each row should show:

- current assistance class (`strong`, `guarded`, `none`, `unknown`)
- what policy or platform limit drives it

### 5) Other-witness map

Show stronger or equivalent witnesses elsewhere:

- seat ref
- witness class
- access grade
- retention horizon if known

This section prevents one weak seat from impersonating the whole constellation's recovery posture.

### 6) Safe language

Always show both:

- strongest safe sentence
- stronger rejected sentence

Example:

- `This seat currently keeps direct Archive-backed rename replay aid for this share.`
- `This page does not prove that every seat or surface in the constellation can recover the same bytes locally.`

## Public object

### `local_recovery_ceiling_page`

Fields:

- `local_recovery_ceiling_page_id`
- `seat_ref`
- `surface_ref`
- `subject_ref`
- `recovery_ceiling`
- `witness_rows[]`
- `access_limit_rows[]`
- `replay_assistance_rows[]`
- `other_witness_rows[]`
- `generated_at`

## Result

A good local recovery ceiling page prevents five failures:

- local Archive presence being confused with constellation-wide parity
- mobile/path-class caveats being rediscovered too late
- rename replay aid being confused with direct restore access
- hidden-path access being mistaken for ordinary UI support
- support and future operators having to reconstruct witness locality from folklore
