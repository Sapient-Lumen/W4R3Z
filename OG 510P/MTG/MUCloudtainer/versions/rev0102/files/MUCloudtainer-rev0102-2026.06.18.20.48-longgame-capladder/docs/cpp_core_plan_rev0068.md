# C++ core plan — rev0068

## Current decision

Do not expand the C++ hot core merely because a new revision exists. The current bottleneck is strategic validity and research-object integrity, not demonstrated transition throughput.

## Continue

```text
retain existing C++ transition/segment parity checks
keep directed mismatch diagnostics
use C++ when a measured experiment is blocked by runtime
```

## Next C++-related priority

Use C++ or another independent framework for **semantic independence**, not only speed:

```text
independent reduced-game state representation
legal-history corpus cross-check
information-state serialization cross-check
terminal utility cross-check
OpenSpiel adapter feasibility
```

Promotion of a new hot kernel should include a benchmark showing the experiment-level wall-clock benefit and a parity corpus that does not derive expected outputs solely from the same Python execution path.
