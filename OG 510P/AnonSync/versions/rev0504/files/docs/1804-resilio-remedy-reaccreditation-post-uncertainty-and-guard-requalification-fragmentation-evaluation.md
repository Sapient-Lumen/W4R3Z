# Resilio remedy reaccreditation, post-uncertainty recovery, and guard-requalification fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials do expose several ingredients an operator can use when trying to recover confidence after watch uncertainty, fallback discovery, or case re-fence.
That candor is valuable.

The strongest ingredients from the present contract are:

- current `My files don't sync` docs still say missing file-change notifications may require restart or touching files so Sync rescans, and some folder-tree problems may require removing and re-adding the folder so it re-indexes
- current `Sync Service Troubleshooting on Windows` docs still say some service-side setups learn updates only during rescan or upon restart, and some service-identity changes require restart plus re-add and re-share or re-connect of folders
- current `Collecting debug logs manually` docs still say meaningful evidence may require enabling debug logging, restarting Sync, reproducing the issue, and waiting for logs to accumulate
- current `Settings on mobile platforms` docs still say restoring Android notification behavior matters because disabling notifications can lower Sync priority and stop background work
- current `Resilio Sync change log` still says there is an option to force rescan a sync share and keeps recording fixes for blank, stale, or incomplete UI states
- current `Sync Preferences` docs still say debug logging and notification behavior are settings rather than a typed requalification flow

## Where the current contract still fragments

The problem is not that Resilio lacks recovery moves.
The problem is that it still lacks a first-class, case-scoped **remedy-reaccreditation** object.

Today the operator can often infer only weaker facts such as:

- the app was restarted
- a rescan or force rescan ran
- logs were collected after the fact
- a mobile or service-side signal path was restored
- a share was re-added or re-connected
- the visible UI stopped looking stale

Those are useful operational recovery moves.
They are not the same as an explicit answer to `is this previously uncertain or re-fenced case now honestly requalified for guarded ordinary life again?`

## Why that matters for AnonSync

AnonSync needs to support stronger post-recovery claims than `the warning went away` or `we rescanned and things look normal now`.
It needs to support claims such as:

- the case stayed fail-safe until required-cohort proof returned, so discharge did not silently revive on the first healthy-looking signal
- a named lane regained signal, but required-cohort requalification is still blocked because one blind lane remains unresolved
- the original uncertainty cause was remediated, the guard was re-proved inside budget, and only then did ordinary-life re-entry become honest again
- the case re-entered guarded ordinary life under tighter budgets and sticky scar conditions rather than reverting to pre-incident optimism
- manual re-entry authority was required because the fail-safe had escalated into a full re-fence rather than a soft narrowing

AnonSync therefore needs a first-class object for **remedy reaccreditation** rather than merely borrowing restart, rescan, reconnect, logging, or notification language.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `after this discharged case went uncertain or was re-fenced, when is it honestly safe to re-enter guarded ordinary life again?` — only by making the operator combine several operational surfaces:

- restart and touch-file troubleshooting
- rescan or force-rescan recovery
- service restart and service-identity reconnection steps
- optional debug logging and delayed evidence collection
- restored notification or background behavior on mobile
- change-log evidence that stale visible surfaces and rescan support still matter

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model the following as separate public truths:

- uncertainty still active
- fail-safe contained but requalification not yet started
- signal path restored but cause not yet remediated
- cause remediated but proof stale
- named-cohort requalification only
- required-cohort requalification pending re-entry authority
- re-entry authorized with sticky scars
- re-entry authorized under tighter watch budget
- re-entry blocked pending fresh end-to-end drill
- requalification collapsed and case remains fenced

That is why this tranche adds five more first-class pages: **Remedy-reaccreditation contract sheet**, **Remedy-reaccreditation review**, **Remedy-reaccreditation proof**, **Remedy-reaccreditation timeline**, and **Remedy-reaccreditation lineage receipt**.
