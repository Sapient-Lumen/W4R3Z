# Cube deep audit rev0270

## Audit focus

Rev0270 audits the `FT-0181` field lane for a specific operational failure: local
contact-clock state can become persuasive even when it is only scratch metadata.
Rev0269 required a confirmation token and source-artifact path; rev0270 checks the
path so the local router cannot advance from a phantom or wrong-class artifact.

## What was still wasteful or fragile

The cube already has enough doctrine saying that prepared packets, smoke outputs,
local receipts, status notes, and workbench seeds are not evidence. The next risk
was not conceptual. It was tooling fragility:

| Fragility | Why it matters | Rev0270 correction |
|---|---|---|
| Phantom source path | A command could record a status while citing a nonexistent source artifact. | Contact-status source artifacts must exist and be readable JSON. |
| Wrong source type | A sent clock could cite a status note, or a no-owner clock could cite a packet manifest. | Each status has an allowed source class. |
| Release-file source leakage | A shipped example or release-control file could become a pseudo-source for scratch progress. | Source artifacts must be local `scratch/` artifacts. |
| Premature re-ask/no-owner | The bounded clock could be compressed without the proper prior due clock. | Re-ask and no-owner sources now check prior due dates. |
| Locally edited packet manifest | A packet manifest could be altered to claim evidence or closure before routing. | Sent clocks reuse packet integrity checks from the field router. |

## Refactor performed

The refactor is intentionally small:

1. `tools/record_ft0181_owner_contact_status.py` gained source-artifact
   verification.
2. `tools/check_ft0181_owner_contact_status.py` now builds real scratch source
   fixtures and tests missing, controlled, and premature sources.
3. `tools/check_ft0181_field_next_action.py` now exercises the router with real
   source artifacts, so routed commands remain compatible with the stricter
   recorder.
4. Root navigation and release-control surfaces now describe the verified-source
   boundary instead of treating `SOURCE_ARTIFACT` as a simple string.

## What should not change next

Do not add another contact-attempt registry. Do not request raw exports,
screenshots, protected facts, small cells, vendor dashboards, credentials, or
security payloads. Do not turn field-texture notes into evidence. Do not close
`FT-0181` because a source-artifact check passed.

## Next substantive move

The actual unblocker remains outside the archive: send or adapt the bounded owner
packet, then record the local sent clock through the router. If a real owner CSV
returns, route it through `make owner-field-next CSV=...` before intake. If the
bounded clock and one clarification fail, record no-owner-packet without widening
the ask.
