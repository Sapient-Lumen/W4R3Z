# Pause semantics review page: download stop, upload/serve, delete propagation, and indexing branches interface spec

## Purpose

The activity-posture sheet says what is currently true.
This page exists for the narrower, more failure-prone question:

> when a user sees `paused`, what exactly still happens anyway?

That question deserves its own page because ordinary language is too lossy here.
Resilio's current docs themselves demonstrate why: one article describes pause as no download/upload while still syncing deletions and indexing new files; another describes scheduled `Paused` as stopping downloads while allowing uploads to other non-paused peers, again with deletion propagation and indexing still alive.
AnonSync must therefore review pause semantics explicitly instead of trusting the word.

## Core decision

AnonSync must require a **Pause semantics review** whenever any activity-control label suggests inertness while some work classes may still continue.

## Review layout

1. **Pause headline**
2. **Residual behavior matrix**
3. **Cause comparison rail**
4. **Operator surprise callouts**
5. **Blocked stronger sentence**

### 1) Pause headline

Show:

- pause label presented to the user
- current reviewed meaning
- strongest safe sentence
- blocked stronger sentence
- review freshness

Supported headline meanings:

- `download-paused-only`
- `bidirectional-byte-transfer-paused`
- `metadata-and-delete-still-live`
- `periodic-sleep-not-pause`
- `hard-stop-not-pause`
- `unknown`

### 2) Residual behavior matrix

Each row must cover one work class:

- peer visibility
- discovery / advertisement
- indexing / rescan
- zero-byte placeholder changes
- delete propagation
- upload of existing bytes
- download of missing bytes
- local change detection

Each row must show one of:

- `continues`
- `continues-conditionally`
- `stops`
- `unknown`

And it must include a short reason.

The operator must be able to answer:

> what will still happen to my tree if I walk away believing this is `paused`?

### 3) Cause comparison rail

Compare the semantics of these causes side by side:

- operator pause
- scheduler zero-rate window
- sleep / idle hibernation
- battery floor stop
- forbidden network

Hard rule:

- the UI may never imply these are interchangeable even if they all reduce transfer volume

### 4) Operator surprise callouts

This section must print reusable warnings for high-surprise combinations, including:

- `Deletes still propagate while byte transfer is paused.`
- `New files may still be indexed while download is paused.`
- `This state hides from peers entirely because the core is asleep.`
- `This is not a pause at all; it is a policy stop caused by battery or network conditions.`
- `This limit does not include LAN traffic.`

### 5) Blocked stronger sentence

Examples:

- `Nothing will change while paused` blocked because indexing remains live
- `Peers cannot see this device right now because it is paused` blocked because visibility loss is caused by sleep, not pause
- `Bandwidth is capped everywhere` blocked because the cap excludes LAN
- `This share is manually held` blocked because the active gate is scheduled or battery-driven

## Hard rules

- the page must review the word presented to the user, not just the underlying machine state
- delete propagation must always be called out explicitly when it survives a pause-like state
- `sleep` must never be presented as a synonym of `pause`
- when docs or runtime evidence disagree, the page must preserve the ambiguity instead of smoothing it over
