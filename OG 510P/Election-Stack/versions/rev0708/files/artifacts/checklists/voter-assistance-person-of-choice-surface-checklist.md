# Voter-assistance person-of-choice surface checklist

Use this when reviewing a public voter-help surface for **person-of-choice assistance, interpreter rules, restricted-helper boundaries, and assistance oaths/forms**.

## What the public surface must make easy to answer

- Does it say clearly who may assist the voter and at which step of the process?
- Does it say clearly which helpers are barred?
- Does it say whether an interpreter may be used and under what conditions?
- Does it say whether the assistant or interpreter must sign an oath, affirmation, or form?
- Does it separate person-to-person assistance from general accessibility or translated-materials pages?
- Does it name the office, phone number, or help route that resolves time-sensitive assistance or interpreter questions?

## Quick pass/fail checks

- State plainly who may help and what restricted-helper rule applies.
- State plainly whether the rule covers registration, ballot marking, ballot return, translation, or another bounded step.
- If an oath, affirmation, or form is required, publish it clearly and link it.
- Do not force the reader to infer assistance rules from generic accessibility, language, or escalation pages.
- Check parity across the elections website, assistance/interpreter form, accessibility page, and phone/help channels.
- Preserve accessible, printable, and translated versions where offered, plus a phone/help route for time-sensitive questions.
- Record `last_verified_at`, the who-may-help summary, the restricted-helper summary, and the latest superseding correction/advisory pointer.
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

- Preserve the adjacent-surface boundary against `301`, `302`; do not let this page silently answer those neighboring questions by analogy or copy-over.
- When the case has moved beyond this page's bounded niche, keep `305` as the ordinary-help / current-office confirmation lane and `307` as the rights/safety escalation lane.
- Treat the rule as jurisdiction-specific and time-volatile: verify the current official source, prefer dated / last-updated material, and do not port another state's, county's, jurisdiction's, or facility's answer into this checklist by analogy.

