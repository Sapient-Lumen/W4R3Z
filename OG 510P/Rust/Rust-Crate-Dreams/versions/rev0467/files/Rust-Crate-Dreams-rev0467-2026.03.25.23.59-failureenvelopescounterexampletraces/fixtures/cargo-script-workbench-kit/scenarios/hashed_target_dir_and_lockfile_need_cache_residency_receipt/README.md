# Hashed target-dir and lockfile need cache residency receipt

Single-file packages default to a hashed target-dir under Cargo home and place the lockfile there.
The receipt should preserve that residency explicitly.
