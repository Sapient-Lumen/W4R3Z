# Preregistered scenario bundles

A scenario bundle is the replicated, multi-block layer above Lacuna's single comparative scenario run. Use it when one four-condition run is not enough and the owner wants to fix the complete block roster, hidden assignments, order, ratings contract, witness policy, and descriptive endpoints before observing any condition result.

It is not the play entrance. A player can still say **“Will you DM?”** and enter play without learning any of this machinery. Bundles are backstage research custody for an experiment owner.

## The invariant in one sentence

> Publish every planned child and hidden assignment first; execute one block at a time; seal every block while it is still blind; unblind none until all are sealed.

The bundle state machine makes that sentence executable:

```text
awaiting-witnesses        optional external-retention gate
        ↓
block-active              exactly one block may advance
        ↓
block-ready-to-seal       all fixed primary ratings and post-rating method assessments are frozen
        ↓ seal
block-active              next scheduled block becomes active
        ↓ repeat
ready-to-unblind          every block is sealed; every child is still blind
        ↓
unblinding               crash-resumable report construction
        ↓
unblinded                 one deterministic rater-level report
```

Earlier blocks remain `ready-to-unblind` while later blocks run. Their private assignments and reports are not joined into an outcome until the complete scheduled prefix has been sealed.

## What this adds to a single scenario

A single `scenario` run compares four conditions from one exact seed:

- `forward-only`;
- `prompt-only-retcon`;
- `lacuna-serial`; and
- `lacuna-role-separated`.

A `scenario bundle` adds:

- two to 128 preregistered blocks;
- one host-randomized block order;
- one precommitted hidden assignment seed per child;
- atomic publication of every exact child clone before execution;
- an optional external witness threshold before the first cell can advance;
- fixed, comparable rating contracts across all blocks;
- cross-block declared context and invocation-ID separation;
- one immutable seal per fully rated and post-rating-masked block;
- seal-all-before-unblind discipline;
- crash-resumable aggregate publication; and
- rater-level JSON and spreadsheet-safe CSV export.

The report performs no significance test and makes no causal claim. It retains integer scores, preference ranks, failures, strata, and execution declarations so a later analysis can use an explicitly chosen model rather than silently treating ordinal sums as interval utility.

## 1. Prepare every block capsule

Create a capsule from each exact seed cube:

```bash
./lacuna scenario template STORY_A > story-a-capsule.json
./lacuna scenario template STORY_B > story-b-capsule.json
```

Edit each capsule before building the bundle. At minimum, replace the scripted off-plan action and fill the exact model policy. Keep the rating object identical across every capsule. The bundle refuses different scales, prompts, dimensions, or required rater counts because their observations would not be directly comparable under the registered contract.

A block may use a different story or model. Record those differences in the generated plan's `story_stratum` and `model_stratum`. The plan's `replicate` and `tags` fields are descriptive strata, not statistical guarantees.

## 2. Build and inspect one preregistration

The shortest entrance accepts repeated `CUBE CAPSULE` pairs:

```bash
./lacuna scenario bundle template \
  --block STORY_A story-a-capsule.json \
  --block STORY_B story-b-capsule.json \
  --block STORY_C story-c-capsule.json \
  --minimum-witnesses 1 \
  > bundle-plan.json
```

The command resolves every selected campaign or bare cube to one normalized absolute seed path and embeds the complete validated capsule. It does not create the experiment yet.

Read and deliberately edit `bundle-plan.json` before `begin`. Important fields are:

- `title` and `research_question`;
- `blocks[].block_id`;
- `blocks[].story_stratum`;
- `blocks[].model_stratum`;
- `blocks[].replicate`;
- `blocks[].tags`;
- `registration.primary_dimensions`;
- `registration.analysis_notes`; and
- `witness_policy.minimum_receipts_before_execution` (zero to 64).

V1 retains at most 64 exact witness records and refuses the next receipt before creating a file or changing `bundle.json`. The v1 inclusion rule is fixed: every scheduled block and every terminal cell failure remains in the report. There is intentionally no post hoc block-exclusion switch.

## 3. Publish the complete bundle

```bash
./lacuna scenario bundle begin bundle-plan.json \
  --root .lacuna-scenario-bundles \
  --format markdown
```

`begin` verifies each source cube and capsule boundary, generates one private master schedule, derives every child run ID and assignment seed, builds every child and all four exact SQLite clones inside a hidden owner-private staging directory, preflights the complete tree, and publishes the directory with one same-filesystem rename.

If any block fails staging, no final bundle directory is published. Publication is still not a transaction across hostile filesystems, remote services, or later provider calls.

Copy the printed bundle path. Thereafter the normal rule is simple:

```bash
cat BUNDLE_PATH/NEXT.md
./lacuna scenario bundle status BUNDLE_PATH --format markdown
```

`bundle.json` is authoritative. `NEXT.md` is a deterministic pointer and can be repaired only after the complete bundle and every child audit:

```bash
./lacuna scenario bundle recover BUNDLE_PATH --format markdown
```

Recovery adopts only permitted parent-cache drift, such as an accepted child transition whose outer cache was not refreshed or a partially completed bundle unblind. It does not invent a return, rating, witness, seal, or report.

## 4. Retain the public commitment externally

When the plan requires witnesses, the bundle starts at `awaiting-witnesses`. No child may advance.

Emit the exact public commitment:

```bash
./lacuna scenario bundle commitment BUNDLE_PATH > public-commitment.json
```

Give that object to an independent person or retention service. Keep the returned receipt, timestamp record, transparency-log locator, detached signature reference, or other evidence outside the bundle host.

Create the local receipt template:

```bash
./lacuna scenario bundle witness-template BUNDLE_PATH \
  --witness-id witness.alice \
  > witness-alice.json
```

Replace every placeholder. A record must include an external receipt ID and either an external locator or a SHA-256 digest of the external receipt. Then freeze it:

```bash
./lacuna scenario bundle witness BUNDLE_PATH witness-alice.json
```

The first block becomes executable only when the preregistered threshold is met.

This is a custody gate, not remote verification. Lacuna binds the operator-supplied receipt description to the exact commitment digest. It does not contact the service, validate a signature, prove a timestamp, or prove that the witness remains available. An external holder can make later mutation or whole-bundle disappearance detectable to that holder; no local mechanism can prove that an entirely unwitnessed earlier bundle was never discarded.

## 5. Execute only the active block

Follow `NEXT.md`. The bundle exposes the same complete local driver as a single scenario but routes it through the sole active child:

```bash
./lacuna scenario bundle dispatch BUNDLE_PATH --format markdown
```

Give the private driver to exactly one isolated cell coordinator, not to a blind rater. The driver contains an operator-only canary. For nested role workers, the coordinator must pass only each exact generated role dispatch; it must not forward the complete driver or open the unrelated filesystem-canary file. Preserve exactly one returned `lacuna.scenario-cell-return.v1` object and record it:

```bash
./lacuna scenario bundle record BUNDLE_PATH CELL_RETURN.json --format markdown
```

Repeat until all four opaque cells are frozen. Before the child blind packet exists, the child freezes its preregistered exact-canary scan. Findings remain private during rating and do not trigger a rerun. The bundle refuses a declared `context_id` used by an earlier block and refuses any repeated non-null provider invocation ID before mutating the child. The child separately enforces cross-cell separation, persistent-context controls, fresh checkpoint roles, capsule-bound narrator continuation, and scan custody.

Context, managed-checkpoint, continuation-checkpoint, capsule-digest, and invocation identifiers remain host declarations. Distinct strings and valid digest topology do not prove fresh model memory, provider isolation, card-only prompting, independent tools, or absence of collusion.

## 6. Collect the fixed blind ratings and post-rating masking assessments

When all four cell returns are retained, create a form for each required rater:

```bash
./lacuna scenario bundle rating-template BUNDLE_PATH \
  --rater-id rater.alice \
  > rating-alice.json
```

Give the rater only the active child blind packet or the generated rating form. Do not give them the bundle directory, private assignment, drivers, canary plan, source tokens, scan findings, schedule, commitment internals, or prior block outcomes.

Record each completed form:

```bash
./lacuna scenario bundle rate BUNDLE_PATH rating-alice.json --format markdown
```

Primary ratings are frozen first. The block reaches `block-ready-to-seal` only after the capsule's fixed unique-rater count has been met and each retained rater has also supplied a post-rating method-identifiability assessment. Use:

```bash
./lacuna scenario bundle masking-template BUNDLE_PATH \
  --assessor-id rater.alice > masking-alice.json
./lacuna scenario bundle mask BUNDLE_PATH masking-alice.json --format markdown
```

The masking form records guessed method, confidence, cue text, familiarity, and recognition flags while the condition key is still hidden. Correctness is joined only during bundle unblinding.

Structured blinding omits condition names and invocation details. It does not guarantee semantic anonymity: prose style, refusals, seams, or a rater's prior knowledge may reveal a method.

## 7. Seal, do not unblind

```bash
./lacuna scenario bundle seal BUNDLE_PATH
```

The v3 seal binds the child run identity, capsule digest, hidden assignment digest, blind-packet digest, exact pre-rating contamination-scan digest, every primary rating artifact digest, and every post-rating masking artifact digest. The child remains `ready-to-unblind`; no condition mapping, canary finding, or scenario report is published by this step.

If another block remains, the next precreated child becomes active. Repeat dispatch → record → rate → seal in the fixed private schedule order.

Directly advancing a future child contaminates the protocol and makes the outer audit refuse. Directly unblinding a sealed child before the bundle enters unblinding now fails closed at the child gate; the bundle parent opens that gate with the block-seal digest during all-block unblinding.

## 8. Unblind all scheduled blocks

Only after every block is sealed:

```bash
./lacuna scenario bundle unblind BUNDLE_PATH --format markdown
```

The bundle durably enters `unblinding`, completes each child report idempotently, then publishes one deterministic aggregate. If the process stops after one child report, rerun the same command. No child is unblinded during experiment execution, but same-host private custody is cooperative rather than cryptographic; the owner can always inspect files they control.

Export the frozen report:

```bash
./lacuna scenario bundle export BUNDLE_PATH --format json > bundle-report.json
./lacuna scenario bundle export BUNDLE_PATH --format csv  > bundle-observations.csv
```

JSON is the exact canonical data view. It retains block scan hashes/status/counts and condition-mapped contamination status. CSV is a convenience view with one row per rater × condition × block and includes contamination status/count columns. Text beginning with a spreadsheet formula marker is prefixed with an apostrophe to reduce formula execution when opened interactively; use JSON when exact authored string bytes matter.

## The three operating roles

### Bundle parent

The parent owns the directory and is the only authority allowed to call `begin`, `witness`, `record`, `rate`, `seal`, `recover`, or `unblind`. It reads the current audited pointer and hands out only the exact next artifact.

### Cell executor

The executor receives one condition-specific private coordinator driver, including its operator canary and the filesystem-canary path/digest. It may be a human, one persistent model context, a shell-capable frontier parent, a native subagent tree plus fresh narrator contexts, or a human bridge to ordinary chat. It must keep the driver at the coordinator boundary, pass only exact role cards to delegated workers, return one exact cell object, and never advance the bundle.

### Blind rater

The rater receives transcript-only material and one complete rating contract. The rater never needs cube access or the ability to run commands.

Do not combine these roles merely because one model can technically perform them. Role separation is useful only when it creates an information boundary.

## ChatGPT, Codex, Claude, Gemini, and weaker coordinators

The bundle does not depend on a provider-specific orchestration API. It compiles the exact next state into files and commands so a coordinator does not need to infer the whole protocol from conversation memory.

- **Codex or another shell-capable workspace agent:** give it the repository and bundle path. Instruct it to run `scenario bundle status`, obey the sole next action, and never inspect private future children or unblind early.
- **ChatGPT with a connected shell/filesystem tool:** use the same parent procedure. Native/role chats may execute explicit cards, but a role-separated cell also needs a fresh non-project-shared narrator after each checkpoint. The parent retains transition authority.
- **Ordinary ChatGPT without tools:** a human runs each printed command, pastes only the returned driver into the chosen chat, saves the exact JSON response, and runs the next parent command. This is a human bridge, not automatic durable custody.
- **Claude Code or Gemini CLI:** use the shell-capable parent pattern and provider-native workers only as wrappers around the complete Lacuna handoffs.
- **A less capable model:** do not ask it to “understand the experiment.” Give it only `NEXT.md` plus the exact input document named there. Require one schema-conforming output and no extra transition.

A safe parent instruction is:

```text
You are the bundle parent, not a player and not a blind rater.
Run `./lacuna scenario bundle status BUNDLE_PATH --format markdown`.
Perform only the single command named by the audited next action.
Never inspect future child directories, private assignments, or prior outcomes to choose what to run.
For one cell coordinator, transmit the complete current private driver; for any nested worker, transmit only its exact generated role dispatch. Give blind raters only the rating packet and accept exactly one JSON object.
Do not call seal until the status is block-ready-to-seal, meaning both primary ratings and masking assessments are frozen.
Do not call unblind until the status is ready-to-unblind.
On interruption, rerun status; use recover only when its documented narrow repair applies.
```

The cube can make delegation more likely by naming the owner, complete input, expected schema, blind flag, and exact command. It cannot force ChatGPT, Codex, Claude, Gemini, or any other host to create subagents, and it cannot attest that two subagents had independent memory.

## Why role-separated Lacuna is one treatment

Inside each block, `lacuna-serial` and `lacuna-role-separated` use the same generator → judge → compressor → verifier protocol. The difference is now the complete declared context topology:

- serial narration and checkpoint roles share one persistent context for the complete cell;
- role-separated checkpoint roles use fresh pairwise-distinct contexts;
- after each completed role-separated checkpoint, `checkpoint run next-turn` binds the exact committed capsule and next player input into one continuation dispatch received by a fresh narrator; and
- that narrator context persists only until the next checkpoint.

This makes “does manufactured context asymmetry plus an actual compression bottleneck help?” an experimental contrast rather than an architectural assumption. A native subagent system is convenient, but separate chats or unlinked API calls can implement the same intended slices. A provider may still share hidden state; Lacuna records declarations and validates topology, not an independence or forgetting certificate.

## Private topology

```text
10-preregistration.json
20-PRIVATE-schedule.json
30-public-commitment.json
witnesses/
    witness-0001-<id>.json
blocks/<opaque-block-label>/
    60-block-seal.json
    scenario-runs/<precommitted-run-id>/
        15-PRIVATE-contamination-plan.json
        65-PRIVATE-contamination-scan.json
        ...complete single-scenario custody...
90-bundle-report.json
bundle.json
NEXT.md
.bundle.lock
```

Every child directory must remain a real contained directory. Replacing a child with a symlink or other filesystem node is refused. The cooperative lock is same-host coordination, not hostile-user or mount-namespace confinement.

## Failure and refusal rules

- A failed `begin` leaves no visible final bundle.
- A missing or changed source cube boundary refuses before publication.
- A witness threshold cannot be bypassed by directly advancing a child.
- A future child changed before its turn contaminates the bundle.
- A reused cross-block declared context or invocation ID refuses before the active child is mutated.
- A persistent-context control that drifts contexts, or a role-separated child that omits/reuses its post-checkpoint narrator or capsule binding, refuses before record publication.
- A linked, unsafe, changed, or nonmatching contamination scan refuses before rating/sealing; a leak-detected scan remains included.
- A rated block cannot be skipped or replaced after sealing.
- No block can be unblinded through the bundle until all are sealed, and no bundle-staged child can be unblinded directly while its gate is closed.
- A crash during unblinding is resumed, not restarted with a new assignment.
- A changed retained commitment, schedule, capsule, assignment, clone, return, rating, seal, child report, aggregate report, or deterministic pointer refuses audit.

## Interpretation boundary

A bundle can show that one method received higher or lower blind ratings under the registered blocks, or that it failed more often, cost more, changed cube state differently, or offered no visible advantage. That is useful evidence against as well as for Lacuna.

It cannot by itself establish general superiority, causal mechanism, provider independence, semantic blindness, fresh memory, filesystem confinement, scientific validity, or a population-level effect. A clean canary scan is not an attestation; a positive exact match is one retained falsification result. The report is an auditable input to analysis, not the conclusion.
