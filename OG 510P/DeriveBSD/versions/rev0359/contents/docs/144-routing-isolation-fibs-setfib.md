# Routing isolation with multiple FIBs (setfib)

pf is excellent for filtering, but egress control often needs **routing separation**:

- “builder/fetcher traffic must never share the host’s default route”
- “this microVM’s egress must go via gateway X, regardless of host routing”

FreeBSD supports multiple routing tables via **FIBs** (Forwarding Information Bases), selectable per process.

Primary references:
- setfib(1): https://man.freebsd.org/setfib
- setfib(2): https://man.freebsd.org/setfib.2

## Lesson to steal

- use a dedicated FIB for high-risk subsystems (fetch/build/update)
- make routing choice explicit and reviewable (policy decides, activation enforces)

## DeriveBSD mapping

### Derived object

- `net.fib.plan.json` binds compartments to routing tables:
  - `fib_id` per jail/service/microVM-runner
  - required routes (default gateway, blackholes)
  - pf anchor bindings (so filtering and routing intent stay aligned)

### Enforcement sketch

- create routes in each FIB as part of activation/network bringup
- launch subsystems under `setfib <fib_id> ...`
- (optional) treat “wrong FIB” as a policy violation, with evidence

### Evidence

- `net.fib.evidence.json`:
  - `net.fibs` configured maximum
  - route dumps per FIB
  - proof that each compartment is launched under the intended FIB

Candidate RFC: *FIB-aware compartments and pf composition*.

Last updated: 2026-02-23
