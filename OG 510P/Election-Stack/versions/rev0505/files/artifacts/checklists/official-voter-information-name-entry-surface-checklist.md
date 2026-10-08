# Official voter-information name-entry surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information routes workable when the public must enter or confirm a personal name before the current answer appears.

## Inventory and review scope

- Identify the critical public-answer routes that depend on a personal name: registration-status lookups, mail-ballot status checks, provisional-ballot status pages, voter-history lookups, correction routes, and similar name-gated help paths.
- Distinguish this from generic field-entry review, date-entry review, address-entry review, and underlying policy questions about whether a voter is eligible or registered.
- Re-check routes whose success depends on split given/family-name fields, registration-record name matching, title or suffix handling, or a prior-name retry path.

## Name structure and character support

- Prefer a single full-name field when the route does not materially need separate name parts.
- If separate fields are required, label them clearly and do not assume every voter has a middle name or family name.
- Support ordinary punctuation, spaces, diacritics, short names, and long names.
- Do not silently coerce the displayed review text by stripping punctuation, changing case, or truncating the value without explanation.

## Optional parts, record-specific cues, and mismatch recovery

- Do not force title, suffix, or other optional name parts unless the route materially needs them.
- If the office expects the registration-record name, previous name, or another record-specific variant, say so before a failed lookup makes the voter guess.
- Preserve entered values across retries; do not clear the form after a mismatch.
- Keep a plainly visible first-party help path available when the automated matcher remains brittle.

## Evidence posture

- Preserve only route labels, reviewed name paths, name-structure review state, character-support review state, mismatch-recovery review state, and last review time.
- Do not preserve raw personal-name corpora, rejected-name logs tied to real voters, complete lookup-attempt histories, or exhaustive session replay when bounded policy reconstruction is sufficient.
