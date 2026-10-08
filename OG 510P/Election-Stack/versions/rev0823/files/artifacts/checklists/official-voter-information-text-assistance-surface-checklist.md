# Official voter-information text-assistance surface checklist

Use this checklist when an election office operates **public routes where browser/device writing assistance or IME composition can change what appears in a text field before the official answer/help lane is reached**.

## Scope and field-class review

- [ ] Record which reviewed fields are natural-language text, personal-name/place text, exact-string identifiers, digital contact targets, or verification-code fields.
- [ ] Distinguish this surface from generic field-entry labels/help, exact-format identifier rules, and contact-target delivery semantics.
- [ ] Keep exact-string and sensitive-field posture explicit instead of inheriting one global mobile-text behavior across all fields.

## Assistance-hint review

- [ ] Review whether `autocapitalize`, `autocorrect`, and `spellcheck` posture matches the field class rather than form-designer habit.
- [ ] Do not assume a requested assistance hint is universally honored across all browsers, devices, or input methods.
- [ ] Review whether exact identifiers, tracking tokens, one-time codes, or similarly decisive strings are protected from silent mutation.
- [ ] Review whether sensitive fields should avoid spellcheck or similar assistance because of mutation or privacy/security concerns.

## Composition and committed-text review

- [ ] Review whether IME composition is treated as provisional until committed text is available.
- [ ] Do not run decisive validation, lookup, auto-advance, or submit as though mid-composition text were already final.
- [ ] Review paste, voice input, and composition-driven entry paths alongside ordinary keyboard entry.

## Visible review and correction review

- [ ] Keep the visible review state honest about which value will actually drive the lookup or submit.
- [ ] Keep correction possible after browser/device assistance changes a value.
- [ ] Do not let auto-capitalized or auto-corrected text masquerade as though the office itself required that exact mutated value.
- [ ] Keep a bounded first-party help/fallback lane visible when writing-assistance posture still fails.

## Evidence and minimization review

- [ ] Preserve a small public digest of reviewed field classes, assistance posture, composition boundary review, and last review time.
- [ ] Do not preserve raw keystroke logs, full composition-event streams, copied codes, or unnecessary sensitive identifiers merely to prove that text-assistance posture was reviewed.
