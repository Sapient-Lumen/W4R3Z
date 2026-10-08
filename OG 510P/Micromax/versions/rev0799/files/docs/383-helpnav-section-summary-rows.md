# Rev441 — current docs navigation gets one tiny broad summary row

## What changed

Micromax already had strong current-doc navigation surfaces:

- `helpoutlinepick` exposed grouped heading rows for the current docs page
- `helplinkpick` exposed grouped link rows for the same page
- `helpnavpick` merged those same heading/link families into one combined navigator
- recent revs added exact `showhelpheading` / `showhelplink` siblings plus `ed.help-current-heading-detail-row` / `ed.help-link-detail-row` for one resolved cursor target

But one small inspectability seam still remained: current docs navigation was stronger at exact target inspection and full picker browsing than at the simpler first question future humans/LLMs often ask first:

> what heading/link buckets are visible in this docs page right now?

Rev441 keeps the fix deliberately small:

- add `help_nav_section_summary_rows(QUERY)` in the editor core
- expose it as `ed.helpnav-section-summary-rows`
- add plain `showhelpnav [QUERY]` for humans

## Row shape

`help_nav_section_summary_rows(QUERY)` / `ed.helpnav-section-summary-rows` return:

```
[label count sample_name sample_detail]
```

Where:

- `label` is the visible current-doc navigation bucket (`Top`, a heading breadcrumb label, `Docs`, `Files`, `External`, or a heading-grouped link bucket when `help.linksections=heading`)
- `count` is the number of currently visible rows in that bucket
- `sample_name` reuses the first visible heading or link label in that bucket
- `sample_detail` reuses that first row's detail text

Examples:

- `['Top', 1, 'Help browser', '1:3']`
- `['Files', 43, 'Vision', '47:4 — Links']`

The shape intentionally stays tiny. Exact heading/link targets still belong to `showhelpheading` / `showhelplink`, and full grouped browse state still belongs to `helpnavpick` / `ed.helpnav-section-rows`.

## Why this matters

This is a small trust/flow improvement for the docs/help loop.

Current docs navigation already had good exact surfaces and good browse surfaces, but there was still no official first-stop register for the smaller broad question of what navigation families currently exist on the page. The new summary rows and plain `showhelpnav [QUERY]` keep that answer inspectable without opening a picker, scraping grouped prompt headers, or walking every grouped row.

## Focused tests

- `tests/test_editor_helpnavpick.py`
- `tests/test_editor_capabilities_registry.py`

## Next tiny seams

- some other grouped picker families still only expose their full grouped row shapes and not a lighter summary sibling
- current docs navigation is now inspectable at exact, grouped, and broad-summary levels, but future work may still want similarly tiny first-stop summaries for other picker-heavy navigation surfaces
