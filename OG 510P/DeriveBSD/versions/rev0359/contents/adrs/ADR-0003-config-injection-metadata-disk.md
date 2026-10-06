# ADR-0003: Baseline config injection via metadata disk

- Status: proposed
- Date: 2026-02-23

## Decision
Use a read-only metadata disk as the baseline config injection channel with a Derive-native schema (`meta.json`, `config.json`), plus optional adapters for cloud-init NoCloud.

## Consequences
- every backend must attach an extra read-only disk
- guests need a minimal agent/init path
