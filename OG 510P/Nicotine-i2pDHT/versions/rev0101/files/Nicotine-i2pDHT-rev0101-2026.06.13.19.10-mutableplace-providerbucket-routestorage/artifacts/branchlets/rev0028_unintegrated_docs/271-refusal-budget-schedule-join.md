# Refusal budget schedule join

A useful refusal should help future scheduling, not launder a failure into success.

`refusalbudget.py` joins refusal-loop evidence with scheduling reports from `schedjoin.py` and `gardenscheduler.py` shaped surfaces. It keeps the evidence local:

```text
accept balanced budget
watch refusal-heavy service
watch under-diverse service
quarantine refusal laundering
quarantine protected starvation
quarantine no-service-with-refusals
```

The report is not global reputation and not payment. It is a local guardrail: do not schedule the next window as if repeated overload/refusal were healthy service.
