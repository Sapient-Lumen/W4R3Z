# Resilio intervention execution choreography, prerequisite checkpoints, and abort-boundary fragmentation evaluation

## Why this pass exists

The archive already had stronger doctrine for:

- rollout-health evidence and promotion confidence
- intervention selection and least-destructive-next-action choice
- reversibility, blast radius, and post-action proof ceilings

What it still lacked was one explicit answer to the next ordinary operator question:

> once we have chosen the least-destructive justified intervention, how do we execute it safely, in what exact order, with what preflight checks, with what witness checkpoints, and at what point do we stop instead of digging deeper damage?

Current official Resilio material is useful here, but it still spreads that answer across many separate troubleshooting and support pages:

- `My files don't sync`
- `Database error`
- `Peers aren't connecting`
- `Service files missing / Cannot identify destination folder`
- `Disconnecting and Removing Folders`
- `Sync Service Troubleshooting on Windows`
- `Running Sync in configuration mode`
- `Collecting debug logs automatically`
- `Agent run out of system notify watchers`
- `How soon does synchronization start?`
- `Some internal tasks are taking time to complete`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `My files don't sync` still tells the operator to check peer connectivity, then UI warnings, then Sync History, then queue state before committing to specific corrective steps like restart, re-add, disk check, deletion of stuck `.!sync` files, or time-drift correction. That is already a multi-step runbook, but it is distributed across prose rather than owned as one execution object.
- `Database error` still gives a strict order: restart first; if one peer is affected, disconnect and reconnect the share to the same destination; if the error persists or hits multiple peers, disconnect/remove and re-add the folder on all peers. That is a real escalation graph with branch conditions.
- `Peers aren't connecting` still mixes router/firewall, relay, multicast, NIC, and proxy checks, which are not merely different causes but different execution lanes with different observer needs and different possible side effects.
- `Service files missing / Cannot identify destination folder` still requires a destructive preflight: before re-adding, make sure nothing important remains in Archive and delete the `.sync` subfolder. That is not a casual note; it is an abort boundary and data-loss gate.
- `Disconnecting and Removing Folders` still separates disconnect from remove, and reconnect can land on a new default path rather than the original path. That means a runbook must preserve path intent explicitly instead of assuming reconnect is neutral.
- `Sync Service Troubleshooting on Windows` still treats switching the service to `Local System` as both a permission remedy and a world-changing act: restart is required, the service comes up with a different storage folder, old folders are absent, and the operator must re-add and re-share or reconnect all folders.
- `Running Sync in configuration mode` still distinguishes between saving `sync.conf` into storage and starting Sync in config mode, with service-mode exceptions and non-default `storage_path` creating a new settings world. That is execution choreography, not mere configuration trivia.
- `Collecting debug logs automatically` still says enable debug logging, restart Sync to ensure it is active, reproduce the issue, then let logs accumulate for at least 15 minutes. That is a witness-capture run with preconditions and observation window.
- `Agent run out of system notify watchers` still says the durable fix is to raise the watcher limit, optionally make it persistent in `/etc/sysctl.conf`, and restart Sync. Again, order matters.
- `How soon does synchronization start?` still says scheduled rescan runs every 600 seconds and on start by default, manual rescan is available on demand, and setting `folder_rescan_interval` to zero disables rescans even on restart. That changes which checkpoints make sense after any fix.
- `Some internal tasks are taking time to complete` still says the symptom can be intermittent and self-recovering, which means a safe runbook must sometimes stop after observe/wait rather than escalate immediately.

So current Resilio still clearly admits serious execution truths:

- chosen interventions have ordered substeps
- some steps are preflight checks rather than the intervention itself
- some steps create new runtime or storage worlds
- some steps require an explicit quiet point or restart before evidence becomes meaningful
- some steps have destructive prerequisites that should block continuation
- some steps should pause for observation instead of immediately escalating
- some steps branch by cohort size, affected surface, or whether the issue is local versus multi-peer
- support-artifact capture is itself a run with timing constraints

But those truths do not yet become one first-class operator-facing **remediation run / checkpoint graph / abort-boundary object**.

## What Resilio still gets right

### 1) It frequently preserves step order

The current `Database error` and debug-log docs are especially useful because they do not flatten restart, reconnect, re-add, reproduce, and log-collection into one vague bucket.
They preserve sequence.
That is worth borrowing.

### 2) It often hints at preflight risk

The `Service files missing` article is valuable because it tells the operator to check Archive importance before deleting `.sync` and re-adding the share.
That is a real preflight gate.

### 3) It admits that not every situation should escalate immediately

`Some internal tasks are taking time to complete` still says the condition can self-recover.
That means `wait and observe` can be a correct rung inside a runbook.

### 4) It preserves that reconnect/remove/re-add are different moves

The disconnect/remove/reconnect docs and database-error docs do useful work by keeping those verbs separate.
That separation should survive into product design.

## Where current Resilio still fragments the operator answer

### A) The execution plan is scattered across separate troubleshooting stories

A careful operator can reconstruct something like this from current docs:

- preflight: inspect peers, warnings, history, queue, archive, permissions, path intent
- local safe step: observe, rescan, restart, or reconnect
- environmental repair: firewall/router, tracker, watcher limit, system permissions
- world-changing step: service-principal switch, config storage-path change, share re-add
- witness run: reproduce, collect logs, wait the right interval
- abort: stop if archive risk, wrong destination path, unexpected world fork, or missing peer coordination
- escalate: move to stronger intervention or human escalation

But that step graph does not exist as one product-owned execution object with prerequisites, step ordering, branch conditions, quiet points, and safe-abort rules.
The operator still has to infer it from article to article.

### B) Preflight checks are not normalized

Current Resilio docs do contain preflight-like warnings, but they are not normalized into one place:

- do peers actually connect
- is the issue local or multi-peer
- do warnings or history explain the block
- is Archive carrying anything important before destructive cleanup
- will reconnect choose the wrong default path
- will service principal switch create a new storage world
- does rescan even run in this configuration
- is the witness capture truly active yet or does restart still remain

### C) Abort boundaries remain too implicit

The strongest non-clone reason in this pass is that the operator still has to infer when not to continue.
Examples:

- do not delete `.sync` until archive risk is reviewed
- do not assume reconnect to default path is acceptable
- do not treat Local System switch as a harmless permission toggle
- do not assume restart proves anything if rescans are disabled
- do not treat intermittent self-recovering internal work as proof that a stronger repair is needed

These are exactly the boundaries that should be first-class product truth.

### D) Checkpoint proof is inconsistent

The current docs can help the operator act, but they are much weaker at preserving checkpoint semantics:

- what did we inspect before doing anything
- what exact step just finished
- what evidence says it is safe to continue
- what stronger sentence remains blocked even after the checkpoint passes
- what exact event should trigger abort or rollback

### E) Handoff and multi-step continuity are too folkloric

Real operators often stop midway and hand work to another person or another maintenance window.
Current Resilio materials do not turn a multi-step repair into one durable, resumable run artifact.

## What AnonSync should borrow

Borrow these truths from current Resilio:

- execution order matters
- preflight inspection is real work
- reconnect, remove, re-add, relink, world-switch, and artifact capture are different run classes
- some runs need quiet points and observation windows
- some symptoms should self-recover before stronger action is justified

## What AnonSync should refuse to clone

Do not clone any contract where:

- selected interventions have no first-class run object
- destructive prerequisites live as side notes rather than hard gates
- checkpoint success is implicit rather than recorded
- reconnect, re-add, and world-fork steps are allowed to sound equivalent
- restart-bound witness capture is allowed without explicit activation confirmation
- a run can continue even though archive risk, wrong destination, or missing coordination was never cleared
- another operator has to reconstruct unfinished remediation from chat or memory

## Product decision forced by this comparison

AnonSync should expose one first-class **remediation run object** for every material multi-step intervention.

That object should preserve:

- chosen intervention and its target sentence
- ordered step graph with branch conditions
- preflight prerequisites and destructive gates
- quiet-point / restart / observation windows
- per-step checkpoint evidence
- safe-continue and safe-abort rules
- rollback or fallback step after each destructive boundary
- durable handoff state and blocked stronger sentence

## The new AnonSync page family this pass requires

This comparison forces five new interface obligations:

1. a **remediation run contract sheet** that names the chosen intervention, step graph, prerequisites, quiet points, destructive gates, and target proof
2. an **execution-readiness review** that checks preflight state, observer coverage, maintenance-window fit, destination/path intent, archive risk, and coordination readiness before step one
3. a **checkpointed run proof** that records step completion, witness basis, safe-continue decision, and safe-abort decision at each gate
4. a **remediation run timeline** that preserves preflight, freeze, execute, verify, cooldown, abort, rollback, and handoff events over time
5. an **execution lineage receipt** that records the executed step graph, gates passed or tripped, abort boundaries encountered, final proof ceiling, and next required action

## Bottom line

Current official Resilio still deserves credit for practical, stepwise remediation advice.
But the execution contract remains too article-fragmented to clone.

The archive should therefore:

- **borrow Resilio's candor that interventions have ordered substeps and real abort boundaries**
- **refuse Resilio's still-scattered execution contract**
- **ship one operator-facing remediation run object with explicit preflight, checkpoints, and abort semantics**

