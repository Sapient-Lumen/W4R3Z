# Remedy-hardening-attestation recurrence-watch review page — after clean state, can stale reliance re-enter before the watch horizon closes?

## Review goal

This page is the explicit review surface for deciding whether a once-clean outsider state can stay trustworthy without hidden operator vigilance.
The page must foreground recurrence and recontamination rather than merely replaying the original remediation steps.

## Review questions

The page must ask, in direct language:

- after the outsider reached clean state, what named channels could still reintroduce stale reliance before the watch horizon closes?
- which of those channels are still open right now?
- which channels are automatically contained versus merely noticed later?
- what proof would survive if the operator, live UI, or short-window history were unavailable?
- what exact stronger sentence remains blocked because the watch posture is incomplete?

## Required review sections

### 1. Last clean boundary

Show the exact event or evidence that established the last accepted clean state.
Do not allow `it looked fine` or `sync was green` to suffice.

### 2. Re-open channels

Present a checklist with at least:

- offline change returns later and outranks newer online state
- archive restore or historical copy replay
- delayed discovery due to rescan-only or disabled watch posture
- partial effects during pause / scheduler windows
- read-only local edits suspending future synchronization
- conflict artifact mishandling that preserves or reintroduces stale state
- disconnected or copied local residue outside the main share path

### 3. Detection and lag

Require the reviewer to name:

- immediate detector
- periodic detector
- manual detector
- no-present-detector channels
- maximum honest lag before the outsider would learn about recurrence

### 4. Containment posture

Require a direct verdict for each channel:

- prevented
- detected quickly
- detected late
- only discoverable by support or operator review
- unknown

### 5. Strongest sentence panel

The review must end with:

- strongest honest recurrence-safe sentence
- blocked stronger sentence
- exact blockers
- next review trigger or horizon-close trigger

## Failure pattern warnings

The page must visibly warn against at least:

- treating one successful clean-state proof as perpetual safety
- assuming `paused` or `scheduled` means no meaningful changes can occur
- assuming recent quiet means no hidden offline or archive-based reopen channel exists
- assuming short-window history is enough for later recurrence disputes
