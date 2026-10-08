# Class upgrade review page: cutover, successor epoch, and peer continuity interface spec

The archive already had successor-cutover and stale-capability rotation doctrine.
What it still lacked was one ordinary page for the question:

> when the operator says `upgrade this subject`, is the product actually changing one thing in place or asking for a cutover to a successor subject class with new peer and capability epochs?

Current Resilio docs still make this seam concrete.
They still say Standard folders cannot be upgraded in place; the operator must disconnect/remove them on all peers and add them back as Advanced.
That is not a toggle.
That is a cutover.

## Page promise

The Class upgrade review page should make six answers adjacent:

1. current class and target class
2. whether same-subject continuity is honest
3. peer / artifact retirement obligations
4. byte continuity plan
5. cutover order and proof
6. strongest honest next action

The page exists so `upgrade` stops impersonating a harmless settings change.

## Fixed page order

Every class-upgrade review page should render the same sections in the same order:

1. **Current subject and target class**
2. **Continuity verdict**
3. **Peer and artifact epoch plan**
4. **Byte and path continuity**
5. **Cutover ladder**
6. **Receipt promise**

### 1) Current subject and target class

This section should show:

- current class and target class
- why the operator is asking for the change
- which capabilities are missing in the current class
- which stronger semantics are expected in the target class
- whether the source bytes remain the same local corpus

The operator should be able to answer: **what do I want that the current class does not honestly provide?**

### 2) Continuity verdict

This section should show one explicit verdict:

- `in-place class change honest`
- `successor cutover required`
- `same bytes, new governance epoch`
- `cannot preserve continuity honestly yet`

For class cliffs like current Resilio's Standard→Advanced case, the page should say plainly that this is a **successor cutover** even if local bytes may be reused.

The operator should be able to answer: **am I still operating the same governed subject after this?**

### 3) Peer and artifact epoch plan

This section should show:

- peers that must disconnect or be retired from the old epoch
- capability artifacts that must be revoked, allowed to expire, or simply become stale
- which remembered identities, approvals, or grouped peer views will only exist after the new epoch is established
- whether any remote peer will need new claim material

The operator should be able to answer: **what old authority world must end before the new one can be trusted?**

### 4) Byte and path continuity

This section should show:

- whether local bytes are being reused in place
- whether remote peers should reconnect to already-existing bytes or stage new targets
- whether path continuity is safe, risky, or impossible to prove
- whether archives / histories / peer expectations stay attached or restart under the new epoch

The operator should be able to answer: **which continuity is real here: bytes, governance, paths, or none of them?**

### 5) Cutover ladder

This section should show the least-confusing ordered plan, for example:

1. freeze issuance from the old class
2. export or inspect the old peer/artifact inventory
3. disconnect or retire the old class on required peers
4. create the new class
5. reconnect or re-issue new artifacts
6. verify new peer epoch and expected grouping
7. mark the old epoch retired

The operator should be able to answer: **what exact order prevents mixed-epoch ambiguity?**

### 6) Receipt promise

A class-upgrade receipt should preserve:

- current class and target class
- continuity verdict
- retired peer/artifact set
- byte/path continuity verdict
- cutover steps executed or still required
- resulting successor subject ID or explicit refusal

The operator should be able to answer: **what did we call this cutover, and what old epoch remains or is retired?**

## What this page must never imply

The page must never imply that:

- class upgrade is necessarily in-place
- reusing bytes proves governance continuity
- old links, keys, or grants automatically became stronger because the local folder stayed the same
- disconnecting old peers is optional when mixed-epoch ambiguity remains
- a new richer peer view means the old epoch was secretly equivalent all along

## Result

This page is how AnonSync borrows Resilio's honesty that some upgrades are really remove/re-add cutovers, while refusing the weaker product shape that hides that truth in a short how-to article.
