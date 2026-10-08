# Rev688 - centralize the invalid-play-count runtime witness

Micromax already has one small runtime sentence for playback counts that are zero or negative: `count must be > 0`. That message can come from bare `macro play`, `macro run`, or the direct `play_macro(...)` path.

Rev688 keeps the follow-up deliberately tiny and structural. New `_macro_invalid_count_runtime_message(...)` now owns that witness once, and both command-dispatch plus direct playback reuse it. Visible behavior stays the same; the goal is simply to keep the invalid-count runtime dialect as coherent as the nearby empty-slot and missing-slot playback witnesses.
