# _cube_lacan_contrastive_scope_audit_v2054

**Date:** 2026-05-30  
**Project:** Ithkuil translation of the love text — Lacan local cube  
**Purpose:** contrastive hinge audit/refactor after v2054

---

## 1. Active line after v2054

```text
rkwalû li sëi ; evvralácboa swou li hlušh-otiröehëi hlu’u «objet petit a» hü swië ; alö extřudêi lo že
```

v2054 changes only the contrastive hinge:

```text
alo  →  alö
```

The change is not a different adversative affix. It is a scope widening from:

```text
CTR/1 over final formative only
```

to:

```text
CTR/1 over final predicate cluster
```

---

## 2. Active-spine ledger delta

| Segment | v2053 form | v2054 form | Status |
|---|---:|---:|---|
| opening love predicate | `rkwalû` | `rkwalû` | unchanged |
| opening speaker | `li` | `li` | unchanged |
| opening addressee | `sëi` | `sëi` | unchanged |
| frame head | `evvralácboa` | `evvralácboa` | unchanged |
| “in you” anchor | `swou` | `swou` | unchanged |
| middle speaker | `li` | `li` | unchanged |
| host prehead | `hlušh-` | `hlušh-` | unchanged |
| host nucleus | `otiröehëi` | `otiröehëi` | unchanged |
| carrier/name | `hlu’u «objet petit a» hü` | `hlu’u «objet petit a» hü` | unchanged |
| comparison standard | `swië` | `swië` | unchanged |
| contrastive hinge | `alo` | `alö` | changed: scope widened |
| final predicate | `extřudêi` | `extřudêi` | unchanged |
| final agent | `lo` | `lo` | unchanged |
| final patient | `že` | `že` | unchanged |

---

## 3. New cube axis: `contrastive-scope-domain`

Active value:

```text
contrastive-scope-domain = final-predicate-cluster
```

Definition:

```text
The adversative operator scopes over the final predicate formative plus its adjacent argument referentials.
```

Active cluster:

```text
alö [ extřudêi lo že ]
```

Not:

```text
alo [ extřudêi ] lo že
```

---

## 4. Scope matrix

| Candidate | Surface | Status | Scope target | Reason |
|---|---:|---|---|---|
| bare affix | `al` | rejected | under-specified | no overt scope vowel; too loose for the cube |
| whole-formative | `alo` | superseded | `extřudêi` only | adequate before final argument cluster was stable; now too narrow |
| formative + adjacent adjuncts | `alö` | active | `extřudêi lo že` | matches “but I mutilate you” as a whole final predication |
| internal suffix | `extřu...l...` | rejected | maim-root/formative | makes contrastiveness too lexical/derivational |
| stronger contrast | `CTR/2` path | rejected/parked | however/on-the-other-hand | too rhetorically explicit for the source’s light “but” |
| XOR path | `XOR/5` / `XOR/6` | rejected | contrary/instead | would imply replacement rather than coexistence of love and violence |

---

## 5. Updated dependency map

```text
sentence
├── opening avowal
│   ├── rkwalû
│   ├── li
│   └── sëi
├── explanatory SIT frame
│   ├── evvralácboa
│   ├── swou
│   ├── li
│   ├── hlušh-otiröehëi
│   │   ├── hlu’u «objet petit a» hü
│   │   └── swië
└── adversative final predication
    ├── alö
    └── extřudêi
        ├── lo
        └── že
```

Important:

```text
The tree is the cube’s control parse, not a claim that the romanized line contains literal brackets.
```

---

## 6. Refactor labels added

### 6.1 `contrastive-final-cluster`

Use when the adversative operator scopes over the final predicate plus its explicit participants.

Current example:

```text
alö extřudêi lo že
```

### 6.2 `vs-o-too-narrow`

Use when an affixual adjunct’s `VS=o` scopes only over the formative but the intended operator should include adjacent argument material.

Superseded example:

```text
alo extřudêi lo že
```

### 6.3 `vs-ö-local-not-global`

Use when `VS=ö` is accepted locally but explicitly prevented from becoming sentence-global.

Current protection:

```text
alö includes lo že; it does not include the preceding frame evvralácboa ... swië.
```

### 6.4 `adversative-coexistence-not-replacement`

Use when the contrastive relation preserves both clauses as true/active, blocking XOR-style replacements.

Current application:

```text
I love you remains active; I mutilate you is paradoxically added, not substituted.
```

---

## 7. Supersession ledger

### 7.1 Now superseded

```text
alo extřudêi lo že
```

Reason:

```text
`alo` says CTR/1 scopes over the final formative as a whole. Once `lo že` became stable adjacent argument material, the final contrast needed to include them.
```

### 7.2 Now active

```text
alö extřudêi lo že
```

Reason:

```text
`alö` uses the same CTR/1 affix but widens the affixual-adjunct scope to include adjacent adjunct material in the final predicate cluster.
```

### 7.3 Protected against auto-reversion

```text
alö
```

Protection condition:

```text
Do not revert to `alo` unless future passes either internalize the final participants into the formative or move `lo že` outside the contrastive target.
```

---

## 8. Risk register after v2054

### 8.1 Over-capture risk

Status: controlled.

```text
... swië ; alö extřudêi lo že
```

`alö` could look wider than intended, but its immediate adjacency to `extřudêi` plus the semicolon bridge keeps it local.

### 8.2 Punctuation-dependence risk

Status: still live.

The semicolons are bridge punctuation. A future polished pass should produce a more native-seeming line without relying on punctuation to carry all major boundaries.

### 8.3 Carrier-boundary heaviness risk

Status: queued.

```text
hlu’u «objet petit a» hü swië
```

The delayed comparison standard remains grammatically motivated but prosodically heavy.

### 8.4 Frame-causality risk

Status: queued.

The active `SIT` frame still says “given/in view of the fact that.” A future pass should audit whether Lacan’s “because” calls for a more causal frame or whether `SIT + RSN/1` is the cleaner psychoanalytic reading.

---

## 9. Active one-line control gloss after v2054

```text
I love you; given, for no reason, that I experience infatuated fixation through all-that-is-you toward the salient fuzzy surplus-object named “objet petit a,” more-than all-that-is-you; nevertheless I maim you-to-your-detriment.
```

---

## 10. Queue for v2055+

1. Carrier boundary/prosody audit: `hü` before delayed `swië`.
2. Punctuation/register pass: make a cleaner poetic bridge line.
3. SIT-vs-causal-frame audit: whether “because” should remain Situative or become more explicitly causal.
4. Active-spine digest: one compact, non-historical file that gives only the current line and parse.
5. Whole love-text integration: decide where the Lacan quote sits relative to the broader goodwill/agape thesis.
