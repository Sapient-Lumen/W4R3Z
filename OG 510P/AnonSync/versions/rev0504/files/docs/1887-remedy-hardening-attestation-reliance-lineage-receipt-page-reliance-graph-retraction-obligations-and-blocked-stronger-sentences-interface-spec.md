# Remedy-hardening-attestation-reliance lineage receipt page — reliance graph, retraction obligations, and blocked stronger sentences

## Why this receipt exists

Once a ruling is final enough for some audience, later operators must not have to reconstruct from linked-device memory, permission guesses, pending or disconnected states, startup rollout, or fading logs who actually depended on it and what now must be undone.
They need one durable receipt that says who was allowed to rely, who actually did, which artifacts were derived, which consumers remain uncertain, and what revocation or revalidation duties apply if the source sentence changes.

## Receipt fields

- case identifier
- source finality receipt identifier
- current governing sentence
- allowed reliance audience class
- current dependency-governance class
- registered consumer set or cohort summary
- observed consumer set or cohort summary
- dependent artifact summary
- unknown-consumer risk grade
- revocation posture
- freeze-new-reliance flag
- active revocation or revalidation obligations
- superseding receipt identifier, if any
- whether source remains dependency-owning or historical only
- strongest blocked broad-reliance sentence
- strongest blocked all-dependents-current sentence
- next evidence that broadens dependency confidence
- next evidence that forces immediate retraction or reseal

## Required receipt sentences

The receipt must be able to say things like:

- `this ruling is allowed for the named automation cohort, but no downstream consumption has yet been observed`
- `this receipt was consumed by the registered named cohort only; broader dependency coverage remains blocked by unknown-consumer risk`
- `this source receipt was superseded and a revocation wave is active for the listed stale derivative artifacts`
- `new reliance is frozen, but historical visibility of the old receipt remains preserved during cleanup`
- `all registered dependents were revalidated or retracted, so the source receipt is now historical only`

## Dependency precedence rules

The receipt must make these rules explicit:

- a receipt allowed for reliance is not automatically dependency-governing until consumer coverage is established
- a superseding receipt does not silently refresh stale dependents; explicit revalidation or reseal is required
- historical preservation of a source receipt does not preserve its dependency authority
- unknown-consumer risk blocks broad `all dependents current` language even if known dependents are already cleaned up

## Blocking rules

The receipt must never let later operators silently say:

- `everyone updated automatically`
- `no one depended on the old ruling` without a real coverage basis
- `supersession completed` when revocation or revalidation obligations remain open
- `historical only` when stale outward artifacts still cite the source as current
- `all dependents are current` when registry or observation coverage remains incomplete

