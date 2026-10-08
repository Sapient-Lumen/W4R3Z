# ADR 0170: Prune guard before evidence deletion

Status: accepted in rev0058.

Evidence deletion is a protocol decision, not housekeeping.

Decision: terminal soft prune is allowed only after finality acceptance; pending retry/dead-letter state must retain its evidence; hard negatives and accepted finality markers cannot be dropped.
