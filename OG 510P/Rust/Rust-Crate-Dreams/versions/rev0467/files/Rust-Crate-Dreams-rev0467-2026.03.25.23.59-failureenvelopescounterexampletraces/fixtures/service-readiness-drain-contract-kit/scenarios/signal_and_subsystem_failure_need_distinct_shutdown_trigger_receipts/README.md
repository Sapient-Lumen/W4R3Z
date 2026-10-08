# shutdown trigger classes must remain explicit

This scenario keeps **OS-signal shutdown** separate from **subsystem-failure-triggered shutdown**.
A service may support both, but they should not be flattened into one vague ‘shutdown happens somehow’ claim.
