# Rev335: help/doc navigation feedback

## Why this exists

Rev331–rev334 already pushed one small but important editor rule: when a command or picker moves you somewhere meaningful, it should report the real landed target instead of merely succeeding.

That work had already reached:

- explicit file opens (`open ...`)
- buffer switching / close flows
- jump-style cursor movement
- picker-driven jumplist/docs navigation

But ordinary help/doc browsing still had a quieter split-brain path. These already worked:

- `help docs TOPIC`
- docs-fallback `help QUERY`
- `helppick` / `docpick` submission
- `helpfollow` for internal docs links
- `helpback`

Yet several of those success paths still changed the page or cursor without saying where the user landed.

That is small, but it matters: the editor's own docs browser is part of the product. If it feels more tacit than file or buffer navigation, the editor feels less trustworthy than it already is.

## Rev335 rule

Successful docs-opening flows should report the real landed help target.

Use:

- `help: topic @ line:col` for page-opening / page-restoring flows
- `helpjump: topic @ line:col` for successful internal docs-link following

The intent is not verbosity. The intent is orientation.

## What changed

Rev335 now makes these success paths explicit:

- `help docs TOPIC`
- docs-fallback `help QUERY`
- `helppick` / `docpick` submission
- `helpfollow` for successful internal docs navigation
- `helpback`

The target label uses the current help-doc topic when available, so the message stays short and doc-oriented (`vision @ 1:0`) instead of falling back to a noisier file path unless needed.

## Why this is the right-sized move

This is intentionally tiny. It does not add a new subsystem. It just closes one more ordinary success-path honesty gap.

That keeps the repo aligned with the current sequencing:

1. trust first
2. taste second
3. flow third

This change primarily helps **trust** and **flow**:

- trust, because the editor tells the truth about where it actually took you
- flow, because the user spends less time re-orienting after docs moves

## Verification

Focused tests pin down the new message shape for:

- direct `help docs ...` success
- docs-fallback `help ...` success
- `helppick` / `docpick` submission
- internal `helpfollow`
- `helpback`

See:

- `tests/test_editor_help_docs_buffers.py`
- `tests/test_editor_help_docs_navigation.py`


## Rev389 follow-up

Rev382 already taught direct `help docs TOPIC` misses to say `help docs: no such doc: TOPIC`, but two navigation-side misses still lagged behind that more explicit dialect:

- `helpfollow` on an internal docs link whose target page does not exist
- `helpback` when the stored docs topic no longer resolves

Those paths still said `help: no doc for ...`, which was understandable but less structured than the direct lookup path and slightly harder to scan in logs or future scripted traces.

Rev389 keeps that follow-up intentionally tiny: docs navigation now reuses the same `help docs: no such doc: TOPIC` wording as direct docs lookup. The goal is consistency, not verbosity.
