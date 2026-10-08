# Official voter-information fixed-format identifier-entry surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information routes workable when the public must enter a voter ID, tracking number, case number, license fragment, or other fixed-format identifier before the current answer appears.

## Inventory and review scope

- Identify the critical public-answer routes that depend on a fixed-format or mixed-format public identifier: registration-status lookups, ballot-status checks, provisional-status pages, voter-history lookups, correction routes, and similar identifier-gated help paths.
- Distinguish this from generic field-entry review, date-entry review, address-entry review, and name-entry review.
- Re-check routes whose success depends on leading zeros, exact length, mixed letters and digits, visible separators, or masked review states.

## Identifier semantics, format cues, and keyboard posture

- Say which identifier the office wants before failure occurs.
- State whether letters, spaces, or hyphens are allowed, optional, or required.
- Preserve leading zeros and other meaningful characters.
- Use keyboard hints that fit the token, but do not force number-control semantics onto exact identifier strings.

## Masks, correction, and retry recovery

- If a mask or segmented helper is present, make sure paste and mid-string correction still work.
- Do not silently submit or reroute when the voter finishes typing the last character.
- Preserve entered values across retries; do not clear the field after a failed match.
- Explain whether the problem is format, wrong identifier kind, or no matching record, and keep a plainly visible first-party help path available.

## Evidence posture

- Preserve only route labels, reviewed identifier paths, identifier-kind review state, exact-string/leading-zero review state, mask-and-retry review state, and last review time.
- Do not preserve raw voter IDs, full tracking-number corpora, rejected-token logs tied to real voters, complete lookup-attempt histories, or exhaustive session replay when bounded policy reconstruction is sufficient.
