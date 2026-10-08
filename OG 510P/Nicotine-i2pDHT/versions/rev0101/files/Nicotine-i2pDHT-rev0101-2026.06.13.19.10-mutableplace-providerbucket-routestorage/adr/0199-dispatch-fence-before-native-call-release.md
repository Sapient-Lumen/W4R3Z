# ADR 0199 — Dispatch fence before native call release

Accepted: rev0093.

Dispatch remains fenced after load loopback and call canary evidence. A later revision may model release pressure, but rev0093 accepts only a fenced state.

Rationale: native call release is a separate safety boundary, not the automatic consequence of good canary evidence.
