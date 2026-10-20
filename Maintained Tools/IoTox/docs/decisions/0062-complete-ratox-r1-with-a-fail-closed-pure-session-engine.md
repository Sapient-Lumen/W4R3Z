# ADR 0062: Complete Ratox R1 with a fail-closed pure session engine

Status: accepted
Date: 2026-08-16

## Context

ADR 0061 froze Ratox v1 framing, cumulative byte positions, attachment identity, and resource
ceilings before any PTY existed. `InputReceiver` and `OutputHistory` then proved whole-frame input
commitment and explicit output gaps, but the repository still lacked the object that owns a complete
session. In particular, a naive duplicate-result cache could execute a control side effect and only
then discover that result retention was full or allocation had failed. Attachment also needed to
apply a controller's cumulative output position without partially fencing the old controller first.

R1 must close those state-machine holes while remaining unreachable from toxcore, authority,
filesystem, process, terminal, and wall-clock code.

## Decision

Implement `MessageReplayCache`, `InteractiveSession`, and `SessionDirectory` as a pure C++20 library
beside the existing byte primitives.

- A control message ID is reserved before its side effect. Reservation stores the exact canonical
  request and preallocates a bounded result capacity. Commit cannot exceed that capacity. An exact
  committed duplicate replays the retained result; an exact in-progress duplicate is unavailable;
  conflicting bytes under the same ID are a protocol error. There is no public post-effect
  insertion shortcut: callers must reserve and then commit or cancel.
- Retained control IDs are not evicted. Entry or byte exhaustion refuses a new control before any
  effect instead of making an old ID executable again. Cancel releases a reservation only when the
  caller proves no side effect occurred.
- One session fixes its session ID and controller principal. Every accepted ATTACH or RESUME uses a
  fresh retained nonce, increments generation, and immediately fences the prior token.
- ATTACH and RESUME validate the controller's input/output positions against a copied output
  history. A valid cumulative output position releases acknowledged history in the same state
  transition as the new token. A position before the retained base accepts the attachment with an
  explicit gap fact. An impossible future position changes neither history, nonce retention, nor
  generation.
- A staged INPUT survives controller replacement. Partial sink failure makes the current
  incarnation terminal and invalidates its controller; uncertain bytes are never replayed into a
  replacement. Explicit incarnation replacement resets byte state, preserves generation fencing,
  and requires a fresh attachment.
- Controller CLOSE accepts only Ratox reasons 0..4. Internal termination alone may use process
  failure or daemon shutdown. The final content-free lifecycle event is recorded before input and
  output buffers are wiped. Control results remain retained so an exact duplicate CLOSE can still
  receive its original result. Existing pending reservations may finish after the transition, but a
  terminal session cannot reserve a fresh control effect.
- Session events contain identity, lifecycle, generation, incarnation, and cumulative positions,
  never terminal bytes. Their ring is bounded and reports dropped-event count. Rejected
  attachments distinguish invalid identity, invalid position, replayed nonce, quota exhaustion,
  and terminal lifecycle; stale INPUT tokens are recorded without copying input bytes.
- A device-local directory validates nonzero identity before occupancy checks and atomically
  enforces two sessions per principal and eight per device before publishing a session pointer. Its
  initial attachment uses the session's configured input/output sequence origins rather than an
  assumed value of one.
- Generation, incarnation, nonce, entry, byte, sequence, and quota exhaustion are checked before
  mutation. Feature bit 23 remains unset; no PTY, profile, authority-bit migration, Agent dispatch,
  local terminal client, or network advertisement is added.

## Consequences

R1 now has one deterministic model for duplicate control effects, attachment ownership, input
commitment, output catch-up, process replacement, close/termination, audit facts, and quotas. The
model can be unit tested and fuzzed without a socket or PTY. The interactive state fuzzer now drives
complete session sequences under AddressSanitizer and UndefinedBehaviorSanitizer in addition to the
standalone byte primitives.

The replay cache reserves the full promised result capacity before effect, then releases unused
capacity when commit copies the actual result into that already allocated storage. Retained-byte
accounting is therefore exact without introducing a post-effect allocation or cache-full window.
Because IDs are never evicted, a long-lived session can still exhaust its entry or byte budget; a
later protocol revision may add an authenticated epoch or durable compaction rule, but v1 fails
closed.

R2 authority-ledger migration and R3 local PTY/profile construction are now the next independent
prerequisites. R4 may integrate them only after both exist, and R8 remains the sole activation gate.
