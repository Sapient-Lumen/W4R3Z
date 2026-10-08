# Research — playerctl pack and MPRIS thin adapters

## Main lesson

When Linux already ships a shared media-control contract, VHK should not force media automation back through fake generic desktop replay. It should expose a thin adapter seam.

## What others are teaching us

- MPRIS is already the shared contract: media players expose common methods, properties, and change signals over D-Bus rather than requiring focus-sensitive key replay.
- `playerctl` is explicitly built on top of that contract and adds two practical operator surfaces that matter for VHK design:
  - `--follow` for streaming state/metadata changes
  - `playerctld` for “most recently active player” policy

## Product implication for VHK

That means the right VHK move is not “add media support” as another hidden runtime mode. The right move is:

1. let the planner recognize MPRIS-shaped projects
2. materialize a reviewable adapter pack for them
3. keep VHK as the macro runtime while the bus/media tool owns target-player discovery and follow semantics

## Why a thin pack is enough for now

A thin pack gives operators the real integration seam immediately:

- a route catalog they can review
- exact playerctl/VHK command examples
- helper wrappers they can test in print mode before enabling `vhk run` dispatch

That closes a meaningful gap without pretending every media app should be driven through one bespoke VHK daemon.
