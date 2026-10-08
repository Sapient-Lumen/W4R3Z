# Resilio policy rollout, ring promotion, readiness-gate, and rollback-window fragmentation evaluation

## Why this pass exists

The archive already had stronger doctrine for:

- policy profiles
- binding classes
- conformance review
- typed waivers and exception debt
- policy supersession, successor relation, and retirement truth

What it still lacked was one explicit answer to the next ordinary operator question:

> we know which policy succeeds which — but how do we ship that successor safely across a real cohort, in stages, with explicit gates, automatic stop conditions, and truthful rollback classes?

Current official Resilio material is useful here, but it still spreads the answer across several families:

- `FAQ Resilio Sync 3.0.0`
- `Updating installation to Resilio Sync v3`
- `Resilio Sync: supported platforms and system requirements`
- `Sync Private Identity & Linking My Devices`
- `Selective Sync`
- `Power user preferences`
- `Running Sync as a service on Windows`
- `Sync Service Troubleshooting on Windows`
- `Resilio Sync change log`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `FAQ Resilio Sync 3.0.0` still says v2 and v3 preserve synchronization compatibility, while linked devices should all be updated to v3 to avoid license conflicts.
- `Updating installation to Resilio Sync v3` still says Business cannot be updated to v3, warns that important changes may affect existing usage and shares configuration, and shows that the update procedure depends on install posture: default install, CLI with `/config` or `/storage`, service install, or `sync.conf` beside the binary.
- The same update doc still says that a mistaken Business-to-v3 attempt may lead to lost shares configuration while files remain intact.
- `Resilio Sync: supported platforms and system requirements` still shows a narrower v3 platform envelope than v2 in important ways, including v3 not being supported on Windows Servers while v2 still lists Windows Server support and broader Linux/FreeBSD coverage.
- `Sync Private Identity & Linking My Devices` still says mixed v2/v3 linking is highly inadvisable because licenses may conflict and access to Sync UI and shares configuration may be lost, even though files on storage are not affected.
- `Selective Sync` still marks feature availability by version and entitlement, which means a rollout claim can be true for one subset and false for another.
- `Power user preferences` still says older versions may be missing settings or still have deprecated ones, and at least one field (`profiler_enabled`) still requires restart to activate.
- `Running Sync as a service on Windows` still says service installation offers a migrate-settings path or a clean-install path, and config-mode use requires placing `sync.conf` in the service storage folder and restarting the service.
- `Sync Service Troubleshooting on Windows` still says changing the service principal to `Local System` creates another storage world with no old folders present and requires re-add / re-share.
- `Resilio Sync change log` still contains release-history evidence that rollout state has repeatedly interacted with restart boundaries, advanced-setting persistence after autoupdate, license application after restart, startup crashes, path corruption after restart, and linked-version issues.

So current Resilio still clearly admits real rollout truths:

- byte compatibility can survive while rollout safety does not
- one cohort can contain members that must not move together
- install posture changes the upgrade procedure
- platform class changes the upgrade lane
- service migration and clean install are different activation paths
- some changes take effect only after restart
- restart itself can be a risk window worth naming
- feature claims can be subset-safe and cohort-unsafe at the same time
- rollback may preserve data while still leaving configuration, identity, or shares-state discontinuities

But those truths do not yet become one first-class operator-facing **policy rollout / ring promotion / stop condition object**.

## What Resilio still gets right

### 1) It admits that `compatible` is weaker than `safe to roll out together`

This is the most important thing to borrow.
Current docs say v2 and v3 remain sync-compatible while warning against mixed-major linked families.
That is exactly the kind of distinction a serious product must preserve.

### 2) It admits that upgrade posture depends on installation posture

Default install, service install, CLI `/config` or `/storage`, and sidecar `sync.conf` are not one lane.
The update steps differ.
That is useful operator truth.

### 3) It admits that platform and product lane constrain rollout

Business, Windows Server, older NAS / Linux classes, and v2-only lanes are not just `older members`.
They set different movement rules.

### 4) It admits that some rollout changes are cold-apply, not live-apply

Restart-required settings, service restarts, migration-vs-clean-install choices, and storage-world changes are real activation boundaries.
This matters for staged deployment.

### 5) It admits that feature rollout can be narrower than byte compatibility

Feature availability by version/entitlement means the operator needs staged claim discipline, not one optimistic rollout sentence.

## Where current Resilio still fragments the operator answer

### A) Promotion sequencing exists, but not as one explicit object

An operator can piece together that a rollout should probably happen in stages because of:

- mixed-major linked-family risk
- Business holdouts
- platform limits
- service migration branches
- restart-required fields
- subset-only feature availability

But current docs do not yield one canonical rollout object with:

- target revision
- target cohort
- ring membership
- readiness gates
- stop conditions
- rollback class
- blocked stronger sentence

### B) Readiness is scattered across unrelated pages

Before a rollout, the operator may need to know all of these:

- is every linked family on one safe major?
- is any member held on a platform lane that cannot move?
- is any subject already living under waivers that block promotion?
- does this change require restart or clean rebind?
- is this feature safe only on a subset?

Current Resilio docs answer those pieces across FAQ, support articles, feature pages, update guides, and changelog archaeology.

### C) There is no first-class stop-condition workspace

A serious rollout needs to stop when:

- a new blocker enters the target ring
- a linked family becomes mixed-major mid-rollout
- a migration branch lands in clean-install instead of continuity
- a service principal switch creates a new storage world
- a waiver expires or a prerequisite fails

Current Resilio docs describe each ingredient separately, but there is no operator-owned stop-condition workspace.

### D) Rollback class is not modeled strongly enough

Rollback is not one thing.
Depending on the move, rollback may be:

- live revert with continuity
- restart-bound revert
- fork-and-rebind
- reinstall preserving storage
- data-safe but config-discontinuous
- impossible without new waivers

Current docs expose the raw ingredients but not one stable rollback classification.

### E) Promotion proof and claim discipline are too easy to overstate

Without a rollout object, `rolled out successfully` can accidentally hide that:

- only canary moved
- broad rollout was frozen
- some members were held back on old lane
- some members moved via clean install instead of continuity
- some policy claims are still subset-only

## Hard product decisions now locked for AnonSync

### 1) Every policy successor rollout is a first-class rollout object, not a boolean publish

The product must preserve:

- predecessor revision
- successor revision
- target subject set
- ring structure
- readiness gates
- stop conditions
- rollback class
- outcome counts by ring

### 2) Ring membership is explicit and typed

Supported ring classes must include at least:

- `canary`
- `pilot`
- `broad`
- `holdback`
- `frozen`
- `rollback`
- `unknown`

### 3) Promotion is gate-based, not hope-based

A ring may promote only after the product publishes verdicts for at least:

- version-floor readiness
- platform-lane readiness
- waiver status
- restart / cold-apply debt
- storage-world continuity class
- feature-claim safety

### 4) Stop conditions are first-class and can halt broader promotion

At minimum the product must support stop classes:

- `new-governing-blocker`
- `mixed-major-linked-risk`
- `waiver-expired`
- `cold-apply-not-completed`
- `storage-world-fork-detected`
- `subset-claim-only`
- `unknown-regression`

### 5) Rollback class must be published before promotion

Supported rollback classes must include at least:

- `hot-revert`
- `restart-bound-revert`
- `rebind-required`
- `reinstall-preserving-data`
- `config-discontinuous-revert`
- `no-safe-rollback`
- `unknown`

### 6) A broader ring may never inherit an optimistic sentence from a narrower ring

`canary succeeded` must never overclaim `safe cohort-wide`.
The product must restate the strongest safe sentence at each ring boundary.

## Required page family

This seam now requires five AnonSync pages:

- **Policy-rollout contract sheet**
- **Rollout-readiness review**
- **Ring-promotion proof**
- **Rollout-event timeline**
- **Policy-rollout lineage receipt**

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that compatibility, eligibility, activation, and safe broad rollout are different truths; refuse any interface contract where the operator must reconstruct rollout rings, readiness gates, stop conditions, and rollback class from scattered FAQ, update, service, feature, platform, and changelog pages instead of one explicit rollout object.
