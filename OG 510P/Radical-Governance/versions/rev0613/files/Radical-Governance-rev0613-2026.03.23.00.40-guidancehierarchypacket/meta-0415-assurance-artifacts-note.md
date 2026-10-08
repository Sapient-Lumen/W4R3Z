# 0415 — Assurance-artifacts note

This revision adds `ASSURANCE_ARTIFACTS.json`, a generated crosswalk that groups notes by the concrete governance artifact they expect to exist: registers, assessments, notices, logs, runbooks, schedules, waivers, and similar objects.

Why this helps:

- the archive increasingly specifies not just principles but documentary obligations;
- merge work gets easier when reviewers can ask which notes require a public register, which require a schedule, and which require an evidence packet or waiver record;
- the new administrative-law layer in rev0415 benefits from a machine-readable view of which artifacts must exist for a system to be challenge-ready.

This crosswalk is heuristic rather than canonical. It is meant to make the continuation snapshot easier to audit and merge, not to freeze one final ontology for the full archive.
