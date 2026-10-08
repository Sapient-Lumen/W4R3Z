# Conviction-related voting eligibility surface checklist

- Identify one authoritative public path for conviction-related voting eligibility and one authoritative help or restoration path when the answer is uncertain.
- State which conviction-related conditions matter publicly: incarceration, parole/probation/supervision, financial terms ordered in the sentence, election-offense exceptions, and any special treatment of out-of-state or federal convictions.
- State whether rights are unaffected, automatically restored, restored on sentence completion, or available only through petition / clemency / individualized review.
- State whether the voter must register or re-register after rights are restored.
- State which office, clerk, court, election office, or restoration authority the voter should contact when sentence completion or conviction class is unclear.
- Distinguish this surface from ordinary registration-status, inactive/removed-status, and update-of-record surfaces.
- Check parity across the dedicated eligibility page, registration portal, FAQ/help page, brochure/PDF, hotline/contact listing, and any public restoration tool.
- Publish accessible and translated versions where required, plus a fallback phone/help path when the web tool or registration portal is unavailable.
- Record `last_verified_at`, the current effective rule summary, and the latest superseding correction/advisory notice pointer.
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

- Preserve the adjacent-surface boundary against `294`, `318`; do not let this page silently answer those neighboring questions by analogy or copy-over.
- When the case has moved beyond this page's bounded niche, keep `305` as the ordinary-help / current-office confirmation lane and `307` as the rights/safety escalation lane.
- Treat the rule as jurisdiction-specific and time-volatile: verify the current official source, prefer dated / last-updated material, and do not port another state's, county's, jurisdiction's, or facility's answer into this checklist by analogy.

