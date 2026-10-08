# Scenario — X11 Fcitx5 key-release leaks need normalization and an explicit transaction receipt

This scenario exists to keep **native IME normalization truth** reviewable.

The backend claims to suppress ordinary keyboard events during composition, but leaked `KeyboardInput` release events are still observed under X11 with Fcitx5.
The engine therefore owes a visible explanation of whether it:

1. ignores those releases,
2. normalizes them away from the transaction log,
3. or still leaves a manual-review hole in the replay.

The point is not to pretend native IME is broken everywhere.
The point is to stop one backend-specific leak from inheriting the trust surface of a clean transaction model.
