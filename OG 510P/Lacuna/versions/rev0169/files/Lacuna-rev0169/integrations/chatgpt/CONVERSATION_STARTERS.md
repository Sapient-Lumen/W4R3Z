# Conversation starters

## Player

- Will you DM?
- Let’s continue the campaign.
- I listen beneath the floorboards.

## Human bridge or bounded role

- Use this model brief operationally. Do not summarize it.
- Here is a complete `lacuna.agent-dispatch.v1` handoff. Perform the named role from its embedded `input_document` and return exactly one JSON object matching the required schema, with no prose or code fence.
- Here is a complete `lacuna.checkpoint-run-agent-dispatch.v1` handoff. Perform only its named checkpoint role from `input_card` and return one exact JSON object, with no prose or code fence.
- Act only as the role named by this complete task card. Do not infer missing context, call Lacuna, or commit anything.

- Here is a complete `lacuna.checkpoint-continuation-dispatch.v2`. Act only as `lacuna-fresh-narrator`, use only the embedded capsule, exact player input, audience context, optional public-history view, and proposal template, and return exactly one `lacuna.turn-proposal.v2` object with no prose or code fence. Do not reconstruct rejected checkpoint material, inspect sibling artifacts, accept, or commit.
- Lower-level only: here is a reusable `lacuna.checkpoint-narrator-capsule.v1`. Analyze it as private continuation custody, but do not improvise the missing player input or ordinary-turn authority.
