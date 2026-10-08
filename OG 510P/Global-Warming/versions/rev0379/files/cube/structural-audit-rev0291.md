# Structural audit rev0291

Rev0291 hardens the nuclear-positive orientation by adding a regulatory legitimacy, security, waste-consent, emergency-preparedness and traceability/red-team control plane.

## Counts

- numbered_markdown_files: 444
- index_rows: 444
- registered_sources: 800
- service_floors: 460
- nuclear_service_floors: 42
- nuclear_assurance_gates: 28
- nuclear_assurance_gap_rows: 1176
- traceability_rows: 1176
- route_edges: 3940
- cube_csvs: 163
- sqlite_imported_tables: 163

## Audit findings

- The pro-nuclear policy is now more explicit but also more bounded: licensing, public participation, security/material-accountability, waste-consent, emergency preparedness, regulator capacity and red-team traceability are hard maturity caps.
- New gates NG_21–NG_28 prevent general nuclear-support sources from being treated as project certification.
- The traceability matrix links nuclear service floors to gates, claims, evidence tables, source IDs, owner roles, public challenge paths and maturity caps.
- Publication controls now distinguish public accountability metadata from security-sensitive or proprietary local/project details.

## Remaining caveat

Rev0291 still does not certify any real project, reactor, site, license application, security plan, emergency plan, waste facility, transport route or host-community agreement. The new rows are control-plane templates until localized evidence exists.
