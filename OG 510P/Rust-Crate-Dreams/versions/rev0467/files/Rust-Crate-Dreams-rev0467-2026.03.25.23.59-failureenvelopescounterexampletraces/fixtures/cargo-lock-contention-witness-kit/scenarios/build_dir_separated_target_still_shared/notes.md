# build_dir_separated_target_still_shared

This scenario exists to resist a common false simplification:
changing `build.build-dir` or another intermediate-artifact lane does **not** automatically mean the entire contention story is solved.

The support artifact should make it obvious that:

- build-dir lanes were isolated,
- target-dir remained shared,
- and the recommended mitigation still targets the shared target lane.
