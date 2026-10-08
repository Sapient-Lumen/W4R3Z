# Launch quorum cold-start boundary

`launchquorum.py` is a joined gate over three earlier lanes:

1. `safestart.py`: negotiation + migration + SAM-shadow trace accepted for one intent.
2. `persistjoin.py`: reload + journal replay + checkpoint + scope/store debt accepted after restart.
3. `samprobe.py`: a local, explicit, streaming-first or no-router probe outcome.

The risky failure is accepting these independently and then starting sticky state anyway.  rev0034 therefore checks:

- component report replay or digest aliasing;
- safe-start intent mismatch;
- SAM endpoint drift;
- unavailable router used as live launch permission;
- garden/bridge mode without completed stream probe;
- crash-tail restart watch accidentally ignored.

This is still no-network design.  The no-router outcome is useful only when explicitly launching in offline-design mode.
