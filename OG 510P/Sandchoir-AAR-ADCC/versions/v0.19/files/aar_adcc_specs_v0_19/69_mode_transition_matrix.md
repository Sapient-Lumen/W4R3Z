# 69 — Mode Transition Matrix (v0.19)

Modes are “gear shifts.” You do not negotiate them mid-flight; MetaLLM/human selects based on signals.

This doc provides a deterministic *default* transition policy.

## 1) Modes (recap)
- Normal
- Gatekeeper (evidence-first)
- PatchOnly (no debate)
- Freeze (read-only WS except mandatory)
- Recovery (repair/compaction/checkpoint focus)

## 2) Signals (inputs)
Telemetry:
- ctrl_parse_success_rate
- time_to_ctrl (p90)
- truncation markers
- evidence density (E# per cursor window)
- patch churn (selected patch changes without checks)
- deadlock (no progress for N cycles)
- REQ pressure (inbound cap hits)

## 3) Default transitions
### To Gatekeeper
Trigger if:
- evidence density low AND patch churn high
- or consensus collapse detected (55_)
Exit when:
- evidence density stabilizes OR certified CE resolved

### To PatchOnly
Trigger if:
- drift detected (agents diverging goals)
- REQ spam/backchannel risk
- repeated merge conflicts
Exit when:
- one patch applied cleanly + cheap checks pass

### To Freeze
Trigger if:
- truncation spikes + parse failures
- WS near cap + compaction backlog
Exit when:
- compaction done + parse success recovers

### To Recovery
Trigger if:
- crash/restart
- checkpoint restore
- repeated I/O/broadcast issues
Exit when:
- view assembly stable + telemetry normal

## 4) Human override
Human can force any mode via Gearbox. Router logs mode change as mandatory delta.

## 5) MetaLLM policy
MetaLLM chooses one transition at a time.
Avoid oscillation: minimum dwell time (e.g., 1–2 rounds) unless catastrophic.
