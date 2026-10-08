# Concurrency Contract Kit closure finality / post-close availability boundaries — 2026-03-23

This note exists to keep **P-0538 Concurrency Contract Kit** from collapsing too many lifecycle questions into one fake “closed means done” story.

## Keep these lanes separate

### 1. Closure finality
This answers:
- what closure finalizes right now.

Examples:
- immediate terminal state;
- drain-then-terminal state;
- reopenable closed state;
- close/send race with a maybe-already-stored value.

### 2. Post-close availability
This answers:
- what remains observable after closure and how it is accessed.

Examples:
- buffered tail still drains;
- retained broadcast history still drains;
- latest snapshot remains borrowable;
- an in-flight one-shot value may still be recoverable;
- nothing remains.

### 3. Delivery memory
This answers:
- what is remembered when nobody is ready right now.

### 4. Delivery acceptance
This answers:
- what producer-visible success meant at the moment of send / notify.

### 5. Observation evidence
This answers:
- what evidence exists later that anybody actually observed or processed the unit.

### 6. Delivery order / gap visibility
This answers:
- what sequence exists and how missed units are exposed.

### 7. Wait cancellation
This answers:
- what state is lost when a waiter is cancelled, dropped, or loses a race.

## What to reject

Reject bundle drafts that flatten any of the following into one fake verdict:

- the channel is closed, therefore no values remain to be read;
- the last sender dropped, therefore the receiver immediately becomes terminally empty;
- `changed` returned `RecvError`, therefore there is no current value left to inspect;
- `close` prevented future sends, therefore there is no in-flight value or retained tail left behind;
- a surface can be reopened, therefore previously closed intervals were never observable;
- buffered tail or last-snapshot access, therefore the surface provides receipt proof or durable history.

## Practical rule

If a primitive does not document exactly what closure finalizes and what remains available after closure, the artifact should say so explicitly and keep **manual review required** cheap to declare.
