# Canary join after settlement

`canaryjoin.py` is a no-network side-effect gate.

A SAM canary and router canary can both be valid while still being unsafe if they do not bind to the same settlement store and tomb repair join. The canary join rejects missing tomb repair, boundary drift, terminal state that unexpectedly carries retry escrow, retry state without retry escrow, and hard-negative pressure.

The point is not to perform I2P/SAM transport. The point is to prevent future live side effects from being authorized by a canary that rehearsed a different local state.
