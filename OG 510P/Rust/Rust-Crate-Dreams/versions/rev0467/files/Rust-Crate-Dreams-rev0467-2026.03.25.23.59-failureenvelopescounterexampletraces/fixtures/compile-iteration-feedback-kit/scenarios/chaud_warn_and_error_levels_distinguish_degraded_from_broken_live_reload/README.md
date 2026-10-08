# Scenario — Chaud log levels distinguish degraded live update from fully broken live update

This scenario proves why the archive needs a separate **degraded-iteration-mode** artifact.

Chaud documents that many things can go wrong while hot-reloading and recommends enabling logs at least at `warn`.
It also documents a meaningful difference between `error` (“hot-reloading will not work”) and `warn` (“hot-reloading likely won’t work correctly”).
That difference should not be flattened into one generic “reload status unknown” bucket.
