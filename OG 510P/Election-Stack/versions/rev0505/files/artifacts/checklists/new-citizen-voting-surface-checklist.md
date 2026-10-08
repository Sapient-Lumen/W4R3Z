# New-citizen voting surface checklist

Use this when reviewing a public voter-help surface for **new citizens and newly naturalized voters**.

## What the public surface must make easy to answer

- Does it say clearly that a person must not register before citizenship is complete?
- Does it say what changes once the oath or naturalization ceremony occurs?
- Does it say whether the ordinary registration path, same-day registration, or a late-naturalization exception controls now?
- Does it say what proof, certificate, declaration, or in-person office visit is required?
- Does it say whether the online/DMV path is usable immediately or whether a paper/in-person fallback is safer?
- Does it name the office, phone number, or help route that resolves close-to-deadline or proof questions?

## Quick pass/fail checks

- State plainly that registration before citizenship is not allowed.
- State plainly what a newly naturalized voter should do next, not just the general eligibility rule.
- If the jurisdiction has a special late-naturalization exception or same-day-registration path, publish it clearly and link it.
- If proof of naturalization, ceremony timing, or a declaration is required, say so plainly.
- If the ordinary online/DMV workflow is not immediately available for new citizens, publish the paper or in-person fallback.
- Check parity across the elections website, FAQ, flyer/PDF, and phone/help channels.
- Preserve accessible, printable, and translated versions where offered, plus a phone/help route for ceremony-adjacent questions.
- Record `last_verified_at`, the current post-naturalization registration summary, the proof/in-person summary, and the latest superseding correction/advisory pointer.
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

- Preserve the adjacent-surface boundary against `303`, `318`; do not let this page silently answer those neighboring questions by analogy or copy-over.
- When the case has moved beyond this page's bounded niche, keep `305` as the ordinary-help / current-office confirmation lane and `307` as the rights/safety escalation lane.
- Treat the rule as jurisdiction-specific and time-volatile: verify the current official source, prefer dated / last-updated material, and do not port another state's, county's, jurisdiction's, or facility's answer into this checklist by analogy.

