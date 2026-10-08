# Rev686 - centralize the empty-default-slot runtime witness

Micromax now has one clear runtime message for trying to play the empty default `last` slot: `default slot is empty`. That message can come from bare `macro play`, `macro run`, or the direct `play_macro(...)` path.

Rev686 keeps the follow-up deliberately tiny and structural. New `_macro_default_slot_empty_runtime_message(...)` now owns that runtime witness once, and the command-dispatcher plus direct playback path both reuse it. Visible behavior stays the same; the goal is simply to make the empty-default-slot runtime dialect as easy to keep coherent as the prompt/action dialect around it.
