# Bounded source note — Bloom-filter mechanics — rev0070

Source: NIST publication page and PDF for *A New Analysis of the False-Positive Rate of a Bloom Filter* by Ken Christensen, Allen L. Roginsky, and Miguel Jimeno, published October 15, 2010.

Evidence references: `turn517676view0`, `turn517676view1`, and PDF screenshot `turn382894view0`, researched June 18, 2026.

Bounded mechanics used here:

- insertion sets several hash-selected bits in a bit array;
- a query whose selected bits are all set is treated as possibly present;
- a nonmember can map only to bits already set by other records, producing a false positive;
- in the standard insertion-only form, false negatives are not expected;
- small filters can show significant error in classic approximate false-positive-rate predictions.

The P0005 artifact proves its own exact bit state and makes no empirical rate claim. No full publication is reproduced.

Non-claim: technical source support only; not literary evidence, security certification, or evidence about any real person or case.
