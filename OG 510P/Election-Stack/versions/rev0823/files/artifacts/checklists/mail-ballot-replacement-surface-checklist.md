# Mail-ballot replacement surface checklist

- Identify one authoritative public path for replacement-ballot / replacement-envelope / spoilage / nonreceipt questions and one fallback help path.
- State which problem classes are covered: lost, damaged, spoiled, never received, replacement-envelope-only, or another bounded packet issue.
- Publish whether the voter must return, surrender, or affirmatively void the original ballot before a reissued ballot will count.
- State whether a downloadable packet includes a replacement ballot, a replacement envelope only, or another limited component.
- Publish office cutoffs, satellite-office hours, online replacement-request cutoffs, and any representative-delivery or designated-agent paths that are currently valid.
- Distinguish ordinary replacement/reissue from live ballot-status/cure answers and from post-cast provisional-ballot status answers.
- Distinguish early-voting fallback from Election Day fallback, including whether the voter receives a regular ballot or a provisional ballot in each case.
- Check parity across the website, downloadable forms, satellite-office notices, contact directories, FAQs, and hotline/help scripts.
- Publish accessible and translated versions where required, plus a fallback phone/help path when the primary replacement route fails.
- Record `last_verified_at`, the current office/deadline note, and the latest superseding correction/advisory notice pointer.
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

- Preserve the adjacent-surface boundary against `304`, `311`; do not let this page silently answer those neighboring questions by analogy or copy-over.
- When the case has moved beyond this page's bounded niche, keep `305` as the ordinary-help / current-office confirmation lane and `307` as the rights/safety escalation lane.
- Treat the rule as jurisdiction-specific and time-volatile: verify the current official source, prefer dated / last-updated material, and do not port another state's, county's, jurisdiction's, or facility's answer into this checklist by analogy.

