# 452 — Authority allowlists, integrity pins, and fail-closed external evidence imports

## One-line thesis

Consequential public AI should treat external evidence, supplier assurances, and authoritative-source materials as governed inputs with narrow authority allowlists, integrity or version pins where needed, and fail-closed blocking when authenticity or exact identity cannot be established.

## Why this matters

Public-sector AI systems increasingly depend on outside materials: supplier documentation, upstream datasets, linked regulations, retrieval corpora, third-party benchmarks, uploaded evidence, public-source content, and externally hosted guidance pages. Institutions often govern those materials too loosely. They know a source is “official enough,” but cannot say which host was trusted, which exact version or byte sequence was reviewed, whether the content later changed, whether a mirror was acceptable, or what should happen when authenticity cannot be confirmed.

That gap creates a quiet governance failure. A system can appear controlled while taking consequential input from a moving boundary. A broken or spoofed source can silently enter a decision path. A supplier claim can be cited as if institutionally adopted. A retrieval dependency can drift underneath an unchanged model version. The archive should therefore treat external evidence imports as governed boundaries: authority must be intentionally scoped, exact identity must be pinned when material, unresolved authenticity must trigger blocking or downgraded use, and drift in the imported basis must reopen review rather than disappearing into the background.

## Pattern pack

### 1. Narrowly scope which external authorities are allowed to matter

An institution should be able to name which external sources are allowed to influence a given consequential function, such as:

- statutes, regulations, or policy manuals from specific official hosts,
- approved supplier attestations or support bulletins,
- designated public registries,
- approved document repositories,
- or case-specific evidence channels.

An “official internet” posture is too wide to govern.

### 2. Separate authority recognition from exact identity

A source can be in an allowed class without the exact artifact being trusted yet. The archive should distinguish:

- authority family or host,
- exact document or object identity,
- exact version or date,
- byte-level integrity where material,
- and institutional adoption or review status.

This prevents the system from collapsing “came from somewhere official” into “this exact artifact is safe to rely on.”

### 3. Pin exact versions or integrity state when consequential claims depend on them

Some uses require more than a hostname or title. They require an exact reviewed artifact. Appropriate pins can include:

- version number,
- publication date,
- canonical URL,
- object identifier,
- content hash,
- or frozen local snapshot reference.

The archive should prefer exact pins where change in the imported artifact could change rights, obligations, thresholds, or routing.

### 4. Distinguish live import, monitored import, placeholder, and blocked states

External materials should not exist in one generic “available” state. Useful governance states include:

- reviewed and allowed for consequential use,
- authority-recognized but pending review,
- monitoring only and not decision-bearing,
- placeholder or stub awaiting authenticated fetch,
- blocked due to authenticity or integrity failure,
- or superseded and awaiting refresh.

This prevents incomplete import state from masquerading as approved reliance.

### 5. Fail closed when authenticity or integrity is required but unresolved

If a consequential path depends on a source whose authenticity, integrity, or exact identity cannot be established, the system should block or downgrade rather than quietly continue as if trust were intact. That may mean:

- abstaining,
- routing to human review,
- using a frozen last-approved snapshot,
- refusing the import,
- or restricting the system to advisory-only posture.

The archive should prefer an honest block to a graceful but unjustified guess.

### 6. Record what kind of trust each imported artifact actually carries

A governance record for an external artifact should say whether the artifact is:

- merely from an allowed host,
- cryptographically or operationally integrity-checked,
- reviewed for use in this context,
- adopted into institutional guidance,
- or only attached as raw outside evidence.

That distinction keeps supplier claims, public-source material, and institutionally adopted policy from flattening into one authority class.

### 7. Reopen governance when imported dependencies drift

If an external source changes materially, moves host, loses integrity status, becomes unavailable, or is replaced by a new version, that should reopen relevant review, documentation, or release gates. Imported dependency drift is still drift.

## Guardrails

- Do not confuse an allowed host with an approved exact artifact.
- Do not let unauthenticated or drifting external content silently stay decision-bearing.
- Do not flatten supplier assertions into institutional truth.
- Do not keep placeholders or stubs in a state that looks approved.
- Do not treat external retrieval dependencies as outside governance merely because they are upstream.

## Failure modes

- **host-only trust**: anything from a familiar domain is treated as good enough.
- **version blur**: the institution cannot say which exact artifact was reviewed or relied on.
- **silent dependency drift**: upstream content changes without re-triggering governance.
- **placeholder authority**: incomplete or unauthenticated imports behave like approved inputs.
- **borrowed certainty**: supplier or external claims are repeated as if institutionally verified.

## Practical tests

An external-evidence-import boundary passes when it can answer yes to all of the following:

1. Is the set of external authorities that may influence consequential use intentionally scoped?
2. Can the institution distinguish allowed source class from exact reviewed artifact identity?
3. Are exact versions or integrity pins used where imported change could materially affect outcomes?
4. Does unresolved authenticity or identity trigger blocking or downgrade rather than silent continuation?
5. Does drift in imported sources reopen review, release, or disclosure obligations?

## Compression rule for the archive

If the team cannot say **where an external input came from, which exact artifact was trusted, and whether use should have been blocked when that answer failed**, then the system still lacks a real **import boundary**.
