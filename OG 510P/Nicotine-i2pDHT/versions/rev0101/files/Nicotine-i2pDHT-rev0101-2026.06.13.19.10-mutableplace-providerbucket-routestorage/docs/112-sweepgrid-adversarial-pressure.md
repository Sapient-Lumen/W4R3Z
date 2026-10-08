# Sweepgrid adversarial pressure

`sweepgrid.py` is a boring deterministic pressure map. It does not simulate I2P, churn, or real attackers. It varies a few hard knobs that have repeatedly mattered in this cube:

- family count
- captured-family count
- false-provider fraction
- stale-head fraction
- captured latency advantage
- fast-window size

The purpose is to avoid one-off tests where the happy path wins because the fixture was too small.

## Why a grid now?

The DHT design has accumulated many local rules:

- do not trust same-family evidence as diversity;
- do not accept provider records without semantic confirmation;
- do not accept signed mutable heads without local history and path pressure;
- do not treat fast answers as automatically good answers.

A grid lets us check how these rules interact when pressure dimensions rise together. The current decisions are:

- `accept_low_pressure`
- `continue_capture_pressure`
- `continue_false_provider_pressure`
- `continue_stale_head_pressure`
- `continue_fast_window_capture`
- `quarantine_combined_pressure`

The most important behavior is not the exact thresholds. It is that combined pressure escalates before the local node accepts a convenient answer.
