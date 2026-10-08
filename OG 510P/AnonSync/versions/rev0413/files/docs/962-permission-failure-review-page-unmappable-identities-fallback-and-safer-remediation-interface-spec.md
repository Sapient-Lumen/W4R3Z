# Permission failure review page — unmappable identities, fallback, and safer remediation interface spec

## Purpose

This page exists for the moment when bytes can still move, but metadata truth cannot be cleanly upheld.

The operator should not have to infer from one error string whether the safe response is:

- change the runtime principal
- repair target identity mappings
- choose a weaker metadata mode
- continue with preserve-only
- stop and recreate

## Review order

1. **Failure class**
2. **What still succeeded**
3. **What specifically failed**
4. **Risk of continuing**
5. **Remediation ladder**
6. **Rejected shortcuts**
7. **Receipt promise**

## 1) Failure class

Use exactly one primary class:

- `principal-insufficient`
- `owner-application-insufficient`
- `target-identity-unmappable`
- `cross-platform-non-native-apply`
- `inheritance-rewrite-mismatch`
- `preseed-ownership-ambiguity`
- `unknown`

## 2) What still succeeded

Show separately:

- byte transfer succeeded or not
- metadata preservation succeeded or not
- metadata application succeeded or not
- local rewrite succeeded or not

Examples:

- `bytes arrived; permission application blocked`
- `bytes arrived; ACL preserved for later NTFS application`

## 3) What specifically failed

List concrete unmet facts:

- runtime was not Local System
- runtime lacked domain-admin rights
- target missing matching uid/gid
- target missing matching user/group name
- target filesystem cannot apply selected metadata family
- reference source missing for pre-seeded RW merge

## 4) Risk of continuing

Show what the operator must not overclaim if they continue:

- `reject saying owner matched`
- `reject saying permissions are identical on all peers`
- `reject saying cross-platform destination enforces source ACL`

## 5) Remediation ladder

Ordered from least disruptive to most disruptive:

1. `Refresh proof / re-test mapping`
2. `Change runtime principal`
3. `Repair target user/group registration`
4. `Downgrade to preserve-only`
5. `Rewrite to local inheritance`
6. `Downgrade to bytes-only`
7. `Create successor with a different metadata contract`

For each rung show:

- expected effect
- whether bytes are touched
- whether subject recreation is required
- whether stronger claims become available afterward

## 6) Rejected shortcuts

Always include a short section for shortcuts the product refuses:

- `continue and still claim full metadata parity`
- `auto-create unknown target principals silently`
- `auto-escalate service account privileges`
- `rewrite ownership silently without receipt`

## 7) Receipt promise

The receipt must keep:

- failure class
- failed assumptions
- chosen remediation rung
- resulting metadata ceiling
- stronger rejected sentence

## Object model

### Permission failure review

- `permission_failure_review_id`
- `subject_ref`
- `seat_ref`
- `failure_class`
- `byte_outcome`
- `metadata_preservation_outcome`
- `metadata_application_outcome`
- `failed_assumptions[]`
- `risk_summary`
- `remediation_rungs[]`
- `chosen_rung_ref` nullable
- `resulting_metadata_ceiling`
- `blocked_stronger_sentence`

## CLI shape

```text
anonsync metadata failure review --subject finance-share --seat branch-gw-1
```

## Result

AnonSync should treat permission failures as a first-class repair family instead of a side-effect note under generic job errors.
