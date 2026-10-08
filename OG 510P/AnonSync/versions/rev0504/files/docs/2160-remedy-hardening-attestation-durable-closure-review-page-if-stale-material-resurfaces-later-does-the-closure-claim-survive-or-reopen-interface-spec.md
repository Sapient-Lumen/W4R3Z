# Remedy-hardening-attestation durable-closure review page — if stale material resurfaces later, does the closure claim survive or reopen?

## Purpose

This review page asks the question point-in-time closure cannot answer by itself:

**if stale material resurfaces later, does the existing closure claim survive, narrow, or reopen?**

## Mandatory review prompts

The review must force explicit answers to at least:

1. Which rediscovery surfaces were considered before declaring closure durable?
2. Which latent survivor classes are still possible even after the closure verdict?
3. What exact rediscovery events would automatically reopen the claim?
4. What exact rediscovery events would only narrow the claim?
5. Which stronger durable-closure sentence would become dishonest if one survivor resurfaced tomorrow?

## Review buckets

### Rediscovery surface review

For each relevant surface, the page must show:

- surface name
- latent survivor class
- whether the surface is user-visible, hidden, or third-party-carried
- whether rediscovery from this surface is plausible, remote, or already observed
- whether rediscovery here would reopen, narrow, or merely annotate the closure verdict

### Invalidation review

For each invalidator class, the page must show:

- trigger event
- required reaction
- maximum honest lag before reaction
- blocked stronger sentence tied to that invalidator

### Residual-survivor durability review

The page must separately review at least:

- hidden archive residue
- disconnected filesystem residue
- placeholder-backed refetch posture
- expired-transfer UI versus local-byte divergence
- forwarded or reshared one-time copies
- local-share or sibling-path rediscovery

## Refusal rules

The review must refuse to bless a durable-closure claim if:

- rediscovery surfaces were not enumerated
- the invalidator set is missing
- the claim depends on UI disappearance rather than byte-retirement evidence
- a tolerated survivor class is present but the sentence still says `durably closed` without qualification
- the review cannot say what happens when a late survivor is found

## Output

The output must be one of:

- `durable closure proven within named invalidator budget`
- `closure proven; durable closure conditional`
- `durable closure blocked by latent survivors`
- `closure verdict would reopen on rediscovery`
