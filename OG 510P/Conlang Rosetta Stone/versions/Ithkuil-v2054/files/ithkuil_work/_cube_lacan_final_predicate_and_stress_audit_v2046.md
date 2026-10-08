# _cube_lacan_final_predicate_and_stress_audit_v2046

**Date:** 2026-05-25  
**Project:** Ithkuil translation of the love text — Lacan local cube  
**Purpose:** Slot-X/stress and final-predicate refactor after v2046

---

## 1. Summary decision

v2046 promotes two repairs into the active line:

```text
evvrálacboa  →  evvralácboa
aixtřas      →  extřudá
```

Active line:

```text
rkwal li sëi ; evvralácboa sou li hlušh-otilöehëi sue hlu’u «objet petit a» hü ; alo extřudá lo že
```

This cube file is a structural audit, not a new semantic paraphrase.  Its function is to prevent the project from silently mixing three things that New Ithkuil keeps distinct:

1. **Slot order** inside a formative.
2. **Relation** as shown by stress.
3. **VC / VK / VF** interpretation of Slot IX.

---

## 2. Relation/stress policy ledger

| Zone | Form | Relation/stress decision | Status |
|---|---:|---|---|
| opening predicate | `rkwal` | compressed monosyllabic unframed verbal; morphologically ultimate | active but later audit |
| middle frame head | `evvralácboa` | FRAMED + VC; antepenultimate stress | active, repaired |
| salience prehead | `hlušh-` | Type-1 concatenated prehead; ultimate by concatenation/monosyllable | active |
| host parent | `otilöehëi` | nominal unframed + VC; penultimate stress unmarked | active |
| carrier adjunct | `hlu’u` | suppletive carrier adjunct, RLT | active |
| carrier-end | `hü` | end of carrier-governed foreign phrase | active |
| contrast adjunct | `alo` | affixual adjunct CTR/1 with whole-formative scope | active, later audit |
| final predicate | `extřudá` | unframed verbal + VK; ultimate stress with explicit default VK | active, repaired |

---

## 3. Final predicate cube

### 3.1 Root axis

| Candidate | Status | Reason |
|---|---|---|
| `XTŘ₂` | active | Official Stem 2 means maiming another. |
| `XTŘ₁` | inactive | Too broad: battery/aggravated assault. |
| `XTŘ₃` | inactive | Too strong/different: torture. |
| `KÇ`/cut roots | inactive | Would over-literalize cutting and lose “maim/mutilate another.” |

### 3.2 Function/specification axis

| Candidate | Status | Reason |
|---|---|---|
| DYN + BSC | active | The final clause is an agentive act, while the Stem-2 BSC gloss already supplies “maim another.” |
| STA + BSC | inactive | Would report an obtaining maiming-state rather than the act “I mutilate you.” |
| CSV | inactive | Drifts to physical battery/assault more generally. |
| OBJ | inactive | Victim-centered nominal reading duplicates `že`. |

### 3.3 Ca axis

| Candidate | Active surface under New slot spine | Status |
|---|---:|---|
| CSL + UPX + PRX + M + NRM | `d` | active |
| CSL + UPX + DEL + M + NRM | default/near-zero or `l` depending explicitness | live alternate for completed-event reading |
| CSL + UPX + PRX + A + NRM | PRX plus Abstract perspective | future semantic alternate if the event is treated as abstract psychoanalytic structure |
| ASO + PRX | purpose/design-marked maiming | inactive; over-intentionalizes the violence |
| RPV essence | representational maiming | inactive; would translate “symbolically maim” rather than the source wording |

### 3.4 VK / validation axis

| Candidate | Surface | Status | Rationale |
|---|---:|---|---|
| ASR/OBS | `extřudá` | active bridge | Default assertive value; makes unframed-verbal status explicit. |
| ASR/USP | `extřudêi` | live alternate | Philosophically safer if the quote should avoid observational validation. |
| ASR/ITU | `extřudû` | inactive but interesting | Would construe the violent relation as intuitive/subjective feeling. |
| ASR/INF | `extřudú` | inactive but interesting | Would construe the sentence as an inference from desire-structure. |
| DEC | `extřudáu` | inactive | Would make the utterance performatively declare/alter status; too strong. |

---

## 4. Frame-head stress cube

The active middle predicate is:

```text
e-vvr-a-l-acb-oa
```

Vowel-nucleus count relevant to stress:

```text
e  a  a  o  a
```

because final `oa` is disyllabic, not a falling diphthong.

Therefore:

```text
FRAMED relation = antepenultimate stress = the second a
```

Active:

```text
evvralácboa
```

Retired:

```text
evvrálacboa
```

The older stress would only be acceptable if final `oa` were treated as a one-syllable diphthong, but New Ithkuil does not list `oa` among the falling diphthongs.

---

## 5. Supersession map after v2046

```text
FINAL PREDICATE

v2031  <XTŘ₂> lo že
v2032  aixtř- lo že
v2033  aixtřa- lo že
v2034  aixtřas lo že
v2035  alo aixtřas lo že
v2043  alo aixtřas lo že       [New branch restored, final predicate not yet audited]
v2044  alo aixtřas lo že
v2045  alo aixtřas lo že
v2046  alo extřudá lo že       [active]
```

```text
MIDDLE FRAME HEAD

v2043  évvroalacb
v2044  evvrálacboa             [slot order repaired]
v2045  evvrálacboa
v2046  evvralácboa             [stress repaired]
```

---

## 6. Cube hygiene changes

### 6.1 New audit label: `slot-spine risk`

A surface form receives this label when it was derived under a previous slot model and then carried forward into the New-Ithkuil branch without reconstruction.

Affected retired forms:

```text
aixtř-
aixtřa-
aixtřas
```

### 6.2 New audit label: `disyllabic-conjunct stress risk`

A surface form receives this label when it contains a non-diphthong vocalic conjunct near the right edge and stress was counted as if the conjunct were one syllable.

Affected retired form:

```text
evvrálacboa
```

### 6.3 Rule for future passes

Any future pass that adds or moves one of these vowel-forms must explicitly state whether it is a falling diphthong or a disyllabic conjunct before placing non-penultimate stress:

```text
oa  öe  öa  ië  uä  uë  üä  üë  ua  iä  eë
```

---

## 7. Remaining high-priority audit queue

### Priority A — host nucleus Perspective

```text
hlušh-otilöehëi sue
```

Questions:

- Is default Monadic `M` enough for “something”?
- Does the Lacanian technical object require Abstract `A` perspective?
- Would Agglomerative `G` better capture “some indeterminate excess”?

### Priority B — opening predicate explicit VK

```text
rkwal li sëi
```

Question:

- Should the opening predicate remain compressed, or should it mirror the final predicate’s explicit default VK policy?

### Priority C — validation policy for the whole quotation

Question:

- Should the line use default ASR/OBS locally, or should the quotation’s philosophical status push predicates toward ASR/USP or ASR/INF?

---

## 8. Active start point for v2047

Future Lacan passes begin from:

```text
rkwal li sëi ; evvralácboa sou li hlušh-otilöehëi sue hlu’u «objet petit a» hü ; alo extřudá lo že
```
