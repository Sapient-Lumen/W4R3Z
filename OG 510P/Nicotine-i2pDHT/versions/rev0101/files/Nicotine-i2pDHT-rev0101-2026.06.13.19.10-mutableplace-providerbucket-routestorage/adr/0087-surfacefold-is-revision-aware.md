# ADR 0087 — surfacefold is revision-aware

Accepted for rev0021.

A current-revision audit must not hard-code the previous revision.  `surfacefold.py` now discovers current docs using the revision parameter and the active public surface.
