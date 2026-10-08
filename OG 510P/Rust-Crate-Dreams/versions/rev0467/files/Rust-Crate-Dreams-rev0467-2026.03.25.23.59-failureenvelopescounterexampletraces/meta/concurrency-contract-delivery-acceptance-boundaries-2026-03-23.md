# Concurrency Contract Kit delivery-acceptance / observation boundaries — 2026-03-23

This note exists to keep **P-0538 Concurrency Contract Kit** from collapsing too many message-passing questions into one fake “send succeeded” story.

## Keep these lanes separate

### 1. Delivery acceptance
This answers:
- what producer-visible success means right now.

Examples:
- endpoint was still open;
- a wake/permit was recorded;
- a value became the latest shared state;
- a queued unit was admitted;
- at least one active receiver existed.

### 2. Observation evidence
This answers:
- what evidence exists later that anybody actually observed or processed the unit.

Examples:
- none;
- only a close signal;
- only an active-receiver-count hint;
- only receiver-local seen state;
- explicit application-level ack required.

### 3. Delivery audience
This answers:
- who could observe one wake/value/message unit.

### 4. Consumption claim
This answers:
- what one observer taking / marking the unit does to others.

### 5. Delivery memory
This answers:
- what is remembered when nobody is ready right now.

### 6. Backlog pressure
This answers:
- what happens when producers outrun consumers.

### 7. Wait cancellation
This answers:
- what state is lost when a waiter is cancelled, dropped, or loses a race.

## What to reject

Reject bundle drafts that flatten any of the following into one fake verdict:

- `send` returned `Ok`, therefore the receiver definitely processed it;
- there was at least one active receiver, therefore the value definitely reached all of them;
- the sender can detect closure, therefore the sender can prove receipt;
- the surface notifies receivers, therefore future receivers inherit the same accepted unit;
- the primitive stores a permit/value/message, therefore it also exports proof that somebody observed it.

## Practical rule

If a primitive does not document end-to-end receipt proof, the artifact should say so explicitly and keep **application-level acknowledgment** cheap to declare.
