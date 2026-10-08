# Confidential voter registration / protected-address voting surface checklist

- Identify one authoritative public path for confidential voter registration or protected-address voting and one authoritative help path for safety-program uncertainty.
- State whether the voter must first enroll in a named Safe at Home, ACP, or similar address-confidentiality program.
- State clearly which ordinary public tools the voter should avoid if using them would expose the address or defeat the protection.
- State what parts of the voter record remain out of public disclosure.
- State how precinct, district, or political-subdivision assignment is still determined while the residence remains protected.
- Publish the ballot-routing model explicitly: ordinary protected-records voting, special ballot by mail, separate confidential ballot application, or another current path.
- Link the current form, office, and deadline or defect-correction path that controls time-sensitive action.
- Check parity across the elections site, confidentiality-program site, county instructions, forms, and any hotline or FAQ text.
- Preserve accessible and translated versions where offered, plus a phone/help route when the web path is unsafe or unavailable.
- Record `last_verified_at`, current protected-path summary, and the latest superseding correction/advisory notice pointer.
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

