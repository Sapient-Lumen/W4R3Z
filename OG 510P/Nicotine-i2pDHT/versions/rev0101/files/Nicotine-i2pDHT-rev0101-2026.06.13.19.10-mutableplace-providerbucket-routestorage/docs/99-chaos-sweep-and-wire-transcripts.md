# Chaos sweep and wire transcripts

rev0012 adds two supporting surfaces.

## `chaossweep.py`

A deterministic parameter sweep models captured fast windows.

Inputs:

```text
captured_families
honest_families
paths
max_per_family
fast_window_size
```

Outputs:

```text
accept_pressure
continue_fast_window_captured
continue_not_enough_families
```

This is deliberately toy-shaped. Its job is to keep pressure questions visible: if family caps change, does captured-fast-window risk change?

## `wiretranscript.py`

Signed transport-neutral wire frames:

```text
find_node
find_provider
provider_probe
witness_receipt
garden_refusal
mutable_head
```

The DHT should not wait for live SAM/I2P transport before testing canonical payloads, signatures, frame digests, transcript digests, and duplicate sequence detection.

## Current nonclaim

These are not production wire messages. They are fixtures for reproducible disagreement tests.
