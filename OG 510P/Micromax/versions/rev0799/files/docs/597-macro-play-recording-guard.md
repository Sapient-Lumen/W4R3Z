# Rev656: block macro playback while recording

## What changed

Micromax no longer starts macro playback while a recording session is already open.

The guard now applies consistently across:

- `macro play NAME [COUNT]`
- `macro run NAME [COUNT]`
- direct `Editor.play_macro(...)`
- portable `ed.macro-play`
- command-bar preview rows for `macro play` / `run`, exact play slots, and exact play counts
- empty play slot/count suggestion menus while recording

The shared blocker witness is:

- `recording · NAME (N step[s]) · stop or cancel first`

## Why this matters

Before this rev, Micromax already blocked playback while playback was active, and the prompt surface already spent several revs getting more truthful about blocked macro states. But one stronger semantic mismatch remained: playback was still allowed during recording.

That was confusing because macro capture intentionally suppresses steps while `_macro_playing` is true. So if a user started recording, then replayed a saved macro, they could watch visible edits happen in the editor without those replayed actions becoming part of the recording buffer. The final saved macro could therefore diverge from the visible editing session that just happened.

That is a trust problem, not just a wording problem.

## Shape of the fix

Keep the fix tiny and coherent:

- reject command-path `macro play` / `run` during recording through the existing shared runtime-summary helper
- reject direct `play_macro(...)` during recording with the same canonical `macro play: ... stop or cancel first` message
- make exact play subcommand/slot/count preview rows reuse that same recording blocker
- hide empty play slot/count menus during recording, but still preserve typed exact slot/count fallbacks so the blocked path stays inspectable before Enter

## Result

Micromax now has one simpler rule:

- recording blocks recording-start and playback-start
- playback blocks playback-start, record-start, save/discard, and related picker/count menus

That keeps tiny automation calmer and makes the saved macro match what the user could reasonably expect from the visible session.
