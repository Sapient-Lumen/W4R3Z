# 82 — Credential loss, theft, and rapid reissuance (election-week playbook)

**Track:** B (Remote return / hard-mode research)



> **Deployment honesty:** Track B documents are **exploratory** and are **not deployment guidance**.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N-2**) and the [`Track B → Track A promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

Credential loss is not a corner case; it is expected at scale.

## Scenarios
1. Lost phone / lost hardware token
2. Device seized by an abuser/coercer
3. Device compromised (malware) / account takeover
4. Natural disaster / mass displacement

## Principles
- **Never strand the voter.** There must be a same-day recovery option.
- Recovery must avoid creating a transferable artifact that proves how/if someone voted.
- Recovery must be auditable without exposing PII.

## Election-week recovery tiers
### Tier 1 (fast): Backup authenticator
If the voter previously enrolled a backup authenticator:
- authenticate with backup
- revoke the lost authenticator
- re-mint eligibility tokens

### Tier 2 (safe): In-person rapid reissuance
- voter appears at authorized site
- identity proofing per published policy
- revoke old credential and issue new one
- mint fresh tokens

### Tier 3 (fail-safe): Paper-of-record override
If digital recovery cannot be completed safely:
- voter casts a paper ballot-of-record
- if remote ballots exist, the override precedence rules apply (see `31-time-ordering-and-censorship-resilience.md`).

## Abuse-safe recovery UI requirements
- Provide a prominent “**I’m not safe**” option.
- Do not display any status that confirms to a coercer that recovery succeeded.

## Evidence and logging
- Every revocation/reissuance creates a `CredentialLifecycleEvent` entry.
- Publish aggregate metrics (counts, not identities) for transparency.

Checklists: `artifacts/checklists/credential-recovery-checklist.md`.