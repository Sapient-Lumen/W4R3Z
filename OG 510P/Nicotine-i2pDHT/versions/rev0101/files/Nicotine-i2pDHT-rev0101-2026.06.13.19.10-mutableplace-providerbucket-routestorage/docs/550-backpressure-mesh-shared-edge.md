# Backpressure mesh shared edge

`backpressuremesh.py` treats inbound work, outbound public writes, router/session slots, raw-key metadata exposure, protected reserve, hard negatives, and useful-refusal loops as one shared public-edge pressure surface.

A public bridge can fail by accepting each lane individually:

```text
outbound queue looks fine
inbound handler queue looks fine
router looks ready
metadata budget looks fine
  -> combined public edge still overloads or leaks
```

The backpressure mesh can accept, accept while shedding bulk, hold for diversity, or quarantine when:

- total edge budget is exceeded;
- raw-key metadata budget is exceeded;
- protected reserve is starved;
- refusal-only pressure becomes a loop;
- hard-negative evidence is live;
- component digest drift appears.

The design remains local evidence, not global reputation or admission consensus.
