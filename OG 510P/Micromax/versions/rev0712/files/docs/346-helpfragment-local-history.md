# Rev404: docs history should remember landed destinations inside one page too

## What changed

- same-page `helpjump` now pushes the prior docs cursor target onto local help history before it lands
- same-page fragment / footnote `helpfollow` now does the same
- heading picks from `helpoutlinepick` and `helpnavpick` now reuse that same tiny same-page history rule
- `status_model()` / `help_navigation_model()` now expose `help_position` for the current docs target
- same-topic `help_navigation_summary` strings now include the current `help_position` when needed so `help-browser <- help-browser` no longer collapses distinct landed destinations into one blurry topic label

## Why this matters

Rev402 and rev403 made Micromax's docs history exact, inspectable, and session-honest at the page level.

But one destination seam still lingered inside that same tiny loop: a help page can contain multiple meaningful places — sections, outline targets, footnotes, explicit fragment ids — and explicit docs-navigation actions could move among them without becoming part of local help history at all. That meant the retrace surface still flattened a multi-stop docs journey back into one topic slug unless the user had crossed into a different page.

The right import from the other datacubes was not "capture every cursor wiggle".
It was the smaller rule: **when the product offers an explicit navigation action, history should remember the landed destination that action changed, not just the larger container around it.**

## New contract

- same-page help navigation is now retraceable through `helpback` / `helpforward`
- arbitrary cursor movement is still **not** promoted into docs history
- the history remains local to the docs/help lane and still stays session-only
- status/model consumers can inspect the current docs target through `help_position` instead of inferring it from the last transient message

## Intended effect

Micromax should feel browser-like enough that a section jump is a real place you can retrace, while still staying small enough that only explicit docs-navigation actions become history.
