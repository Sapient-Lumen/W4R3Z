# Defect: duplicate lifecycle choreography obscured the invariant owner

Rev0835 implemented near-parallel leader observation, group termination, exact
reap, `ECHILD` handling, and cleanup in `inherited_test_process.cpp` and
`self_exec_test_process.cpp`. The duplication was not only maintenance cost: it
allowed the two capture paths to retain numeric group authority in different
ways after the exact leader had been reaped.

Rev0836 moves all nine direct `kill`/`waitid`/`waitpid` call sites into one
compiled test-only translation unit. The public header is a 57-line ownership
contract rather than inline choreography. Both wrappers contain zero direct
lifecycle syscall sites and depend privately on one dependency-free leaf
library. A configure-time dependency guard and source audit prevent the owner
from entering the production graph or being reabsorbed into either wrapper.
