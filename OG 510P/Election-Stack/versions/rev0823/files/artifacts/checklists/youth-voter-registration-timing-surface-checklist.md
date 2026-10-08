# Youth-voter registration timing surface checklist

Use this when reviewing a public voter-help surface for **youth pre-registration, future-voter status, turning-18 timing, and primary-before-general eligibility**.

## What the public surface must make easy to answer

- Does it say clearly when a 16- or 17-year-old may pre-register or register?
- Does it say when that record becomes active for voting?
- Does it say whether a 17-year-old may vote in a primary before turning 18 because the voter will be 18 by the general election?
- Does it say whether the young voter should use an ordinary registration workflow or a future-voter/pre-registration workflow?
- Does it separate age timing from party-primary, same-day-registration, or ordinary update rules?
- Does it name the office, phone number, or help route that resolves time-sensitive youth-registration timing questions?

## Quick pass/fail checks

- State plainly the minimum age to pre-register or register.
- State plainly when a pre-registered or future-voter record becomes active.
- If a by-the-general-election rule allows 17-year-olds to vote in a primary, publish it clearly and link it.
- Do not force the reader to infer youth eligibility timing from generic registration, status, or primary pages.
- Check parity across the registration page, youth-program page, FAQ, and phone/help channels.
- Preserve accessible, printable, and translated versions where offered, plus a phone/help route for deadline-sensitive questions.
- Record `last_verified_at`, the age-threshold summary, the activation summary, and the latest superseding correction/advisory pointer.
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

- Preserve the adjacent-surface boundary against `294`, `303`; do not let this page silently answer those neighboring questions by analogy or copy-over.
- When the case has moved beyond this page's bounded niche, keep `305` as the ordinary-help / current-office confirmation lane and `307` as the rights/safety escalation lane.
- Treat the rule as jurisdiction-specific and time-volatile: verify the current official source, prefer dated / last-updated material, and do not port another state's, county's, jurisdiction's, or facility's answer into this checklist by analogy.

