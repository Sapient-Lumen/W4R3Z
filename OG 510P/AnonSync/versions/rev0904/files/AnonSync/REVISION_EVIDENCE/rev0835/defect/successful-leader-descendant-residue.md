# Defect: successful leader could strand descendants

## Before

A normal top-level leader exit could be reaped before the owner terminated the
remaining process group. Reap released the strongest local PID identity pin
while descendants could still be alive.

## Correction

Both owners observe with `waitid(..., WNOWAIT)`, kill the still-bound group, then
reap the exact leader. Linux subreaper oracles prove a deliberately lingering
descendant dies by `SIGKILL` even when the leader returned success.
