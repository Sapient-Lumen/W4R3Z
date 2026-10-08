# Scenario — portable bundle keeps scope, route, and adjacent context separate

The bundle includes imported tool-only context from a compile-time-deps / editor lane, but keeps that import visibly separate from direct rebuild evidence.
The point is to let another reviewer see what was imported without mistaking that adjacent context for direct proof.
