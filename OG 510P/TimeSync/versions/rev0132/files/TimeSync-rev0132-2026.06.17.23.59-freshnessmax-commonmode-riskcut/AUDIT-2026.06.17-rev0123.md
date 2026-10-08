# TimeSync rev0123 audit — capture envelope and negative-delay hardening

## Highest-risk work addressed

rev0122 proved a replayed chrony transcript could become a conservative P1 TimeState. The next risk was capture integrity: without a transcript envelope, a future live path would still treat operator-facing text as if it had trustworthy collection timing.

rev0123 therefore adds a narrow capture layer before the evaluator:

```text
chronyc command transcript + wall/monotonic brackets -> validated replay evidence -> TimeState/profile decision
```

It also corrects a conservative-bound edge case: negative root delay can appear in chrony/NTP operational surfaces and must not reduce a safety interval.

## Concrete changes

- Added `tools/chrony_capture.py` for `chrony_command_capture_v1` transcript validation and live capture.
- Added command/version capture for `chronyc -v`, `chronyc -n tracking`, and `chronyc -n sources`.
- Added collector and per-command wall-clock and monotonic nanosecond brackets.
- Added capture tamper tests for inverted monotonic intervals, command intervals outside the collector bracket, and failed command replay.
- Refactored `tools/chrony_adapter.py --live` to route through the capture envelope and added `--capture` replay input.
- Added `tests/fixtures/chrony/capture-normal.json` as a deterministic capture fixture.
- Hardened the interval rule to use `0.5 * max(root_delay, 0)` instead of allowing negative root delay to shrink the bound.
- Added `examples/chrony/tracking-negative-root-delay.txt`, golden case `CHRONY-P1-NEGATIVE-ROOT-DELAY-CONSERVATIVE`, generated example `chrony-p1-negative-root-delay-conservative.json`, and semantic vector `TV-123-001`.
- Regenerated chrony-derived state/explanation examples so their policy reference and basis reflect rev0123.

## Refactor/audit performed

The capture work is kept in `tools/chrony_capture.py` instead of adding a generic evidence-capture registry. That choice matters: the immediate risk is command collection discipline, not a new vocabulary family. The adapter imports only the replay extraction boundary, so future non-chrony adapters can define their own capture envelopes without bloating the TimeState core.

The arithmetic audit found a concrete safety issue: `root_delay / 2` was used literally. Because negative root delay should not make a consumer more confident, the evaluator now clamps the delay contribution at zero. This is a deliberate waste of precision to preserve safety.

## Remaining risk

FT-0121 remains open. The live path exists but is not exercised in this cloud container because `chronyc` is not installed here. NTS/authdata verification, named UTC realization traceability, leap-smear discovery, RFC 9249 field comparison, and independent evaluator comparison remain future work.

## Validation delta

- Semantic vectors increase from 364 to 365.
- Chrony golden cases increase from 6 to 7.
- Capture envelope self-tests are executed through the chrony adapter self-test and normal archive validation.
- Mutation-survivor probes remain at 29; this pass avoids adding another broad mutation layer.
