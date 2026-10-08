# Deterministic temp-path race reproduction

`atomic_writer_race_same_harness.cpp` is the same 12-thread, 12-round, 8 MiB
publication harness in both lanes. Against the sealed rev0816 writer it produced
129 exceptions in 144 calls: writers collided on one payload-derived temporary
pathname, then either observed `EEXIST` or lost the pathname before rename. The
same harness linked to rev0817 completed 144/144 calls, with byte-exact final
content and no module temp residue.

The harness proves the local concurrent-publication defect and its correction.
It is not a crash/power-loss proof, distributed convergence proof, or a proof
against a principal that can arbitrarily mutate the trusted destination
directory.
