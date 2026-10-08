# Ignore-divergence review page — peer-local rules, retroactivity, and size mismatch

## Purpose

Review any disputed ignore decision before the interface says a subject is simply `ignored`, `excluded`, or `missing from size`.
This page exists because a local ignore rule, a shared policy, and a later-edited rule are not the same truth.

## This review must distinguish

- ignore rule present before first scan;
- ignore rule added after the folder was already scanned;
- path hidden by pattern on this peer only;
- path likely to be treated differently on another peer because ignore lists are not guaranteed to match;
- object structurally known while actual file delivery is excluded;
- count/size mismatch caused by peer-local ignore divergence rather than replication failure.

## Inputs the page must collect

### Rule facts

- exact rule text
- source file of the rule
- case-sensitivity posture
- path separator basis for this platform
- whether wildcard matching is involved
- whether root-only matching is involved

### Timing facts

- whether the rule existed before first scan of the folder
- whether the rule was added later
- whether the folder structure had already been indexed and announced before the rule changed
- whether Sync has re-read the rule file yet
- whether a restart or periodic rescan is still outstanding

### Divergence facts

- whether other peers are known to have the same rule set
- whether same-share size mismatch is currently explained by rule divergence
- whether the reviewed subject exists physically on disk despite current exclusion
- whether the reviewed subject was previously replicated before the rule changed

## Decision ladder

### Branch 1 — pre-scan exclusion

Use this branch when the rule clearly existed before the folder was first indexed.
The page should show:

- strongest exclusion basis
- whether any peer divergence remains possible
- that pre-scan local exclusion is still weaker than global purge proof

### Branch 2 — post-scan exclusion with structural survivor

Use this branch when the rule was added after the folder was already known.
The page should show:

- that structure may remain known and may already have been propagated
- whether bytes are now excluded only prospectively
- that `ignored now` does not prove `never announced`

### Branch 3 — peer-local divergence

Use this branch when other peers may not share the same rule set.
The page should show:

- scope divergence class
- whether share size differences are therefore expected
- whether the object may still exist or arrive on peers without the same exclusion
- that this is policy divergence, not necessarily a sync fault

### Branch 4 — stale rule-read / not yet re-evaluated

Use this branch when the rule file changed but Sync may not yet have re-read it.
The page should show:

- current re-read certainty
- whether restart or rescan is still pending
- that present exclusion claims are provisional until re-evaluation occurs

## Required warnings

- `Same share` is weaker than `same peer-local scope`.
- `Ignored now` is weaker than `never announced before`.
- `Missing from Size` is weaker than `not present on disk`.
- `Rule changed on disk` is weaker than `rule already took effect`.
- `Path not delivered here` is weaker than `path impossible elsewhere`.

## Review outputs

- ignore-basis class
- retroactivity class
- peer-divergence class
- count-mismatch explanation
- next proof action if current certainty is incomplete

