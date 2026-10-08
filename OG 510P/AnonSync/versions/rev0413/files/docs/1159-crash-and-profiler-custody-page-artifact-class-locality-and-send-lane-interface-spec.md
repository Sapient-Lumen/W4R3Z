# Crash and profiler custody page: artifact class, locality, and send lane interface spec

## Purpose

This page answers:

> what heavy diagnostic artifacts can exist here, where do they live, which runtime/profile produced them, and what exactly would it mean to export them outward?

The page exists because profiler traces, minidumps, crash reports, and core dumps are not one evidence family.

## Core decision

Whenever the operator opens or requests heavier-than-log diagnostics, AnonSync must render one first-class **Crash and profiler custody** page.

The page owns:

- artifact family
- originating runtime/profile
- local storage locality
- collection preconditions
- export sensitivity
- post-export residue state

## Fixed page order

1. artifact family header
2. runtime and locality card
3. collection-precondition card
4. export lane card
5. residue and cleanup card

### 1) Artifact family header

Show:

- artifact family (`profiler trace`, `crash report`, `minidump`, `core dump`, `mixed`, `unknown`)
- origin runtime (`desktop app`, `service-local-user`, `service-localsystem`, `linux package runtime`, `mobile app`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

### 2) Runtime and locality card

Show:

- current or expected local path class
- seat/profile attribution
- whether a runtime/profile change could move the artifact root
- whether the artifact is already present or only armed for later creation

### 3) Collection-precondition card

Show:

- prerequisite class (`restart`, `profiler toggle`, `wait for crash`, `run from terminal`, `ulimit change`, `manual device extraction`, `unknown`)
- whether the incident/crash has already occurred
- whether additional operator work outside the main UI is needed

### 4) Export lane card

Show:

- recommended review lane (`private archive`, `vendor support`, `trusted teammate`, `self-serve analysis only`, `unknown`)
- sensitivity class (`high`, `very high`, `unknown`)
- whether redaction/minimization is feasible or limited

### 5) Residue and cleanup card

Show:

- what stays local after export
- whether cleanup is automatic, UI-driven, or manual
- whether export completion is weaker than custody closure

## Rules

### Rule 1 — profiler and crash artifacts may not hide under generic logs language

The operator must see that these are heavier artifact classes with different locality and risk.

### Rule 2 — runtime/profile attribution must stay visible

If service-user or storage-root differences can move artifacts, the page must publish that plainly.

### Rule 3 — export is weaker than cleanup

Sending a crash dump may still leave the local copy present and sensitive.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- what exact heavy artifact family is involved
- which runtime/profile owns it
- where it lives or will live locally
- what has to happen before it can even exist
- what still remains local after export
