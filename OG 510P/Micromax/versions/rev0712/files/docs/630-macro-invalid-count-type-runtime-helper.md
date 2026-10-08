# Rev689 - keep direct playback honest about non-integer counts

Micromax's prompt rows and command surface already distinguish two different playback-count failures: `count must be an int` versus `count must be > 0`. But the direct `play_macro(...)` path still collapsed a non-integer count into the less truthful non-positive-count message.

Rev689 keeps the fix deliberately small and headless-first. New `_macro_invalid_count_type_runtime_message(...)` now owns the non-integer runtime witness, the command-dispatch path reuses it too, and direct `play_macro(...)` now returns `count must be an int` when callers pass a bad count type. The goal is simple: direct playback should preserve the same validation truth the prompt and command surfaces already teach.
