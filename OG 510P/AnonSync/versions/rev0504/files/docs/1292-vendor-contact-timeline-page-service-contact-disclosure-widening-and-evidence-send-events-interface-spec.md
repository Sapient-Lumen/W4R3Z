# Vendor-contact timeline page: service contact, disclosure widening, and evidence-send events interface spec

## Purpose

This page exists to answer:

> when did vendor-visible facts widen, when did they narrow, and which changes came from automatic runtime behavior versus explicit operator choice?

## Core decision

AnonSync must expose one **Vendor-contact timeline** whenever service-contact posture, telemetry posture, or support-send posture changes.

## Timeline event classes

The timeline must distinguish at least these event families:

- tracker contact enabled or disabled
- relay fallback allowed, witnessed, or blocked
- landing-page claim event
- update-check enabled or disabled
- telemetry enabled or disabled
- diagnostics capture enabled
- diagnostics sent
- crash/profiler artifact exported
- billing / license identity disclosed
- vulnerability report submitted

## Per-event row fields

Each row must show:

- event time
- actor class (`automatic`, `operator`, `support-flow`, `purchase-flow`, `unknown`)
- disclosure delta
- intervention delta
- strongest safe sentence after the event

## Required comparisons

The page must keep three comparisons visible:

1. **automatic service contact** vs **explicit disclosure send**
2. **metadata widening** vs **artifact-content send**
3. **service reachability change** vs **vendor intervention power change**

## Honest outputs

This timeline may conclude:

- `service contact widened, but intervention power did not`
- `telemetry narrowed, but tracker metadata lane remained enabled`
- `diagnostic disclosure widened only after explicit operator send`
- `landing contact occurred without exposing fragment-contained capability material`

It may not let `support contacted` or `privacy mode on` stand in for the whole disclosure chronology.
