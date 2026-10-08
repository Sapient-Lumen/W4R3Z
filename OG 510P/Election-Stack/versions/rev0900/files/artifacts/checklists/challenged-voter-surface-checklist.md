# Challenged-voter surface checklist

Use this when reviewing a public voter-help surface for **challenged-voter procedure, challenge affidavits/oaths, witness rules, and fail-safe ballot rights**.

## What the public surface must make easy to answer

- Does it say clearly who may challenge a voter and on what basis?
- Does it say clearly whether the voter may answer questions, sign an oath or affidavit, or produce a witness and still receive a regular ballot?
- Does it say clearly which challenged, affidavit, or provisional ballot path applies if the challenge is not cured or remains unresolved?
- Does it say who decides the immediate ballot path and whether later review exists?
- Does it separate ordinary challenge procedure from generic complaint/escalation pages?
- Does it name the office, phone number, or help route that resolves time-sensitive challenged-voter questions?

## Quick pass/fail checks

- State plainly which challenge bases are allowed and who may enter a challenge.
- State plainly whether the voter can cure the challenge and still receive a regular ballot.
- If an oath, affidavit, or witness step is required, publish it clearly and link it.
- State plainly which fail-safe ballot path applies if the challenge is not cured.
- Do not force the reader to infer challenge procedure from provisional-ballot pages, statutes, or complaint pages alone.
- Check parity across the elections website, challenge-affidavit form, posted rights materials, handbook excerpts, and phone/help channels.
- Preserve accessible, printable, and translated versions where offered, plus a phone/help route for same-day challenge questions.
- Record `last_verified_at`, the challenge-bases summary, the cure-path summary, the fail-safe-ballot summary, and the latest superseding correction/advisory pointer.
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

- Preserve the adjacent-surface boundary against `321`, `307`; do not let this page silently answer those neighboring questions by analogy or copy-over.
- When the case has moved beyond this page's bounded niche, keep `305` as the ordinary-help / current-office confirmation lane and `307` as the rights/safety escalation lane.
- Treat the rule as jurisdiction-specific and time-volatile: verify the current official source, prefer dated / last-updated material, and do not port another state's, county's, jurisdiction's, or facility's answer into this checklist by analogy.

