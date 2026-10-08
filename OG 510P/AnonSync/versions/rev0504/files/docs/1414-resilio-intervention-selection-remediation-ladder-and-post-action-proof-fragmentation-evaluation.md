# Resilio intervention selection, remediation ladder, and post-action-proof fragmentation evaluation

## Why this pass exists

The archive already had stronger doctrine for:

- policy profiles
- typed waivers and exception debt
- policy supersession and retirement
- rollout rings, readiness gates, stop conditions, and rollback class
- rollout-health evidence, signal adjudication, and promotion confidence

What it still lacked was one explicit answer to the next ordinary operator question:

> we have enough health evidence to know something is wrong or ambiguous — but what exact intervention should we take next, how destructive is it, what evidence justifies it, and what proof would tell us whether it actually helped?

Current official Resilio material is useful here, but it still spreads that answer across many separate troubleshooting and warning articles:

- `My files don't sync`
- `Peers aren't connecting`
- `Database error`
- `Service files missing / Cannot identify destination folder`
- `Core warnings`
- `Agent run out of system notify watchers`
- `Folders are duplicating with an index (i) in their name`
- `Sync Service Troubleshooting on Windows`
- `Collecting debug logs automatically`
- `Power user preferences`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `My files don't sync` still proposes a broad range of interventions with very different cost and reversibility: re-add a folder to re-index it, run a disk check, restart Sync so it rescans, free disk space, delete stuck `.!sync` files after restart fails, or fix time drift.
- `Database error` still suggests a stepped ladder: first restart Sync, then disconnect and reconnect the share to the same destination folder if only one peer is affected, then re-add the shared folder on all peers, and only after persistent failure send debug logs.
- `Peers aren't connecting` still suggests connectivity-oriented actions such as checking tracker use, switching to predefined hosts, opening the listening port in router and firewalls, rechecking routing when multiple NICs are involved, or addressing relay and multicast constraints.
- `Service files missing / Cannot identify destination folder` still treats the `.sync` directory as critical state, says corruption or duplicate-instance interaction can suspend synchronization, and says remediation can require removing the share, deleting the `.sync` subfolder, and adding the share back.
- `Core warnings` still includes identity and license remedies such as unlinking from identity and creating a new one, or removing and reapplying a license.
- `Agent run out of system notify watchers` still says the immediate symptom may degrade into periodic/manual rescan dependence, and remediation can require changing system watcher limits and then restarting Sync.
- `Folders are duplicating with an index (i)` still says the fix can require disconnecting and reconnecting the folder and choosing a different location, while the preventive posture can require changing default synchronization mode to `Disconnected` before future arrivals.
- `Sync Service Troubleshooting on Windows` still shows a particularly costly action class: switching the service to `Local System` can solve permission issues, but it also creates a new service storage location with no old folders present, requiring re-add and re-share or reconnect of all folders.
- `Collecting debug logs automatically` still says debug logging may need to be enabled and Sync restarted before the issue is reproduced, and that logs should be collected for at least 15 minutes after reproduction.
- `Power user preferences` still includes action-relevant toggles like `profiler_enabled` which requires restart, plus save/refresh intervals and folder rescan cadence settings.

So current Resilio still clearly admits serious intervention truths:

- not all fixes are equal in destructiveness
- some interventions are observation-oriented, some are topology-oriented, some are identity-oriented, some are filesystem-oriented, and some are evidence-collection-oriented
- some interventions are local and reversible, while others fork or replace a settings/storage world
- some interventions require restart before they even become active
- some interventions repair symptoms without proving root cause
- some interventions are safe only if all peers or all linked devices coordinate
- support escalation and artifact capture are themselves actions with cost and prerequisites

But those truths do not yet become one first-class operator-facing **intervention-selection / remediation-ladder / post-action-proof object**.

## What Resilio still gets right

### 1) It preserves that different failures need different action classes

Resilio does not pretend every issue has one generic fix.
Network, disk, identity, folder metadata, permissions, and service-world issues really do call for different interventions.
That practical candor is worth borrowing.

### 2) It sometimes orders actions from cheaper to more expensive

`Database error` is especially useful because it presents a rough ladder: restart, then reconnect, then re-add, then escalate with logs.
That is better than jumping straight to rebuild.

### 3) It admits that some interventions have world-level side effects

The service-troubleshooting docs are valuable because they do not hide that changing service user can land the operator in a different storage world that no longer contains prior folders.
That is exactly the kind of discontinuity a serious product must make impossible to miss.

### 4) It treats evidence gathering as real work

Restart-bound log capture and profiler activation are intervention costs, not passive conveniences.
That is a useful truth.

## Where current Resilio still fragments the operator answer

### A) The intervention ladder is present only as scattered folklore

A careful operator can reconstruct something like this from current docs:

- observe / wait / rescan
- restart app or service
- repair connectivity path
- reconnect folder to same destination
- re-add share locally or on all peers
- rebuild identity
- delete service files and recreate sync instance
- switch synchronization mode or default location strategy
- change service principal or config surface
- collect artifacts and escalate

But that ladder does not exist as one product-owned object with typed action classes, blast radius, prerequisites, reversibility, and success claims.
The operator still has to infer it from article to article.

### B) Destructiveness and reversibility are not normalized

Current Resilio docs may list restart, reconnect, re-add, unlink, delete `.sync`, or change service account as remediation choices.
Those are not equivalent.
Yet the product/docs do not consistently normalize:

- which action changes only live state
- which action rebuilds local metadata
- which action affects one folder versus all folders
- which action forks into a different storage world
- which action requires coordination with other peers
- which action is reversible without further data loss risk

### C) Post-action proof is inconsistent

Some docs imply that symptom disappearance means the fix worked.
Others only say to contact support if the problem persists.
But the stronger operator question is:

> what exact sentence may we safely claim after this intervention?

Examples that should stay distinct:

- `symptom disappeared after restart`
- `folder metadata was rebuilt successfully`
- `network route now permits peer connection`
- `identity corruption was replaced with a new identity`
- `service permissions issue appears mitigated but old service world was abandoned`
- `issue remains unexplained`

Current Resilio materials contain pieces of this truth, but not one canonical post-action proof contract.

### D) Support escalation is separated from the intervention ladder

Debug logging, profiler capture, manual log collection, and support contact are all described.
But they still read more like separate troubleshooting infrastructure than typed ladder steps with clear entry conditions.

### E) “Least destructive next action” is still mostly implicit

The strongest non-clone reason in this pass is simple:
current official Resilio docs still do not give one joined place where the operator can say:

> given our current evidence and risk tolerance, the least destructive intervention that is justified right now is X, these weaker actions are insufficient for stated reasons, these stronger actions are premature for stated reasons, and the proof we expect afterward is Y.

That is exactly the product seam AnonSync should own.

## What AnonSync should borrow

Borrow these truths from current Resilio:

- different failure modes really do need different intervention classes
- some interventions should come before more destructive rebuilds
- restart-bound activation and restart-bound observation are real costs
- changing runtime world, service user, or identity is qualitatively stronger than reconnecting one folder
- log/profiler capture is part of intervention planning, not an afterthought

## What AnonSync should refuse to clone

Do not clone any contract where:

- restart, reconnect, re-add, relink, and world-fork actions sit side by side without normalized risk labels
- support-artifact capture is separate from the operator’s intervention plan
- symptom disappearance is allowed to masquerade as root-cause resolution
- destructive actions are allowed without an explicit statement of why weaker steps are insufficient
- storage-world replacement or service-world fork can happen without an intervention proof page
- the operator must reconstruct the remediation ladder from multiple KB articles

## Product decision forced by this comparison

AnonSync should expose one first-class **intervention object** for every material corrective action, including observation-only actions and support-artifact actions.

That object should preserve:

- problem statement and current strongest safe sentence
- target symptom or blocked sentence
- candidate interventions in ladder order
- evidence threshold required for each candidate
- blast radius and reversibility class
- prerequisites and coordination scope
- expected post-action proof
- abort / rollback conditions
- resulting stronger sentence if the intervention succeeds

## The new AnonSync page family this pass requires

This comparison forces five new interface obligations:

1. an **intervention contract sheet** that names symptom, target sentence, candidate action classes, risk class, reversibility, and expected success proof
2. a **remediation-ladder review** that compares wait/retry/restart/rescan/reconnect/re-add/relink/rebuild/escalate options without collapsing them into one vague “fix it” verb
3. an **intervention approval proof** that records why the chosen least-destructive viable action won and why weaker or stronger actions were rejected
4. an **intervention timeline** that preserves attempt, result, cooldown, retry, rollback, and escalation history
5. an **intervention lineage receipt** that records evidence basis, chosen action, reversibility class, observed outcome, and blocked stronger sentence

## Bottom line

Current official Resilio still deserves credit for practical, specific remediation advice.
But the advice remains too article-fragmented to clone.

The archive should therefore:

- **borrow Resilio’s candor that interventions differ in cost and scope**
- **refuse Resilio’s still-scattered remediation contract**
- **ship one operator-facing intervention ladder with explicit risk, reversibility, and post-action-proof semantics**
