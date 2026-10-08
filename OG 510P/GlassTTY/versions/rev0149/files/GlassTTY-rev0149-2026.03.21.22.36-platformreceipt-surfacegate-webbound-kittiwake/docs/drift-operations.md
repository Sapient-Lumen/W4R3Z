# Drift operations

This file describes how the drift program should run in practice.

## Trigger types

### Scheduled sweep
Purpose:
- proactively detect surface changes before they become user-visible failures

Expected outputs:
- fresh baseline comparison
- drift severity
- support-record update if relevant

### Operator-triggered sweep
Purpose:
- investigate suspected breakage after a real failed run

Expected outputs:
- before/after comparison bundle
- likely affected workflows
- recommended next action

### Release-blocking sweep
Purpose:
- verify that a stronger support claim is still justified

Expected outputs:
- current comparison bundle
- release-gate artifact
- explicit support-tier recommendation

### User-reported sweep
Purpose:
- convert anecdotal “it changed” reports into inspectable artifacts

Expected outputs:
- reproduction notes
- captured evidence
- drift classification or evidence-insufficient result

## Minimum useful drift artifact

A drift artifact should include:
- surface key
- browser lane
- compared artifact refs
- affected workflows
- drift severity
- summary of changed cues
- next recommended action

## Update responsibilities

When drift is detected:
1. update or annotate the relevant support record
2. update the support matrix summary if a tier changes
3. preserve a comparison artifact ref
4. record whether the issue is route drift, receiver drift, composer drift, generation drift, or turn-parsing drift

## Important truth

A failed comparison is still useful if it narrows which workflows remain healthy and which look suspect.
