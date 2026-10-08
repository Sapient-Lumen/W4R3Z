# Effective rate policy, LAN exception, and scheduled throttle interface spec

## Purpose

The archive already had route truth, pause semantics, and transfer explanation language.
What it still lacked was one stricter contract for a quieter but very real operator question:

> what bandwidth policy is actually in effect right now for this seat and this subject, especially when LAN peers, scheduled rules, pause-like states, and global preferences do not mean the same thing?

Current Resilio docs make this seam concrete.
Their current preferences docs still say sending and receiving limits apply to internet connections by default, not LAN, unless `rate_limit_local_peers` is set in power-user preferences.
Their scheduler docs still say `Paused` cells stop upload/download bandwidth but still allow zero-sized files, deletions, rescans, indexing, and some uploads to non-paused peers.
Their current configuration-mode docs also still expose rate limits through declarative config, separate from the ordinary preferences surface.

That means effective rate policy is still reconstructed from several layers and exceptions.

## Core decision

AnonSync must expose one **effective rate-policy ledger** per seat and per subject.
The ledger must distinguish:

- WAN caps
- LAN caps
- schedule-derived caps
- explicit pause states
- non-rate activity that still proceeds under pause/throttle

The operator must never need to remember that `paused` is not fully paused or that LAN silently escapes the normal limit.

## Why this matters

Current Resilio behavior still leaves too much meaning distributed across preference pages and scheduler notes:

- global send/receive limits are not the whole story
- LAN can bypass those limits unless a different hidden preference is set
- scheduler rules live on a separate grid
- `Paused` still allows several state-changing operations
- config mode can define another source of truth

AnonSync should therefore hold one stronger rule:

> every cap, exception, and surviving side effect must be visible in one effective policy surface.

## Fixed review order

Every bandwidth or schedule review must render the same sections in the same order:

1. **Current effective caps**
2. **Scope stack**
3. **Activities still allowed**
4. **Upcoming schedule transitions**
5. **Rate-policy receipt**

### 1) Current effective caps

Show:

- current upload cap
- current download cap
- whether values differ for WAN and LAN
- whether the cap is unlimited, throttled, or zero
- whether the current subject inherits seat policy or overrides it

### 2) Scope stack

List policy layers in precedence order, for example:

- subject override
- seat global preference
- LAN override
- schedule window
- declared config
- emergency safe mode

The operator must be able to answer:

> which layer produced the number I am seeing right now?

### 3) Activities still allowed

This section must explicitly say whether the following still proceed under the current state:

- deletions
- placeholder or namespace announcements
- indexing / rescans
- zero-byte items
- uploads to specific peer classes
- local hashing or verification

### 4) Upcoming schedule transitions

Show:

- next scheduled change time
- next cap values
- which activities are still allowed during that window
- whether the transition is local-seat only or subject-specific

### 5) Rate-policy receipt

Record:

- policy layers considered
- effective WAN and LAN caps
- surviving activities under pause/throttle
- actor and seat for any mutation
- start and end time for schedule-driven state

## Main surface

Expose one **Rate policy** page reachable from both seat settings and subject details.
The page should use explicit labels such as:

- `wan limited / lan unlimited`
- `scheduled pause; deletions and indexing still propagate`
- `subject override replaces seat default`
- `declared config locked this cap`

## Acceptance criteria

This spec is satisfied when:

- the operator can tell the current WAN and LAN caps without visiting multiple settings layers
- `paused` never hides the fact that deletions or indexing still proceed
- schedule windows and global limits converge on one effective explanation
- every cap mutation leaves a receipt that names the winning layer
