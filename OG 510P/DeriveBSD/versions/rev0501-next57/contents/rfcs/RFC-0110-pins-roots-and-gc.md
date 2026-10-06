# RFC-0110: Pins, roots, and garbage collection

Status: Draft

## Problem

DeriveBSD accumulates generations, images, and store objects. Without explicit liveness, retention becomes ad-hoc and unsafe.

## Proposal

Introduce explicit **roots** and **pins** that define reachability for garbage collection.

* roots are typed references to digests and (where applicable) ZFS snapshot identifiers
* pins are operator/user named roots
* GC is a deterministic reachability computation from roots

## Evidence

* `pin.add.receipt`, `pin.rm.receipt`
* `gc.plan` and `gc.run.receipt`

## References

See `docs/175-pins-roots-and-garbage-collection.md`.
