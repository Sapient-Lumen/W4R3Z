# q_lacan_new_ithkuil_recanonicalization_rsn1_cube_branch_audit_pass_v2043

**Date:** 2026-05-25  
**Project:** Ithkuil translation of the love text — Lacan quotation micro-passage  
**Source span:** “I love you, but, because inexplicably I love in you something more than you—the objet petit a—I mutilate you.”  
**Pass type:** canonical-branch correction + RSN suffix audit + cube branch refactor

---

## 1. Scope of this revision

v2043 is not a small forward spelling pass. It is a correction to the project’s branch policy.

The v2037–v2042 sequence treated the older public `ithkuil.net` grammar pages as the active “current-public” target. That was a useful audit mistake because it forced several hidden assumptions into the open, but it is not the right canonical target for this project. The old Ithkuil grammar site explicitly states that, as of February 2023, the language has been replaced by **New Ithkuil**. The New Ithkuil design document is the successor grammar branch that should govern this translation unless the project explicitly opens an Ithkuil-III historical branch.

Therefore this pass does three things:

1. demotes v2037–v2042 from “active current spine” to “archival Ithkuil-III/old-public migration experiment”;
2. restores the New-Ithkuil-compatible referential/case/carrier line from the v2022–v2036 branch;
3. keeps the useful v2041 insight that “inexplicably” should be handled by `RSN`, but corrects its degree and consonantal form using the New Ithkuil affix list.

---

## 2. Working bridge line after v2043

### v2042 line — now quarantined

```text
rkwal ti kui ; evvróîlošš köi ti hlušh-otilöehui kè upealöt’ «objet petit a» ; iňň aixtřas to ke
```

### v2043 line — active New Ithkuil spine

```text
rkwal li sëi ; évvroalacb sou li hlušh-otilöehëi sue esälu’u «objet petit a» hü ; alo aixtřas lo že
```

Approximate back-translation:

> I love you; given the background situation that, for no reason / inexplicably, through you I undergo infatuated-obsessive attachment toward the salient something-more-than-you, identified by “objet petit a”; nevertheless, I maim you.

This line is a **bridge form**, not the finished literary translation. Its job is to keep every major grammatical decision visible while the cube stabilizes.

---

## 3. Major active replacements from v2042 to v2043

```text
ti    → li
kui   → sëi
köi   → sou
hlušh-otilöehui → hlušh-otilöehëi
kè    → sue
upealöt’ «objet petit a» → esälu’u «objet petit a» hü
iňň   → alo
to    → lo
ke    → že
evvróîlošš → évvroalacb
```

The replacements are not arbitrary reversions. They follow the restored canonical target:

```text
New Ithkuil design-doc branch: active
Ithkuil-III/old-public migration branch: quarantined
```

---

## 4. Why the v2037–v2042 branch is demoted

The old public grammar pages are still valuable, but they are not the target grammar for this translation. They are retained for provenance and historical comparison only.

The decisive practical consequences are:

```text
1m monadic neutral:       l, not t
2m monadic neutral:       s, not k
2m detrimental:           ž, not k+default ABS
carrier root:             -S-, not -P-
carrier-end option:       hü remains available as END
```

So the v2042 line is not “wrong because it was careless”; it is wrong because it follows the wrong grammar generation for the project’s stated canon target.

---

## 5. Referential and case restoration

The New Ithkuil referential table gives:

```text
1m monadic speaker       l / r / ř
2m monadic addressee     s / š / ž
```

where the three columns are Neutral, Beneficial, and Detrimental Effect.

Therefore the local personal forms return to:

```text
li   = l + AFF(i)       = I as affective experiencer
sëi  = s + STM(ëi)      = you as affective stimulus
sou  = s + ITP(ou)      = through/in you as subjective interpretive context
sue  = s + CMP(ue)      = than/as-compared-to you
lo   = l + ERG(o)       = I as agent/force of tangible maiming
že   = ž + ABS(e)       = you as detrimentally affected patient
```

This restores the key conceptual split:

```text
opening love:      li ... sëi      affective love relation
middle obsession:  sou li ...      through/in you, I as experiencer
final violence:    lo že           I as agent, you as harmed patient
```

---

## 6. RSN correction: `evvróîlošš` → `évvroalacb`

v2041’s insight was correct in kind: “inexplicably” belongs on the affective/obsessive middle predicate, not as a separate “puzzlement” prehead. The error was in the affix data used.

The active New Ithkuil affix list gives:

```text
RSN = -cb
RSN/1 = “for no reason”
```

The New Ithkuil VXCS vowel table gives Type-1 Degree 1 as:

```text
a
```

Therefore the working Type-1 suffix is:

```text
RSN/1 Type-1 = -acb
```

The v2041/v2042 form:

```text
evvróîlošš
```

is retired because it uses the older `-šš` consonantal form and the wrong degree assignment.

The replacement is:

```text
évvroalacb
```

working analysis:

```text
évvroal-    VVR₂ affective/obsessive state in SIT frame posture
-acb        RSN/1 “for no reason”
```

I am deliberately keeping the older `VVR₂.SIT` shell `évvroal-` for now rather than rederiving the full framed formative from scratch in this same pass. The point of v2043 is to fix the branch and the RSN affix; a later pass can audit the entire framed-formative stress and slot shape.

---

## 7. Carrier restoration and TPF quarantine

v2042 used:

```text
upealöt’ «objet petit a»
```

That is now quarantined for two separate reasons:

1. it used the older public `-P-` carrier branch rather than New Ithkuil’s `-S-` carrier root;
2. it treated `TPF/2` as the frame-end marker, whereas the New Ithkuil affix list gives `TPF/1` as `[end of frame]`.

The active line therefore returns to the known New Ithkuil carrier construction:

```text
esälu’u «objet petit a» hü
```

with the status:

```text
esälu’u     abstract/inanimate carrier for the foreign technical phrase, currently RLT-marked
hü          END / carrier-end marker for the foreign phrase
```

The conceptual ESS insight from v2038 is not discarded; it is moved to the open-debt list:

```text
RLT carrier vs ESS carrier for «objet petit a» remains a high-value future audit.
```

I am not attaching a TPF marker in v2043. If a frame-end marker is later needed, the target will be New Ithkuil `TPF/1`, not the v2042 `TPF/2`, and it must be hosted somewhere that does not corrupt the carrier/foreign phrase construction.

---

## 8. Host nucleus status after branch correction

The host nucleus returns to:

```text
hlušh-otilöehëi sue
```

working burden:

```text
“the salient something more than you” as the affective stimulus/cause of VVR₂
```

This remains the highest-value local morphology audit, but v2043 does not reopen its root/prehead derivation. The important thing in this pass is that it is no longer carrying the v2037 `DER` migration:

```text
hlušh-otilöehui   retired
hlušh-otilöehëi   active again
```

Reason: New Ithkuil’s STM case directly marks the trigger of an unwilled affective response, which is precisely the Lacanian role of the surplus object as object-cause of desire.

---

## 9. Active local morpheme ledger after v2043

```text
rkwal             li        sëi
RKW₁-love          1m.AFF    2m.STM

évvroalacb                     sou       li        hlušh-otilöehëi             sue       esälu’u                 «objet petit a»  hü
VVR₂.SIT.FRAMED + RSN/1          2m.ITP    1m.AFF    salient-more.host.STM       2m.CMP   carrier.abstract.RLT      foreign phrase   END

alo        aixtřas      lo        že
CTR/1      XTŘ₂-maim     1m.ERG    2m.DETR.ABS
```

Expanded interpretation:

```text
rkwal li sëi
    I love you.

évvroalacb sou li hlušh-otilöehëi sue esälu’u «objet petit a» hü
    Given that, for no reason / inexplicably,
    through you I undergo infatuated-obsessive attachment toward the salient
    something-more-than-you, identified by the technical phrase “objet petit a.”

alo aixtřas lo že
    Nevertheless, I maim you.
```

---

## 10. Cube refactor performed in this pass

This pass adds a new cube ledger:

```text
_cube_lacan_branch_policy_new_ithkuil_recanonicalization_v2043.md
```

It supersedes the v2042 cube ledger as the active navigation file.

The refactor changes the cube’s top-level branch policy:

```text
canonical target:       New Ithkuil / Ithkuil IV design-doc + New lexicon + affixes v1.0.1
archival branch:        Ithkuil-III / old public grammar pages
active Lacan spine:     v2043
quarantined spine:      v2037–v2042
```

No older files were deleted. The purpose is to prevent the archive from silently compounding a grammar-generation mismatch.

---

## 11. Remaining open problems after v2043

### 11.1 Re-derive the framed `VVR₂.SIT` head

```text
évvroalacb
```

The RSN piece is now corrected. The older `évvroal-` shell still deserves a from-first-principles New Ithkuil reparse.

### 11.2 Audit carrier case: RLT vs ESS

```text
esälu’u «objet petit a» hü
```

RLT preserves the “identifying/distinguishing relative apposition” reading. ESS may better encode “the role/name by which the surplus object is known.” This must be rederived using the New Ithkuil `-S-` carrier root, not the old `-P-` carrier.

### 11.3 Audit host nucleus

```text
hlušh-otilöehëi sue
```

The surface is restored to the New Ithkuil branch, but the internal derivation of `hlušh-otil-` still needs a current lexicon and syntax pass.

### 11.4 Decide if a frame-end marker is needed

If needed, use New Ithkuil `TPF/1`, not v2042’s `TPF/2`, and do not suffix the foreign phrase itself.

---

## 12. Reference anchors for this pass

- New Ithkuil design document v1.3.2: `https://www.ithkuil.net/New_Ithkuil_design_doc_v_1_3.pdf`
- New Ithkuil lexicon: `https://ithkuil.net/newithkuil_lexicon.pdf`
- New Ithkuil affixes v1.0.1: `https://ithkuil.net/affixes_v_1_0.pdf`
- Old Ithkuil grammar introduction, used only to confirm that the old public pages are archival: `https://ithkuil.net/00_intro.html`
