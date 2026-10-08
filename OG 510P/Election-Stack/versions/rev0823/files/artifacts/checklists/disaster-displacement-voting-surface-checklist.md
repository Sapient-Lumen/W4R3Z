# Disaster displacement voting surface checklist

Use this when reviewing a public voter-help surface for **temporary disaster displacement, evacuation, or temporary relocation**.

## What the public surface must make easy to answer

- Does the voter keep the permanent residential/home address for voting purposes when the displacement is temporary?
- Does the voter add or change only a temporary mailing address, and how?
- Does the public surface clearly distinguish temporary displacement from permanent relocation?
- Does the public surface say whether ballots can be forwarded, picked up, or rerouted?
- Does it point to replacement-ballot, remote-accessible-ballot, drop-box, vote-center, or other fallback paths if ordinary delivery fails?
- Does it name the office, phone number, or help route that resolves time-sensitive displacement questions?

## Quick pass/fail checks

- State clearly whether temporary displacement does **not** require changing the permanent residential voting address, if that is the rule.
- State clearly what changes if the displacement has become permanent.
- Publish exactly how to provide a temporary mailing address and by what current method or deadline.
- Say plainly if ballots are not forwardable or if post-office pickup, hold, or other delivery fallback is required.
- Link the current replacement-ballot, remote-access, drop-box, vote-center, and/or office-help path when delivery is at risk.
- Check parity across the elections website, FAQ, factsheet/PDF, and phone/help channels.
- Preserve accessible, printable, and translated versions where offered, plus a phone/help route for voters with disrupted connectivity.
- Record `last_verified_at`, the current temporary-displacement summary, the mailing/delivery fallback summary, and the latest superseding correction/advisory pointer.
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

- Preserve the adjacent-surface boundary against `318`, `324`; do not let this page silently answer those neighboring questions by analogy or copy-over.
- When the case has moved beyond this page's bounded niche, keep `305` as the ordinary-help / current-office confirmation lane and `307` as the rights/safety escalation lane.
- Treat the rule as jurisdiction-specific and time-volatile: verify the current official source, prefer dated / last-updated material, and do not port another state's, county's, jurisdiction's, or facility's answer into this checklist by analogy.

