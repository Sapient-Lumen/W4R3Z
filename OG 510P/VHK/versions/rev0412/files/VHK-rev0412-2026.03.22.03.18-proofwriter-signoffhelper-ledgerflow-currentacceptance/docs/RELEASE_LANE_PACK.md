# Release lane pack

`vhk gen-release-lane-pack` turns hypothetical target-route comparisons into a
ship-facing Linux release matrix.

Outputs:

- `docs/VHK_RELEASE_LANES.md`
- `docs/VHK_RELEASE_SNIPPETS.md`
- `docs/VHK_RELEASE_LANE_PLAN.json`
- `scripts/vhk_refresh_release_lanes.sh`

Use it when the project already understands activation routes and target-desktop
comparisons, but the maintainer still needs to answer release-facing questions:

- which desktop family is the flagship/reference lane?
- which lanes are supportable but not the headline story?
- which lanes still need caveats or experimental language?
- what text should README/release notes/support docs actually use?

The pack intentionally reuses the existing activation/route-selection/target
route language so the release story is derived from the same planner output the
operator and support packs already see.
