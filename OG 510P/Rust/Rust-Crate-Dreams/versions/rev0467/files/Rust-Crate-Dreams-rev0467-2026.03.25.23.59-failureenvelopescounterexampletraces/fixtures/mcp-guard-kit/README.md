# mcp-guard-kit fixtures

This fixture pack exists to make **P-0071 MCP Guard Kit** concrete.

The goal is not to prove every MCP deployment.
The goal is to make three truths reviewable:

1. **transport exposure truth** — what local/remote surface is actually exposed,
2. **auth-boundary truth** — what audience, consent, and token rules are actually enforced,
3. **operation-guard truth** — what tools/resources/prompts/sampling paths are actually bounded.

## Core artifacts

- `transport-exposure.receipt.schema.json`
- `auth-boundary.receipt.schema.json`
- `operation-guard.contract.schema.json`
- `malicious-output-cases.md`

## Scenario families

- `localhost_http_origin_validation_missing/`
- `remote_proxy_token_passthrough_and_missing_audience_binding/`
- `tool_sampling_enabled_without_approval_or_loop_limits/`
