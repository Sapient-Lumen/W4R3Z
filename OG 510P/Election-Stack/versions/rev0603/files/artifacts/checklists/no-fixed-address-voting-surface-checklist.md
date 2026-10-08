# No-fixed-address / homelessness voting surface checklist

- Identify one authoritative public path for voters who do not have a fixed address and one authoritative help path when the answer is uncertain.
- State what can be used as a voting residence: last residence, shelter, cross-streets, park/encampment description, or another bounded local rule.
- State separately what mailing address or delivery path is acceptable for ballots and election mail.
- State clearly that residence drives precinct/district/polling-place assignment, not merely the mailing address.
- Publish an explicit fallback when ordinary mail delivery is not reliable: pickup, replacement-ballot printing, in-person voting, or another official path.
- Link the current registration deadline and any same-day / conditional / in-person late-help path that can still save the voter’s ballot opportunity.
- Check parity across the dedicated special-circumstances page, registration portal help text, translated flyers, FAQ pages, and office-contact listings.
- Preserve translated and accessible versions where offered, plus a phone/help route when the web path is unavailable.
- Record `last_verified_at`, the current residence-and-delivery rule summary, and the latest superseding correction/advisory notice pointer.
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

- Preserve the adjacent-surface boundary against `318`, `304`; do not let this page silently answer those neighboring questions by analogy or copy-over.
- When the case has moved beyond this page's bounded niche, keep `305` as the ordinary-help / current-office confirmation lane and `307` as the rights/safety escalation lane.
- Treat the rule as jurisdiction-specific and time-volatile: verify the current official source, prefer dated / last-updated material, and do not port another state's, county's, jurisdiction's, or facility's answer into this checklist by analogy.

