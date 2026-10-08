# rev0010 PB-01 connection state-machine probe

The probe imports each archived source lane and uses fake sockets/selectors to exercise `NetworkThread` peer-init and post-init handlers without opening network sockets.

## Summary

| lane | U-168 P replace | U-168 D replace | U-176 P promote | U-176 D promote | U-176 F promote | PF secondary P promotes |
|---|---:|---:|---:|---:|---:|---:|
| github-tag-3.3.10 | True | True | True | True | True | True |
| github-branch-3.3.x | True | True | True | True | True | True |
| github-branch-master | True | True | True | True | True | True |

## Boundary and caveat

This is a handler/state-machine proof. It does not claim a polished end-to-end exploit, code execution, or file disclosure. It is enough to demonstrate that the election/replacement invariant is in code and reproducible across current/future lanes.

Raw JSONL evidence: `evidence/rev0010-pb01-connection-state-machine-probe.jsonl`.
