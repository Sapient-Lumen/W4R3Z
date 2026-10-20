# Per-namespace synchronization four-root rollback-witness evidence

- Date: 2026-09-02
- Host: IoTox founding x86_64 Linux machine
- Decision: ADR 0312

## Direct gate

The source-linked Clang build and complete owned registry ran as:

```sh
cmake --build build/witness-clang -j2 --target iotox_tests
nix develop --command ctest --test-dir build/witness-clang \
  -R '^iotox\.unit-and-integration$' --output-on-failure
```

Result: `800/800 tests passed` in 35.44 seconds.

The 16 Clang AddressSanitizer/UndefinedBehaviorSanitizer owned-registry shards also passed:

```sh
nix develop --command sh -c \
  'cmake --build build/clang-asan-ubsan -j2 --target iotox_tests && \
   ctest --test-dir build/clang-asan-ubsan -L owned-registry --output-on-failure -j2'
```

The 13 dedicated checks cover:

- stable namespace-domain derivation, 64-way separation, and device/base-domain separation;
- digest changes for namespace ID/root/engine/every quota and each published, accepted, activated,
  and retained root;
- explicit tree-v2 refusal;
- publish, accept, activate, pin, and unpin advancement;
- local root replacement that does not land versus one that lands despite a late error;
- lost replies after both remote pending and final committed CAS;
- recovery of local pending/root-old/external-old, local pending/root-new/external-old, local
  pending/root-new/external-pending, and local-committed/external-pending;
- refusal of local-old/external-pending, third heads, same-position forks, pending-target forks,
  and wrong selectors;
- rollback refusal before an otherwise early mutator decision; and
- a namespace-transaction reader blocked from observing a locally landed successor until the
  external witness commits.

## Two-guest gate

The retained NixOS/Sandwurm-style test ran as:

```sh
nix build .#checks.x86_64-linux.rollback-witness-service-vm -L --no-link
```

Result: pass. One Agent guest and one witness guest used separate processes and virtual disks. The
source-linked binary enrolled authority, application incarnation, Ratox incarnation, route
generation, terminal policy, command effects, complete sync policy, update lifecycle, and two
range-v1 namespace four-root records through the authenticated TCP service. The namespace records
used different derived domains at lane 9.

The Agent published the `notes` namespace and advanced its external record. With that service record
left current, the test removed the complete published root and matching local rollback guard,
recreating the valid enrolled-empty snapshot. The next Agent start refused and did not create the
named RuntimeTree. Restoring the exact current root and guard allowed startup. Existing complete
policy-tree rollback, update-policy substitution, route, terminal, startup-incarnation, authority,
service-outage, restart, and wrong-key cells also remained green.

## Evidence boundary

The direct matrix establishes the bounded four-root state machine and in-process serialization. The
two guests establish authenticated protocol and state separation on one hypervisor. They do not
establish physical or administrative independence, rollback resistance of the witness disk itself,
or a live lease against another concurrently running clone.

The lane covers only the signed published, accepted, activated, and retained semantic roots for
non-tree-v2 namespaces. It does not prove content correctness or availability, backup, complete
custody, health-record freshness, object/quarantine/projection/current-pointer freshness, tree-v2
frontier/workspace/maintenance freshness, or safe permanent deletion.
