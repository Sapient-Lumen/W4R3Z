# Source artifact integrity audit rev0270

## Audit focus

This audit targets the narrowest remaining false-progress seam after rev0269:
`SOURCE_ARTIFACT` was required on contact-status commands, but the recorder did
not inspect whether that path existed, lived under `scratch/`, or matched the
status being recorded.

That meant a well-formed local command could cite a nonexistent packet manifest,
a release-control JSON file, a wrong prior clock, or a premature re-ask source.
The resulting status would still be non-evidence, but it could steer the router
and make the session look further along than it was.

## Findings

| Finding | Risk | Rev0270 correction |
|---|---|---|
| `SOURCE_ARTIFACT` was a trace string, not a checked artifact. | Phantom paths could support a local sent/re-ask/no-owner clock. | `record_ft0181_owner_contact_status.py` now resolves and reads the path. |
| The source path was not limited to scratch. | A shipped example, template, or release-control file could be cited as if it caused field progress. | Source artifacts must resolve to an existing file under archive `scratch/`. |
| Sent clocks did not verify packet-manifest integrity. | A locally edited packet manifest could claim sent/evidence/closure and still drive a status. | Sent clocks require a valid `packet-manifest.json` that passes packet integrity checks. |
| Re-ask clocks did not verify prior route. | A re-ask could be recorded before the first clock passed or without a `RE-ASK-ONCE` intake. | Re-ask source must be either a due prior `SENT_AWAITING_REPLY` contact status or a live `RE-ASK-ONCE` intake bundle. |
| No-owner clocks did not verify the final bounded source. | A no-owner outcome could be recorded from the wrong artifact class. | No-owner source must be a due prior `REASK_AWAITING_REPLY` contact status. |

## Refactor performed

The contact-status recorder now has explicit source-artifact verification. It
adds `source_artifact_verified`, `source_artifact_type`, and
`source_artifact_verification` to `contact-status.json` and writes the verified
type into the markdown status note. The owner-contact and field-next validators
now build real scratch source fixtures and assert that phantom, release-controlled,
wrong-class, and premature source artifacts are blocked.

## Deliberate limit

This is not a mail receipt, delivery receipt, owner attestation, or evidence
upgrade. A human can still lie to a local tool. The point is lower and more useful:
a maintainer can no longer advance the local FT-0181 contact clock using a missing
or wrong-class artifact by accident.

## Correct next move

Run the field router, prepare the packet if needed, complete the external
human send/adaptation outside the archive, and then execute the router-emitted
contact-status command. The command's `SOURCE_ARTIFACT` must point to the actual
scratch artifact selected by the router; do not substitute examples, templates,
release files, or hand-written paths.
