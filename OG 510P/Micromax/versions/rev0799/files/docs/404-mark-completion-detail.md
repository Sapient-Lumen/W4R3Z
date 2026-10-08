# Rev462: mark and markjump completion now reuse exact mark detail

Micromax already had the right tiny exact mark surface before rev462:

- `showmark NAME` gave humans a side-effect-free first-stop inspector
- `mark_detail_row(NAME)` / `ed.mark-detail-row` exposed the same exact `[name buffer position preview active here]` row to scripts and future UIs
- `markpick [QUERY]` / `ed.mark-section-rows` kept the broader grouped browse state searchable

But one small drift still lingered in the ordinary named-mark loop. Command-bar completion for `mark NAME` and `markjump NAME` still fell back to the older generic mark prompt row, so the user could complete a known mark name without seeing the same active/here/preview metadata that `showmark NAME` already exposed one command later.

Rev462 keeps the follow-up deliberately small:

- add `_prompt_exact_mark_row(...)` as the shared completion formatter for one known mark
- make `showmark NAME` completion reuse that helper instead of keeping an inline formatter copy
- make `mark NAME` and `markjump NAME` completion reuse the same exact mark row too
- keep the broader grouped `markpick` row shape unchanged
- pin the command-bar metadata contract with focused completion tests

That keeps the marks surface more coherent: if one known mark already has a tiny honest exact row, both inspection and ordinary named-mark commands should reuse it instead of degrading back to a thinner prompt row.
