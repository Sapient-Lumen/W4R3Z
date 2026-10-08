# Scenario — Windows preedit keyboard-input overlap requires dedup

This scenario models a Windows backend where IME preedit is active but plain `KeyboardInput` events still leak through.
The point is to keep **transaction truth** honest:

- the adapter must record the overlap,
- the engine must say whether it applied, ignored, or deduplicated the leaked keys,
- and the resulting bundle must not pretend the platform behaved like a clean single-channel IME stream.
