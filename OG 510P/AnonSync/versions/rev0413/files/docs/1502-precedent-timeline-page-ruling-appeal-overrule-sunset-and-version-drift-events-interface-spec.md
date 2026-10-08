# Precedent timeline page: ruling, appeal, overrule, sunset, and version drift events interface spec

## Purpose

After the archive learned how to prove doctrine, it still needed one chronology page for operators asking:

> how did this doctrine become what it is now, and which later appeal, fix, or version drift event changed what we are allowed to claim?

## Core decision

AnonSync must expose one first-class **Precedent timeline** page for every materially reused doctrine path.

## Required event families

- source ruling issued
- precedent docket opened
- doctrine adopted
- exception granted
- distinction recorded
- appeal opened
- precedent narrowed
- precedent overruled
- precedent sunset
- version drift detected
- downstream recall sent

## Event-row schema

Each row must show:

- timestamp
- event family
- affected doctrine sentence
- old binding weight
- new binding weight
- scope delta
- who caused the change
- downstream cases affected
- stronger sentence newly allowed or blocked

## Hard rules

### 1) Version drift is a doctrine event

A later product fix or changed warning meaning must appear on the doctrine timeline if it changes how older rulings should be read.

### 2) Overrule cannot erase history

The timeline must preserve what doctrine existed before the overrule and which dependent cases were still shaped by it.

### 3) Appeal must be durable

An appeal cannot live only inside comments on the old ruling.
It must appear as a timeline event with visible effect on doctrine certainty.

## Empty state

If no reusable doctrine exists yet, show:

- `No doctrine timeline yet. The case history exists, but no reusable precedent has been adopted.`
