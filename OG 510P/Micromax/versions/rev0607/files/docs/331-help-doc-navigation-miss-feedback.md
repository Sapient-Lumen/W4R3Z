# Rev389: docs-navigation doc misses use the direct help-doc dialect

## Why this exists

Rev382 already cleaned up direct docs lookup misses:

- `help docs TOPIC`

failed as:

- `help docs: no such doc: TOPIC`

That was a good tiny trust-first move because it kept the surface (`help docs`) and the noun (`doc`) visible at the point of failure.

But the docs browser still had two older navigation-side fallbacks:

- `helpfollow` on an internal docs link whose target page does not exist
- `helpback` when the saved docs topic no longer resolves

Those still said `help: no doc for ...`. That wording was understandable, but it drifted away from the newer typed help dialect and made docs browsing feel a little less inspectable than docs lookup.

## Rev389 rule

Docs navigation misses should use the same typed doc-miss wording as direct docs lookup.

Use:

- `help docs: no such doc: TOPIC`

for both direct lookup and navigation-side doc-resolution failures.

## What changed

Rev389 updates two tiny navigation paths in `Editor`:

- `helpback` when the stored docs topic no longer resolves
- `_follow_help_link(...)` when an internal docs link points at a missing docs topic/path

Both paths now report:

- `help docs: no such doc: TOPIC`

instead of the older `help: no doc for TOPIC`.

## Why this is the right-sized move

This is intentionally tiny. It does not change docs resolution, help-stack behavior, or markdown parsing. It only makes the failure dialect consistent across the same user-visible surface.

That helps both:

- **trust**, because the docs/help browser now names the failing surface and noun directly
- **flow**, because logs and automated traces stay easier to scan when docs navigation breaks

## Verification

Focused tests pin down both navigation-side miss paths:

- missing internal docs link via `helpfollow`
- stale back-stack topic via `helpback`

See:

- `tests/test_editor_help_docs_navigation.py`
