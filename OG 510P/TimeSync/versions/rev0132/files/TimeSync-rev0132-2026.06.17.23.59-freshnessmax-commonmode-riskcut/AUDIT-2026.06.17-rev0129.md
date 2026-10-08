# TimeSync rev0129 audit — second-adapter risk cut

## Risk selected

The highest remaining substance risk after rev0128 was chrony monoculture. The project had a stronger capture envelope, authentication no-overclaim posture, and an independent evaluator over typed chrony observations, but it still had only one implementation family proving the six-field waist.

## Corrective change

rev0129 adds `tools/ntpq_adapter.py`, which consumes sanitized `ntpq -c rv` and `ntpq -pn` text, emits `ntpq_observation`, and evaluates P1 using an adapter-specific conservative bound:

```text
abs(offset) + rootdisp + 0.5 * max(rootdelay, 0) + clk_wander_ppm * age / 1_000_000
```

The adapter uses ntpq peer tally only to assess `source_posture`; it does not claim independent roots, named UTC traceability, leap-smear discovery, or packet authentication.

## Refactor/audit work

- Added adapter-family policy IDs to `evaluator/p1-chrony-policy.json` so the shared lane table no longer needs string replacement for non-chrony output.
- Refactored `tools/rfc9249_crosswalk.py` to validate both chrony and ntpq observation crosswalk files.
- Added `tests/rfc9249-ntpq-observation-crosswalk.yaml` to prevent ntpq fields from being promoted into TimeState core just because they resemble RFC 9249 operational-state leaves.

## Remaining risks

- No live `ntpq` or `chronyc` run happened in this cloud container.
- No NTS packet/session, symmetric-key MAC, or packet transcript verification exists.
- The ntpq adapter parses one common readvar/peers display style; it is not a complete ntpq dialect matrix.
- UTC remains unqualified and leap-smear policy remains undiscovered.
- PTP remains untested.

## Next best move

Run both `chrony_capture.py` and a future `ntpq_capture.py` on real hosts, retain their command envelopes, and compare replay outputs. If live evidence remains unavailable, the next useful local cut is a packet-transcript verifier design that refuses to output verified authentication until cryptographic material is present.
