# rev0014 source-page anchor and diff sentinel report

Governing rule: **a source-page delta sentinel is not a public delta claim.**

Rev0014 adds a live-observation control layer over the DOJ SLS law-enforcement source page. The page exposes the law-enforcement-agencies section and the 27 pilot matter rows, and the page footer carries `Updated May 1, 2026`. This revision records where each row was observed, maps the document-link anchor state for every document-label census row, assigns recheck cadence tiers, and creates gates for future public change notes.

Rev0014 records:

- 27 source-page anchor observations;
- 27 baseline-vs-observation diff sentinels;
- 148 document link-anchor rows;
- 27 status-label freshness tiers;
- 8 section/source capture-readiness rows;
- 10 public change-note candidates;
- 12 source-page delta assertion gates;
- 6 source-observation events;
- 9 provenance activity templates;
- 7 volatile source-family watch rows.

No source-page structural delta is admitted in rev0014. The observation only says that the carried baseline and the rev0014 web observation were mapped into a diff-control surface. It does not say that the page is preserved, that linked documents are preserved, that current legal status is known, or that any department/officer/person did anything.

## Why this matters

The DOJ page is authoritative but mutable. If an official page changes, the cube must not quietly overwrite history. It needs a source-memory layer that can distinguish:

1. row observed;
2. row changed;
3. document label added/removed;
4. linked payload captured;
5. linked payload hash changed;
6. legal effect reviewed;
7. public change note allowed.

Rev0014 opens only the first comparison/control layer.
