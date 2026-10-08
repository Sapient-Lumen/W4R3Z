# _cube_lacan_apposition_scope_audit_v2052

**Date:** 2026-05-30  
**Project:** Ithkuil translation of the love text — Lacan local cube  
**Purpose:** apposition/name/comparison scope ledger after v2052

---

## 1. Summary decision

v2052 changes the order of the host/name/comparison packet:

```text
hlušh-otiröehëi swië hlu’u «objet petit a» hü
        ↓
hlušh-otiröehëi hlu’u «objet petit a» hü swië
```

Active line:

```text
rkwalû li sëi ; evvralácboa swou li hlušh-otiröehëi hlu’u «objet petit a» hü swië ; alo extřudêi lo že
```

Cube summary:

```text
RKW₁ opening love predicate            active from v2047
VVR₂ middle affective fixation         active from v2044
RSN/1 inexplicable/for-no-reason        active from v2044
SIT framed background/“given that”      active from v2044
2m-ABSTRACT/ITP swou                    active from v2050
host AGGLOMERATIVE perspective          active from v2048
carrier adjunct hlu’u + hü              active from v2045
carrier-adjacent-to-host ordering        active from v2052
2m-ABSTRACT/CMP swië                    active from v2051, now after host+name
final XTŘ₂ ASR/USP extřudêi             active from v2049
```

---

## 2. New cube axis: `apposition-attachment-target`

This axis tracks what the RLT carrier/name phrase is structurally attached to.

| Candidate order | Status | Attachment risk | Reading |
|---|---|---|---|
| `host CMP carrier` | superseded | carrier may attach to CMP standard | “than all-that-is-you, named objet petit a” |
| `host carrier CMP` | active | comparison is less adjacent, but apposition is clean | “something named objet petit a, more than all-that-is-you” |
| `carrier host CMP` | rejected | carrier/name precedes what it names; bad default order | “objet-petit-a-ish something…” |
| `host CMP [parenthetical carrier]` | parked | would need register/intonation policy | closer to English dash order |
| `host carrier + explicit case-scope + CMP` | parked | more morphology than the bridge needs | maximally disambiguated but heavier |

Active value:

```text
apposition-attachment-target = host
```

---

## 3. New cube axis: `cmp-adjacency-vs-apposition-adjacency`

This axis records the tradeoff exposed by v2052.

### 3.1 Old priority

v2051 prioritized comparison adjacency:

```text
X-SUR Y-CMP NAME-RLT
```

Advantage:

```text
hlušh-otiröehëi swië
```

keeps the Level/CMP pair visually tight.

Disadvantage:

```text
swië hlu’u
```

puts the name/apposition next to the wrong target.

### 3.2 New priority

v2052 prioritizes apposition adjacency:

```text
X-SUR NAME-RLT Y-CMP
```

Advantage:

```text
hlušh-otiröehëi hlu’u
```

puts the carrier/name phrase next to the host it identifies.

Disadvantage:

```text
hü swië
```

pushes the comparison standard after the carrier closure.

Active rule for the cube:

```text
When a carrier/name apposition and a comparison standard compete for adjacency, apposition-to-host outranks X/Y adjacency, because CMP case still identifies the comparison standard.
```

---

## 4. New cube axis: `host-name-complex`

v2052 treats:

```text
hlušh-otiröehëi hlu’u «objet petit a» hü
```

as a local host-name complex before the comparison standard applies.

The complex has internal layers:

```text
host semantics       hlušh-otiröehëi
name/apposition      hlu’u «objet petit a» hü
comparison standard  swië
```

This prevents the carrier phrase from being mistaken for the primary object-stimulus or for the comparison standard.

---

## 5. Supersession ledger

```text
CARRIER / NAME ZONE

v2022  esälu’u «objet petit a»                 full carrier-root RLT pass
v2023  esälu’u «objet petit a» hü              carrier-end marker added
v2045  hlu’u «objet petit a» hü                carrier adjunct RLT replaces full carrier stem
v2051  ... swië hlu’u «objet petit a» hü       abstract CMP before carrier, attachment risk
v2052  ... hlu’u «objet petit a» hü swië       active: carrier immediately apposes host
```

---

## 6. Risk register

### 6.1 Comparison distance risk

Risk:

```text
hlušh-otiröehëi ... swië
```

may be read less immediately than:

```text
hlušh-otiröehëi swië
```

Mitigation:

CMP case remains overt on `swië`, and the appositional repair prevents a worse attachment error.

### 6.2 Carrier-boundary overpause risk

Risk:

```text
hü swië
```

may make the comparison standard sound like a new afterthought rather than the Y-term of SUR.

Mitigation:

The source already uses dash punctuation around the Lacanian term. The bridge line can tolerate the pause until a later prosody/register pass.

### 6.3 Case-scope under-audited risk

Risk:

The host’s natural `h` case-scope may be too weak after inserting the carrier before the CMP term.

Mitigation:

Add `host-case-scope-after-name-insertion` to the v2053 queue.

---

## 7. Refactor labels added

### 7.1 `apposition-attachment-risk`

Flags forms where a Relational/Appositive case phrase is nearest the wrong target.

### 7.2 `cmp-vs-rlt-adjacency-conflict`

Flags cases where a Level/CMP pair and an RLT/name phrase both want to be next to the same host.

### 7.3 `host-name-complex`

Treats host + carrier/name as a temporary constituent for cube bookkeeping.

### 7.4 `foreign-name-after-caseful-host`

Marks places where unchanged foreign material follows a caseful host and may interrupt later arguments.

---

## 8. Active start point for v2053

```text
rkwalû li sëi ; evvralácboa swou li hlušh-otiröehëi hlu’u «objet petit a» hü swië ; alo extřudêi lo že
```

Recommended next targets:

1. Host Case-Scope after apposition insertion: `hlušh-otiröehëi`.
2. Contrastive adjunct scope: `alo extřudêi lo že`.
3. Create a compact active-line index, separating active v2052 surface from legacy branch history.
4. Audit whether `hü` should be retained in written bridge form or replaced by a register/intonation annotation in a polished poetic line.
