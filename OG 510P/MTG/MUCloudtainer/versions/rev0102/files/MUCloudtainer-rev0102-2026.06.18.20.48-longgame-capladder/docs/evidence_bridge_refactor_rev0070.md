# Evidence bridge refactor — rev0070

rev0069's evidence index was too conservative: it counted generated files under `data/` as live blockers when those files merely quoted historical raw filenames. That made stale audit-summary references look equivalent to source, script, test, or documentation dependencies.

rev0070 changes `src/muc5/evidence_index.py` so each reference is split into:

```text
active references:     src/, scripts/, tests/, docs/, README.md, manifest.json
historical references: generated data/ mentions
```

The index still records all references, but retention classification now blocks migration on active references only. Historical data mentions remain provenance, not a reason to keep bulky raw tables in every linked working cube.

## Measured change

```text
bulk records scanned:           78
bulk bytes scanned:             844.324 MiB
rev0069 blocked live records:   75
rev0070 blocked live records:   73
new missing-derivative blockers: 2
archive candidates:             3
active reference edges:         115
historical reference edges:      47
```

This does not delete evidence yet. It makes the next deletion/migration pass safer by separating real executable/doc dependencies from generated historical echoes. The immediate migration blockers are now clearer: active references must be redirected, and two bulky files need compact derivatives before they can leave the linked core.
