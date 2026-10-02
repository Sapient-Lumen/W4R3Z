# Mutable-command effect rollback-witness evidence

Date: 2026-09-02
Host: founding x86_64-linux machine; two NixOS guests
Decision: ADR 0309

## Direct gate

```bash
nix develop -c cmake --build build/witness-clang --target iotox_tests iotox -j4
nix develop -c ctest --test-dir build/witness-clang \
  --output-on-failure -R '^iotox\.unit-and-integration$'
```

The direct registry passed 782/782 checks. The new check constructs a real signed command store and
proves that its empty and merely received frontiers agree, that a principal/authority-bound
`STARTED` mutable command changes the digest, and that terminal result/delivery churn leaves it
unchanged. With effect retention enabled at a two-record ceiling, an eligible read-only result is
pruned and the effect identity remains.

The retained generic policy-witness checks additionally prove durable intent before CAS, prepared
and pending lost-reply recovery, refusal of complete old checkpoint/digest restoration, and refusal
of a same-domain backend outside tests.

## Two-guest gate

```bash
nix build .#checks.x86_64-linux.rollback-witness-service-vm \
  --no-link -L --max-jobs 1 --cores 4
```

The Agent guest derives the empty effect frontier from its existing signed command store, creates a
device-signed `command-effect` enrollment, and the witness guest installs it without replacement.
The source-linked Agent then authenticates and reconciles that lane beside authority, application
incarnation, Ratox incarnation, route generation, and terminal policy before RuntimeTree. The
retained outage, service restart, wrong-key, terminal-policy rollback, route rollback, incarnation
rollback, and complete authority rollback cells continue to pass.

## Evidence boundary

The direct gate proves the precise frontier and retention rules; the VM proves actual enrollment,
wire authentication, startup reconciliation, and coexistence of all six lanes. The VM does not send
a live remote mutable command. Code ordering plus the existing one-binary crash/recovery gate place
the witness call between signed `STARTED` persistence and the existing provider/update effects; a
future dedicated injected service failpoint should strengthen this to a process-level before-effect
oracle.

Both guests still share one physical/admin failure domain. This is protocol evidence, not proof of
an independent production witness or exactly-once physical actuation.
