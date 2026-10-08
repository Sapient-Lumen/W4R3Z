# rev0294 post-readout context receipt gate audit

The post-readout context receipt gate remains current. A recheck that says new
owner context exists is not enough to intake a new CSV/source packet. The router
must first link the actual returned context file to the current recheck through a
scratch-local context receipt.

`rev0294` changes only the command after that receipt exists. Instead of routing
straight to direct intake, the router now emits `owner-returned-reply-work` with
`SOURCE_POST_READOUT_CONTEXT_RECEIPT`. That helper reuses the same source/hash
checks, runs intake, and creates a workbench seed only when the returned context
is `PROCEED-STAGED`.

The receipt still does not copy owner answers. It does not accept evidence,
change a service record, authorize public language, move lifecycle state, create
custody, or close `FT-0181`.

## Correct post-readout sequence

1. Record the post-readout action dispatch.
2. Record the due-date recheck.
3. If new owner context exists, record the context receipt against the same CSV.
4. Rerun `owner-field-next` with the same actual returned context CSV.
5. Execute the emitted `owner-returned-reply-work` command.

Do not intake from receipt prose, old contact clocks, or a different CSV hash.
