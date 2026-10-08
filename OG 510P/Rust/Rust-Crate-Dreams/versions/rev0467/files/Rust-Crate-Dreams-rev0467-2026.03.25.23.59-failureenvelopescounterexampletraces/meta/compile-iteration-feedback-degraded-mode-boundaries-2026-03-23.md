# Compile Iteration Feedback degraded-mode boundaries (2026-03-23)

When future passes touch **P-0537** again, keep these lanes explicit:

1. **patch eligibility** — whether the edit class is theoretically hotpatch / relink / restart compatible;
2. **live-update outcome** — what actually happened on this attempt;
3. **degraded iteration mode** — what operating posture the process is in now;
4. **restart fallback plan** — what deterministic recovery path exists if the session must be abandoned;
5. **activation / generation / retirement / drain** — what code became reachable, what generation is claimed, and whether old work is gone.

Do not let any of the following stand in for an honest outcome or mode answer by themselves:

- “the edit was patch-eligible”,
- “a reload callback fired”,
- “the build finished”,
- “the logger only printed warnings”,
- “the app is still running”,
- or “we have a restart procedure”.

A pass may truthfully show a patch-eligible edit, a completed build, an activation boundary, and a restart fallback while still lacking an honest answer about whether the attempted live update applied or whether the process is now degraded.
