# Simulator note — rev0068

rev0068 changes no simulator or referee semantics.

The only strategic-analysis behavior change is fail-closed handling of incomplete response matrices. Missing policy evidence is now represented as missing, not as a zero target score. The response gate reports `scope = operational_integrity_only` and requires all expected size/life/policy cells.
