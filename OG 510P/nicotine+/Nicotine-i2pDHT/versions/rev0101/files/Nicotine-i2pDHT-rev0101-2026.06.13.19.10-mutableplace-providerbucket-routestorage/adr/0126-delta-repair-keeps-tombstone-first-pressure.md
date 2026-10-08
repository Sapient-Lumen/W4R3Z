# ADR 0126 — delta repair keeps tombstone-first pressure

Status: accepted for rev0030 baby cube.

Range-delta sketches request repair; they do not decide truth. If tombstone material is missing, the repair join keeps the window open until exact tombstone material arrives or the repair path is rejected.

Rationale: deletion, compromise, withdrawal, and revocation evidence must not be buried behind ordinary provider churn.
