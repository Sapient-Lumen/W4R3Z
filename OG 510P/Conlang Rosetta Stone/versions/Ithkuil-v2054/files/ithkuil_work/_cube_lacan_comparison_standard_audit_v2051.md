# _cube_lacan_comparison_standard_audit_v2051

**Date:** 2026-05-30  
**Project:** Ithkuil translation of the love text — Lacan local cube  
**Purpose:** comparison-standard ledger after v2051

---

## 1. Summary decision

v2051 changes the comparative “than you” term:

```text
sue  →  swië
```

Active line:

```text
rkwalû li sëi ; evvralácboa swou li hlušh-otiröehëi swië hlu’u «objet petit a» hü ; alo extřudêi lo že
```

Cube summary:

```text
RKW₁ opening love predicate          active from v2047
VVR₂ middle affective fixation       active from v2044
RSN/1 inexplicable/for-no-reason      active from v2044
SIT framed background/“given that”    active from v2044
2m-ABSTRACT/ITP swou                  active from v2050
host AGGLOMERATIVE perspective        active from v2048
2m-ABSTRACT/CMP swië                  active from v2051
carrier adjunct hlu’u + hü            active from v2045
final XTŘ₂ ASR/USP extřudêi           active from v2049
```

---

## 2. New cube axis: `comparison-standard-domain`

v2051 adds a dedicated axis for what kind of “you” is being exceeded by the “something more.”

| Value | Candidate | Status | Meaning |
|---|---:|---|---|
| monadic-standard | `sue` | superseded/minimal | more than you as simple conversational addressee |
| abstract-standard | `swië` | active | more than all-that-is-you / everything-about-you |
| nomic-standard | `sçue`-type | rejected | more than you-ness / the category of you |
| possessive-source | GEN option | rejected | more than that which is of you / your inherent possession |
| correlative-standard | COR option | rejected for active comparison | more in relation to you, too loose for Level comparison |
| external-standard-marked | XCL/SCL option | parked | would add external-standard nuance not present in the source |

---

## 3. New cube axis: `paired-case-vowel-after-abstract`

This pass also adds a morphology-safety axis:

```text
paired-case-vowel-after-abstract
```

Problem:

```text
s + w + ue  →  *swue
```

This looks semantically transparent but misses the alternate case vowel triggered after `-w-`.

Active solution:

```text
s + w + ië  →  swië
```

This axis should be checked whenever a referential contains:

```text
ABSTRACT -w/-y + paired Vc case
```

Known local candidates already affected or worth watching:

```text
swië  = active CMP after -w
swou  = not affected; ITP is ou, no paired CMP-style alternant here
```

---

## 4. Relation to v2050 anchor-domain axis

v2050 separated:

```text
swou = beloved-as-field
sue  = beloved-as-standard
```

v2051 revises this to:

```text
swou = all-that-is-you as interpretive/desire field
swië = all-that-is-you as comparison standard
```

This does not erase the field/standard distinction. It moves the distinction from referential domain into case-role:

```text
ITP vs CMP
```

The cube now treats the Lacan “you” as abstract in both locations, but grammatically differentiated:

```text
in you          → swou
more than you   → swië
```

---

## 5. Supersession ledger

```text
COMPARATIVE “THAN YOU” TERM

v2026  sue     first frozen 2m/CMP form, design-doc branch
v2037  kè      deprecated public-grammar migration branch
v2043  sue     New-Ithkuil recanonicalized branch restored
v2050  sue     kept monadic after swou abstraction
v2051  swië    abstract 2m/CMP active; “than all-that-is-you”
```

`kè` stays quarantined with the v2037–v2042 public-grammar migration branch. `sue` remains a valid minimal New-Ithkuil fallback.

---

## 6. New refactor labels added

### 6.1 `comparison-standard-domain`

Tracks whether the Y-term in the SUR comparison is monadic, abstract, nomic, possessive, etc.

### 6.2 `paired-case-vowel-after-abstract`

Forces an allomorph check when `-w/-y` precedes a case vowel with an alternate form.

### 6.3 `same-domain-different-case`

Marks the new `swou` / `swië` pair: same abstract second-person domain, different case role.

### 6.4 `sue-fallback-live`

Flags that `sue` is not “wrong”; it is only superseded by a stronger Lacanian reading.

---

## 7. Risk register

### 7.1 Over-abstracting “you”

Risk:

```text
swië
```

may overstate “more than you” as “more than absolutely everything about you,” whereas the source may intend a simpler contrast with the empirical beloved.

Mitigation:

Keep `sue` as a live fallback.

### 7.2 Pseudo-finality of the bridge line

Risk:

The line now looks very polished but remains a bridge. Host nucleus and contrastive wrapper are still under audit.

Mitigation:

Every active file must continue to label the current line as a working bridge, not a final poem-quality translation.

### 7.3 Misreading `swië` as a separate root

Risk:

The surface form may look opaque to future readers.

Mitigation:

The derivation must be shown wherever the line is explained:

```text
s + w + ië = swië
```

---

## 8. Active start point for v2052

```text
rkwalû li sëi ; evvralácboa swou li hlušh-otiröehëi swië hlu’u «objet petit a» hü ; alo extřudêi lo že
```

Recommended next targets:

1. Full host-nucleus audit: `hlušh-otiröehëi`.
2. Contrastive adjunct audit: `alo` Degree/type/scope.
3. Carrier-boundary audit: `hlu’u ... hü` for written multi-word foreign phrase convention.
4. Global active-line index: create a compact file listing only current active forms and superseded branches.
