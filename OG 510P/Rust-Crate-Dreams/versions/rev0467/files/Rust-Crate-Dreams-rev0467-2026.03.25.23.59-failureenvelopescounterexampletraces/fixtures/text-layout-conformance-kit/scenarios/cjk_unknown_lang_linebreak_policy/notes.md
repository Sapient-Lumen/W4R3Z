# cjk_unknown_lang_linebreak_policy

This scenario exists to make **policy-profile drift** reviewable.

It models a case imported from WPT-style CSS Text material where the same CJK string is run twice:

- once under a raw `unicode_default` profile,
- once under a `css_text_like` strict line-break profile.

The point is not to claim that one result is universally correct.
The point is to make the interpretation lane explicit and diffable.

Why this matters:

- Unicode default break opportunities are not the whole browser/toolkit story.
- WPT imports often encode CSS policy expectations rather than pure Unicode-default behavior.
- Future readers need to know whether a changed wrap came from Unicode data, the chosen profile, backend discretion, or the runtime font universe.
