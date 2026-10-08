# Accessibility/language publication no-go notice

Archive version: `v900`  
Release date: `2026-06-18`  

**No-go for public release of local voter-facing artifacts until accessibility, language-access, plain-language, fallback, and human-help review is complete. Synthetic-only. This is not live election evidence, not current voter instruction, not public-release authorization, not formal accessibility certification, not a language-coverage determination, and not legal advice.**

## Decision

`NO_GO_PUBLIC_RELEASE_ACCESSIBILITY_LANGUAGE_REVIEW_INCOMPLETE`

The synthetic archive can publish example outputs, but live or local voter-facing artifacts need a separate reviewer-approved usability path. This gate prevents digest-correct and privacy-reviewed evidence from being treated as voter-ready when it lacks accessible text, language parity, alternate formats, low-bandwidth fallback, or safe human help.

## Current accessibility/language state

- Policies: `14`.
- Blocking policies: `14`.
- Missing local approval rows: `14`.
- Release-gate families: `5`.

## Promotion condition

Regenerate this pack with local accessibility and language-access approvals, documented exceptions, source-text parity checks, public/private field separation, and verified human-help routes. Public release remains no-go until every applicable policy row is closed or an accountable local exception is recorded.

## First actions

- `ALP-001` / `public_notice_feed` — Create accessible text and plain-language copies before treating the notice as voter-ready.
- `ALP-002` / `public_status_page` — Run keyboard/focus/heading/form/status-update checks before public promotion.
- `ALP-003` / `language_access_coverage` — Confirm covered and locally supported languages, proofing, oral assistance, and correction parity.
- `ALP-004` / `alternate_formats` — Publish alternate-format request paths and response expectations before relying on the artifact.
- `ALP-005` / `assistive_technology_interoperability` — Run representative screen-reader, keyboard, zoom/reflow, and error-message smoke checks.
- `ALP-006` / `hotline_and_human_help` — Verify human help routes, hours, fallback channels, and minimum-disclosure safety language.
- `ALP-007` / `emergency_notice_parity` — Check emergency publication parity across channels, languages, accessible text, and fallback copies.
- `ALP-008` / `translated_correction_notice` — Propagate supersession and correction status to translated and simplified versions.
- `ALP-009` / `media_and_screenshot_accessibility` — Add captions, transcript, alt text, and body-text equivalent before public release.
- `ALP-010` / `polling_location_and_map_accessibility` — Add text-list location fallback, accessible-route notes, date scope, and non-geolocation lookup.
- `ALP-011` / `ai_assisted_translation_or_summary` — Record source text, human approval, PII discipline, and prohibited-use checks for AI-assisted output.
- `ALP-012` / `intimidation_safety_public_answer` — Route help and preserve evidence while avoiding legal conclusions and unsafe disclosure requests.
- `ALP-013` / `offline_low_bandwidth_copy` — Publish printable or low-bandwidth text with digest, check date, share-safe link, and fallback channel.
- `ALP-014` / `accessibility_language_gate` — Keep public release blocked until each applicable row has local approval or documented exception.

## Boundary

Accessibility/language publication support only; not live election evidence, not current voter instruction, not public-release authorization, not certification, not formal WCAG/ADA conformance, not a Section 203 coverage determination, not a public-records ruling, and not legal advice.
