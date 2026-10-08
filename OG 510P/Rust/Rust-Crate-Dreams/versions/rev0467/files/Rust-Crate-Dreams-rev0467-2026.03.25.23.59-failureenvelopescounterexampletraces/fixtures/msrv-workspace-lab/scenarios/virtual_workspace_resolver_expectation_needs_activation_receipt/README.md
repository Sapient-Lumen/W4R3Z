
# Virtual workspace resolver expectation needs activation receipt

This scenario exists to show that a member’s edition or local expectation is not enough to prove that the workspace is actually using the intended MSRV-aware resolver policy.

What should happen:
- the receipt should show that the workspace is virtual,
- the expected policy was `fallback`,
- the observed policy remained `allow`,
- and the activation failure came from missing explicit root resolver configuration rather than from a member manifest.

The point is not “resolver v3 exists”.
The point is that another reviewer can see whether the expected policy was truly active.
