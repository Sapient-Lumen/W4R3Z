# Provisional-ballot-issuance surface checklist

- Identify one authoritative public surface that states why a voter may be issued a provisional ballot before casting.
- Publish the bounded voter-facing reasons that can trigger provisional-ballot issuance, not just a generic “eligibility uncertain” label.
- State when the voter should go to the correct precinct, county, or site instead of assuming a provisional ballot at the current site is the only option.
- State whether the ballot can be fully counted, partially counted, statewide-only counted, or not counted for each important reason/location combination.
- Publish the immediate voter instructions that matter before casting: affidavit, ID follow-up, address proof, surrender requirement, or other required action.
- Point clearly to the official post-cast status/free-access surface and any help or complaint path that takes over after the ballot is issued.
- Check parity across websites, posted notices, poll-worker handouts, hotline/help scripts, and poll-site finder guidance.
- Treat changed issuance reasons, wrong-place semantics, and partial-count consequences as explicit superseding notices, not silent edits.
- Publish accessible and translated versions where required, plus a fallback phone/in-person help path if the main web surface is unavailable.
- Record `last_verified_at`, the latest correction/advisory notice pointer, and any special extended-hours or court-order note that changes provisional-ballot issuance rules.
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

- Preserve the adjacent-surface boundary against `296`, `300`; do not let this page silently answer those neighboring questions by analogy or copy-over.
- When the case has moved beyond this page's bounded niche, keep `305` as the ordinary-help / current-office confirmation lane and `307` as the rights/safety escalation lane.
- Treat the rule as jurisdiction-specific and time-volatile: verify the current official source, prefer dated / last-updated material, and do not port another state's, county's, jurisdiction's, or facility's answer into this checklist by analogy.

