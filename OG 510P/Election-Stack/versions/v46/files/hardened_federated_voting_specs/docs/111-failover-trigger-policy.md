# Failover trigger policy

**Track:** A (Deployable core)


## Why pre-commit
Improvised decisions during an attack are easy to delegitimize.

## Policy object
Publish a signed FailoverTriggerPolicy inside the EPB:
- intake freeze triggers
- mirror rotation triggers
- evidence portal fallback triggers
- “paper-of-record” escalation triggers

## Example triggers
- parity failure > X minutes
- inclusion proof issuance failure rate > Y%
- witness quorum unavailable > Z minutes

## Normative requirements
- **MUST** publish the policy before polls open.
- **MUST** log policy changes as EPB updates (with ceremony).
- **MUST** provide public, signed statements when triggers activate.