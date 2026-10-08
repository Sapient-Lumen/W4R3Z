# Lease-route gossip pressure — rev0019

`leaseroute.py` joins two surfaces that were intentionally separate earlier: route gossip and contact leases. A route-gossip batch can look close and diverse while still carrying stale, expired, unleased, or forked contacts.

The local rule is:

```text
route-gossip repair should only commit selected contacts that have fresh, purpose-scoped, monotonic contact leases
```

The module does not make leases into global identity truth. It asks whether the repair set has enough live route-capable leases, enough lease-family diversity, and no lease fork pressure before it updates local routing memory.
