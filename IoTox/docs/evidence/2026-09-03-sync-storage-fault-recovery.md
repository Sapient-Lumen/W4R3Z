# Bounded synchronization storage-fault recovery

- Date: 2026-09-03
- Host: IoTox founding x86_64 machine
- Decision: ADR 0325
- Status: retained Sandwurm gate accepted

## Direct gate

The source-linked product at revision `10013e0b57b2af8e3abc47b6081d64d78ddde7c5`
was built into a 2-vCPU/2-GiB Sandwurm Cloud Hypervisor guest. Its IoTox binary SHA-256 was
`705d65f96e64c13d4d6079a787e28d12bb02a62467697e18bbe9ada84110d010`.
The guest had no external network and used one private loopback c-toxcore bootstrap.

The combined cell first passed the normal 512-file persistent capacity/lifecycle phase in 271,399
ms, with 61,488-ms catch-up, 52/73/53-ms repairs, 17,012/16,256/16,128-KiB Agent high-water RSS,
and zero restarts across 24 cycles. It then passed the one-node/all-node recovery ceremony in
82,398 ms.

## Storage-fault gate

The additive phase placed three fresh node roots on three separate 192-MiB loop-backed ext4
filesystems. It produced the following content-free observations:

| Fault | Accepted observation |
| --- | --- |
| live capacity exhaustion | real `ENOSPC` after 178,147,328 filler bytes; checkpoint mutation refused |
| full-filesystem process loss | Agent killed with exit `-9`; exact restart/convergence/repair succeeded after reclaiming the filler |
| read-only node root | startup exit 3; durable state digest unchanged; exact restart succeeded after read-write remount |
| large in-flight exchange | 33,554,432-byte successor killed with exit `-9` at signed `pending-workspace`; restart joined and converged |
| final integrity | three repairs; 19 files, one directory, 33,620,017 bytes; tree SHA-256 `444795f5a52d94a9301bececa30987cc907b650551f11b562f76ac6b4f360b93` |
| storage-fault phase | 144,433 ms |

The raw storage receipt SHA-256 was
`802384a8f71033f8c62b1e7e0622824b39eab6b49dac4da37b507ad79c750fe2`.
Both the generic VM-smoke verifier and the dedicated three-writer verifier independently accepted
the raw proof, and then accepted its compact export. The secret-free compact proof is
`.sandwurm/exports/three-writer/run.XXJNFmNN` (91,482 manifested bytes, 104 KiB allocated). Its
manifest SHA-256 is
`d47fc6347114b63edf9e563b8bc0ec772ca16de35955e9ecab7b848d1e9a8a6e`; the merged receipt
SHA-256 is `d017f317faa4b203f166dff5e8f4f9fdb5882a67d8f9b4e523d65ee2e663d880`.

## Evidence boundary

This was one same-computer, same-hypervisor, networkless guest. The fault volumes were real ext4
filesystems, but their backing files and VMM shared the founding machine. The harness used real
filesystem exhaustion, an exact read-only remount, and abrupt Agent `SIGKILL`; it did not cut power
to the VMM or host, emulate a controller that lies about flushes, inject bit corruption, exercise
every fsync/rename transition, or prove independent storage. The receipt therefore fixes
`storage_fault_power_cut=false`, `storage_fault_dishonest_storage_assessed=false`, and
`contains_secrets=false`. This is recovery construction evidence, not precious-data approval.
