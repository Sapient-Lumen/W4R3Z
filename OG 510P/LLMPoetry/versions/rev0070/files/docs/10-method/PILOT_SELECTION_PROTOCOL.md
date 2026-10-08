# P0001 pilot selection protocol

P0001 should not be selected by taste alone. It should be selected for what it can teach the cube.

## Selection weights

A first pilot should score well on:

1. **machine-native necessity**: machine origin makes the form stronger rather than embarrassing;
2. **verification path**: constraints can be checked with available tools or a visible manual ladder;
3. **anti-imitation safety**: the form does not reward copying Fable specimen weather;
4. **reader access**: the poem can still be read as a poem, not only as a technical artifact;
5. **disclosure survival**: authorship disclosure should deepen or at least not ruin the poem;
6. **receipt cost**: the pilot should not require weeks of infrastructure before a draft exists.

## Current recommendation

Use `PILOT-0001`, the prompt-reply diptych, unless the human explicitly prefers a baseline poem first. It makes machine interaction load-bearing, keeps verification tractable, and avoids requiring unavailable embeddings or tokenizer internals.

## P0001 preflight

Before drafting:

- run and log the web pulse;
- create `poems/P0001/metadata.json` before the draft;
- choose exactly one primary pilot from `registries/pilot_queue.json`;
- create source and quote receipt placeholders if any factual/source claims appear;
- run the anti-imitation firewall after drafting;
- do not judge the poem in the same turn.


## rev0012 note

The human selected high-risk machine-native work. P0001 now exists as `draft_001` using `FORM-branch-selector-diptych`; it is unjudged and cannot be promoted in the drafting turn.
