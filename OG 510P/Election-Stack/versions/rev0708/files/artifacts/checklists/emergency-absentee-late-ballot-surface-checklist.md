# Emergency absentee / late-ballot surface checklist

- Identify one authoritative public path for emergency absentee / hospitalized-or-incapacitated / late-emergency ballot questions and one fallback help path.
- State which emergency classes are in scope and what timing trigger makes the emergency path available.
- Publish the exact request cutoff and the exact ballot-return cutoff for the emergency path.
- Publish whether a designated representative, clerk deputy, election assistant, or named person may obtain or transport the ballot.
- State which forms, written requests, attestations, or identity checks are required for the voter and any representative.
- Distinguish this late-emergency lane from ordinary absentee-request guidance, ordinary replacement-ballot guidance, and provisional-ballot issuance guidance.
- Publish the fallback instruction for voters who can still appear in person or who miss the emergency-ballot window.
- Check parity across the website, downloadable forms, late-ballot instructions, hotline/help scripts, and office-facing handouts.
- Publish accessible and translated versions where required, plus a fallback phone/help path when the website or forms are unreachable under time pressure.
- Record `last_verified_at`, the current request/return cutoff note, and the latest superseding correction/advisory notice pointer.
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

- Preserve the adjacent-surface boundary against `304`, `317`; do not let this page silently answer those neighboring questions by analogy or copy-over.
- When the case has moved beyond this page's bounded niche, keep `305` as the ordinary-help / current-office confirmation lane and `307` as the rights/safety escalation lane.
- Treat the rule as jurisdiction-specific and time-volatile: verify the current official source, prefer dated / last-updated material, and do not port another state's, county's, jurisdiction's, or facility's answer into this checklist by analogy.

