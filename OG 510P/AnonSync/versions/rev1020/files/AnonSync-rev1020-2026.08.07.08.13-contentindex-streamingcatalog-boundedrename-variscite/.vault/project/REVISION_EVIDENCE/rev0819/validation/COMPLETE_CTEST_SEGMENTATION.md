# Complete CTest accounting

CTest inventories 97 obligations. The tool execution window did not retain one
uninterrupted invocation long enough to finish the three slow final corpora, so
the release claim is deliberately narrower and exactly evidenced: four disjoint
CTest index ranges were executed against the same immutable, fully built Ninja
tree after the final active-source change.

- 1–34: 34/34 passed;
- 35–68: 34/34 passed;
- 69–83: 15/15 passed; and
- 84–97: 14/14 passed.

The ranges are disjoint and exhaustive: 97/97 passed, zero failed. No single
uninterrupted all-test invocation is claimed.
