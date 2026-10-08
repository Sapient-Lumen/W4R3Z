# simulator rev0049

No card-rule semantics changed in rev0049.

The simulator-facing change is evaluation policy: promotion-facing payoff rows
should be terminal-clean, and truncation diagnostics should stay separate from
normal standings.

The existing hidden-information contract remains unchanged:

```text
true GameState belongs to the referee
public agents see only DecisionFrame observation + legal actions
C++ shadows Python transitions but does not replace Python semantics
```
