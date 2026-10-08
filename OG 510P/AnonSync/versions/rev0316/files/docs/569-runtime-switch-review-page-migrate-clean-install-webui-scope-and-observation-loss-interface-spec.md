# Runtime switch review page — migrate, clean install, WebUI scope, and observation loss

## Purpose

Prevent runtime-envelope changes from looking like harmless toggles.
This page rewrites the requested runtime switch into the exact control-plane mutation it really is.

## Inputs

- current runtime profile review
- storage lineage forecast
- operator requested change
- available migration paths
- control reach settings
- observation / shell affordance evidence

## Questions this page must answer

1. What switch did the operator ask for?
2. What exact runtime mutation will the product perform?
3. Is this a migrate-in-place, fresh-profile install, principal swap, reach widening, or retirement action?
4. What surfaces or capabilities will narrow or widen as a side effect?
5. What sentence may the product honestly say afterward?

## Mutation classes

1. `migrate existing profile into service`
2. `fresh service install on same host`
3. `service principal swap`
4. `config-mode root relocation`
5. `control reach widening / narrowing`
6. `runtime retirement without residue cleanup`
7. `runtime retirement with profile cleanup`

## Layout

### A. Requested-versus-effective card

Fields:

- operator asked for
- effective runtime mutation
- continuity verdict
- highest-risk side effect

Examples:

- `Run in background` -> `fresh service install` is not equivalent to `keep same control plane`
- `Make it reach more folders` -> `service principal swap to Local System` also implies profile-root change risk
- `Expose WebUI on LAN` -> `control reach widening` is not just a convenience toggle

### B. Side-effect ladder

Rows:

- shares preserved?
- identity surface preserved?
- old profile still exists?
- manual reconnect needed?
- WebUI exposure changed?
- file-update observation changed?
- shell/context integration changed?

### C. Safe-language rewrite

Three stacked lines:

- **operator asked for**
- **product can honestly do now**
- **product may honestly say afterward**

### D. Proof-of-completion pane

For the chosen mutation, state the proof condition.

Examples:

- `Migrated profile opened with expected shares and same fingerprint.`
- `Fresh service profile created; old profile remains separate.`
- `WebUI now listens beyond localhost and exposure review completed.`
- `Observation narrowed to rescan/restart discovery under this principal.`

## Required actions

- `Apply runtime switch`
- `Choose narrower alternative`
- `Review storage lineage again`
- `Export runtime switch receipt`
- `Cancel`

## Guardrails

- Never let `background` or `service` language hide a fresh-profile outcome.
- Never let a Local System swap look like a pure permission gain without naming observation and storage-root consequences.
- Never let WebUI LAN exposure appear without an explicit reach sentence.
- Never let `successful switch` overclaim same-seat continuity when the result is a different active profile.

## Output

A reviewed runtime-mutation contract that replaces a vague runtime toggle with a continuity-aware, surface-aware switch statement.
