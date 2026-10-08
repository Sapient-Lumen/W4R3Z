# ADR 0102 — partition merge waits for route and witness pressure

Decision: split-merge should run against scratch memory until route/witness pressure passes.

Reason: a signed linked mutable head can still arrive through captured routes or weak witness evidence. Committing too early makes later local checks advisory instead of gating.

Consequence: `partitionwitness.py` commits only after split-merge, route, and witness checks agree locally.
