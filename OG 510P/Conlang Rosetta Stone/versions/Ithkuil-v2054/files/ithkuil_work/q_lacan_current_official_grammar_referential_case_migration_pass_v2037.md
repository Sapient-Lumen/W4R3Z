# q_lacan_current_official_grammar_referential_case_migration_pass_v2037

**Date:** 2026-05-23  
**Project:** Ithkuil translation of the love text — Lacan quotation micro-passage  
**Source span:** “I love you, but, because inexplicably I love in you something more than you—the objet petit a—I mutilate you.”  
**Pass type:** canonicality/migration audit against the current public Ithkuil HTML grammar

---

## 1. Scope of this revision

v2022–v2036 made useful local decisions, but they also carried forward several design-document-era constants: old personal-reference consonants, an old `STM` case label, older `SIT`/`ITP` values, and an older `CTR₁ → alo` analysis. v2037 does **not** pretend the whole Lacan sentence is final. It freezes a safer policy:

> **Prospective rule:** from this revision onward, the current public Ithkuil HTML grammar wins over older New Ithkuil design-document values unless a pass explicitly says it is preserving an older dialect/specification for a named reason.

The immediate result is a controlled migration of the most exposed personal-reference and case material around the Lacan sentence.

---

## 2. Working bridge line after v2037

### v2036 line being audited

```text
rkwal li sëi ; <FRAMED:SIT[ hleňfó-évvroal- sou li hlušh-otilöehëi sue esälu’u «objet petit a» hü ]> alo aixtřas lo že
```

### v2037 current-grammar bridge line

```text
rkwal ti kui ; <FRAMED:SIT[ hleňfó-évvroal- köi ti hlušh-otilöehui kè esälu’u «objet petit a» hü ]> iňň aixtřas to ke
```

### Important reading note

`kè` is the low-toned Form-1 personal-reference adjunct for `2m:CMP` in the current grammar. If tone cannot be reliably represented in a working plain-text environment, temporarily display this token as:

```text
<2m:CMP(current)>  // surface target: kè
```

---

## 3. Migration table

| v2036 token | v2036 analysis | v2037 token | current-grammar analysis | Status |
|---|---|---|---|---|
| `li` | `1m:AFF` using old `l` = speaker | `ti` | `t` = 1m, `i` = AFF | frozen |
| `sëi` | `2m:STM` using old `s` = addressee and old STM | `kui` | `k` = 2m, `ui` = DER stimulus/circumstantial cause | frozen |
| `sou` | `2m:ITP` using old `s`, old `ou` ITP | `köi` | `k` = 2m, `öi` = ITP | frozen |
| second `li` | `1m:AFF` | `ti` | `t` = 1m, `i` = AFF | frozen |
| `hlušh-otilöehëi` | host object in old STM | `hlušh-otilöehui` | host object in DER, the non-agential stimulus/cause of affective state | frozen as case correction, not as full host finality |
| `sue` | `2m:CMP` with old `s`, old `ue` | `kè` | `k` = 2m, short-form personal CMP = `e` with low-tone shift | frozen with orthographic warning |
| `alo` | old `CTR₁` affixual adjunct | `iňň` | current `CTR` suffix `-ňň`, Degree 1 via Type-1 `i` | frozen provisionally as affixual adjunct |
| `lo` | `1m:ERG` old `l` | `to` | `t` = 1m, `o` = ERG | frozen |
| `že` | detrimental 2m ABS | `ke` | `k` = 2m, `e` = ABS; detriment is lexical in `XTŘ₂` for now | frozen |

---

## 4. Why `DER` replaces the old `STM` lane

The previous passes used `STM`/Stimulative for “you” and for the “something more than you” as affective trigger. The current public grammar still recognizes **stimulus** as a semantic role, but the case label that carries this role is **DER / Derivative**, not a separate primary `STM` case. DER has two functions relevant here:

1. abstract or circumstantial cause/reason, often glossable as “because of / due to / owing to”; and
2. the non-agential, unconscious, or non-deliberate **stimulus** of an affective mental state, emotion, or autonomic sensory experience.

That is a much better fit for Lacan’s *objet petit a* than a flat object case. In the inner clause, the “something more than you” is not simply something acted on. It is the cause-like lure/stimulus through which the speaker’s attachment/desire is hooked.

Therefore:

```text
sëi  →  kui
hlušh-otilöehëi  →  hlušh-otilöehui
```

The host itself is **not** declared fully final. Only its current-case correction is frozen.

---

## 5. Personal-reference correction band

Current public grammar gives the short-form single-referent personal adjunct as:

```text
C1 + Vc
```

For this passage, the relevant referents are:

```text
t = 1m, monadic speaker
k = 2m, monadic addressee
```

So:

```text
ti   = 1m:AFFECTIVE
kui  = 2m:DERIVATIVE / stimulus-cause
köi  = 2m:INTERPRETATIVE
kè   = 2m:COMPARATIVE, low-toned Form-1
ke   = 2m:ABSOLUTIVE
to   = 1m:ERGATIVE
```

This removes the old-series `l/s/ž` mapping for 1m/2m/detrimental-2m. Current grammar does not preserve that same neutral-vs-detrimental monadic addressee opposition in the basic Table-26 way v2031 assumed. For now, the final harm in “I mutilate you” is carried by the violent root/stem `XTŘ₂` and the ABS patient `ke`. If needed later, a dedicated suffix or other construction can reintroduce explicit affectedness/detriment.

---

## 6. `in you` remains Interpretative, but its surface changes

The old `sou` was conceptually good but formally outdated. “I love **in you** something more than you” is still best read as a subjective/interpretational access point rather than a literal locative interior. So the **case choice** ITP remains.

But current ITP is `öi`, and current 2m is `k`, so:

```text
sou  →  köi
```

Gloss:

```text
köi = through/in you, as the interpretive context or subjective locus
```

This preserves the key Lacanian distinction:

```text
köi = “in/through you”
kè  = “than you”
kui / ...ui = stimulus/cause of the affective state
```

---

## 7. Comparative “than you”: `kè`

The v2026 form `sue` must be retired under the current system. Current personal-reference short forms use Table-28 personal-reference case vowels rather than simply borrowing the formative case vowel. For `CMP`, Table 28 gives short-form `e`; because this is in the second comparative-associated block of personal-reference cases, falling-tone referents shift to low tone in Form 1.

Thus:

```text
2m + CMP  →  k + low-tone e  →  kè
```

The working line will use `kè`, but this remains the most notation-sensitive update in v2037. If a future pass decides tone cannot be safely represented in the project’s plain-text orthography, the line should display `<2m:CMP(current)>` until the orthographic policy is settled.

---

## 8. Contrastive wrapper: `alo` → `iňň`

v2035’s `alo` came from an older `CTR = -l` analysis. Current public grammar lists `CTR` as the coordinative suffix `-ňň`, with Degree 1 meaning approximately:

```text
still / nevertheless / however — despite seemingly inherent conflict or contradiction
```

That is exactly the force needed for Lacan’s “I love you, **but** … I mutilate you.” It is not merely additive contrast; it is contradiction-bearing opposition.

Using the Type-1 Degree-1 vowel from the suffix table:

```text
CTR/1  = i + ňň  →  iňň
```

I keep it as an affixual adjunct before `aixtřas` rather than internalizing it into the final predicate, because the intended force scopes over the whole final predication:

```text
iňň aixtřas to ke
≈ nevertheless/however, I mutilate you
```

This is frozen provisionally as an adjunct-surface decision. A later pass may still decide whether it should be integrated into the final formative or kept adjacent.

---

## 9. Situative frame policy

The frame remains analytical in the line:

```text
<FRAMED:SIT[ ... ]>
```

But the current target for SIT is now clear:

```text
SIT = oi
```

The old design-document `SIT = oa` is retired. A future pass must solve how `SIT` is hosted on the frame’s verbal formative, most likely on `hleňfó-évvroal-`, while also ensuring the required **FRAMED relation stress**. For now, v2037 only says:

```text
FRAMED:SIT = current case-frame with Vc:oi + framed stress
```

It does not yet claim the final surface of `hleňfó-évvroal-` under frame hosting.

---

## 10. Frame-end marker correction

v2030’s caution was right, but the old “TPF-family `-n`” note should be replaced. Current grammar gives:

```text
TPF = -t’
Degree 2 = end of frame
```

Using the normal Type-1 degree vowel, an isolated suffixal target would be:

```text
TPF/2  →  -öt’
```

However, v2037 still does **not** attach this to `hü`. The reason is unchanged: `hü` is already performing the specialized carrier-ending job for the foreign phrase. Before attaching a frame-end suffix to it, we need a hostability audit: can `hü` bear a regular VxC suffix in this construction, or should the frame-end marker attach to another final word / be avoided because the bracket boundary is clear?

Frozen policy:

```text
No automatic hü + -öt’ yet.
```

---

## 11. Carrier-root note: do not force the old RLT carrier yet

The current line leaves this segment unchanged:

```text
esälu’u «objet petit a» hü
```

This is deliberate. The foreign-phrase carrier construction is a special-construction problem, and v2037 is already doing a broad migration of referential/case constants. I do **not** want to pretend we have fully revalidated the carrier under current public grammar in the same pass.

That said, the next carrier audit should test whether the old RLT-cased carrier `esälu’u` should remain, or whether the current **ESSIVE** (`ea`) is a better fit for the foreign label/name “objet petit a.” Current ESS identifies the role or name by which a noun is known or contextually identified. That sounds promising for a named theoretical construct, but it must be checked against the carrier construction itself, not merely the general case definition.

Next-pass candidate:

```text
esälu’u  →  <carrier:foreign-name + ESS?>
```

No change is frozen here in v2037.

---

## 12. Updated morpheme-gloss sketch

```text
rkwal       ti       kui
love.RKW₁   1m.AFF   2m.DER/STIMULUS-CAUSE

<FRAMED:SIT[
  hleňfó-évvroal-   köi      ti       hlušh-otilöehui    kè       esälu’u «objet petit a» hü
  inexplicably?     2m.ITP   1m.AFF   salient-more.host.DER 2m.CMP carrier foreign-phrase end
]>

iňň       aixtřas    to       ke
CTR/1      maim.XTŘ₂  1m.ERG   2m.ABS
```

Approximate back-translation:

> I love you; but/nevertheless, given the inexplicable fact that I love, through/in you, the salient something-more-than-you — “objet petit a” — I maim you.

---

## 13. What this pass supersedes

v2037 prospectively supersedes these earlier frozen decisions:

- v2026 `sue` as `2m:CMP` → replaced by `kè`.
- v2027 `hlušh-otilöehëi` as old `STM` host → corrected to `...ui` DER lane.
- v2028 `sou` as `2m:ITP` → replaced by `köi`.
- v2029 `li` as `1m:AFF` → replaced by `ti`.
- v2031 `lo že` as 1m ERG + detrimental 2m ABS → replaced by `to ke`.
- v2035 `alo` as old `CTR₁` → replaced by `iňň`.
- v2036 `rkwal li sëi` → replaced by `rkwal ti kui`.

It does **not** yet supersede:

- `rkwal` itself as the RKW₁ verbal surface;
- `hleňfó-évvroal-` as the inexplicable/unknowability wrapper;
- `hlušh-otilöeh-` as the “salient something-more” host stem;
- `esälu’u ... hü` as the foreign carrier construction;
- `aixtřas` as the maiming predicate surface.

Those require separate follow-up audits.

---

## 14. Next best pass

The next revision should probably be:

```text
q_lacan_carrier_current_ess_vs_rlt_and_frame_end_hostability_pass_v2038
```

It should solve two linked problems:

1. whether `objet petit a` as a foreign theoretical name should use the old RLT carrier case or a current ESS/name-role analysis; and
2. whether the final frame boundary should remain implicit, attach `TPF/2 = -öt’` somewhere, or be avoided because `hü` already closes the foreign phrase and the main predicate resumes immediately after.

---

## 15. Working revision summary

v2037 is a correction pass, not a stylistic pass. Its main contribution is to stop the project from compounding older design-document referential/case constants. The new line to carry forward is:

```text
rkwal ti kui ; <FRAMED:SIT[ hleňfó-évvroal- köi ti hlušh-otilöehui kè esälu’u «objet petit a» hü ]> iňň aixtřas to ke
```

This is now the local base for v2038.

