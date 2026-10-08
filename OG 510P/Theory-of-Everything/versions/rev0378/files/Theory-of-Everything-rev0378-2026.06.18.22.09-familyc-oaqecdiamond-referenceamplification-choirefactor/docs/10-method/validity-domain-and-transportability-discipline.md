# Validity-domain and transportability discipline

This surface owns the rev0268 rule that local evidence is not automatically portable evidence.

A route may hold support inside a source domain while failing to support the same wording in a target domain. The archive therefore separates:

1. **source domain** — where the record, proof, benchmark, simulation, catalog, or laboratory result was produced;
2. **target domain** — where someone wants to spend the result;
3. **preserved invariant** — what is allowed to travel;
4. **shift variables** — what may change between source and target;
5. **transport map** — the explicit rule, formula, reconstruction map, RG map, frame map, likelihood reweighting, or validation argument that licenses transfer;
6. **residual cap** — what authority remains after transport.

The default is nontransport: evidence remains source-domain support until `TRANSPORTABILITY-LEDGER.json` says otherwise. This mirrors the transportability lesson from causal inference: internal validity is not enough to license target-population validity when source and target domains differ. In this archive the "population" may be a code subspace, simulator ecology, EFT scale range, survey likelihood, detector regime, reference frame, compactification chart, or observed-sector target.

## Route-local rule

A route can use generalized or portable wording only when:

- a `DOMAIN-OF-VALIDITY-LEDGER.json` row declares source/target domains and preserved invariants;
- a `TRANSPORTABILITY-LEDGER.json` row declares a source-to-target map or explicitly says no such map exists;
- the target wording stays below the route's promotion ceiling;
- measurement, systematic, calibration, contrast, prior, evidence-credit, public-record, negative-control, and rollback handles remain live;
- no extrapolation fence is violated.

## Non-promotion rule

Domain and transport rows can only restrict, split, quarantine, or repair authority. They cannot promote a route. A successful transport row means the archive knows how to move one bounded support object; it does not mean the candidate is identified, the observed sector is recovered, or a ToE is closed.
