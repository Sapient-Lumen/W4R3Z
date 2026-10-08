# 0416 — Lifecycle-gates note

This revision adds `LIFECYCLE_GATES.json`, a generated crosswalk that groups notes by the stage-gates where they most strongly bite: scoping and authority, prelaunch approval, live operation, change and release, redress and review, and retirement and continuity.

Why this helps:

- the archive increasingly specifies controls that matter at different moments in a system’s life rather than only as general principles;
- merge work gets easier when reviewers can ask which notes matter before launch, which matter during live operations, and which only become critical during change, challenge, or shutdown;
- the new internal-controls layer in rev0416 benefits from a machine-readable view of where maker-checker rules, approved baselines, and privileged-access review should attach in the operating lifecycle.

This crosswalk is heuristic rather than canonical. It is meant to make the continuation snapshot easier to audit and merge, not to claim that every note belongs to only one stage forever.
