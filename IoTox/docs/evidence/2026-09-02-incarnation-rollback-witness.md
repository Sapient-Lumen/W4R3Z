# Application and Ratox incarnation-witness evidence

Date: 2026-09-02  
Host: founding x86_64-linux machine; two NixOS guests, Linux 6.6.94  
Decision: ADR 0306

## Direct checks

```bash
nix develop -c cmake --build build/witness-clang --target iotox_tests -j4
nix develop -c ctest --test-dir build/witness-clang \
  --output-on-failure -R '^iotox\.unit-and-integration$'
```

The direct owned registry passed 772/772 checks. ADR 0306 adds five checks. They require:

- separate application and Ratox enrollment at absent position zero, followed by exact startup
  advances to positions one and two;
- refusal of a restored, valid, device-signed position-one record while the external lane remains at
  position two;
- a durable pending transition with exact local-new state and intent after an injected final-CAS
  failure, then deterministic completion before the next startup advances again;
- production refusal of an in-process/same-domain backend; and
- an application incarnation advance across the actual signed ADR 0305 TCP client/server protocol.

## Two-guest gate

```bash
nix build .#checks.x86_64-linux.rollback-witness-service-vm \
  --no-link -L --max-jobs 1 --cores 4
```

The retained gate creates distinct Agent and witness VM disks and dedicated device/witness
identities. The Agent first creates its ordinary application state, then installs an owner-private
Ratox profile for a real UID-1000 login account. With the Agent quiescent it generates three
device-signed, no-replace enrollments: authority at position zero, application at its exact current
signed record, and absent Ratox at position zero.

The source-linked Agent starts with all three remote lanes. RecallRoot bootstrap advances authority;
each successful security initialization consumes the next application and Ratox incarnation before
runtime creation. The gate then independently restores:

1. complete pre-bootstrap authority state while the authority witness remains advanced;
2. a prior exact application incarnation while authority and Ratox remain current; and
3. a prior exact Ratox incarnation while authority and application remain current.

Each case fails and leaves the requested runtime path absent. The Ratox-rollback case may consume an
application incarnation first by the documented lane order, but exposes no runtime/network/effect
surface. Exact-current restoration, complete service outage, durable service restart, wrong pinned
key, and final recovery also pass.

## Evidence boundary

The result proves the transaction, Agent integration, and isolated rollback detection while the
witness disk remains current. It does not prove physical or administrative independence, the
witness service's own rollback resistance, high availability, arbitrary kernel/filesystem behavior,
terminal profile/binding freshness, or any later route/sync/update/effect lane. The two guests share
the founding host and hypervisor.
