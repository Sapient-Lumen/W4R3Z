# Rev648: macro playback blockers tell the truth too

## Why

Micromax had already made most macro blockers truthful before Enter and, after rev647, on several blocked runtime paths too. But active playback still had one narrow blind spot: nearby macro commands could look runnable in the command bar or fail too quietly after Enter even though the editor already knew playback was in progress.

## What changed

- exact `macro play` / `run` rows now show `playing · NAME (N step[s]) · wait for playback` while playback is active
- exact `macro stop` / `end` / `cancel` / `abort` rows now use that same playback guard instead of degrading to `not recording`
- blocked `macro play` / `run` now reject after Enter through the same shared runtime witness path used by other blocked macro subcommands
- focused tests pin both command-bar previews and runtime feedback during playback

## Intent

When Micromax is already replaying tiny automation, adjacent macro commands should be boringly explicit about that fact. `wait for playback` is a better answer than silence and a better answer than pretending the state is merely idle.
