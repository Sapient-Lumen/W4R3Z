# External source review queue (generated; no URLs)

**Track:** Shared


Generated from `evidence/lock/external-sources.toml`.

Purpose: keep unpinned-source drift risk **visible and bounded** without expanding the archive.

Notes:
- Sorted by `review_by` (earliest first), then by a small heuristic priority score.
- `refs` counts total `source:` + `xref:` occurrences across in-repo markdown.
- `docs` shows up to 6 numbered docs that reference the ID.
- Output is intentionally capped to the first 3 actionable rows to keep the archive size-disciplined; use the lockfile directly for exhaustive triage.

Unpinned entries: 1138

Visible rows: 3 (remaining summarized: 1135; blocked=35; mutable=939; temporary=161)

| review_by | id | exemption | retrieved | refs | tags | docs (top) |
|---|---|---|---|---:|---|---|
| 2026-05-15 | `arxiv_more_style_less_work_2012_03371_pdf` | temporary | 2026-02-22 | 1 | audit,rla,card_style_data | `DOC:docs/36-risk-limiting-audits-integration.md` |
| 2026-05-15 | `arxiv_stylish_rla_in_practice_2309_09081_pdf` | temporary | 2026-02-22 | 1 | audit,rla,card_style_data | `DOC:docs/36-risk-limiting-audits-integration.md` |
| 2026-05-15 | `eac_enr_securing_results_checklist_pdf` | temporary | 2026-02-26 | 4 | eac,enr,results_reporting,checklist | `DOC:docs/63-election-night-reporting-and-public-results-security.md`, `DOC:docs/252-election-night-reporting-and-unofficial-results-as-evidence-surfaces.md`, `DOC:docs/261-public-commitments-and-transparency-logs-for-election-evidence.md`; (+1 other) |
