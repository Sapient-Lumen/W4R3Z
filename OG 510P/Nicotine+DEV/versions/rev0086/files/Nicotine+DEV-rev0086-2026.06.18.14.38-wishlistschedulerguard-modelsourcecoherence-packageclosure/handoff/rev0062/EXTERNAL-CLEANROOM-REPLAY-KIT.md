# rev0062 external clean-room replay kit

rev0062 adds a reviewer-facing clean-room kit under `handoff/rev0062/cleanroom-kit/`. The kit copies the exported rev0059 split bundle patches and the seven fixed-behavior regression tests into a minimal folder with a standalone runner.

Purpose: verify that the strict/front patch and regression chain can be replayed outside the cube against the uploaded archived source bundle, without relying on hidden cube-relative paths.

Boundary: this is still archived-source proof against the supplied `Nicotine-source(1).zip`, not live-current upstream filing proof.
