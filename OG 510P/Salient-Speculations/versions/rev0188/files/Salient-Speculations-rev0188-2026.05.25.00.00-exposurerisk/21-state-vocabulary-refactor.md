
# State Vocabulary Refactor

rev0184 tightens the archive's vocabulary for proof and status states. The goal is to prevent the cube from treating every troubled proof object as generically “invalid.”

## The problem

The archive's managed-legibility dossiers now use many neighboring state terms:

- invalid;
- stale;
- expired;
- revoked;
- suspended;
- stayed;
- superseded;
- withdrawn;
- retired;
- archived;
- challenged;
- unverifiable;
- unsupported;
- non-reliance.

These terms name different governance problems. If they blur together, the archive loses predictive power.

## State families

### 1. Validity states

Validity states answer whether the artifact is allowed to support reliance.

- `valid`
- `expired`
- `revoked`
- `withdrawn`
- `suspended`
- `non-reliance`

### 2. Freshness states

Freshness states answer whether the artifact is current enough for a particular action.

- `live-current`
- `valid-cached`
- `stale-permitted`
- `stale-if-error`
- `revalidation-due`
- `stale-prohibited`

### 3. Dispute states

Dispute states answer whether the artifact is under challenge.

- `contested`
- `appeal-filed`
- `stay-active`
- `stay-denied`
- `correction-pending`
- `correction-final`

### 4. Version states

Version states answer whether another object now governs.

- `current-version`
- `superseded-prospective`
- `superseded-retroactive`
- `successor-known`
- `successor-gap`
- `archive-only`

### 5. Observability states

Observability states answer whether the verifier can inspect the source or proof path.

- `verifiable`
- `source-unavailable`
- `resolver-unavailable`
- `witness-nonresponse`
- `proof-path-broken`
- `redacted-beyond-verification`

## Editorial rule

When writing a new dossier, do not say “the record becomes invalid” unless invalidity is really the point. Specify whether the problem is expiry, stale cache, revocation, dispute, supersession, source unavailability, or non-reliance.

## Why this matters

Each state implies different infrastructure.

| State problem | Needed infrastructure |
|---|---|
| expired | renewal, grace, exception, revalidation |
| stale | cache-age disclosure, refresh SLA, stale-use policy |
| revoked | revocation propagation, past-reliance afterlife |
| stayed | interim reliance labels, appeal-routing, status subscriptions |
| superseded | successor maps, cutover notices, version scoping |
| archive-only | retention floors, evidentiary tombstones, historical renderers |
| unverifiable | fallback channels, witness requests, escalation paths |
| non-reliance | recipient notice, packet amendment, liability cutoff |

## Refactor instruction for future YAML

Future front matter may include:

```yaml
state_family:
  - freshness
  - dispute
  - version
state_terms:
  - valid-cached
  - stale-if-error
  - revalidation-due
freshness_clock:
  - source_observed_at
  - validated_at
  - relied_at
```

These are optional for legacy dossiers but recommended for new files in the managed-legibility family.
