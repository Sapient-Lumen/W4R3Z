# Macro-play feedback (rev338)

This is a tiny **trust-first** follow-up.

Micromax already had working macro recording and playback: `ToggleMacro`, `PlayMacro`, `macro record`, `macro stop`, `macro cancel`, `macro play`, and the portable macro hostcalls all existed. But one ordinary success path still felt too vague: **playback itself**.

Before rev338, the editor would happily replay a macro, mutate the buffer, and leave the user to infer whether anything actually happened. Failure was also too quiet when a named macro did not exist.

Rev338 keeps the change deliberately small:

- successful playback now says exactly what ran, for example `macro: played a x2 (1 step)`
- missing named macros now fail explicitly as `macro play: no macro: NAME`
- non-positive counts now fail explicitly as `macro play: count must be > 0`

Why this matters:

- macros are one of the editor's first real automation loops
- automation should feel **reliable**, not uncanny
- the record/stop/play loop should speak one honest dialect instead of going silent at the moment something consequential happens

This is not flashy polish. It is the kind of tiny reliability improvement that helps the editor feel more like a tool you can trust with repeated work.
