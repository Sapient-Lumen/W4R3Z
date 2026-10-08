# Ballot-handoff / agent-bearer surface checklist

Use this when reviewing a public voter-help surface for **ballot return by another person, designated-agent or bearer rules, and ballot-custody handoff boundaries**.

## What the public surface must make easy to answer

- Does it say clearly who may move, deposit, or return ballot materials for the voter at each step?
- Does it say whether the rule applies to ballot pickup, delivery to the voter, drop-box deposit, mailing, or hand delivery to the election office?
- Does it say what authorization section, oath, envelope certification, or separate form must be completed?
- Does it say which helpers are barred or specially restricted, and whether compensation rules apply?
- Does it separate ordinary return methods from special agent, bearer, or emergency representative paths?
- Does it name the office, phone number, or help route that resolves time-sensitive handoff questions?

## Quick pass/fail checks

- State plainly whether another person may return the ballot and by which methods.
- State plainly when only the voter may act personally.
- If a designated-agent or bearer form is required, publish it clearly and link it.
- If compensation, candidate, age, or household restrictions apply, say so plainly.
- Do not force the reader to infer the handoff rule from generic return instructions, assistance pages, or enforcement memos.
- Check parity across the elections website, agent/bearer form, return instructions, and phone/help channels.
- Preserve accessible, printable, and translated versions where offered, plus a phone/help route for close-to-deadline handoff questions.
- Record `last_verified_at`, the who-may-return summary, the authorization/form summary, and the latest superseding correction/advisory pointer.
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

- Preserve the adjacent-surface boundary against `311`, `341`; do not let this page silently answer those neighboring questions by analogy or copy-over.
- When the case has moved beyond this page's bounded niche, keep `305` as the ordinary-help / current-office confirmation lane and `307` as the rights/safety escalation lane.
- Treat the rule as jurisdiction-specific and time-volatile: verify the current official source, prefer dated / last-updated material, and do not port another state's, county's, jurisdiction's, or facility's answer into this checklist by analogy.

