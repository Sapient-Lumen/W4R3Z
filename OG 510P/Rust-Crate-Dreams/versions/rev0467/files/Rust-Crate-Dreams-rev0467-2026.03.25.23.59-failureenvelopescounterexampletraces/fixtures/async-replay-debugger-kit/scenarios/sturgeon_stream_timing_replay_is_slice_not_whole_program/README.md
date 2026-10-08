# sturgeon stream timing replay is a slice, not the whole program

This scenario captures an async stream recorded and replayed with timing information.
The important truth is that a narrow effect cassette can be highly useful without covering the rest of the application's tasks and dependencies.

What the receipts should prove:

- that the effect class is `streams`,
- that the capture posture is a real cassette,
- and that the overall fidelity stays at slice-level replay rather than whole-program replay.
