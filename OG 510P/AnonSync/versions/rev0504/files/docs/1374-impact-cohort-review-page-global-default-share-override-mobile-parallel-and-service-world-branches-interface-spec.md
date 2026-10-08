# Impact-cohort review page — global default, share override, mobile parallel, and service-world branches

## Review question

> what cohort does this mutation actually govern, and what nearby cohort is a false friend that must not be overclaimed?

## Mandatory review branches

### 1) Global-default branch

Use when the operator edits a default that other subjects may inherit.
Required outputs:

- exact inherited cohort reached now
- exact detached cohort excluded now
- future-subject inheritance rule
- explicit statement whether `inherit` and `explicit none` are separate values here

### 2) Share-override branch

Use when the operator edits one focused share.
Required outputs:

- focused subject identity
- whether this creates, edits, or removes a detach
- whether the resulting state is `inherit` or explicit local value
- whether same-looking values elsewhere remain untouched

### 3) Mobile-parallel branch

Use when mobile has a same-looking setting that is only device-local or share-local there.
Required outputs:

- mobile platform and route
- whether this is parallel rather than shared authority
- exact cohort reached on that device
- stronger desktop/global sentence refused

### 4) Startup-config branch

Use when `sync.conf` or another startup-authored route owns the value.
Required outputs:

- config file location
- current runtime vs next-startup cohort
- whether interactive runtime surfaces are only witnesses
- whether new storage path or config world changes the membership base

### 5) Service-world branch

Use when service installation, service storage, or service principal defines the governed world.
Required outputs:

- service world identity
- migrated continuity vs clean-install fork
- whether shares survive from prior world or require re-share
- exact cohort reachable from this route

### 6) Reattach branch

Use when the operator wants a detached subject to follow the default again.
Required outputs:

- proof that the subject is detached now
- exact action that restores inheritance
- whether matching value alone is insufficient
- next default change that would prove reattachment

### 7) Unknown-membership branch

Use when the product cannot yet prove the full cohort.
Required outputs:

- missing witness
- provisional inclusion/exclusion ceiling
- blocked stronger sentence
- exact evidence needed to unblock batch change

## False-friend cases the page must catch

- `None` on one share when the subject is actually detached rather than inheriting
- `global default changed` when several shares are manually protected
- `same setting on mobile` when that lane is only local parallel configuration
- `service install` when the real fork is between migrated world and clean world
- `config written` when the running world has not adopted that cohort yet

## Required review outputs

Every impact-cohort review must end with:

- canonical setting id
- mutation class
- target cohort verdict
- detached exceptions verdict
- inherit-vs-explicit verdict
- nearest false-friend cohort
- activation rung
- blocked stronger sentence