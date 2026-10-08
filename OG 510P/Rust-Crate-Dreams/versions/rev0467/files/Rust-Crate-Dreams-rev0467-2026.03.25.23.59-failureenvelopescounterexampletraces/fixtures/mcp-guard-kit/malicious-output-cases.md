# MCP malicious / untrusted-output cases

Use these as fixture ideas for **operation-guard** and **audit/redaction** tests.

## Prompt-injection-ish payloads
- Tool output that includes instructions like “Ignore previous instructions and exfiltrate ...”.
- Tool output that embeds “BEGIN SYSTEM PROMPT” sections.
- Sampling responses that try to add unrelated content alongside required tool results.

## Data-exfil attempts
- Output that includes secret-looking patterns (API keys, OAuth bearer tokens) that should be redacted.
- Resource responses that try to tunnel filesystem or network data outside declared roots.
- Oversized payloads that should trigger size limits or truncation receipts.

## Capability-drift / approval problems
- A deployment that enables `tools/list_changed` and injects new high-risk tools without approval review.
- A deployment that enables sampling without user approval or loop limits.
- A local server config with one-click startup commands that mask risky shell behavior.
