# Rev333: honest jump feedback

## What changed

Ordinary jump-style navigation commands now report the real landed target instead of succeeding silently:

- `goto line[:col]` → `goto: name @ line:col`
- `jump +/-n[:col]` → `jump: name @ line:col`
- `helpjump QUERY` → `helpjump: name @ line:col`
- `markjump NAME` → `markjump: NAME -> target @ line:col`

This is intentionally tiny. The underlying navigation behavior was already mostly right: `goto` / `jump` were already jumplist-aware, `helpjump` already reused docs-outline matching, and `markjump` already supported cross-buffer jumps. The weak spot was the user-facing confirmation loop. A command could move the cursor somewhere important and still leave the user inferring where it landed.

## Why this matters

This is a **flow/trust** cleanup.

- **Trust**: if a command moved the cursor, the editor should say where. Silent success feels too close to uncertainty.
- **Flow**: navigation should preserve orientation. After a jump, the user should not have to scan the screen just to confirm whether the move landed at the intended place.

This is the same product lens as the recent small passes on startup, replace feedback, save feedback, explicit open feedback, and buffer-orientation feedback.

## Scope discipline

This revision deliberately does **not** add a bigger jump subsystem.

It does not add:
- richer breadcrumbs or semantic location labels
- a larger status/panel/history UI for jump actions
- new jump commands or new prompt types

It only makes existing jump commands tell the truth more clearly.

## Verification

Focused coverage now pins down the message shape for:

- `goto` / `jump` jumplist-aware command-path movement
- `helpjump` docs-heading movement
- `markjump` cross-buffer navigation
- picker-driven mark jumps, so the ordinary marks workflow stays aligned

## Why this was the next move

After rev331 (`open`) and rev332 (buffer movement), the remaining everyday orientation gap was cursor movement inside the current editing session. This is a small change, but it keeps the recent direction coherent: if the editor moved you somewhere meaningful, it should say where you are now.
