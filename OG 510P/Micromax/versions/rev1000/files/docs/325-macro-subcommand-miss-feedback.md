# Rev383: macro subcommand misses should stay typed too

Recent trust-first work has been tightening one small rule across Micromax: when an editor command fails, the failure should still name the surface that failed and the thing it could not find. That made buffer, mark, hook, help, keybinding, and command-bar misses much easier to scan.

Macros already had most of that honesty: playback reports what ran, missing named macros fail as `macro play: no macro: NAME`, and `macro list` stays count-aware. But one tiny seam still lingered in the same automation loop: asking for an unknown `macro` subcommand only produced `unknown macro subcommand`, which dropped both the `macro` surface prefix and the actual rejected subcommand.

Rev383 keeps the change deliberately small:

- unknown `macro` subcommands now fail as `macro: no such subcommand: NAME`
- successful `macro record` / `stop` / `cancel` / `play` / `list` behavior stays unchanged
- focused macro tests now pin down the miss shape next to the rest of the named-macro coverage

This is not new macro power. It is a small trust/flow cleanup for one of the editor's earliest automation surfaces. A future human or LLM scanning status output should be able to tell immediately that this was a `macro` command typo, not a generic parser or REPL error.
