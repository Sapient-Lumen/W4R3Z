# Discovery / Service Check Runbook

## Purpose

Verify whether the local development or supervised-runtime environment exposes the expected transport-side services.

## Current scope

The default config checks loopback endpoints such as:
- I2P SAM bridge
- Tor SOCKS
- Tor ControlPort

## Run

```bash
python scripts/discovery_service_check.py --config discovery/service-targets.yaml
```

## Output

A JSON report is written to `artifacts/discovery-service-check.json`.

## Why this matters

The project promises a bundled product experience, but development and testing still need cheap, explicit reachability checks for the child-process endpoints the application depends on.
