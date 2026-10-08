# Unresolved daemon-owner fencing hazard

This is a recorded negative result, not a passed safety claim.

The current owner-lock row prevents a second cooperating daemon from starting
while the first row appears live. It does not yet make the owner generation a
capability checked by every mutation boundary.

## Minimal stale-owner trace

1. Daemon A acquires the owner row using caller-supplied worker epoch `E` and
   pauses.
2. The row expires.
3. Daemon B overwrites the expired row. The schema requires only a positive
   epoch and acquisition does not require the replacement generation to exceed
   the stored generation.
4. B performs work.
5. A resumes. Its scheduler mutators carry workorder lease evidence but no
   daemon-owner ID/generation.
6. The mutator obtains SQLite's serialized writer slot, but its transaction
   does not read the owner row and therefore cannot reject A as stale.

`BEGIN IMMEDIATE` is useful because an owner check and mutation can be made
atomic with respect to other writers. It is not itself an owner check.

The machine-readable evidence and exact source locations are in
`audits/daemon-owner-fencing-hazard.json`.
