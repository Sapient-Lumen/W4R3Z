# Sandwurm selected content-source loss evidence

Date: 2026-08-30  
Decision: ADR 0256  
Result: accepted for fail-closed recovery over direct UDP

## Claim

One subscriber and two independently authenticated complementary publishers ran as three IoTox
agents in two simultaneous Sandwurm/Cloud Hypervisor guests. During a real content-v2 pull, the host
stopped the exact secondary Agent only after it had received an object request. The in-flight job
failed closed. After that same publisher identity returned at a higher authenticated epoch, an
explicit fresh atomic multi-source pull converged, accepted the original signed HEAD last, and
activated the exact revision.

This qualifies explicit recovery, not transparent continuation. It is a one-machine/two-VM native-
UDP experiment, not a two-physical-host result.

## Retained proof

The secret-free compact proof is `.sandwurm/exports/pairs/pair.xujufman` and allocates 184,320 bytes.
Its two role receipts have SHA-256 digests:

```text
client  fad753de8b45b3dc485be14d56a8ab5190428d000150222877e8f4328616cdfa
device  4b19e92a72c593fc8a957cc1856fc1aa733317e84284b91abfa6dc29d13de26b
binary  ce106f26e008e947f5cdc5c11b832d8a8de88b5ca811e6b38d214d6a1eabb6bf
```

Strict verification of both the 2.4 GiB private proof and its compact export returned `status:
passed`, `scenario: sync-content-multi-source-loss`, and `observed_connection: udp`.

## Exact observations

```text
atomic multi-source pull observed roles       2
sources                                       2
availability requests/results                 4 / 4
primary/secondary physical CAS objects        5 / 2
first job ID                                  654376067927402308
replacement job ID                            10633691218072366106
secondary object requests before stop         1
verified objects retained from failed job     2
verified bytes retained from failed job       528
secondary authenticated epoch                 1 -> 2
secondary Agent restarts                      1
loss observed roles                           2
recovery observed roles                       2
staging clean roles                           2
HEAD fenced roles                             2
activation fenced roles                       2
```

The old and new job IDs differ. The first job retained only verified immutable prerequisites; both
role receipts prove no accepted HEAD, no activation, and clean transient staging after loss. The
fresh job used `sync-pull-multi`, so both authenticated sources were registered before the primary
HEAD could dispatch. Both sources then produced availability and object traffic before exact
reconstruction.

## Construction boundary discovered by the gate

The two publishers deliberately share an identical stable-device-signed revision for this
complementary-store fixture. Copying that root into the secondary's `published-heads` tree and cold
starting it failed, correctly, with a foreign-writer rollback error. The test did not weaken that
guard. It held the foreign root out of local publication state, restarted the same secondary
Tox/signing identity, completed a correlated local-control readiness check, and then reinjected the
already verified construction replica HEAD. The pair manifest binds
`multi_source_loss_constructed_replica_head_reinjected: true`.

Therefore this proof does not qualify a durable replica cold start. IoTox still needs a separate
authenticated replica/accepted-HEAD representation whose persistence semantics cannot be confused
with locally authored publication.

ADR 0257 subsequently constructed and qualified that distinct representation in compact proof
`pair.w_ws202c`. This section remains the exact historical boundary of `pair.xujufman`; see
`2026-08-30-sandwurm-sync-content-replica-restart.md` for the superseding cold-start claim.

## Reproduction

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-content-multi-source-loss
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.xujufman sync-content-multi-source-loss
```

The raw proof contains private guest disks and is intentionally disposable after compact export and
strict replay.

## Nonclaims

This evidence does not qualify transparent in-job source replacement, a subscriber daemon or guest
restart, durable replica cold start, multiple simultaneous content lanes, byte striping, forced TCP,
Tor or I2P, comparative speedup, two physical hosts, arbitrary timing, hostile filesystems/kernels,
power loss, fleet behavior, or unattended update safety.
