# Macro blocked slot menus

Rev654 closes one small adjacent trust/flow seam in the macro command bar.

Micromax already told the truth for exact blocked slot rows:

- `macro play demo` / `macro run demo` could already show `wait for playback`
- `macro record other` / `macro rec other` / `macro start other` could already show `stop or cancel first` or `wait for playback`

But the empty slot menus one token earlier could still look more runnable than the live state:

- during active playback, empty `macro play ` / `macro run ` still offered saved macro slots
- while recording or playback already blocked recording, empty `macro record ` / `macro rec ` / `macro start ` still offered save targets

That taught the wrong next step. In a small automation loop, a blocked subcommand should not advertise cheerful target choices it cannot run yet.

The rev654 fix stays deliberately small:

- `_prompt_command_token_candidates(...)` now suppresses empty blocked slot menus for `play` / `run` during playback
- the same helper suppresses empty blocked slot menus for `record` / `rec` / `start` during recording or playback
- typed exact slot tokens are still preserved as fallback candidates, so completion can keep showing the exact blocker row instead of going blank

The result is calmer and more truthful:

- no impossible slot menu when the live macro state already blocks the subcommand
- still no loss of inspectability once a user has typed an exact target
