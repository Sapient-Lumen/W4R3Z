# Lacan Situative frame-boundary and no-premature-TPF-`-n` pass v2030 — 2026-05-21

## English target span

This checkpoint continues directly from v2029.

Target sentence:

> **I love you, but, because inexplicably I love in you something more than you—the objet petit a—I mutilate you.**

The v2029 middle-clause fragment was:

```text
hleňfó-évvroal- sou li hlušh-otilöehëi sue esälu’u «objet petit a» hü
```

The v2029 sentence-level readable working line was:

```text
<RKW₁> <1m> <2m> ; <FRAMED:SIT hleňfó-évvroal- sou li STM:[hlušh-otilöehëi sue esälu’u «objet petit a» hü]> <CTR₁> <XTŘ₂> <1m> <2m>
```

The continuation point named by v2029 was the framed `SIT`/because-wrapper and the case-frame boundary question:

```text
<FRAMED:SIT hleňfó-évvroal- sou li ...>
```

This pass does **not** reopen the already-frozen inner middle-clause participant work:

```text
sou                  = <2m:ITP>
li                   = <1m:AFF>
hlušh-otilöehëi      = salient something-more-than-you as STM
sue                  = <2m:CMP>
esälu’u ... hü        = RLT carrier + foreign phrase + carrier end
```

It audits how that whole packet is enclosed as the `SIT`-framed background of the final violent predicate.

## Official grammar pressure consulted

New Ithkuil treats subordinate / relative clauses as **case-frames**: the embedded sentence is treated as a noun participant and is marked for case like a noun.  The case of the case-frame is shown on the verbal formative, and the framed formative takes **FRAMED** relation, signaled by antepenultimate stress in the New Ithkuil description.

The current official `SIT` value is `-oa`; it identifies a noun or case-frame as the **background context** for a clause.  This is the source of the archive's long-standing `FRAMED:SIT` wrapper.

The grammar also allows, where useful, a special TPF-family `-n` affix on the final word of a case-frame to signal the end of the frame when the frame is inserted at the beginning or middle of a main sentence.

## What this checkpoint now freezes

### 1. the middle clause remains **SIT**, not a stronger causal frame

The English source has the word:

```text
because
```

That makes a direct causal reading tempting.
Nevertheless, this checkpoint keeps the already-established `SIT` analysis rather than promoting the frame to a heavier cause/reason frame.

The reason is that the source is not only giving a simple cause for mutilation.  It is staging a pathological explanation whose central content is itself opaque:

```text
because inexplicably I love in you something more than you — the objet petit a —
```

Earlier passes correctly rendered the onset as:

```text
given the puzzling fact that ...
```

not:

```text
because of the direct cause that ...
```

The difference matters.  The Lacan line does not say:

> I mutilate you because this determinate reason rationally explains my action.

It says, more nearly:

> Given the puzzling background fact that through you I am obsessively attached to a cause-like excess beyond you, I mutilate you.

So the archive keeps:

```text
FRAMED:SIT
```

as the case-frame wrapper.

### 2. the frame boundary should now be treated as a live surface problem, not as merely punctuation

Before v2030, the readable line used angle brackets:

```text
<FRAMED:SIT hleňfó-évvroal- sou li ... hü>
```

That was useful, but the archive should no longer treat the closing bracket as a mere editorial convenience.
The frame is inserted before the final violent predicate:

```text
[case-frame] <CTR₁> <XTŘ₂> <1m> <2m>
```

So the frame boundary is grammatically consequential.
If the boundary is not recognized, the final predicate could be misread as still inside the background clause.

This pass therefore freezes the boundary as a **real active frontier**:

```text
... hü  ||FRAME-END||  <CTR₁> <XTŘ₂> <1m> <2m>
```

However, it does not yet claim that the frame-end frontier has a final overt Ithkuil surface.

### 3. no TPF `-n` is added yet

The tempting next surface move would be:

```text
... hü + TPF/-n
```

or some equivalent:

```text
... hü-n
```

This checkpoint explicitly refuses that as premature.

The official syntax allows a final-word `-n` boundary marker when helpful, but the current last visible in-frame element is not an ordinary fully audited formative.  It is the carrier-end marker:

```text
hü
```

which is already doing one specialized job:

```text
hü = close the foreign/proper phrase governed by esälu’u
```

If the archive immediately forces a second job onto the same element:

```text
hü = carrier-end + case-frame-end host
```

it risks hiding two unresolved questions:

1. whether `hü` itself can cleanly host the TPF-family end-of-frame affix in the intended construction, and
2. whether the final hostable in-frame word should instead be the carrier formative, the carrier-end marker, or some other post-carrier boundary strategy.

Therefore v2030 freezes:

```text
FRAME-END = semantically and syntactically required boundary
TPF/-n    = not yet surfaced
```

This is not anti-canonical conservatism.  It is canonical caution: do not manufacture a surface form before the exact hostability of the terminal carrier material has been audited.

### 4. `hü` remains only the carrier-end marker

This pass keeps the v2023 decision intact:

```text
esälu’u «objet petit a» hü
```

Here:

```text
esälu’u       = carrier formative, RLT-cased
«objet petit a» = foreign/proper phrase
hü            = carrier-end marker
```

The new policy is:

```text
hü closes the foreign phrase.
It does not yet close the entire SIT case-frame in the overt running form.
```

That prevents a future reader from misparsing the current line as if the archive had already solved the carrier-end-plus-frame-end collision.

### 5. the active readable line should now show the frame closure explicitly, but analytically

The v2029 line used this compact representation:

```text
<RKW₁> <1m> <2m> ; <FRAMED:SIT hleňfó-évvroal- sou li STM:[hlušh-otilöehëi sue esälu’u «objet petit a» hü]> <CTR₁> <XTŘ₂> <1m> <2m>
```

The v2030 line should now prefer this boundary-audited version:

```text
<RKW₁> <1m> <2m> ; <FRAMED:SIT[ hleňfó-évvroal- sou li hlušh-otilöehëi sue esälu’u «objet petit a» hü ]> <CTR₁> <XTŘ₂> <1m> <2m>
```

The square brackets inside the `FRAMED:SIT[...]` wrapper are not final punctuation.  They mean:

```text
this is the whole in-frame clause whose end must be kept outside the following contrastive mutilation predicate
```

The old `STM:[...]` label is also no longer needed in the running control line because v2027 has already built `STM` into the word:

```text
hlušh-otilöehëi
```

So v2030 both:

- makes the frame boundary more explicit, and
- removes a redundant object-side scaffolding label.

### 6. why the final violent predicate stays outside the frame

The final predicate begins after the frame closes:

```text
<CTR₁> <XTŘ₂> <1m> <2m>
```

This must not be pulled inside the `SIT` frame.

If it were inside, the sentence would become something like:

> I love you, but, given the puzzling fact that through you I am attached to the excess and that I mutilate you, ...

That is not the source structure.  The source has:

```text
I love you,
but,
[background: because/in view of the fact that ...],
I mutilate you.
```

Therefore the frame must end before the contrastive violent predicate begins.

### 7. the boundary also preserves the rhetorical asymmetry of the source

The source has three `I` roles:

```text
I love you
I love in you something more than you
I mutilate you
```

The archive has already split them grammatically:

```text
opening I       = ordinary love predicate participant
middle I        = AFF experiencer of obsessive attachment
final I         = agent of mutilation, still unresolved but outside the frame
```

If the frame boundary is blurred, the third `I` can begin to look like another internal participant in the puzzling affective frame.  That would flatten the sentence's ethical violence.

The final `I` must emerge after the frame, not inside it.

So v2030 treats the frame boundary as rhetorically essential, not merely syntactic housekeeping.

## Rejected or demoted alternatives

### A. add TPF `-n` directly to `hü`

Rejected for now.
`hü` already closes the foreign carrier phrase.  It should not also be forced to carry the case-frame-ending burden until the grammar of affixing that carrier-end element has been separately audited.

### B. leave the boundary only as the old external angle bracket

Demoted.
The old notation was serviceable, but after v2029 the in-frame clause is now concrete enough that the boundary deserves explicit analytical visibility.

### C. reopen `SIT` in favor of a more causal case-frame

Rejected.
The source's **because** is real, but the archive's `SIT + ŇF₂` analysis captures the line's “given the puzzling fact that” better than a direct-cause frame would.

### D. pull `<CTR₁> <XTŘ₂> <1m> <2m>` inside the frame

Rejected.
That would make the final mutilation part of the background explanatory clause instead of the contrastive main predicate licensed by that background.

## Updated active state after v2030

### Middle clause fragment

```text
hleňfó-évvroal- sou li hlušh-otilöehëi sue esälu’u «objet petit a» hü
```

No segmental change is made inside the fragment.
The gain is the boundary policy that governs what comes after it.

### Sentence-level readable working line

```text
<RKW₁> <1m> <2m> ; <FRAMED:SIT[ hleňfó-évvroal- sou li hlušh-otilöehëi sue esälu’u «objet petit a» hü ]> <CTR₁> <XTŘ₂> <1m> <2m>
```

### Smooth control-reread

> I love you, but, given the puzzling fact that through you I undergo obsessive attachment toward the salient something-more-than-you, namely the _objet petit a_, I mutilate you.

## Provisional takeaway

Carry forward the middle frame as:

```text
<FRAMED:SIT[ hleňfó-évvroal- sou li hlušh-otilöehëi sue esälu’u «objet petit a» hü ]>
```

not as:

```text
<FRAMED:SIT hleňfó-évvroal- sou li STM:[hlušh-otilöehëi sue esälu’u «objet petit a» hü]>
```

and not yet as:

```text
<FRAMED:SIT hleňfó-évvroal- sou li hlušh-otilöehëi sue esälu’u «objet petit a» hü-n>
```

The frame-end is now a named frontier.  The overt `-n` implementation remains a future pass.

## Next clean continuation point

The next highest-value move is probably to leave the middle frame intact and begin the final clause:

```text
<CTR₁> <XTŘ₂> <1m> <2m>
```

The first narrow question there should be:

```text
<1m> in final mutilation clause = ERGATIVE agent?
<2m> in final mutilation clause = ABSOLUTIVE patient?
```

The likely candidate pair is:

```text
lo  = 1m/ERG
sa  = 2m/ABS
```

but that should be checked in its own pass because the final predicate's root/stem choice and the ethical force of detriment may put pressure on simple neutral referentials.
