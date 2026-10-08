# Field execution risk burndown rev0270

## Purpose

This pass burns down execution risk in the contact-clock lane. The target is not
more doctrine; it is a stricter local tool boundary between a generated packet,
a real human send/adaptation, one bounded clarification, and a no-owner-packet
outcome.

## Risk table

| Risk | Consequence | Rev0270 change | Residual boundary |
|---|---|---|---|
| Phantom source artifact | A status note cites a path that does not exist. | The recorder resolves and reads `SOURCE_ARTIFACT` before writing. | Still not proof of external send or receipt. |
| Release-controlled source | A shipped example, template, or release JSON becomes a pseudo-source for field progress. | Source artifacts must live under archive `scratch/`. | Scratch artifacts remain local non-evidence. |
| Wrong source class | Sent, re-ask, or no-owner status is sourced from the wrong local artifact type. | Each status has a required source class and manifest state. | A valid local class still cannot prove owner action. |
| Premature re-ask | One clarification is recorded before the first response clock passed. | Re-ask from prior sent status requires the source due date to be on or before the new sent date. | Re-ask from a real `RE-ASK-ONCE` intake remains allowed. |
| Premature no-owner-packet | Missing owner packet is recorded before the bounded clarification clock passed. | No-owner-packet source must be a due prior `REASK_AWAITING_REPLY` status. | Keeps `FT-0181` live; does not retire the evidence need. |
| Locally edited packet | Packet manifest is altered to look like evidence or closure and then used for sent status. | Sent source packet must pass packet-manifest integrity checks. | Packet prep is still not evidence. |

## Refactor footprint

Changed high-risk surfaces:

- `tools/record_ft0181_owner_contact_status.py`
- `tools/check_ft0181_owner_contact_status.py`
- `tools/check_ft0181_field_next_action.py`
- `docs/00-meta/source-artifact-integrity-audit-rev0270.md`
- active re-entry, release-control, and metadata surfaces for rev0270

## Operational effect

The operator still uses the router-emitted command, but `SOURCE_ARTIFACT` now has
teeth. For example, the first sent clock must cite the actual generated packet
manifest under `scratch/owner-request-packets/.../packet-manifest.json`; a missing
path, release example, local note, or edited evidence-claiming manifest is blocked.

## Completion risk still open

The live blocker remains unchanged: the cube still needs a real `SRC2+`
owner-reviewed packet or a bounded no-owner-packet outcome. Rev0270 only prevents
local source-trace weakness from pretending that external progress happened.
