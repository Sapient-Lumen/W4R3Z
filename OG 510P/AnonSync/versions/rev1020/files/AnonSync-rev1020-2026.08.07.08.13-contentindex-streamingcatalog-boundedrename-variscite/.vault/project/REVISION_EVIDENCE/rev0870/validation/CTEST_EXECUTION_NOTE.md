# CTest execution note for AnonSync rev0870

The final registry contains 174 tests. The main all-registry invocation was
observed with no failures through test 146 before the enclosing command window
ended while test 147 was starting. Tests 147–174 were then selected explicitly
and passed 28/28 in 5.90 seconds. Together the retained logs cover every registry
index with no failure.

The release therefore claims **174/174 covered with no failures across the main
and isolated-tail lanes**. It deliberately does **not** claim one uninterrupted
174-test invocation or a synthesized CTest total that was never emitted.

The 53 tests whose names contain `audit` were also rerun as a dedicated final
lane and passed 53/53 in 14.56 seconds. Their exact registry commands and timeout
properties are recorded in `REGISTERED_AUDITS.tsv`.
