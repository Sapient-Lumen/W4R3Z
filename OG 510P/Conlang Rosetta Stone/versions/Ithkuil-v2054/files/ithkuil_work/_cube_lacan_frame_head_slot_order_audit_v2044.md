# _cube_lacan_frame_head_slot_order_audit_v2044

**Date:** 2026-05-25  
**Project:** Ithkuil translation of the love text — Lacan local cube  
**Purpose:** frame-head slot-order refactor after v2044

---

## 1. Summary decision

The active New-Ithkuil Lacan spine now uses:

```text
evvrálacboa
```

not:

```text
évvroalacb
```

The old form is retired because it let `oa` appear before `Ca`, where it belongs to Slot IV `VR`, while the project intended `oa` as Slot IX `SIT` case.

---

## 2. Active line after v2044

```text
rkwal li sëi ; evvrálacboa sou li hlušh-otilöehëi sue esälu’u «objet petit a» hü ; alo aixtřas lo že
```

---

## 3. Frame-head slot ledger

| Slot | Category | Active material | Value | Notes |
|---|---|---:|---|---|
| I | CC | Ø | standalone, no shortcut | No concatenation or shortcut marker. |
| II | Vv | `e` | Stem 2, PRC | `VVR₂` = infatuation/obsessiveness. |
| III | Cr | `vvr` | emotion root | Lacanian inner cathexis, not opening RKW love. |
| IV | Vr | `a` | STA/BSC/EXS | Emotional state, not dynamic process. |
| V | VxCs | Ø | none | No stem-only affix. |
| VI | Ca | `l` | default Ca | Keeps the state unmarked/default. |
| VII | VxCs | `acb` | RSN/1 Type-1 | “for no reason,” applied to stem+Ca. |
| VIII | VnCn | Ø | none | No added valence/aspect/level/effect. |
| IX | Vc | `oa` | SIT | “given that / in view of the fact that.” |
| X | stress | antepenultimate | FRAMED + Vc | Stress on second vowel nucleus: `evvrálacboa`. |

---

## 4. High-risk vowel ledger

This cube now tracks **homographic vowel risk**, i.e. cases where the same surface vowel sequence has different meanings depending on which slot hosts it.

### 4.1 `oa`

| Surface | Slot | Meaning | Status |
|---|---|---|---|
| `oa` | Slot IV `Vr` | DYN + BSC + AMG | not intended for the middle frame head |
| `oa` | Slot IX `Vc` | SIT / Situative | active target |

Rule added:

```text
Any future pass using `oa`, `ue`, `ië`, `ëi`, or another high-load vowel must explicitly declare its slot before accepting the surface.
```

---

## 5. Supersession map

```text
v2043: évvroalacb
       status: retired / slot-order bug

v2044: evvrálacboa
       status: active / slot-correct framed SIT VVR₂ head with RSN/1
```

---

## 6. What remains active from v2043

Retained unchanged:

```text
rkwal li sëi
sou li
hlušh-otilöehëi sue
esälu’u «objet petit a» hü
alo
aixtřas lo že
```

Updated:

```text
évvroalacb → evvrálacboa
```

---

## 7. Next audit targets ranked after v2044

### Priority A — host nucleus

```text
hlušh-otilöehëi sue
```

Reason: now the densest inherited form. Needs a root/prehead, Level, case, and comparison audit.

### Priority B — carrier case

```text
esälu’u «objet petit a» hü
```

Reason: RLT vs ESS remains the sharpest philosophical case question.

### Priority C — CTR adjunct

```text
alo
```

Reason: semantically apt, but should be rechecked against New-Ithkuil affixual-adjunct form and scope.

### Priority D — phonotactic repair audit

```text
evvrálacboa
```

Reason: slot-correct, but later pronunciation audit should test the `-cb-oa` transition.

---

## 8. Future-pass rule

Future Lacan passes begin from:

```text
rkwal li sëi ; evvrálacboa sou li hlušh-otilöehëi sue esälu’u «objet petit a» hü ; alo aixtřas lo že
```

The cube should not use `évvroalacb` as active surface again.
