# Workflow acceptance checklists

These checklists turn workflow names into concrete proof expectations.

## surface-detect
- correct surface key identified
- wrong or unsupported routes do not claim support falsely
- lane and URL context recorded
- route/history continuity captured when context could be ambiguous
- evidence includes at least one state or probe artifact

## receiver-resolve
- candidate count recorded
- chosen receiver or ambiguity stated explicitly
- multi-frame or shadow-root concerns noted
- failure path records why resolution was unsafe or impossible

## composer-read
- editable/not-editable state reported
- empty/non-empty state reported
- text readback is honest about truncation or masking
- evidence includes state snapshot or equivalent read record

## composer-write
- target receiver recorded
- before/after state or readback captured
- action outcome says attempted/result/reason
- failure path distinguishes receiver error from editor write error

## turn-submit
- submit target recorded
- action outcome emitted
- transient submit cues captured but not overread
- post-submit generation, route, or no-op state checked
- failure path distinguishes disabled submit, wrong target, silent no-op, and ambiguous navigation

## generation-read
- status emitted with honest uncertainty when needed
- transition or progression hints captured if available
- transient status/live-region cues separated from durable completion
- partial vs complete state distinguished
- failure path does not fake idle if state is unknown

## latest-turn-read
- latest turn identity or rationale for ambiguity stated
- partial vs complete latest turn distinguished
- speaker attribution present when available
- parsing, virtualization, route, or overlay caveats surfaced

## support-capture
- support bundle or equivalent manifest written
- workflow statuses included or linked
- route/history and transient-cue artifacts included when relevant
- evidence refs stable enough to inspect later
- next action included when capture reveals failure or drift
