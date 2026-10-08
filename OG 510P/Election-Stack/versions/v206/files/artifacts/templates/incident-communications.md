# Incident communications worksheet (maps to PublicNotice)

Use this as a **drafting worksheet**; the canonical artifact is a **PublicNotice** envelope:
- `DOC:docs/186-incident-communications-as-evidence.md`
- `SCHEMA:schemas/PublicNotice.json`
- Starter payload: `artifacts/templates/public-notice-payload.json`

## Draft (facts only)

### notice_type (pick one)
- `status_update` | `incident_declaration` | `incident_advisory` | `rumor_control` | `correction`

### title (short)

### message (short; what is known vs unknown)

### what voters should do now (clear instructions)

### evidence pointers (digests / packet paths; avoid screenshots)

### next update time (measurable commitment)

### channels
Use canonical `channel_id`s from `artifacts/registries/official-channels.csv`.

## Publish
- Build the `hfv.public.notice` envelope + required attachments.
- Print a digest short form for comms surfaces:
  - `python tools/public_notice_card.py --packet <packet_dir>`
