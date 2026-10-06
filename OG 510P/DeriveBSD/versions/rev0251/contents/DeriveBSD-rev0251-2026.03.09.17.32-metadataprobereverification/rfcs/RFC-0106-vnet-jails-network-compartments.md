# RFC-0106: VNET jails as network compartments

Status: Draft

## Problem

DeriveBSD wants **policy-governed networking** with minimized blast radius. A shared host network stack creates subtle coupling:

* shared routing tables and neighbor caches
* hard-to-prove “this domain had no network” claims
* rule-only boundaries that are fragile under misconfiguration

## Proposal

Treat **VNET jails** as a first-class executor target for networked compartments.

* `netcompartment.realization = vnet-jail` creates a jail with a separate stack (`vnet=new`).
* the jail is connected via `epair(4)` to a host `bridge(4)` (or forwarding jail).
* `pf` anchors remain the policy composition layer.

## Non-goals (v0)

* full per-VNET `pf` management
* automatic DHCP inside VNET compartments
* replacing microVMs for hostile workloads

## Evidence

Emit:

* `netcompartment.intent`
* `netcompartment.realization`
* `netcompartment.topology`

and bind their digests into `plan_digest`.

## Security notes

* VNET is not a firewall; it is **separation**.
* Combine with deny-by-default `pf` and (optionally) FIB isolation.

## References

See `docs/171-vnet-jails-network-compartments.md`.
