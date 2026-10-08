# Cube deep audit rev0273

## Deep read

The archive is now strong at preventing prepared packets, send logs, contact
statuses, and bounded clocks from becoming evidence. The next weak point was not
another claim surface; it was the first inbound file after the external send. A
returned owner CSV is psychologically powerful because it looks like the missing
thing. If the path accepts any plausible local CSV, the cube can drift from
"owner replied" into "someone produced a file."

Rev0273 treats provenance as an execution issue. A returned CSV must be routed
through the field-next utility from the same scratch session that contains an
active contact clock. The emitted intake command includes the contact-status
source. Intake then verifies that source before it receipts, triages, or stages
anything.

## Audit judgment

This is a high-value change because it closes a practical bypass without adding
a new doctrine family. The change is narrow and testable:

- the router refuses returned CSV routing when there is no active contact clock;
- direct intake refuses missing `SOURCE_CONTACT_STATUS`;
- terminal `NO_OWNER_PACKET` statuses cannot source intake;
- bundle manifests preserve the clock trace as non-evidence metadata;
- owner-reply and field-next tests now exercise the source-clock gate.

## Waste corrected

The waste corrected is contextless local staging. Before this pass, a maintainer
could spend time triaging, staging, and seeding workbench state from a plausible
CSV that was not linked to a bounded send/reask attempt. That work might still
be labelled non-evidence, but it would consume the same attention the field lane
needs for the real owner path.

## Remaining concern

There is still a large archive tail and many historical surfaces that contain
older direct commands. Current first-read surfaces now point to router-first
intake with a source-contact-status gate, but future cleanup should continue to
compress old instructions that encourage direct tool invocation without the
router.

## Next audit target

After one complete local dry run with a real or locally simulated send clock,
inspect the generated `FIELD-NEXT-ACTION.md`, `send-log.json`,
`contact-status.json`, and intake bundle. Keep only fields that changed routing,
blocked false progress, or preserved minimization; remove anything that merely
makes the trail feel official.
