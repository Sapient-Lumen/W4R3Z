# Spill mailbox and retention frontier

Revision: rev0028

## Why this frontier exists

The SAB frame ring proved fast bounded memory transport. But real browser workloads will hit bursts: parsing, rendering, media, indexing, and cross-worker pipelines can all temporarily produce faster than downstream lanes consume.

BrowserRT needs a principled answer that is better than either:

```txt
unbounded memory queue
```

or:

```txt
random app-level file writes
```

## Provider contract shape

The current provider contract is intentionally tiny and fake-provider friendly.

## Current provider contract

The rev0025 fake spill mailbox requires a provider with:

```ts
put(bytes, fields) -> { ref, digest, bytes }
get(ref) -> Uint8Array
delete(ref) -> boolean
snapshot() -> provider status
```

This deliberately matches the baby block-store contract already in the cube.

## Delivery-semantics ladder

```txt
at-most-once-memory-only
at-least-once-until-ack
recoverable-until-checkpoint
persistent-until-retention
exactly-once facade via idempotent consumer, not a transport guarantee
```

rev0025 proves only **at-least-once-until-ack inside one process**.

## Watermarks

Future spill mailboxes should expose at least:

- memory high watermark;
- memory low watermark;
- spill high watermark;
- provider quota threshold;
- pending age threshold;
- reclaim/replay threshold.

High water should tell producers to slow down. Low water should tell them they may resume. A boolean `isFull` is too coarse.

## Retention and compaction

Future retention modes:

```txt
ack-delete
age-delete
size-delete
key-compact
manual-retain
```

Kafka-style delete/compact vocabulary maps surprisingly well to BrowserRT mailboxes, but BrowserRT should keep this small until concrete workloads demand it.

## Failure semantics

A spill mailbox should distinguish:

```txt
oversize frame
memory full but spill accepted
memory full and spill rejected
provider quota exceeded
provider unavailable
provider checksum mismatch
pending frame reclaimed
pending frame acked
```

The producer cannot make a good decision if all failures collapse into “queue full.”

## Non-claims

rev0025 does not claim:

- OPFS spill;
- durable persistence;
- crash replay;
- cross-tab coordination;
- compaction;
- throughput or latency;
- multi-producer or multi-consumer correctness.
