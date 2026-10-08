# ADR 0152 — operator intent is protocol data

Decision: local operator actions are signed, scoped, sequenced capsules before they can affect garden-service state.

Reason: manual pause/demote/freeze/resume can bypass safety gates if treated as UI-only state.

Consequence: operator control remains possible, but it enters the same replay, rollback, fork, and scope-drift pressure lanes as other claims.
