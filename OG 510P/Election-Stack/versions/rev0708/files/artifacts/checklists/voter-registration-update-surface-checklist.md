# Voter-registration-update surface checklist

- Identify one authoritative public path for ordinary voter-registration updates and one authoritative fallback/help path.
- State which change types are accepted through which methods, including address, name, party, signature, mailing-address, or other bounded update classes.
- Publish ordinary deadline semantics and distinguish them from late-move or late-change fallback rules.
- State what the voter should do if they moved close to the election, changed their name close to the election, or changed party affiliation after the ordinary cutover.
- Explain how the voter can confirm that the update landed, such as through a status checker, voter-information card, notice window, or clerk/board contact path.
- Check parity across the update page, registration-status checker, assignment/polling-place surfaces, sample-ballot pages, primary-eligibility pages, FAQs, and hotline/help scripts.
- Treat changed effectivity rules, changed accepted methods, and changed late-fallback instructions as explicit superseding events, not silent edits.
- Publish accessible and translated versions where required, plus an alternate path if the main online update portal is unavailable.
- Do not publish internal transaction logs, DMV records, or unnecessary voter-file details when a bounded public answer plus help path will do.
- Record `last_verified_at`, the latest correction/advisory notice pointer, and the confirmation/help expectation.
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

