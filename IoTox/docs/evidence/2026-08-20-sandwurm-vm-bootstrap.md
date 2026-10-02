# Sandwurm VM bootstrap evidence — 2026-08-20

## Claim

Two distinct IoTox NixOS closures, `client` and `device`, booted under Sandwurm's stock Cloud
Hypervisor direct runner on the founding machine. Each run used 2 vCPUs, 2 GiB shared memory, a fresh
writable sparse runtime root, one receipt-only virtiofs workspace, and no virtual network device.

This is VM-substrate and role-profile evidence. It is not simultaneous-two-node, Tox connectivity,
latency, route, sync convergence, delegated-cgroup-controller, or destructive-GC evidence.

## Accepted observations

Both terminal live-chain receipts reported:

- `status=guest-evidence-observed` and no failure;
- prelaunch `ready`, live VMM `exited`, complete generic guest receipts;
- Cloud Hypervisor as the observed VM substrate;
- planned `network.class=none`, `network.mode=none`, and no `--net` argument.

Both IoTox receipts reported:

- IoTox `0.39.0 rev0039` from source identity
  `c7bcce7ec1b65a8d0410f0128f0af931aa47709e-dirty`;
- binary SHA-256 `e6f1bee157a50c4396221b57a6468c4e404515433ea117690c1830ced38e5da0`;
- the exact independent role (`client` or `device`), `virtualization=kvm`,
  `cgroup_type=cgroup2fs`, `network_class=none`, and `contains_secrets=false`.

The accepted historical run IDs were device `run.XXcdLMEe` and client `run.XXKDAHAD`. Their raw
ignored roots included sparse 16 GiB runtime images and were never repository artifacts. Later
source-linked simultaneous pair gates superseded these substrate-only disks, so the guarded
zero-retention cleaner removed them after the content-free findings below were frozen.

The same role profile can be reproduced and its content-free receipt tree checked with:

```sh
./tools/iotox-sandwurm-lab.sh up device
./tools/iotox-sandwurm-lab.sh up client
./tools/iotox-sandwurm-lab.sh verify device PROOF_ROOT
./tools/iotox-sandwurm-lab.sh verify client PROOF_ROOT
```

## Construction findings

The gate found and corrected three real integration problems:

1. Raw Nix `path:` traversal entered ignored FIFO runtime state; the lab now uses Git-backed source
   projection and a narrow product fileset.
2. GCC 13 rejected a copied structured binding under `-Werror`; the loop now binds by reference.
3. The prepared-host NAT declaration named Wi-Fi while the actual lowest-metric default route used
   USB Ethernet. `/etc/nixos/modules/sandwurm-cloud-hypervisor.nix` now declares
   `enp0s20f0u3c2`; the NixOS dry build and switch completed, and the prepared-host probe became ready.

The first live device attempt also proved the IoTox-specific service before revealing that the
generic Sandwurm receipt service was absent from the caller closure. The final profiles explicitly
include the Sandwurm package and both terminal attempts passed.
