# Burst exception timeline page — authorize, borrow, renew, expire, payback, and restored normal entitlement events

## Purpose

This page renders the life of temporary extra-room use from exception request through authorization, live borrowing, renewal, expiry, payback, withdrawal, and restored ordinary entitlement.
It must show when out-of-envelope use was authorized, when that authority tightened or expired, and when the system actually returned to ordinary room truth.

## Required event families

### 1. Exception open events

- exception requested
- exception justified
- exception denied
- exception authorized
- borrowed room recorded

### 2. Live borrow events

- first authorized extra-room use seen
- first reserve-touch event
- first harmed-claimant consequence published
- first edge-of-exception warning
- first beyond-exception event

### 3. Renewal and expiry events

- renewal requested
- renewal granted
- renewal denied
- exception expired while still active
- exception withdrawn manually

### 4. Payback and restoration events

- payback obligation opened
- reserve restoration begun
- claimant relief begun
- payback partially completed
- payback completed
- ordinary entitlement fully restored

### 5. Escalation events

- throttle-back applied
- reclaim applied
- contention reopened
- future exception authority narrowed
- normalization risk escalated

## Timeline obligations

- distinguish `out of envelope` from `out of envelope under typed temporary authority`
- show when borrowed room source changed from shared headroom to protected reserve if that occurs
- show how long harmed claimants or reserve carried the consequence
- preserve payback as a typed event rather than inferring it from later lower usage
- allow operator to replay exactly when the exception was legitimate, when it ceased to be legitimate, and whether restitution actually closed the debt

## Stronger-sentence guard

The timeline may say `claimant kept running with extra room`.
It may not imply `claimant kept holding a valid exception` unless authorization and expiry events remain current and unbroken.