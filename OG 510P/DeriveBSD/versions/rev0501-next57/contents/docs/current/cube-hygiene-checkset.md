# Current cube hygiene checkset

The live hygiene checkset is `cube.hygiene.checkset.manifest` for 2026-05-30r533. It keeps the full `tools/hygiene.py` inventory visible while allowing focused profiles for release work.

Current shard counts:

```text
top_level_check_scripts: 350
hygiene_referenced_check_scripts: 350
release_critical_count: 25
post_detach_focus_count: 32
generated_surface_count: 2
schema_cube_audit_count: 3
deep_contract_count: 290
missing_from_hygiene_count: 0
```

Use `python3 tools/hygiene.py --profile release-critical` for the bounded front-door slice and `python3 tools/hygiene.py --profile post-detach` for the removable-media lifecycle slice. r533 adds the terminal-closure successor-cutover checker to the post-detach hygiene shard.

Last updated: 2026-05-30r533

Profile tokens: `release-critical`, `post-detach`, `generated-surface`, `schema-cube-audit`, `deep-contract`.
