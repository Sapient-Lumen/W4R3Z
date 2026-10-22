# SlopOS rev0900 — reopen the office without promoting it

This is a linked, resumable Epoch Zero office—an Epoch-Zero construction. It is neither the old vault nor
the living project, and it grants no authority.

Run first:

```sh
python3 -B TOOLS/resume.py basic
```

Then follow `OFFICE/READ-ORDER.tsv`. Begin with `MISSION.md`, `EPOCH.md`,
`STATUS.md`, Review 23, Repository V24, Handoff Cell V12, the rev0900 evidence
boundaries, and `OFFICE/NEXT-CONSTRUCTION.md`.

The current construction is deliberately narrower than “safe path opening.” A
caller supplies one already-open `O_PATH` directory descriptor. The proposed
leaf open requires the fixed one-component etcd release name, the complete
`openat2` resolution mask, and Linux `OPENAT2_REGULAR` in the same syscall. A
post-open `fstat` is only a contract check; it is not allowed to be the file-type
barrier. The retained FIFO counterexample shows why.

This cloudtainer runs Linux 6.12.13. It supports the resolution mask but rejects
`OPENAT2_REGULAR`, so the production observation is
`HOST_OPENAT2_REGULAR_UNAVAILABLE`: zero candidate descriptors and zero
leaf bytes. Two descriptor-ready relation rows are synthetic premises for a
future supporting kernel, not host readiness. The exact archive is also absent,
but archive absence is downstream of the earlier capability stop.

Even on a supporting host, rooted regular-file acquisition would remain mutable
content. V11 complete capture into a private memfd, write/grow/shrink/seal
barrier, digest recomputation from sealed bytes, exact comparison, and passive
archive inspection remain mandatory. No archive member is extracted or
executed.

Do not turn a descriptor, path, mode bit, checksum, seal, synthetic fixture,
query observation, passing harness, or release-candidate UAPI into provenance,
operation, settlement, owner constitution, or living authority.

## Exact checkpoint identity

`SlopOS-rev0900-2026.07.28.09.21-rootfdopenat2-beneath-ancestorcounterproof-copperlintel`

Canonical transport: `SlopOS-rev0900-2026.07.28.09.21-rootfdopenat2-beneath-ancestorcounterproof-copperlintel.zip`.
