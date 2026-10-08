# 71 — CLI Client CAP Probing + Slice Measurement (v0.19)

Your key unknown: “how many subturn slices do I get?” and “how does truncation behave?”
We can’t observe internals, but we can measure externally and adapt.

## 1) CAP probing (per agent)
At session start or after upgrades, run a CAP probe:
- Does the model reliably emit CTRLJSON early?
- Does it follow line caps?
- Does it respect “no prose” constraints?
- Does it support tool-like behaviors (e.g., structured outputs) via its CLI?

Record CAP# fields:
- ctrl_first_reliability (0–1)
- json_valid_rate
- truncation_rate
- avg_bytes_per_slice
- latency_to_first_token

## 2) Slice proxies you can measure
Even if you don’t know “slice count,” you can measure:
- number of state reads performed by the client during a single “turn” (if visible in logs)
- number of times the client prints or refreshes output
- time_to_ctrl distribution
- output length distribution
- repair loop rate (how often you had to re-ask)

## 3) Measurement harness (router-level)
The router can:
- timestamp when a view is delivered to Ai
- timestamp when first CTRL token/line arrives
- record total bytes until output ends (or you cut it off)
- flag truncation heuristics (missing terminators)

Store rolling windows:
- last 10 slices and last 50 slices per agent

## 4) Adaptive policy hooks
If ctrl_first_reliability is low:
- enforce stricter prompt (68_) and shrink view
- enable JSON healing
If truncation is high:
- disable exploration
- switch to PatchOnly/Freeze
If latency spikes:
- reduce view and rely on HOT only

## 5) “Stop-after-CTRL” experiment
For each agent, test:
- request CTRLJSON first and then `DONE=yes`
Measure improvement in salvage rate vs loss of useful content.
Use this to tune the parser policy (keep draining vs stop reading).

## 6) Why this is enough
You don’t need the *true* slice count if your runtime adapts to the signals you can observe.
