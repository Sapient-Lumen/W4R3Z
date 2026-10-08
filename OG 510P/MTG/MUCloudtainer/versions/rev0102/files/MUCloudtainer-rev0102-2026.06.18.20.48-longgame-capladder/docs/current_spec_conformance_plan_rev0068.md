# Current specification and conformance plan — rev0068

`docs/muc5_spec.md` remains historically useful but is not a current specification; it begins at rev0002 and its last substantive addendum is near rev0010.

## Required current-spec sections

```text
card and deck legality
pregame/mulligan procedure
state and chance model
information states and public observations
legal macro-action grammar
priority/stack compression and intentional deviations
terminal conditions and utility
replay/event schema
agent boundary and hidden-information rules
C++ supported-transition contract
experiment/claim integrity contract
```

## Conformance matrix

Each normative clause should map to:

```text
Python directed test
Python property/fuzz test where appropriate
C++ parity or independent check where supported
replay fixture
known deliberate simplification
```

The new spec should be generated or versioned from one source rather than extended by unrelated appendices indefinitely.
