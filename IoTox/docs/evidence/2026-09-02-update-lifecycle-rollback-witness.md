# Update-lifecycle rollback-witness evidence

Date: 2026-09-02
Host: founding x86_64-linux machine; two NixOS guests
Decision: ADR 0311

## Direct gate

```bash
nix develop -c cmake --build --preset clang-debug --target iotox_tests iotox --parallel 3
nix develop -c ctest --test-dir build/clang-debug \
  --output-on-failure -R '^iotox\.unit-and-integration$'
```

The direct registry passed 787/787 checks. The four update-lifecycle checks use the real canonical
policy, release identity, signed bundle, immutable slot, signed update state, and `UpdateStore` state
machine around an exact-CAS backend. They prove refusal after deletion/restoration to the enrolled
absent state, recovery when either pending or final CAS applied but its reply was lost, exact
successor installation from the signed intent, and forward pointer repair after witnessed apply.

The complete pre-existing update suite remains unchanged in default-off mode. It covers stage,
apply, later-incarnation health admission, confirmation, health expiry, automatic rollback, both
legacy pointer/state interruption directions, abrupt process exit, tamper, slot capacity,
quarantine recovery, payload-kind binding, and unsafe-root refusal.

## Two-guest gate

```bash
nix build .#checks.x86_64-linux.rollback-witness-service-vm \
  --no-link -L --max-jobs 1 --cores 4
```

The Agent guest creates a range-v1 delivery namespace, release identity, canonical update policy,
and an absent-state `update-lifecycle` enrollment. The witness guest installs it without replacement.
The source-linked Agent then authenticates all eight lanes through the TCP service before exposing
RuntimeTree. Replacing the enrolled update policy with a different canonical target is refused before
the requested runtime path appears; restoring the enrolled bytes recovers. Existing outage,
service-restart, wrong-key, authority, incarnation, route, terminal-policy, sync-policy, and final
recovery cells remain in the same gate.

## Evidence boundary

The direct gate proves live lifecycle advancement and exact crash joins. The VM proves real remote
enrollment/query and policy-substitution refusal but does not yet inject remote-service loss during a
live update transition. Neither guest has a separate physical/admin failure domain. No test here
claims payload quality, precious-data trust, permanent deletion, or witness replacement safety.
