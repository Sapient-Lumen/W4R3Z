# ADR 0127 — live smoke binds SAM script to contact lease

Status: accepted for rev0030 baby cube.

No-router SAM smoke transcripts must be bound to the same Destination advertised by the contact lease. Destination drift is quarantined even if the synthetic SAM script otherwise looks plausible.

Rationale: transport shadows are useful only if they do not launder a different routing identity into the tested entrance.
