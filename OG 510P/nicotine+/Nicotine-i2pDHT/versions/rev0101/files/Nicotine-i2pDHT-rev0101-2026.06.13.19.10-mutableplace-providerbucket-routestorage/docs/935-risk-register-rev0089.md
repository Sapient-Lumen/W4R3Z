# Risk register rev0089

Known risks:

- cold-start code may accidentally load or dlopen while trying to inspect artifacts
- old probe corpus may mask a crash-fixed-but-not-retested artifact
- loader cleanup may erase tombstone/fallback/quarantine memory
- native profile toggles may be mistaken for production sandbox proof

Mitigation in this cube: no-network/no-load markers, Python oracle corpus, loader tombstones, fold/audit visibility.
