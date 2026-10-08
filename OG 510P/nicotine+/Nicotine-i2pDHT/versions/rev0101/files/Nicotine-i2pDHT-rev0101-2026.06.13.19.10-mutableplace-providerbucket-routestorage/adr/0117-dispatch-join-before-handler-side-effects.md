# ADR 0117 — Dispatch join before handler side effects

Accepted for rev0029.

Validator, misbind, capability, and egress reports must be joined at the handler intent boundary.  Valid reports from adjacent surfaces do not authorize side effects unless they bind to the same scope, actor, request, and object.
