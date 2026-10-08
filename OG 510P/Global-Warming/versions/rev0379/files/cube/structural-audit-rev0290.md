# Structural audit rev0290

Revision rev0290 continues the nuclear-positive refactor by turning the preference into deployment sequencing, fuel-cycle assurance, climate/water/site screening, grid-load matching, and a service-floor-wide propagation audit.

## Counts

- numbered_markdown_files: 439
- index_rows: 439
- sources: 792
- service_floors: 443
- nuclear_service_floors: 25
- nuclear_gates: 20
- nuclear_gap_backlog_rows: 515
- propagation_audit_rows: 443
- exception_ledger_rows: 405
- route_edges: 3769
- sqlite_tables_imported: 151
- cube_csvs: 152

## Audit findings

- The nuclear preference is now represented in canon files 434-438 and machine tables rather than only prose.
- Nuclear gates expanded from project safety/delivery controls to include fuel-cycle, HALEU, climate-water, grid interconnection, offtake, anti-crowding-out, lifecycle/decommissioning and public-benefit gates.
- Every service floor now has a nuclear propagation audit row. Floors that are not directly energy/high-load related receive a recorded exception; energy/high-load floors without route coverage become refactor backlog.
- The service-floor scorecard remains conservative: global template rows do not certify any real reactor, site, fuel contract, interconnection, host-community benefit covenant, or local emergency plan.

## Remaining caveat

The new local evidence requirements are control-plane templates. They must not be interpreted as project certification. Real promotion requires dated local evidence, regulatory dockets, source provenance, owner attestations, independent challenge records, open-contracting traces, and retests.
