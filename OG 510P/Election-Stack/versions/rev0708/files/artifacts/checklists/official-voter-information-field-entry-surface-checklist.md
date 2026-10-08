# Official voter-information field-entry surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information lookup or help routes workable after the voter starts typing, pasting, or autofilling the data needed to reveal the current answer.

## Inventory and review scope

- Identify the critical public-answer routes that require typed, pasted, or autofilled input before the voter can reach the answer lane: registration status, polling-place lookups, ballot-status checks, address validators, district lookups, topic selectors, and contact/help forms.
- Distinguish this from downloadable-form governance, keyboard-only review, screen-reader review, pointer-operability review, and generic mobile polish.
- Re-check routes whose success depends on constrained formatting, remembered values, pasted IDs, mobile keyboards, or brittle date/address/ZIP entry.

## Field purpose, labels, and format cues

- Confirm that each critical field has a task-accurate label and any needed format cue in visible text.
- Do not rely on placeholder-only hints to explain uncommon formats or distinguish similar fields.
- Keep visible labels, helper text, and programmatic field purpose aligned closely enough that the voter can predict what belongs in the field before validation fires.

## Keyboard/input hints, paste, and autofill

- Re-check whether the route presents a sensible entry posture for the expected value type on mobile and other assisted-entry devices.
- Confirm that ordinary pasted or autofilled values can be reviewed and corrected instead of being trapped by masks, silent normalization, or unexpected field collisions.
- Treat masks or inline formatting helpers as subordinate to the answer lane: they may guide entry, but they should not make deletion, paste, or retry materially harder than plain entry.

## Error identification and retry

- Confirm that entry errors identify the affected field and describe the problem in text rather than by color, icon, or generic failure banners alone.
- When a safe correction is known, provide a practical suggestion or example for retry.
- Preserve enough entered information after a failed lookup that the voter can correct the problem without retyping the full query from memory.
- Keep a plainly visible first-party office/help fallback available when the main field-entry path remains brittle.

## Evidence posture

- Preserve only route labels, reviewed input paths, field-purpose review state, input-hint review state, paste/autofill survivability state, error-recovery state, and last review time.
- Do not preserve raw public-entered values, copied IDs, full addresses, autofill contents, keystroke logs, or exhaustive session replay when bounded policy reconstruction is sufficient.
