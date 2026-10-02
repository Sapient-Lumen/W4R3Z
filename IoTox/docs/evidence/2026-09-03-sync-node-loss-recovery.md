# Tree-v2 node-loss recovery rehearsal

- Date: 2026-09-03
- Host: IoTox founding x86_64 machine
- Decision: ADR 0323
- Status: direct source-linked and retained Sandwurm gates accepted

## Direct gate

The final direct harness used the source-linked IoTox derivation at
`/nix/store/ihybql6vd5hq51bpm2jwlngdqkr9r335-iotox-source-linked-0.46.0-rev0046/bin/iotox`
and the pinned local c-toxcore bootstrap fixture. The binary SHA-256 was
`705d65f96e64c13d4d6079a787e28d12bb02a62467697e18bbe9ada84110d010`.

```sh
./tools/run-sync-recovery-rehearsal.py \
  --iotox /nix/store/ihybql6vd5hq51bpm2jwlngdqkr9r335-iotox-source-linked-0.46.0-rev0046/bin/iotox \
  --bootstrap /nix/store/jgy3lf9w65yllk5zyx5q1gxbajjhw125-iotox-tox-bootstrap-33445-0.2.23/bin/DHT_bootstrap \
  --three-writer-helper tools/run-sync-three-writer.py \
  --state-root /var/tmp/iotox-recovery-direct.XXmamfDo/state \
  --evidence /var/tmp/iotox-recovery-direct.XXmamfDo/recovery.json
```

The gate completed in 81,771 ms. It matched 33 files in one directory and 131,099 bytes across four
strict verifier calls. The selected tree digest was
`c19b5020ecf46691f9d2032b48bbca7d456cb96b16b36e386defc97077f462b4`. Two survivors each
recorded one capability revocation, writer cutoff, peer removal, and post-cutoff checkpoint. One
empty replacement converged to three branches; after all live roots were erased, three further
replacement identities also converged to three branches. Six node instances passed repair.

The 1,975-byte content-free receipt SHA-256 was
`5ae7a50e261c4498802d54f67f4f642feb01415c7bf1f511751ae236a1df85d1`. It contains hashes rather
than principal values and explicitly records `backup-independence=not-assessed`,
`restore-provenance=not-assessed`, and `contains-secrets=false`.

## Retained Sandwurm gate

A clean 2-vCPU/2-GiB Sandwurm Cloud Hypervisor guest ran source revision
`2d5e869f72e94e3591c6b5b1ffe1aa1bbc5f6b69` and the same byte-identical source-linked binary. It
first completed the persistent three-writer cell: 512 16-KiB files caught up in 46,326 ms, repair
took 46/43/44 ms, Agent high-water RSS was 17,096/16,896/16,256 KiB, and allocated state grew
21,512,192/19,857,408/19,853,312 bytes. All 24 persistent shadow cycles completed in 129,671 ms with
zero watchdog restarts, followed by conflict resolution, maintenance, quarantine/restore, and writer
cutoff.

The additive recovery phase then completed in 97,238 ms. The one-node replacement and all three
fresh post-loss replacements each reached `[3,3,3]` branch frontiers; six replacement views passed
repair and four external-tree comparisons matched the exact 33-file/131,099-byte selected tree.
Obsolete and replacement principal hashes were disjoint. The merged 4,255-byte receipt SHA-256 is
`ae50fdfa5c3514eb1197349dad850f0430f44ae5850535bcf8cdbb6d499e1f6b`.

The raw proof root was `.sandwurm/lab/three-writer/run.XXJGHoNd` (26 GiB apparent, 2.4 GiB
allocated). The independently reverified secret-free compact proof is
`.sandwurm/exports/three-writer/run.XXJGHoNd` (90,435 manifested bytes); its manifest SHA-256 is
`81213534d4754ad8cd8bebe04838b39d88205e87e092271d6c3b9d8191b72439`. Both the VM-smoke and
three-writer verifiers passed against the compact copy.

## Rejected diagnostic gates

Earlier synthetic runs were retained only long enough to identify and correct ceremony defects:

- completed publisher replay cache entries prevented additive membership even after cutoff,
  revocation, friendship removal, and survivor restart;
- a fresh writer rejected live branch history that still observed the retired writer;
- creating the post-cutoff graph floor before peers exchanged the cutoff checkpoint caused a valid
  1-to-3 generation-skip refusal; and
- polling authenticated history at 10 Hz perturbed the event loop and was replaced by a fixed-header
  liveness observation; and
- a clean post-authority-fix VM reached the recovery mesh but tried to add another writer while an
  earlier edge had an active pull. The Agent correctly refused the concurrent policy mutation; the
  final harness creates the six-edge mesh while empty, then installs the ordinary restore tree.

No rejected run produced an accepted receipt.

## Evidence boundary

The backup and restored view were outside every node root but remained on one host and one storage/
administration domain. This gate proves orchestration, strict identity replacement, ordered cutoff/
checkpoint semantics, ordinary-tree reseeding, convergence, and verification. It does not prove an
independent backup, restore provenance, physical loss, power-cut durability, correct generation
selection, or precious-data readiness.
