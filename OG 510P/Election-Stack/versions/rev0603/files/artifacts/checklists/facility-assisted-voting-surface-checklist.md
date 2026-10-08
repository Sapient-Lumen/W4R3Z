# Facility-assisted voting / residential-facility voting surface checklist

- Identify one authoritative public path for voters living in nursing homes, assisted-living facilities, treatment centers, veterans homes, group homes, or other covered residential facilities, plus one authoritative help path for facility-specific uncertainty.
- State which facility categories are covered and whether some categories are routed to a different workflow.
- State clearly what residence address, proof-of-residence, or staff-vouching rule controls registration and assignment for the covered facilities.
- Publish the assistance model explicitly: ordinary absentee only, agent delivery, special voting deputies, multipartisan assistance team, supervised voting, or another named path.
- State who may assist with ballot request, witnessing, marking, sealing, pickup, delivery, or return, and under what public constraints.
- Publish the trigger, scheduling rule, or deadline for activating the facility-specific workflow.
- Link the current form, office, phone number, and any scheduling contact that controls time-sensitive action from the facility.
- Check parity across the elections site, facility handout, PDF flyer, county instructions, and any hotline or FAQ text.
- Preserve accessible, printable, and translated versions where offered, plus a phone/help route when web access is unavailable to the resident.
- Record `last_verified_at`, the current facility-voting summary, and the latest superseding correction/advisory notice pointer.
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

