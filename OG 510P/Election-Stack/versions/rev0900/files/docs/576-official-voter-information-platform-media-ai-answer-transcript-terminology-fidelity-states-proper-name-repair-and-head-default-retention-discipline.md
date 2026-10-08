# 576 — Official voter-information platform media AI-answer transcript-terminology-fidelity states, proper-name repair, and head/default-retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- player-native AI answer modules as public-answer boundaries (`499`),
- AI-pane open/summary/answer-visible state inside the same object (`562`),
- AI question-thread carryover and prompt-origin ownership inside the same object (`563`),
- AI-answer output-language state inside the same object (`564`),
- AI-answer grounding state inside the same object (`565`),
- AI-answer source-basis / provenance posture inside the same object (`566`),
- AI-answer outcome / disposition posture inside the same object (`567`),
- AI-answer eligibility / rollout gating inside the same object (`570`),
- AI-answer input-sufficiency / transcript-floor posture inside the same object (`572`),
- AI-answer governing-transcript precedence inside the same object (`573`),
- AI-answer transcript-language alignment inside the same object (`575`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, the AI-answer surface, pane/thread/language/provenance/governing-transcript posture are already understood, but the governing transcript may still misrecognize candidate names, office titles, acronyms, or domain terms — or later be repaired through manual transcript correction or product-level vocabulary help — and that terminology-fidelity fact starts to look like a new head, a safer citation target, or a reason to retain long transcript bodies or long custom vocabulary lists?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/499-official-voter-information-platform-ai-video-summaries-ask-this-video-and-answer-module-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/545-official-voter-information-platform-media-text-track-selection-states-caption-subtitle-language-picks-and-head-default-retention-discipline.md`
- `docs/562-official-voter-information-platform-media-ai-answer-pane-states-summary-focus-and-head-default-retention-discipline.md`
- `docs/563-official-voter-information-platform-media-ai-question-thread-states-follow-up-carryover-and-prompt-history-minimization-discipline.md`
- `docs/564-official-voter-information-platform-media-ai-answer-output-language-states-translated-response-mode-and-head-default-retention-discipline.md`
- `docs/572-official-voter-information-platform-media-ai-answer-input-sufficiency-states-transcript-floors-and-content-fit-discipline.md`
- `docs/573-official-voter-information-platform-media-ai-answer-governing-transcript-states-original-transcript-precedence-and-displayed-translation-noninheritance-discipline.md`
- `docs/575-official-voter-information-platform-media-ai-answer-transcript-language-alignment-states-spoken-source-match-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that transcript-driven answer quality can depend on **term-level fidelity**, not just whether a transcript exists or whether its language matches the audio.
Vimeo's current custom-vocabulary guidance says the feature improves transcription and translation accuracy, helps the AI more accurately recognize words specific to the team or company when transcribing the video's original language, and is not a translation dictionary.
Microsoft's current Clipchamp autocaptions guidance says misspelled or incorrect transcript words can be rewritten manually, and its current Copilot-in-Clipchamp help says the player answers based on information in the transcript.
(xref: `vimeo_custom_vocabulary_help_page`; xref: `microsoft_clipchamp_autocaptions_support_page`; xref: `microsoft_clipchamp_copilot_video_player_support_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one AI pane already governed by `499` and `562`,
- one governing transcript posture already governed by `573`,
- one transcript-language-alignment posture already governed by `575`,
- one answer whose practical reliability still turns on whether names, offices, acronyms, or domain terms were recognized correctly in that governing transcript,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they flatten terminology-fidelity problems into `575` as if every bad proper noun were really a language-match problem,
- they flatten terminology drift into `573` as if the only question were which transcript variant governed,
- they promote a corrected transcript word or vocabulary-setting change into a fresher head,
- they retain too much transcript text or too much of a custom vocabulary list just to preserve one bounded term-recognition fact,
- or they omit the terminology-fidelity fact entirely and later cannot explain why two same-object AI answers diverged on names, acronyms, or election-specific terminology even though the same object, same pane, and same governing transcript still controlled.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object AI-answer transcript-terminology fidelity + bounded repair/minimization**.

## This is not the same thing as `545`, `572`, `573`, or `575`

`545` governs selected caption/subtitle tracks and text-track visibility around the same media object.

`572` governs whether the AI layer cleared a published minimum transcript-length, duration, or content-fit floor.

`573` governs which transcript variant actually governed the answer when originals, regenerations, or translations coexist.

`575` governs whether the governing transcript language matched the spoken source language.

`576` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **AI-answer transcript-terminology-fidelity note** such as `proper_name_or_term_drift_suspected`, `terminology_repaired_or_manually_corrected`, or `term_specific_accuracy_controls_disclosed`,
- while recording that the same governing transcript still controlled but its term-level recognition quality or repair posture mattered **without** creating a new route, a new head, or a safer citation target than the controlling head.

If the decisive issue is which text track was selected or displayed, use `545`.
If the decisive issue is whether the AI layer cleared a minimum floor or best-fit profile, use `572`.
If the decisive issue is which transcript variant governed, use `573`.
If the decisive issue is whether the governing transcript language matched the spoken source, use `575`.
Use `576` only when the surface and transcript-governance posture are already understood but the archive still needs to classify the **same-object transcript terminology/proper-name fidelity state** inside an already-governed media chain.

## Default rule: preserve terminology-fidelity truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **AI-answer transcript-terminology-fidelity note** when all of the following hold:

1. **The underlying object is still the same.**
   Playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is term-level transcript fidelity or repair posture, not a new publication.**
   The decisive fact is that names, offices, acronyms, jargon, or domain terms in the governing transcript appeared doubtful, acceptable, or later repaired through bounded transcript correction or vocabulary help.
3. **Treating the terminology issue as a new route would mislead.**
   A reader could mistake a transcript-word repair, corrected proper noun, or vocabulary-control disclosure for a fresher head, a reviewed replacement publication, or a safer citation target than the controlling head.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The terminology-fidelity fact still matters.**
   The archive would lose useful truth if it omitted whether same-object AI-answer reliability turned on correct recognition of names, acronyms, or domain terms.
6. **The archive can stay minimal.**
   The needed fact can be preserved through one canonical token and one short basis sentence without retaining long transcript bodies, long correction histories, or long custom vocabulary lists.

When those conditions hold, keep the head/default under `529–530`, keep any selected text-track fact under `545`, keep any AI-answer boundary fact under `499`, keep any answer-language fact under `564`, keep any floor/fit fact under `572`, keep any governing-transcript fact under `573`, keep any spoken-source language-alignment fact under `575`, and add one `576` terminology-fidelity note.
Do **not** silently promote transcript word repair or vocabulary-help posture into the chain's current head.

## Minimal AI-answer transcript-terminology-fidelity grammar

When a same-object chain has a current head or fallback anchor plus a meaningful transcript-terminology-fidelity state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; terminology_fidelity_state=<terminology_repaired_or_manually_corrected|proper_name_or_term_drift_suspected|term_specific_accuracy_controls_disclosed|terminology_fidelity_acceptable|terminology_fidelity_unclear|unknown>; terminology_basis=<clipchamp_manual_transcript_edit_guidance|vimeo_custom_vocabulary_guidance|transcript_answer_depends_on_term_accuracy|capture_only|no_published_rule|unknown>; cite_default=<head|fallback anchor>; cite_terminology_when=<claim about proper-name or domain-term recognition, transcript correction, or why terminology fidelity did not become the safer citation lane>; retain_vocab_lists=<no>; basis=<why terminology fidelity mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **whether transcript term recognition itself mattered to the AI answer** without making one corrected name, one acronym repair, or one vocabulary-control disclosure sound like a new route or a better citation target than the head.

`header_pick_order=<terminology_repaired_or_manually_corrected|proper_name_or_term_drift_suspected|term_specific_accuracy_controls_disclosed|terminology_fidelity_acceptable|terminology_fidelity_unclear|unknown>`

`detail_pick_order=<terminology_repaired_or_manually_corrected|proper_name_or_term_drift_suspected|term_specific_accuracy_controls_disclosed|terminology_fidelity_acceptable|terminology_fidelity_unclear|unknown>`

For packet headers, that winner order means the carried `576` token should prefer the most reconstructively specific terminology-fidelity fact: a known repair outranks suspected term drift, which outranks a merely disclosed term-accuracy control, which outranks acceptable or unclear fidelity posture. If one extra same-doc `576` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `576`.

## When to use an AI-answer transcript-terminology-fidelity note

Typical uses include:

1. **Proper-name or acronym drift on the same governing transcript**
   The same head still controls, but later reviewers need to preserve that a candidate name, precinct acronym, office title, or other domain term appeared mistranscribed and likely shaped the AI answer.
2. **Manual repair or transcript correction happened without a new head**
   The same governing transcript lane still controls, but the archive needs to preserve that term-level errors were later corrected manually without treating that repair like a new publication.
3. **Custom vocabulary or term-specific controls matter**
   The same object stayed current, and later reviewers need to preserve that published vocabulary controls were relevant to interpreting why transcript-based answers improved or stabilized.
4. **Term fidelity looked acceptable and that matters for comparison**
   The same object stayed current, and later reviewers need to preserve that domain-term recognition did not appear to be the reason for disagreement across captures.
5. **No published terminology rule and no clear observed drift**
   The same object stayed current, but the archive still needs to say term-level transcript fidelity was unclear rather than pretending that language match or transcript existence resolved the whole issue.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `576` terminology-fidelity note SHOULD be cited only when the later claim is specifically about:
- whether names, offices, acronyms, or other domain terms were recognized correctly in the governing transcript,
- whether term-level transcript drift likely shaped the observed AI answer,
- whether term-level transcript problems were later repaired or bounded by vocabulary controls,
- or why terminology fidelity did **not** outrank the head-first citation rule.

That means `576` preserves one honest transcript-terminology exception to head-first citation without letting a corrected word, a term list, or a vocabulary-setting disclosure quietly become the archive's present-tense authority object.

## Minimization rule

Reviewers SHOULD preserve only the smallest terminology-fidelity fact needed for later reconstruction.
Usually that means:
- one canonical `terminology_fidelity_state` token,
- one short basis sentence,
- and at most one short example term only when the exact term is load-bearing.

Do **not** preserve long transcript bodies, long correction histories, or long custom vocabulary lists unless another archive rule independently requires a short excerpt.

## When not to use this

Do **not** use `576` when:
- the decisive issue is the selected caption/subtitle track rather than transcript term fidelity — use `545`,
- the decisive issue is whether the AI layer cleared a minimum floor or best-fit profile — use `572`,
- the decisive issue is which transcript variant governed rather than whether names or domain terms were recognized well inside that governing transcript — use `573`,
- the decisive issue is spoken-source / transcript-language mismatch rather than term-level recognition — use `575`,
- or the archive is trying to preserve long transcript corrections, bulk vocabulary exports, or long lists of terms when one compact token and one short basis note are enough.

If deleting the terminology-fidelity fact would erase **why the same governing transcript produced a name/jargon-sensitive answer that looked wrong, repaired, or unusually trustworthy**, `576` is probably the right companion.
If deleting that fact would erase only which language was shown, which transcript variant governed, or whether the AI surface existed at all, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_budget_hearing_apr_2026; head=public Vimeo replay packet; terminology_fidelity_state=proper_name_or_term_drift_suspected; terminology_basis=transcript_answer_depends_on_term_accuracy; cite_default=head; cite_terminology_when=proving that the governing transcript appeared to misrecognize one office-specific acronym and that this likely shaped the visible AI answer without turning transcript terminology drift into the controlling route; retain_vocab_lists=no; basis=the same replay stayed current while transcript-driven AI behavior still hinged on one election-domain term being recognized correctly`
- `chain=county_board_budget_hearing_apr_2026; head=published Microsoft 365 recording packet; terminology_fidelity_state=terminology_repaired_or_manually_corrected; terminology_basis=clipchamp_manual_transcript_edit_guidance; cite_default=head; cite_terminology_when=proving that a misspelled candidate surname in the governing transcript was later corrected manually without treating the correction workflow as a new head or reviewed publication; retain_vocab_lists=no; basis=the same recording stayed current while the platform's own transcript-edit path made one term-level repair salient`
- `chain=regional_training_replay_apr_2026; head=public Vimeo replay packet; terminology_fidelity_state=term_specific_accuracy_controls_disclosed; terminology_basis=vimeo_custom_vocabulary_guidance; cite_default=head; cite_terminology_when=proving that the product's own custom-vocabulary controls were relevant to interpreting why transcript-based answers handled organization-specific names better without treating the vocabulary settings page as the citation-safe head; retain_vocab_lists=no; basis=the same replay stayed current while Vimeo documented team-specific terminology controls for transcription and translation accuracy`

## Tie-breaker when reviewers ask “if the transcript term was corrected, why isn't that the head?”

Ask three questions:
- does the terminology-fidelity note prove **how well the governing transcript recognized names or domain terms** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to transcript correction or vocabulary settings instead of the controlling head,
- and can the needed reconstruction stay truthful without preserving long transcript bodies or long vocabulary lists?

If yes, keep current control under `529–530`, preserve any selected text-track fact under `545`, preserve any floor/fit fact under `572`, preserve any governing-transcript fact under `573`, preserve any transcript-language-alignment fact under `575`, and record the terminology-fidelity state under `576`.
Do **not** let transcript terminology drift or repair absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same transcript-driven AI answer looked sensitive to a misspelled name, a corrected acronym, or a disclosed custom vocabulary list.
Tighten `576` first.
Only add another numbered surface when the ambiguity is really about a new public route, a new authority object, or a new transcript/governing surface rather than about **AI-answer transcript terminology fidelity inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that terminology-fidelity cases still drift between `545`, `572`, `573`, and `575` after this compact note contract exists.
