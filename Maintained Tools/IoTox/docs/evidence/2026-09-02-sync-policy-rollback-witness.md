# Synchronization-policy rollback-witness evidence

Date: 2026-09-02
Host: founding x86_64-linux machine; two NixOS guests
Decision: ADR 0310

## Direct gate

```bash
nix develop -c cmake --build build/witness-clang --target iotox_tests iotox -j4
nix develop -c ctest --test-dir build/witness-clang \
  --output-on-failure -R '^iotox\.unit-and-integration$'
```

The direct registry passed 783/783 checks. The new check creates a strict empty policy store, then
adds one canonical namespace and one stable-device-signed automation. Empty, namespace-only, and
complete-tree digests are distinct; repeat encoding is stable; and a duplicate namespace is
refused. Existing namespace and automation codec/store tests retain their complete validation and
ownership checks.

The generic policy-witness checks additionally prove durable intent before CAS, prepared and
pending lost-reply recovery, refusal of a complete old checkpoint/digest restoration, and refusal
of a same-domain backend outside tests.

## Two-guest gate

```bash
nix build .#checks.x86_64-linux.rollback-witness-service-vm \
  --no-link -L --max-jobs 1 --cores 4
```

The Agent guest initializes a strict empty namespace index and creates a device-signed
`sync-policy` enrollment. The witness guest installs it without replacement. A source-linked Agent
then reconciles all seven lanes through the authenticated TCP service and serves local control. A
live `sync-create notes /var/lib/iotox/sync-source` durably installs the namespace, commits that
candidate tree, durably installs its automatic publication record, commits the complete tree, and
activates both in the running Agent.

After clean stop, the guest restores the complete valid enrolled-empty namespace/automation view
and its matching signed local checkpoint while the remote service remains at the post-create head.
The next Agent start fails and the requested RuntimeTree is absent. Exact-current policy restoration
then preserves the existing outage, service-restart, wrong-key, authority, incarnation, route,
terminal-policy, and final-recovery cells.

## Evidence boundary

The direct gate proves the canonical policy-tree commitment. The VM proves enrollment, actual
authenticated service traversal, two live Agent-mediated mutations, startup reconciliation, and
whole-policy rollback refusal beside all six earlier lanes. It does not mutate policy concurrently
from a second process, inject a crash at every policy-store fsync/CAS boundary, or witness any
per-namespace data/runtime state.

Both guests share one physical and administrative failure domain. This is protocol/state-separation
evidence, not proof of an independently administered or rollback-resistant production witness.
