# Example County public verifier quickstart

**Synthetic example only. This is not live election evidence.**

Scenario: `EXAMPLE-COUNTY-2026-MUNI-v900`  
Archive version: `v900`  
Packets listed: `20`

## One-command rehearsal

```bash
python3 tools/example_county_pilot_smoke.py --json
```

Expected synthetic result: `PASS` for every listed packet.

## Output pack files

- `artifacts/examples/example_county_2026_municipal_pilot/evidence-map.json` maps phases to packet kinds, paths, manifest digests, and verifier commands.
- `artifacts/examples/example_county_2026_municipal_pilot/smoke-report.json` records the synthetic verifier run for every listed packet.
- `artifacts/examples/example_county_2026_municipal_pilot/court-packet-index.csv` gives a preservation-oriented index with non-claims.
- `artifacts/examples/example_county_2026_municipal_pilot/mission-kernel-closeout-index.json` maps the seven mission-kernel elements to actual packets, owner roles, and live blockers.
- `artifacts/examples/example_county_2026_municipal_pilot/public-summary.md` gives safe public-language phrases.

## Boundary

This rehearsal checks packet integrity, digest linkage, manifest closure, and bounded publication-state evidence. It does not prove that an election outcome is correct, does not replace canvass, audit, certification, recount, or court procedure, and does not turn missingness, parity divergence, or incident evidence into proof of intent or fraud.
