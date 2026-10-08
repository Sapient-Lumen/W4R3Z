# Release gates

Use these questions before promoting a workflow to a stronger support tier.

## Experimental gate
- Is there at least one real surface attempt?
- Did the workflow complete once end-to-end?
- Is there a support bundle or equivalent evidence artifact?

## Provisional gate
- Is the workflow repeatable enough to leave consistent structured outputs?
- Is current drift known?
- Is the support record current and lane-specific?

## Supported gate
- Does the workflow have current evidence, comparison history, and release-gate artifacts?
- Can a future implementer inspect the proof without rerunning everything?
- Are caveats and unsupported edge cases documented?

## Important rule

A support tier is not a vibe. It is a statement about evidence quality and repeatability.


## Support publication boundary

Support-bundle queue state is not publication authority. `support-publish-gate` is the machine-readable boundary that decides whether a bundle may honestly clear `published-ready` or `published`.
