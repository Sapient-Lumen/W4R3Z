# Rev690 - make exact macro count rows validate counts before slot lookup

Micromax's runtime playback path already validates the count token before it decides whether a named macro slot exists. That means `macro play ghost oops` and `macro play last oops` both stop first at `count must be an int`, even if the slot is missing or the default `last` slot is empty.

Rev690 keeps the follow-up deliberately small and trust-first. Exact `macro play|run NAME COUNT` prompt rows now mirror that same validation order: after blocker checks, count parsing happens before missing-slot or empty-default-slot fallback. The goal is simple: the exact count row should preview the first real reason Enter would stop, not a later slot-state error that runtime never reaches.
