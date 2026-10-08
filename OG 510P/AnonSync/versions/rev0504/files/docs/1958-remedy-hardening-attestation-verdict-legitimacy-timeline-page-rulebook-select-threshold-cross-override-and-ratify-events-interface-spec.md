# Remedy-hardening-attestation verdict-legitimacy timeline page — rulebook select, threshold cross, override, and ratify events

## Purpose

This page is the ordered event view for adjudication questions after witness trust is established.
It exists so later operators can see whether the case moved from trusted clues into a legitimately governed verdict, or whether rulebook ambiguity, authority disputes, threshold failure, or exception review kept the stronger sentence blocked.

## Event classes

The timeline must support at least these events:

- target sentence proposed
- rulebook candidate attached
- rulebook selected
- rulebook version changed
- world or platform scope changed
- adjudicator assigned
- adjudicator authority challenged
- burden class selected
- trusted evidence admitted
- trusted evidence excluded
- threshold not met
- threshold met for named slice
- tie-break opened
- tie-break resolved
- override or exception review opened
- override or exception granted
- override or exception denied
- verdict ratified
- broader stronger sentence blocked
- rulebook superseded

## Required columns

- timestamp
- event class
- source evidence or rulebook reference
- resulting verdict-legitimacy class
- stronger sentence newly allowed or newly blocked

## Hard rules

The timeline must never collapse:

- trusted witness arrival and rulebook selection into one event by default
- threshold met and ratified verdict into one event by default
- override opened and override granted into one event by default
- rulebook change and unchanged verdict legitimacy into one event by default
- named-slice threshold crossing and broader stronger sentence into one event by default
