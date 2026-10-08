# Principal mapping proof page — service account, identity compatibility, and apply ceiling interface spec

## Purpose

This page exists because `permission sync enabled` is not proof.
The operator needs a place to inspect whether the current runtime and target identity space can actually uphold the selected metadata contract.

The page answers:

> who is applying the metadata, how are principals mapped, what part is proved versus assumed, and what is the strongest safe sentence right now?

## Required sections

1. **Runtime principal witness**
2. **Identity-space mapping witness**
3. **Target apply witness**
4. **Confidence and expiry**
5. **Current apply ceiling**
6. **Next safe actions**

## 1) Runtime principal witness

Show:

- service / process identity
- elevation class
- origin of proof (`live runtime`, `imported receipt`, `operator attestation`, `unknown`)
- freshness timestamp

The page must not hide whether the runtime is merely assumed to be elevated.

## 2) Identity-space mapping witness

Show the current mapping mode:

- `same-domain SID resolution`
- `same uid/gid by numeric ID`
- `same uid/gid by name only`
- `default ACL fallback`
- `preserve-only no native mapping`
- `mapping absent`
- `unknown`

Also show any mismatches:

- missing user
- missing group
- owner unresolved
- domain mismatch
- target known to rewrite locally instead

## 3) Target apply witness

Show:

- target filesystem / storage class
- native permission family supported here or not
- whether metadata can be preserved without apply
- whether later application on another target is expected
- any active inheritance rewrite policy

## 4) Confidence and expiry

Every proof row needs:

- `fresh`
- `stale but probably still valid`
- `expired`
- `contradicted`
- `never proved`

The page should degrade the overall verdict when any load-bearing witness is stale.

## 5) Current apply ceiling

This section must publish one verdict:

- `full-apply-proved`
- `full-apply-plausible-not-proved`
- `partial-apply-only`
- `preserve-only`
- `rewrite-locally`
- `blocked`
- `unknown`

Examples of strongest safe sentences:

- `Current runtime can apply NTFS ACL here now.`
- `Current runtime can carry ACL intent, but this target cannot apply it natively here.`
- `Current runtime can sync bytes, but permission application is blocked by unresolved target identity mapping.`

## 6) Next safe actions

Allowed actions:

- `Refresh runtime proof`
- `Refresh target identity mapping`
- `Inspect missing principals`
- `Review safer metadata mode`
- `Export proof receipt`

Forbidden actions:

- silently upgrading `plausible` to `proved`
- treating imported historical proof as live runtime truth without freshness labeling

## Object model

### Principal mapping proof

- `principal_mapping_proof_id`
- `subject_ref`
- `seat_ref`
- `runtime_principal_ref`
- `runtime_principal_class`
- `mapping_mode`
- `target_compatibility_class`
- `proof_rows[]`
- `overall_apply_ceiling`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `fresh_until`
- `source_basis_refs[]`

## CLI shape

```text
anonsync metadata proof show --subject finance-share --seat branch-gw-1
```

## Result

AnonSync should make principal and identity-space assumptions visible enough that a metadata promise can be audited before the run fails.
