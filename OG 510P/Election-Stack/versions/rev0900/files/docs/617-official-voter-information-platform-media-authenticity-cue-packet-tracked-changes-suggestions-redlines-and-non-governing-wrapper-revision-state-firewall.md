# 617 — Official voter-information platform media authenticity-cue packet tracked changes, suggestions, redlines, and non-governing wrapper-revision-state firewall

**Track:** Shared / Public surfaces

This document covers a narrow packet-wrapper problem:
**later packets can preserve tracked changes, suggestions, redlines, replace-text marks, insert/delete proposals, or similar visible revision-state layers around same-route detached derivatives, and later readers can start mistaking those revision proposals for source text, source revision, source approval, or the packet's governing member.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/490-official-voter-information-browser-managed-reading-lists-offline-saved-pages-and-web-archive-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/595-official-voter-information-platform-media-authenticity-cue-text-extracts-transcript-caption-ocr-derivatives-and-non-carried-cue-firewall.md`
- `docs/598-official-voter-information-platform-media-authenticity-cue-metadata-extracts-title-description-chapter-list-derivatives-and-non-carried-cue-firewall.md`
- `docs/600-official-voter-information-platform-media-authenticity-cue-detached-derivative-family-quickmap-mixed-packets-and-anti-fragmentation-firewall.md`
- `docs/602-official-voter-information-platform-media-authenticity-cue-packet-synopses-forwarding-comments-speaker-notes-and-non-governing-wrapper-summary-firewall.md`
- `docs/603-official-voter-information-platform-media-authenticity-cue-packet-markup-highlights-arrows-and-non-governing-wrapper-emphasis-firewall.md`
- `docs/616-official-voter-information-platform-media-authenticity-cue-packet-review-threads-comment-replies-and-non-governing-wrapper-discourse-firewall.md`

## What this is for

Use `617` when a later packet preserves or reenacts a **revision-proposal layer** around same-route detached derivatives:
- suggestion-mode insertions and deletions,
- tracked changes,
- redlines,
- replace-text / insert-text / strikethrough-text correction marks,
- accept/reject preview states,
- or similar visible revision proposals.

Those revision states are real packet facts and should be preserved honestly.
But they are still **later wrapper-added revision posture**, not automatic proof of:
- current source wording,
- current source revision,
- office approval,
- office rejection,
- or the packet's governing member.

`617` exists so maintainers can say:
**this packet preserved a later revision-state layer around a same-route detached derivative, and that layer mattered for how later readers interpreted the packet, but the revision layer itself does not govern the packet and does not silently rewrite source provenance.**

## Why this is distinct

`602` asks whether later synopsis prose or forwarding summary text drifted into source-language territory.

`603` asks whether later markup or emphasis changed how the packet looked — highlights, arrows, circles, underlines, comment anchors, zoom lenses, or similar annotation posture.

`616` asks whether later attached review discourse — comment threads, replies, task-like notes, or resolution history — drifted into source wording, source endorsement, source resolution, or governing-member proof.

`595` and `598` ask whether the decisive surviving artifact is still copied source text or copied source metadata.

`600` asks how to route a mixed same-route packet when several detached derivatives coexist and no single `595–599` member clearly dominates.

`617` asks a different question:
**did a later packet add or preserve a visible revision-state layer — suggestions, tracked changes, redlines, or text-correction proposals — and did later readers start overreading that layer as if it were source text, an adopted source revision, or the packet's governing member?**

If the real problem is only review conversation, use `616`.
If the real problem is only markup/emphasis, use `603`.
If the real problem is only summary prose, use `602`.
If the real problem is still copied source text or metadata, use `595` or `598`.
Use `617` only when the missing distinction is **revision-state posture itself**.

## Decision test

Use `617` when all three conditions hold:

1. later evidence preserves or reenacts a **visible revision-state layer** around same-route detached derivatives — for example suggestion-mode insertions/deletions, tracked changes, redlines, replace-text notes, insert-text notes, or similar proposed revision markers;
2. that layer is **later wrapper-added proposal state or review-edit posture**, not the source route's already-adopted current wording; and
3. later readers are drifting toward treating that layer as if it proved **source text, source revision, accepted office change, or the governing member**.

If any condition fails, keep the packet under the narrower doc that already owns the real problem.
If the surviving packet is still mainly copied source text or copied source metadata with some visible revision marks around it, keep the detached derivative in `595–600`, keep any markup fact in `603`, keep any review-conversation fact in `616`, and add one bounded `617` revision-state note.

## Keep source-derived content and wrapper-added revision state separate

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and current media head (`194`, `369`, `529`, `530`);
2. **surviving detached derivative** — which `595–599` member, if any, the packet actually preserved;
3. **family routing** — whether the packet needed `600` because no single detached derivative dominated;
4. **source-derived text** — transcript/caption/OCR or other copied route text (`595`);
5. **source-derived metadata** — labels copied from the official route itself (`598`);
6. **wrapper-added summary prose** — forwarding comments, share messages, speaker notes, memo-body summaries, or similar longer later packet narrative (`602`);
7. **wrapper-added markup/emphasis** — highlight boxes, circles, arrows, underlines, zoom lenses, or similar later visual emphasis (`603`);
8. **wrapper-added review discourse** — comment-thread bodies, replies, task assignments, or similar later attached discussion (`616`);
9. **wrapper-added revision state** — suggestions, tracked changes, redlines, replace-text proposals, insert-text proposals, deletion proposals, or accept/reject preview posture (`617`);
10. **carrier wrapper** — slide deck, PDF memo, doc comment layer, saved page, web archive, issue ticket, or other transport context (`490`, `600`);
11. **assembly state** — whether later materials also fused several observations into one stronger-looking posture (`591`).

That separation matters because later packets can otherwise make two different mistakes:
- treating proposed changes as if they were already-adopted source wording, or
- letting the existence of a redline/suggestion layer become evidence that the packet itself governs the source route.

`617` exists so the archive can keep that later visible revision layer **truthful but non-governing**.

## Minimal wrapper-revision-state note grammar

When wrapper revision state matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; governing_member=<595|596|597|598|599|600|none>; wrapper_revision_kind=<suggestion|tracked_change|redline|replace_text_markup|insert_text_markup|deletion_markup|accept_reject_preview|mixed|unknown>; revision_anchor_relation=<whole_member|member_region|slide|page|object|text_range|mixed|unknown>; wrapper_revision_origin=<later_wrapper_added|reviewer_added|editor_added|imported_review_layer|mixed|unknown>; proposal_status=<pending|accepted_preview|rejected_preview|mixed|unknown>; treat_revision_as_source_text=<forbid>; treat_revision_as_adopted_source_revision=<forbid>; treat_revision_as_governing_member=<forbid>; carrier_wrapper=<doc_comment_layer|slide_deck|pdf_memo|saved_page|web_archive|ticket|email_thread|none>; cite_default=<head|fallback anchor>; use_617_when=<revision_state_changed_reading>; promote_wrapper_revision_state=<no>; basis=<why the later visible revision layer needed one bounded note>`

This is a note contract, not a new schema.
It exists so packets and summaries can say “this later packet also carried a visible revision-proposal layer” without minting a new detached-derivative member or silently rewriting source text, accepted revision state, or governance.

## Typical uses

1. **Suggestion-mode overread**
   A later document packet shows inserted and deleted text in suggestion mode and later readers start retelling those proposed edits as if they were already-adopted official wording.
2. **Tracked-changes overread**
   A later packet preserves tracked changes or redlines and later readers start treating that revision posture as if it were the current source text rather than a review-state layer.
3. **Accept/reject preview overread**
   A later packet previews how the document would look with or without tracked changes and later readers start narrating that preview as if it proved what the source officially adopted.
4. **PDF text-correction markup overread**
   A later PDF packet carries replace-text, insert-text, or strikethrough correction marks and later readers start treating those proposed corrections as if they were source-native edits.
5. **Imported revision-layer overread**
   A later packet converts Office tracked changes into another editor's suggestion layer and later readers start treating the converted proposal state as if it were the packet's governing member.

## When not to use this

Do **not** use `617` when:
- the decisive issue is still packet synopsis or forwarding summary prose (`602`),
- the decisive issue is still wrapper-added emphasis or annotation (`603`),
- the decisive issue is still wrapper-added review-thread discourse (`616`),
- the decisive issue is still copied source text (`595`),
- the decisive issue is still copied source metadata (`598`),
- the decisive issue is still a mixed detached-derivative packet with no dominant member (`600`),
- the decisive problem is still print/save/offline/web-archive authority or portability (`490`),
- or the decisive problem is still cross-state composite assembly (`591`).

If deleting the visible proposal layer leaves an ordinary summary-prose problem, markup problem, review-discourse problem, or mixed-packet problem, use the narrower doc and omit `617`.
If deleting it would erase **why a later tracked-change / suggestion / redline layer changed the way the packet was being read or retold**, `617` is probably right.

## Promotion rule

Future media additions should usually **not** be promoted just because a later packet carried tracked changes, suggestions, redlines, replace-text marks, or accept/reject preview posture.
Tighten `602`, `603`, `600`, `616`, or `617` first.
Only add another numbered doc when repeated revision-state mistakes still cannot be expressed as:
- one governing `595–599` member,
- or a mixed-packet routing note under `600`,
- plus one bounded wrapper-revision-state note under `617`.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless wrapper-revision-state drift still persists after this compact bridge exists.

## Sources

- Google Docs Editors Help — Suggest edits in Google Docs. (xref: `google_docs_suggest_edits_help_page`)
- Microsoft Support — Track changes in Word. (xref: `microsoft_track_changes_word_help_page`)
- Adobe Acrobat Help — Annotations: Text Correction Commenting Tools Update. (xref: `adobe_acrobat_text_correction_commenting_tools_update_help_page`)
