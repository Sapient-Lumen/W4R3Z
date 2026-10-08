# 406 — Federation-safe identity and delegated authority

## One-line thesis

Public digital identity should prove **what role a person can act in, for whom, for how long, and under what limits** without forcing total account fusion or unnecessary identity disclosure.

## Why this matters

Many institutions confuse identity with authority. But a great deal of public life depends on structured representation:

- a parent acting for a child,
- a lawyer acting for a client,
- a clerk acting for an office,
- a treasurer acting for an association,
- a contractor acting for an agency,
- a citizen acting under temporary power of attorney.

If systems only know how to authenticate a natural person, representation becomes a patchwork of unsafe password sharing, informal workarounds, and hidden administrative overrides. If systems over-correct by fusing every service into one giant profile, they create surveillance, brittleness, and excessive blast radius.

The archive should therefore separate **identity, credential, role, and mandate**.

## Design rule

Build for **federation with bounded delegation**:

- identity should be portable,
- roles should be credentialed,
- mandates should be explicit,
- disclosures should be minimal,
- revocation should be fast,
- logs should show who acted, in what capacity, under which authority.

## Pattern pack

### 1. Identity is not mandate

A public system should distinguish:

- who the holder is,
- what credential they possess,
- what organisation or person they represent,
- what powers are actually delegated,
- what expiry or revocation state applies.

Never infer broad authority merely because someone is authenticated.

### 2. Mandate credential, not blanket profile merge

Where a person acts for another person or organisation, issue a specific representation credential that can state:

- delegator,
- delegate,
- role,
- powers granted,
- jurisdiction or service scope,
- start and end date,
- conditions for suspension or revocation.

This keeps representation legible and avoids mixing every context into a single permanent account state.

### 3. Selective disclosure first

Service providers should only learn the minimum needed to decide the transaction:

- that the holder is authorised,
- in what role,
- for what action class,
- whether the mandate is still valid.

They should not receive unnecessary background data merely because the wallet or identity layer can technically carry it.

### 4. Delegation registry with privacy discipline

A public delegation layer may need a registry or resolvable status service, but it should reveal status without gratuitously exposing the full social graph of representation.

Default outputs should distinguish between:

- public facts required for third-party reliance,
- auditable facts available to supervisors,
- private supporting evidence available only through due process.

### 5. Revocation and expiry as first-class operations

Representation is dynamic. Systems must support:

- immediate revocation,
- narrow amendment,
- automatic expiry,
- emergency suspension,
- notice to affected services,
- durable logs of who relied on which mandate and when.

### 6. Multi-principal audit trail

Whenever a delegate acts, the receipt should show:

- acting natural person,
- represented person or entity,
- role or mandate used,
- operation performed,
- time,
- service,
- reviewer or exception path where relevant.

That allows later challenge without erasing either agency or accountability.

### 7. Anti-fusion rule

Do not let convenience features quietly collapse boundaries between:

- home and work identity,
- citizen and office-holder identity,
- personal and fiduciary authority,
- one jurisdiction and another.

Cross-context linking should require an explicit legal and operational reason.

## Guardrails

- Delegation must be revocable without deleting a person’s base identity.
- Organisations should not demand more identifying data than the transaction requires.
- Wallet ecosystems should not assume one issuer, one device, or one national stack forever.
- Representation for vulnerable users must preserve assisted access without normalising coercive control.
- Paper, phone, and in-person fallback paths still matter where digital exclusion would nullify the right to representation.

## Failure modes

- **authority by password**: staff or family share credentials informally because the system cannot model delegation.
- **identity sprawl**: every service keeps its own local shadow roles and exceptions.
- **forced fusion**: a single super-profile links all capacities and transactions.
- **stale mandates**: expired authority continues because revocation does not propagate.
- **opaque agency**: an action is logged, but outsiders cannot tell whether it was taken personally or representationally.

## Practical tests

A delegation-capable public identity stack passes when it can answer yes to all of the following:

1. Can a user prove authority to act without disclosing their whole identity dossier?
2. Can a mandate be limited by role, service, and time?
3. Can revocation propagate fast enough to matter operationally?
4. Can audit logs reconstruct who acted for whom and under what authority?
5. Can the same person maintain separate contexts without silent account fusion?

## Compression rule for the archive

Whenever identity reform becomes conceptually muddy, ask:

**Is this proving personhood, proving a claim, or proving delegated authority?**

Those are different governance tasks and should not be collapsed by default.
