# Structural audit — rev0279

This audit was generated during the rev0279 packaging pass.

## Summary

rev0279 adds the impact-to-intake layer. The audit checks numbering, source resolution, route targets, cube CSV parseability, front matter, H1s, and citation footers.

## Results

- Numbered Markdown files: 389 (`00`–`388`); missing IDs: none.
- Front matter missing: 0; H1 missing: 0; citation-footer missing: 0; post-footer content: 0.
- Sources registered: 697 through S697; unresolved used IDs: none; unused IDs: none.
- cube/index.csv rows: 389; columns: 80; nonexistent numeric routes_to targets: none.
- Cube CSV parse defects: none.
- Schema revision: rev0279; schema fields: 80.
- S687 cited in numbered files: 3.
- S688 cited in numbered files: 4.
- S689 cited in numbered files: 3.
- S690 cited in numbered files: 2.
- S691 cited in numbered files: 3.
- S692 cited in numbered files: 3.
- S693 cited in numbered files: 3.
- S694 cited in numbered files: 2.
- S695 cited in numbered files: 5.
- S696 cited in numbered files: 3.
- S697 cited in numbered files: 4.

## Interpretation

The archive is structurally valid for the rev0279 changes. The new fields make post-impact conversion queryable: `incident_management_state`, `rapid_assessment_state`, `lifeline_stabilization_clock`, `building_safety_placard_state`, `survivor_intake_access`, `commodity_distribution_state`, `volunteer_donations_management`, and `emergency_powers_guardrail`.
