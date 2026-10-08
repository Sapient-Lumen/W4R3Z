# Remedy-flight-protection timeline page — start, suspend, resume, preempt, stall, and abort events

## Purpose

This page is the chronological surface for how a repair lane moved from runnable to started, interrupted, protected, stalled, resumed, or collapsed.
It exists so later readers can see whether an apparently promising start actually enjoyed bounded interruption risk.

## Event families

The timeline must support at least these event families:

- cure start requested
- cure start admitted
- first byte or first object committed
- queue preempted by stronger work
- queue rebuilt materially
- scheduler window opened
- scheduler window closed during flight
- pause asserted
- pause released
- hidden-task stall detected
- watcher-loss or rediscovery lag detected
- source disappeared mid-flight
- source continuity restored
- service-metadata integrity failed
- cure resumed after interruption
- finish-protection strengthened
- finish-protection collapsed
- cure aborted

## Required fields per event

Each event row must preserve:

- timestamp and time-authority basis
- actor or system trigger
- affected cohort
- affected object set
- interruption class
- prior posture rung
- resulting posture rung
- strongest sentence gained or lost
- compensating or recovery action
- receipt pointer

## Timeline invariants

- the page never compresses `started`, `preempted`, `stalled`, `resumed`, and `aborted` into one activity blur
- the page always records whether an interruption was allowed ordinary behavior or a genuine breach of finish protection
- the page preserves which cohort lost protection when only part of the case degraded
- the page never lets a later resumption erase earlier interruption history
