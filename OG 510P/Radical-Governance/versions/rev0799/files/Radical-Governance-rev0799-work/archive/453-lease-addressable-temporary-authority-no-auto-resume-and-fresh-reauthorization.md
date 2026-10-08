# 453 — Lease-addressable temporary authority, no-auto-resume, and fresh reauthorization

## One-line thesis

Temporary elevated authority for support, incident response, testing, or emergency accommodation should be issued as an explicit lease-addressable instance with bounded scope, expiry, and no automatic resume after interruption, restart, or session loss.

## Why this matters

Many governance failures hide in the exceptions that feel temporary. An operator enters a support mode, a privileged reviewer receives short-term access, an incident bridge unlocks a backstage control, or an emergency accommodation widens access to keep service moving. These grants are often described as temporary, but governed like ordinary standing permissions: the scope is fuzzy, the grant has no durable instance identity, expiry is informal, and session restart or network reconnection silently revives powers that should have required fresh justification.

That is a structural problem for consequential public AI. Temporary authority frequently touches the most sensitive moments: incident response, manual fallback, evidence review, administrative repair, high-friction citizen service, and privileged debugging. If these grants blur into normal permissions, the archive loses the ability to say which exact exceptional authority existed, why it existed, when it ended, and whether later actions still had a live basis. The archive should therefore treat temporary authority as a bounded lease instance with named scope, explicit end conditions, and a no-auto-resume default.

## Pattern pack

### 1. Issue temporary authority as a named lease instance

A temporary grant should not exist only as a flag on an account. It should have its own instance identity, such as a lease, ticket-bound grant, or emergency access record, with:

- grant identifier,
- actor,
- approver or route,
- reason,
- scope,
- start time,
- expiry or termination condition,
- and linked case, incident, or task reference.

That makes the exception reviewable as an event, not only as account metadata.

### 2. Keep scope and end conditions bounded and explicit

A lease should specify what it covers, for how long, and what ends it, such as:

- one service or one tenant,
- read-only versus write or admin actions,
- one case family or one incident,
- manual fallback only,
- time expiry,
- task completion,
- handoff completion,
- or explicit revocation.

Temporary authority that cannot state its boundary is already drifting toward permanence.

### 3. Separate the justification from the lease instance

The reason for a grant may persist longer than any one lease. For example, “incident investigation” may last days, but each privileged session or temporary route should still be a bounded instance. This keeps long-running operational pressure from turning one approval into indefinite background access.

### 4. Default to no automatic resume after interruption or restart

If a client restarts, connectivity breaks, a browser is reopened, a terminal detaches, or an admin console reconnects, the temporary grant should not quietly resume as though nothing happened. The default should be:

- fresh check of whether the lease is still live,
- fresh user reauthentication where appropriate,
- fresh step-up or approver confirmation where appropriate,
- or denial until a new lease instance is issued.

This prevents interruption from becoming a loophole for privilege persistence.

### 5. Keep temporary and durable authority visibly distinct

The user interface, logs, and later review records should make it obvious when an action occurred under a temporary lease rather than standing authority. The archive should preserve:

- lease identifier,
- temporary-versus-durable label,
- visible elevated-state cues,
- and the route by which the lease became active.

Invisible exception lanes are hard to govern well.

### 6. Bind temporary authority to the evidence lane that justified it

Where possible, a lease should point to the case packet, incident record, accessibility accommodation, or support request that justified it. This allows later review to assess not only that access existed, but whether the underlying reason still supported it.

### 7. Treat expiry, extension, and revival as governance events

The archive should record:

- normal expiry,
- manual revocation,
- extension,
- replacement by a fresh lease,
- and attempted reuse after expiry or interruption.

That makes the lifecycle of exceptional authority visible instead of collapsing into a single vague “temporary access was granted” story.

## Guardrails

- Do not describe elevated access as temporary if it silently survives interruption or restart.
- Do not let one long-running reason justify an unbounded series of invisible privileged actions.
- Do not merge temporary and durable permissions in logs or user-visible state.
- Do not rely on staff memory to explain which exceptional authority was active.
- Do not let lease extensions or revivals happen without reviewable state changes.

## Failure modes

- **temporary in name only**: the grant is called temporary but behaves like standing access.
- **silent resume**: reconnect or restart revives elevated authority without fresh checks.
- **reason sprawl**: one justification becomes a blanket permission for unrelated actions.
- **exception invisibility**: later reviewers cannot tell which acts happened under exceptional authority.
- **lease amnesia**: no one can reconstruct when the temporary grant ended, rolled over, or should have expired.

## Practical tests

A temporary-authority lease discipline passes when it can answer yes to all of the following:

1. Does every temporary elevated grant exist as a named lease-like instance rather than only as account state?
2. Are scope, expiry, and end conditions bounded and reviewable?
3. Does interruption, restart, or session loss require fresh confirmation rather than silent resume?
4. Can later reviewers distinguish actions taken under temporary versus durable authority?
5. Are expiry, extension, replacement, and attempted reuse preserved as governance events?

## Compression rule for the archive

If a temporary grant cannot answer **which exact instance was active, what ended it, and why it did not need fresh authority to return**, then it is not yet governed like a true **bounded lease**.
