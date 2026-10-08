# Location-eligibility-model surface checklist

- Identify one authoritative public surface that states whether voters may use any countywide site, any vote center, an assigned subset of centers, or only one assigned precinct/poll site.
- State the rule separately for early voting, Election Day, and any special-election or runoff phase if the model differs by phase.
- Make it explicit whether a poll-site finder is exclusive, advisory, or binding only for a specific phase or voter class.
- Publish explicit superseding notices when a county starts or stops using vote centers, changes assigned-site rules, or changes district-only exceptions.
- Check parity across site directories, vote-center pages, poll-site finders, hotline/help scripts, PDFs, and closure/change notices.
- Do not force voters to infer the model by combining an hours page with a site list and a precinct lookup; state the model directly.
- Publish accessible and translated versions where required, plus a fallback phone/in-person help path if the main web surface is unavailable.
- Do not publish internal siting, staffing, or security details when a bounded public rule statement plus site pointers will do.
- Record `last_verified_at`, the latest correction/advisory notice pointer, and any current countywide-voting or assigned-site exception note.
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

- Preserve the adjacent-surface boundary against `292`, `297`; do not let this page silently answer those neighboring questions by analogy or copy-over.
- When the case has moved beyond this page's bounded niche, keep `305` as the ordinary-help / current-office confirmation lane and `307` as the rights/safety escalation lane.
- Treat the rule as jurisdiction-specific and time-volatile: verify the current official source, prefer dated / last-updated material, and do not port another state's, county's, jurisdiction's, or facility's answer into this checklist by analogy.

