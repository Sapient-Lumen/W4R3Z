# Priority fairness slice

Revision: rev0028

Manifest task:

```txt
scheduler:priority-fairness-proof
```

Command:

```bash
node tools/priority_fairness_probe.mjs --json artifacts/validation/REV0044-PRIORITY-FAIRNESS-PROBE.json
```

## What it proves

The slice creates a deterministic `PriorityFairScheduler` and checks:

- a noisy background flow does not starve two same-priority peers;
- same-priority dispatch rotates through flows in the expected order;
- variable task cost is accounted through deficit events;
- critical work dispatches before user-visible/background work;
- user-visible work dispatches before remaining background work;
- background work resumes after higher-priority queues drain;
- per-flow queue limit rejection is observed;
- oversize task rejection is observed;
- rejected work does not mutate queue count or queue cost;
- all accepted tasks dispatch;
- final queue state is empty;
- required trace events are present.

## Why it belongs in release

This is a cheap Node-only proof. It does not launch Chromium. It gives future scheduler work a semantic guardrail before BrowserRT spends browser/worker budget.

## Non-claims

- No exact DRR or Kubernetes APF implementation.
- No production scheduler claim.
- No preemption/deadline proof.
- No browser Worker proof.
- No multi-threaded contention proof.
- No throughput or latency performance claim.
