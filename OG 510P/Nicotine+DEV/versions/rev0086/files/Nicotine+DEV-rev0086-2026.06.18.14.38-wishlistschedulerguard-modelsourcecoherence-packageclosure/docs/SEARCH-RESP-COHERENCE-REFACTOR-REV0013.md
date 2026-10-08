# SEARCH-RESP coherence refactor — rev0013

## Canonical report-candidate

```text
SEARCH-RESP-01 = U-163
```

U-163 is the coherent lead because it captures the source/scope binding invariant. It can also absorb useful regression checks for token shape and response generation.

## Supporting rows, not standalone strict reports

```text
U-262 = private result-list parse-before-display-policy support
U-267 = invalid-token prefix decompression support
U-266 = accepted response full-list materialization before visible UI cap
U-263 = hidden/filter result-limit accounting backlog
U-264 = first visible claimed-username wins; UI consequence of source/scope binding
U-265 = parse-before-term include/exclude policy backlog
U-254 = parse-before-ignore/IP policy backlog
U-270 = connection lifetime after search result; already public-adjacent/pruned
```

## Why this matters

A pile of separate fixes could be incoherent: one cap in the GUI, one token tweak in the parser, and one private-result preference check would still leave a user-scoped response accepted from the wrong source. The coherent fix should begin with a response-admission object that knows token, mode, request generation, and expected source constraints, then apply parser budgets and UI policy ordering under that root.

## Backlog effect

This refactor reduces future reports. Only U-163 remains strict/front-lane. The other search-response rows should become regression tests or hardening tasks under the same report unless a later harness proves a genuinely separate high-impact invariant.
