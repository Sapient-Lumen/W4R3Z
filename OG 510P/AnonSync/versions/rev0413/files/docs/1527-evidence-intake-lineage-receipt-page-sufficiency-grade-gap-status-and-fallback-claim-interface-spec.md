# Evidence intake lineage receipt page: sufficiency grade, gap status, and fallback claim interface spec

## Purpose

Later operators need one durable receipt that answers:

> what packet was reviewed, what grade it actually earned, which gaps remain open or expired, and what exact fallback claim survives if no one does more work?

## Receipt structure

The receipt must contain seven sections:

1. **Receipt header**
2. **Packet identity block**
3. **Target-question block**
4. **Sufficiency block**
5. **Open-gap block**
6. **Supplement-state block**
7. **Claim-ceiling block**

### 1) Receipt header

Show:

- intake receipt id
- source intake id
- source packet id
- issuance time
- issuing reviewer
- review finality class

Supported `review_finality_class` values:

- `provisional`
- `stable-until-freshness-expiry`
- `stable-until-supplement-response`
- `stable-until-superseded`
- `closed-insufficient`

### 2) Packet identity block

Required rows:

- packet form reviewed
- source world reviewed
- artifact classes reviewed
- redaction class reviewed
- validation posture

### 3) Target-question block

Required rows:

- named question answered
- questions explicitly not answered
- scope boundaries
- version or world assumptions

### 4) Sufficiency block

Required rows:

- final sufficiency grade
- window-fitness verdict
- fit verdict
- whether action is allowed, bounded, or blocked

### 5) Open-gap block

Required rows:

- still-open gaps
- expired gaps
- gaps intentionally tolerated
- strongest sentence each gap still blocks

### 6) Supplement-state block

Required rows:

- supplements requested
- supplements received
- supplements declined or unavailable
- current best next ask, if any
- timeout posture

### 7) Claim-ceiling block

Required rows:

- strongest safe sentence now
- strongest blocked sentence now
- weaker fallback sentence if freshness expires
- explicit overclaim to avoid

Hard rule:

The receipt must preserve the fallback sentence even when the current packet looks good.
Future operators inherit packets after freshness decays.

## Receipt footer sentence

Form:

> Packet **[packet id]** is recorded as **[final sufficiency grade]** for **[named question]**. It is fit as **[fit verdict]** with window posture **[window fitness]**. Open or expired gaps are **[gap list]**. The strongest safe sentence is **[safe sentence]**. The explicit fallback sentence if nothing else happens is **[fallback sentence]**. The overclaim to avoid is **[forbidden sentence]**.
