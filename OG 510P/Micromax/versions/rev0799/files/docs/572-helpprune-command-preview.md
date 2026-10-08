# Rev631: `helpprune` command preview tells the truth before Enter

## Why

Micromax already kept stale docs-history cleanup honest after Enter: `helpprune` pruned only missing session, back, and forward targets and failed explicitly as `helpprune: nothing to prune` when the local trail was already clean. But the command-bar row still flattened that same cleanup state back to generic command metadata right before execution. That made the last step in the docs recovery loop less trustworthy than neighboring `helpback` / `helpforward` / `helpresume` previews even though the editor already knew the exact answer.

## What changed

- added `_helpprune_preview_summary()` as one tiny shared witness for plain `helpprune`
- exact command-bar completion for `helpprune` now previews one of:
  - `prune N missing help target(s) (session S; back B; forward F)`
  - `nothing to prune`
- added focused prompt tests for pending-cleanup and empty-state previews

## Why it matters

This keeps explicit stale-history cleanup in the same trust-first dialect as the other help-browser previews: Micromax should say whether anything needs pruning, and where, before the user presses Enter. That makes the archive easier for future humans and LLMs to inspect because the exact local cleanup state is visible through one tiny deterministic row instead of hidden behind static prose.
