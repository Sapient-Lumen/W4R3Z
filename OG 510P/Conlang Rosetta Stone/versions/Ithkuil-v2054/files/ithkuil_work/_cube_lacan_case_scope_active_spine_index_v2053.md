# _cube_lacan_case_scope_active_spine_index_v2053

**Date:** 2026-05-30  
**Project:** Ithkuil translation of the love text — Lacan local cube  
**Purpose:** host Case-Scope audit and compact active-spine refactor after v2053

---

## 1. Active line after v2053

```text
rkwalû li sëi ; evvralácboa swou li hlušh-otiröehëi hlu’u «objet petit a» hü swië ; alo extřudêi lo že
```

v2053 is a no-surface-change pass. Its cube effect is to mark host Case-Scope as audited and to create a compact active-spine ledger.

---

## 2. Active-spine ledger

| Segment | Active form | Status | Main burden |
|---|---:|---|---|
| opening love predicate | `rkwalû` | active from v2047 | RKW₁ romantic love; ASR/ITU validation |
| opening speaker | `li` | active from v2029 / restored v2043 | 1m/AFF experiencer |
| opening addressee | `sëi` | active from v2036 / restored v2043 | 2m/STM stimulus |
| frame head | `evvralácboa` | active from v2046 stress repair | VVR₂ affective fixation; RSN/1; SIT frame |
| “in you” anchor | `swou` | active from v2050 | 2m-ABSTRACT/ITP interpretive field |
| middle speaker | `li` | active from v2029 / restored v2043 | 1m/AFF experiencer |
| host prehead | `hlušh-` | active from v2024 | salience/prominence prehead |
| host nucleus | `otiröehëi` | active from v2048 + v2053 | T₀-OBJ; AGG perspective; SUR; CCN; STM |
| carrier/name | `hlu’u «objet petit a» hü` | active from v2045 + v2052 | RLT carrier apposition, adjacent to host |
| comparison standard | `swië` | active from v2051 + v2052 | 2m-ABSTRACT/CMP, now after host+name |
| contrastive hinge | `alo` | active from v2035 / restored v2043 | CTR/1 nevertheless/but/yet |
| final predicate | `extřudêi` | active from v2049 | XTŘ₂ maim; DYN; PRX; ASR/USP |
| final agent | `lo` | active from v2031 / restored v2043 | 1m/ERG agent |
| final patient | `že` | active from v2031 / restored v2043 | detrimental 2m/ABS patient |

---

## 3. New cube axis: `host-case-scope-after-name-insertion`

Active value:

```text
host-case-scope-after-name-insertion = CCN / NATURAL / keep
```

Rationale:

```text
The host’s STM case must remain associated with the framed VVR₂ predicate.
The RLT carrier attaches by appositive adjacency.
The CMP standard attaches via SUR + CMP, not by turning the host into a broad case-scope head.
```

---

## 4. Candidate Case-Scope outcomes

| Candidate | Hypothetical surface | Status | Reason |
|---|---:|---|---|
| CCN / NATURAL | `hlušh-otiröehëi` | active | host remains STM participant of VVR₂ |
| CCA / ANTECEDENT | `hlušh-otiröehlëi` | rejected | too broad; risks governing the framed-clause participants |
| CCP / PRECEDENT | `hlušh-otiröehnëi` | rejected | would associate host too narrowly with following carrier |
| CCV / SUCCESSIVE | `hlušh-otiröehňëi` | rejected | would associate host too narrowly with preceding `li` |
| CCS / SUBALTERN | `hlušh-otiröehrëi` | parked/rejected | requires paired architecture not present |
| CCQ / QUALIFIER | `hlušh-otiröehmëi` | parked/rejected | requires paired architecture not present |

---

## 5. Updated host-name-comparison parse

The active parse after v2053:

```text
[ VVR₂-framed predicate ]
    swou       = interpretive field: through all-that-is-you
    li         = affective experiencer
    X-STM      = host-name complex
        hlušh-otiröehëi          = salient fuzzy surplus-object, more-than, STM, CCN
        hlu’u «objet petit a» hü  = RLT name/apposition attached to X
    Y-CMP      = swië = than all-that-is-you
```

Local dependency map:

```text
evvralácboa
├── swou  ITP
├── li    AFF
└── hlušh-otiröehëi  STM / SUR / CCN
    ├── hlu’u «objet petit a» hü  RLT apposition
    └── swië  CMP comparison standard
```

Important bookkeeping note:

```text
The tree above is an interpretive dependency map, not a claim that Ithkuil literally brackets all dependents in this order. It is the cube’s active control parse.
```

---

## 6. Supersession and protection ledger

### 6.1 Surface forms protected by v2053

```text
hlušh-otiröehëi   active, do not auto-upgrade to CCA/CCP/CCV
hlu’u ... hü      active, still RLT apposition after host
swië              active, still delayed CMP standard
```

### 6.2 Bad repairs now blocked

```text
hlušh-otiröehlëi   blocked unless a future pass deliberately broadens the host as a case-scope head
hlušh-otiröehnëi   blocked because it misdirects STM toward carrier adjacency
hlušh-otiröehňëi   blocked because it misdirects STM toward preceding experiencer adjacency
```

---

## 7. Risk register after v2053

### 7.1 Residual comparison-distance risk

Status: tolerated.

```text
hlušh-otiröehëi ... swië
```

The comparison standard is delayed by the carrier phrase, but CMP case remains overt.

### 7.2 Residual carrier-boundary overpause risk

Status: still live.

```text
... «objet petit a» hü swië
```

The carrier-end marker may create a stronger boundary than ideal before the comparison standard.

### 7.3 Contrastive scope risk

Status: queued.

```text
alo extřudêi lo že
```

The cube has not yet decided whether `alo` scopes only over the final predicate or over the larger consequence relation: love-despite/fixation-therefore-mutilation.

---

## 8. Refactor labels added

### 8.1 `case-scope-overcorrection-risk`

Use when a local ambiguity tempts a non-default CN value that would over-govern the clause.

### 8.2 `level-cmp-not-case-scope`

Use when a comparison standard is linked by Level + CMP, not by a Case-Scope head relation.

### 8.3 `appositive-adjacency-exception-active`

Use when a Relational/Appositive case phrase attaches by immediate adjacency and does not need the head to change CN.

### 8.4 `active-spine-index`

Use for files that summarize the current active branch independently of legacy revision history.

---

## 9. Queue for v2054+

1. Contrastive adjunct scope audit: `alo`.
2. Carrier boundary/prosody audit: `hü` before delayed `swië`.
3. Whole-line register audit: bridge semicolons versus polished poetic punctuation.
4. Opening/middle love-root distinction audit: `RKW₁` versus `VVR₂`.
5. Future full-text integration: how this Lacan line will sit inside the larger love essay once the quotation block is translated as a whole.
