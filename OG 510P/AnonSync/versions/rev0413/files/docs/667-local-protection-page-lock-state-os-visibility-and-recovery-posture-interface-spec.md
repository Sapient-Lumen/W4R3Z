# Local protection page — lock state, OS visibility, and recovery posture interface spec

## Purpose

This page answers one ordinary question:

> when local protection is enabled for this seat or subject, what exactly becomes gated, what operating-system surfaces stop seeing the data, what edit lanes still work, and what recovery cliff exists if the local secret is lost?

The page exists because `protected`, `hidden from Recents`, `editable in another app`, and `recoverable later` are not interchangeable.
The operator needs one direct statement of what the local-protection posture really means.

## Core decision

Every seat or subject whose local data can be app-locked, PIN-gated, or biometrically gated must render one first-class **Local protection** page.
The page owns:

- current local lock posture
- OS-surface visibility consequences
- external-edit lane class
- local-only data at risk if recovery fails
- strongest safe sentence for this protection state

## Primary layout

The page always renders the same regions in the same order:

1. protection strip
2. gated-surface matrix
3. OS visibility card
4. external-edit lane card
5. recovery posture card
6. receipts

### 1) Protection strip

Show:

- seat label
- subject scope (`whole app`, `selected shares`, `selected exports`, `unknown`)
- protection class (`none`, `pin`, `biometric+pin`, `device-key-only`, `unknown`)
- protection state (`off`, `on`, `temporarily bypassed`, `locked-out`, `unknown`)
- one honest next action

### 2) Gated-surface matrix

Render rows for these capability families:

- open data inside AnonSync
- expose items in OS `Recents` / provider recency surfaces
- hand off to outside apps
- receive modified bytes back into the authoritative share
- clear local copies
- export or reveal file location
- recover after forgotten local secret

Columns:

- `current yes/no`
- `basis`
- `scope`
- `stronger claim forbidden?`
- `receipt wording`

The product must not compress these rows into one `protected` badge.

### 3) OS visibility card

This card publishes:

- whether the OS may show these files in Recents
- whether provider-backed browsing remains visible
- whether the data remains only app-local / sandbox-local
- whether file paths remain meaningful outside the app
- whether any previously exposed hints may persist until OS recency clears

The operator must be able to answer: **what system surfaces still know these files exist?**

### 4) External-edit lane card

This card publishes:

- edit lane class (`live-provider`, `copy-return`, `copy-branch`, `blocked`, `unknown`)
- whether edits happen against the authoritative bytes or a temporary copy
- whether the original can be replaced automatically
- whether duplicate old/new versions are expected
- minimum permission required to commit the modified version back

The operator must be able to answer: **what really happens if I edit this in another app?**

### 5) Recovery posture card

This card publishes:

- forgotten-secret consequence (`re-enter secret`, `device auth fallback`, `supportless lockout`, `reinstall-required`, `unknown`)
- whether local-only bytes would be lost
- whether replicated bytes remain available on other peers
- whether any local service state or receipts survive reinstall
- strongest honest sentence about recovery ceiling

The operator must be able to answer: **if I lose the local secret, what exactly do I lose?**

### 6) Receipts

Show the latest protection receipt, reviewed changes, lockout events, and whether the current posture is native or workaround-shaped.

## Public object

### `local_protection_explainer`

Fields:

- `local_protection_explainer_id`
- `seat_ref`
- `subject_scope`
- `protection_class`
- `protection_state`
- `gated_surface_rows[]`
- `os_visibility_rows[]`
- `external_edit_lane`
- `recovery_posture`
- `local_only_risk_rows[]`
- `claim_ceiling`
- `generated_at`

## Non-negotiable rules

### Rule 1 — protection must never overclaim invisibility

If Recents is hidden but other OS/provider surfaces may still expose the data, the page must say so directly.

### Rule 2 — external editing must never overclaim live authority

If outside-app editing is copy-return or branch-shaped, the page must say that directly and must not imply live in-place editing.

### Rule 3 — recovery must separate local-only loss from replicated safety

`Protected` must never imply `recoverable`.
If forgetting the local secret can force reinstall or local-only byte loss, that must appear on the same page as the protection toggle.

## Honest outputs

The page may conclude:

- `Protection is ON for this app. Files no longer appear in OS Recents, but replicated bytes still exist on other peers.`
- `External editing currently uses copy-return. Outside apps edit a copy, and the modified version must be sent back explicitly.`
- `Recovery ceiling is local-only. Forgetting the local secret would require reinstall and lose local in-app bytes not yet safely replicated elsewhere.`

It may not flatten those truths into `private mode`, `secure`, or `editable externally` alone.
