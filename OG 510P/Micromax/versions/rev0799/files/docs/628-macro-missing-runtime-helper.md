# Rev687 - centralize the missing-macro runtime witness

Micromax already distinguishes an empty default `last` slot from a genuinely missing named macro slot at runtime. The latter case uses the tiny `no such macro: NAME` witness across playback entry points.

Rev687 keeps the follow-up deliberately small and structural. New `_macro_missing_runtime_message(...)` now owns that missing-slot witness once, and the command-dispatch plus direct playback path both reuse it. Visible behavior stays the same; the goal is simply to keep the missing-slot runtime dialect as coherent as the empty-default-slot runtime dialect nearby.
