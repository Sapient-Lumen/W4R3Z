# Incident communications worksheet (maps to PublicNotice)

**Track:** Shared (cross-cutting)


Use this as a **drafting worksheet**; the canonical artifact is a **PublicNotice** envelope:
- `DOC:docs/186-incident-communications-as-evidence.md`
- `SCHEMA:schemas/PublicNotice.json`
- Starter payload: `artifacts/templates/public-notice-payload.json`

Drafting discipline (Claude coherence):
- For any load-bearing statement, **do not hedge** (“likely / appears / seems / probably”). Use explicit epistemic tags (`DOC:docs/218-epistemic-status-tags-and-confidence-rubric.md`) and make missingness visible (`DOC:docs/219-uncertainty-safe-public-updates.md`).
- Treat every public status/rumor surface as a **digest-first view** over notices (MAPT; `DOC:docs/187-publication-compliance-and-coverage.md`).

## Draft (facts only)

### notice_type (pick one)
- `status_update` | `incident_declaration` | `incident_advisory` | `rumor_control` | `correction` | `audit_result` | `election_milestone`

Tip: for canvass/certification/recount milestones, use `election_milestone` and set `milestone_id` (see `DOC:docs/237-canvass-certification-and-recount-as-evidence-surfaces.md`).

### title (short)

### message (short; what is known vs unknown)

Prefer tagged bullets (copy/pasteable):
- `[OBSERVED|HIGH] ...`
- `[UNKNOWN|HIGH] ...`

### what voters should do now (clear instructions)

### evidence pointers (digests / packet paths; avoid screenshots)

### next update time (measurable commitment)

### channels
Use canonical `channel_id`s from `artifacts/registries/official-channels.csv`.

## Publish
- Build the `hfv.public.notice` envelope + required attachments.
- Print a digest short form for comms surfaces:
  - `python tools/public_notice_card.py --packet <packet_dir>`
