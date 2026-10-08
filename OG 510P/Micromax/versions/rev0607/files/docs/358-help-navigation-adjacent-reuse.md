# 358 — adjacent help-topic opens should reuse local history when unambiguous

Hyperepo's local navigation history spec keeps one tiny browser-like rule explicit:
if a newly observed destination already matches the immediate previous or next
history item, treat that observation as a back/forward move instead of pushing a
fresh duplicate branch.

Micromax's docs-navigation lane had almost reached that same place by rev415.
`helpback`, `helpforward`, dormant branching, and same-topic dormant reopen all
preserved exact local history honestly.

But one ordinary-open seam still remained.

If the user opened a docs topic by name (or followed a cross-doc help link) and
that topic already matched the immediate `helpback` or `helpforward` target,
Micromax still treated the event as a brand-new branch:

- opening the immediate back target could duplicate the current page onto back
  history instead of reusing the existing replay edge
- opening the immediate forward target could clear deeper forward history even
  though the user had effectively just moved one step forward

## Rev416 rule

When a docs open matches exactly one adjacent history target, Micromax should
reuse that local history step instead of branching a new one.

Deliberately small scope:

- only the **immediate** back/forward target is considered
- only **unambiguous** matches are reused
- the existing exact cursor target stored on that history entry is restored
- ordinary opens to non-adjacent topics still branch exactly as before

This keeps explicit `help docs TOPIC` / `help TOPIC` opens and cross-doc
`helpfollow` moves aligned with the same tiny replay loop that `helpback` /
`helpforward` already use.
