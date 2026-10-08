# q_lacan_carrier_adjunct_rlt_reparse_hluu_pass_v2045

**Date:** 2026-05-25  
**Project:** Ithkuil translation of the love text — Lacan quotation micro-passage  
**Source span:** “I love you, but, because inexplicably I love in you something more than you—the objet petit a—I mutilate you.”  
**Pass type:** carrier-phrase reparse + naming/apposition audit + cube carrier refactor

---

## 1. Scope of this revision

v2044 fixed the middle framed predicate and made the active New-Ithkuil bridge line:

```text
rkwal li sëi ; evvrálacboa sou li hlušh-otilöehëi sue esälu’u «objet petit a» hü ; alo aixtřas lo že
```

v2045 moves rightward to the foreign technical phrase:

```text
esälu’u «objet petit a» hü
```

The active change is:

```text
esälu’u «objet petit a» hü  →  hlu’u «objet petit a» hü
```

The new line is:

```text
rkwal li sëi ; evvrálacboa sou li hlušh-otilöehëi sue hlu’u «objet petit a» hü ; alo aixtřas lo že
```

Approximate back-translation:

> I love you; given that, for no reason, through you I undergo infatuated-obsessive attachment toward a salient something more than you, named/identified “objet petit a”; nevertheless, I maim you.

This remains a bridge line, not a final literary line.

---

## 2. Why this is not a cosmetic carrier shortening

The inherited form:

```text
esälu’u
```

was treated as a full carrier-stem-style expression: a carrier root with a Slot-IX RLT case burden. That was defensible during the early archive phase because the project was still trying to make the foreign phrase grammatically visible.

But v2044 has already made the host semantically explicit:

```text
hlušh-otilöehëi sue
```

That host already means:

```text
salient/prominent + discourse-specified object/entity/situation/idea + more-than-you + STM
```

So the following foreign phrase no longer needs to carry the burden of being a full nominal inanimate/abstract entity. Its job is narrower:

```text
name / technical label / appositive identifier
```

For that narrower job, New Ithkuil provides a better tool: the **carrier adjunct**.

---

## 3. Official pattern: carrier adjunct marked for Relative case

The design grammar gives a directly relevant example:

```text
Yuřká warrnenëi kšila hlu’u Bubu.
```

with the gloss:

```text
CARRIER-RLT ‘Bubu’
```

and the translation:

```text
“The clown owns an ocelot named Boo-boo.”
```

That is structurally close to what the Lacan line needs:

```text
salient something more than you, named/identified “objet petit a”
```

The carrier adjunct is described as a shortcut for a full carrier stem that provides case information only. This is exactly the reduced function needed here: the host tells us what kind of entity is being discussed; the carrier adjunct tells us that the following foreign material is the name/label by which it is picked out.

So v2045 replaces the full carrier-stem-style inherited form with:

```text
hlu’u
```

where:

```text
hl      = CAR carrier adjunct consonantal form
u’u     = RLT / Relative case realization
hlu’u   = CARRIER-RLT
```

---

## 4. Why RLT remains active, not ESS

The strongest challenger remains ESS, because English apposition often tempts an “as / known as / identified as” interpretation.

Possible inactive alternative:

```text
hlei’ «objet petit a» hü
```

Control gloss:

```text
CARRIER-ESS “objet petit a”
```

But the local function is not primarily predicative role-assignment:

```text
I treat the host as objet petit a.
```

Nor is it a claim that the host is functioning in the role of objet petit a. The dash in the source is closer to a naming or relative apposition:

```text
something more than you — the objet petit a —
```

That is, the foreign phrase is a technical name identifying the host. The official “ocelot named Boo-boo” carrier example uses RLT, not ESS, for precisely this kind of naming relation.

Therefore:

```text
hlu’u «objet petit a»
```

is retained over:

```text
hlei’ «objet petit a»
```

ESS remains a live alternate only if a later literary version wants the stronger reading:

> the something-more-than-you under the role / guise / identificatory function of objet petit a

That is a Lacanianly interesting reading, but it is less source-near than the active RLT naming/apposition.

---

## 5. Why the carrier-end `hü` remains

v2038 temporarily retired `hü` during the quarantined old-public branch, but v2043 restored the New-Ithkuil branch and v2045 confirms the need for `hü` in this exact local environment.

The foreign phrase is multi-word:

```text
objet petit a
```

and it is immediately followed by a return to Ithkuil material:

```text
alo aixtřas lo že
```

New Ithkuil allows the end of a term/phrase governed by a carrier stem or carrier adjunct to be signaled by the carrier-end adjunct:

```text
hü
```

So v2045 keeps:

```text
hlu’u «objet petit a» hü
```

rather than:

```text
hlu’u «objet petit a»
```

The end marker is not case on the French phrase. It is a parsing boundary: “the carrier-governed foreign phrase is over; return to ordinary Ithkuil parsing now.”

---

## 6. Why NAM is not used

New Ithkuil also has a **NAM** naming adjunct. This is tempting, but it is not the right active form here.

NAM marks the following word as a name being referred to as a name, rather than referring to the entity bearing that name.

That would be useful for a sentence like:

```text
He said the words “objet petit a.”
```

But in the Lacan line, the speaker is not referring to the phrase as a string of words. The phrase names the thing/excess/object-cause in the sentence. We need reference to the named entity, not metalinguistic mention of the name.

So:

```text
hlu’u = carrier-relative reference to the entity/technical object named by the phrase
```

not:

```text
hn... = naming-adjunct mention of the phrase as a name-token
```

---

## 7. Why PHR is not used

PHR is also tempting because “objet petit a” is a phrase, not a single proper noun. But PHR turns the subsequent phrase into a conventionalized quasi-lexicalized gestalt at a meta-level. Here, the source already supplies a conventionalized foreign technical term; the task is not to make the whole French phrase an Ithkuil phrasal gestalt. It is to let it remain French while linking it to the preceding Ithkuil host.

Therefore PHR is too meta-grammatical for the active line.

The active policy is:

```text
foreign term stays foreign;
Ithkuil grammar supplies only the relational wrapper.
```

---

## 8. Resulting local parse after v2045

The local object packet is now:

```text
hlušh-otilöehëi sue hlu’u «objet petit a» hü
```

Parse:

```text
hlušh-        Type-1 concatenated salience/prominence prehead
otil-         Stem-0 -T- OBJ parent head: discourse-specified object/entity/situation/idea
öeh           Slot VIII SUR + natural Case-Scope: more-than
ëi            Slot IX STM: affective stimulus of VVR₂
sue           2m neutral referential in CMP: than you
hlu’u         carrier adjunct in RLT: named/identified as...
«objet petit a» unchanged foreign phrase
hü            carrier-end marker
```

English diagnostic:

```text
the salient something-more-than-you, named “objet petit a,” as the stimulus of my obsessive attachment
```

---

## 9. Supersession map

```text
v2022: esälu’u «objet petit a»
       status: early full-carrier RLT solution, no explicit phrase end

v2023: esälu’u «objet petit a» hü
       status: full-carrier RLT + correct carrier-end policy

v2038: upeal «objet petit a»
       status: quarantined old-public-grammar migration branch

v2042: upealöt’ «objet petit a»
       status: quarantined old-public-grammar migration + frame-end experiment

v2043-v2044: esälu’u «objet petit a» hü
       status: New-Ithkuil branch restored but still over-heavy full-carrier surface

v2045: hlu’u «objet petit a» hü
       status: active New-Ithkuil carrier-adjunct RLT solution
```

---

## 10. Updated active line for the next pass

Future Lacan passes should begin from:

```text
rkwal li sëi ; evvrálacboa sou li hlušh-otilöehëi sue hlu’u «objet petit a» hü ; alo aixtřas lo že
```

Next recommended audit target:

```text
hlušh-otilöehëi sue
```

Reason: after this carrier refactor, the host nucleus is again the densest inherited object. It needs a separate stress/Level/case-scope audit, but v2045 does not re-open it because the carrier replacement already touches the appositional edge of that object packet.
