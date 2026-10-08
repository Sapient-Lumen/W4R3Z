# Scenario — interrupted rewrite recovers last known good state

Goal: inject interruption during a file rewrite, remount, and classify whether:

- the last known good state survives,
- the latest write is lost but the filesystem remains consistent,
- or a stronger claim cannot be made.

This scenario is about **power-cut truth**, not marketing language.
