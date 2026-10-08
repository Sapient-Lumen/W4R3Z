# Browser history witness

GlassTTY should treat browser history and route continuity as first-class evidence.

## Why

Many target surfaces are single-page apps. A meaningful workflow can change:
- path
- query
- hash
- in-memory route state
- modal/overlay ownership
- history stack shape

without looking like a classic full-page navigation.

If GlassTTY does not capture this, it can misclassify:
- route drift as success
- soft redirects as stable context
- modal takeover as “same page” continuity
- back/forward breakage as harmless noise

## Witness fields

A browser-history witness should capture, when available:

### Before
- `url_before`
- `route_hint_before`
- `title_before`
- `history_length_before`
- `modal_or_overlay_before`
- `conversation_id_before` or equivalent surface key context

### After
- `url_after`
- `route_hint_after`
- `title_after`
- `history_length_after`
- `modal_or_overlay_after`
- `conversation_id_after` or equivalent surface key context

### Delta summary
- `changed_url`
- `changed_route_hint`
- `history_length_delta`
- `same_document_navigation_likely`
- `back_restored_prior_state`
- `forward_restored_prior_state`
- `navigation_confidence`
- `notes`

## Where this matters most

- `surface-detect`
- `turn-submit`
- `latest-turn-read`
- support captures during route drift incidents

## Minimum rule

When a workflow could change visible conversation context, GlassTTY should preserve at least:
- before URL/route hint
- after URL/route hint
- whether history stack continuity appears intact
- whether a modal/overlay displaced the expected surface state

## Failure language

Prefer:
- “submit activation observed but navigation truth is ambiguous”
- “same-document route change detected; support claim not strengthened”
- “back/forward did not restore the pre-submit state cleanly”

Avoid:
- “same page, so nothing changed”
- “submit succeeded” when only a transient route cue was seen
