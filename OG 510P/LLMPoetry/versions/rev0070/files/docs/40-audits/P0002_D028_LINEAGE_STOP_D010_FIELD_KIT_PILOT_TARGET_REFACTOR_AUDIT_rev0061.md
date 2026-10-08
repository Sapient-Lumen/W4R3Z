# P0002-D028 lineage stop / D010 field kit / pilot-target refactor audit — rev0061

## The risky unfinished work

The cube's largest completion risk was no longer missing infrastructure. It was the P0002 rewrite treadmill. D010 remained the strongest internally held poem while D011 through D028 accumulated eighteen successor drafts, each with fresh source pressure and fresh validation surfaces. The lineage could keep moving without producing the one thing the mission still lacked: a disclosed reading by someone outside the drafting loop.

Rev0061 applies the stop rule. The later-turn review of D028 is `revise_not_promote_stop_lineage`. D028 remains the terminal current head for provenance, but no D029 is made. Operational attention returns to D010.

## Literary result

D028's source premise is strong; its poem is not. It breaks a Station Datum definition into emphatic fragments, adds exact station objects, and closes by explaining the definition again. In two presentation orders, D010 wins the internal pairwise comparison because scene and image carry the measurement problem rather than the apparatus explaining it.

The decision is deliberately narrower than “D028 is worthless” or “D010 is proven.” D028 is dead **as a successor**. D010 is merely the best preserved internal candidate and now has to face a reader.

## The refactor

`tools/check_pilot_queue.py` previously inherited a hidden assumption: the recommended pilot's target should be the global current head. That is appropriate for a cold review but wrong for a preserved-candidate evidence launch. It made the strongest candidate operationally unreachable unless the lineage head was rewritten or falsified.

The checker now declares pilot kind explicitly:

- `cold_review` targets the global head;
- `reader_evidence_launch` may target a preserved non-current candidate, but must say so, carry a complete verification path, preserve an empty response log, and pass field-kit checks;
- legacy current-head pilots remain supported.

The pilot-target check is wired into the main validator and doctor. This is a correction to work routing, not another doctrine layer.

## The field kit

`tools/build_reader_field_kit.py` deterministically creates one offline ZIP containing:

- a single disclosure-first HTML page with the exact D010 poem body;
- the response form and local JSON download in that page;
- a short operator README;
- a manifest with the current D010 hash and explicit exclusions.

The page makes no network request, loads no remote asset, asks for no identity or demographics, embeds no evaluator rubric or source packet, and creates no response until a real reader completes it. The returned JSON matches the existing hardened intake tool. The response log remains empty.

## Why the research changes the test

Porter and Machery's poetry study makes blind human-passing a weak objective: non-expert readers could not reliably identify authorship and often preferred the AI poems. More recent work reports that disclosure itself can shift perceptions, and that literary evaluation varies substantially with reader profile and evaluative criteria. SPHERE's evaluation-card framing reinforces the need to state what is evaluated, how, by whom, when, and how validation occurs. Those findings do not prove anything about D010; they support a disclosure-first, reader-sensitive, fully documented field encounter rather than a disguised-authorship test.

## Completion boundary

Rev0061 completes the internal decision and the runnable handoff. It does **not** complete the reader test. The next real event must occur outside the cube: one person reads the disclosure and poem, returns a non-identifying JSON file, and the operator runs the dry-run intake before append.

## Validation

Before packaging, the integrated validator passed 6,536 checks with zero failures; doctor passed 42 checks with zero failures; and the dedicated pilot/field-kit checker passed its complete target, offline, hash, payload, and empty-log checks. The final archive is revalidated after extraction.

## Non-claim

Rev0061 records an internal later-turn judgment and launch tooling only. P0002-D028 is not promoted, P0002-D010 has no external response yet, and field-kit readiness is not reader evidence, admission, publication clearance, or a live NOAA value.
