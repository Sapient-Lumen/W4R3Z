# Quiet runtime proof page — hidden window, background process, and control-surface truth

## Purpose

Prove what still exists and what still runs when a runtime is not visibly foregrounded.

This page exists to answer:

- `is the runtime merely quiet or actually absent?`
- `what control surface still exists?`
- `what work can still continue?`
- `what stronger stop or non-exposure sentence is blocked?`

## Required sections

### 1. Runtime quietness class

Must show exactly one current class:

- `foreground-visible`
- `minimized-visible`
- `window-hidden runtime active`
- `service runtime active`
- `headless runtime active`
- `process absent`
- `unknown`

### 2. Surviving surfaces

Must list each surviving surface with reachability and mutability truth:

- local workbench
- browser/local-web surface
- remote-reviewed control surface
- CLI/TUI attachment
- tray or shell affordance
- none

### 3. Continuing work block

Must publish whether the runtime may still:

- transfer bytes
- publish deletions or structural updates
- index or rescan
- keep sockets/listeners open
- accept control requests
- auto-start later under standing policy

### 4. Quietness provenance

Must show whether quietness comes from:

- operator launch choice
- standing startup policy
- service profile
- headless deployment profile
- crash / abnormal absence
- unknown observation gap

### 5. Strongest safe sentence

Examples:

- `The main window is hidden, but the reviewed service runtime is still active and reachable through loopback control.`
- `This session is minimized only; it is not a stop state.`
- `No live control surface is currently proven, but the last reviewed autostart policy may reopen one later.`

### 6. Blocked stronger sentence

Examples:

- `No window means Sync is stopped.`
- `Silent launch means nothing can still move.`
- `Headless means uncontrolled.`
- `Tray absence proves process absence.`

## Interaction rules

- this page must be reachable from any `quiet`, `hidden`, `background`, or `service` status chip
- stop actions must link out to stop-proof / drain review rather than impersonating visibility changes
- receipt export must keep quietness provenance and continuing-work truth adjacent

## CLI examples

```text
anonsync runtime quietness show
anonsync runtime quietness prove --seat self
anonsync runtime quietness receipt <receipt>
```

## Non-clone conclusion

Resilio's present docs still make operators piece together silent start, minimized UI, service backgrounding, browser-open control, and headless Linux behavior from multiple articles.
AnonSync should instead let `quiet` answer one honest question in one place.
