# rev0326 pedagogy-forward execution refactor

## Change

The field handoff is now discovery-first. Its default micro-pilot packet is
`teacher-selected-concept`, not equality one-step. Equality remains an optional worked kit when a
local owner actually chooses that construct.

The owner plan now requires:

- a local problem statement and reason to act now;
- an explicit `FEASIBILITY_AND_USABILITY_ONLY` evaluation class;
- tool/model/version/configuration and prompt-card hash;
- learner notice or participation rule and aggregate learner voice;
- a local privacy threshold and protected local equity-review owner;
- an ordinary non-AI fallback.

The packet's transfer count is descriptive. It can trigger caution or stopping, but one small cycle
cannot establish efficacy.

## Hot path

```bash
make field-handoff-bundle OVERWRITE=1
```

Open `scratch/field-handoff/rev0326/FIELD-HANDOFF.md`, complete the discovery fields, and run no
learner-facing work until the local owner approves the plan.

## Boundary

This refactor changes preparation quality, not evidence state. No real pilot has run.
