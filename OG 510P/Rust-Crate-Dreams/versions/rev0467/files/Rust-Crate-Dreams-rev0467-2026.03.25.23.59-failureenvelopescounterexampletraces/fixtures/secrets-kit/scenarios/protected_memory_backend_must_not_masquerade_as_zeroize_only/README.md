# protected memory backend must not masquerade as zeroize only

This scenario captures an application that uses a protected-memory backend from the `secrets` crate.

That posture is stronger than ordinary zeroize-on-drop handling and should be reported distinctly.
