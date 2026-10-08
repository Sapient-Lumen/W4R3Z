# Seed capture and portfolio diversity

A mutable seed portfolio is the road away from central entrances. It is also the easiest place to recreate centrality accidentally.

## Implemented

`seedcapture.py` adds:

```text
SeedCapturePolicy
SeedCapturePressure
analyze_seed_capture_pressure
select_diverse_seed_entries
```

The analyzer measures:

```text
known attacker weight fraction
max single-channel fraction
max single-family fraction
channel count
family count
garden/seed-gate count
```

The selector picks a bootstrap subset by alternating underrepresented channels and families, preferring gardenish entries when otherwise tied.

## Design guess

A default seed portfolio should not just be "a list". It should be a portfolio of entrance sources:

```text
maintainer defaults
community gardens
friends/direct invites
cached last-good contacts
classic-side leaks while central networks exist
room/buddy/search hints when user opts in
```

The DHT should make centrality progressively less relevant, not deny that entrances matter.

## Nonclaim

This is not an anonymity model. More entrance paths often mean more metadata. The test is about resilience and capture pressure, not privacy guarantees.
