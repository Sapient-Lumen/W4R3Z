# ADR 0100 — Lineage windows before latest-head acceptance

Status: accepted for rev0026 prototype.

A signed higher-sequence mutable head is not automatically safe. rev0026 requires local lineage pressure: previous digest linkage, direct-gap limits, fork quarantine, scope checks, and source/path-family diversity before local commit.

This is not consensus. It is local acceptance hygiene.
