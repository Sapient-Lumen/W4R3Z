# Migration map — rev0126 to rev0127

## Operational change

Chrony capture replay now treats `chronyc -n tracking` as the command that establishes the effective observation instant. The replay `collected_at` returned by `tools/chrony_capture.py --extract` is the tracking command's `start_wall`, not the collector envelope's final `collected_at`.

## Adapter change

`capture_context` now preserves both timestamps:

- `effective_collected_at` / `collected_at`: conservative tracking command start used for interval growth;
- `collector_collected_at`: final wall timestamp for the whole transcript.

Existing rev0126 capture envelopes remain structurally readable if they include the required command roles. Downstream consumers that displayed the collector-final timestamp as the observation instant should switch to `effective_collected_at` and treat `collector_collected_at` as envelope metadata.

## Validation change

`tests/fixtures/chrony/capture-delayed-tracking.json` proves that later `sources` and `sourcestats` commands cannot make the tracking observation look younger. The golden case expects a 300-second age at the P1 security boundary even though the collector envelope finishes ten seconds after the tracking command begins.

## Core invariant

No new TimeState field was added. The six-field core remains interval, timescale, freshness, regime, source posture, and applicability.
