# Concurrency Contract Kit delivery-audience boundaries — 2026-03-23

This note exists to keep the new delivery-audience / consumption-claim slice of **P-0538** from dissolving into adjacent lanes.

## Keep these claims separate

### 1. Delivery audience is not delivery memory
A surface may remember one permit, the latest value, or bounded history, but that still does not say whether one observer or many observers are eligible to see it.

### 2. Consumption claim is not backlog pressure
Blocking senders, overwriting history, or risking unbounded growth tells you what happens under pressure, not whether one observer claiming a value excludes others.

### 3. Delivery audience is not fairness
FIFO or eventual fairness may order waiters, but it still does not say whether the delivered unit goes to one claimant, every active receiver, or each receiver’s own seen-state cursor.

### 4. Consumption claim is not cancellation class
A receive operation can be cancel safe while still being exclusive-claim, and a surface can have per-receiver seen state while still having distinct cancellation caveats.

### 5. Delivery audience is not executor / runtime choice
This lane does not replace runtime adapters, actor frameworks, or channel implementations.
It exports receiver-facing support reports over them.

## Adjacency guardrails

- If the main question is what is remembered or overwritten, stay in delivery-memory / backlog-pressure first.
- If the main question is whether a dropped waiter loses place or state, stay in wait-cancellation first.
- If the main question is starvation or queue order, stay in fairness first.
- If the main question is who can observe a unit and whether one observer’s receipt blocks others, this slice owns it.

## Doctor-rule direction

Future doctor checks should reject at least these false equivalences:

- “multiple receivers exist” == “every receiver gets each message”
- “subscribable” == “fanout clone delivery”
- “latest shared state” == “every send is retained for every receiver”
- “cloneable receiver” == “broadcast channel”
- “wakes all current waiters” == “future observers are included”
