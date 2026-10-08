# Wake from amnesia — rev0014

Current revision: `rev0014 proofprobe-gardensentinel-sweepgrid`.

## What happened

We joined separate risk surfaces:

- provider proof handshakes are now evaluated as part of private-ish provider probe sessions;
- garden/sentinel autocuration now ingests provider proof reports and witness mesh reports;
- adversarial pressure is now swept over capture, false-provider, stale-head, and latency dimensions;
- family diversity is refactored into a shared helper;
- historical duplicate docs/ADRs/module names are mapped with `HISTORICAL_SUPERSESSION.json`.

## Read first

1. `docs/109-rev0014-proofprobe-gardensentinel-sweepgrid.md`
2. `docs/110-proofprobe-private-provider-session.md`
3. `docs/111-garden-sentinel-autocuration.md`
4. `docs/112-sweepgrid-adversarial-pressure.md`
5. `docs/113-familydiversity-and-supersession-refactor.md`
6. `docs/114-python-surface-rev0014.md`
7. `docs/115-research-notes-2026-06-01.md`

## Strong sentence

```text
Claims are cheap; coupled local pressure is expensive enough to be useful.
```

## Next likely revision

`rev0015 witnesscache-routingpressure-samshadow`

Suggested focus:

- witness cache aging and local evidence decay;
- path-family routing pressure with more explicit lookup transcript objects;
- provider proof/session transcript fixtures suitable for eventual SAM transport;
- stronger garden overload/refusal scheduling;
- deeper refactor of duplicate provider poison modules after tests pin behavior.
