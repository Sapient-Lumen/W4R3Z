# Signature-alternatives voting surface checklist

Use this when reviewing a public voter-help surface for **signature alternatives, mark/witness rules, signature stamps, typed/digital signatures, and signature-cure/update paths**.

## What the public surface must make easy to answer

- Does it say clearly which substitute counts here: mark, witnessed mark, signature stamp, typed signature, digital signature, attorney-in-fact authorization, or another official substitute?
- Does it say which workflow step the rule applies to: registration, request, return, cure, update, accessible portal, or precinct register?
- Does it say whether a witness, assistant, or other supporting signer is required and what that person must do?
- Does it say whether the voter may update the signature on file or cure a mismatch through a special statement or other official method?
- Does it say whether an accessible absentee or remote ballot workflow offers a typed or digital signature path?
- Does it name the office, phone number, or help route that resolves time-sensitive signature-alternatives questions?

## Quick pass/fail checks

- State plainly which substitute is valid now; do not force the voter to infer the answer from generic accessibility or cure pages.
- Separate registration, request, return, and cure/update rules when the signature substitute differs by workflow step.
- If a witness or assistant is required, state exactly what that person must add.
- If a signature stamp or mark may be used for future elections, say how the voter updates the registration record or signature on file.
- If a typed or digital signature is allowed only in a specific accessible workflow, say so plainly and link it.
- Check parity across the elections website, cure/update form, accessible-ballot instructions, and phone/help channels.
- Preserve accessible, printable, and translated versions where offered, plus a phone/help route for deadline-sensitive cure questions.
- Record `last_verified_at`, the accepted-substitutes summary, the workflow-scope summary, and the latest superseding correction/advisory pointer.
## High-risk routing/control backstop

- Expose `authoritative_help_uri` and/or `authoritative_help_phone`; preserve `305` for ordinary-help confirmation and `307` for rights/safety escalation.
- Record `authoritative_office_name` and `authoritative_office_scope` so the responsible official office is explicit and jurisdiction-matched.
- Record `official_secure_channel_note` and `minimum_necessary_disclosure_note`; use official secure channels and avoid oversharing sensitive identifiers.
- Record `operability_now_note` and `deadline_imminence_note`; verify the named office/path is still live right now under same-day or near-cutoff pressure.

## High-risk freshness/current-state/conflict backstop

- Record `last_verified_at`, `source_review_window_days`, and `latest_notice_uri`; keep the high-risk surface inside the bounded review window and point to the newest controlling public notice or update.
- Record `current_official_controls_note`; say the current directly governing state/local election-office source controls and that national/generalized/archive summaries are routing aids rather than substitutes.
- Record `superseding_notice_note`; when older pages, PDFs, screenshots, or inserts remain visible, tell readers to follow the newer official correction, update, replacement, or last-updated instruction.
- Record `unresolved_conflict_stop_note`; do not synthesize an answer from unresolved official conflict — use the responsible office or `305` help path for confirmation and preserve `307` when the conflict is paired with rights/safety risk.
## High-risk boundary/portability backstop

- Preserve the adjacent-surface boundary against `301`, `311`; do not let this page silently answer those neighboring questions by analogy or copy-over.
- When the case has moved beyond this page's bounded niche, keep `305` as the ordinary-help / current-office confirmation lane and `307` as the rights/safety escalation lane.
- Treat the rule as jurisdiction-specific and time-volatile: verify the current official source, prefer dated / last-updated material, and do not port another state's, county's, jurisdiction's, or facility's answer into this checklist by analogy.

