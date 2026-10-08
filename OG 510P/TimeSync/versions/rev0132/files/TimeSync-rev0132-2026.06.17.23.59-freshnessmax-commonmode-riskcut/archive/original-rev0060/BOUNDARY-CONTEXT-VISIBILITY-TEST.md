# BOUNDARY-CONTEXT-VISIBILITY-TEST

This note tests how visible `boundary_context` should be.

The archive now has a named tiny wrapper and a state-coupled lifetime rule.
The remaining question is whether this wrapper should be exported by default,
only on request,
or kept purely local.

## Question

Should `boundary_context` be:
- export-default
- requestable
- or local-only?

## Source pattern

The source base again points to a middle answer.

- Telecom protection scenarios require downstream devices to be informed that traceability has been lost so they can switch behavior immediately; this is pressure for default visibility in some profiles.
- PMU / measurement-oriented material strongly pressures default visibility of timing state and quality, but not equally strong pressure for exporting the boundary explanation itself everywhere.
- NTPv5 reference-ID exchange shows a pattern where chain context can be retrieved when needed rather than being pushed in every minimal response.

That pattern argues against both extremes:
- always-exported globally is too heavy
- local-only everywhere is too weak

## Smallest visibility rule that survives the pressure

The current best answer is:

> `boundary_context` should be **requestable by default**, and **profile-default** only where omission would mislead live transition handling or control-path behavior.

This means:
- the archive does **not** promote `boundary_context` into the always-exported minimal state
- the archive does allow it to be requested when a client, relay, or operator needs the explanation
- profiles may still make it default-visible where boundary explanation itself is operationally load-bearing

## Why not export-default everywhere

Because most downstream consumers first need:
- current timing state
- timing quality / applicability
- and profile-required hook visibility

They do not all need the boundary explanation every time.
Making `boundary_context` universally default-exported would overstate how central it is.

## Why not local-only everywhere

Because some profiles really do need the explanation to travel.
Telecom protection behavior is the clearest current case:
- the fact of losing traceability is not merely internal bookkeeping
- it changes downstream behavior during holdover and path re-selection

That is enough to keep local-only from being the archive-wide default.

## Hook comparison

### `traceability_posture`
This is the stronger case for profile-default visibility.
When loss of traceability changes active control-path behavior,
omitting the explanation can mislead downstream participants during transition.

### `sync_dimension`
This is usually weaker.
Many consumers need the declared dimension itself more than they need the boundary explanation for why it changed.
That makes requestable visibility a better general fit here.

## Current archive judgment

`boundary_context` should be:
- **requestable by default**
- **profile-default where omission would mislead control or transition handling**
- **not globally always-exported**

This keeps the wrapper useful without inflating the minimal response surface.

## What this still does **not** settle

This note still does not decide:
- whether `boundary_context` should reuse the archive's existing discovery/request surface directly
- whether profiles should advertise support for boundary-context export explicitly
- whether operator-facing and machine-facing visibility should always match

## Next useful move

Test whether `boundary_context` can reuse the archive's existing small discovery/request surface,
or whether the wrapper needs separate visibility semantics of its own.
