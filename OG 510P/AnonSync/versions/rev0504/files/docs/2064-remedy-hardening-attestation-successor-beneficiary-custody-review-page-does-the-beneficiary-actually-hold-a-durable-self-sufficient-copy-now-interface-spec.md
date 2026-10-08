# Remedy-hardening-attestation successor beneficiary-custody review page — does the beneficiary actually hold a durable, self-sufficient copy now?

## Purpose

This review exists to stop the operator from claiming custody merely because the beneficiary can presently use the result.
The page forces a separate answer to whether the beneficiary actually holds bytes in a durable way that survives upstream disappearance, local mode reversion, or storage cleanup.

## Review questions

### 1. Byte possession and retention anchor

- Does the beneficiary have actual bytes locally right now, or only placeholdered or source-dependent accessibility?
- Where do those bytes live: ordinary file system, app sandbox, downloads area, local share, or another named storage world?
- Is the copy anchored in the beneficiary world, or only mirrored through a source-controlled topology?
- Could local cleanup or share removal erase this copy without any separate beneficiary export step?

### 2. Upstream dependency and withdrawal sensitivity

- If the source peer disappears, disconnects, revokes, changes mode, or loses the bytes, does the beneficiary still keep a sufficient copy?
- Is the current state only a re-fetch opportunity rather than present custody?
- Does the beneficiary depend on a local share whose source can be removed or downgraded?
- Does license loss, share removal, or source placeholder state collapse beneficiary custody?

### 3. Export, portability, and handoff

- Has the beneficiary exported or relocated the bytes into a world they control independently?
- Is the current copy bound to one app sandbox, one device path, or one topology that the beneficiary does not truly govern?
- Is a one-time transfer being mistaken for durable ongoing custody or vice versa?
- Can the beneficiary demonstrate portable retention, or only current presence at one location?

### 4. Reversion and eviction hazards

- Can `Remove from this device`, placeholder reversion, storage cleanup, or app-level purge discard the current copy while leaving metadata behind?
- Could removing the share, removing the app-held download, or clearing the device storage destroy local bytes while keeping UI traces or history?
- Is the current copy at risk of reverting into visibility-only or source-dependent posture?
- Are there any hidden cleanup, mode, or topology actions that would narrow the custody sentence immediately?

### 5. Strong-sentence ceiling

- What is the strongest honest beneficiary-custody sentence now?
- What stronger `the beneficiary now has an independent durable copy` sentence must stay blocked?
- Which future evidence would upgrade or downgrade that sentence?

## Required comparisons

The review must show a side-by-side comparison of:

- beneficiary-usability standing versus beneficiary-custody standing
- present useability versus durable custody
- local byte presence versus durable retention anchor
- self-sufficiency expected versus upstream dependence observed
- withdrawal independence expected versus withdrawal fragility observed
- exportable or portable custody expected versus sandboxed or topology-bound possession observed

## Required layout

### Header

Show:

- action name
- beneficiary identifier
- custody posture
- fragility badge
- strongest honest sentence now

### Left column — intended beneficiary custody

Show:

- intended custody class
- intended retention horizon
- expected retention anchor
- expected independence from upstream withdrawal
- unacceptable substitute states

### Right column — actual beneficiary custody

Show:

- actual byte-possession class
- actual storage or sandbox anchor
- actual upstream dependency and withdrawal sensitivity
- actual export or handoff posture
- blocker-by-blocker custody reasoning
- whether the beneficiary merely uses, temporarily possesses, or durably retains the result

### Footer decision rail

The footer must make plain whether the beneficiary is:

- presently usable only
- source-dependent only
- locally present but fragile
- durable for named slice only
- self-sufficient custody sentence still blocked
