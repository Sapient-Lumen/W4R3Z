# ADR 0088 — Parseguard before network bytes

Status: accepted in rev0022.

Future live transport must not be the first time arbitrary peer bytes meet a parser.  The cube now has a strict bounded bdecode surface for canonical fixture parsing.

Decision: reject ambiguous/non-canonical forms and expose structured rejection kinds.
