# Ratox terminal-policy rollback witness evidence

Date: 2026-09-02
Host: founding x86_64-linux machine; two NixOS guests
Decision: ADR 0308

## Direct checks

```bash
nix develop -c cmake --build build/witness-clang --target iotox_tests -j4
nix develop -c ctest --test-dir build/witness-clang \
  --output-on-failure -R '^iotox\.unit-and-integration$'
```

The direct owned registry passed 781/781 checks. ADR 0308 adds five checks covering:

- one deterministic semantic digest over the complete validated profile/binding tree;
- refusal to auto-accept a changed tree, explicit one-position commit, and complete old-checkpoint
  plus old-policy rollback refusal;
- recovery when the exact intent is durable but the begin CAS/reply is unavailable;
- recovery when external pending is durable but the final CAS/reply is unavailable;
- refusal of a same-domain backend outside tests; and
- verification/advance/query through the actual authenticated TCP witness protocol.

The complete host CTest surface then passed 55/55 entries in 66.69 seconds. The five delegated-
cgroup tests retained their expected construction-host skips; their separate kernel gates are not
reclassified by this policy work.

## Two-guest gate

```bash
nix build .#checks.x86_64-linux.rollback-witness-service-vm \
  --no-link -L --max-jobs 1 --cores 4
```

The Agent guest creates a real UID-1000 shell profile with deliberate host-authorized sudo
permission, binds it to one principal, and enrolls the complete tree at terminal-policy position
one. The separately running witness guest enrolls and serves the terminal lane beside authority,
application incarnation, Ratox incarnation, and route generation.

After a successful source-linked Agent start, the guest installs a no-escalation replacement. The
next start refuses with no requested runtime directory. The explicit
`witness-terminal-policy-commit` command advances position two over authenticated TCP, after which
the Agent starts successfully. Restoring the exact position-one sudo profile and exact position-one
signed local checkpoint is then refused before RuntimeTree while the external head remains at two.
Exact current restoration and the retained service outage/restart/wrong-key cells still pass.

## Evidence boundary

This proves the policy digest, explicit review transaction, recovery joins, pre-runtime Agent
integration, and same-host process/disk separation. The guests share one physical/admin failure
domain. The gate does not prove independently administered or rollback-resistant witness storage,
sudo configuration correctness, a native deployment kernel, or safety against a privileged live
host attacker.
