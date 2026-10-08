# Precedent lineage receipt page: binding weight, scope, version window, and overrule boundary interface spec

## Purpose

After the archive learned how to track doctrine history, it still needed one final handoff page that answers:

> what exactly is the current doctrine sentence, how strong is it, where does it apply, and how could a later operator lawfully challenge or overrule it?

## Core decision

AnonSync must expose one first-class **Precedent lineage receipt** whenever doctrine is published for reuse beyond the originating case.

## Fixed page order

1. **Receipt header**
2. **Current doctrine sentence card**
3. **Binding-weight and scope card**
4. **Version and world window card**
5. **Overrule and exception boundary card**
6. **Blocked stronger sentence card**

### 1) Receipt header

Show:

- precedent receipt id
- governing doctrine id
- source ruling ids
- current doctrine owner
- publication time
- latest rereview time
- current status

### 2) Current doctrine sentence card

Required rows:

- exact current doctrine sentence
- case class covered
- explicit exclusions
- allowed citation class
- weaker sentence outside scope

### 3) Binding-weight and scope card

Required rows:

- binding weight
- scope breadth
- dependent active cases
- known exception count
- latest distinction recorded

### 4) Version and world window card

Required rows:

- minimum version covered
- maximum tested version covered
- world or lane applicability
- known drift beyond window
- sunset or rereview trigger

### 5) Overrule and exception boundary card

Required rows:

- who may distinguish locally
- who may overrule globally
- evidence needed for each
- interim hold rule
- recall obligations if doctrine changes

### 6) Blocked stronger sentence card

Required rows:

- strongest safe doctrine sentence
- strongest blocked overclaim
- what evidence would unlock it
- what evidence would collapse it

## Hard rule

A precedent receipt must let a later operator answer four questions immediately:

- what is the doctrine?
- how strong is it?
- where does it apply?
- how can it lawfully change?

If any of those are missing, the receipt is incomplete.

## Empty state

If the ruling never became reusable doctrine, show:

- `No precedent receipt: this ruling remains case-only and may not be reused as doctrine.`
