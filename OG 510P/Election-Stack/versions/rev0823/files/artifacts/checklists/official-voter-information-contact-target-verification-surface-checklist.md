# Official voter-information contact-target and verification-code surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information routes workable when the public must enter a phone number or email address, receive a code, or complete a contact-target confirmation step before the current answer appears.

## Inventory and review scope

- Identify the critical public-answer routes that depend on a voter-entered phone number, email address, or verification code before revealing the next answer/help lane.
- Distinguish this from general office contact-directory publication, generic field-entry review, and fixed-format identifier review.
- Re-check routes whose success depends on SMS delivery, immediate email inbox access, segmented code boxes, resend-code flows, or alternate method changes.

## Contact-method semantics and ordinary entry

- Say whether the route wants a phone number, an email address, or either one.
- State clearly if the route requires a U.S. phone number or an SMS-capable mobile number.
- Tell users why the office needs the contact method and when it may be used.
- Allow ordinary paste of phone numbers and email addresses, and avoid unnecessary re-entry.

## Autofill, code entry, and predictable behavior

- Keep useful autocomplete/input-purpose cues on contact fields.
- If a code is sent, let the code field support paste and accessible review/correction.
- Do not make segmented code boxes the only workable posture.
- Do not silently auto-submit or change context when contact entry or code entry completes unless that behavior is clearly predictable.

## Error recovery and help

- Distinguish malformed contact data, unsupported channel type, delivery failure, expired code, mismatch, and temporary-send throttle states.
- Preserve entered contact data across safe retries; do not clear it by default after a failed verification attempt.
- Keep a plainly visible first-party help or alternate recovery lane available when automated delivery is the weak link.

## Evidence posture

- Preserve only route labels, reviewed contact/code paths, contact-method requirement review state, autofill/paste review state, code-entry/retry review state, and last review time.
- Do not preserve real voter phone numbers, real email addresses, live verification codes, full delivery logs tied to named voters, mailbox contents, or exhaustive session replay when bounded policy reconstruction is sufficient.
