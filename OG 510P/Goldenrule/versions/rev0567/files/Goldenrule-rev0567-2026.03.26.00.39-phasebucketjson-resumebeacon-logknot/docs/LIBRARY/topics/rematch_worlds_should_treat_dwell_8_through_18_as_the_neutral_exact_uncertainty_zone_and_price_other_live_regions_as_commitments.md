# Rematch worlds should treat dwell 8 through 18 as the neutral exact uncertainty zone and price other live regions as commitments

The exact compact repeat-state uncertainty menu now has enough structure that implementors should stop treating all live dwell regions as interchangeable.

The saved cards support a cleaner rule:

- dwell `8–18` is the **neutral exact zone** whenever dwell is not physically forced;
- insisting on dwell `2` is an **expensive precision commitment** unless the required exact floor really exceeds `0.980481`;
- insisting on dwell `19–32` is a **relaxed-only commitment** unless cap or tolerance constraints themselves force the lower-guarantee lane.

That rule is sharper than a generic tier summary. Relative to the neutral `8–18` band, insisting on dwell `2` buys only `+0.019341` more exact floor but costs `+6` hard-cap steps, `+6` pre-amortization checkpoints, all positive anchor slack, and almost all band width. Insisting on dwell `19–32` goes the other way: it saves only `2` cap steps and `3` checkpoints before amortization, while giving back `0.109999` exact floor.

So the current menu should be read as three different **commitment types**, not just three labels:

- `8–18` is the default zone for strong non-fragile operation,
- `{2}` is the precision-only override,
- and `19–32` is the relaxed suffix you enter only when external dwell shape or tolerance limits really force it.
