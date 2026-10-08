# q_lacan_host_case_scope_natural_freeze_after_apposition_pass_v2053

**Date:** 2026-05-30  
**Project:** Ithkuil translation of the love text — Lacan quotation micro-passage  
**Source span:** “I love you, but, because inexplicably I love in you something more than you—the objet petit a—I mutilate you.”  
**Pass type:** host Case-Scope audit; no-surface-change grammatical freeze; cube hygiene pass

---

## 1. Scope of this revision

v2052 active line:

```text
rkwalû li sëi ; evvralácboa swou li hlušh-otiröehëi hlu’u «objet petit a» hü swië ; alo extřudêi lo že
```

v2053 audits the host/name/comparison complex after the v2052 apposition reorder:

```text
hlušh-otiröehëi hlu’u «objet petit a» hü swië
```

The local question is whether the host should retain its current NATURAL Case-Scope:

```text
hlušh-otiröehëi
           öe h ëi
           SUR CCN STM
```

or whether the carrier insertion now requires an overt non-default Case-Scope, e.g. ANTECEDENT, PRECEDENT, or SUCCESSIVE.

**v2053 freezes the answer: keep NATURAL / CCN.**

No surface change is made to the active line:

```text
rkwalû li sëi ; evvralácboa swou li hlušh-otiröehëi hlu’u «objet petit a» hü swië ; alo extřudêi lo že
```

This is a deliberately conservative pass. The work done here is negative but important: it prevents a tempting overcorrection of the host.

---

## 2. Why this audit matters

The v2052 reorder solved the immediate apposition risk:

```text
v2051: host CMP carrier/name     = apposition may attach to CMP standard
v2052: host carrier/name CMP     = apposition attaches to host
```

But moving the comparison standard after the carrier raised a new concern:

```text
X-SUR [RLT name phrase] Y-CMP
```

Could `Y-CMP` be too far away from the host to remain the comparison standard? Should the host be explicitly marked as a scope head?

That temptation is understandable, but the Case-Scope machinery is not the right fix here.

---

## 3. Parse of the host under v2053

Active host:

```text
hlušh-otiröehëi
```

Working parse:

```text
hlušh-          Type-1 salience/prominence prehead
otir-           T₀-OBJ host with AGGLOMERATIVE perspective
öe              SURPASSIVE Level: X is more M than Y
h               CCN / NATURAL Case-Scope
ëi              STM / STIMULATIVE case
```

Semantic role:

```text
host = the salient fuzzy/agglomerative surplus-object, as the stimulus of the VVR₂ affective state
```

The host must remain a participant in the framed middle predicate:

```text
evvralácboa ... li [host-STM] ...
```

That is, the speaker `li` undergoes the affective state, while the host is what triggers it.

---

## 4. Why NATURAL / CCN remains correct

New Ithkuil Case-Scope is for controlling how the case of one formative associates with adjacent formatives. The host’s actual Slot-IX case is STM:

```text
ëi = STIMULATIVE
```

If the host keeps NATURAL / CCN, then in the absence of a special head it remains associated with the framed verb. That is exactly what we want:

```text
VVR₂ framed predicate = affective state
li                    = experiencer
hlušh-otiröehëi       = stimulus
```

The host should **not** become a local case-governor of the carrier phrase or of the whole noun cluster. Its first job is still to be the STM participant of the embedded VVR₂ state.

---

## 5. Why the carrier does not require a host-scope change

The carrier phrase is:

```text
hlu’u «objet petit a» hü
```

It is a RLT carrier adjunct, not an independent participant in the affective predicate. Its job is only to provide the technical name/apposition for the host.

New Ithkuil’s special behavior for Appositive/Relational nouns solves this already: an Appositive or Relational noun adjacent to another noun naturally associates with the adjacent noun. In this order, the carrier is adjacent to the host:

```text
hlušh-otiröehëi hlu’u
```

So the carrier phrase does not need the host to become ANTECEDENT scope. It already has the right adjacency.

---

## 6. Why the comparison still does not force non-default Case-Scope

The comparison structure is not a plain possessive or appositive dependency. It is a Level construction:

```text
X-SUR ... Y-CMP
```

Here:

```text
X-SUR  = hlušh-otiröehëi
Y-CMP  = swië
```

The Y-term is explicitly in COMPARATIVE case:

```text
swië = 2m-ABSTRACT/CMP = “than all-that-is-you”
```

So the comparison standard is signaled by CMP case plus the host’s SUR Level. The carrier phrase is an intervening apposition, not a competitor for comparison-standard status.

The result is:

```text
[the salient surplus-object, named “objet petit a”] [more-than all-that-is-you]
```

rather than:

```text
[the salient surplus-object] [more-than [all-that-is-you named “objet petit a”]]
```

---

## 7. Rejected Case-Scope repairs

### 7.1 Rejected: ANTECEDENT / CCA on the host

Hypothetical surface:

```text
hlušh-otiröehlëi
```

This would make the host too much of a case-scope head. In the larger framed clause, the host is not supposed to govern every other case-marked participant. The clause already contains:

```text
swou = interpretive field
li   = affective experiencer
swië = comparison standard
```

A broad ANTECEDENT mark risks making the host structurally imperial, when it should remain one STM participant plus a Level-bearing comparison anchor.

### 7.2 Rejected: PRECEDENT / CCP on the host

Hypothetical surface:

```text
hlušh-otiröehnëi
```

This is worse. It would make the host’s case associate only with the immediately following formative, i.e. with the carrier adjunct. But the host is not the stimulus of the carrier/name; it is the stimulus of the speaker’s VVR₂ affective state.

### 7.3 Rejected: SUCCESSIVE / CCV on the host

Hypothetical surface:

```text
hlušh-otiröehňëi
```

This would associate the host only with the immediately preceding formative. The immediately preceding participant is `li`, the speaker as experiencer. That would collapse the host’s role into the experiencer zone rather than letting it remain the object-cause/stimulus of the affective state.

### 7.4 Rejected: SUBALTERN / QUALIFIER pair

Hypothetical surfaces:

```text
hlušh-otiröehrëi
hlušh-otiröehmëi
```

These require a paired scope architecture and would be overbuilt for the current local need. The carrier apposition is already solved by adjacency, and the comparison standard is already solved by CMP case.

---

## 8. Active v2053 result

No surface change:

```text
rkwalû li sëi ; evvralácboa swou li hlušh-otiröehëi hlu’u «objet petit a» hü swië ; alo extřudêi lo že
```

But the cube status changes:

```text
host-case-scope-after-name-insertion = audited
host CN value                         = CCN / NATURAL / keep
host non-default Case-Scope           = rejected for now
```

This is now a protected decision, not an unexamined inheritance from v2048.

---

## 9. Updated slot/rôle sketch

```text
rkwalû          RKW₁ romantic-love predicate, ASR/ITU
li              1m/AFF, speaker as affective experiencer
sëi             2m/STM, addressee as affective stimulus
;
evvralácboa     VVR₂ framed SIT: infatuation/obsessiveness, for no reason, as background circumstance
swou            2m-ABSTRACT/ITP, through/in all-that-is-you as interpretive field
li              1m/AFF, speaker as affective experiencer
hlušh-          Type-1 salience/prominence prehead
otiröehëi       T₀-OBJ + AGGLOMERATIVE + SUR + CCN + STM: salient fuzzy something-more as stimulus
hlu’u           carrier adjunct RLT, named/identified/distinguished as
«objet petit a» foreign Lacanian technical phrase
hü              carrier-end boundary
swië            2m-ABSTRACT/CMP, than all-that-is-you
;
alo             CTR/1 nevertheless / but / yet
extřudêi        XTŘ₂ DYN-BSC-PRX unframed verbal predicate, ASR/USP
lo              1m/ERG, speaker as tangible agent
že              detrimental 2m/ABS, harmed addressee as patient
```

---

## 10. What this pass prevents

v2053 prevents three likely future mistakes:

1. **Over-marking the host as a scope-head** merely because a carrier phrase interrupts the Level/CMP pair.
2. **Treating the carrier phrase as a participant** in the VVR₂ affective predicate.
3. **Mistaking Case-Scope for Level-governance**, when the comparison standard is already flagged by CMP case.

The line remains visibly imperfect and bridge-like, but it is now safer.

---

## 11. Next live targets

The next useful passes are now:

1. audit `alo` for whether CONTRAST should scope over the final predicate only or the whole consequence relation;
2. audit whether the active bridge line needs a polished poetic/register version without semicolons;
3. audit whether `hü` remains acceptable before delayed `swië`, or whether a parenthetical/register treatment of the French phrase would be cleaner;
4. begin a compact active-line-only index for all Lacan decisions so the cube can stop relying on revision history to reconstruct the current spine.
