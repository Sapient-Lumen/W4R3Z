# Service continuity as a joined boundary

A garden service decision is no longer one report. It is a local join across typed reports:

```text
catalog wire exposure
service announcement
inbound ingress gate
load/ticket grant
service receipt
service use gate
handoff/egress
optional probe / relay / veiled receipt evidence
withdrawal negative evidence
```

`servicecontinuity.py` normalizes those reports into `ServiceContinuitySignal` records and then applies `ServiceContinuityPolicy` before accepting a side-effect boundary.

Risk cases now tested:

```text
active withdrawal blocks otherwise valid service use
catalog drift between wire/ticket/use signals blocks continuity
scope drift blocks continuity
request drift blocks continuity
replayed branch reports block continuity
duplicate branch reports block continuity
quarantined branch reports poison the joined window
missing required branches hold instead of accepting convenience
refusal-only or watch-only windows do not become healthy service
```

This is not consensus. It is local refusal to let a convenient pass in one lane authorize a different lane.
