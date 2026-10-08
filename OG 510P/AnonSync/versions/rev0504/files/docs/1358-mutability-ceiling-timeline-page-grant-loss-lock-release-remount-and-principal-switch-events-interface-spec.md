# Mutability-ceiling timeline page — grant loss, lock release, remount, and principal-switch events

## Purpose

This page keeps local-write truth chronological.
It exists so the product can explain how a subject moved between writable, blocked, unsafe, and continuity-broken states over time.

## Required event classes

### 1) Grant-issued / grant-lost

Examples:

- Android storage permission granted
- provider-root grant picked correctly
- provider grant lost or never issued
- NAS `rslsync` RW right added or removed

### 2) Lock-acquired / lock-released

Examples:

- app opened file exclusively
- SMB lock residue persisted after network issue
- lock recheck interval elapsed
- operator closed blocking app

### 3) Mount / health shift

Examples:

- drive missing
- mount returned
- file-system error detected
- fs repair completed

### 4) Principal or runtime-world switch

Examples:

- interactive user runtime changed to service user
- service moved to Local System
- new storage world appeared
- subject had to be re-added / re-shared

### 5) Host-lane shift

Examples:

- direct local access began while SMB users still mutate same files
- setup moved back to one consistent lane
- subject moved to safer local storage

## Timeline output rules

- Every event must say whether it changed **grant**, **principal**, **lane**, **barrier**, or **continuity**.
- Every event must say whether the stronger sentence `writeable now` was widened, narrowed, or remained blocked.
- Every world switch must say whether old folder continuity survived or had to be re-established.

## Final timeline sentence

The page must end with one summary sentence in this shape:

> `Current mutability ceiling is the result of <latest governing event>; stronger sentence <...> remains blocked because <...>.`
