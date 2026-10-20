# Sandwurm unattended one-writer synchronization evidence

Date: 2026-09-01
Decision: ADR 0276
Scenario: `sync-automation`

## Result

Two simultaneous source-linked IoTox guests completed three unattended one-writer directory
generations over both direct UDP and forced TCP. Policy was installed once. The publisher Agent and
replica Agent were then independently stopped and restarted. After setup, only source filesystem
mutation drove publication, pull, exact-HEAD acceptance, verified activation, and final projection.

| Carrier | Compact proof | Manifest SHA-256 | Binary SHA-256 | Result |
| --- | --- | --- | --- | --- |
| direct UDP | `pair.7vk1u4wn` | `b9558acf6bf474d75c00a69a8b472af46a5b2d744940309e3bc2f810f56b5639` | `4ee0f545a852ec11eb42363e141ae21d9ac20100ae241fd84d8314d6f3bbad88` | pass |
| forced TCP | `pair.s67dd_2e` | `c6d78641c943d8101eac333401557e258cdd1316b76bf8c459847f284c84c898` | `4ee0f545a852ec11eb42363e141ae21d9ac20100ae241fd84d8314d6f3bbad88` | pass |

Each compact proof occupies 167,936 allocated bytes. Neither contains guest disks or private key
state.

The post-change clean verification rebuilt the GCC debug tree with warnings as errors and completed
all 50 CTest targets with zero failures: 45 passed and the five host-shell tests that require a
delegated cgroup were correctly reported as skipped there. Its owned unit/integration target contains
711 checks. `nix flake check
--no-build`, the source-linked `.#iotox` package build, both pair-tool self-tests, shell syntax, and
compact replay of both accepted proofs also pass.

## Exact lifecycle

The publisher runs `sync-create automatic-notes SOURCE 1`, then uses the RecallRoot-bound
`sync-share ... read-only` ceremony. The replica independently chooses its destination, installs a
reviewed treepack-v1 namespace, grants the exact publisher principal `sync.publish`, and runs
`sync-follow ... verified 1`.

The proof joins these content hashes on both roles:

1. `a38b63d20844a25c35a872aab9988d2280dfc4c10d2fa626d252eedbc4a83945`
2. `c92740acd745679f5aa44b02b971765ccfd20a395fa3ab89615b5ed4deb5457b`
3. `1cdd300ae68361bfd6bc5b9793df532325d324c8509d11a488e6fde35939f2ca`

Generation 1 materializes before any restart. The publisher then reloads its signed `publish`
record after an Agent restart and publishes generation 2 from a source-only mutation; the replica
requires a higher publisher online epoch before accepting that result. The replica then reloads its
signed `follow activation=verified` record and exact source principal after its own Agent restart.
Generation 3 is another source-only mutation and must materialize without a new automation or
transfer command. Both receipts state `sync_automation_manual_transfer_commands=0`.

## Reproduce and verify

```bash
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-automation
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-automation

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-automation
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-automation
./tools/iotox-sandwurm-lab.sh export-pair PROOF_ROOT

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.7vk1u4wn \
  --route direct-udp --scenario sync-automation
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.s67dd_2e \
  --route forced-tcp --scenario sync-automation
```

## Boundary

This is a controlled two-guest, one-host result using reused private lab identities and a local
ephemeral bootstrap/relay fixture. It proves native UDP and forced-TCP behavior of the source-linked
tool, not physical-host diversity, abrupt VMM or host power loss, public relay availability,
cross-client behavior, hours-long operation, selective sync, filesystem watching, case-folding,
symlinks, richer metadata, or sole-copy readiness.
