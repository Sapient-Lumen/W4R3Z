# Review Order

This file tells a future LLM where to spend attention first.

## Main rule

Do **not** start by reviewing whatever paper was touched most recently.
Start with the papers most likely to survive publication without dragging a moving tail behind them.

## Suggested order

1. **Standalone-series papers first**
   - `series/anonymity_series/`
   - `series/anondht_state_series/`
   - `series/bossfight_series/`
   - `series/certified_series/`
   - `series/congestion_series/`
   - `series/evaluation_series/`
   - `series/operational_series/`
   - `series/release_and_destination/`

2. **Early synthesis foundations second**
   - use these to understand interfaces, crosswalks, and receipts
   - do not assume they are the first public entrypoints just because they are important internally

3. **Late synthesis tail last**
   - especially the successor / challenge-answer / source-only reissue sub-tail
   - default posture is defer / hold unless a future turn records a specific stabilization reason

## Why this order is conservative

The patch notes show repeated extension of the late synthesis tail through recent archive revisions.
That is exactly the kind of movement that should push a family later in the review order, not earlier.

## Operational takeaway

A future turn should usually choose **one** paper from the standalone-series bucket or write **one** family-level hold note about a high-churn tail.
