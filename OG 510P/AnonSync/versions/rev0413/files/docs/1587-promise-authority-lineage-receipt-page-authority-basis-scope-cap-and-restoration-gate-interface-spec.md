# Promise authority lineage receipt page: authority basis, scope cap, and restoration gate interface spec

## Purpose

Later operators, reviewers, and downstream audiences need one durable receipt that preserves:

> why this actor had this promise authority, what exact cap applied, what stronger sentence stayed blocked, and what restoration gate still governed broader authority?

## Core decision

Every meaningful change in promise authority must emit one durable **Promise authority lineage receipt**.

## Fixed receipt order

1. **Receipt header**
2. **Authority basis section**
3. **Cap and signer section**
4. **Restoration gate section**
5. **Blocked stronger sentence section**
6. **Surviving sentence**

### 1) Receipt header

Include:

- receipt id
- subject id
- authority event id
- issuance review id
- timestamp
- acting reviewer or signer set
- current authority class
- current promise-class cap
- current scope-cap class

### 2) Authority basis section

Include:

- breach or recovery events considered
- credibility budget grade
- trust-repair status relied upon
- version, world, or support constraints relied upon
- whether the authority came from normal policy or manual override

### 3) Cap and signer section

Include:

- strongest allowed promise class
- strongest blocked promise class
- allowed scope
- blocked scope
- required co-sign rule
- allowed audiences
- blocked audiences

### 4) Restoration gate section

Include:

- probation status
- restoration trigger
- downgrade trigger
- expiry or review date
- who may restore broader authority

### 5) Blocked stronger sentence section

Include one explicit sentence that remains blocked and why.

### 6) Surviving sentence

The receipt must end with the strongest truthful sentence still allowed now.

Hard rules:

- the receipt may not imply `full trust` unless full promise authority is actually restored
- a manual override must remain visible forever in lineage
- restored narrower authority may not masquerade as restored original authority
