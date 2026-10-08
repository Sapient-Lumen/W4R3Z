# Repeated-round probe ledger

`probeledger.py` treats bootstrap/liveness/absence observations as restart-sensitive protocol memory.

A round may contain:

- a bootstrap join report;
- live-probe digests;
- negative-space/absence pressure;
- egress budget pressure;
- source-family and path-family hints;
- a fast-window flag.

The tests pin these guesses:

- two diverse positive rounds can advance local sticky entrance state;
- replayed round digests are quarantined;
- repeated absence-only windows are not allowed to become durable state;
- positive evidence contradicting absence is hard pressure;
- one family repeatedly winning the fast window is capture pressure even if later replies make the total set look diverse.

The ledger is not consensus and not a timing model for I2P. It is a local guard against the easy bug: accepting the first convenient path repeatedly until it becomes the network.
