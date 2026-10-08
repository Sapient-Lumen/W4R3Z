# External source review queue (generated; no URLs)

**Track:** Shared


Generated from `evidence/lock/external-sources.toml`.

Purpose: keep unpinned-source drift risk **visible and bounded** without expanding the archive.

Notes:
- Sorted by `review_by` (earliest first), then by a small heuristic priority score.
- `refs` counts total `source:` + `xref:` occurrences across in-repo markdown.
- `docs` shows up to 6 numbered docs that reference the ID.
- Output is intentionally capped to the first 3 actionable rows to keep the archive size-disciplined; use the lockfile directly for exhaustive triage.

Unpinned entries: 1098

Visible rows: 3 (remaining summarized: 1095; blocked=36; mutable=949; temporary=110)

| review_by | id | exemption | retrieved | refs | tags | docs (top) |
|---|---|---|---|---:|---|---|
| 2026-07-25 | `uscode_52_usc_21081_voting_systems_standards_page` | mutable | 2026-04-26 | 2 | citation_backfill,law,us_code | `DOC:docs/301-accessible-voting-accommodations-curbside-and-change-notices-as-evidence-surfaces.md` |
| 2026-07-25 | `uscode_52_usc_21082_provisional_voting_page` | mutable | 2026-04-26 | 2 | citation_backfill,law,us_code | `DOC:docs/296-provisional-ballot-status-lookups-and-reason-notices-as-evidence-surfaces.md` |
| 2026-07-25 | `asa_post_election_audit_best_practices_2018_pdf` | temporary | 2026-04-26 | 2 | citation_backfill,audit,pdf | `DOC:docs/291-risk-limiting-audit-evidence-surface.md` |
