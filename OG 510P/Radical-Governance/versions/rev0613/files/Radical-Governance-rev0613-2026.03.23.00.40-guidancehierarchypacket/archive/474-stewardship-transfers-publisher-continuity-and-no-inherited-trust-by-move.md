# 474 — Stewardship transfers, publisher continuity, and no inherited trust by move

## One-line thesis

When a third-party model, dataset, API, repository, document host, or supplier changes steward, publisher, domain, or ownership, prior trust and approval should not silently carry forward; stewardship transfer should trigger continuity proof or trust reset.

## Why this matters

The archive already knows how to pin external evidence, narrow allowed hosts, and track supplier dependencies. What it still lacked was a direct rule for what happens when the *same seeming thing* moves under different hands.

A model card moves to a new host. A vendor is acquired. A repository transfers to a successor maintainer. A model marketplace mirror becomes the new canonical download path. An API remains reachable at the same integration point but now sits behind different contract terms, different incident practices, or different content provenance promises. In each case, sameness of artifact name or endpoint can hide a change in institutional stewardship.

That change matters because trust is not only about bytes or outputs. It is also about notification duties, change management posture, provenance practices, contractual recourse, outage handling, fallback rights, and whether the steward can still explain or remediate what the archive depends on.

## Pattern pack

### 1. Separate artifact continuity from steward continuity

A system should distinguish:

- same artifact, same steward,
- same artifact, new steward,
- new artifact under same steward,
- and new artifact under new steward.

One stable URL, identifier, or package name is not enough to prove continuity of trust.

### 2. Classify stewardship-transfer events

Relevant events include:

- domain or host move,
- repository transfer,
- vendor acquisition,
- contract novation,
- mirror promotion,
- maintainer handoff,
- or service migration behind a stable API surface.

Different transfer types may require different levels of review, but none should be invisible.

### 3. Require continuity proof or trust reset

After stewardship transfer, the archive should require one of two explicit moves:

- **continuity proof**: evidence that the new steward preserves required security, provenance, disclosure, incident, and support obligations,
- or **trust reset**: reopen approval, risk review, allowlist status, and fallback planning.

Ambient inheritance is too weak.

### 4. Reopen linked governance surfaces

A stewardship transfer can require refresh of:

- supplier registers,
- public disclosures,
- incident contacts,
- fallback and exit plans,
- approved host or provider lists,
- import pins and integrity expectations,
- and contractual or procurement assumptions.

A quiet move can break more than the download path.

### 5. Preserve old-to-new lineage on the evidence surface

If a public artifact or dependency moved, preserve:

- prior steward,
- new steward,
- effective time,
- basis for trust continuation,
- and any temporary downgrade or quarantine status.

People should not have to discover stewardship change through rumor.

### 6. Treat unchanged bytes as insufficient by themselves

Even when a model weight, file hash, or endpoint behavior appears unchanged, the archive should still ask whether the new steward changed:

- monitoring,
- support,
- incident reporting,
- retention,
- access controls,
- or future update authority.

Byte-level sameness does not fully answer governance continuity.

### 7. Test fallback and exit at transfer time

If governance relied on the prior steward, transfer is the right time to test:

- alternate provider readiness,
- export or escrow path,
- manual fallback,
- and decommission triggers if continuity proof fails.

## Guardrails

- Do not let a stable name or URL silently prove stable stewardship.
- Do not inherit prior approval without checking what obligations changed.
- Do not treat mirror promotion or repository transfer as a cosmetic event.
- Do not keep old incident contacts, contracts, or disclosures live after steward change.
- Do not let unchanged outputs hide changed authority, changed liability, or changed support posture.

## Failure modes

- **trust by address**: the same endpoint or name is mistaken for the same steward.
- **silent successor inheritance**: a new owner inherits old approval without review.
- **byte-only continuity theater**: unchanged artifacts hide changed obligations and changed future control.
- **stale dependency posture**: registers, disclosures, and fallback plans still point to the old steward.
- **transfer surprise**: users and operators learn about stewardship change only during outage, dispute, or incident.

## Practical tests

A stewardship-aware dependency model passes when it can answer yes to all of the following:

1. Can the archive detect and classify steward, host, or ownership transfer events?
2. After transfer, does it require either continuity proof or an explicit trust reset?
3. Are linked governance surfaces refreshed when stewardship changes?
4. Can users and operators see old-to-new lineage for the dependency or public artifact?
5. Are fallback and exit routes tested when continuity is uncertain?

## Compression rule for the archive

If a consequential dependency or public artifact can move to a new steward, publisher, or host without forcing either **continuity proof** or **trust reset**, then the archive is still letting **location sameness impersonate governance continuity**.
