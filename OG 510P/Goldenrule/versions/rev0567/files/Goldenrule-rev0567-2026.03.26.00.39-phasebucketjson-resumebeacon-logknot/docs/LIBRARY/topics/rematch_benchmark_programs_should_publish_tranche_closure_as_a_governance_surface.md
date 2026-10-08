# Rematch benchmark programs should publish tranche closure as a governance surface

A benchmark tranche is not just "done" or "not done" in an operator's head.
If closure state is hidden in workflow residue, later inheritors cannot tell whether a benchmark was intentionally frozen, provisionally staged, or merely abandoned mid-pass.

The compact rule is simple: publish the tranche-closure state as governance metadata.
That closure field is part of the benchmark's institution because it determines whether downstream users should treat the current artifact as provisional, rehearseable, or publication-ready.
