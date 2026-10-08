# 471 — Production-entry readiness receipts, boundary checks, and no live by installation

## One-line thesis

Consequential public-AI systems should cross into live use only through an explicit production-entry readiness receipt that attests the exact system, approvals, disclosures, monitoring attachments, fallback routes, and operator controls now in force, rather than letting installation, provisioning, or flag flips impersonate governed go-live.

## Why this matters

There is a recurrent governance illusion in software-backed administration: people say a system is “live” when what actually happened is that code was copied, a model endpoint was configured, a feature flag was enabled, or infrastructure began responding. None of those events proves that the governed deployment is ready.

A system can be reachable while the public record is stale. It can serve outputs before monitoring is attached. A model can start running before operators are trained on the current route, before fallback and recourse links are verified, or before the canonical disclosure head reflects the actual deployment. A package may be installed and still not be the governed service the institution thought it launched.

The archive already distinguishes approval from live use, and simulated proof from live proof. What it still lacked was one note for the **operational cutover boundary itself**: the moment where a configured system becomes an institutionally authorized live actor.

## Pattern pack

### 1. Separate installation, configuration, readiness, and live entry

The archive should keep at least these states distinct:

- installed or provisioned,
- configured,
- reachable,
- readiness-attested,
- shadow or bounded-live,
- and fully live.

A deployment that can answer requests is not automatically a deployment that is governance-ready.

### 2. Require one readiness receipt before consequential live entry

A production-entry receipt should name the exact deployment entering service, including as applicable:

- model, provider, and version identity,
- approved baseline or change window,
- responsible owner,
- canonical public disclosure head,
- monitoring coverage class,
- fallback and recourse routes,
- operator training state,
- rollback owner and rollback path,
- and the date and authority under which live entry is approved.

The receipt is the compact answer to: *what exactly just became live under whose authority?*

### 3. Verify boundary attachments, not only software health

Before go-live, readiness should confirm that the system is attached to its real governance boundaries, including:

- logging and retention surfaces,
- appeals and override paths,
- incident reporting routes,
- human fallback lanes,
- access-control gates,
- public notices and explanatory surfaces,
- and any model or supplier restrictions required for lawful operation.

A healthy service without those attachments is still governance-incomplete.

### 4. Block live entry when a named prerequisite is missing

If a required boundary is absent, the archive should treat the system as not ready, even if it is technically functional. Missing prerequisites can include:

- stale or absent public notice,
- unverified monitoring,
- expired approval,
- missing operator training,
- broken packet export,
- missing rollback readiness,
- or unresolved integrity checks on a required upstream component.

### 5. Preserve first-run witness data

The first consequential live use after readiness should leave behind a compact witness of the deployment that actually entered service, so later investigators can distinguish:

- what was approved,
- what was installed,
- and what actually ran.

### 6. Re-attest after significant modification or cutover-relevant drift

A deployment should require a fresh readiness receipt when significant modification changes the deployment in ways that affect decision scope, live behavior, or governance obligations. Routine maintenance is not the same as cutover-relevant change.

### 7. Do not let auto-start, resume, or default routing create accidental go-live

A consequential service should not become live merely because a process restarted, a flag defaulted to on, traffic was silently routed, or a fallback environment began serving production requests. Live entry should remain a named act with a named receipt.

## Guardrails

- Do not treat installation or reachability as proof of governed live readiness.
- Do not allow missing disclosure, monitoring, or fallback attachments to be patched in later by habit.
- Do not let first real use occur without a preserved readiness basis.
- Do not hide the identity of the exact deployment that entered service.
- Do not let restarts or default routing silently resume consequential live operation.

## Failure modes

- **installed-is-live illusion**: technical presence impersonates governed entry.
- **ghost go-live**: the deployment serves real cases without a named readiness act.
- **unattached live service**: the system runs before monitoring, notice, or fallback routes are actually connected.
- **cutover drift**: the deployment that entered service is not the one described in the approval story.
- **auto-resume launch**: a restart or routing default quietly recreates live use without fresh authorization.

## Practical tests

A production-entry discipline passes when it can answer yes to all of the following:

1. Are installation, readiness, and live-entry states kept separate?
2. Does each consequential go-live produce a named readiness receipt for the exact deployment?
3. Does readiness verify governance-boundary attachments, not only service health?
4. Will live entry block when required disclosure, monitoring, fallback, or approval prerequisites are missing?
5. Does significant modification trigger re-attestation before renewed live use?

## Compression rule for the archive

If a consequential system can say **the service is up** but cannot also say **which deployment entered live use, under what readiness receipt, with which disclosures, monitors, and fallback routes attached**, then it is still letting **installation impersonate governed launch**.
