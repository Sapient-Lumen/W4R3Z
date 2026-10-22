# Overseer Bootstrap History

## Purpose

Record the worked example of how the live Overseer house was actually
constructed, tightened, corrected, and expanded.

This is not meant to be a perfect chronicle.
It is meant to give future reasoners a truthful bootstrap narrative:

- what was built first
- what turned out to matter
- what failed or had to be corrected
- how the house shifted from ad hoc shell assistance to a legible stewarding
  system

## Phase 1. House formation

The first decisive move was to stop treating the real docs as a side directory.
`/home/overseer` became the house itself rather than a generic home containing
one important subtree.

That phase established:

- `WAKE.md`
- `CURRENT-FRONTIER.md`
- explicit house placards
- typed rooms under `state/`
- a human wing and human doorway rather than a second sovereign territory

The lesson from that phase is that the place had to become legible before it
could become ambitious.

## Phase 2. Stability and host truth

The second major phase was making the machine observable and low-entropy:

- `/etc/nixos` became a first-class versioned surface
- root, network, desktop, and backup surfaces were made explicit
- health rooms were added for system alerts, machine health, boot health,
  journals, storage, coredumps, and auth
- off-machine backup and restore drills were turned into real rooms

The lesson from this phase is that the Overseer cannot be credible if it only
knows its own repo and not its host.

## Phase 3. Browser, auth, and quota groundwork

The third phase established that browser truth matters:

- Firefox profiles were made explicit and named
- browser-side quota reading was proven with fallback layers
- browser automation planning became a first-class program
- auth state and quota state became part of house survival rather than
  incidental operator labor

The lesson from this phase is that dialogue continuity, quota, and OAuth are
not small convenience problems. They are survival surfaces.

## Phase 4. Loop substrate

The fourth phase built the loop substrate before there was any conductor:

- finite loops
- loop groups
- followups
- lineages
- holds
- deadman/autorescue
- loop observability and timing science

Then the first workers arrived:

- `audit-loop`
- `green-loop`
- `frontier-loop`

This phase proved something important: bounded workers are usable if they are
observable, subordinate, and able to stop themselves early.

## Phase 5. Attention stack

The fifth phase was the long paranoid pass over attention:

- routes
- integrity
- dynamics
- trends
- review memory
- governance
- actuation trust
- drills

This turned the front desk into something closer to an operating system for
attention rather than a pile of symptoms.

The lesson from this phase is that protecting attention is not cosmetic. It is
one of the core survivability problems.

## Phase 6. Archive as substrate

The current phase is treating the archive itself as part of the system:

- reproducible build
- bounded WebUI packet
- explicit north star
- trajectory map
- how-to-help surface
- metalooper planning surfaces
- archive-aware reconstruction logic

The house is no longer just exporting snapshots.
It is building a portable cognitive artifact.

## What this bootstrap history is evidence for

This house was not produced by one top-down design.
It was built by repeated cycles of:

- noticing a lie or fragility
- naming the surface
- making it explicit
- testing it
- tightening it again

That means the worked example is itself part of the design.
Future loopers, outside reasoners, and the eventual conductor/metalooper should
learn from this bootstrap history instead of pretending the system appeared in a
finished form.
