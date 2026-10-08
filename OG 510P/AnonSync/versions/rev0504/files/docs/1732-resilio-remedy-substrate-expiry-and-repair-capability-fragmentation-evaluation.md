# Resilio remedy-substrate, expiry, and repair-capability fragmentation evaluation

## What current Resilio gets right

Current official Resilio docs are candid that `something bad happened` and `we can still repair it cleanly` are not the same truth.
That honesty is useful.

The most valuable ingredients from the present contract are:

- Archive is real, device-local, and bounded by default retention rather than infinite repair memory
- restoration is manual rather than magically self-healing
- archive coverage can be disabled or limited by maximum file-size settings
- mobile and platform differences matter, including Android internal-memory-only Archive controls, Android SD-card gaps, and no Archive access on iOS
- placeholder states can preserve names without preserving content
- placeholder-only meshes can degrade into ghost/no-source residue where nobody actually has the file anymore
- low free space can block further downloading and patched files may need temporary extra space before landing
- background/runtime limits on mobile can delay or prevent the repair lane from actually executing

## Where the current contract still fragments

The problem is not that Resilio hides repair limits.
The problem is that the repair substrate is scattered across archive docs, placeholder docs, mobile docs, no-source warnings, and storage-threshold docs instead of being owned as one remedy object.

Today the operator can often infer only weaker facts such as:

- some peer once had an archived prior version
- some placeholder still remembers that a file name existed
- some mobile device might not expose or sustain the relevant repair lane
- some copy might still exist but only on a peer that is offline, placeholder-only, or no longer source-capable
- some restore might be possible only if enough free space exists for temporary patching
- some repair opportunity may silently decay when archive TTL expires or version-size ceilings exclude the needed file

Those are useful evidence inputs.
They are not a first-class cure-capability contract.

## Why that matters for AnonSync

AnonSync is trying to make stronger semantic claims than `compensation is owed` or `something might still be recoverable somewhere`.
It needs to support claims such as:

- repair material still exists on named peers and remains within retention horizon
- only partial cure is still possible because the needed version exceeded versioning limits
- semantic repair is blocked because only placeholders remain and no source peer still has bytes
- manual restoration is possible on desktop but not honestly available on a required mobile cohort
- a remedy lane looked plausible yesterday but collapsed today because retention expired or free-space gating prevented the restore path
- compensation remains owed, but the product must no longer overstate that clean cure is available

Resilio gives clues for these judgments.
It does not provide the judgment object itself.

## Non-clone conclusion

So the line stays hard:

- borrow Resilio's candor about Archive horizons, manual restore, versioning ceilings, placeholder-only states, ghost/no-source residue, mobile/platform gaps, and free-space limits
- do not clone a model where repair-material sufficiency, source survivorship, expiry risk, and cure capability still have to be reconstructed from scattered KB pages and operational warnings

AnonSync should therefore own a dedicated page family for remedy substrate rather than treating `compensation owed` as if it already implied `clean cure still available`.
