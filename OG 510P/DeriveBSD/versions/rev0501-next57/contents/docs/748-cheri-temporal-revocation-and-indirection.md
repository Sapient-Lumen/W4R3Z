# CHERI temporal revocation vs authority revocation (design with indirection)

**Tier:** C (Optional lane)
**Profiles:** A, B, C, D
**Pillars:** isolation, operability, supply-chain
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate

DeriveBSD uses *leases* and mediated handles to revoke **authority** (who may do what).

CHERI-style systems also talk about *revocation*, but in a very different sense:
revoking **dangling pointers/capabilities** to enforce temporal memory safety.

This doc captures a subtle but important design lesson:
> authority revocation is cheapest when you have an indirection point.
> pointer revocation is expensive when you *remove* indirection.

DeriveBSD should bake this lesson into the optional CHERI lane and into its “leases everywhere” posture.


## Why this matters

- DeriveBSD favors capability-style designs (Capsicum, portals, object-cap RPC).
- CHERI enables fine-grained in-address-space compartmentation, but revocation is hard without a central point of control.

If DeriveBSD adopts CHERI for certain components, we should avoid designing hot paths that *require* frequent
“global” pointer revocation sweeps.


## Lessons worth stealing

### CHERIvoke / Cornucopia: revocation looks like GC
CHERI temporal safety techniques (e.g., CHERIvoke, Cornucopia) typically:
- quarantine freed objects
- periodically sweep memory to revoke capabilities that still reference freed objects
- trade off stop-the-world time vs heap growth and complexity

CheriBSD also exposes revocation policy controls (e.g., a sysctl default policy) for runtime revocation.

### Capability revocation wants indirection
A classic capability-system lesson is that revocation is easiest when you introduce indirection (proxy objects, forwarders).
DeriveBSD already embraces that for *authority* revocation via mediated handles (`docs/182-capability-leases-and-revocation.md`).


## DeriveBSD design implications

### 1) Keep authority revocation separate from pointer revocation
- **Authority revocation** (leases) should remain a broker/proxy concern and should be cheap.
- **Pointer revocation** (CHERI temporal safety) is a runtime/memory-safety concern and may involve sweeps/epochs.

Don’t let “revocation” vocabulary blur these concepts.


### 2) CHERI lane should treat temporal revocation as a *budgeted operation*
If we ever run CHERI-hardened long-lived daemons on tight latency budgets:
- model revocation epochs as scheduled/bounded work
- record revocation policy in evidence (a small “cheri runtime policy” receipt)
- consider applying budgets (CPU/time) to revocation sweeps, similar to GC pacing


### 3) Prefer indirection points at compartment boundaries
For security boundaries between compartments, indirection is a feature:
- object-cap RPC endpoints
- portal proxies
- activation escrow handles

Indirection enables cheap authority revocation even if the underlying implementation uses CHERI.


## Where it plugs in

- CHERI lane overview: `docs/163-cheri-capability-lane.md`
- Capability leases: `docs/182-capability-leases-and-revocation.md`


## References

- CHERIvoke (temporal safety via sweeping revocation): https://www.cl.cam.ac.uk/research/security/ctsrd/cheri/
- CHERIvoke paper (Micro 2019): https://www.cl.cam.ac.uk/research/security/ctsrd/pdfs/201910micro-cheri-temporal-safety.pdf
- Cornucopia / Cornucopia Reloaded (epoch/sweep approaches): https://www.cl.cam.ac.uk/research/security/ctsrd/pdfs/2020oakland-cornucopia.pdf
- CheriBSD temporal safety note (runtime revocation default): https://ctsrd-cheri.github.io/cheribsd-getting-started/features/temporal.html

Last updated: 2026-05-18r492
