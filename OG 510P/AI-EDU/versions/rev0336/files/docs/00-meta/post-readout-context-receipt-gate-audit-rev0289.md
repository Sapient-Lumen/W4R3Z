# rev0289 post-readout context receipt gate audit

## What changed

`rev0289` turns the post-readout new-context handoff into an executable gate. When a `post-readout-recheck.json` records `new_owner_context_available`, the router now requires a scratch-local `post-readout-context-receipt.json` before returned-owner intake can run.

## Risk corrected

The risky pattern was stale lineage. `rev0288` correctly held new owner context outside the recheck, but the returned-CSV branch could still fall back to the latest old contact clock. That would make a late post-readout context look like a first-contact reply and lose the source chain that discovered it.

## New executable firebreak

The context receipt records only the source recheck path, the recheck hash, the returned CSV/source-packet hash and size, column presence, reviewer role count, and explicit no-expansion/no-public/no-service/no-lifecycle/no-closure confirmations. It does not copy owner answers or make evidence claims.

`owner-reply-intake` now accepts exactly one provenance source: either `SOURCE_CONTACT_STATUS` for ordinary first/reask replies, or `SOURCE_POST_READOUT_CONTEXT_RECEIPT` for post-readout new context. The workbench seed revalidates the same provenance chain and blocks mixed or missing sources.

## What this still does not do

This gate does not contact an owner, import a real `SRC2+` packet, accept evidence, edit service records, move lifecycle state, create custody, support public language, or close `FT-0181`. It only prevents post-readout owner context from being laundered through an old clock or a local recheck summary.

## Correct next move

Use `owner-field-next`. If the router sees new post-readout owner context without a matching receipt, it emits `owner-post-readout-context-receipt`. After the receipt exists, rerun the router with the same CSV and execute the emitted `owner-reply-intake ... SOURCE_POST_READOUT_CONTEXT_RECEIPT=...` command.
