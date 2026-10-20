# Signed route-generation witness evidence

Date: 2026-09-02  
Host: founding x86_64-linux machine; two NixOS guests  
Decision: ADR 0307

## Direct checks

```bash
nix develop -c cmake --build build/witness-clang --target iotox_tests -j4
nix develop -c ctest --test-dir build/witness-clang \
  --output-on-failure -R '^iotox\.unit-and-integration$'
```

The direct owned registry passed 776/776 checks. ADR 0307 adds four checks and extends the existing
CLI route-set check. The retained assertions cover:

- device-signed enrollment of the reviewed artifact generation/digest with no local mutation;
- initial exact checkpoint materialization and generation-one-to-two adoption;
- restoration of the complete valid generation-one artifact/checkpoint while the witness remains at
  generation two;
- refusal of a generation gap and of a same-domain backend outside tests;
- deterministic completion after the exact new local checkpoint is durable but the final external
  CAS and resolving query are interrupted; and
- generation advance through the signed ADR 0305 TCP client/server protocol.

## Two-guest gate

```bash
nix build .#checks.x86_64-linux.rollback-witness-service-vm \
  --no-link -L --max-jobs 1 --cores 4
```

The Agent guest creates an ordinary Tox identity, derives its exact protected-primary Tox key from
the retained runtime projection, and authors a two-member generation-one route set. It signs a
separate route-lane enrollment under the same domain/epoch as authority, application, and Ratox.
The witness guest accepts each lane exactly once before serving.

The source-linked Agent adopts generation one. After the existing authority and incarnation restore
tests, the guest authors generation two at a separate no-replace path, atomically places it at the
configured route path, and starts successfully. It saves the resulting exact pair, restores both
generation-one files, and requires the next start to fail with no requested runtime directory. The
generation-two pair is restored before the retained outage, service restart, wrong-key, and final
recovery cells.

## Evidence boundary

The result proves route transaction ordering and same-host state separation while the witness guest
remains current. It does not prove a separately administered witness, rollback-resistant witness
storage, physical-machine independence, filesystem behavior beyond the tested guests, route-policy
correctness, anonymity, reachability, or live route-set mutation. Route generations must be
contiguous after enrollment.

