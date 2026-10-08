# ADR 0061 — SAM shadow before live I2P transport

## Decision

Create SAM shadow transcript fixtures before implementing live SAM/I2P transport.

## Reason

Live router state would make basic integration assumptions harder to audit.  The cube should first test ordering, persistent destination assumptions, session creation, stream connect shape, and unsupported feature assumptions.

## Consequence

`samshadow.py` validates streaming-first SAM transcript shapes while explicitly rejecting premature dependence on SAM 3.3 datagram/primary subsession support in the bundle-first i2pd path.
