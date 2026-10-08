# Array API kit fixtures

This fixture family supports **P-0003 Array API**.

It keeps five truths explicit:

1. `semantic-profile.receipt` — what family of array semantics is actually being promised;
2. `layout-view.receipt` — what shape/stride/order/view guarantees really exist;
3. `device-dtype.receipt` — what devices and dtype defaults exist at runtime;
4. `namespace-coverage.receipt` — what operation sets are intentionally supported and at what strength;
5. `interop-route.receipt` — how values cross crate or format boundaries and what is lost.

The point is not to prove that every numerics crate is secretly the same.
The point is to make their support surfaces reviewable without flattening dense n-D arrays, linear algebra, tensor backends, and columnar arrays into one fake “array support” verdict.
