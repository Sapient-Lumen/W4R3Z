# _cube_lacan_current_public_spine_refactor_v2042

**Date:** 2026-05-25  
**Project:** Ithkuil translation of the love text — Lacan local cube  
**Purpose:** active-spine ledger and current-public grammar refactor overlay

---

## 1. Why this cube ledger exists

The Lacan subproject now contains over a hundred exploratory files. That is useful provenance, but it also creates a navigation problem: old design-document-era surfaces sit beside current-public repairs, and filename duplicates from Unicode export quirks sit beside their intended Unicode originals.

This ledger does not delete history. It defines the active local cube:

```text
source burden × grammatical role × surface token × status
```

The active current-public line after v2042 is:

```text
rkwal ti kui ; evvróîlošš köi ti hlušh-otilöehui kè upealöt’ «objet petit a» ; iňň aixtřas to ke
```

---

## 2. Active current-public spine

| Source burden | Active surface | Working role | Status after v2042 |
|---|---:|---|---|
| I love you | `rkwal ti kui` | opening affective-love predication | active, medium-high confidence |
| because / given that | `evvróîlošš ...` | SIT case-frame head with FRAMED stress | active, high confidence |
| inexplicably | `-ošš` in `evvróîlošš` | RSN/7 “for no reason” on VVR₂ state | active, high confidence |
| I love / am infatuated | `evvróîlošš ... ti ...` | VVR₂ affective/obsessive state + 1m AFF | active, medium-high confidence |
| in you / through you | `köi` | 2m Interpretative | active, medium confidence |
| something more than you | `hlušh-otilöehui kè` | salient host with SUR/DER comparison shell + 2m CMP | active, needs audit |
| objet petit a | `upealöt’ «objet petit a»` | abstract carrier, ESS, TPF/2 frame-end; foreign phrase unchanged | active, high confidence but hostability caveat |
| but / nevertheless | `iňň` | CTR/1 adversative wrapper | active, medium-high confidence |
| I mutilate you | `aixtřas to ke` | DYN XTŘ₂ maim + 1m ERG + 2m ABS | active, medium-high confidence |

---

## 3. Current-public migration spine

The active branch begins at v2037:

```text
v2037  current referential/case migration
v2038  current -P- carrier migration and retirement of written hü
v2039  current SIT = oi + FRAMED stress
v2040  retirement of hleňfó as non-current / wrong-root burden
v2041  RSN/7 repair for “inexplicably”
v2042  TPF/2 frame-end marker on the carrier construction + cube refactor
```

Everything before v2037 remains provenance unless a later pass explicitly revives it under current public grammar.

---

## 4. Deprecated / superseded surface map

| Deprecated form | Superseded by | Reason |
|---:|---:|---|
| `li` | `ti` | current 1m referential migration |
| `sëi` | `kui` | current 2m DER/stimulus migration |
| `sou` | `köi` | current 2m Interpretative migration |
| `sue` | `kè` | current 2m Comparative migration |
| `hlušh-otilöehëi` | `hlušh-otilöehui` | current DER replaces older STM route for affective stimulus/cause |
| `esälu’u ... hü` | `upeal ...` then `upealöt’ ...` | current `-P-` carrier root; no written `hü` carrier-end particle |
| `hleňfó-évvroal-` | `evvróîlošš` | `ŇF` no longer means mystery/puzzle; SIT now `oi`; RSN/7 handles inexplicability |
| `alo` | `iňň` | current CTR suffix migration |
| `lo že` | `to ke` | current 1m/2m referential migration |

---

## 5. Filename hygiene notes

The archive contains three Unicode-escaped duplicate filename artifacts from earlier generation:

```text
q_lacan_final_predicate_xt#U253c#U00d62_dynamic_function_vr_ai_skeleton_pass_v2032.md
q_lacan_final_predicate_oblique_case_shell_aixt#U253c#U00d6a_pass_v2033.md
q_lacan_final_predicate_ca_prx_uniplex_csl_surface_aixt#U253c#U00d6as_pass_v2034.md
```

The intended Unicode originals also exist:

```text
q_lacan_final_predicate_xtř2_dynamic_function_vr_ai_skeleton_pass_v2032.md
q_lacan_final_predicate_oblique_case_shell_aixtřa_pass_v2033.md
q_lacan_final_predicate_ca_prx_uniplex_csl_surface_aixtřas_pass_v2034.md
```

Policy after v2042:

```text
Keep duplicates as archival-only; cite/use the Unicode originals when discussing those passes.
Do not create new #U... filenames.
Do not delete old files inside revision archives unless a separate archival-cleanup pass is requested.
```

---

## 6. Next audit targets ranked

### Priority A — host nucleus

```text
hlušh-otilöehui kè
```

Reason: the outer cases are current, but the root/prehead burden should be rechecked against the current public lexicon and current rules for incorporation / adjunct behavior. This is the densest remaining legacy inheritance.

### Priority B — opening love predicate

```text
rkwal ti kui
```

Reason: current referentials are fixed, but the semantic split between affective love, goodwill-love, and volitional love remains project-wide. Lacan’s opener can stay affective; the broader essay will probably require a different love-root or argument structure for goodwill.

### Priority C — final clause assertion package

```text
iňň aixtřas to ke
```

Reason: the lexical and participant structure is good enough for the local quote, but a later pass should decide whether this psychoanalytic quotation needs explicit validation/bias or can rely on defaults.

---

## 7. Working rule for future Lacan passes

Future passes should begin from the v2042 current-public line unless the pass explicitly says it is reopening a prior branch:

```text
rkwal ti kui ; evvróîlošš köi ti hlušh-otilöehui kè upealöt’ «objet petit a» ; iňň aixtřas to ke
```

Do not reintroduce the following without a full current-public derivation:

```text
esälu’u
hü
hleňfó
sou / sue / li / lo / že
alo
```

The most valuable next lexical audit is `hlušh-otilöehui`.
