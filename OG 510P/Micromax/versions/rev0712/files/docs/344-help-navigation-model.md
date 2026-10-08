# Rev402: help navigation should stay exact and inspectable

## What changed

- docs-history entries now store the prior docs topic **and** the saved cursor target instead of only a topic string
- `helpback` now consumes a back-stack entry only after the target successfully reopens
- `helpback` now restores the saved cursor target even when the original help buffer had been closed and had to be reopened
- `status_model()` now exposes tiny docs-history fields: `help_topic`, `help_title`, `help_back_available`, `help_back_count`, `help_back_target`, `help_back_title`, `help_back_position`, and `help_navigation_summary`

## Why

Micromax had already made docs navigation speak plainly on the message surface: `helpfollow`, `helpjump`, `help docs`, and `helpback` all named themselves on the paths people actually inspect.

But the underlying docs-history state still lagged behind that same trust-first standard.
The back stack only remembered a topic slug, so two small problems survived:

- stale missing-doc entries were popped *before* Micromax knew they could reopen
- a previously visited docs page lost its exact cursor target once that help buffer was closed

Those are tiny failures, but they matter in exactly the kind of archive/tracing loops Micromax is optimizing for. A future human, script, UI, or LLM should not have to guess whether `helpback` is currently actionable, nor lose the exact return target because one intermediate help buffer was closed.

## Resulting contract

Docs history now behaves more like a small inspectable navigation witness:

- current docs page and next back target are separate truths
- back-stack entries are fail-closed: a missing target reports `help docs: no such doc: TOPIC` **without** silently consuming the entry
- successful `helpback` returns can restore the exact prior docs cursor target instead of only the page identity
- future UIs/scripts/LLMs can inspect docs-history availability through stable `status_model()` fields instead of reconstructing it from transient message text
