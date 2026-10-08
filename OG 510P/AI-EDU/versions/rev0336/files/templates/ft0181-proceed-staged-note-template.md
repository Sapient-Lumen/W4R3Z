# FT-0181 proceed-staged note template

Use this local note only after `tools/triage_owner_reply_csv.py` returns `PROCEED-STAGED` for the
first `AIEDU-SR-003` eight-row owner reply. It is the small landing artifact before the owner packet
workbench. It is not closure evidence, not a public summary, and not proof of learning, safety,
access, workload reduction, compliance, scale, or effectiveness.

## Fill from the staged CSV

| Field | Value |
|---|---|
| Date staged | `[YYYY-MM-DD]` |
| Source CSV or email table | `[local path or local note reference; do not paste raw/protected/security material]` |
| Source truth class at staging | `UNVERIFIED-OWNER-REPLY`; never `SRC0-SMOKE` for archive/workbench use |
| Triage outcome | `PROCEED-STAGED` |
| Selected service | `[from row 1]` |
| Owner path / source / date range | `[from row 1; role/contact path only]` |
| Aggregate workflow counts | `[from row 2; aggregate only and above local privacy threshold]` |
| Action boundary | `[from row 3; draft-only/no-send/no-write/no-penalty/no-protected-inference]` |
| Fallback / rollback / stop condition | `[from row 4]` |
| Workload signal | `[from row 5 or explicit unknown]` |
| Training or use guidance | `[from row 6 or explicit unknown]` |
| Public claim ceiling | `[from row 7; process-only or weaker]` |
| Redaction and owner attestation | `[from row 8]` |
| Next artifact | `docs/30-operations/ft0181-owner-packet-workbench.md` |
| Closure boundary | `Staging note only; FT-0181 remains live pending accepted SRC2+ packet and downstream gates.` |

## Local-only rule

Do not paste learner identifiers, messages, assignment text, gradebook rows, screenshots, protected
support facts, small cells, raw telemetry, credentials, system prompts, exploit strings, or vendor
marketing material into this note. If any of that material arrived, the CSV should not have been
classified as `PROCEED-STAGED`; rerun triage, block, quarantine locally, or use the outcome note.
If the source is under `fixtures/` or carries smoke labels, use only `make owner-reply-smoke`; do not
fill this template as an archive or workbench artifact.

## Use boundary

After the note is filled, copy only the minimized surviving answers into the owner packet workbench.
Do not add fields, new owner roles, a broader source system, public claim language, live-window work,
or closure language while staging.
