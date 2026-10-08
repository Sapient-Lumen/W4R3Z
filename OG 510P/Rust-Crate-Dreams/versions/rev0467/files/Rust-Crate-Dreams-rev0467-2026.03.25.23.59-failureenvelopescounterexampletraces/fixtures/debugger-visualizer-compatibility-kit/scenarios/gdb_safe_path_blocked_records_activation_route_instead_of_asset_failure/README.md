# Scenario — GDB safe-path refusal is an activation-route fact, not asset corruption

This scenario models a crate that ships an embedded GDB pretty-printer script and whose asset discovery succeeds.
The debugger still declines to auto-load it because the binary path is outside the configured safe path.

The point of the receipt is to keep the explanation honest:
- the asset exists,
- the backend lane is intended,
- but the activation route was blocked by trust policy.
