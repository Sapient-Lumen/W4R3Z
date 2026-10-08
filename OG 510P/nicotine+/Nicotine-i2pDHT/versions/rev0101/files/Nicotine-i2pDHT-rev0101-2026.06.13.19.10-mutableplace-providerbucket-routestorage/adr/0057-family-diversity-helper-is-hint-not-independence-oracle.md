# ADR 0057 — Family diversity helper is a hint, not an independence oracle

Family IDs are local hints. They may represent router family, operator group, invite channel, path class, or test fixture labels. They do not prove independence.

Decision: add `familydiversity.py` to cap same-family evidence and count diversity while preserving the nonclaim that family labels are not Sybil resistance.
