# rev0310 post-readout dispatch lane-class firebreak refactor

## Problem

A post-readout action dispatch is supposed to be a narrow conversion from a
terminal live-window readout disposition into one bounded next step. The dispatch
lane was already checked against the source readout, and the owner-action class
was checked against that lane. Two sibling classes were looser:

```text
next_evidence_ask_class
public_language_action
```

Both were allow-list checked, but not lane-map checked. That left room for a
record that was syntactically valid yet semantically mismatched, for example a
continue-same-ceiling dispatch that carried a quarantine-resolution ask or a
suppress-public-language action.

## Change

The dispatch lane now controls all three route classes:

```text
owner_action_class == lane_owner_action_map[dispatch_lane]
next_evidence_ask_class == lane_next_ask_map[dispatch_lane]
public_language_action == lane_public_action_map[dispatch_lane]
```

The recorder fails before writing output when an override violates the map. The
shared guard also fails tampered records, so copied JSON cannot bypass the CLI.

## Regression coverage

`tools/check_ft0181_post_readout_action.py` now checks:

- a valid continue-same-ceiling dispatch still records and passes integrity;
- a tampered `next_evidence_ask_class` fails the shared guard;
- a tampered `public_language_action` fails the shared guard;
- the CLI/builder blocks both mismatched override classes before scratch output
  becomes a plausible next step.

## Boundary

This firebreak does not create post-readout action completion, service-record
edits, public-summary support, evidence custody, or closure. It only prevents a
locally valid post-readout dispatch from carrying the wrong bounded next ask or
public-language posture.
