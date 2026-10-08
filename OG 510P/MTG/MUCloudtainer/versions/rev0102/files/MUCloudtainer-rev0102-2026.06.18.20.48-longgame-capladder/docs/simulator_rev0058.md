# Simulator note — rev0058

rev0058 does not change gameplay semantics.

New code is analytical/refactor code around terminal mechanisms and decomposition experiment generation:

```text
src/muc5/terminal_mechanisms.py
src/muc5/terminal_decomposition.py
```

The live decomposition panel used the existing Python simulator as semantic authority and C++ as a chosen-transition parity shadow.

Validation result:

```text
terminal games: 192 / 192
truncations: 0
C++ mismatches: 0
replay passed: 8 / 8
```
