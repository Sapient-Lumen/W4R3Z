# RP-0062 — false presence and release-scaffold pruning

The new wager moves away from deletion. P0005-D001 commits a four-byte Bloom filter whose absent query receives `POSSIBLY PRESENT` because its three probe bits were set independently by three other records. The exact ledger remains available, so the artifact proves both the probabilistic answer and the exact absence without assigning the event to a real person or system.

The audit also found release waste and drift risk: 22 parent-dependent `do_rev*.py` constructors occupied about 1.4 MB and were shipped even though the pruning policy says the working cube is not the preservation archive. Release-tree path rules were duplicated between manifesting and packaging. Rev0070 removes the constructors, excludes future root revision scaffolds, and centralizes member collection and zip verification in one module.

No candidate was promoted and no reader response was created. See `docs/40-audits/P0005_D001_BLOOM_FALSE_PRESENCE_RELEASE_SCAFFOLD_AUDIT_rev0070.md`.
