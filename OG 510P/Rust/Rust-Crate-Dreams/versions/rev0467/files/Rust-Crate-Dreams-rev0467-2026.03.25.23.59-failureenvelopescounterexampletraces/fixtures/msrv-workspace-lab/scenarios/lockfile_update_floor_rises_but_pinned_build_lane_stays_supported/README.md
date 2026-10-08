
# Lockfile update floor rises while pinned builds stay supported

This scenario exists to show that building from an existing lockfile and authoring or updating that lockfile are different support promises.

What should happen:
- the build floor stays at the published lower promise,
- lockfile update/generation requires something newer,
- the receipt records the lockfile format and the action,
- and the final bundle keeps authoring support separate from build support.

The point is not to outlaw split floors.
The point is to make them reviewable.
