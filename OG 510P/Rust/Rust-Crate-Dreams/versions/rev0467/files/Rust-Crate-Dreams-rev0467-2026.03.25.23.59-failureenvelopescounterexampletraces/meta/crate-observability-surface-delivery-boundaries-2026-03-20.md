# Crate observability-surface delivery boundaries — 2026-03-20

This note keeps **P-0518 Crate Observability Surface Pack Kit** from quietly collapsing **route truth** into **delivery/completeness truth**.

## The new boundary

`bridge-route.receipt` answers:

- where a signal family can go,
- which integration path carries it,
- and whether extra glue is required.

It does **not** answer:

- whether every event is delivered,
- whether a queue may drop records,
- whether a metric is exported per event or only after aggregation,
- whether traces are sampled,
- or whether clean shutdown / `force_flush` / last-provider-drop is required to make “delivery” honest.

That is the job of **delivery posture** and **completeness class**.

## What belongs inside P-0518 after this pass

A proposal is still inside **P-0518** when the missing value is primarily about one or more of these:

1. **signal inventory**
2. **activation truth**
3. **bridge-route truth**
4. **schema/convention posture**
5. **sensitivity / redaction posture**
6. **delivery posture**
7. **completeness class / operator expectation**
8. **release-to-release observability-surface drift**

## What does not belong here

### 1. Not a queue/appender/exporter implementation

A missing nonblocking writer, batching queue, or collector/exporter improvement is telemetry plumbing.
**P-0518** may import those facts, but it is not itself the implementation lane for them.

### 2. Not a sampling processor or collector policy product

Head sampling, tail sampling, collector-side tail processors, or vendor sampling control planes are separate operational products.
**P-0518** only records what sampling posture another team is expected to assume for one crate’s signals.

### 3. Not a durability or delivery-SLO platform

A backend that guarantees retention, retries, or transport durability is not the same thing as a crate-authored support contract.
**P-0518** can say `best_effort_buffered` or `representative_sample`; it does not become a storage guarantee layer.

### 4. Not runtime lifecycle support

Shutdown barriers, cancellation verbs, and timeout aftermath belong to **P-0520**.
Observability delivery truth may import flush/shutdown posture, but it should stop at “what claim is honest for this signal surface?” rather than turning into generic service-teardown tooling.

### 5. Not generic performance or memory profiling

Continuous profiling, overhead measurement, and backend memory pressure belong elsewhere.
**P-0518** only needs enough cost/delivery vocabulary to keep operators from overclaiming what the published signal surface means.

## Working rule for future passes

When a future pass touches telemetry support, it must state explicitly which question it is answering:

1. **Can the signal be activated?**
2. **Which route carries it?**
3. **What does the name/field mean?**
4. **Is the field safe?**
5. **What delivery shape is in play?**
6. **What completeness class is honest?**
7. **How did the support surface drift across releases?**

Do **not** let the archive quietly say “the crate exports metrics/logs/traces” when the real missing question is “sampled, lossy, periodic, or flush-dependent under which route?”
