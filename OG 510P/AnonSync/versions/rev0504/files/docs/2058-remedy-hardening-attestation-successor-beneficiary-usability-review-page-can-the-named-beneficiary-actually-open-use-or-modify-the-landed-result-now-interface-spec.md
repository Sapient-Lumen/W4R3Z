# Remedy-hardening-attestation successor beneficiary-usability review page — can the named beneficiary actually open, use, or modify the landed result now?

## Purpose

This review exists to stop the operator from claiming beneficiary usability merely because the result landed, the folder appears, or the path exists.
The page forces a separate answer to whether the named beneficiary can actually perform the intended action now.

## Review questions

### 1. Materialization and byte possession

- Does the beneficiary have actual bytes locally, or only placeholders, disconnected visibility, or announced metadata?
- If the bytes are not local, what exact act would materialize them?
- Is that act dependent on a source peer being online?
- Could the mesh already be placeholder-only for this object?

### 2. Open and handler readiness

- Does the expected shell or file-browser affordance exist on this platform?
- Can the beneficiary invoke the intended action directly, or is a side-path workaround required?
- Is WebUI or another non-integrated surface being mistaken for ordinary local usability?
- Does the file auto-open in the ordinary path, or only after a longer manual fetch flow?

### 3. Access and update posture

- Does the beneficiary actually have permission to perform the intended action?
- Is the local copy writable, readable, executable, or shareable in the intended way?
- Has read-only local mutation or another mode transition put the beneficiary on a copy that no longer receives updates?
- Is a visible local copy being mistaken for a live participant in the intended update lane?

### 4. Blocker classes

- Are files locked by applications, security tools, encryption tools, or the system itself?
- Does the runtime user have read-write access to the folder and files?
- Are path-length, character-encoding, or filesystem errors blocking the intended action?
- Is a ghost-file or source-peer-absence warning narrowing the usable sentence?

### 5. Strong-sentence ceiling

- What is the strongest honest beneficiary-usable sentence now?
- What stronger `the named beneficiary can use this now as intended` sentence must stay blocked?
- Which future evidence would upgrade or downgrade that sentence?

## Required comparisons

The review must show a side-by-side comparison of:

- landed result class versus beneficiary-usable result class
- intended action versus currently exercisable action
- local bytes expected versus local bytes actually present
- self-sufficient usability versus online-source dependency
- ordinary affordance expected versus workaround-only access
- live-updating posture expected versus blocked or degraded update posture

## Required layout

### Header

Show:

- action name
- beneficiary identifier
- usability posture
- blocker severity badge
- strongest honest sentence now

### Left column — intended beneficiary use

Show:

- intended action class
- expected bytes posture
- expected handler or shell path
- expected access and update posture
- unacceptable substitute states

### Right column — actual beneficiary useability

Show:

- actual materialization state
- actual source dependency
- actual handler or shell state
- actual access and update state
- blocker-by-blocker reasoning
- whether the beneficiary can currently read, open, modify, or merely inspect

### Footer decision rail

The footer must make plain whether the beneficiary is:

- not materially equipped yet
- materially equipped but blocked
- partially usable only
- usable for named slice only
- fully usable sentence still blocked
