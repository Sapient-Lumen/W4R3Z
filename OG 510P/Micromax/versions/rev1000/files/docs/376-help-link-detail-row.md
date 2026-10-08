# Rev434: current docs-link detail row

Micromax already had a small honest docs-link loop:

- `helplinkpick` exposed searchable link rows for the current docs page
- `helpfollow` followed the link under the current cursor
- `helplinkcopy` copied that same target without inventing extra UI state

But one tiny seam still lingered underneath those surfaces: the exact current
link target only existed implicitly inside per-command markdown rescans. Humans
could act on the link, and scripts could enumerate *all* visible links through
`ed.help-link-rows`, but there was no named machine-facing sibling for the one
link the cursor was currently on.

Rev434 keeps the fix deliberately small:

- `help_link_detail_row()` / `ed.help-link-detail-row` now expose one resolved
  `[topic label target kind line col section]` row for the current docs-link
  target
- `showhelplink` gives humans the same exact inspection path directly
- `helpfollow` / `helplinkcopy` now reuse that shared row instead of reparsing
  the cursor target independently

That keeps the docs browser tiny and inspectable. If one current docs-link
already matters enough to follow or copy directly, it should also have one tiny
stable row that future UIs, scripts, and LLMs can inspect without rescanning
an entire page of links.
