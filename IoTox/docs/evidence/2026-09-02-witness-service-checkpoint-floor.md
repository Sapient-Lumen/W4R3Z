# Witness-service complete checkpoint-floor evidence

- Date: 2026-09-02
- Host: IoTox founding x86_64 Linux machine
- Decision: ADR 0313

## Direct gate

The source-linked Clang build and complete owned registry ran as:

```sh
cmake --build build/witness-clang -j2 --target iotox_tests iotox
nix develop --command ctest --test-dir build/witness-clang \
  -R '^iotox\.unit-and-integration$' --output-on-failure
```

Result: `804/804 tests passed` in 33.49 seconds.

The four dedicated checks establish:

- deterministic service-signed encoding of the complete strictly sorted selector population;
- exact preservation of committed and pending wire records;
- expected-service-key pinning and signature failure after byte mutation;
- acceptance of an exact floor and a legitimately advanced descendant;
- refusal after selective restoration of an older authentic service record;
- refusal when a formerly enrolled selector is absent; and
- acceptance of an exact pending floor and its committed successor, but not its predecessor.

## Two-guest gate

The retained source-linked NixOS VM ran as:

```sh
nix build .#checks.x86_64-linux.rollback-witness-service-vm -L --no-link
```

Result: pass. The witness guest exported `IOTXWCP1` after all ten service records were enrolled and
verified it offline against the public key captured from witness-key creation. It started the real
TCP service with that checkpoint as a mandatory floor. After the Agent guest advanced its lanes, the
witness guest stopped the service, exported a new ten-record floor, and selectively restored the old
but correctly signed authority service record. `witness-service-serve` refused with exit status 3
before binding. Restoring the exact current record allowed restart against the advanced floor and
the Agent completed its final authenticated startup.

## Evidence boundary

The checkpoint directories and both virtual disks remain on one founding machine and hypervisor.
This proves format, CLI, complete-population scan, floor comparison, refusal-before-bind, and recovery
logic. It does not prove separate administration, storage-media rollback resistance, off-host
availability, checkpoint transport or retention policy, service-key protection, a live clone-fencing
lease, witness replacement/epoch handoff, or emergency re-anchor. A coordinated rollback of the
service and its only trusted checkpoint copy remains outside the protection boundary.
