# Authenticated remote authority-witness evidence

Date: 2026-09-02
Host: founding x86_64-linux machine; two NixOS guests, Linux 6.6.94
Decision: ADR 0305

This records the ADR 0305 authority-only checkpoint. ADR 0306 subsequently widens the retained
two-guest gate; see `2026-09-02-incarnation-rollback-witness.md` for its current three-lane result.

## Owned protocol and integration checks

```bash
nix develop -c cmake --build build/witness-clang --target iotox iotox_tests -j4
nix develop -c ctest --test-dir build/witness-clang \
  --output-on-failure -R '^iotox\.unit-and-integration$'
```

The direct registry passed 767/767 checks. The eight ADR 0305 additions require:

- an exact persistent authenticated query/begin/query/commit/query sequence;
- one winner from two simultaneous clients presenting the same exact expectation;
- refusal of a response whose signature does not match the pinned witness identity;
- refusal of a modified signed durable service record after restart;
- exact device/domain/epoch/head enrollment binding and signature-tamper refusal;
- exclusive ownership of one service store;
- a real `AuthorityLedger` RecallRoot bootstrap and restart through the TCP backend; and
- service survival after an accepted client closes before sending the fixed request.

The source-linked release derivation also built with GCC 13 warnings-as-errors and emitted a
validated six-package SPDX 2.3 JSON document.

## Two-guest state-separation gate

```bash
nix build .#checks.x86_64-linux.rollback-witness-service-vm \
  --no-link -L --max-jobs 1 --cores 4
```

The retained test runs two isolated NixOS guests. The witness guest owns a dedicated witness-role key,
private store, and TCP listener. The Agent guest owns a different device key, Tox savedata, authority
ledger/guard, exact intent, and runtime. The test passes this sequence:

1. create an empty authority state and a device-signed position-zero enrollment;
2. enroll once on the witness guest and pin its returned public key on the Agent;
3. survive the harness's truncated TCP port probe;
4. start the real Agent and commit RecallRoot bootstrap through pending to position one;
5. save the exact current ledger/guard, then delete both to reconstruct the valid position-zero local
   state while the service remains at position one;
6. require Agent refusal and absence of the requested runtime tree;
7. restore the exact current pair and start successfully;
8. stop the service, require connection-refused startup and no runtime tree;
9. relaunch the service from the same durable store, reject a wrong pinned public key before runtime;
   and
10. start successfully again with the correct pin.

## Boundary of the evidence

These guests have distinct disks and processes but share the founding host, hypervisor,
administrator, clock, and physical failure domain. The result proves protocol logic and complete
Agent-disk rollback detection while the service disk remains advanced. It does not prove protection
against coordinated restoration of both disks, rollback of the service's own disk, malicious host
root/kernel, network availability, transport confidentiality, geographic independence, or any
witness lane beyond authority at this checkpoint.
