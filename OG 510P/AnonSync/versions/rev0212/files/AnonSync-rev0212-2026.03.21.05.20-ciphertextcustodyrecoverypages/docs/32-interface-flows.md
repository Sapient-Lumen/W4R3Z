# Interface flows (canonical operator journeys)

These flows exist as design tests.
If the proposed surface cannot express them clearly, the interface is not ready.

## Flow 1 — link two personal devices without universal hidden authority

Goal:

- link laptop and desktop as personal devices
- allow future convenience
- avoid implicit owner semantics

Suggested flow:

```text
anonsync link create --label personal --profile personal-strict --plan
anonsync plan show pln_01J...
anonsync plan apply pln_01J...
anonsync link add --group personal --invite ./desktop.link
anonsync link show personal --show-provenance
```

Expected semantics:

- devices become members of a linked group
- no local identity is replaced
- no share grant is created unless profile/policy says so
- provenance shows which profile created which defaults

Expected operator answers from CLI alone:

- what the linked group implies
- what it does **not** imply
- whether future shares will auto-grant anywhere
- who or what created those defaults

## Flow 2 — add an untrusted encrypted cache node

Goal:

- use a cheap VPS as storage/transit only
- ensure no plaintext lands there

Suggested flow:

```text
anonsync device add --name cache-vps --addr cache.example.net:4747
anonsync device set cache-vps --trust-class untrusted
anonsync grant create vault --device cache-vps --perm encrypted-replica --plan
anonsync plan show pln_01J...
anonsync plan apply pln_01J...
anonsync status --json
```

Expected semantics:

- remote node can store ciphertext only
- status shows at least one encrypted-only replica
- fetch on another device explains whether a plaintext source is currently reachable

Expected operator answers from CLI alone:

- does this device have plaintext authority?
- which grant caused the ciphertext-only behavior?
- is the share still recoverable if the origin goes offline?

## Flow 3 — make a LAN-only sync policy actually legible

Goal:

- restrict a share to LAN-only sync
- confirm that no tracker/relay path is still in effect

Suggested flow:

```text
anonsync policy create --name lan-only --tracker disabled --relay disabled --lan enabled
anonsync share set media --policy lan-only --plan
anonsync plan show pln_01J...
anonsync plan apply pln_01J...
anonsync policy cache clear --policy lan-only
anonsync doctor --share media
```

Expected semantics:

- share now uses the named policy
- cached non-LAN endpoints are removable through an explicit command
- status and doctor explain whether viable LAN paths exist

Expected operator answers from CLI alone:

- which policy is active
- which peers are currently reachable through LAN
- whether stale non-LAN cached routes were cleared
- why sync is blocked if no viable LAN route exists

## Flow 4 — replace a lost laptop without identity folklore

Goal:

- replace a dead laptop with a new machine
- preserve trust semantics explicitly
- avoid clone-style magic

Suggested flow:

```text
anonsync backup create --output ./preloss.asb
# later on replacement machine
anonsync recover import ./preloss.asb
anonsync recover replace-device --old dev_dead --new dev_new --reason "hardware replacement" --plan
anonsync plan show pln_01J...
anonsync plan apply pln_01J...
anonsync audit --type recovery.replace_device_completed
```

Expected semantics:

- recovery is explicit and auditable
- linked-group membership and grants are reconciled through recovery, not through linking
- any residual access for the dead device can be revoked explicitly

Expected audit highlights:

- initiator
- old device ID
- new device ID
- objects rewritten
- grants re-bound or revoked
- correlation IDs to emitted recovery events

## Flow 5 — answer “why can’t this file fetch?” without guesswork

Goal:

- diagnose a blocked fetch in selective mode

Suggested flow:

```text
anonsync file fetch vault Secrets/Taxes/report.pdf
anonsync transfer list --json
anonsync doctor --share vault
anonsync events --type transfer.blocked --since evt_000120
```

Expected semantics:

- blocked state includes a stable reason code
- doctor points to the same underlying condition as transfer state and event stream
- operator can tell whether the issue is:
  - no reachable peer
  - only encrypted replicas reachable
  - trust/policy mismatch
  - invalid mount or local path permissions

## Flow 6 — widen trust only after an explicit reviewed plan

Goal:

- promote a device from read-only to read-write on a sensitive share
- ensure the operator sees the real blast radius before apply

Suggested flow:

```text
anonsync grant set grt_01J... --perm rw --reason "promote studio laptop" --plan
anonsync plan show pln_01J...
anonsync audit --subject grt_01J...
anonsync plan apply pln_01J...
```

Expected semantics:

- the preview states that write authority is expanding
- any linked-group or policy-derived implications are listed explicitly
- apply fails if relevant share/grant state changed after preview

Expected operator answers from CLI alone:

- exactly what new authority is being granted
- whether any policy references depend on this grant
- whether the plan is still valid to apply

## Flow 7 — capability mismatch should be legible, not mysterious

Goal:

- understand why a requested placeholder or transport feature is unavailable on this host

Suggested flow:

```text
anonsync daemon capabilities
anonsync mount attach media ~/Media --mode selective --json
anonsync doctor --device self
```

Expected semantics:

- capability output states which placeholder strategies are supported locally
- mount or policy operations degrade explicitly or fail explicitly, never silently half-work
- doctor points to the same capability facts as the command failure


## Flow 8 — adopt or relocate into a populated path only after a real comparison

Goal:

- bind a visible share to an already-populated local directory, or move an existing mount to a new path
- surface what is identical, local-only, remote-only, or colliding before commit
- avoid reconnect-dialog or timestamp-win guesswork

Suggested flow:

```text
anonsync incoming compare inc_01J... --path /Volumes/External/Media
anonsync incoming adopt inc_01J... --path /Volumes/External/Media --mode selective --plan
anonsync plan show pln_01J...
anonsync mount compare mnt_01J... --path /Volumes/Archive/Media
anonsync mount relocate mnt_01J... /Volumes/Archive/Media --plan
```

Expected semantics:

- comparison reports whether the target path is empty, already bound, or non-empty
- output classifies identical content, local-only content, remote-only content, and true collisions
- adopt/relocate into a non-empty path does not silently proceed without that comparison becoming part of the review surface
- local path rebinding is auditable separately from share identity or permission changes

Expected operator answers from CLI alone:

- whether the target path is safe to bind directly
- which files would be merged harmlessly
- which paths need policy or manual resolution first
- whether the action changes only local binding or also wider replicated state

## Flow 8a — reconcile same-path divergent bytes before binding a pre-populated target

Goal:

- bind a visible share or repair an old mount into a non-empty local directory with pre-existing bytes
- show whether this is same-lineage reuse, harmless merge, timestamp-risky divergence, or encrypted-target mismatch
- avoid treating `Folder not empty` as an operator contract

Suggested flow:

```text
anonsync incoming compare inc_01J... --path /srv/archive/workdocs
anonsync incoming reconcile inc_01J... --path /srv/archive/workdocs --plan
anonsync plan show pln_01J...
anonsync mount compare mnt_01J... --path /srv/archive/workdocs
anonsync mount reconcile mnt_01J... --path /srv/archive/workdocs --plan
```

Expected semantics:

- comparison output separates identical, local-only, remote-only, same-path-divergent, and path-collision classes
- reconciliation output states whether lineage suggests prior bind continuity or a foreign local tree
- timestamp evidence may rank candidates but cannot hide that chronology confidence is weak or guarded
- encrypted-target misuse blocks or diverts into preservation/quarantine work instead of pretending it is an ordinary merge
- apply emits a reconciliation receipt, not just an ordinary mount/adopt receipt

Expected operator answers from CLI alone:

- whether the target is really an old copy of this share or just a folder with overlapping names
- which files are safe to preserve as-is, which can merge, and which require an explicit winner choice
- whether chronology confidence is strong enough to trust an automatic ranking
- whether encrypted/annex reuse is even admissible for this target

## Flow 9 — verify the bundled privacy runtimes before trusting them

Goal:

- inspect what exactly shipped for Tor and I2P on this host
- confirm persistence and update posture
- avoid treating embedded privacy support as a black box

Suggested flow:

```text
anonsync transport list
anonsync transport show tor
anonsync transport verify tor
anonsync transport show i2p
anonsync transport verify i2p
anonsync transport session list
```

Expected semantics:

- output states whether Tor is compiled in and whether I2P is carried as an embedded helper/runtime payload
- verification shows version/build facts, digest/provenance summary, persistence path, and update mode
- the operator can tell whether a degraded transport problem is a bootstrap problem, a verification problem, or an ordinary policy-disable outcome
- session output stays separate from runtime output so “present”, “warm”, and “actively carrying routes” do not blur together

Expected operator answers from CLI alone:

- what exactly is bundled here
- where any persistent runtime state lives
- whether updates come only with daemon releases or through another channel
- whether the runtime is merely present, actually warm, or currently active in route selection

## Flow 10 — grant a temporary clearnet-direct bulk-transfer lease without rewriting durable policy

Goal:

- keep overlay-first WAN policy as the default
- temporarily allow direct clearnet for a trusted high-bandwidth transfer
- make the exception easy to inspect and easy to expire

Suggested flow:

```text
anonsync route show --share media --decision-trace
anonsync route allow-clearnet-direct --share media --ttl 90m --reason "initial seed to trusted workstation"
anonsync route show --share media --explain
anonsync override list
anonsync effective-state share media
```

Expected semantics:

- the normal policy remains overlay-first before and after the lease
- the direct-speed exception has explicit scope, reason, and expiry
- route output says directly that `public-direct` became eligible only because of the active lease
- effective-state output makes clear that durable discovery policy was not rewritten underneath the exception

Expected operator answers from CLI alone:

- what the normal route would have been without the lease
- when the lease expires automatically
- whether the lease is share-scoped, peer-scoped, or broader than intended
- whether a current direct route is ambient policy or a deliberate temporary exception

## Interface quality test

The interface is probably not ready if any of these flows require:

- undocumented support knowledge
- UI-only rescue steps
- guessing hidden transport state
- linking as a substitute for recovery
- manual log scraping just to understand ordinary blocked states
- re-running a dangerous mutation without knowing whether the preview is still valid
- silently creating default-path mounts for newly visible shares
- binding a share into a non-empty path without a comparison report
- using one delete verb for both local space reclamation and distributed deletion
- showing a dashboard card that can silently mutate trust or authority without revealing the underlying object
- forcing operators to open multiple unrelated views just to answer whether a share is visible, adopted, materialized, and settled


## Flow 11 — adopt a newly visible share without accidental default-path creation

Goal:

- let a linked or manually shared dataset become visible
- choose a local path deliberately
- avoid surprise duplicate folders or default-path mounts
- do this per share without flipping the whole device into a different default mode

Suggested flow:

```text
anonsync incoming list
anonsync incoming show inc_01J...
anonsync incoming defer inc_01J... --reason "waiting for external disk"
anonsync incoming adopt inc_01J... --path ~/Sync/media --mode selective
anonsync mount show ~/Sync/media --show-provenance
```

Expected semantics:

- the share can be visible before a mount exists
- adoption chooses path and initial materialization mode explicitly
- provenance shows whether visibility came from linking, manual share, or recovery
- declining or deferring adoption is a first-class action

Expected operator answers from CLI alone:

- why this share is visible here
- whether it is already mounted anywhere locally
- which policy made it visible
- which path choice actually bound it to the filesystem

## Flow 12 — evict local bytes without risking a share-wide delete

Goal:

- free local disk space on a selective/full mount
- keep the share intact elsewhere
- make destructive share-wide delete a separate reviewed action

Suggested flow:

```text
anonsync file evict media Movies/2025/bigfile.mkv
anonsync file remove media Movies/2025/bigfile.mkv --scope local
anonsync file remove media Movies/2025/bigfile.mkv --scope share --plan
anonsync plan show pln_01J...
```

Expected semantics:

- eviction and local-only remove never delete remote replicas
- share-wide delete is explicitly scoped and previewable
- the command surface makes the blast radius legible before apply

Expected operator answers from CLI alone:

- whether the bytes are still stored locally
- whether the file still exists in the replicated share
- whether the action touched metadata/materialization only or shared state too

## Flow 13 — prove what survives before a share-wide delete

Goal:

- decide whether deleting from the replicated share still leaves any recoverable copy
- distinguish remaining plaintext replicas from encrypted-only remnants
- avoid assuming version history exists when retention or size caps mean it does not

Suggested flow:

```text
anonsync file check vault Secrets/Taxes/report.pdf --for remove-share
anonsync file remove vault Secrets/Taxes/report.pdf --scope share --plan
anonsync plan show pln_01J...
```

Expected semantics:

- `file check` reports local post-action state, known remaining plaintext replicas, encrypted-only replicas, and history coverage/gaps
- `remove --scope share --plan` references that preservation report instead of forcing the operator to reconstruct safety from folklore
- the plan becomes guarded or blocked when the action would leave no known plaintext copy and no credible rollback path

Expected operator answers from CLI alone:

- whether any plaintext bytes will remain anywhere after the delete
- whether recovery would depend only on encrypted replicas or limited history retention
- whether the daemon considers the action low-risk, guarded, high-risk, or blocked

## Flow 14 — recover from encrypted-replica data after local state loss

Goal:

- recover useful data from an encrypted-untrusted replica
- avoid requiring the original daemon state to still exist
- keep the workflow explicit and auditable

Suggested flow:

```text
anonsync recover decrypt-replica --input /mnt/cache/vault --output ./vault-restored
anonsync recover import ./mesh.asb
anonsync doctor --share vault
```

Expected semantics:

- offline recovery can operate without a running daemon when sufficient recovery material exists
- recovery material requirements are explicit
- later daemon-side import/reconciliation remains a separate, auditable step

Expected operator answers from CLI alone:

- whether recovery material is sufficient
- whether recovered output is plaintext, partial, or blocked by missing keys
- what daemon-side follow-up is still required


## Flow 15 — restore a deleted file without browsing hidden archive directories

Goal:

- inspect recoverable prior versions of a file
- restore locally without surprising other peers
- require an explicit reviewed path for replicated restore back into the share

Suggested flow:

```text
anonsync file history workdocs report.docx
anonsync file restore workdocs report.docx --entry hst_01J... --scope local
anonsync file restore workdocs report.docx --entry hst_01J... --scope share --plan
anonsync plan show pln_01J...
```

Expected semantics:

- history output shows candidate restore points, source, capture time, and allowed restore scopes
- local restore does not mutate replicated share state
- share-scope restore is previewable and auditable
- the user never needs to know hidden on-disk archive conventions to perform an ordinary restore

Expected operator answers from CLI alone:

- which prior versions exist
- where they came from
- whether restoring this version will affect only this device or the whole share
- which audit/event records were produced


## Flow 16 — resolve a conflict without treating a magic filename as the API

Goal:

- inspect an actual conflict case
- choose a winner deliberately
- avoid the "delete the weird filename and hope" workflow

Suggested flow:

```text
anonsync conflict list --share workdocs
anonsync conflict show cft_01J...
anonsync conflict resolve cft_01J... --winner candidate_02 --plan
anonsync plan show pln_01J...
anonsync plan apply pln_01J...
```

Expected semantics:

- conflict output shows type, path, candidates, and likely blast radius
- resolution makes clear whether the result is local-only or changes replicated share state
- the user never needs to infer the safe action from a suffix like `.Conflict`
- audit and events record how the conflict was resolved

Expected operator answers from CLI alone:

- what actually conflicted
- which candidates exist
- which resolution was chosen
- whether the resolution affected just this device or the cluster

## Flow 17 — change ignore behavior without editing hidden service files

Goal:

- inspect ignore rules for a share
- add a rule safely
- test whether a path will be ignored
- see whether rule drift exists

Suggested flow:

```text
anonsync ignore list workdocs
anonsync ignore add workdocs '*.tmp'
anonsync ignore test workdocs build/output.log
anonsync ignore set-consistency workdocs --mode warn-on-drift
anonsync share rescan workdocs
```

Expected semantics:

- ignore rules are listed as supported objects with provenance
- adding a rule is incremental and auditable, not a full hidden-file rewrite by default
- `test` explains rule matches in human-readable and machine-readable forms
- drift warnings are explicit if peer-local or imported rule state diverges from policy expectations

Expected operator answers from CLI alone:

- which ignore rules are active
- why a path is ignored or indexed
- whether drift exists
- which audit/event records were produced by the rule change


## Flow 18 — preview a mixed-version or capability-mismatched link before accepting it

Goals:

- inspect a pending personal-device link
- surface version-family, role, or feature downgrade risks before commitment
- avoid learning about compatibility trouble only after identity or policy state changed

Example:

```text
anonsync preflight link --invite ./old-laptop.link
anonsync preflight show rpt_01J...
anonsync link add --group personal --invite ./old-laptop.link --plan
anonsync plan show pln_01J...
```

Expected behavior:

- preflight reports `ok`, `warning`, or `blocked`
- warnings explain concrete downgrade or compatibility consequences
- blocked output points to the exact remediation path instead of letting the operator discover it after the fact
- if the later plan references the report, apply fails when relevant capabilities or versions changed since preview

Operator questions this flow must answer clearly:

- what exactly is incompatible or risky
- whether the issue is a blocker or merely a warning
- whether a different role or policy would make the action safe
- which audit/event records captured the preview and later acceptance

## Flow 18a — review a device join without silently merging identity or widening authority

Goals:

- inspect a candidate device before adding it to a personal constellation
- prove whether the action is an ordinary join, a migration, or should become replacement instead
- surface visibility and authority blast radius before any shares appear locally

Example:

```text
anonsync preflight link --invite ./old-laptop.link
anonsync preflight show rpt_01J...
anonsync claim prepare --invite ./old-laptop.link --group personal --member-class appliance
anonsync claim show clm_01J... --view review
anonsync claim apply clm_01J...
```

Expected behavior:

- the review says whether the candidate keeps its current identity or needs a different workflow
- requested member class and defaults are explicit before apply
- the review counts or summarizes the incoming visibility delta instead of hiding it behind a later folder list surprise
- approval, re-share, revoke, or successor power changes are explicit rather than ambient
- compatibility or migration warnings can block apply before the join mutates live state

Operator questions this flow must answer clearly:

- is this device joining, replacing, or taking over something
- what shares become visible immediately and in what posture
- what authority widens, if any
- which member class and defaults will govern later incoming shares
- what receipt will later prove the join and its blast radius

## Flow 19 — add a read-only personal device without downgrading the share model

Goals:

- keep a convenient linked personal mesh
- attach one device as read-only or receive-only
- avoid falling back to a weaker share type or manual key-entry ritual

Example:

```text
anonsync role create --name readonly-viewer --perm ro --write-policy receive-only --mode selective
anonsync preflight grant receipts --group personal --role readonly-viewer
anonsync grant create receipts --group personal --role readonly-viewer
anonsync incoming list
anonsync incoming adopt inc_01J... --path ~/Receipts --role readonly-viewer
```

Expected behavior:

- the same share/grant model stays in use; only the applied role changes
- preflight explains whether the target device can satisfy the role without downgrade
- authority does not silently expand to owner-like power just because the device is part of a personal linked group
- the eventual grant and adoption surfaces show the chosen role and resulting constraints explicitly

Operator questions this flow must answer clearly:

- what authority this device actually receives
- whether local edits will propagate or be blocked
- whether plaintext is permitted on the target device
- whether any capability mismatch forced a different outcome than the requested role

## Flow 20 — claim an offered share without silently turning visibility into a mount

Goal:

- inspect a share-access invite or newly visible incoming share
- choose the local outcome deliberately
- keep an auditable record of what was offered versus what was claimed

Suggested flow:

```text
anonsync invite show ./media.invite
anonsync claim prepare --invite ./media.invite --path ~/Sync/media --mode selective --role readonly-viewer
anonsync claim show clm_01J...
anonsync claim apply clm_01J...
anonsync incoming list
```

Expected semantics:

- inspecting the invite does not itself create a mount
- claim preparation records intended local path, mode, and role
- claim apply can create incoming or adopted state explicitly, but not by surprise
- audit can distinguish offered capability from accepted local state

Expected operator answers from CLI alone:

- what was actually offered
- what this machine claimed
- whether the claim widened authority, created a mount, or only staged visibility
- what drift or expiry would now block apply

## Flow 21 — verify encrypted offline-recovery material before disaster

Goal:

- export supported recovery prerequisites for an encrypted share
- verify sufficiency while the system is healthy
- avoid discovering too late that recovery depends on hidden database state

Suggested flow:

```text
anonsync recover bundle export --type encrypted-offline-decrypt --share vault --output ./vault.arb
anonsync recover bundle verify ./vault.arb
anonsync status
anonsync doctor --share vault
```

Expected semantics:

- recovery bundle export produces a durable artifact with explicit scope and format
- verification says whether offline decrypt is sufficient, partial, or blocked
- status and doctor surface degraded recovery posture when bundle sufficiency changes
- operators do not need to recover database names from logs just to know whether recovery will work

Expected operator answers from CLI alone:

- do I currently have enough material to decrypt offline?
- what dependency, if any, still exists on daemon/database state?
- which share or workflow this bundle covers
- whether rotation or replacement has invalidated older recovery material


## Flow 22 — approve a collaborator for one future share class without creating ambient trust

Goal:

- keep the convenience of not re-approving the same collaborator every time
- bound that convenience to one class of future shares
- make later approval use auditable from CLI/API alone

Suggested flow:

```text
anonsync approval issue --peer alex --scope share-tag:photos --max-role readonly-viewer --approver-scope linked-group --expires 90d --plan
anonsync plan apply pln_01J...
anonsync approval list --peer alex
anonsync approval test --peer alex --share vacation-2026
```

Expected semantics:

- the approval becomes a durable object with explicit scope, approver scope, expiry, and maximum role
- later photo-share invites may use this approval without a fresh prompt, but unrelated shares may not
- audit can show which later action consumed the approval record
- operators do not have to remember invisible certificate history to understand why a future share auto-approved

Expected operator answers from CLI alone:

- what class of future shares this peer is pre-approved for
- which local devices may exercise that approval
- when the approval expires or was last used
- whether the approval can imply read-only, read-write, owner, or encrypted-only access

## Flow 23 — prove a share only uses approved discovery and relay infrastructure

Goal:

- allow only approved topology exposure for one share
- verify not just the chosen route, but what metadata the policy publishes and to whom

Suggested flow:

```text
anonsync policy create --name private-topology \
  --announce-scope private-infra-only \
  --announce-via private-discovery \
  --dial-via known-host,private-discovery \
  --relay private-only \
  --fallback-order known-host,private-discovery,private-relay
anonsync share set workdocs --policy private-topology --plan
anonsync plan show pln_01J...
anonsync plan apply pln_01J...
anonsync policy show private-topology --explain
anonsync route show --share workdocs --json
anonsync policy exposure show private-topology
```

Expected semantics:

- the share binds to a named topology policy, not just a bag of route toggles
- route output explains whether the current path depended on public or private infrastructure
- exposure output explains what reachability is being published, where, and under which fallback rules

Expected operator answers from CLI alone:

- does this policy publish anything to public discovery infrastructure?
- can the daemon still fall back to a relay, and if so which class of relay?
- is it dialing only known/private targets, or also tracker-learned targets?
- what exact policy or fallback step would widen metadata exposure from the current baseline?


## Flow 24 — explain why a route won and what would change it

Goal:

- answer why the daemon chose one route for a share
- identify which alternative paths were rejected
- verify whether policy tightening or cache clearing would actually change the result

Suggested flow:

```text
anonsync route show --share workdocs --explain
anonsync explain route --share workdocs
anonsync policy show private-topology --explain
anonsync doctor --share workdocs
```

Expected semantics:

- route output shows the active path plus serious rejected candidates
- explanation output names decisive facts such as policy restrictions, stale endpoints, missing direct reachability, or relay prohibition
- output says whether the explanation is current or was generated before the last policy/cache change
- doctor can point to the exact remediation if the operator wants a different route

Expected operator answers from CLI alone:

- why did this share use relay/direct/known-host instead of another candidate?
- which candidate routes failed because of policy, and which failed because of reachability?
- would clearing cached endpoints materially change anything?
- which policy change would be required to prevent this route class in the future?


## Flow 25 — drain a device for maintenance without mutating its long-term policy

Goal: prepare a laptop for shutdown on a weak uplink without rewriting grants, share modes, or discovery policy.

```bash
anonsync override create \
  --target device:laptop-ember \
  --mode drain-egress \
  --ttl 45m \
  --reason "shutdown maintenance"

anonsync status --device laptop-ember --json
anonsync explain device laptop-ember --effective
anonsync route show --device laptop-ember --effective
anonsync override show ov_01J...
```

Expected behavior:

- the operator can see that current behavior differs from baseline because of an active override lease
- uploads already in flight may finish, but new downloads do not start
- grants, linked-group policy, and discovery policy remain unchanged durable objects
- the lease carries its own expiry and reason

Later:

```bash
anonsync override list --active
anonsync events --follow
```

The daemon should emit a clean `override.expired` / `effective-state.changed` sequence and the device should return to baseline policy without any hidden config drift.

## Flow 26 — retire a stolen or dead device without confusing cleanup, ignore, revoke, and replace

Problem: a laptop is stolen or a NAS dies. The operator needs to decide whether to merely hide the old device from ordinary lists, ignore future contact from it, revoke its existing authority, or bind a successor device into selected continuity.

```text
$ anonsync device show laptop-old --explain
Device: laptop-old
Trust class: trusted
Retirement status: active
Linked group: personal
Grants: 6
Approval-memory references: 2
Last seen: 2026-03-06T19:11:00-05:00

$ anonsync device retire laptop-old --intent revoke --reason "stolen on train" --plan
Plan: pln_01JRT...
Would create retirement record: rtr_01JRT...
Effects:
  - stop announcements for successorless device references
  - revoke 6 grants
  - revoke 2 approval-memory records
  - clear cached route preferences referencing laptop-old
  - leave historical audit and file-history records intact

$ anonsync plan show pln_01JRT...
Risk: medium
Old device may reconnect after network delay: yes, until peers observe revocation
Successor binding: none
Remote cleanup remaining: 2 peers have not yet observed the retirement

$ anonsync device replace laptop-old --successor laptop-new --plan
Plan: pln_01JRU...
Would create retirement record: rtr_01JRU...
Continuity review:
  - grants to rebind: 4
  - grants to revoke: 2
  - approval-memory to carry forward: 0
  - recovery bundle required: no

$ anonsync plan apply pln_01JRU... --yes
Applied. Retirement record rtr_01JRU... is active.

$ anonsync device retirement show rtr_01JRU...
Intent: replace
Subject: laptop-old
Successor: laptop-new
Grant action: rebind-to-successor
Approval action: revoke
Publication action: stop-announcing
Status: completed
Residual cleanup: one offline peer has not yet observed the retirement
```

What this demonstrates:

- the operator never has to pretend that “remove from list” and “revoke trust” are the same thing
- replacement continuity is reviewed before apply
- remote lag is visible instead of treated as mysterious ghost-device behavior
- the retirement record becomes the durable explanation surface for the exit

## Flow 27 — hand off a small-team share without turning everyone into owners

Problem: a project lead is leaving the share, but the team should not solve that by widening owner-equivalent authority across every linked device or by re-sharing the whole folder with a new key.

```text
$ anonsync stewardship show team-notes
Share: team-notes
Stewards: [lead-laptop]
Grantors: [lead-laptop]
Delegation policy: bounded
Max delegable role: collaborator
Handoff policy: dual-review
Candidate successors: [ops-nas, deputy-laptop]

$ anonsync stewardship plan-handoff team-notes --to deputy-laptop --reviewer ops-nas --plan
Plan: pln_01JRV...
Would update stewardship record: stw_01JRV...
Authority to transfer:
  - grant
  - revoke
Authority to retain:
  - none
Blocked by recovery/retirement state: no
Existing grants affected: 0
Approval-memory records to re-scope: 2

$ anonsync plan show pln_01JRV...
Risk: medium
Preconditions satisfied: yes
Effects:
  - deputy-laptop becomes steward for share team-notes
  - approval-memory scope narrows to successor steward set
  - lead-laptop keeps data access until retirement record completes

$ anonsync stewardship apply pln_01JRV... --yes
Applied. Stewardship record updated.

$ anonsync stewardship show team-notes --explain
Stewards: [deputy-laptop]
Grantors: [deputy-laptop]
Departure behavior for lead-laptop: freeze-grants until retirement completes
Last change provenance: plan pln_01JRV... by lead-laptop reviewed by ops-nas
```

What this demonstrates:

- share governance is not overloaded onto a coarse Owner bit
- a successor can be reviewed before authority moves
- data access and grant authority can diverge during the transition
- later audit can explain exactly how stewardship changed


## Flow 28 — attach a read-only mirror without choosing between silent desync and silent overwrite

Problem: an operator wants a non-authoritative mirror or backup target. They need to know whether accidental local edits will be preserved, auto-reverted, or block further pulls, instead of discovering that behavior from a mode-specific caveat later.

```text
$ anonsync deviation create --name mirror-flag --for receive-only --on-add preserve-and-flag --on-modify preserve-and-flag --on-delete re-fetch
Created deviation policy devpol_01JS0...

$ anonsync role create --name backup-mirror --perm ro --write-policy receive-only --mode full --deviation-policy mirror-flag
Created role rol_01JS0...

$ anonsync grant create project-archive --device backupbox --role backup-mirror
Created grant grt_01JS0...

$ anonsync mount show project-archive --device backupbox --explain
Mount: mnt_01JS0...
Role: backup-mirror
Write policy: receive-only
Deviation policy: mirror-flag
Local add: preserve-and-flag
Local modify: preserve-and-flag
Local delete: re-fetch
Remote progress while deviated: continue-with-warning
Forced by capability: no

$ anonsync status project-archive --device backupbox --explain
Status: degraded-by-local-deviation
Detected deviation:
  - path: reports/q4.csv
  - class: local-modify
  - propagation: blocked from leaving backupbox
  - local bytes preserved: yes
  - remote pulls continue: yes
Recommended actions:
  - review deviation
  - revert local copy
  - clone into conflict artifact
```

What this demonstrates:

- one-way or mirror behavior is not just “read-only plus folklore”
- the operator can inspect add / modify / delete remediation separately
- accidental local edits do not have to choose between silent sync breakage and silent destructive overwrite
- any forced stricter behavior is visible as capability-derived policy, not as a surprise side effect


## Flow 29 — adopt into a mac/windows-mixed path without learning case and Unicode collisions the hard way

Problem: the operator is about to adopt a share containing mixed-case names, decomposed Unicode names, symlinks, and xattrs onto a target path whose filesystem may not preserve all of those semantics.
They need a preflighted answer before creating a mount, not a pile of later `.Conflict`-style surprises.

```text
$ anonsync fs profile ~/Incoming/photos
Path: /Users/alex/Incoming/photos
Filesystem: apfs
Case sensitivity: insensitive
Unicode normalization: nfd
Symlink support: preserve
Junction support: blocked
xattr support: full
ACL support: partial
Timestamp precision: ns
Clock status: ok

$ anonsync fs compare --share travel-archive --path ~/Incoming/photos
Filesystem compatibility report: fsr_01JS9...
Status: warning
Path findings:
  - 2 case-only collisions would be blocked on target
  - 3 names require normalization rewrite to target form nfd
Metadata findings:
  - Windows-style junction entries in share cannot be preserved on target
  - 14 xattr keys will downgrade to portable subset
Recommended actions:
  - reject current path and choose case-sensitive target
  - or continue with explicit normalization policy portable-nfd
  - or strip unsupported metadata classes during adopt

$ anonsync fs explain fsr_01JS9...
Blocked patterns:
  - Reports/Q1.csv vs reports/q1.csv
Auto-correctable:
  - café.jpg -> café.jpg on target normalization
Downgrade consequences:
  - junction-like entries become ordinary directories: not allowed by default
  - xattr set portable-only removes non-portable keys on pull

$ anonsync mount adopt inc_01JS9... --path ~/Incoming/photos --plan --fs-report fsr_01JS9...
Plan: pln_01JS9...
Risk: medium
Preconditions:
  - fs report fsr_01JS9... still fresh
  - share path set unchanged since report generation
Policy deltas:
  - apply normalization policy portable-nfd
  - deny junction preservation on this mount
  - preserve xattrs only in portable subset
```

What this demonstrates:

- filesystem/path semantics are first-class compatibility state, not support lore
- pathname and metadata risk is visible before adoption commits
- auto-correctable rewrites are explicit policy, not magic side effects
- blocked patterns stay blocked until the operator chooses a safer target or different policy


## Flow 30 — hide build outputs from peers without guessing whether names still leak through as placeholders

Problem: a developer share contains `build/` and `.cache/` paths. The operator wants those paths suppressed from the share namespace peers learn about, and also wants a selective local mount on one laptop to omit them entirely instead of showing placeholder noise. They need to know what changes for peers, what changes only locally, and whether already-indexed structure requires review.

```text
$ anonsync projection show codebase
Share projection: prj_01JT1...
Default namespace visibility: visible
Default remote announcement: announce
Tighten behavior: review-existing
No explicit rules

$ anonsync projection test codebase build/output/app.tar
Path: build/output/app.tar
Share namespace visibility: visible
Remote announcement: announce
Local mount default projection: placeholder
Existing indexed structure: yes
Existing local bytes on this device: no
Review required if tightened: yes

$ anonsync projection add codebase --match 'build/**' --namespace hidden --announce suppress
Added rule prjr_01JT1...

$ anonsync projection add mnt_01JT1... --match 'build/**' --local omit
Added rule prjr_01JT2...

$ anonsync projection test codebase build/output/app.tar
Path: build/output/app.tar
Share namespace visibility: hidden
Remote announcement: suppress
Mount mnt_01JT1... local projection: omit
Existing indexed structure: requires review before full retraction
Suggested next step: plan projection-tighten codebase --path build/output/app.tar

$ anonsync plan create --action projection-tighten --share codebase --path build/output/app.tar
Plan: pln_01JT1...
Risk: medium
Effects:
  - stop announcing build/** to peers
  - omit build/** from mount mnt_01JT1...
  - leave already-materialized bytes on workstation-1 unchanged
  - mark previously indexed remote structure for review on peers that have already seen it
```

What this demonstrates:

- share-wide namespace suppression and local mount-view hiding are separate supported actions
- `projection test` answers both “will peers still see the name?” and “will this mount still show a placeholder?”
- tightening rules after indexing is explicit reviewable state, not hidden ignore-timing folklore
- local omission does not silently imply share-wide suppression, and share-wide suppression does not silently delete already-materialized local bytes


## Flow 31 — prove a share is settled enough for cutover instead of guessing from peer counts and warnings

Problem: an operator wants to relocate a mount and treat the current laptop copy as the handoff baseline. The share looks quiet in ordinary status output, but they need to know whether that really means "safe to cut over" or whether clock skew, watcher fallback, hidden merge work, or missing sources still weaken confidence.

```text
$ anonsync status
Shares:
  workdocs   idle   peers 2/3   warnings 1

$ anonsync converge show --share workdocs --intent cutover
Convergence report: cvr_01JU4...
State: degraded-converged
Confidence: medium
Reachable sources: 2 / 3 required
Detection mode: periodic-rescan
Watcher health: degraded
Clock health: ok
Background work: none
Blocking findings: none
Why not high confidence:
  - local watcher exhaustion detected; fresh local edits are only guaranteed on rescan
  - peer studio-nas currently unreachable, so remote completeness is known only for reachable peers
Suggested next step: raise watcher limit, force rescan, or lower required source set for cutover intent

$ anonsync doctor --share workdocs
Findings:
  - WATCHER_EXHAUSTED on laptop-1: local change detection degraded to periodic rescan
  - SOURCE_UNREACHABLE peer studio-nas for share workdocs

$ anonsync share rescan workdocs
Rescan queued

$ anonsync converge wait --share workdocs --intent cutover --timeout 10m
Waiting for: high-confidence convergence
...
Result: blocked
Reason codes:
  - SOURCE_UNREACHABLE
Suggested alternatives:
  - retry with --intent relocate-local-only
  - or mark studio-nas non-required for this cutover plan

$ anonsync converge show --share workdocs --intent relocate --json
{
  "state": "degraded-converged",
  "confidence": "medium",
  "required_sources": 3,
  "reachable_sources": 2,
  "watcher_health": "degraded",
  "detection_mode": "periodic-rescan",
  "blocking_findings": []
}
```

What this demonstrates:

- idle status and settlement confidence are different supported answers
- watcher exhaustion, missing sources, and hidden background work can lower confidence without necessarily meaning "actively syncing"
- a caller can wait for a required readiness level and get structured blocker reasons instead of hand-rolled polling
- cutover, backup, and relocate can demand stricter readiness than casual status inspection

## Flow 32 — keep WAN traffic overlay-first by default

Goal: confirm that a privacy-oriented policy uses Tor and/or I2P for WAN traffic and does not silently fall back to clearnet direct.

```text
anonsync policy create \
  --name privacy-mixed \
  --tor preferred \
  --i2p allowed \
  --clearnet-direct manual-opt-in \
  --dial-via lan-direct,tor,i2p,private-relay

anonsync share set workdocs --policy privacy-mixed
anonsync route show --share workdocs --explain
```

The surface is ready when:

- the policy says explicitly that WAN clearnet direct is manual-only
- route output says which overlay class is active and why
- no operator has to guess whether “direct” is active merely because transfer speed looks good

## Flow 33 — deliberately enable faster clearnet direct for one transfer window

Goal: allow a trusted peer/share to use faster direct WAN routing temporarily without silently rewriting the long-lived privacy stance.

```text
anonsync route allow-clearnet-direct \
  --share media \
  --peer studio-seed \
  --ttl 2h \
  --reason "trusted bulk transfer"

anonsync route show --share media --explain
anonsync override list
```

The surface is ready when:

- the output says direct clearnet is active because of a manual override
- the override has a visible expiry
- policy and effective-state views make it obvious that the durable baseline remains overlay-first

## Flow 34 — inspect bundled Tor/I2P runtime health on Linux

Goal: confirm that the transport engines shipped inside the AnonSync binary story are actually healthy and ready on this host.

```text
anonsync transport list
anonsync transport show tor
anonsync transport show i2p
anonsync doctor
```

The surface is ready when:

- `transport show` distinguishes compiled-in versus embedded-payload integration
- bootstrap and health findings are visible without debug logs
- doctor can say whether a missing privacy route is blocked by policy, bootstrap failure, or Linux-host filesystem/runtime problems



## Flow 35 — warm bundled privacy transports and inspect real session use

Goal:

- keep overlay routing as the default WAN posture
- confirm that the daemon is using inspectable bundled runtimes
- confirm that I2P is reusing a stable shared session instead of churning per transfer

Suggested flow:

```text
anonsync transport list
anonsync transport warm tor
anonsync transport warm i2p
anonsync transport session list
anonsync route show --share archive --decision-trace
```

Expected semantics:

- engine output distinguishes compiled-in versus embedded-helper runtime
- session output distinguishes warm runtime from active route participation
- route output shows whether overlay paths are currently viable and which session(s) they depend on
- operators can tell whether clearnet direct is absent because it is disabled by policy, not because the daemon silently forgot it exists

Expected operator answers from CLI alone:

- which privacy engines are merely installed versus actually warm
- which routes are currently active
- whether I2P is using a shared long-lived session
- whether any WAN direct path is active only because of a manual override

## Flow 36 — deliberately enable faster WAN direct for a short bulk-transfer window

Goal:

- keep privacy-default routing intact
- allow a trusted high-speed bulk copy over clearnet direct
- make the privacy trade explicit and temporary

Suggested flow:

```text
anonsync route show --share media --explain
anonsync route allow-clearnet-direct --share media --ttl 90m --reason "trusted bulk transfer"
anonsync route show --share media --decision-trace
anonsync override list
```

Expected semantics:

- the override is visible as a lease, not a hidden policy edit
- route output states that WAN direct is active because of a temporary operator choice
- decision trace shows which overlay candidates lost and why
- after lease expiry, normal overlay-first routing resumes automatically

## Flow 37 — probe a Linux target path before adoption and learn the support tier

Goal:

- adopt or relocate into a real Linux path safely
- know whether the target filesystem is first-class, warning-tier, or best effort
- surface xattr/ACL/symlink/pathname risk before commitment

Suggested flow:

```text
anonsync fs profile /srv/archive
anonsync fs support --path /srv/archive
anonsync fs compare --share archive --path /srv/archive
anonsync fs explain fsr_01J...
anonsync incoming adopt inc_01J... --path /srv/archive --mode selective --plan
```

Expected semantics:

- support output names the effective support tier
- compare output explains case, normalization, xattr, ACL, special-file, and symlink posture
- adoption requires or strongly prefers a fresh filesystem report when risk is non-trivial
- operators can block themselves from pretending that a weak target path is equivalent to ext4/xfs/btrfs

## Flow 38 — preview route exposure before adopting a WAN posture

Goal:

- understand who can learn reachability before a route policy is exercised
- separate baseline publication from temporary leases
- avoid reconstructing exposure from route symptoms after the fact

Suggested flow:

```text
anonsync exposure show --policy privacy-mixed
anonsync exposure show --share media --effective
anonsync route show --share media --decision-trace
```

Expected semantics:

- exposure output names the infrastructure classes that can currently learn reachability
- effective output shows whether a temporary route lease is widening the baseline stance
- the route decision trace and the exposure report agree on why a candidate is eligible

## Flow 39 — admit a peer-pinned direct path without enabling public direct everywhere

Goal:

- trust one peer at one address for one share window
- gain speed when appropriate
- keep ambient public direct disabled

Suggested flow:

```text
anonsync route known-host add \
  --peer laptop-ember \
  --addr sync.example.net:3847 \
  --share media \
  --ttl 7d \
  --reason "trusted home uplink"
anonsync exposure show --share media --effective
anonsync route show --share media --explain
```

Expected semantics:

- the new path is visible as a known-host record, not a hidden global preference change
- exposure output says that public direct is still not generally allowed
- route output can say when the peer-pinned path is the reason a direct candidate now exists

## Flow 40 — grant a bulk-speed exception that expires by time or bytes

Goal:

- temporarily allow faster public direct for a trusted transfer window
- keep that exception bounded enough that it cannot quietly become ambient policy

Suggested flow:

```text
anonsync route allow-clearnet-direct \
  --share media \
  --peer laptop-ember \
  --ttl 90m \
  --byte-cap 250GiB \
  --reason "trusted bulk transfer"
anonsync route lease show rls_01J...
anonsync route show --share media --decision-trace
```

Expected semantics:

- the speed exception is represented as a first-class route lease
- the lease shows both its expiry time and byte budget when present
- after lease exhaustion, the daemon re-evaluates the route against baseline policy without rewriting that baseline


## Flow 41 — review a newly contacting peer without silently linking or auto-sharing

Goal:

- inspect an unknown or newly introduced peer
- decide whether to trust, defer, quarantine, or ignore
- keep that decision separate from grants and mounts

Suggested flow:

```text
anonsync pending peer list
anonsync pending peer show ppd_01J...
anonsync pending peer accept ppd_01J... --as-contact alex --plan
anonsync plan show pln_01J...
anonsync plan apply pln_01J...
anonsync contact show alex --show-provenance
```

Expected semantics:

- the pending peer record explains whether the contact came from direct contact, linked-device introduction, or share announcement
- accepting the pending peer must say whether it will create only a contact, a link membership, a claim plan, or some combination
- no share grant or mount should appear merely because contact trust was accepted
- ignore and quarantine remain visible durable states, not silent disappearance

Expected operator answers from CLI alone:

- who surfaced this peer and why
- whether the peer was merely trusted as a contact or also linked into a constellation
- whether any future approval or introduction scope was created

## Flow 42 — allow bounded introductions for one trusted constellation without ambient auto-add

Goal:

- allow one trusted device group to surface additional peers for one narrow scope
- keep new peers staged in pending state unless stronger policy is explicitly reviewed
- prove the policy is narrower than Resilio-style ambient linked-device spread

Suggested flow:

```text
anonsync link show personal
anonsync link set personal --introduction-policy pending-only --plan
anonsync plan show pln_01J...
anonsync plan apply pln_01J...
anonsync pending peer list --watch
anonsync contact list
```

Expected semantics:

- the plan shows exactly which link or share scope receives introduction rights
- default outcome is a pending-peer record, not automatic grant or owner-like authority
- explain output shows who may introduce whom, and what happens next when they do
- successor replacement or contact ignore state should be able to narrow or suppress that behavior later

Expected operator answers from CLI alone:

- whether introductions are disabled, pending-only, share-scoped, or wider
- whether any newly surfaced peer automatically gained share visibility or only entered the queue
- how to revoke the policy cleanly without deleting the underlying link group


## Flow 43 — open the workbench and know what matters now

Goal:

- open the system and immediately see what is blocked, risky, or newly awaiting review
- avoid scanning every share and peer by hand
- keep the summary honest by letting every card point back to its real subject

Suggested flow:

```text
anonsync review list
anonsync review list --lane now
anonsync review show riv_01J...
anonsync review open riv_01J...
anonsync review snooze riv_01J... --for 2h
```

Expected semantics:

- the queue can summarize pending peers, incoming shares, stale plans, transport degradation, convergence blockers, conflicts, and successor reviews
- each card shows why it is in `now`, `soon`, or `quiet`
- `review open` jumps to the underlying object summary instead of mutating it
- dismissing or snoozing the card does not silently approve, reject, revoke, or delete the underlying subject

Expected operator answers from the interface alone:

- what needs action first
- what is merely informative background state
- which cards are presentation-only summaries versus direct pending decisions
- which proof objects are attached before any risky action is taken

## Flow 44 — read one share view without confusing visibility, mount state, authority, and delete scope

Goal:

- inspect a share and answer the dangerous questions from one coherent surface
- avoid jumping between unrelated commands or UI areas just to reconstruct the model

Suggested flow:

```text
anonsync share show vault --explain
anonsync mount list --share vault
anonsync exposure show --share vault --effective
anonsync converge show --share vault --intent cutover
anonsync file check vault Secrets/Taxes/report.pdf
```

Expected semantics:

- the share surface distinguishes visible-only state from adopted local mounts
- materialization mode is separate from authority and separate from route posture
- route/exposure output distinguishes durable policy from active leases or overrides
- convergence output says whether the share is settled enough for the chosen intent instead of only appearing idle
- file-check output attaches preservation evidence before any destructive local or share-wide action proceeds

Expected operator answers from the interface alone:

- is this share merely visible here or actually mounted
- how much of it is local right now
- who can mutate or delegate it
- whether current connectivity is baseline policy or temporary exception
- whether a delete/evict/restore action is safe, guarded, or blocked



## Flow 45 — review a proof-backed plan and apply it only while assumptions are still fresh

Goal:

- make risky apply operations feel reviewable rather than magical
- keep the proof panel, drift checks, and final apply step tied together

Suggested flow:

```text
anonsync mount compare workdocs --path /srv/team/workdocs
anonsync claim prepare --incoming inc_01J... --path /srv/team/workdocs --mode selective --plan
anonsync plan show pln_01J...
anonsync review home --lane now
anonsync plan apply pln_01J...
```

Expected semantics:

- the comparison report and preflight findings are attached to the plan rather than lost after preview
- the review/home surface can summarize the pending plan, why it matters now, and which proof objects back it
- `plan apply` checks object versions and proof freshness before mutating state
- if assumptions have drifted, apply fails explicitly and sends the operator back to refresh or re-prepare rather than proceeding optimistically

Expected operator answers from the interface alone:

- exactly what path binding or authority change this plan would perform
- which assumptions the plan depends on
- whether the proof is still fresh enough to trust
- what must be refreshed before apply is allowed


## Shared report triage sequence — inspect a risky or degraded state through one common report surface

Goal:

- encounter a guarded or blocked condition from any page or queue
- inspect proof without losing scope
- refresh stale findings when needed
- move toward the safest next action without warning archaeology

Suggested flow:

```text
anonsync home
anonsync report show rpt_01J...
anonsync report refresh rpt_01J...
anonsync report explain rpt_01J...
anonsync plan show pln_01J...
```

Expected semantics:

- the same report grammar works whether the underlying subject is `preflight`, `comparison`, `preservation`, `convergence`, or `plan-drift`
- report output states current answer, severity, freshness, scope, next-safe action, and unresolved aftermath in one stable order
- stale or drifted reports visibly downgrade apply confidence instead of quietly remaining actionable
- queue cards, share pages, and peer pages can all deep-link into the same report detail rather than inventing separate warning metaphors

Expected operator answers from CLI alone:

- what is true right now
- whether the finding is merely informative, guarded, high-risk, or blocked
- whether the report is still fresh enough to trust
- what safest next action the daemon recommends
- what still remains unresolved even if that action succeeds


## Flow 46 — inspect the active state root before trusting the current control surface

Goal:

- answer which durable state root is active right now
- confirm which runtime/service profile is controlling it
- avoid confusing “the app launched” with “the expected control universe is open”

Suggested flow:

```text
anonsync state show
anonsync state roots
anonsync state verify
anonsync audit --type state_root.verified
```

Expected semantics:

- `state show` prints active root ID/path, active service profile, identity fingerprint summary, and inventory counts
- `state roots` distinguishes active, attached-but-inactive, stale, and superseded roots
- `state verify` produces a current attestation rather than only a yes/no response
- audit can show whether this root was recently attached, moved, imported, or switched under a different profile

Expected operator answers from the interface alone:

- which state root is active
- whether the current profile is workstation, background-service, local-web, or maintenance
- whether this root was verified recently enough to trust
- whether there is another local root that looks temptingly similar but is not the active one

## Flow 47 — move a state root without turning “copy some files” into the recovery story

Goal:

- relocate the durable state root to a new path
- keep identity continuity explicit
- preserve rollback and post-move verification

Suggested flow:

```text
anonsync state show
anonsync state move-root --to /srv/anonsync/root --plan
anonsync plan show stp_01J...
anonsync plan apply stp_01J...
anonsync state verify
```

Expected semantics:

- move-root preparation emits a state-transition report and a plan rather than mutating immediately
- the plan states whether quiesce/restart is required and what rollback path exists
- apply produces before/after state snapshots and explicit audit entries
- post-move verify confirms that the same identity and inventory now live at the new root path

Expected operator answers from the interface alone:

- whether this is a true move of the current root or an attach/import of something else
- whether rollback is credible before commit
- which exact inventory and identity continuity the daemon expects to preserve
- whether the new root passed integrity verification after transition

## Flow 48 — switch runtime profile without silently opening a different state universe

Goal:

- change from workstation to background service or local-web profile deliberately
- keep semantics and active root legible
- avoid profile-switch surprises that look like missing shares or a fresh install

Suggested flow:

```text
anonsync state show
anonsync state switch-profile --to background-service --plan
anonsync plan show stp_01J...
anonsync plan apply stp_01J...
anonsync state show
```

Expected semantics:

- switch preparation says whether the target profile reuses the same root or requires explicit attach
- any listen-policy change, privilege narrowing/widening, or restart boundary is shown before apply
- apply emits service-profile switch events and preserves one common audit trail
- post-switch `state show` still makes the active root explicit so the operator can confirm they did not land in a clean or detached universe

Expected operator answers from the interface alone:

- whether the profile switch kept the same state root
- whether control-surface exposure changed
- whether mutation capabilities changed
- where to go next if the target profile cannot safely attach the intended root


## Flow 49 — repair a moved or missing path without re-adding the share

Goal:

- keep share continuity explicit
- prove whether a candidate path is really the same local mount
- avoid remove/re-add folklore when repair is possible

```text
anonsync mount doctor mnt_01J...
anonsync mount compare mnt_01J... --path /srv/workdocs
anonsync preserve show mnt_01J...
anonsync mount repair mnt_01J... --path /srv/workdocs --plan
anonsync plan show pln_01J...
anonsync plan apply pln_01J...
```

Expected behavior:

- `mount doctor` says whether the current problem is missing path, marker drift, or some stronger blocker
- `compare` shows whether the candidate path looks like the expected continuity target or a risky merge target
- `preserve show` makes rollback posture explicit before any cleanup or repair apply
- `repair --plan` keeps the same share lineage when that continuity can be proven
- the operator never has to treat “broken path” as synonymous with “brand new mount”

## Flow 50 — preview preservation before cleaning up broken local binding artifacts

Goal:

- make hidden-history assumptions explicit
- warn when cleanup would strand the easiest rollback path
- keep local surgery attached to recovery posture

```text
anonsync mount doctor mnt_01J...
anonsync preserve show mnt_01J...
anonsync file check workdocs Reports/Q1.xlsx --for remove-local
anonsync report show rpt_01J...
```

Expected behavior:

- the product says whether preservation comes from local history, replica-derived history, or almost nothing
- history limits such as peer-only capture or size caps are visible before cleanup
- risky cleanup actions point back to preservation evidence instead of filesystem ritual
- the operator does not learn rollback weakness only after the broken state has been “fixed”

## Flow 51 — detach a local path while keeping incoming visibility and recovery legible

Goal:

- separate local unbinding from forgetting the share
- preserve a future path back to adoption or repair
- avoid ambiguous `disconnect` semantics

```text
anonsync mount show mnt_01J...
anonsync preserve show mnt_01J...
anonsync mount detach mnt_01J... --keep-visible
anonsync incoming list
```

Expected behavior:

- detaching the local path does not revoke trust or erase share visibility by accident
- the post-detach state remains visible as incoming or otherwise explicitly re-adoptable
- preservation posture is still inspectable after detach
- later re-adoption or repair can point back to the previous binding receipt instead of pretending no local history existed


## Flow 52 — choose the right file-action scope without guessing from placeholder or mode state

Problem: the operator is looking at one path in a selectively materialized share and wants to reclaim space or delete the file everywhere. They must be able to tell whether the next action is local-only, share-wide, or really a restore path in disguise.

```text
$ anonsync file check vault Secrets/Taxes/report.pdf --for remove-share
Preservation report: prr_01JV4...
Risk: guarded
Known plaintext replicas online: 1
History candidates: 3
Recommended safer actions:
  - restore locally from hst_01JV4...
  - remove --scope local

$ anonsync file remove vault Secrets/Taxes/report.pdf --scope local
Local view removed. File-intent receipt: fir_01JV4...

$ anonsync file remove vault Secrets/Taxes/report.pdf --scope share --plan
Plan: pln_01JV4...
Intent: delete-from-share
Scope: replicated share
Attached proof: prr_01JV4...
```

What this demonstrates:

- local-only removal and replicated delete are separate supported actions
- the same path can surface different valid intents without overloading one `remove` verb
- preservation proof attaches before destructive scope expansion
- later audit can point to one file-intent receipt instead of reconstructing meaning from mode or UI path

## Flow 53 — resolve a receive-only deviation case without destroying local evidence by accident

Problem: a backup mirror received an accidental local edit. The operator wants to keep forensic evidence briefly, then restore ordinary receive-only behavior, without guessing whether Sync will silently revert, stall, or keep the edit forever.

```text
$ anonsync deviation case list --mount mnt_01JV5...
Deviation cases:
- devc_01JV5...  reports/q4.csv  local-modify  preserved  continue-with-warning

$ anonsync deviation case show devc_01JV5...
Deviation case: devc_01JV5...
Path: reports/q4.csv
Effective policy: mirror-flag
Suggested actions:
  - preserve-and-keep-blocked
  - copy-aside-and-revert
  - revert-local

$ anonsync deviation case resolve devc_01JV5... --action copy-aside-and-revert
Resolved. Local artifact copied aside to .anonsync/deviation-copies/...
Remote progress: continue-with-warning
File-intent receipt: fir_01JV5...
```

What this demonstrates:

- non-authoritative local drift is a real object, not just a status caveat
- the operator can choose whether local evidence survives
- deviation resolution emits the same kind of receipt trail as other scope-sensitive file actions
- read-only or mirror semantics do not have to collapse into silent overwrite or silent desync


## Flow 54 — inspect what “paused” actually means right now

Problem: a share or device is under an override or recurring window. The operator must be able to see whether uploads, downloads, scans, and delete propagation are all stopped, or only some of them.

```text
$ anonsync activity show --share vault
Activity state for share vault
- scan-index: active
- ingress-bytes: suspended
- egress-bytes: suspended
- delete-propagation: active
- announce-discovery: active
Current answer: Transfers suspended; scans and delete propagation still active.
Sources:
  - override ov_01JW0... (pause-transfer, expires 01:20)
```

What this demonstrates:

- the product does not stop at the word `Paused`
- transfer truth, scan truth, and delete truth are separately inspectable
- the operator can see which override created the current state and when it ends

## Flow 55 — create a recurring metered-link window without accidentally capping LAN too

Problem: a laptop is often on a weekday hotspot. The operator wants slower Internet transfers during work hours but does not want to throttle LAN sync at home.

```text
$ anonsync schedule create     --target device:laptop-ember     --preset metered-link     --route-class internet     --down 2MiB/s     --up 512KiB/s     --rrule 'FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=8,9,10,11,12,13,14,15,16,17'

Schedule window: swn_01JW0...
Next activation: 2026-03-17T08:00:00-04:00

$ anonsync schedule show swn_01JW0...
Preset: metered-link
Route-class scope: internet
LAN effect: none
Phases affected:
  - ingress-bytes: throttled
  - egress-bytes: throttled
  - scan-index: active
  - delete-propagation: active
```

What this demonstrates:

- recurring windows are first-class objects rather than hidden UI calendar state
- route-class scope stays explicit, so Internet and LAN behavior do not blur
- the operator can inspect the exact phase effect before the window ever activates

## Flow 56 — choose a stronger maintenance freeze deliberately

Problem: an operator is preparing a fragile maintenance window and wants a stronger guarantee than ordinary transfer pause. They need to know whether delete propagation also stops and whether that higher-risk choice is being made deliberately.

```text
$ anonsync schedule create     --target share:finance     --preset maintenance-freeze     --rrule 'FREQ=DAILY;COUNT=1;BYHOUR=23;BYMINUTE=0'     --plan

Plan: pln_01JW1...
Guard level: high
Why review is required:
  - delete-propagation would be suspended
  - background scans would remain visible but write effects would queue
  - peers may observe delayed destructive convergence

$ anonsync plan show pln_01JW1...
$ anonsync plan apply pln_01JW1...
```

What this demonstrates:

- stronger runtime freezes are separated from ordinary transfer pause
- the operator can see exactly which phases are being suppressed
- recurring windows and plan/apply can coexist without creating hidden durable drift

## Flow 57 — tighten namespace after indexing without pretending peers never saw the path

Problem: a team realizes `build/private/` should no longer be announced to peers. The tree was already indexed earlier, and one laptop once materialized part of it. The operator needs to know whether the new rule affects only future announcement, what still exists locally, and what receipt will prove the change later.

```text
$ anonsync projection test codebase build/private/release-notes.txt
Path: build/private/release-notes.txt
Share namespace visibility: visible
Peer announcement: announce
Mount mnt_workstation local view: placeholder
Local bytes on this device: absent
Visibility history: announced-remote
Review required if tightened: yes
Suggested next step: projection prepare-tighten

$ anonsync projection add codebase --match 'build/private/**' --namespace hidden --announce suppress-new
Added rule prjr_01JU9...

$ anonsync projection prepare-tighten codebase --path build/private/release-notes.txt --plan
Projection effect report: prjrep_01JU9...
Severity: guarded
Before:
  - peers can learn path names in build/private/**
  - workstation mount may still show placeholders
After:
  - future peer announcement suppressed
  - workstation mount remains placeholder until local tighten is reviewed
  - prior indexed visibility cannot be erased retroactively
Follow-up required:
  - review remote retraction posture
  - choose whether workstation should omit or preserve placeholder visibility

$ anonsync projection receipt show prc_01JU9...
Projection receipt: prc_01JU9...
Change class: namespace-tighten
Peer-facing effect: future announcement suppressed
Local-view effect: unchanged
Prior visibility history: announced-remote
Follow-up: review remote retraction posture
```

What this demonstrates:

- late tightening must distinguish future suppression from retroactive erasure
- peer namespace, local placeholder state, and local byte state are read together from one surface
- the resulting receipt explains what truly changed instead of forcing audit to infer from absent placeholders or rule text alone

## Flow 58 — hide clutter locally without changing what peers learn

Problem: a laptop user wants `.cache/` omitted locally because placeholder noise is distracting, but the share owner still wants peers to see the namespace and fetch files on demand elsewhere.

```text
$ anonsync projection test mnt_01JT1... .cache/pip/http-v2/index.json
Path: .cache/pip/http-v2/index.json
Share namespace visibility: visible
Peer announcement: announce
Mount local view: placeholder
Local bytes on this device: absent
Visibility history: announced-remote

$ anonsync projection add mnt_01JT1... --match '.cache/**' --local omit
Added rule prjr_01JV0...

$ anonsync projection explain --mount mnt_01JT1... --path .cache/pip/http-v2/index.json
Projection effect report: prjrep_01JV0...
Before:
  - peers learn the path name
  - this mount shows placeholder entries
After:
  - peers still learn the path name
  - this mount omits the path
  - no share deletion or remote suppression implied
Local bytes consequence: none (path already absent)

$ anonsync projection receipt show prc_01JV0...
Projection receipt: prc_01JV0...
Change class: local-tighten
Peer-facing effect: none
Local-view effect: omit instead of placeholder on mount mnt_01JT1...
```

What this demonstrates:

- local omission is a mount policy, not a share deletion
- the interface can prove “peers still see it” even when the local filesystem no longer does
- projection receipts keep later troubleshooting from misreading local cleanup as remote suppression


## Flow 59 — create a strict cutover barrier instead of trusting one nice-looking converge report

Problem: an operator wants to move a share from a laptop mount to a workstation mount and treat the laptop copy as the cutover baseline. They already have a convergence report, but they need a stronger public answer: all writable peers present, continuous detection healthy, evidence fresh, and a two-minute quiet window before the relocate plan may apply.

```text
$ anonsync settle policy create \
  --name cutover-strict \
  --intent cutover \
  --confidence high \
  --required-sources all-writable \
  --require-continuous-detection \
  --max-report-age 30s \
  --quiet-window 2m

Settlement policy created: stp_01JV...

$ anonsync settle barrier create --share workdocs --intent cutover --policy cutover-strict
Settlement barrier: stb_01JV...
State: pending
Waiting on:
  - quiet window 0 / 2m
  - writable peer studio-nas unreachable

$ anonsync settle barrier wait stb_01JV... --timeout 15m
Waiting for barrier stb_01JV...
...
State changed: pending -> satisfied
Evidence age: 9s
Quiet window: 2m / 2m
Writable sources: 3 / 3
Detection mode: continuous
Barrier expires: 2026-03-17T03:42:11-04:00

$ anonsync mount relocate --share workdocs --to /srv/workdocs --require-settlement cutover-strict --plan
Plan: pln_01JV...
Settlement requirement: satisfied via barrier stb_01JV...
```

What this demonstrates:

- convergence evidence and readiness policy are different objects
- quiet windows, evidence age, and witness/source rules are public state rather than operator folklore
- a future UI/TUI can use the same barrier object instead of inventing a second readiness heuristic

## Flow 60 — audit which readiness proof a destructive or continuity-sensitive action actually used

Problem: later, another operator wants to know whether a share-scope restore was applied under strict readiness or merely under a guarded degraded policy. Ordinary audit history says the restore happened, but the important question is what evidence standard backed it.

```text
$ anonsync audit --subject rst_01JV...
2026-03-17T03:48:09-04:00 restore.applied  rst_01JV...

$ anonsync settle receipt show --subject rst_01JV...
Settlement receipt: str_01JV...
Subject: restore rst_01JV...
Intent: restore
Policy: restore-safe
Accepted state: degraded-satisfied
Accepted confidence: medium
Accepted convergence report: cvr_01JV...
Accepted sources:
  - laptop-ember
  - backupbox
Missing but allowed:
  - cold-vault
Detection mode: continuous
Background work: none
Clock health: ok
Accepted at: 2026-03-17T03:48:07-04:00
Expires at: 2026-03-17T03:50:07-04:00
Note: cold-vault exempted by backup/restore witness policy

$ anonsync report show cvr_01JV...
Convergence report: cvr_01JV...
State: degraded-converged
Why degraded:
  - required source cold-vault offline
```

What this demonstrates:

- later audit can answer not just what changed, but under what readiness standard it changed
- guarded degraded acceptance is legible instead of hidden behind one generic “restore succeeded” line
- convergence report, settlement receipt, and audit history remain linked but distinct


## Flow 61 — inspect rollback provenance before restoring a file

Problem: an operator sees that a document changed unexpectedly and wants to know which peer/capture produced the recoverable version before doing anything that might rewrite replicated share state.

```text
$ anonsync file history workdocs Docs/spec.md --show-provenance
Path: Docs/spec.md
Candidates: 4

- hst_01JW1... remote-replaced
  captured_from: dev_alice_laptop
  captured_at: 2026-03-17T03:40:19-04:00
  retention_horizon: 2026-04-16T03:40:19-04:00
  allowed_scopes: mount-local, device-local, share-plan
  confidence: high

- hst_01JW2... conflict-candidate
  captured_from: dev_offline_editor
  captured_at: 2026-03-17T03:41:07-04:00
  allowed_scopes: device-local, share-plan
  confidence: guarded

$ anonsync file restore workdocs Docs/spec.md --entry hst_01JW1... --scope local
Restored locally.
Rollback receipt rrb_01JW3... emitted.

$ anonsync rollback receipt show rrb_01JW3...
Action: restore-local
Source: history-entry hst_01JW1...
Scope: device-local
Loser handling: left-intact
Outcome: applied
```

Expected semantics:

- history output is provenance-first, not just a pile of timestamps
- local restore is clearly separated from share-scope rewrite
- successful rollback emits a durable receipt that can be audited later without revisiting transient event logs

## Flow 62 — resolve a path-mapping conflict without deleting magic `.Conflict` files

Problem: a cross-platform share hits a case/unicode/path-mapping conflict. The operator must resolve it from one supported conflict case instead of manually moving “healthy” files around and hoping the suffixes mean what they think.

```text
$ anonsync conflict list --share design-assets
Open conflicts: 1

- cft_01JW4... path-mapping  Assets/Logo.svg
  class: case-insensitive collision
  candidates: 2
  recommended: prepare reviewed resolution

$ anonsync conflict show cft_01JW4... --history
Conflict: cft_01JW4...
Kind: path-mapping
Path: Assets/Logo.svg
Candidates:
  - cand_local_01 path=Assets/Logo.svg source=dev_macbook
  - cand_remote_02 path=Assets/logo.svg source=dev_linux_ws
History refs:
  - hst_01JW5...
  - hst_01JW6...
Safe actions:
  - choose canonical winner and rename loser aside
  - quarantine loser locally and continue

$ anonsync conflict resolve cft_01JW4... --winner cand_local_01 --loser-handling copy-aside --plan
Plan pln_01JW7... created.

$ anonsync plan apply pln_01JW7...
Applied.
Rollback receipt rrb_01JW8... emitted.
```

Expected semantics:

- the operator never has to treat a `.Conflict` filename as the public API
- the system explains conflict class, candidates, linked history, and loser handling explicitly
- the resulting resolution is provable later through a rollback receipt, not just a generic “conflict resolved” event


## Flow 63 — adopt onto an SMB/NAS target only after accepting warning-tier semantics deliberately

Problem: a team wants the convenience of binding a share onto an SMB-backed NAS path.
The operator does not merely need one warning that “SMB is quirky”.
They need to know whether notifications degrade to periodic rescan, whether the path is only warning-tier support, what pathname/metadata classes will be dropped or blocked, and what receipt will later prove those tradeoffs were accepted.

```text
$ anonsync fs profile /mnt/nas/projects
Path: /mnt/nas/projects
Filesystem: cifs
Case sensitivity: server-reported mixed
Unicode normalization: unknown
Symlink support: blocked
xattr support: partial
ACL support: partial
Notification posture: periodic-rescan
Support tier: warning-tier

$ anonsync fs compare --share project-ledger --path /mnt/nas/projects
Filesystem compatibility report: fsr_01JT4...
Status: warning
Path findings:
  - 2 symlink entries will be blocked by target policy
  - server path rules do not support strong native pathname guarantees
Metadata findings:
  - xattrs downgrade to portable subset
  - ACL fidelity is partial on target
Runtime findings:
  - change detection degrades to periodic rescan
  - target is network-backed and mixed local/direct access is disallowed

$ anonsync fs contract prepare --share project-ledger --path /mnt/nas/projects --policy smb-reviewed
Fidelity contract draft: fsc_01JT4...
Path semantics: mixed
Metadata semantics: portable-subset
Notification semantics: periodic-rescan
Network path state: network-reviewed
Accepted downgrade candidates:
  - symlink preservation blocked
  - xattr portable subset only
  - readiness policy must treat this mount as periodic-rescan

$ anonsync mount adopt inc_01JT4... --path /mnt/nas/projects --fs-contract fsc_01JT4... --plan
Plan: pln_01JT4...
Preconditions:
  - fs contract fsc_01JT4... still fresh
  - support tier remains warning-tier, not blocked
  - operator acknowledges network-reviewed posture
```

What this demonstrates:

- network-share convenience is a reviewed support posture, not a silent fallback
- degraded notifications become part of the contract and later readiness truth
- pathname/metadata downgrade is explicit policy, not post-hoc troubleshooting lore
- adoption can emit a fidelity receipt proving the warning-tier posture was knowingly accepted


## Flow 64 — detect that a once-healthy mount drifted into weaker filesystem semantics

Problem: a mount was originally adopted onto a healthy local path, but later the underlying target changed — perhaps permissions narrowed, the path is now backed by a network filesystem, or notifications degraded.
The operator needs a direct answer to “is the original fidelity contract still true?” rather than a pile of generic sync warnings.

```text
$ anonsync fs contract show media-archive
Fidelity contract: fsc_01JT7...
Mount: mnt_01JT7...
Path semantics: native
Metadata semantics: full
Notification semantics: continuous
Network path state: local-native
Verification state: fresh
Last verified: 2026-03-17T04:03:12-04:00

$ anonsync fs contract verify media-archive
Verification result: drifted
Drift case: fdc_01JT7...
Detected changes:
  - notification-loss
  - network-share-detected
Effect summary:
  - mount now depends on periodic rescan
  - support tier downgraded from linux-first to warning-tier
Blocked follow-up:
  - strict cutover barrier using this mount must refresh readiness under degraded detection
Recommended actions:
  - move mount back to local-native target
  - or accept new fidelity contract with receipt

$ anonsync fs drift show fdc_01JT7...
Severity: high
Affected semantics:
  - notification fidelity
  - support tier
  - readiness assumptions for maintenance/cutover
Next safe action: preview new contract or relocate mount

$ anonsync review home --lane now
1. Filesystem fidelity drift on media-archive (high)
   Previous contract no longer holds; readiness receipts depending on continuous detection are stale.
```

What this demonstrates:

- portability is a living contract, not just a bind-time report
- drift against the contract is visible as its own object
- later readiness, repair, and maintenance flows can depend on the updated fidelity truth
- the operator can prove whether they accepted the weaker posture or instead chose to relocate/repair


## Flow 65 — inspect why a device is low on space without guessing from hidden folders

Goal: answer “what is actually consuming space here?” without forcing the operator to infer from placeholders, hidden archives, or service-path lore.

Suggested path:

```text
anonsync space show
anonsync space pressure list
anonsync space pressure show spc_01J...
```

Expected UX semantics:

- the first view should break space down by byte class, not by implementation path
- the pressure case should name dominant classes such as materialized bytes, archive/history, temp-download remnants, logs, or state DB
- the output should say whether new materialization is merely discouraged, review-required, or blocked
- the next safe action should be a reclaim preview, not a generic “free disk space somehow” message

## Flow 66 — reclaim local space without turning it into replicated delete semantics

Goal: free meaningful local space while keeping the blast radius explicit.

Suggested path:

```text
anonsync space reclaim prepare --mount mnt_01J... --target-bytes 20GiB
anonsync report show rpt_01J...
anonsync space reclaim apply rcp_01J...
anonsync space receipt show rcr_01J...
```

Expected UX semantics:

- the reclaim preview should separate local materialized-byte eviction, temp cleanup, and retention trimming
- if rollback/history posture would weaken, the report should say so plainly before apply
- the flow must never silently widen into share-state deletion; replicated delete remains a separate file/share action model
- the receipt should state freed bytes actual, classes changed, and whether history/preservation posture changed


## Flow 67 — send a bounded share-access offer without making delivery encoding the real trust model

Goal:

- offer read-only access to one share
- pin the expected recipient
- keep expiry and use budget explicit
- avoid turning “copied a link” into hidden standing authority

Suggested flow:

```text
anonsync offer create --kind share-access --share vault --role readonly-viewer --delivery file --peer-pin fp_01Jalex --expires 7d --uses 1 --approval required --output ./vault-readonly.aso
anonsync offer show ./vault-readonly.aso
anonsync offer receipt list --subject shr_vault
```

Expected semantics:

- the artifact manifest renders the same authority no matter whether it is later reissued as file, URI, or QR
- output names expiry, use budget, peer pin, redelegation posture, and whether claim review will be required
- sender-side audit can later show whether the offer expired unused, was revoked, or produced a claim receipt

Expected operator answers from CLI alone:

- what exact capability is being offered
- whether the receiver may pass it onward
- when the artifact stops being redeemable
- which receipt would later prove consumption

## Flow 68 — receive an offer artifact and choose the local outcome before any real mutation

Goal:

- inspect an incoming capability artifact
- decide whether to stage visibility only or adopt into a local path
- avoid hidden authority or mount creation just because the artifact was delivered as a link or QR

Suggested flow:

```text
anonsync offer show ./vault-readonly.aso
anonsync claim prepare --offer ./vault-readonly.aso --path ~/Sync/Vault --mode selective
anonsync claim show clm_01J...
anonsync claim apply clm_01J...
anonsync claim receipt show clr_01J...
```

Expected semantics:

- inspection normalizes file / URI / QR delivery into one readable offer manifest
- claim preview states the intended local outcome before apply
- apply fails safely if expiry, peer pinning, redemption budget, or compatibility facts drifted
- later audit shows the claim receipt even if the original artifact was one-time and no longer exists

Expected operator answers from CLI alone:

- whether this artifact creates visibility only or a bound mount
- whether another approval or review step is still required
- whether the artifact is still valid to consume
- which durable receipt proves what local state was created


## Flow 69 — explain why one transfer is slow without reverse-engineering three settings pages

Goal:

- inspect one active transfer that feels unexpectedly slow
- determine whether route choice, cap, fairness, source absence, or disk pressure is the real bottleneck
- avoid using speed graphs and relay icons as the only explanation surface

Suggested flow:

```text
anonsync transfer list
anonsync transfer show trf_01Jbulk
anonsync transfer explain trf_01Jbulk
anonsync transfer policy show --share media
anonsync transfer budget show --share media
```

Expected semantics:

- `transfer explain` gives one current-answer sentence in operator language
- output names selected route class, any better rejected candidate, queue lane, and current bottleneck kind
- if the transfer is capped, the responsible budget and whether it is durable or temporary are named directly
- if the transfer is merely waiting on source availability, route or budget pages do not pretend otherwise

Expected operator answers from CLI alone:

- whether the transfer is on relay, overlay, or direct and why
- whether slowdown comes from budget, fairness, delay, source absence, or disk backpressure
- whether current behavior comes from durable policy or only a temporary window
- what change would most directly improve progress

## Flow 70 — apply a metered-share budget without mutating ambient route policy

Goal:

- keep one share usable over a hotspot week
- cap Internet throughput and relay spend for that share only
- avoid silently rewriting the device's broader route-permission posture

Suggested flow:

```text
anonsync transfer policy show --share media
anonsync transfer budget set --share media --internet-up 2MiB/s --internet-down 8MiB/s --relay-byte-budget 10GiB/day --reason "hotspot week"
anonsync transfer budget show --share media
anonsync transfer receipt show tbr_01Jmetered
```

Expected semantics:

- the new budget is visibly scoped to transfer throughput, not to route permission or trust scope
- LAN behavior can remain exempt if policy says so, and that exemption is rendered explicitly
- a receipt proves the metered budget was created and shows effective route scope and limits
- later expiry or cancellation of the budget also emits receipt-shaped state rather than disappearing into scheduler folklore

Expected operator answers from CLI alone:

- what exact throughput posture changed
- which route classes are capped and which are unaffected
- whether relay use is blocked, discouraged, or merely budgeted
- which receipt proves the hotspot policy actually took effect


## Flow 71 — acknowledge a high-signal condition without accidentally mutating the subject

Goal:

- inspect one high-signal attention event
- acknowledge or snooze it without silently approving, deleting, or resolving the underlying subject
- keep a durable receipt of what presentation changed

Suggested flow:

```text
anonsync attention list --lane now
anonsync attention show att_01Jhot
anonsync report show rpt_01Jhot
anonsync attention ack att_01Jhot
anonsync attention receipt show atr_01Jack
```

Expected semantics:

- `attention show` names the subject, report, lane reason, and delivery channels that carried the event
- the operator can see whether the safest next move is only acknowledgement or true subject resolution elsewhere
- `ack` records a receipt that says presentation changed while subject state did not
- later audit can prove who acknowledged the event and when, even after the workbench lane quiets down

Expected operator answers from CLI alone:

- what underlying report created this attention event
- whether acknowledgement changes only presentation or also resolves anything real
- which channels already carried the event
- which receipt proves the acknowledgement happened

## Flow 72 — configure headless-safe attention delivery without giving one client exclusive meaning

Goal:

- set attention policy for a Linux-first or headless deployment
- deliver guarded and blocked conditions somewhere reliable without making desktop toasts the semantic source of truth
- keep report meaning, lane placement, and delivery channel visibly separate

Suggested flow:

```text
anonsync attention policy show
anonsync attention policy set --headless-policy webhook-first --channel webhook --severity guarded,high-risk,blocked --dedupe-window 30m
anonsync attention policy show
anonsync attention list --lane now
```

Expected semantics:

- policy output names workbench lanes and delivery channels separately
- headless fallback does not erase the same event from the local workbench or CLI surfaces
- delivery failure remains visible as attention state rather than disappearing into daemon logs
- future acknowledgements still emit receipts even when the event first arrived through a webhook or browser session

Expected operator answers from CLI alone:

- which report classes leave the local workbench for external delivery
- what happens when a preferred channel fails
- whether Linux/headless deployments lose any semantic fidelity compared with richer clients
- which policy currently governs deduplication and quieting


## Flow 73 — review headless-safe remote control without opening ambient LAN exposure

Goal:

- reach a Linux-first daemon from another machine for administration
- keep the daemon itself local-only where possible
- make the exposure class, session scope, and resulting receipt explicit

Suggested flow:

```text
anonsync access show
anonsync access endpoint list
anonsync access expose plan --class ssh-tunnel-reviewed --reason "temporary remote administration"
anonsync plan show apl_01Jaccess
anonsync access expose apply apl_01Jaccess
anonsync access session list
anonsync access receipt show acr_01Jexpose
```

Expected semantics:

- the plan says whether the daemon stays loopback-only, expects an SSH-forward, or opens a broader network surface
- a reviewed exposure class is rendered directly instead of forcing the operator to infer it from bind addresses
- resulting sessions show endpoint, scope, and expiry without collapsing browser and CLI access together
- later audit can prove that remote administration used a bounded exposure change instead of an ambient LAN listener

Expected operator answers from CLI alone:

- whether control is still local-only or intentionally exposed
- which compensating posture the reviewed exposure expects
- who is connected now and through which endpoint
- which receipt proves the access change happened

## Flow 74 — rotate workbench/browser access without mutating unrelated daemon state

Goal:

- issue fresh interactive access for a workbench/browser client
- revoke stale browser or automation access cleanly
- avoid the kind of credential-repair ritual that resets preferences or duplicates device identity state

Suggested flow:

```text
anonsync access token issue --audience workbench --scope mutate --ttl 8h
anonsync access session list
anonsync access session revoke css_01Jstale
anonsync access token revoke tok_01Jold
anonsync access receipt show acr_01Jrotate
```

Expected semantics:

- token issuance is visible as credential state, not hidden as a browser-only login side effect
- session revocation does not pretend to revoke unrelated trust or identity state
- stale browser/workbench sessions can be removed without deleting settings bundles or moving the active state root
- the resulting receipt says exactly which token or session lost authority and which subjects were unaffected

Expected operator answers from CLI alone:

- which interactive credential is current
- which sessions still exist and with what scope
- whether revocation changed only control access or any real data/trust state
- which receipt proves the rotation happened

## Flow 74b — diagnose a missing browser control and repair access without storage surgery

Goal:

- learn whether a missing or broken browser/workbench control is policy denial or client degradation
- recover safe administration without relying on click-through trust ritual or deleting settings files
- keep auth repair bounded to control authority only

Suggested flow:

```text
anonsync access capability list
anonsync access integrity list
anonsync access integrity show cir_01Jbrowser
anonsync access repair open --kind session-rotate --endpoint cep_01Jloopback
anonsync access repair show arc_01Jbrowser
anonsync access repair apply arc_01Jbrowser
anonsync access receipt show acr_01Jrepair
```

Expected semantics:

- capability output says whether the missing action is actually forbidden or only degraded in the current browser/client posture
- integrity output says whether the problem is browser compatibility, content blocking, session expiry, trust/bootstrap failure, or something else
- the repair case states whether collateral effect is `none` or would require escalation into bring-up or state-root review
- applying the repair rotates only control authority and emits a receipt instead of resetting preferences or duplicating device identity state

Expected operator answers from CLI alone:

- what action was unavailable and why
- what browser-independent fallback exists right now
- whether the repair changes only access state or any broader durable state
- which receipt proves the repair happened

## Flow 75 — export a reviewed device-replacement bundle before hardware loss

Goal:

- package continuity prerequisites for one device before disaster
- verify what grants, identity continuity, and state-root assumptions the bundle actually covers
- avoid turning “copy the app state” into the unofficial recovery story

Suggested flow:

```text
anonsync recover posture show --device laptop-01
anonsync recover bundle export --type device-replacement --device laptop-01 --output ./laptop-01.arb
anonsync recover bundle show ./laptop-01.arb
anonsync recover bundle verify ./laptop-01.arb
anonsync recover receipt show rcr_01Jreplaceprep
```

Expected semantics:

- the bundle names whether it is portable, split-secret, or still daemon-bound in an important way
- verification says whether replacement is sufficient, partial, blocked, or stale
- continuity claims say what can carry forward and what will still require later review
- the receipt proves when this device last had a reviewed recovery posture

Expected operator answers from CLI alone:

- what would survive if this device died now
- whether the bundle is portable enough to use without the original daemon still running
- what future rotation or state-root change would invalidate it
- which receipt proves the current replacement-preparation posture

## Flow 76 — recover encrypted bytes without silently reviving old authority

Goal:

- restore bytes from an encrypted or detached recovery path
- keep byte recovery distinct from share authority, grant continuity, and later adoption into live sync state
- avoid turning decrypt success into an accidental trust or share-rebind event

Suggested flow:

```text
anonsync recover bundle verify ./vault.arb
anonsync recover decrypt-replica --input /srv/encrypted-vault --bundle ./vault.arb --output ./vault-restored
anonsync recover import ./vault-restored --mode local-only --plan
anonsync plan show pln_01Jlocalrecover
anonsync recover receipt show rcr_01Jdecrypt
```

Expected semantics:

- decrypt verification says whether bundle material is sufficient and whether any database dependency still remains
- decrypt success emits a receipt proving byte recovery, not automatic share-authority revival
- later import/adoption stays reviewed and can choose local-only, observe-only, or rebind-into-share paths explicitly
- continuity claims stay visible throughout instead of being inferred from a successful file output

Expected operator answers from CLI alone:

- whether the recovered bytes came from a supported workflow or an improvised one
- whether share authority or grants were changed at all
- what follow-up review is required before recovered bytes re-enter live sync state
- which receipt proves the exact recovery scope that just happened

## Flow 77 — preview a reviewed daemon upgrade before crossing a release boundary

Problem: an operator sees a new daemon build and wants to know whether this is just a routine restart, a guarded cutover, or a blocked migration because of edition family, schema, linked-constellation skew, or runtime-bundle mismatch.

CLI sketch:

```text
anonsync release check
anonsync release plan create --target stable-1.2.0
anonsync release plan show rup_01J...
```

Workbench sketch:

- open `Releases`
- select the daemon posture card
- compare current release against the proposed target
- inspect cutover scope, rollback posture, and compatibility findings before any apply action appears

The product should make clear:

- whether the target is merely newer or actually supported for this installation
- whether any peer or linked-device skew remains acceptable, guarded, or blocked
- whether schema change or state verification narrows rollback honesty
- which warnings would be accepted if the plan were later applied

Success criteria:

- the operator does not need platform-specific update pages or release notes to learn the actual compatibility boundary
- “update available” does not masquerade as “safe to cut over”
- rollback posture is visible before commitment, not after trouble

## Flow 78 — accept a guarded compatibility boundary without pretending the system is fully uniform

Problem: a trusted personal mesh or mixed deployment sometimes carries tolerated version or channel skew for a while. The operator needs to acknowledge that boundary honestly without pretending the constellation is now fully healthy or fully upgraded.

CLI sketch:

```text
anonsync release show --subject peer-constellation
anonsync release plan create --target stable-1.2.0 --allow-guarded-skew
anonsync release receipt show rlr_01J...
```

Workbench sketch:

- open `Releases`
- inspect the peer-constellation posture
- choose `Accept guarded boundary`
- read exactly which skew remains, what it affects, and when it must be revisited
- inspect the resulting receipt

The product should make clear:

- which subjects remain on older or different channels
- whether sync compatibility survives while linking/configuration or API posture remains guarded
- what expiry or next-review rule governs the accepted boundary
- that acknowledgement changed reviewed posture, not the actual installed versions

Success criteria:

- accepted skew remains visible in release posture instead of disappearing into a one-time dismissal
- acknowledgement creates a durable receipt rather than mutating hidden health state
- later operators can see what was accepted, why, and under what review horizon



## Flow 79 — explain why one share is behaving this way without reconstructing three settings layers

Goal:

- inspect a share that is throttled, relay-eligible, and partially pinned away from defaults
- answer which values come from defaults profile, which from share pinning, and which from temporary override
- avoid ambiguous “reset” folklore

Suggested flow:

```text
anonsync policy explain --share media
anonsync policy binding list --subject share:media
anonsync override list --active --subject share:media
anonsync policy receipt list --subject share:media
```

Expected semantics:

- the operator sees effective values together with per-field origin
- the output distinguishes durable inheritance from temporary override state
- pinned fields are visible as pinned rather than merely “different from default”
- prior receipts make clear when and why the subject stopped or resumed following defaults

Expected operator answers from CLI alone:

- why this share is currently throttled or relay-eligible
- which values are still inheriting from defaults profile
- whether a reset would return to inheritance or preserve an explicit null/pin
- what receipt proves the last policy-origin change

## Flow 80 — change a defaults profile without silently rewriting pinned subjects

Goal:

- change a defaults profile for a linked group or share class
- preview which existing subjects are eligible because they still inherit
- avoid silently mutating subjects that were intentionally pinned away from defaults

Suggested flow:

```text
anonsync defaults profile show personal-strict
anonsync defaults profile apply personal-strict --to link:personal --eligible-existing --plan
anonsync plan show pln_01J...
anonsync plan apply pln_01J...
anonsync policy receipt list --subject link:personal
```

Expected semantics:

- the preview distinguishes future-only impact from eligible existing inheriting subjects
- pinned subjects are listed separately and left untouched unless the operator chooses them explicitly
- apply emits durable policy receipts rather than silently updating background state
- later `policy explain` on any touched subject shows the new origin chain clearly

Expected operator answers from CLI alone:

- which subjects changed because of the defaults-profile update
- which subjects stayed unchanged because they were pinned
- whether any temporary override still masks the newly changed default
- what receipt proves the scoped defaults change later


## Flow 81 — collect a reviewed evidence bundle for a stuck share without exporting unrelated secrets

Goal:

- open a diagnostic incident from a share or transfer that is repeatedly failing
- collect logs, events, transfer explanation, and optional per-file diagnostics for one bounded window
- inspect redaction findings before sealing/export

Suggested flow:

```text
anonsync diagnostic incident open --subject share:media --kind transfer-slow
anonsync diagnostic depth set dgi_01J... --to elevated --for 30m
anonsync evidence bundle collect --incident dgi_01J... --classes events,recent-logs,transfer-samples,policy-explanation --plan
anonsync evidence bundle show evb_01J...
anonsync evidence bundle seal evb_01J...
anonsync evidence receipt show evr_01J...
```

Expected semantics:

- the operator can see which evidence classes were included and which were deliberately omitted
- redaction findings name paths, peer identities, addresses, or secrets that were tokenized, blocked, or still need review
- sealing the bundle emits a receipt instead of silently dropping a zip somewhere near daemon state
- incident scope remains visible so later audit can tell which problem the bundle was collected for

Expected operator answers from CLI alone:

- what evidence window was collected and at what diagnostic depth
- what redaction profile was applied before sealing
- whether any sensitive material blocked export or required explicit review
- what receipt proves that the bundle was sealed for later export or destruction

## Flow 82 — raise temporary diagnostic depth and return to baseline without leaving sticky debug state behind

Goal:

- investigate an intermittent problem that needs higher-verbosity logs for a short period
- avoid leaving verbose tracing enabled indefinitely after the incident window closes
- keep the depth change receipt-bearing and inspectable from any surface

Suggested flow:

```text
anonsync diagnostic incident open --subject peer:laptop --kind connectivity
anonsync diagnostic depth set dgi_01J... --to trace --for 15m
anonsync diagnostic incident show dgi_01J...
anonsync logs tail --incident dgi_01J...
anonsync diagnostic depth set dgi_01J... --to baseline
anonsync evidence receipt list --incident dgi_01J...
```

Expected semantics:

- diagnostic depth changes show explicit expiry instead of acting like hidden global debug mode
- returning to baseline emits a receipt rather than being lost in process logs
- the incident keeps a durable record of when elevated tracing was active and for what reason
- headless/Linux operators get the same truth without needing a tray menu or advanced settings page

Expected operator answers from CLI alone:

- whether higher-verbosity logging is active right now
- when it will expire if not lowered manually first
- which incident justified the temporary change
- what receipt proves that verbose logging was later turned back down


## Flow 83 — create a reviewed maintenance exception without forgetting what baseline will resume

Problem: an operator is about to work from a fragile hotel uplink. They want temporary throttling and upload drain on one share without silently rewriting durable transfer or route policy.

CLI:

```text
anonsync override create --target share:media --mode throttle --down 4MiB/s --up 1MiB/s --ttl 6h --reason "hotel uplink" --plan
anonsync override show ov_01JX1...
anonsync activity show --share media --effective
anonsync override receipt show ovr_01JX1...
```

Workbench:

- open `Exceptions`
- create a new override on `media`
- review baseline transfer policy versus temporary effective cap
- apply the override
- verify the receipt and expiry horizon

Expected semantics:

- the baseline transfer policy remains visible and unchanged
- the override shows exactly which phases or caps differ now
- the override has a real expiry and receipt instead of one sticky settings mutation
- `activity` and `policy explain` both point back to the active override rather than pretending the cap is durable

## Flow 84 — audit all active exceptions before leaving a risky environment

Problem: before shutting a laptop and leaving a temporary workspace, the operator wants one answer to “what unusual posture is still active?” without manually visiting route, diagnostics, access, and activity pages one by one.

CLI:

```text
anonsync override list --active
anonsync override explain ov_01JX1...
anonsync override cancel ov_01JX1...
anonsync override receipt show ovr_01JX2...
```

Workbench:

- open `Exceptions`
- filter to `expiring-soon`, `no-expiry-ack`, and `high-consequence`
- inspect any overlap between route, diagnostic, and access exceptions
- cancel the ones that should end now
- verify the resulting receipts

Expected semantics:

- one page can enumerate every active temporary exception family affecting this machine
- overlapping exceptions are explained instead of left to operator memory
- canceling a lease restores baseline or next scheduled posture explicitly
- later audit can prove which exceptions were still active when the operator left the environment


## Flow 85 — tighten one appliance-like member inside a personal constellation without breaking the constellation

Problem: a personal mesh contains a laptop, a phone, and a NAS-like appliance. The operator wants the appliance to stay in the same reviewed constellation while defaulting new shares to detached/incoming-only posture instead of ambient writable visibility.

CLI:

```text
anonsync constellation show cst_01J...
anonsync constellation member show mem_nas01
anonsync constellation member class set mem_nas01 --to appliance --plan
anonsync constellation visibility-default set mem_nas01 --to incoming-only --plan
anonsync constellation authority show --share projects
anonsync constellation receipt show csr_01J...
```

Workbench:

- open `Constellation`
- inspect the `nas01` member drawer
- compare current authority/visibility against the proposed appliance posture
- apply the reviewed change
- verify the resulting receipt and updated authority-domain view

Expected semantics:

- the member remains in the same constellation instead of being forced into “not my device anymore”
- default visibility tightening is visible separately from per-share writable role
- authority-domain views show what the appliance can still do on existing important shares
- later audit can prove when the member stopped receiving ambient writable visibility by default

## Flow 86 — check whether a disconnect or removal action is local or constellation-wide before applying it

Problem: a share is present across several linked personal devices. The operator wants to disconnect it on one member without accidentally revoking or removing it across the whole constellation.

CLI:

```text
anonsync constellation authority show --share media
anonsync incoming show media --member mem_phone01
anonsync share disconnect media --member mem_phone01 --plan
anonsync plan show pln_01J...
anonsync constellation receipt show csr_01J...
```

Workbench:

- open `Constellation`
- select `media` in the authority-domain view
- inspect scope-risk findings for the requested disconnect
- confirm that the action is member-local rather than constellation-wide
- apply only after the scope summary matches intent

Expected semantics:

- the operator can see the exact blast radius before apply
- a member-local disconnect does not masquerade as a share-wide revocation
- any constellation-wide consequence is reported as a guarded or blocked scope-risk finding
- receipts later prove whether the action was local-only, member-wide, or share-wide


## Flow 87 — preview what a route/discovery policy really publishes before applying it

Problem: an operator wants to enable a faster or more convenient path, but they need to know whether that widens identity disclosure, share-membership disclosure, endpoint disclosure, or only route eligibility.

```text
$ anonsync disclosure preview   --policy travel-quiet   --announce-via private-discovery,lan   --dial-via known-host,private-discovery

Disclosure preview for policy: travel-quiet

Audience matrix:
- local-broadcast-domain -> device-stable-id, share-membership, local-ip, listen-port
  via: lan-broadcast
- private-infra -> device-stable-id, overlay-endpoint
  via: private-discovery
- named-endpoint -> none (no new named endpoint disclosure)
- public-infra -> none

Route effect:
- direct LAN candidate enabled
- WAN remains private-discovery/known-host only

Widening steps introduced:
- local broadcast domain can now learn share-membership for eligible shares

Residual change if later narrowed:
- recent LAN announcements may remain observable until quiet window passes

Recommended next action:
- review LAN audience scope on shares tagged travel-safe before apply
```

Desired properties:

- the operator learns not only that LAN speed may improve, but what new audience/fact classes are disclosed
- preview output keeps disclosure and routing in the same view without collapsing them into one answer
- public-infrastructure disclosure remains visibly separate from LAN or private-infra disclosure

## Flow 88 — narrow publication before travel and prove what residue still remains

Goal: leave a risky network environment with future public discovery disabled, known residue named honestly, and receipts proving what was narrowed versus what merely needs time or clearance.

```text
$ anonsync disclosure preview --policy travel-quiet --disable-lan --disable-public-tracker --clear-cache

Disclosure preview for policy: travel-quiet

After apply:
- local-broadcast-domain -> none
- public-infra -> none
- private-infra -> overlay-endpoint only

Residual disclosure findings:
- cached-endpoint: one retained public endpoint record may persist until cache clear completes
- recent-lan-announcement: decay expected after quiet window

Required clearance actions:
- clear retained endpoint cache
- wait 2m quiet window before claiming zero LAN residue

$ anonsync policy apply travel-quiet --plan
$ anonsync disclosure residue list
$ anonsync disclosure receipt show dsr_01J...

Disclosure receipt: dsr_01J...
Action: narrow-publication
Residual delta:
- public tracker publication stopped
- LAN announcement stopped
- residual findings remaining: 2
Next safe claim:
- no future public publication
- zero-residue claim not yet valid
```

Desired properties:

- “off” does not lie about residue that still needs time or explicit clearing
- the operator can prove later that future publication stopped even if older residue had not yet decayed
- receipts keep policy narrowing and residue-clearing as related but distinct operator actions


## Flow 89 — decommission a workstation before sale without confusing cleanup, revocation, and continuity

Problem: a laptop is about to be sold or donated. The operator wants it out of active use, wants trust and sessions revoked, wants unnecessary local bytes cleaned up, but still wants an explicit record of what recovery material or remote residue remains.

```text
$ anonsync exit prepare daemon self --intent decommission --preserve recovery-only --clear local-history --plan
Would create exit plan: exp_01JXQ...
Intent: decommission
Subject: daemon-self on laptop-ember

Would stop now:
  - 3 active control sessions
  - 2 access tokens
  - future share publication from this node
  - future sync participation for 12 mounted shares

Would preserve intentionally:
  - 2 sealed recovery bundles
  - successor suggestion for office-laptop-new

Residual findings:
  - 1 offline peer may still remember this device until next observation
  - 4 hidden archive directories will remain unless explicit erase-local-residue is added

Apply blocker: none
```

```text
$ anonsync exit apply exp_01JXQ...
Applied exit plan: exp_01JXQ...
Exit receipt: exr_01JXQ...
Residual findings open: 2
```

```text
$ anonsync exit receipt show exr_01JXQ...
Intent: decommission
Authority ended: sessions, tokens, share participation
Continuity preserved: 2 recovery bundles retained
Residue remaining:
  - offline-peer-memory on dev_01JR...
  - intentionally-preserved-bytes in local archive paths
Safest next action: erase-local-residue --receipt-linked
```

What this flow proves:

- decommission is not the same as “delete everything”
- local cleanup, trust revocation, and continuity preservation stay legible as separate outcomes
- the operator gets one durable receipt instead of support-lore confidence

## Flow 90 — retire an encrypted backup-style replica without pretending authority and byte cleanup are the same thing

Problem: an encrypted replica on a rented VPS is being retired. The operator wants future participation and publication ended, wants to keep the trusted peers intact, and wants a clear answer about what ciphertext bytes or disclosure residue remain after shutdown.

```text
$ anonsync exit prepare device dev_vps9 --intent revoke-authority --scope share:archive --plan
Would create exit plan: exp_01JXR...
Intent: revoke-authority
Subject: device dev_vps9 on share archive

Would stop now:
  - future encrypted-replica participation on share archive
  - direct/publication routes for dev_vps9
  - recovery preference that counted this replica as available witness

Would preserve intentionally:
  - trusted peers and grants on other devices unchanged
  - local recovery bundles on trusted peers unchanged

Residual findings:
  - provider cache may still retain recent endpoint disclosure for up to TTL window
  - ciphertext bytes on remote disk remain until erase-local-residue is separately applied or externally verified
```

```text
$ anonsync exit apply exp_01JXR...
Applied exit plan: exp_01JXR...
Exit receipt: exr_01JXR...
```

```text
$ anonsync exit residue list --subject device:dev_vps9
exd_01JXR1  cached-publication        clearability: time-bound
exd_01JXR2  intentionally-preserved-bytes  clearability: operator-clearable
```

What this flow proves:

- replica retirement can end future authority without pretending remote bytes vanished already
- disclosure residue and byte residue remain separate public facts
- the operator can keep continuity on trusted peers without re-learning support ritual about what “remove” meant

## Flow 91 — review a workstation decommission in the workbench before apply

Problem: a Linux workstation is being retired. The operator must confirm what really stops, what local state intentionally stays, and what residue remains, without depending on a desktop-only dialog or support ritual.

```text
Workbench → Exits & Replacement → Drafts → workstation-lab-03

Intent: Decommission
Subject: device/workstation-lab-03
Scope chips: local, constellation, remote
Risk: high
Freshness: ready (proof checked 2m ago)

Stops now
- local control sessions from this device
- future share mutations from this device identity
- 3 direct-route leases referencing this device

Stays intentionally
- encrypted recovery bundle rec_01JW...
- file-history receipts already captured in audit
- local byte archive kept until reclaim plan is reviewed

Residue after apply
- 2 offline peers may still remember this device until they observe revocation
- one private relay cache entry may persist until TTL expiry

Follow-up options
- prepare successor binding
- rotate portable access token tok_01JV...
- create reclaim plan for preserved local bytes

Receipt promise
- exit receipt will prove decommission intent, preserved continuity, and unresolved residue

Primary action: Decommission device
Secondary: Preview successor handoff
Danger note: local byte cleanup is NOT included in this plan
```

What this demonstrates:

- the workbench uses the same stop/stay/residue/follow-up grammar as textual surfaces
- preserved continuity and preserved bytes stay visible instead of hiding behind one remove verb
- residue is part of the main review, not a footnote after apply

## Flow 92 — render the same exit plan in CLI and workbench without semantic drift

Problem: an operator previews an exit plan in the workbench, then later checks the same plan over SSH from a textual surface. The meaning must not change.

```text
$ anonsync exit show exp_01JWX... --view review
Intent & scope
  Subject: device:workstation-lab-03
  Intent: decommission
  Scope: local + constellation + remote-observation

Stops now
  [local] control sessions from this device
  [constellation] authority to mutate 4 shares
  [remote] future direct-route dialing toward this device identity

Stays intentionally
  [local] encrypted recovery bundle rec_01JW...
  [local] preserved archive bytes pending reclaim review
  [audit] prior history receipts remain searchable

Residue after apply
  [time-bound] relay cache TTL remains active
  [remote] 2 offline peers have not yet observed revocation

Follow-up options
  rotate token tok_01JV...
  prepare successor binding
  prepare reclaim plan

Receipt promise
  exr_01JWY... will record intent, preserved continuity, and unresolved residue
```

What this demonstrates:

- layout may compress, but section order and meaning stay fixed
- a Linux/headless operator gets the same safety-critical truth as the richer workbench
- no channel is allowed to turn a decommission review back into an ambiguous remove action


## Flow 93 — render the same claim/adoption review in CLI and workbench without semantic drift

Problem: an operator inspects an incoming share from the workbench, then later rechecks the same prepared claim over SSH. The way-in truth must not change by channel.

```text
$ anonsync claim show clm_01K2... --view review
Source & offer
  Source: incoming share inc_01K1... from contact:alex
  Visibility origin: linked-group:personal
  Offered role: rw

Local outcome
  Target action: incoming-adopt
  Requested role: laptop-cache
  Requested mode: selective

Path & filesystem
  Requested path: /srv/media
  Path state: non-empty
  Compare report: cmp_01K3...
  Filesystem contract: fsc_01K4... (native, warning-free)

Authority delta
  Local mount will be created
  No new re-share authority will be granted

Blockers & drift
  none

Receipt promise
  clr_01K5... will record source, accepted path, mode, and authority outcome
```

What this demonstrates:

- `incoming`, portable `offer`, and prepared `claim` can collapse to one fixed intake grammar
- a Linux/headless operator gets the same acceptance truth as the richer workbench
- no channel is allowed to turn a reviewed intake back into an ambiguous `Connect` prompt



## Flow 94 — render the same successor-cutover review in CLI and workbench without semantic drift

Problem: an operator imports recovery material for a replacement laptop, previews the cutover in the workbench, and later rechecks the same prepared plan over SSH. The continuity truth must not change by channel.

```text
$ anonsync plan show pln_01K9... --view review
Predecessor & candidate
  Predecessor: dev_laptop_old (retired, last seen 18d ago)
  Candidate: dev_laptop_new (fresh identity, bundle verified)

Continuity carry-forward
  Carry: share membership for 6 subjects
  Freeze: future approvals until post-cutover review
  Re-verify: 2 known-host direct paths

State-root & runtime target
  Target root: srt_01KA... (/var/lib/anonsync/main)
  Runtime target: svc_background
  Root posture: same inventory restored from verified bundle

Share / grant / authority rewrite
  Rebind 6 grants from dev_laptop_old -> dev_laptop_new
  Do not widen re-share or successor authority

Residue & revocation
  1 offline predecessor may still retain stale route cache until observation
  Local preserved bytes on old machine are unknown/offline

Receipt promise
  rcr_01KB... will prove predecessor, candidate, carry-forward, rewrite scope, and unresolved residue
```

What this demonstrates:

- successor replacement and continuity-sensitive re-home work can collapse to one fixed cutover grammar
- a Linux/headless operator gets the same continuity and residue truth as the richer workbench
- no channel is allowed to turn a reviewed cutover back into installer or migration folklore


## Flow 95 — review a suspected stolen-device response without confusing freeze, revoke, rotate, and replacement

Problem: a laptop is missing. The operator wants immediate containment, wants to know what can freeze now, wants later revocation and identity rotation handled honestly, and may still want a reviewed successor path if the device is truly gone.

```text
Workbench → Exits & Replacement → Compromise Cases → missing-laptop-ember

Trigger & scope
- suspected theft reported 11m ago
- primary subject: device/laptop-ember
- related subjects: 2 access tokens, 3 active sessions, 1 portable offer, 4 share grants

Immediate freeze
- stop new control sessions from laptop-ember
- suspend future approvals originating from laptop-ember
- pause direct-route leases referencing laptop-ember

Revocation & rotation
- revoke 2 access tokens
- revoke 1 portable offer that is still valid
- prepare identity rotation for constellation/personal
- do not yet revoke 4 share grants until successor decision is reviewed

Continuity & successor
- recommended next path: prepare successor for office-laptop-new
- carry-forward candidate exists from verified recovery bundle rec_01M1...
- clean-break alternative remains available

Residue & observation
- 1 offline peer has not yet observed the freeze
- local archive bytes on missing laptop remain unknown
- relay cache residue may persist until TTL expiry

Receipt promise
- cpr_01M2... will prove immediate freeze, revoked artifacts, pending rotation, and unresolved residue

Primary action: Apply containment
Secondary: Prepare successor
Danger note: erase-local-residue is NOT possible from this draft
```

What this demonstrates:

- suspected compromise is not the same as confirmed revocation
- immediate freeze, later rotation, and successor continuity stay visibly distinct
- the workbench does not force the operator to reconstruct containment meaning from unlink, uninstall, or relink ritual

## Flow 96 — render the same compromise review in CLI and workbench without semantic drift

Problem: an operator opens a compromise case in the workbench, then later rechecks the same prepared case over SSH. The incident truth must not change by channel.

```text
$ anonsync compromise show cpc_01M1... --view review
Trigger & scope
  Trigger: suspected theft
  Subjects: device:laptop-ember, token:tok_01M0..., offer:off_01M0...
  Posture: probable

Immediate freeze
  [local] new control sessions from laptop-ember blocked
  [share] future approvals from laptop-ember suspended
  [route] direct-route leases referencing laptop-ember paused

Revocation & rotation
  revoke token tok_01M0...
  revoke offer off_01M0...
  prepare rotate-identity for constellation personal
  keep share grants frozen pending successor decision

Continuity & successor
  successor candidate: dev_office_laptop_new
  verified bundle: rec_01M1...
  clean-break alternative remains available

Residue & observation
  [remote] 1 offline peer has not yet observed the freeze
  [unknown] local bytes on missing device cannot be attested
  [time-bound] relay cache TTL still active

Receipt promise
  cpr_01M2... will record freeze effects, revoked artifacts, pending rotation, and unresolved residue
```

What this demonstrates:

- compromise response can collapse to one fixed review grammar
- a Linux/headless operator gets the same containment and residue truth as the richer workbench
- no channel is allowed to turn a reviewed compromise case back into unlink/uninstall/reshare folklore


## Flow 97 — review a long-offline device return without confusing visibility, chronology, and writable replay

Problem: a laptop that was hidden from the device list months ago suddenly comes back online. The operator needs to know whether this is just harmless visibility, whether its edits can be trusted chronologically, whether its announced bytes are still real, and whether the next step is resume, quarantine, or escalation.

```text
Workbench → Reports → Re-entry Cases → laptop-ember-return

Subject & dormancy
- subject: device/laptop-ember
- last seen: 46d ago
- previous posture: hidden from list, not unlinked
- related shares: vault, photos, workdocs

Chronology & evidence
- local clock now within 2s of quorum
- remote last-observed clock drift was 11m at prior disconnect
- chronology confidence: guarded until fresh scan completes

Authority & scope
- proposed default: resume as reader only
- writable replay for vault/workdocs is blocked pending review
- successor diversion remains available if this is really a replacement case

Divergence & availability
- 14 files changed locally while device was offline
- 3 announced placeholders on photos have no live source yet
- 1 path on workdocs collides with later online rename

Admissible actions
- guarded resume as reader
- open merge review for vault/workdocs
- quarantine device and escalate to compromise
- divert to successor-cutover review

Receipt promise
- rer_01N3... will prove dormancy facts, chronology posture, allowed authority, and unresolved divergence
```

What this demonstrates:

- “device reappeared” is not yet the same as “safe to resume as writer”
- chronology confidence and source reality stay visible before replay authority returns
- the workbench can branch cleanly into merge, compromise, or successor handling without pretending stale return is one generic status update

## Flow 99 — review a destructive delete/overwrite wave before allowing replay

Problem: a share suddenly wants to delete or overwrite a large amount of local state. The operator needs to know whether this is ordinary expected propagation, whether any preserved copy still exists, whether source confidence is strong enough to trust the wave, and whether the safest next action is apply, narrow, freeze, or escalate.

```text
$ anonsync destructive open media-archive --reason remote-delete-wave --plan
Destructive replay case created: drc_01N4...

$ anonsync destructive show drc_01N4... --view review
Trigger & scope
- share: media-archive
- trigger: remote delete wave observed over 11m window
- candidate sources: editor-laptop, render-node
- affected paths: 1,842 deletes, 36 replacements
- protected scope hits: 4 paths under contracts/

Destructive effect summary
- local materialized bytes affected: 128 GiB
- placeholders only: 612 paths
- receive-only mirrors impacted: 3 peers
- max single-directory blast radius: 71% of current tree under exports/2026-03-17/

Preservation & recoverability
- rollback witness: guarded
- local retained history: present on this node for 14d
- remote preserved copy: unavailable on render-node (archive disabled)
- 22 paths would have no verified recovery path beyond current local bytes

Authority & source confidence
- source confidence: guarded
- contributing writer set includes editor-laptop returning after 9d absence
- settlement posture: degraded-satisfied, not strict
- suspicion note: delete density exceeds 30d baseline by 41x

Admissible actions
- freeze destructive replay now
- allow non-destructive sync only
- require stronger witness and reopen review
- escalate to compromise or re-entry review
- apply reviewed replay for non-protected paths only

Receipt promise
- drr_01N4... will record accepted destructive scope, preserved recovery posture, confidence level, and any frozen/escalated remainder
```

What this demonstrates:

- destructive propagation is not the same thing as ordinary transfer progress
- pause, preservation, source confidence, and suspicious-wave posture stay separate before consent
- the workbench can branch into freeze, narrower apply, re-entry, or compromise without pretending every delete wave is routine maintenance

## Flow 100 — render the same destructive-replay review in CLI and workbench without semantic drift

Problem: an operator previews a delete wave in the workbench, then later rechecks it from SSH on a headless Linux box. The destructive-replay truth must not change by channel.

```text
$ anonsync destructive show drc_01N4... --view review
Trigger & scope
  Share: media-archive
  Trigger: remote-delete-wave
  Window: 11m
  Affected paths: 1,842 deletes, 36 replacements
  Protected hits: contracts/, custody/

Destructive effect summary
  Local bytes affected: 128 GiB
  Placeholder-only paths: 612
  Largest subtree impact: 71% under exports/2026-03-17/

Preservation & recoverability
  Rollback witness: guarded
  Local retained history: 14d on this node
  Remote preserved copies: missing on render-node
  Unrecoverable risk: 22 paths if current local bytes are surrendered

Authority & source confidence
  Source confidence: guarded
  Writer set includes device returning after 9d dormancy
  Settlement posture: degraded-satisfied
  Suspicion: elevated delete density relative to baseline

Admissible actions
  freeze destructive replay
  allow non-destructive sync only
  require stronger witness
  escalate compromise
  escalate re-entry
  apply narrowed destructive replay

Receipt promise
  drr_01N4... will record destructive scope accepted or frozen, preservation posture, confidence level, and escalations
```

What this demonstrates:

- destructive replay can collapse to one fixed review grammar
- a Linux/headless operator gets the same delete/overwrite truth as the richer workbench
- no channel is allowed to turn a reviewed destructive wave back into a generic `Resume syncing`, `Pause`, or `Archive will save you` story

## Flow 98 — render the same stale-return review in CLI and workbench without semantic drift

Problem: an operator previews a stale return in the workbench, then later rechecks it from SSH on a headless Linux box. The re-entry truth must not change by channel.

```text
$ anonsync reentry show rec_01N2... --view review
Subject & dormancy
  Subject: device:laptop-ember
  Last seen: 46d ago
  Prior posture: hidden-only, not unlinked
  Shares: vault, photos, workdocs

Chronology & evidence
  Confidence: guarded
  Prior clock drift: 11m
  Fresh scan: still pending for 2 shares

Authority & scope
  Resume as: reader only
  Writable replay: blocked for vault, workdocs
  Escalation path: successor-cutover or compromise available

Divergence & availability
  14 offline-local changes detected
  3 announced files currently ghosted (no live source)
  1 rename collision requires merge review

Admissible actions
  apply guarded-resume
  open merge-review
  quarantine subject
  escalate compromise
  divert successor-cutover

Receipt promise
  rer_01N3... will record dormancy facts, chronology posture, authority outcome, and unresolved divergence
```

What this demonstrates:

- stale return can collapse to one fixed review grammar
- a Linux/headless operator gets the same dormancy and replay-authority truth as the richer workbench
- no channel is allowed to turn a reviewed re-entry case back into peer counters, archive warnings, or a generic `Resume syncing` button


## Flow 101 — review a non-trivial conflict as one adjudication sheet before choosing a winner

Problem: a cross-platform share hits a delete-vs-modify and path/case collision seam at the same time. The operator must not infer resolution meaning from suffix filenames, timestamps alone, or hidden rollback state.

```text
$ anonsync conflict show cft_01N6... --view review
Trigger & semantic class
  Share: design-assets
  Path: Brand/Logo.svg
  Class: delete-vs-modify with unicode/path collision side finding
  Triggered by: laptop-ember and macbook-nova
  Related findings: stale-return review open for laptop-ember

Candidates & authority posture
  cand_local_01  modified locally 7m ago   confidence: guarded
  cand_remote_02 deleted remotely 4m ago  confidence: low (writer returned after 11d dormancy)
  Winning scope if remote delete chosen: replicated

Path, materialization & compatibility reality
  Local filesystem: case-insensitive, unicode-normalizing
  Peer evidence: remote tree still has NFC/NFD divergence on sibling path
  Portability note: preserve-both cannot land cleanly without reviewed rename

Resolution scope & loser handling
  If cand_local_01 wins: remote delete is suppressed, local bytes replicate
  If cand_remote_02 wins: local bytes are removed from share path
  Loser preservation options: copy-aside, quarantine, retain-history-only
  Last easy recovery path: current local bytes on this node

Admissible resolutions
  choose cand_local_01 with loser-handling copy-aside
  defer and open portability repair
  quarantine remote candidate and escalate re-entry review

Receipt promise
  rbr_01N6... will record semantic class, winning candidate, loser handling, replicated scope, and linked stale-return finding
```

What this demonstrates:

- conflict adjudication is not the same thing as cleaning up a filename artifact
- candidate trust, portability reality, and loser handling stay visible before resolution
- the surface can branch into defer, portability repair, or re-entry escalation without pretending every conflict is routine collaboration

## Flow 102 — render the same conflict-adjudication review in CLI and workbench without semantic drift

Problem: an operator previews a conflict in the workbench, then later rechecks it from SSH on a headless Linux box. The adjudication truth must not change by channel.

```text
$ anonsync conflict show cft_01N6... --view review
Trigger & semantic class
  Share: design-assets
  Path: Brand/Logo.svg
  Class: delete-vs-modify
  Side finding: unicode/path collision on case-insensitive target

Candidates & authority posture
  cand_local_01  modified locally  confidence: guarded
  cand_remote_02 deleted remotely confidence: low
  Replicated outcome if remote wins: yes

Path, materialization & compatibility reality
  Target tier: warning
  Coexistence: both names cannot land cleanly here
  Portability drift: unresolved on 1 peer

Resolution scope & loser handling
  Safe primary: choose cand_local_01 with copy-aside
  Riskier alternative: replicated delete with history-only retention
  Last easy recovery path: current local bytes on this node

Admissible resolutions
  resolve winner cand_local_01
  defer for editor review
  open portability repair
  escalate re-entry

Receipt promise
  rbr_01N6... will record class, winner, loser handling, scope, and unresolved portability caveat
```

What this demonstrates:

- conflict adjudication can collapse to one fixed review grammar
- a Linux/headless operator gets the same candidate, compatibility, and loser-handling truth as the richer workbench
- no channel is allowed to turn a reviewed conflict back into `.Conflict` filename folklore or a generic `Resolve` button


## Flow 103 — review a same-host derivative before creating a self-edge on a weaker target

Problem: an operator wants another local branch of an existing share on this machine, but the proposed target is a removable/network-reviewed path and the source is only partially materialized. The product must not reduce that to a path picker plus a create action.

```text
Workbench → Share: field-kit → Create local derivative

Source & target
  Source: share field-kit / mount primary-worktree
  Proposed target: /mnt/usb/team-drop/field-kit
  Target tier: removable-reviewed
  Fanout set: second derivative of this source

Topology & loop risk
  Relation: sibling path under separate mount root
  Loop risk: guarded-none
  Existing derivative: /srv/cache/field-kit-cache
  Overlap proof: no parent/child recursion detected

Authority & lifecycle coupling
  Requested derivative: read-only local derivative
  Source authority: read-write
  Inherited authority: narrowed to read-only
  Lifecycle coupling: source detach freezes derivative until reviewed reconnect

Materialization & target-tier reality
  Source posture: placeholder-heavy (18 paths not yet materialized)
  Byte promise on target: cache/materialized only for fetched paths
  Target caveat: removable-reviewed target weakens durability witness
  Archive/history posture: reduced compared with local-native target

Admissible derivations
  Create read-only derivative on removable-reviewed target
  Narrow to cache branch only
  Pick stronger local-native target
  Reject self-edge

Receipt promise
  ldr_01P1... will record source/target, loop-risk proof, inherited authority, lifecycle coupling, target-tier caveats, and byte-availability promise
```

What this demonstrates:

- same-host derivation is not the same thing as choosing another path for ordinary sync
- target tier, source materialization, and lifecycle coupling stay visible before apply
- the surface can narrow to cache-only or safer target selection without pretending every local fanout is an ordinary mirror

## Flow 104 — render the same local-derivation review in CLI and workbench without semantic drift

Problem: an operator previews a same-host derivative in the workbench, then later rechecks it from SSH on a headless Linux box. The topology and lifecycle truth must not change by channel.

```text
$ anonsync derive local show ldr_01P1... --view review
Source & target
  Source: share field-kit / mount primary-worktree
  Target: /mnt/usb/team-drop/field-kit
  Tier: removable-reviewed
  Intent: read-only local derivative

Topology & loop risk
  Relation: sibling target on separate mount
  Loop risk: guarded-none
  Fanout count after apply: 2 derivatives from this source

Authority & lifecycle coupling
  Inherited authority: read-only
  Write-back to source: no
  Source detach effect: derivative freezes pending reviewed reconnect
  Source permission downgrade: derivative downgrades with source

Materialization & target-tier reality
  Source materialization: placeholder-heavy
  Target promise: fetched bytes only until source fully materializes
  Tier caveat: durability weaker than local-native root

Admissible derivations
  apply read-only derivative
  narrow to cache-branch
  choose stronger target
  reject self-edge

Receipt promise
  ldr_01P1... will record topology proof, inherited authority, lifecycle coupling, target-tier caveats, and byte-availability posture
```

What this demonstrates:

- local derivation can collapse to one fixed review grammar
- a Linux/headless operator gets the same topology, lifecycle, and target-tier truth as the richer workbench
- no channel is allowed to turn a reviewed same-host derivative back into a bare path picker or `sync local folders` folklore

## Flow 105 — review a live access downgrade without confusing write loss, delegation loss, and preserved bytes

Problem: a contractor laptop currently has `rw` on a sensitive share and has also been allowed to pass along approved access to a narrow sub-team. The operator now wants to narrow the laptop to `ro` without guessing whether bytes stay, delegation disappears, or dependent local derivatives quietly keep too much mutability.

Goal:

- preview a non-trivial authority change as one reviewed boundary decision
- surface active-subject fallout, dependent fallout, and byte-retention truth before apply
- avoid peer-list dropdown ritual, disconnect folklore, or remove/re-share workarounds

Suggested flow:

```text
anonsync grant set grt_01J... --perm ro --reason "contractor leaving write rotation" --plan
anonsync plan show pln_01J... --view review
anonsync audit --subject grt_01J...
anonsync plan apply pln_01J...
```

Expected semantics:

- the review states the current authority, the desired authority, and whether delegation/re-share reach is being stripped in the same step
- the review states whether bytes already present on the target stay in place, become read-only evidence, or require a separate destructive or reclaim action later
- the review states whether any local derivatives, linked members, or dependent grants narrow automatically, remain unchanged, or require follow-up review
- apply fails if the subject, share, or dependent authority graph changed after preview

Expected operator answers from CLI alone:

- exactly which authority is being removed and which authority remains
- whether any dependent subjects are narrowed, preserved, or split into follow-up review
- whether the mutation preserved bytes intentionally instead of pretending revoke means erase
- whether the change was direct, blocked, or diverted into authority-substrate migration


## Flow 106 — render the same authority-mutation review in CLI and workbench without semantic drift

Problem: a Linux/WebUI operator and a CLI operator both need to widen a backup node from `ro` to `rw` on one share while ensuring the node still lacks delegation power and while seeing whether any imported/legacy authority substrate needs migration.

Goal:

- prove that rich and textual surfaces render the same reviewed authority-mutation case
- make current authority, desired boundary delta, active fallout, and substrate effects read like one product

Workbench expectations:

- opening `Change access` from the subject row or share member list lands on one authority-mutation sheet
- the sheet renders sections in this order:
  1. trigger and current authority
  2. desired boundary delta
  3. active subject state and coupled dependents
  4. authority-substrate and compatibility effects
  5. admissible mutations
  6. receipt promise
- the primary action inherits the reviewed intent, for example `Grant write without delegation` or `Narrow to read-only and preserve bytes`, instead of generic `Apply`

CLI expectations:

```text
$ anonsync grant set grt_01J... --perm rw --without-delegation --plan
Authority mutation review
-------------------------
1. Trigger and current authority
   Subject: backup-node
   Current authority: ro
   Current delegation reach: none

2. Desired boundary delta
   Requested authority: rw
   Delegation after apply: none
   Boundary expansion: write only

3. Active subject state and coupled dependents
   Present local bytes remain
   No dependent grants widen
   1 local derivative remains read-only

4. Authority-substrate and compatibility effects
   Share authority substrate: native grant model
   Migration required: no

5. Admissible mutations
   - Grant write without delegation
   - Keep read-only
   - Divert to full stewardship review

6. Receipt promise
   Receipt will prove the pre/post authority boundary, preserved dependent posture, and byte-retention outcome.
```

Cross-surface success criteria:

- both surfaces answer the same question: **what authority boundary is changing, what remains deliberately unchanged, and what fallout was reviewed before apply?**
- neither surface falls back to generic `Disconnect`, `Owner`, `re-share`, or folder-class language when the real decision is a narrower authority mutation


## Flow 107 — review a nested child share without pretending the graph is ordinary

Problem: an operator already shares `/srv/projects` with a small team and now wants to share `/srv/projects/blue` separately with a narrower subgroup. The product must not make this look like just “add another folder” when the graph is no longer disjoint.

Goal:

- preview nested-share topology as one reviewed graph decision
- surface double-indexing, propagation shape, selective-sync constraints, and root/path continuity before apply
- avoid child-share folklore, loop warnings, and reconnect memory as the primary explanation

Suggested flow:

```text
anonsync topology review   --subject share:projects   --subject path:/srv/projects/blue   --intent nest --plan
anonsync topology show top_01J... --view review
anonsync topology apply top_01J...
```

Expected semantics:

- the review states whether the candidate is child, parent, overlap, or ambiguous relative to existing graph subjects
- the review states whether propagation would be independent, piggyback through the parent, or create blocked/self-edge behavior
- the review states whether selective materialization or root-boundary policy forbids the chosen topology or requires a narrower action
- the review states whether the safest next step is accept nesting, flatten the structure, rebind elsewhere, or reject as unsafe

Expected operator answers from CLI alone:

- whether the new share is truly separate or only separately addressed inside an already replicated parent
- whether edits in the child will still flow onward through the parent graph
- whether the topology increases indexing or replay cost enough to matter operationally
- whether path continuity and allowed-root policy remain honest after apply

## Flow 108 — render the same topology review in CLI and workbench without semantic drift

Problem: a Linux/WebUI operator previews a cross-share move that would relocate one mount near another shared tree; later a headless operator checks the same plan over SSH. Both surfaces must show the same graph and root-boundary truth.

Goal:

- prove that rich and textual surfaces render the same reviewed topology case
- make graph subjects, containment shape, path/root-boundary effects, and admissible actions read like one product

Workbench expectations:

- opening `Review topology` from a path compare, bind repair, nested-share warning, or local-derivation sheet lands on one topology review page
- the sheet renders sections in this order:
  1. trigger and graph subjects
  2. containment and propagation shape
  3. path and root-boundary effects
  4. admissible topology actions
  5. receipt promise
- the primary action inherits the reviewed intent, for example `Accept nested child with explicit propagation caveat` or `Rebind outside parent graph`, instead of generic `Apply`

CLI expectations:

```text
$ anonsync topology show top_01J... --view review
Topology review
---------------
1. Trigger and graph subjects
   Primary subject: mount blue-team
   Related subject: share projects
   Requested action: move candidate path to /srv/projects/blue

2. Containment and propagation shape
   Relation: child within existing share
   Propagation shape: piggyback-via-parent
   Indexing cost: child path will be scanned twice if accepted separately

3. Path and root-boundary effects
   Path continuity: rebind-required, not local-only rename
   Allowed-root posture: within approved root
   Selective-sync posture: disabled-required for this topology

4. Admissible topology actions
   - Rebind outside parent graph
   - Accept reviewed nested topology
   - Flatten by keeping only the parent share
   - Reject overlap

5. Receipt promise
   Receipt will prove the accepted graph relation, propagation posture, root-boundary findings, and any required follow-up.
```

Cross-surface success criteria:

- both surfaces answer the same question: **what graph relationship is being created or repaired here, how will changes propagate, and is this path transition actually safe?**
- neither surface falls back to generic `add folder`, `move`, or `connect in new location` language when the real decision is a reviewed topology change

## Flow 109 — review writer contention on a mixed-access path before silent overwrite or rollback folklore takes over

Problem: a Linux operator sees a busy project subtree alternately appear as delayed, rescanned, and locked while a local editor and SMB users both touch the same files. The product must explain coordination truth directly instead of asking the operator to infer it from badges and retries.

Goal:

- prove that lock pressure, delay profiles, notification weakness, and mixed-writer risk can render as one reviewed contention case
- make the safe next action read like coordination policy rather than troubleshooting lore

Workbench expectations:

- clicking `Review contention` from a transfer delay badge, filesystem warning, or workbench report opens one contention review page
- the page renders sections in this order:
  1. trigger and contested scope
  2. writer and lock reality
  3. notification and filesystem posture
  4. quiesce and propagation effects
  5. admissible actions
  6. receipt promise
- the primary action inherits the reviewed intent, for example `Freeze bidirectional propagation` or `Hold uploads and preserve local writes`, instead of generic `Retry` or `Resume syncing`

CLI expectations:

```text
$ anonsync contention show cnt_01J... --view review
Contention review
-----------------
1. Trigger and contested scope
   Trigger: smb-mixed-access
   Scope: share design-lab / subtree /srv/design/current

2. Writer and lock reality
   Writer posture: mixed
   Locked paths: 12 confirmed, 4 recently cleared
   Evidence confidence: guarded

3. Notification and filesystem posture
   Notifications: periodic-rescan only
   Filesystem posture: network-reviewed
   Mixed-access risk: direct local writes outside Samba may roll back remote edits

4. Quiesce and propagation effects
   Current posture: upload-hold
   Delete propagation: held
   Propagation risk if released now: rollback-risk

5. Admissible actions
   - Freeze bidirectional propagation
   - Keep upload hold and re-evaluate after quiet window
   - Escalate into filesystem fidelity review

6. Receipt promise
   Receipt will prove trigger scope, writer evidence, notification posture, applied quiesce effect, and any required follow-up.
```

Expected operator answers from CLI alone:

- whether the contested state is just burst-save delay or a stronger mixed-writer problem
- whether freshness is continuous or rescan-only while the conflict exists
- what propagation is actively being held back right now
- which safer action exists before the operator lets bidirectional sync continue again

## Flow 110 — render the same contention review in CLI and workbench without semantic drift

Problem: a WebUI operator freezes propagation for a contested Office-heavy subtree; later a headless operator checks the same case over SSH. Both surfaces must show the same writer, notification, quiesce, and receipt truth.

Goal:

- prove that rich and textual surfaces render the same reviewed contention case
- make contested scope, writer reality, notification posture, and quiesce effects read like one product

Cross-surface success criteria:

- both surfaces answer the same question: **who appears to be writing here, what is currently delayed or frozen, how trustworthy is freshness, and when may safe propagation resume?**
- neither surface falls back to generic `Retry`, `Resume syncing`, or `Increase delay` language when the real decision is a reviewed coordination action

## Flow 111 — review host fit before adopting a huge subject on a watcher-limited Linux machine

Problem: a Linux operator is about to adopt a very large pre-seeded project tree onto a machine with limited RAM, nearly exhausted watcher budget, and modest free space. The product must explain host-fit truth directly instead of asking the operator to infer it from warnings, slow indexing, and later rescans.

Goal:

- prove that scale, RAM, watcher, indexing, headroom, and path blockers can render as one reviewed capacity-fit case
- make the safe next action read like admission policy rather than troubleshooting lore

Workbench expectations:

- clicking `Review host fit` from claim/adoption, path rebind, or a warning opens one capacity-fit review page
- the page renders sections in this order:
  1. subject and intended local role
  2. local capacity and index cost
  3. freshness and notification posture
  4. portability and path blockers
  5. admissible modes and mitigations
  6. receipt promise
- the primary action inherits the reviewed intent, for example `Adopt metadata-only on this host` or `Defer and reclaim before full materialization`, instead of generic `Connect` or `Add folder`

CLI expectations:

```text
$ anonsync fit show fit_01J... --view review
Capacity-fit review
-------------------
1. Subject and intended local role
   Subject: incoming share research-archive
   Requested local role: full-materialize
   Estimated scale: 9.8M entries / 2.4 TiB

2. Local capacity and index cost
   Memory posture: guarded
   Watcher posture: rescan-fallback likely on this host
   Index cost: heavy-preseed-verify
   Storage headroom: warning

3. Freshness and notification posture
   Expected freshness: periodic-rescan if fully adopted here
   Settlement honesty: guarded, not continuous

4. Portability and path blockers
   Path blocker posture: none-known
   Additional blocker: candidate path sits on network-reviewed mount

5. Admissible modes and mitigations
   - Adopt metadata-only on this host
   - Narrow to subtree and rerun fit review
   - Reclaim space and keep selective materialization
   - Escalate to filesystem fidelity review

6. Receipt promise
   Receipt will prove reviewed scale, accepted local role, degraded freshness posture, and any required follow-up.
```

Expected operator answers from CLI alone:

- whether the machine is comfortable, guarded, or blocked for the requested subject
- whether degraded freshness is structural from watcher limits rather than temporary contention
- whether a narrower local mode is the honest answer
- whether another review family should take over because the real blocker is portability or topology

## Flow 112 — render the same capacity-fit review in CLI and workbench without semantic drift

Problem: a GUI operator narrows a large share to metadata-only on a low-resource laptop; later a headless operator checks the same case over SSH. Both surfaces must show the same scale, host posture, freshness, and receipt truth.

Goal:

- prove that rich and textual surfaces render the same reviewed host-fit case
- make subject role, local capacity, freshness posture, path blockers, and admissible modes read like one product

Cross-surface success criteria:

- both surfaces answer the same question: **can this machine honestly carry this subject, under what local mode, and with what freshness guarantees if accepted?**
- neither surface falls back to generic `Add folder`, `Connect`, `Retry indexing`, or `Re-add` language when the real decision is a reviewed host-fit choice


## Flow 113 — review bring-up on a headless Linux host before accidentally opening the wrong state or exposing the wrong endpoint

Problem: a Linux operator launches AnonSync on a server and the daemon discovers an existing state root from prior use. The operator also wants browser access from another machine. The product must explain whether this is fresh start, attach-known state, recovery/import, or successor-sensitive continuity, and must make the first control boundary explicit before the daemon becomes ordinary background fact.

Goal:

- prove that bring-up can render as one reviewed case instead of startup ritual
- make continuity and first-control truth legible before the daemon opens durable state or a remotely reachable endpoint

Workbench expectations:

- if startup is not obviously fresh local-only state, the first page becomes `Review bring-up`
- the page renders sections in this order:
  1. host role and runtime target
  2. state and continuity choice
  3. identity and relationship posture
  4. control access and network posture
  5. blockers and bootstrap dependencies
  6. receipt promise
- the primary action inherits the reviewed intent, for example `Attach verified state with loopback control` or `Prepare reviewed LAN control`, instead of generic `Start` or `Open WebUI`

CLI expectations:

```text
$ anonsync bringup show brc_01J... --view review
Bring-up review
---------------
1. Host role and runtime target
   Host role: background-service
   Runtime target: local-web + CLI

2. State and continuity choice
   Candidate state root: /srv/anonsync/root-a
   Continuity posture: attach-known-root

3. Identity and relationship posture
   Identity posture: retained
   Relationship effect: existing grants remain inactive until attach succeeds

4. Control access and network posture
   Current control posture: local-socket-only
   Requested posture: lan-reviewed on 10.0.0.8:4747
   Discovery baseline: known-host-only

5. Blockers and bootstrap dependencies
   Blocker: requested interface not currently present
   Dependency: candidate root verification age 19 days

6. Receipt promise
   Receipt will prove chosen host role, opened state root, accepted control posture, and unresolved follow-up.
```

Expected operator answers from CLI alone:

- whether startup is fresh, attached, recovered, continuity-sensitive, or blocked
- whether identity continuity is being retained or merely inspected
- whether control remains local-only or is about to become remotely reachable
- whether the honest next step is verify root, narrow exposure, or stop

## Flow 114 — render the same bring-up review in CLI and workbench without semantic drift

Problem: a workstation operator previews a reviewed attach with loopback-only control; later a headless operator inspects the same case over SSH before applying reviewed LAN exposure. Both surfaces must show the same host role, continuity, identity, endpoint, blocker, and receipt truth.

Goal:

- prove that rich and textual surfaces render the same reviewed bring-up case
- make first-open semantics read like one product instead of one wizard plus one hidden headless mode

Cross-surface success criteria:

- both surfaces answer the same question: **what exactly is this host opening, under which continuity story, and with what first control boundary?**
- neither surface falls back to generic `init`, `start`, `open WebUI`, or `run with --config` language when the real decision is a reviewed bring-up choice


## Flow 115 — issue a reviewed mutation grant before a browser/workbench session widens control exposure

Problem: a remote operator can inspect the daemon through a healthy workbench session, but now wants to widen control from local-only to trusted-LAN. The product must not treat the already-open browser/workbench session as sufficient mutation proof.

Goal:

- prove that visible inspectability and reviewed mutation authority are separate states
- make dangerous apply read like one explicit gate/grant contract rather than one more password prompt

Workbench expectations:

- pressing `Allow trusted-LAN control` first opens a mutation-gate review, not the final exposure apply sheet
- the gate renders sections in this order:
  1. current session and endpoint
  2. requested mutation and subject scope
  3. required authority and grant scope
  4. binding and freshness
  5. blockers and fallback
  6. receipt promise
- if the current session is observe-only, the primary action is `Issue reviewed mutation grant`, not `Apply exposure`
- the later exposure apply step references the grant directly and repeats its scope/expiry binding

CLI expectations:

```text
$ anonsync access gate show --action control-expose --subject endpoint:cep_01J...
Mutation gate
-------------
1. Current session and endpoint
   Session: css_01J... (workbench-browser)
   Endpoint: ssh-tunnel-reviewed
   Current authority: observe

2. Requested mutation and subject scope
   Action family: control-expose
   Subject: endpoint policy for daemon dmn_01J...
   Blast radius: local-only -> trusted-lan-reviewed

3. Required authority and grant scope
   Required authority: mutation-grant
   Minimal grant scope: action-family control-expose / subject endpoint-policy
   Batch budget: one reviewed apply

4. Binding and freshness
   Channel binding: workbench-browser
   Endpoint binding: ssh-tunnel-reviewed only
   State root: srt_01J...
   TTL if issued now: 10m

5. Blockers and fallback
   Gate state: grant-required
   Safe next action: issue mutation grant

6. Receipt promise
   Grant receipt will prove scope, binding, TTL, and later consume state.
```

Expected operator answers from CLI alone:

- whether the current workbench/browser session is only inspect-capable or already mutation-capable
- what exact grant scope is required for this exposure change
- what channel, endpoint, and state-root bindings would invalidate that grant
- whether the honest next step is reviewed elevation, broader review, or stop

## Flow 116 — render the same mutation-gate truth in CLI and workbench without semantic drift

Problem: a browser/workbench operator issues a short-lived grant to perform a share-authority change; later a headless operator inspects the same gate and grant state over SSH. Both surfaces must show the same authority, scope, binding, freshness, and receipt truth.

Goal:

- prove that rich and textual surfaces render the same reviewed mutation gate
- make inspect-versus-mutate separation read like one product

Cross-surface success criteria:

- both surfaces answer the same question: **can this current session mutate this subject now, under what explicit authority object, for how long, and with what invalidation conditions?**
- neither surface falls back to generic `Confirm password`, `Apply anyway`, or `Session active` language when the real decision is a reviewed mutation-elevation step


## Flow 117 — inspect a removable disk with foreign marker state before claiming it as an ordinary local target

Intent:

- make same-host/removable-media ownership explicit before bind
- avoid silent collision, fork, or delete-and-re-add ritual
- prove the difference between same-lineage continuation, foreign-marker inspection, and reviewed cleanup

Suggested flow:

```text
anonsync custody inspect --path /media/backup-disk/projects
anonsync custody review --path /media/backup-disk/projects --intent attach
anonsync custody show bcc_01J... --view review
```

Expected review truth:

- discovered marker state and storage tier for `/media/backup-disk/projects`
- whether the marker belongs to the current active root, another local root/profile, or unknown lineage
- whether collision or unsupported clone-like reuse is suspected
- whether preservation is required before cleanup or takeover
- admissible actions: reuse verified bind, inspect-only preserve, prepare successor claim, or block
- custody receipt promise

The operator should not have to infer from `.sync` presence, `already managed`, or a non-empty-path warning whether this disk is safe to claim.

## Flow 118 — render the same target-custody review in CLI and workbench without semantic drift

CLI review should show the fixed custody grammar in this order:

1. target and discovered markers
2. current custody and lineage
3. requested bind and continuity story
4. collision and corruption risk
5. admissible custody actions
6. receipt promise

Workbench review should show the same six sections with the same meaning.
Neither surface may collapse foreign-marker state into ordinary `Use folder` language or offer cleanup as a casual retry button.



## Flow 119 — continue a degraded browser/workbench delete review in CLI without changing its meaning

Problem: a Linux operator opens a share-exit review in WebUI/workbench, but the current browser posture is degraded and the strongest destructive-action guardrails cannot be applied honestly there. The operator must continue the same action in CLI without downgrading the review to generic `remove` ritual.

Goal:

- prove that a degraded browser/workbench surface can hand off the same reviewed exit action into CLI
- keep subject, blast radius, residue truth, and receipt promise stable across the handoff

Suggested flow:

```text
anonsync access handoff create --action exit-share --subject share:shr_01J... --to cli
anonsync access handoff show rhf_01J... --view review
anonsync exit show exc_01J... --view review
anonsync exit apply exc_01J... --grant mgr_01J...
```

Expected review truth:

- the requested action remains `exit-share`, not a weaker `remove path` substitute
- the CLI render preserves the same fixed review order as the workbench exit sheet
- the handoff states why the browser/workbench channel is degraded and why CLI is the safe apply target
- any required mutation grant or broader blocker survives the handoff instead of being silently re-evaluated away
- the later receipt proves both the handoff and the applied exit action

The operator should not have to infer from a missing button or Linux/WebUI caveat whether the action disappeared, changed, or merely moved.

## Flow 120 — render the same channel-parity review in workbench and CLI without semantic drift

CLI review should show the fixed channel-parity grammar in this order:

1. requested action and subject
2. capability and semantic parity
3. current channel and degradation facts
4. safe fallback and handoff
5. apply guarantees and review continuity
6. receipt promise

Workbench review should show the same six sections with the same meaning.
Neither surface may collapse a degraded action into `try another client`, generic `not available`, or a weaker confirm path.


## Flow 121 — review switching from an interactive seat to a service-style seat without pretending the same host is the same world

Problem: an operator wants to move an existing workstation-managed node into a background-service seat so it survives logout. The product must explain whether the same state root stays active, whether previously visible paths remain reachable, and whether any path now falls back to degraded notification or rescan-only posture.

Goal:

- prove that service-account or runtime-seat switching is a reviewed continuity/reachability decision, not install folklore
- keep state continuity, path loss, and freshness downgrade visible before apply

Workbench expectations:

- choosing `Run as background service` from the System State page first opens `Review execution seat`
- the page renders sections in this order:
  1. requested seat switch and continuity intent
  2. state root and identity continuity
  3. reachable-target delta
  4. freshness and substrate delta
  5. fallout and admissible actions
  6. receipt promise
- if some targets would only survive through degraded workaround posture, the primary action becomes `Prepare reviewed rebind` or `Keep current seat`, not a generic `Install service`

CLI expectations:

```text
$ anonsync state seat show esr_01J... --view review
Execution-seat review
---------------------
1. Requested seat switch and continuity intent
   Source seat: workstation / interactive-user
   Target seat: background-service / local-system
   Requested intent: preserve-state-and-reachability

2. State root and identity continuity
   Active state root: /home/jane/.config/anonsync/root-a
   Continuity expectation: same-root-new-principal
   Result if applied now: guarded — target seat would not reopen this root without explicit attach

3. Reachable-target delta
   Lost path: Z:\team-share\ledger
   Reason: mapped drive exists only in interactive seat
   Reviewed fallback: UNC path \\nas\team-share\ledger requires explicit rebind

4. Freshness and substrate delta
   Current posture: native notifications
   Target posture for fallback path: rescan-only
   Reason: target seat cannot rely on direct change notifications for reviewed workaround path

5. Fallout and admissible actions
   Safe actions: keep current seat / prepare rebind / create clean service seat
   Blocked shortcut: switch seats and preserve all current targets automatically

6. Receipt promise
   Receipt will prove continuity choice, lost or rebound targets, freshness downgrade, and final seat outcome.
```

Expected operator answers from CLI alone:

- whether the target seat really preserves the same state root or needs explicit attach/rebind
- which current targets vanish or degrade under the new seat
- whether freshness remains native or falls back to reviewed rescan-only posture
- whether the honest next step is keep current seat, rebind carefully, or start a clean service seat

## Flow 122 — render the same execution-seat review in CLI and workbench without semantic drift

Problem: a browser/workbench operator previews a switch into a service-style seat; later a headless operator inspects the same review over SSH before applying it. Both surfaces must show the same continuity, reachability, freshness, fallout, and receipt truth.

Goal:

- prove that rich and textual surfaces render the same reviewed execution-seat case
- make service-seat switching read like one product instead of one installer path plus one pile of troubleshooting lore

Cross-surface success criteria:

- both surfaces answer the same question: **if I change runtime seat on this host, am I still operating the same state world, which targets or guarantees change, and what reviewed fallout follows?**
- neither surface falls back to generic `run as service`, `switch account`, or `re-share folders` language when the real decision is a reviewed continuity/reachability change

## Flow 125 — migrate a legacy in-tree share layout toward an external annex without pretending cleanup is ordinary file deletion

Goal: preserve a live share's continuity while moving managed sync bytes out of the ordinary tree and making residue classes explicit.

```text
$ anonsync layout show workdocs
Share: workdocs
Live root: /srv/workdocs
Live namespace state: legacy-import
Layout class: in-tree-explicit
Managed byte classes:
  - identity-marker
  - history
  - metadata-carry
  - temp-transfer
Cleanup risk: preservation-required

$ anonsync layout prepare workdocs \
    --annex /var/lib/anonsync/annex/workdocs \
    --history external-annex \
    --temp-residue external-only \
    --plan
Share layout review: slr_01NY...

Requested layout:
  external-annex
  visibility posture: external-only

Live namespace guarantee:
  ordinary user tree will become clean after migration
  existing hidden managed bytes preserved until receipt commits

Residue findings:
  .sync/Archive -> class: history
  .sync/Streams -> class: metadata-carry
  .!sync remnants -> class: temp-transfer

Admissible actions:
  - migrate with preservation checkpoint
  - keep legacy inspect-only
  - clean temp-transfer residue only after checkpoint

Receipt promise:
  lyr_01NZ... will prove live-tree cleanup and annex placement
```

What this proves:

- layout cleanup is class-based and preservation-aware, not generic hidden-file deletion
- history, metadata-carry, and temp-transfer bytes stay visibly distinct during migration
- the live tree can become cleaner without pretending those bytes never existed

## Flow 126 — render the same share-layout review in CLI and workbench without semantic drift

Problem: a workbench operator prepares an annex migration and later a headless operator inspects the same review over SSH before applying it. Both surfaces must show the same layout class, residue classes, cleanup posture, and receipt truth.

Goal:

- prove that rich and textual surfaces render the same reviewed share-layout case
- make layout migration read like one product instead of one file-browser ritual plus one support article

Cross-surface success criteria:

- both surfaces answer the same question: **which bytes in this tree are ordinary data, which are managed sync state, and what exactly happens if I migrate or clean them?**
- neither surface falls back to generic `Show hidden files`, `Delete .sync`, `Open Archive`, or `Clean temp files` language when the real decision is a reviewed layout migration or residue-class cleanup

## Flow 123 — correct a device label typo without rotating authority

Goal: fix a peer-visible name while proving the same trusted subject and same authority remain in place.

```text
$ anonsync subject show dev_laptop
Subject: dev_laptop
Current label: jonnys-laptop
Peer-visible label: jonnys-laptop
Authority fingerprint: fp_9f2c...
Continuity class: same-authority
Previous labels: none

$ anonsync subject relabel dev_laptop --label johnny-laptop --scope peer-visible --plan
Identity continuity review: icr_01NV...

Requested action: peer-visible-relabel
Current subject: dev_laptop
Current authority: fp_9f2c...
Candidate authority: same as current

Continuity verdict:
  same-authority
  no grant or constellation widening

Peer-visible fallout:
  contacts will observe new label at next normal observation
  previous label will remain searchable as alias

Receipt promise:
  ilr_01NW... will prove relabel-only with unchanged authority

Safest next action: Apply relabel

$ anonsync subject relabel dev_laptop --label johnny-laptop --scope peer-visible --apply
Applied.
Receipt: ilr_01NW...
```

What this proves:

- a label correction does not silently regenerate authority
- peer-visible naming changes keep the same trust subject unless the review says otherwise
- alias history survives for audit and search

## Flow 124 — compare a same-person claim before accepting new authority under an old name

Goal: inspect a candidate replacement device that looks like the same human subject without pretending name similarity is enough proof.

```text
$ anonsync identity continuity prepare dev_laptop --candidate dev_laptop_new --claim same-person --plan
Identity continuity review: icr_01NX...

Current subject:
  label: johnny-laptop
  authority: fp_old_73...

Candidate subject:
  label: johnny-laptop
  authority: fp_new_11...

Continuity verdict:
  same-person-new-authority
  successor proof: missing
  automatic future-approval carry-forward: blocked

Grant and constellation fallout:
  3 future-approval paths would be reset
  2 linked members would remain separate unless successor review succeeds

Admissible actions:
  - keep separate subject
  - add alias only
  - open successor cutover review
  - reject same-person continuity claim

Receipt promise:
  no relabel receipt until one admissible action is chosen
```

What this proves:

- same label is not treated as same authority
- convenience continuity claims do not silently inherit approvals or grants
- successor/replacement work stays visibly separate from harmless rename hygiene


## Flow 127 — accept a degraded network-share profile without pretending it is only a speed tweak

Problem: an operator wants to keep syncing a large share onto a network-mounted path that lacks reliable notifications and has weaker locking semantics. They need to see whether the product is merely slower or whether rename continuity, detection freshness, and corruption risk are weaker too.

```text
$ anonsync semantics show media-archive
Semantic runtime contract: src_01PA...

Profile: balanced
Detection posture: notifications-plus-rescan
Rename continuity: preserved-with-history
Delta transfer: diff-preferred
Verification: eager
Target degradation: none

$ anonsync semantics prepare media-archive --profile degraded-network-share --reason smb-fallback --plan
Semantic optimization review: sor_01PB...

Requested optimization or degraded target:
  profile: degraded-network-share
  reason: SMB target lacks trustworthy notifications

Semantic guarantees at risk:
  detection freshness -> weakens to rescan-biased
  rename continuity -> uncertain under target interruption
  conflict honesty -> unchanged
  verification -> unchanged

Target and runtime findings:
  target class: network-share
  notification posture: unreliable
  mixed-access risk: present
  safer alternative: move share to local tier and re-export via ordinary file service

Admissible actions:
  - accept degraded profile with receipt
  - keep balanced profile and block this target
  - move to stronger local target

Receipt promise:
  sorc_01PC... will prove accepted degraded-network-share posture

$ anonsync semantics apply sor_01PB...
Applied.
Receipt: sorc_01PC...
```

What this proves:

- degraded storage is rendered as weaker semantics, not just slower sync
- the operator sees which guarantees changed and why
- the receipt preserves that this was a reviewed downgrade, not an invisible speed tweak

## Flow 128 — restore stronger guarantees after watcher repair without semantic drift

Problem: a large pre-seeded subject temporarily used lazy proof and rescan-biased detection during intake. Later the operator repairs watcher limits and wants to restore stronger rename and verification guarantees without guessing what still needs to catch up.

```text
$ anonsync semantics show workdocs
Semantic runtime contract: src_01PD...

Profile: large-preseeded-intake
Detection posture: rescan-biased
Rename continuity: uncertain
Delta transfer: diff-preferred
Verification: lazy
Target degradation: watcher-exhausted

$ anonsync semantics prepare workdocs --profile full-verify --plan
Semantic optimization review: sor_01PE...

Requested optimization or degraded target:
  profile: full-verify
  restore stronger guarantees: yes

Semantic guarantees at risk:
  none weaken
  detection freshness -> strengthens to notifications-plus-rescan
  rename continuity -> strengthens to preserved-with-history
  verification -> strengthens to eager

Target and runtime findings:
  watcher exhaustion: repaired
  catch-up requirement: one verification pass still pending

Admissible actions:
  - restore stronger profile now
  - defer until quiet window

Receipt promise:
  sorc_01PF... will prove stronger guarantees restored after catch-up
```

What this proves:

- stronger semantics are restored through the same reviewed model that accepted the earlier downgrade
- the product keeps catch-up obligations visible instead of silently flipping a switch back
- CLI and richer surfaces can render the same guarantee delta without drift


## Flow 129 — revoke future updates while honestly attesting that retained copies remain

Problem: a contractor laptop should stop receiving future changes to a share immediately, but the operator also wants the product to stay honest that the laptop already has materialized bytes and no remote-delete observation has occurred.

```text
$ anonsync replicas list --share designs
Peer: dev_contractor
Authority: write
Bytes: materialized
Future updates: active
Recall verdict: not-requested

$ anonsync recall prepare --share designs --peer dev_contractor --change revoke-future-updates --bytes attest-existing-copies --plan
Replica recall review: rcr_01PG...

Requested boundary change:
  action: revoke future updates
  byte outcome: attest existing copies

Current authority and byte reality:
  authority: write
  bytes: materialized
  recovery usefulness: ordinary collaborator, not required backup

Retained-copy and recovery findings:
  retained copies remain: yes
  remote delete requested: no
  stronger recall proof: none yet

Recall and observation posture:
  future updates -> will become revoked-pending-observation
  retained copy verdict -> retained-copy-confirmed

Admissible actions:
  - revoke future updates with retained-copy attestation
  - request remote delete as a separate follow-up
  - defer until quiet window if a receipt should include recent settlement proof

Receipt promise:
  rcrp_01PH... will prove future updates stopped and retained copies remained in scope

$ anonsync recall apply rcr_01PG...
Applied.
Receipt: rcrp_01PH...
```

What this proves:

- revoke and recall are rendered as different truths
- the operator sees that bytes remain even though future participation stops
- the receipt preserves the strongest honest claim instead of marketing `remove` as erasure

## Flow 130 — preserve an encrypted backup without pretending ordinary removal erased bytes

Problem: an encrypted backup peer should be removed from ordinary participation in a share migration, but the operator also needs to keep clear that encrypted bytes still exist there and may still matter for reseed if continuity material is preserved.

```text
$ anonsync replicas show enc_backup_1
Replica posture: rrp_01PI...
Authority: encrypted-readonly
Bytes: encrypted-materialized
Future updates: active
Recovery contribution: can-reseed-with-continuity-material
Recall verdict: not-requested

$ anonsync recall prepare --share ledger --peer enc_backup_1 --change narrow-authority --bytes retain-existing-copies --plan
Replica recall review: rcr_01PJ...

Requested boundary change:
  action: narrow authority / retire from ordinary participation
  byte outcome: retain existing copies

Current authority and byte reality:
  authority: encrypted-readonly
  bytes: encrypted-materialized
  recovery usefulness: can reseed if preserved continuity material remains available

Retained-copy and recovery findings:
  encrypted bytes remain: yes
  local decrypt capability on backup peer: no
  continuity dependency: preserved keys and compatible database lineage still required

Recall and observation posture:
  future updates -> frozen after apply
  retained storage verdict -> retained-copy-confirmed
  remote delete -> not requested

Admissible actions:
  - preserve encrypted backup and freeze future updates
  - replace backup first, then request stronger cleanup later
  - block if operator expectation is `erase all copies now`

Receipt promise:
  rcrp_01PK... will prove future participation changed while encrypted retained storage remained intentionally preserved
```

What this proves:

- backup preservation and byte recall are kept visibly separate
- the product exposes when an encrypted retained replica still matters for disaster recovery
- CLI and richer surfaces can tell the same honest story without drift


## Flow 131 — rotate a key-backed share without pretending the old swarm vanished

Problem: a key-backed collaborator share needs a tighter boundary, so the operator issues new authority material. The product should show that this created a new epoch but does not yet prove that every old-key peer stopped syncing among itself.

```text
$ anonsync epochs list --share finance
Current epoch: sae_01PL...
Authority class: key-backed
Convergence verdict: observed-new-epoch-only not yet available

$ anonsync rotate prepare --share finance --change rotate-authority-material --outcome issue-new-epoch --plan
Epoch rotation review: err_01PM...

Requested boundary change:
  action: rotate share authority material
  requested outcome: issue new epoch

Current epoch map:
  current epoch: sae_01PL... (key-backed)
  prior epochs still known: none retired-observed
  peers on current epoch: acct_desktop, acct_laptop, ext_bookkeeper

Stale-capability fallout:
  old copied key may still exist after apply: yes
  mixed-epoch risk after apply: yes until peers are re-admitted or observed retired
  strongest immediate claim: new epoch issued

Derivative and migration obligations:
  local derivatives: none
  downstream grants/offers to reissue: 2

Convergence and observation posture:
  post-apply verdict -> mixed-epoch
  stronger verdict `observed-new-epoch-only` requires later peer observation

Receipt promise:
  errc_01PN... will prove new epoch issuance and mixed-epoch follow-up requirements

$ anonsync rotate apply err_01PM...
Applied.
Receipt: errc_01PN...
```

What this proves:

- issuing new authority and converging on it are rendered as different truths
- the operator sees stale-capability residue before assuming the old swarm disappeared
- the receipt preserves the honest mixed-epoch story instead of marketing `rotated` as complete retirement

## Flow 132 — upgrade authority class without pretending derivative/local-share migration is automatic

Problem: a share should move from a weaker/key-style boundary to a stronger/certificate-backed authority model, but the product also needs to show that some derivative/local-share state must be rebuilt or reissued rather than mutated in place.

```text
$ anonsync epochs show sae_01PQ...
Share: media
Authority class: key-backed
Derivatives referencing epoch: ldr_01PR...
Convergence verdict: current

$ anonsync rotate prepare --share media --change upgrade-share-class --outcome upgrade-authority-class --plan
Epoch rotation review: err_01PS...

Requested boundary change:
  action: upgrade share authority class
  requested outcome: certificate-backed current epoch

Current epoch map:
  current epoch: sae_01PQ... (key-backed)
  proposed epoch class: certificate-backed

Stale-capability fallout:
  legacy offers/keys become superseded after apply: yes
  old artifact residue must remain visible until retired or expired: yes

Derivative and migration obligations:
  local derivative ldr_01PR... cannot mutate in place
  required follow-on: reissue derivative against new epoch
  local-share continuity: data path may remain, authority lineage changes

Convergence and observation posture:
  post-apply verdict -> new-epoch-issued
  stronger verdict `observed-new-epoch-only` blocked by unfinished derivative migration

Receipt promise:
  errc_01PT... will prove authority-class upgrade and outstanding derivative migration
```

What this proves:

- share-class upgrade and derivative migration are rendered as different actions
- the product exposes when local-share fallout is a real boundary change rather than an implementation quirk
- CLI and richer surfaces can tell the same honest epoch story without drift


## Flow 133 — make a replica a full-byte observer without pretending it cannot still help serve clean bytes

Problem: a tablet should keep a fully materialized copy of a share for reading and travel, but it should stop propagating local edits. The product should show that the tablet will still hold useful bytes and may still help serve clean content onward even though local writes are no longer authoritative.

```text
$ anonsync observer show --subject shp_tablet_reports
Observer posture: opc_01PU...
Visibility: full-bytes-visible
Local writes: writes-allowed-review-required
Serve posture: serve-per-normal-authority
Projection limits: none

$ anonsync observer prepare --share reports --peer dev_tablet --posture full-byte-observer --plan
Observer-rights review: orr_01PV...

Requested access posture:
  action: narrow writable replica to full-byte observer
  authority vs projection: authority narrowing, no byte-visibility reduction

Byte visibility and materialization reality:
  current bytes: full
  after apply: full bytes remain materialized
  local byte delta: none required

Local write and repair behavior:
  local edits after apply: writes suspend touched paths unless repaired
  revert helper: available as reviewed path-revert, not automatic
  added local files: remain local until separately handled

Onward serving and redistribution posture:
  serve posture after apply: serve-clean-bytes-only
  retained local bytes still useful for reseed: yes

Projection, share-class, and runtime limits:
  requested posture available in current share class: yes
  linked-convenience widening elsewhere: none

Receipt promise:
  orc_01PW... will prove full-byte observer posture, path-suspend write semantics, and clean-byte serving rights

$ anonsync observer apply orr_01PV...
Applied.
Receipt: orc_01PW...
```

What this proves:

- `read only` is not collapsed into `has no useful bytes`
- the operator sees byte visibility, local-write behavior, and serve posture as different truths
- the receipt preserves the exact observer bundle instead of a vague mode label

## Flow 134 — repair a broken read-only replica without pretending revert helpers are always available

Problem: a kiosk replica was meant to be read-only, but staff edited a locally materialized file. The product should show whether that path can be auto-reverted, whether the current local/projection mode disables that repair, and whether the real next step is repair, deviation review, or posture redesign.

```text
$ anonsync observer show --subject shp_kiosk_media
Observer posture: opc_01PX...
Visibility: placeholder-visible
Local writes: writes-suspend-path
Serve posture: no-serve
Projection limits: selective-sync-bound
Repair mode: unavailable

$ anonsync observer repair --subject shp_kiosk_media --mode path-revert --plan
Observer-rights review: orr_01PY...

Requested access posture:
  action: repair touched path on observer replica
  requested posture: keep placeholder observer

Byte visibility and materialization reality:
  current visibility: placeholders plus one locally materialized edited file
  after repair intent: return touched path to observer-compatible state

Local write and repair behavior:
  touched path status: sync suspended for edited file
  requested helper: path-revert
  helper availability: unavailable while current posture remains placeholder/selective
  reviewed alternatives: materialize-then-repair, explicit deviation review, or redesign posture to full-byte observer

Onward serving and redistribution posture:
  current serve posture: no-serve
  reseed value from current local bytes: low and path-scoped only

Projection, share-class, and runtime limits:
  limiting factor: selective-materialization posture disables automatic overwrite/revert helper
  stronger repair without posture change: not available

Receipt promise:
  orc_01PZ... will prove why repair was blocked and which reviewed alternative was chosen
```

What this proves:

- broken read-only behavior is rendered as a reviewed write/repair problem, not a mysterious sync stall
- projection limits stay visible when they disable a seemingly obvious helper
- CLI and richer surfaces can tell the same honest observer story without drift


## Flow 135 — evict a local copy only when another full-copy witness exists

Problem: a laptop in selective mode needs to free space, but one project subtree is also the only copy the operator actually trusts. The product should show whether eviction is ordinary local convenience or whether it would silently create a placeholder-only universe.

```text
$ anonsync file availability research datasets/2025/ --view review
Fetchability review: ftr_01QA...

Requested materialization intent:
  action: inspect before evict
  scope: subtree research/datasets/2025/

Visibility and local-residency reality:
  visibility: placeholder-visible mixed with 14 full local files
  local residency: current device holds full bytes for 14 files

Source backing and full-copy witnesses:
  witness summary: local-only for 11 files, remote-confirmed for 3 files
  remote witnesses online now: 1 peer for 3 files
  none-known for 11 files beyond local device

Fetchability, ghost risk, and admissible actions:
  posture: local-last-copy for 11 files
  admissible actions:
    - pin subtree
    - fetch/re-witness on another peer before evict
    - evict only the 3 remotely backed files now

Collateral effects on eviction, pinning, and serve value:
  full subtree evict would remove the last known full copy for 11 files: yes
  safe whole-subtree evict now: no

Receipt promise:
  frc_01QB... will prove local-last-copy findings and any bounded evict action chosen

$ anonsync file evict research datasets/2025/ --plan
Blocked.
Reason: 11 paths are local-last-copy and not currently remotely witnessed.
Suggested next action: pin subtree or create another full-copy witness first.
```

What this proves:

- placeholder visibility is not treated as proof that the bytes remain safely fetchable later
- the operator can distinguish ordinary eviction from `you are about to remove the last known full copy`
- CLI and richer surfaces can tell the same honest fetchability story without drift

## Flow 136 — retire a ghost announcement without pretending it is just a slow download

Problem: a peer can still see a file name in the tree, but every known source has already dematerialized or removed the bytes. The product should show that this is stale announcement residue, not an ordinary pending transfer.

```text
$ anonsync file availability media Episodes/ep042.mp3 --view review
Fetchability review: ftr_01QC...

Requested materialization intent:
  action: inspect failed fetchability
  scope: file media/Episodes/ep042.mp3

Visibility and local-residency reality:
  visibility: placeholder-visible
  local residency: no full local bytes
  announcement origin: remote tree merge 14m ago

Source backing and full-copy witnesses:
  local full copy: no
  remote confirmed witnesses: none
  last known source posture: now placeholder-only

Fetchability, ghost risk, and admissible actions:
  posture: ghost-risk
  requested fetch: cannot satisfy now
  admissible actions:
    - keep visible with guarded warning pending re-witness
    - retire stale announcement from local view with receipt
    - preserve current name-only visibility and wait for a real witness

Collateral effects on eviction, pinning, and serve value:
  local serve value: none
  destructive byte loss if retired now: none known

Receipt promise:
  frc_01QD... will prove ghost-risk posture and whether local visibility was retired or preserved

$ anonsync file resolve-ghost media Episodes/ep042.mp3 --mode retire-local-visibility --plan
Prepared.
Review says the path is announcement-visible but not honestly retrievable from any current witness.
```

What this proves:

- a ghost announcement is rendered as stale visibility truth, not a fake pending-download spinner
- the operator can choose between preserving guarded visibility and retiring it with a receipt
- placeholder-visible names and retrievable bytes stay visibly separate



## Flow 137 — split a mixed-risk subtree evict into honest batches instead of one optimistic bulk action

Problem: an operator selects a large subtree and wants to reclaim local space. Some rows are safely remotely backed, some are local-last-copy, and some are stale announcements. The interface should not flatten that into one cheerful `Evict subtree` action.

```text
$ anonsync file availability media Episodes/ --view review
Fetchability review: ftr_01QD...

Answer strip:
  visibility: placeholder-visible mixed with full local rows
  local residency: 37/120 rows have local bytes
  witness summary: 29 remote-confirmed, 6 local-only, 2 none-known
  fetchability: mixed safe-now + local-last-copy + ghost-risk
  safest next step: evict safe rows, re-witness 6 rows, retire 2 stale rows separately

Grouped review table:
  Safe now (29)
  Re-witness first (6)
  Stale / ghost (2)

$ anonsync file evict media Episodes/ --plan
Plan: pln_01QE...
Action split:
  - evict 29 safe rows now
  - keep 6 local-last-copy rows pinned pending new witnesses
  - do not evict 2 stale rows; offer retire-stale-announcement instead
```

What this proves:

- mixed-risk subtree work stays honest by default
- bulk convenience does not erase witness classes
- the plan proves later that the batch was intentionally split

## Flow 138 — render the same availability answer in workbench and CLI without semantic drift

Problem: a richer workbench may show chips and grouped rows, while a headless operator sees text. The product should not let those clients tell different stories about the same path.

```text
$ anonsync file availability media Episodes/ep042.mp3 --view review
Answer strip:
  Placeholder visible · No local bytes · None known · Ghost risk · Retire stale announcement

Requested action:
  inspect failed fetchability

Current visibility and local-byte truth:
  visibility: placeholder-visible
  local bytes: none

Witness evidence:
  remote confirmed witnesses: none
  last known source posture: placeholder-only

Admissible and blocked actions:
  blocked: fetch now
  allowed: keep visible with warning, retire stale announcement

Receipt promise:
  frc_01QF... will prove ghost-risk posture and chosen stale-announcement action
```

What this proves:

- CLI and workbench can render the same five-part answer in different visual forms
- the safer model survives headless use instead of depending on one rich client
- `available on demand` never becomes the only story in one surface while another surface knows better

## Flow 139 — offer restore instead of fetch when history still exists but the swarm no longer does

Problem: a file name is still visible and a local history entry still exists, but no current peer now witnesses durable full bytes. The product must not keep offering ordinary on-demand fetch just because the path once belonged to a selectively materialized share.

Workbench sketch:

```text
File availability — media/Episodes/ep177.mp3

Placeholder visible · No local bytes · History backed · Not fetchable · Restore from history

Requested action
  Inspect / recover this file

Current truth
  Visible in namespace: yes (placeholder projection)
  Local bytes: none
  Current swarm witnesses: none confirmed
  History entries: 2 local restore candidates

Admissible actions
  Primary: Restore from history
  Secondary: Keep visible with warning
  Blocked: Fetch now

Receipt promise
  frc_01QH... will prove history-backed-only posture and that restore, not swarm fetch, was the honest next verb
```

CLI sketch:

```text
$ anonsync file availability media Episodes/ep177.mp3 --view review

Placeholder visible · No local bytes · History backed · Not fetchable · Restore from history

Blocked actions:
  fetch-now  (no current full-copy witness)

Allowed actions:
  restore-from-history
  keep-visible-with-warning
```

Rules proven by this flow:

- history-backed-only is not equivalent to fetchable-now
- the presence of a placeholder or old namespace visibility does not keep `Fetch` honest after witnesses disappear
- the primary verb must switch from transfer language to restore language when the recovery path moved from swarm state to timeline state
- later receipts must prove that the product knew this distinction at decision time



## Flow 140 — scan one availability table and let the row decide direct action versus review

Problem: an operator is in a large subtree table and does not want to open a full pane for every row. The surface should allow direct action for obviously safe rows while still forcing review for guarded, stale, and history-backed rows.

```text
Workbench table

PATH                     LOCAL / VISIBILITY                SOURCE / RECOVERY     NEXT
Episodes/ep001.mp3       Placeholder, no local bytes      Remote-confirmed      Fetch now
Episodes/ep099.mp3       Bytes local here                 Local-only            Pin locally   Review
Episodes/ep177.mp3       Placeholder, no local bytes      History backed        Restore       Review
Episodes/ep201.mp3       Announcement only, no bytes      None known            Retire stale  Review
```

Interaction:

- clicking `Fetch now` on `ep001.mp3` performs the direct safe action or asks only for a lightweight confirmation
- clicking `Pin locally` on `ep099.mp3` opens review because the row is local-last-copy and the operator should see why ordinary evict is blocked
- clicking `Restore` on `ep177.mp3` opens review because the recovery path is timeline-backed rather than swarm-backed
- clicking `Retire stale` on `ep201.mp3` opens review because the operator should see that the row is stale visibility rather than a slow transfer

CLI parity sketch:

```text
$ anonsync file availability media/Episodes/ --view rows

PATH                  LOCAL/VISIBILITY              SOURCE/RECOVERY   NEXT            MODE
ep001.mp3             Placeholder, none             remote-confirmed  fetch-now       inline-direct
ep099.mp3             full-local                    local-only        pin-locally     inline-review
ep177.mp3             Placeholder, none             history-backed    restore         inline-review
ep201.mp3             Announcement, none            none-known        retire-stale    inline-review
```

Rules proven by this flow:

- row-level action honesty can stay fast without becoming magical
- direct mutation is reserved for clearly safe rows
- history-backed and stale rows keep different verbs even before the full review opens
- CLI and workbench can share the same presentation hints instead of inventing separate thresholds


## Flow 141 — keep a newly announced share visible without creating a local path, then claim it later into a chosen path

**Intent:** prove that AnonSync does not need Resilio-style default-path side effects just to make a share visible across a personal constellation.

### Situation

- `Studio-Laptop` announces `WorkDocs` to a linked constellation
- this laptop should know the share exists
- this laptop should **not** create a local path yet because the operator is waiting for an external disk
- later, the operator wants to claim the share into `/media/archive/WorkDocs` as a selective local cache

### Workbench path

1. Home shows a review item: `1 announced share not yet claimed here`
2. Opening it reveals an inbox row:

```text
WorkDocs   Linked from Studio-Laptop   Announced only   Keep deferred   Review
```

3. The operator clicks `Keep deferred`
4. Receipt confirms:

   - visible on this machine
   - not claimed into a local path
   - not withdrawn from sibling devices
   - reason: `wait for external disk`

5. Two days later the external disk is mounted
6. The operator opens the same inbox row and clicks `Review`
7. Review pane shows, in order:

   - subject and origin
   - requested local outcome
   - path and bind choice
   - authority and visibility consequences
   - local-only versus domain-wide effects
   - receipt promise

8. Operator chooses:

   - role: `laptop-cache`
   - path: `/media/archive/WorkDocs`
   - mode: `selective`

9. Because the path is empty, claim can proceed without reconciliation
10. Apply emits a claim receipt proving:

   - the share was previously visible here without bind
   - this machine later claimed it into the chosen path
   - the action changed this machine's bind state, not constellation-wide visibility defaults

### CLI sketch

```text
anonsync incoming list
anonsync incoming defer inc_01J... --reason "wait for external disk"
anonsync incoming show inc_01J...
anonsync incoming adopt inc_01J... --path /media/archive/WorkDocs --mode selective --role laptop-cache
anonsync claim receipt show clr_01J...
```

### Why this matters

A weaker product shape would have created a default-location directory immediately, then forced the operator through disconnect/reconnect/custom-path ritual later.
This flow proves the archive wants a different arrival contract:

- visibility first
- claim second
- bind third
- materialization fourth

## Flow 142 — approve one pending request from a narrow seat without pretending the whole constellation now auto-approves it

**Intent:** prove that AnonSync does not need Resilio-style same-identity owner folklore just to make peer approval convenient.

### Situation

- `Maya` requests access to `Photos-2026`
- three reviewed members are in the operator's personal constellation: `Laptop-Admin`, `Studio-Server`, and `Travel-Phone`
- `Laptop-Admin` may approve this share now
- `Studio-Server` may approve only for this share, not create future approval memory
- `Travel-Phone` is blocked because of mixed release posture
- the operator wants to approve **only this share now**, not widen future auto-approval across the constellation

### Workbench path

1. `Approvals` shows a row:

```text
Maya → Photos-2026   Seat: Laptop-Admin   No future scope   Review   Details
```

2. Opening review shows, in order:

   - requested approval action
   - acting seat and present authority
   - approval horizon and blast radius
   - share / constellation fallout
   - admissible actions
   - receipt promise

3. Seat chooser also shows:

```text
Laptop-Admin   personal    may approve this share or reviewed future scope
Studio-Server  appliance   may approve this share only
Travel-Phone   personal    blocked: mixed release posture
```

4. The operator first inspects the wider option and sees:

   - future approval memory would cover `Photos-* collaboration`
   - sibling reviewed members would inherit that future shortcut
   - this is guarded but admissible

5. The operator instead chooses the narrower path:

   - acting seat: `Studio-Server`
   - horizon: `this subject only`
   - verb: `Approve once`

6. Apply emits a receipt proving:

   - `Studio-Server` was the acting seat
   - `Photos-2026` was the only approved subject
   - no wider future approval memory was created
   - `Travel-Phone` remained blocked and uninvolved

### CLI sketch

```text
anonsync approval queue
anonsync approval review prepare aprq_01J... --seat mem_studio_server --scope this-subject --plan
anonsync approval review show aprv_01J...
anonsync approval approve aprv_01J...
anonsync approval receipt show aprc_01J...
```

### Why this matters

A weaker product shape would have let the operator click a generic `Approve` button from whichever linked device happened to be open, then only later discover that the effective trust shortcut was wider than the current share.
This flow proves the archive wants a different approval contract:

- request first
- reviewed seat second
- horizon choice third
- durable approval memory only if explicitly chosen


## Flow 143 — let prior trust recognize a new arrival without pretending that recognition already claimed or bound it here

**Intent:** prove that AnonSync can reuse remembered approval safely without inheriting Resilio-style `approved before` to `auto-connect here now` collapse.

### Situation

- `Maya` was previously approved for `Photos-2025 collaboration`
- that standing approval remains valid for `photos-collab` class arrivals from the same reviewed identity
- a new arrival `Photos-2026` appears on `Travel-Laptop`
- the approval memory match is real, but this machine has not yet chosen a local path or materialized bytes
- the operator wants low friction without losing truthful local-claim semantics

### Workbench path

1. `Incoming shares` shows a row:

```text
Photos-2026 from Maya   Prior trust matched   Local claim not started   Review   Details
```

2. Opening review shows, in order:

   - arrival and match evidence
   - what prior trust actually covers
   - local claim and bind effects
   - admissible actions
   - memory tighten / revoke options
   - receipt promise

3. The pane makes these facts explicit:

   - prior trust matched `photos-collab` class from Maya
   - this match may admit the arrival as `claim-suggested`
   - no local path is bound yet
   - no bytes will materialize unless claim review later chooses that outcome

4. The operator sees three honest verbs:

   - `Suggest claim`
   - `Require fresh review`
   - `Tighten memory`

5. The operator chooses `Suggest claim`.

6. Apply emits a receipt proving:

   - which standing approval matched
   - that the arrival was admitted only as `claim-suggested`
   - that no bind or materialization happened yet
   - that a later local claim receipt is still required for any path choice

### CLI sketch

```text
anonsync approval match queue
anonsync approval match review prepare apm_01J... --mode suggest-claim --plan
anonsync approval match review show apmr_01J...
anonsync approval match apply apmr_01J...
```

### Why this matters

A weaker product shape would have reused remembered approval as an invisible reason a new folder simply appeared connected at a default path.
This flow proves the archive wants a different contract:

- prior trust may match
- the match may lower friction
- local claim still remains explicit
- bind/materialization still require their own later truth


## Flow 144 — change future-arrival policy on one seat without silently rewriting the current share

**Intent:** prove that AnonSync can offer seat-level convenience without inheriting Resilio-style `change mode` semantics that also rewrite current bind or materialization truth.

### Situation

- `Home-NAS` already has `Photos-2026` claimed, bound at `/srv/family/Photos-2026`, and fully materialized
- future family-share arrivals are currently `claim-suggested`
- the operator wants `Home-NAS` to queue later family arrivals as `announce-only`
- the operator does **not** want the current `Photos-2026` bind or byte posture to change

### Workbench path

1. `Seat defaults` shows:

```text
Family arrivals on Home-NAS   Current default: claim-suggested   Review   Details
```

2. Opening review shows, in order:

   - current posture now
   - future-arrival policy
   - path provenance and collision posture
   - byte posture and fetch policy
   - admissible transitions
   - receipt promise

3. The pane makes these facts explicit:

   - `Photos-2026` remains bound at `/srv/family/Photos-2026`
   - local full bytes for the current share remain unchanged
   - only later arrivals in reviewed `family` scope will switch to `announce-only`
   - no existing path will be relocated, hidden, or dematerialized by this change

4. The operator sees three honest verbs:

   - `Queue future arrivals here`
   - `Keep claim suggestions`
   - `Open stronger automation review`

5. The operator chooses `Queue future arrivals here`.

6. Apply emits a receipt proving:

   - acting seat: `Home-NAS`
   - changed scope: `future-arrivals` only
   - new default: `announce-only`
   - current share `Photos-2026` remained bound and fully materialized

### CLI sketch

```text
anonsync presence policy show --seat home-nas --scope linked-arrivals:family
anonsync presence policy prepare --seat home-nas --scope linked-arrivals:family --default announce-only --plan
anonsync presence review show prr_01J...
anonsync presence apply prr_01J...
anonsync presence receipt show prc_01J...
```

### Why this matters

A weaker product shape would have changed one seat-level `mode` selector and left the operator guessing whether that meant:

- current share becomes disconnected
- future arrivals stop auto-binding
- current placeholders/full bytes change
- or all of the above

This flow proves the archive wants a different contract:

- present current share truth explicitly
- present future-arrival policy explicitly
- let the operator change one without silently rewriting the other


## Flow 145 — review a colliding suggested path without creating a silent `(1)` duplicate or rewriting seat defaults

**Intent:** prove that AnonSync can keep remembered roots and low-friction arrival placement without inheriting Resilio-style default-folder duplication and disconnect/reconnect folklore.

### Situation

- `Home-NAS` has family arrivals reviewed under root template `/srv/family/{{share_name}}`
- a new announced share `Photos-2025` arrives from a trusted family device
- the suggested candidate path is `/srv/family/Photos-2025`
- that path already exists locally and contains unrelated files from an old camera-import workflow
- the operator wants the share on this machine, but does **not** want a silent `/srv/family/Photos-2025 (1)` duplicate and does **not** want to rewrite the seat's future template just to place this one share

### Workbench path

1. `Incoming shares` shows:

```text
Photos-2025   Suggested: /srv/family/Photos-2025   Collision: occupied-unrelated   Review placement
```

2. Opening review shows, in order:

   - subject and current bind truth
   - suggested path and why
   - collision class and evidence
   - admissible placement outcomes
   - future-default impact
   - receipt promise

3. The pane makes these facts explicit:

   - the candidate came from the reviewed family root template
   - the candidate path is occupied by unrelated local files; same-lineage confidence is `none`
   - no bind exists yet for `Photos-2025` on this seat
   - future family-arrival template remains `/srv/family/{{share_name}}` unless explicitly changed in a separate action
   - the product will not silently suffix-create `/srv/family/Photos-2025 (1)`

4. The operator sees four honest verbs:

   - `Choose alternate path`
   - `Keep announced only`
   - `Keep claimed but unbound`
   - `Open template review`

5. The operator chooses `Choose alternate path` and enters `/srv/family/incoming/Photos-2025`.

6. Apply emits a receipt proving:

   - suggestion basis: `scope-template`
   - rejected colliding candidate: `/srv/family/Photos-2025`
   - collision class: `occupied-nonempty-unrelated`
   - chosen bind: `/srv/family/incoming/Photos-2025`
   - future template/default: unchanged

### CLI sketch

```text
anonsync placement suggest show --share photos-2025 --seat home-nas
anonsync placement review prepare --share photos-2025 --seat home-nas --candidate /srv/family/incoming/Photos-2025 --plan
anonsync placement review show plr_01J...
anonsync placement apply plr_01J...
```

### Why this matters

A weaker product shape would have silently created a sibling duplicate, or would have forced the operator to remember that `disconnect` and `connect` are really the path-placement UI.
This flow proves the archive wants a different contract:

- templates may suggest
- collisions must be typed
- alternate paths stay explicit
- one-share placement does not silently rewrite tomorrow's defaults


## Flow 146 — change a seat's future arrival root without moving current shares or silently refreshing old drafts

**Intent:** prove that AnonSync can improve standing seat convenience without inheriting Resilio-style default-folder / simple-mode semantics that quietly change future behavior and leave the operator guessing what else moved.

### Situation

- `Home-NAS` governs `family-arrivals` with standing template:
  - admission: `claim-suggested`
  - path template: `/srv/family/{{share_name}}`
  - collision default: `always-review`
- current bound share `Photos-2026` lives at `/srv/family/Photos-2026`
- current bound share `Scans-2026` lives at `/srv/family/Scans-2026`
- one still-unclaimed announced arrival `Videos-2026` already has a draft suggestion under the old template
- the operator wants future family arrivals to draft under `/tank/family/{{share_name}}`
- the operator does **not** want already bound shares moved and does **not** want the old `Videos-2026` draft silently rewritten

### Workbench path

1. `Seat templates` shows:

```text
Home-NAS / family arrivals   claim-suggested   /srv/family/{{share_name}}   drafts unchanged   Review template
```

2. Opening review shows, in order:

   - reviewed seat and governed scope
   - current standing template
   - proposed standing template
   - effect buckets
   - exceptions and pinned subjects
   - admissible actions
   - receipt promise

3. The pane makes these facts explicit:

   - future unseen family arrivals will draft under `/tank/family/{{share_name}}`
   - currently announced-but-unclaimed `Videos-2026` can either keep its old draft or be explicitly refreshed
   - currently bound shares `Photos-2026` and `Scans-2026` remain unchanged
   - no current bytes, binds, or path provenance on bound shares are touched by this review

4. The operator sees three honest verbs:

   - `Change standing template`
   - `Change standing template and refresh unclaimed drafts`
   - `Keep current template`

5. The operator chooses `Change standing template`.

6. Apply emits a receipt proving:

   - acting seat: `Home-NAS`
   - governed scope: `family-arrivals`
   - old path template: `/srv/family/{{share_name}}`
   - new path template: `/tank/family/{{share_name}}`
   - unclaimed drafts: unchanged
   - bound shares: unchanged

### CLI sketch

```text
anonsync arrival-template show --seat home-nas --scope family-arrivals
anonsync arrival-template review prepare --seat home-nas --scope family-arrivals   --path-template /tank/family/{{share_name}}   --draft-refresh unchanged   --plan
anonsync arrival-template review show atr_01J...
anonsync arrival-template apply atr_01J...
anonsync arrival-template receipt show atc_01J...
```

### Why this matters

A weaker product shape would have changed one seat default and left the operator guessing whether that meant:

- future arrivals go somewhere else
- open drafts already changed too
- current bound shares would later reconnect somewhere new
- or all of the above

This flow proves the archive wants a different contract:

- standing template edits are their own reviewed object
- open drafts refresh only by explicit choice
- current bound shares stay untouched
- later receipts prove that boundary


## Flow 147 — explain why this arrival is here now

### Situation

- `Home-NAS` is linked in a personal constellation
- Maya previously approved one device and chose to allow future sharing across linked devices
- `Home-NAS` has standing template `family-arrivals` with admission `claim-suggested` and path template `/tank/family/{{share_name}}`
- a new subject `Photos-2026` appears on `Home-NAS`
- the operator sees that the row is already `claim-suggested` and wants to know whether anything local already happened or whether the product is only explaining lower friction

### Workbench path

1. The arrival row shows:

```text
Photos-2026   claim-suggested   matched prior approval + family template   no local bind yet   Explain
```

2. Opening `Explain` renders the fixed explanation order from `101-effective-arrival-explanation-and-counterfactual-interface-spec.md`:

   - subject and current stage
   - why it is here now
   - governing standing state
   - what did not happen
   - counterfactuals
   - next honest actions
   - receipts and proofs

3. The causal chain says, in order:

   - subject was announced from linked family scope
   - prior approval memory matched Maya's identity and allowed lower-friction handling
   - standing template for `family-arrivals` suggested claim and drafted `/tank/family/Photos-2026`
   - no local claim was auto-applied
   - no local bind exists yet
   - no bytes were materialized

4. The `what did not happen` section explicitly says:

   - remembered approval did not itself create a local bind
   - the standing template did not widen future approval memory
   - the drafted path is not yet a committed path
   - already bound sibling shares remain unchanged

5. Counterfactuals show:

   - without remembered approval: `pending fresh review`
   - with announce-only template: `announced only` and no drafted candidate path

6. Honest next verbs are:

   - `Claim here`
   - `Open placement review`
   - `Keep announced only`
   - `Inspect approval memory`
   - `Inspect seat template`

### CLI sketch

```text
anonsync arrival explain --subject incoming:photos-2026 --seat home-nas
anonsync arrival explain --subject incoming:photos-2026 --seat home-nas --counterfactual no-approval-memory
anonsync arrival receipts --subject incoming:photos-2026 --seat home-nas
```

### Why this matters

A weaker product shape would have left the operator inferring, from scattered state, whether `Photos-2026` is here because the product already connected it, because a linked-device default fired, or because a prior approval simply lowered friction.
This flow proves the archive wants a stricter contract: one explanation surface, explicit non-causes, and explicit counterfactuals before any further local act.


## Flow 148 — preview exactly what a standing-policy change will touch

### Situation

- `Home-NAS` currently uses standing template `family-arrivals`
- that template is `claim-suggested` with default root `/srv/family/{{share_name}}`
- there is one unclaimed draft `Photos-2026`
- there is one claimed-but-unbound subject `Scans-2026`
- there is one bound share `Invoices-2025` with local bytes already materialized
- the operator wants future family arrivals to become `announce-only` under `/tank/family/{{share_name}}`, but does not want to disturb current binds or current bytes

### Workbench path

1. The standing-policy row shows:

```text
Home-NAS / family arrivals   announce-only + /tank/family/{{share_name}}   future-only unless drafts refreshed   bound shares unchanged   Preview impact
```

2. Opening `Preview impact` renders the fixed review order from `102-policy-delta-preview-and-arrival-simulation-interface-spec.md`:

   - acting seat and governed scope
   - current policy and proposed delta
   - effect buckets
   - example subjects
   - explicit non-effects
   - admissible actions
   - receipt promise

3. The effect buckets say:

   - `future unseen arrivals -> announce-only under /tank/family/{{share_name}}`
   - `announced-unclaimed -> unchanged unless refresh is selected`
   - `claimed-unbound -> unchanged; subset review required for any refresh`
   - `bound -> unchanged`
   - `materialized-bytes -> unchanged`
   - `approval memory and matches -> unchanged`

4. The example subjects section shows:

   - `Photos-2026 -> unchanged draft; old candidate path preserved unless refresh is selected`
   - `Scans-2026 -> unchanged; stronger subset review required`
   - `Invoices-2025 -> unchanged; current bind and current bytes stay untouched`

5. The explicit non-effects section says:

   - changing the default root does not rebind `Invoices-2025`
   - changing arrival admission to `announce-only` does not evict bytes from `Invoices-2025`
   - this edit does not widen or clear remembered approval memory
   - sibling seats remain unchanged

6. Honest next verbs are:

   - `Apply for future arrivals only`
   - `Apply and refresh unclaimed drafts`
   - `Open claimed-subject subset review`
   - `Keep current policy`

### CLI sketch

```text
anonsync policy delta preview --seat home-nas --scope family-arrivals --admission announce-only --path-template /tank/family/{{share_name}}
anonsync policy delta simulate --preview pdp_01J... --subject incoming:photos-2026
anonsync policy delta apply pdp_01J... --refresh unchanged
anonsync policy delta receipt show pdr_01J...
```

### Why this matters

A weaker product shape would have left the operator inferring whether the standing-policy edit only affects future arrivals, silently refreshes drafts, or quietly disturbs existing binds.
This flow proves the archive wants a stricter contract: effect buckets first, named example subjects second, explicit non-effects third, and receipt-backed apply last.



## Flow 149 — explain why an older draft still reflects a previous policy version

### Situation

- `Home-NAS / family arrivals` used to be `claim-suggested` under `/srv/family/{{share_name}}`
- the operator later changed the standing template to `announce-only` under `/tank/family/{{share_name}}`
- `Photos-2026` was announced before the policy change and still shows a drafted candidate path under `/srv/family/Photos-2026`
- `Letters-2026` arrived after the policy change and now remains `announced only`
- the operator wants to understand whether `Photos-2026` is stale, broken, or simply grandfathered

### Workbench path

1. The subject row shows:

```text
Photos-2026   current: announce-only /tank/family   applied: claim-suggested /srv/family   grandfathered draft   Explain policy lineage
```

2. Opening `Explain policy lineage` renders the fixed inspection order from `103-standing-policy-lineage-and-subject-attribution-interface-spec.md`:

   - seat, scope, and current effective version
   - version lineage
   - subject attribution
   - current-versus-applied compare
   - what did not change
   - admissible actions
   - receipts and proof links

3. The lineage section shows:

   - `v6 -> claim-suggested /srv/family/{{share_name}}`
   - `v7 -> announce-only /tank/family/{{share_name}}`
   - `v7 superseded v6 for future arrivals only; bound subjects untouched; drafts refreshed only by explicit choice`

4. The attribution section says:

   - `Photos-2026 -> applied under v6 at draft time`
   - `attribution class -> grandfathered`
   - `current policy now -> v7`

5. The compare section says:

   - `if Photos-2026 arrived now, it would remain announced and no candidate path would be created`
   - `current policy does not invalidate the older draft; it only means the draft reflects an older reviewed template`

6. The `what did not change` section explicitly says:

   - the standing-policy edit did not rewrite the old draft receipt
   - the current policy did not silently refresh this draft
   - already bound sibling shares remained untouched

7. Honest next verbs are:

   - `Keep grandfathered draft`
   - `Refresh draft under current policy`
   - `Inspect policy receipt`
   - `Inspect current standing template`

### CLI sketch

```text
anonsync subject policy show --subject incoming:photos-2026 --seat home-nas
anonsync policy lineage show --seat home-nas --scope family-arrivals
anonsync policy compare --current spv_01Jv7 --applied spv_01Jv6
anonsync policy receipt show pdr_01Jv7
```

### Why this matters

A weaker product shape would have left the operator guessing whether `Photos-2026` was stale, half-broken, or simply older than the current standing policy.
This flow proves the archive wants a stricter contract: policy version lineage first, subject attribution second, compare third, and only then any refresh or mutation verb.



## Flow 150 — review which current subjects should stay grandfathered versus realign to the current policy

### Situation

- `Home-NAS / family arrivals` is now on current policy `v8 announce-only /tank/family`
- older subjects still in view include:
  - `Photos-2026`, an unclaimed draft created under `v6 claim-suggested /srv/family`
  - `Scans-2026`, a claimed-but-unbound subject created under `v7 claim-suggested /tank/inbox`
  - `Invoices-2025`, a bound share intentionally kept at `/srv/family/Invoices-2025`
- the operator wants to clean up drift without pretending all three subjects can take the same action

### Workbench path

1. The seat row shows:

```text
Home-NAS / family arrivals   current v8 announce-only   1 refresh-eligible   1 subset review   1 pinned/grandfathered   Review drift
```

2. Opening `Review drift` renders the fixed inspection order from `104-subject-policy-drift-and-realignment-review-interface-spec.md`:

   - seat, scope, and target current policy
   - drift population summary
   - per-subject drift classes
   - proposed realignment effects
   - what will stay grandfathered or pinned
   - admissible actions
   - receipts and proof links

3. The drift rows show:

   - `Photos-2026 -> refresh-eligible`
   - `Scans-2026 -> subset-review-required`
   - `Invoices-2025 -> pinned exception`

4. Selecting only `Photos-2026` updates the effect summary to:

   - `will change -> old draft path under /srv/family is cleared`
   - `new result -> announced-only under current v8`
   - `will not change -> Invoices-2025 bind and current bytes stay untouched`

5. Selecting `Scans-2026` at the same time does **not** produce one optimistic bulk action.
   Instead the batch bar splits into:

   - `Refresh 1 eligible draft`
   - `Open subset review for 1 claimed subject`
   - `Keep 1 pinned exception`

6. The operator chooses:

   - `Refresh eligible draft` for `Photos-2026`
   - `Keep pinned exception` for `Invoices-2025`
   - leaves `Scans-2026` for later subset review

7. The receipt section records:

   - one realignment receipt for `Photos-2026`
   - the earlier exception-pin receipt for `Invoices-2025`
   - no mutation receipt for `Scans-2026` because it was only inspected

### CLI sketch

```text
anonsync policy drift list --seat home-nas --scope family-arrivals
anonsync policy realignment review prepare --seat home-nas --scope family-arrivals --subjects incoming:photos-2026 --outcome refresh-drafts --plan
anonsync policy realignment apply prp_01J...
anonsync subject exception pin --subject share:invoices-2025 --seat home-nas --reason "legacy bind intentionally retained"
anonsync policy drift show --subject incoming:scans-2026 --seat home-nas
```

### Why this matters

A weaker product shape would have left the operator with one current settings sheet, one lineage sheet, and a pile of non-uniform subjects.
This flow proves the archive wants a stricter contract: drift population first, per-subject classification second, split actions third, and only then any reviewed mutation.



## Flow 151 — re-review an intentional exception when its horizon is due

### Situation

- `Home-NAS / family arrivals` is currently on policy `v8 announce-only /tank/family`
- `Invoices-2025` remains intentionally bound at `/srv/family/Invoices-2025` as a reviewed pinned exception
- that exception was last renewed 170 days ago with a 180-day review horizon
- the operator wants to understand whether the product will silently keep it, silently force it back to current policy, or open one explicit re-review lane

### Workbench path

1. The exception-aging row shows:

```text
Invoices-2025   pinned exception vs current v8 announce-only   due in 10d   Renew exception
```

2. Opening `Renew exception` renders the fixed inspection order from `105-exception-aging-renewal-and-rereview-interface-spec.md`:

   - subject and current divergence
   - why this exception exists
   - review horizon and aging
   - what horizon reach does not do
   - admissible outcomes
   - receipts and proof links

3. The aging section says:

   - `aging class -> due-soon`
   - `review horizon -> 2026-09-14 America/New_York`
   - `last reviewed -> exception receipt exr_01J...`

4. The non-effects section explicitly says:

   - reaching the review horizon will not silently move the bind to `/tank/family`
   - reaching the review horizon will not silently evict current bytes
   - reaching the review horizon will not widen future approvals or change sibling subjects

5. The operator sees three distinct outcomes:

   - `Renew exception for 180d`
   - `Return subject to current policy through reviewed realignment`
   - `Keep without expiry` with an explicit acknowledgement that this removes the ordinary review timer

6. Choosing `Return subject to current policy` does not run instantly if stronger review is needed.
   Instead the product opens the appropriate follow-on review for any bind or byte changes.

7. The receipt section records either:

   - a renewal receipt with the next review horizon, or
   - a no-expiry acknowledgement receipt, or
   - a handoff into the stronger realignment review that will actually move the subject back toward current policy

### CLI sketch

```text
anonsync policy exception review list --seat home-nas --scope family-arrivals
anonsync policy exception review show --subject share:invoices-2025 --seat home-nas
anonsync policy exception renew prepare --subject share:invoices-2025 --seat home-nas --horizon 180d --plan
anonsync policy exception reconsider prepare --subject share:invoices-2025 --seat home-nas --outcome return-to-current-policy --plan
anonsync policy exception acknowledge-no-expiry --subject share:invoices-2025 --seat home-nas --reason "legacy bind remains intentionally permanent"
```

### Why this matters

A weaker product shape would have let the exception quietly live forever or quietly snap back toward current policy once some timer was reached.
This flow proves the archive wants a stricter contract: aging state first, explicit non-effects second, reviewed outcome split third, and only then any renewal or realignment work.

## Flow 152 — review a long-dormant remembered approval before it influences a new arrival again

### Situation

- `Maya / photos-collab` was first approved 14 months ago for `Photos family` arrivals
- the memory was never explicitly refreshed after the initial approval
- the linked-device set has grown since then
- a new `Photos-2026` arrival now matches that remembered trust
- the operator wants to know whether the product will silently reuse it, silently ignore it, or open one explicit trust-freshness lane first

### Workbench path

1. The approval-memory freshness row shows:

```text
Maya / photos-collab   granted: Maya + linked devices / Photos family   cooling   last used 214d ago   Touch-renew
```

2. Opening `Touch-renew` renders the fixed inspection order from `106-approval-memory-freshness-cooling-and-touch-renewal-interface-spec.md`:

   - remembered approval and granted scope
   - freshness evidence
   - what this memory may still do now
   - touch-renewal and narrowing options
   - freeze / require-fresh / revoke options
   - receipts and proof links

3. The freshness section says:

   - `freshness class -> cooling`
   - `last explicit review -> initial approval only`
   - `last exercised -> 214d ago`
   - `cooling reasons -> no recent use, linked device set changed`

4. The effects section explicitly says:

   - without touch renewal, later arrivals may still be recognized as the same identity but may not escalate to `claim-suggested`
   - touch renewal will not claim `Photos-2026`
   - touch renewal will not bind a path or materialize bytes
   - narrowing or freezing this memory will not mutate currently claimed or bound subjects

5. The operator sees five distinct outcomes:

   - `Touch-renew same scope`
   - `Narrow to reviewed seat + photos-only`
   - `Freeze reuse`
   - `Require fresh approval next time`
   - `Revoke memory`

6. Choosing `Narrow to reviewed seat + photos-only` produces a reviewed trust outcome only.
   The later arrival remains separate and still opens its own claim/bind review if adopted.

7. The receipt section records either:

   - a freshness receipt proving touch renewal,
   - a freshness receipt proving scope narrowing,
   - a freeze receipt proving future shortcut reuse is disabled,
   - or a revocation receipt proving remembered trust no longer authorizes later-arrival shortcuts

### CLI sketch

```text
anonsync approval memory freshness list --seat home-nas --scope family-arrivals
anonsync approval memory freshness show --memory apm_01Jmaya --seat home-nas
anonsync approval memory touch-renew prepare --memory apm_01Jmaya --seat home-nas --plan
anonsync approval memory narrow prepare --memory apm_01Jmaya --scope seat:home-nas/photos-only --plan
anonsync approval memory freeze apm_01Jmaya
anonsync approval memory require-fresh-next-time apm_01Jmaya
anonsync approval memory revoke apm_01Jmaya
```

### Why this matters

A weaker product shape would let old trust remain immortal until manual revocation, or else quietly stop reusing it without telling the operator why a previously smooth arrival suddenly became frictionful.
This flow proves the archive wants a stricter contract: freshness evidence first, non-effects second, reviewed trust outcome split third, and only then any later arrival-specific claim or bind work.


## Flow 153 — explain which exact remembered-trust node authorized a later arrival

### Situation

- `Maya / photos-collab` was first approved from `laptop-ember` 14 months ago for `Photos family`
- 21 days ago the operator narrowed remembered reuse to `home-nas / photos-only`
- a `Photos-2026` arrival appeared 34 days ago, before that narrowing
- the operator now wants to know whether the earlier lower-friction match came from the original approval, the later narrowed head, or something that no longer exists

### Workbench path

1. The approval-memory trace row shows:

```text
Maya / photos-collab   head: narrowed-to-home-nas/photos-only   cooling   last mutation 21d ago   Show trace
```

2. Opening `Show trace` for subject `Photos-2026` renders the fixed inspection order from `107-approval-memory-lineage-and-authorization-trace-interface-spec.md`:

   - remembered approval family and current head
   - origin approval act
   - lineage mutations since origin
   - which node authorized this later subject
   - how current trust differs now
   - receipts and proof links

3. The origin section says:

   - `origin approval receipt -> apr_01Jmaya_origin`
   - `acting seat -> laptop-ember`
   - `granted horizon -> Maya + linked devices / Photos family`
   - `identity epoch -> id_epoch_07`

4. The lineage section says:

   - `node 1 -> initial approval / origin scope`
   - `node 2 -> scope narrowed 21d ago / home-nas + photos-only`
   - `current head -> node 2`

5. The authorization section explicitly says:

   - `Photos-2026 matched under node 1`
   - `match time -> 34d ago`
   - `authorization posture at match -> active and cooling`
   - `this match did not claim the subject, bind a path, or materialize bytes`

6. The current-compare section explicitly says:

   - `under today's head, the same subject would not match without fresh review`
   - `later narrowing happened after the subject appeared`
   - `current trust is narrower than the trust version that explained the earlier match`

7. The receipt section records:

   - the origin approval receipt
   - the later narrowing receipt
   - the later arrival/match receipt tying `Photos-2026` to node 1 rather than node 2

### CLI sketch

```text
anonsync approval memory trace list --seat home-nas --scope family-arrivals
anonsync approval memory trace show --memory apm_01Jmaya --subject incoming:photos-2026 --seat home-nas
anonsync approval memory trace show --memory apm_01Jmaya --lineage
anonsync approval memory trace show --memory apm_01Jmaya --at 2026-02-12T16:12:00Z
```

### Why this matters

A weaker product shape would let the operator know only that trust was once approved and perhaps that it is now cooling, but still leave them reconstructing which exact trust version made the earlier shortcut possible.
This flow proves the archive wants a stricter contract: origin first, lineage second, subject-specific authorization node third, current-head compare fourth, and only then any follow-on review.

## Flow 154 — rebase a remembered-trust family after constellation mutation

### Situation

- `Maya / photos-collab` was originally approved 14 months ago for `Maya + linked devices / Photos family`
- `tablet-citrine` was later hidden from the linked-device list after long dormancy, but was never actually unlinked
- 3 days ago `desktop-ash` was linked using a device that already had a different certificate, so the new device took over the current identity epoch
- today `tablet-citrine` came back online and the operator wants to know whether old remembered approval still applies unchanged across `home-nas`, `tablet-citrine`, and `desktop-ash`

### Workbench path

1. The approval-memory rebase row shows:

```text
Maya / photos-collab   certificate takeover 3d ago   split recommended   2 descendants affected   Rebase trust family
```

2. Opening `Rebase trust family` renders the fixed inspection order from `108-approval-memory-constellation-mutation-and-family-rebase-interface-spec.md`:

   - remembered approval family and trigger
   - what constellation or identity changed
   - which descendants still inherit what
   - what definitely does not happen automatically
   - admissible outcomes
   - receipts and proof links

3. The trigger section says:

   - `current head -> apm_01Jmaya_head`
   - `triggering mutation -> certificate takeover observed for desktop-ash`
   - `secondary mutation -> hidden member tablet-citrine reappeared online`
   - `family posture -> split recommended`

4. The mutation section says:

   - `previous constellation -> laptop-ember, home-nas, tablet-citrine(hidden)`
   - `current constellation -> desktop-ash(new epoch), home-nas, tablet-citrine(reappeared)`
   - `identity epoch compare -> desktop-ash now speaks under id_epoch_08, origin approval was under id_epoch_07`

5. The descendant section says:

   - `home-nas -> inherits unchanged / same reviewed seat and same expected scope`
   - `tablet-citrine -> fresh required / hidden member reappeared after 214d offline`
   - `desktop-ash -> split into child family / certificate takeover changed identity epoch`

6. The non-effect section explicitly says:

   - this review does not renew freshness for any descendant
   - `tablet-citrine` does not silently regain warm shortcut status just because it reappeared
   - `desktop-ash` does not silently inherit the full old family without a reviewed child-family decision
   - this review does not claim any arrivals, bind any paths, or materialize any bytes

7. The operator chooses `Split into reviewed child families`, keeping `home-nas` as the current family, requiring fresh approval for `tablet-citrine`, and creating a reviewed child family for `desktop-ash` only after explicit confirmation.

8. The receipt section records:

   - the origin approval receipt
   - the triggering mutation receipt for certificate takeover
   - the descendant posture proof for `tablet-citrine` reappearance
   - the rebase receipt proving current-family carry-forward, fresh-required descendant, and child-family creation

### CLI sketch

```text
anonsync approval memory rebase list --seat home-nas --scope family-arrivals
anonsync approval memory rebase show --memory apm_01Jmaya --seat home-nas
anonsync approval memory rebase prepare --memory apm_01Jmaya --event cmt_01Jtakeover --outcome split-reviewed-branches --plan
anonsync approval memory rebase prepare --memory apm_01Jmaya --event cmt_01Jtakeover --outcome require-fresh-for-selected-descendants --descendant tablet-citrine --plan
anonsync approval memory rebase apply aprb_01Jmaya
```

### Why this matters

A weaker product shape would keep one remembered-trust family warm across a changed constellation and ask the operator to infer the fallout from device lists, hidden-member return, and identity history.
This flow proves the archive wants a stricter contract: trigger first, descendant posture second, explicit non-effects third, and only then reviewed split/freeze/fresh-required outcomes.

## Flow 155 — review descendant liveness after a hidden device reappears

### Situation

- `Maya / photos-collab` still has remembered approval lineage and a reviewed family rebase from the previous revision
- `tablet-citrine` was hidden 214 days ago, later reappeared, and now appears in lineage again
- the operator wants to know whether `tablet-citrine` is merely historical lineage, a current byte source, an approval-capable seat, or a reappeared descendant that still needs stronger proof

### Workbench path

1. The descendant-liveness row shows:

```text
tablet-citrine   inherits frozen   reappeared awaiting proof   guarded confidence   Freeze reuse until live
```

2. Opening `Freeze reuse until live` renders the fixed inspection order from `109-approval-memory-descendant-liveness-and-reachability-confidence-interface-spec.md`:

   - descendant identity and family posture
   - current liveness and confidence
   - what roles this descendant may honestly fill now
   - what definitely is not being claimed
   - admissible reviewed outcomes
   - receipts and proof links

3. The identity section says:

   - `approval family -> Maya / photos-collab`
   - `descendant -> tablet-citrine`
   - `inheritance posture -> inherits frozen`
   - `next honest action -> Freeze reuse until live`

4. The liveness section says:

   - `liveness class -> reappeared awaiting proof`
   - `confidence class -> guarded`
   - `last live observed -> 11m ago`
   - `last byte-source observation -> none since hidden`
   - `evidence basis -> mixed / reappearance proof + stale lineage`

5. The current-role section says:

   - `byte source -> not yet counted`
   - `approval-capable seat -> blocked pending fresh proof`
   - `historical explanation -> still visible`
   - `future convenience -> frozen until live evidence or fresh approval outcome`

6. The non-effect section explicitly says:

   - family membership does not prove that `tablet-citrine` still has bytes
   - reappearance does not silently restore warm approval-seat status
   - this review does not renew trust freshness, widen scope, claim arrivals, bind paths, or materialize bytes

7. The operator chooses `Record live observation` only after the product separately proves a current live session and byte-source capability; until then the descendant remains `reappeared awaiting proof` with reuse frozen.

8. The receipt section records:

   - the hidden-device receipt
   - the reappearance proof
   - the last direct live-observation receipt
   - the descendant-liveness receipt proving `freeze reuse until live`

### CLI sketch

```text
anonsync approval memory descendants list --seat home-nas --scope family-arrivals
anonsync approval memory descendants show --memory apm_01Jmaya --descendant tablet-citrine
anonsync approval memory descendants refresh --memory apm_01Jmaya --descendant tablet-citrine --outcome freeze-reuse-until-live --plan
anonsync approval memory descendants apply apdl_01Jmaya
```

### Why this matters

A weaker product shape would let the operator see that `tablet-citrine` came back and still belongs to the remembered family, then quietly treat that as if it also proved current byte-serving or approval-seat capability.
This flow proves the archive wants a stricter contract: family posture first, liveness class second, current-role honesty third, explicit non-effects fourth, and only then reviewed live-record or freeze outcomes.

## Flow 156 — review descendant capability before reusing a live linked device for a later arrival

### Situation

- `Maya / photos-collab` still has remembered approval lineage, descendant liveness, and a newly visible later arrival `incoming:photos-2026`
- `desktop-ash` is currently `recently-live`, but the operator still does not know whether it may honestly count as a byte source, an approval-capable seat, both, or neither for this subject
- the operator wants one truthful answer before trusting convenience implied by linked ownership and prior approval

### Workbench path

1. The descendant-capability row shows:

```text
desktop-ash   incoming:photos-2026   approval-seat   eligible after proof   Require fresh approval
```

2. Opening `Require fresh approval` renders the fixed inspection order from `110-approval-memory-descendant-role-eligibility-and-capability-proof-interface-spec.md`:

   - governed subject and descendant identity
   - candidate role and current eligibility
   - proof basis and blockers
   - what definitely is not being claimed
   - admissible reviewed outcomes
   - receipts and proof links

3. The identity section says:

   - `approval family -> Maya / photos-collab`
   - `subject -> incoming:photos-2026`
   - `descendant -> desktop-ash`
   - `next honest action -> Require fresh approval`

4. The capability section says:

   - `candidate role -> approval-seat`
   - `eligibility class -> eligible after proof`
   - `liveness class -> recently-live`
   - `current answer -> not yet allowed to approve this subject without fresh approval proof`

5. The proof section says:

   - `proof basis -> mixed / remembered approval lineage + live observation`
   - `blocking reason -> no current subject-scoped approval-seat proof`
   - `byte-source role -> separately eligible after byte proof only`
   - `linked ownership -> explanatory only, not verdict`

6. The non-effect section explicitly says:

   - current liveness does not prove approval-seat eligibility for this subject
   - linked ownership does not silently authorize this seat to approve here now
   - this review does not fetch bytes, claim the arrival, bind a path, or widen future trust reuse

7. The operator chooses `Require fresh approval` for the approval-seat role and leaves byte-source eligibility in `eligible after proof` until a distinct byte-source proof exists.

8. The receipt section records:

   - the remembered-approval lineage node
   - the descendant-liveness receipt proving `recently-live`
   - the descendant-capability receipt proving `approval-seat -> blocked fresh approval required`

### CLI sketch

```text
anonsync approval memory capability list --seat home-nas --scope family-arrivals
anonsync approval memory capability show --memory apm_01Jmaya --subject incoming:photos-2026 --descendant desktop-ash
anonsync approval memory capability prepare --memory apm_01Jmaya --subject incoming:photos-2026 --descendant desktop-ash --outcome require-fresh-approval --plan
anonsync approval memory capability apply apdc_01Jmaya
```

### Why this matters

A weaker product shape would see that `desktop-ash` is linked, remembered, and recently live, then quietly treat that as if it also proved current approval-seat or byte-source capability for this arrival.
This flow proves the archive wants a stricter contract: subject first, role second, eligibility third, blockers fourth, explicit non-effects fifth, and only then reviewed capability outcomes.


## Flow 157 — subject-level share policy overrides remembered approval reuse even when a descendant is eligible

### Situation

- `Maya / photos-collab` still has remembered approval lineage and `desktop-ash` is already separately eligible as an approval-capable seat for `incoming:photos-2026`
- the operator can therefore see a real standing approval match and a real descendant capability path
- however, this specific offer/share was emitted with a stricter policy equivalent to `fresh approval all peers`, so the subject still must not reuse old approval automatically

### Workbench path

1. The reuse-policy row shows:

```text
incoming:photos-2026   memory match with descendant   fresh approval all peers   fresh approval required   Open approval review
```

2. Opening `Open approval review` renders the fixed inspection order from `111-approval-memory-reuse-policy-and-subject-override-precedence-interface-spec.md`:

   - governed subject and standing match candidate
   - subject reuse policy and current precedence outcome
   - winning rule and blocker details
   - what definitely is not being claimed
   - admissible reviewed outcomes
   - receipts and proof links

3. The subject section says:

   - `approval family -> Maya / photos-collab`
   - `subject -> incoming:photos-2026`
   - `standing reuse candidate -> memory match with descendant`
   - `next honest action -> Open approval review`

4. The policy section says:

   - `subject reuse policy -> fresh approval all peers`
   - `precedence outcome -> fresh approval required`
   - `descendant capability -> separately eligible, but not sufficient`
   - `current answer -> old approval memory may not be reused for this subject without a new approval act`

5. The precedence section says:

   - `winning rule basis -> subject policy`
   - `blocking reason -> this offer requires fresh approval even for previously approved peers`
   - `standing memory -> still visible for explanation and trace`
   - `descendant eligibility -> still relevant after approval review, not before`

6. The non-effect section explicitly says:

   - remembered approval does not override this subject's stricter approval policy
   - descendant approval-seat eligibility does not silently authorize reuse here
   - this review does not itself approve the subject, widen future trust, claim a path, or materialize bytes

7. The operator chooses `Require fresh approval` for this subject and leaves standing memory visible as explanation-only support until the new approval act is actually completed.

8. The receipt section records:

   - the remembered-approval lineage node that would otherwise have matched
   - the subject-policy source/offer-security record showing `fresh approval all peers`
   - the descendant-capability receipt proving `desktop-ash` was eligible if reuse had been allowed
   - the reuse-policy receipt proving `subject override -> fresh approval required`

### CLI sketch

```text
anonsync approval memory reuse-policy list --seat home-nas --scope family-arrivals
anonsync approval memory reuse-policy show --memory apm_01Jmaya --subject incoming:photos-2026
anonsync approval memory reuse-policy prepare --memory apm_01Jmaya --subject incoming:photos-2026 --outcome require-fresh-approval --plan
anonsync approval memory reuse-policy apply aprp_01Jmaya
```

### Why this matters

A weaker product shape would see that remembered approval still exists and that `desktop-ash` is eligible to act, then quietly let those facts masquerade as permission to skip fresh approval for this subject.
This flow proves the archive wants a stricter contract: standing match first, subject reuse policy second, winning rule third, explicit non-effects fourth, and only then the actual approval action.


## Flow 158 — a single-use invitation is consumed for one subject without silently promoting broader remembered approval

### Situation

- Maya sends `incoming:photos-2026` with a single-use invitation artifact that was valid for one redemption only
- the claim succeeds and the governed subject is admitted locally
- current policy intentionally wants that success to stay `subject only` rather than silently promoting broader remembered approval for later unrelated subjects

### Workbench path

1. The trust-promotion row shows:

```text
offer consumed   claim applied   subject only   fresh approval next time   Keep this subject only
```

2. Opening `Keep this subject only` renders the fixed inspection order from `112-offer-artifact-expiry-and-trust-promotion-boundary-interface-spec.md`:

   - offer artifact and current redemption posture
   - claim outcome and promotion candidate
   - current durable-trust posture and later reuse posture
   - what definitely is not being claimed
   - admissible reviewed outcomes
   - receipts and proof links

3. The artifact section says:

   - `offer -> off_01Jmaya_photos_2026`
   - `delivery -> uri`
   - `artifact terminal posture -> consumed`
   - `redemption budget -> exhausted by first successful claim`
   - `next honest action -> Keep this subject only`

4. The claim section says:

   - `claim outcome -> claim applied`
   - `subject -> incoming:photos-2026`
   - `promotion candidate -> pending reviewed promotion`
   - `current question -> should this successful first claim create broader remembered approval or remain subject only?`

5. The durable-trust section says:

   - `promotion posture -> subject only`
   - `promotion scope basis -> offer policy plus approval review`
   - `later reuse posture -> fresh approval next time`
   - `current answer -> this invitation admitted this one subject but did not create family-level reuse convenience`

6. The non-effect section explicitly says:

   - the artifact being consumed does not keep it redeemable for another subject
   - the successful claim does not silently create broader remembered approval
   - future unrelated subjects still require their own approval/reuse decision
   - this review does not itself bind a path, widen a seat, or materialize bytes beyond the already-applied subject result

7. The operator leaves the outcome at `Keep this subject only` rather than `Promote to family reuse candidate`.

8. The receipt section records:

   - the original offer artifact receipt proving `single-use link`
   - the claim receipt proving first successful admission of `incoming:photos-2026`
   - the trust-promotion receipt proving `consumed artifact -> subject only -> fresh approval next time`

### CLI sketch

```text
anonsync offer promotion list --seat home-nas --scope recent-claims
anonsync offer promotion show --offer off_01Jmaya_photos_2026 --subject incoming:photos-2026
anonsync offer promotion prepare --offer off_01Jmaya_photos_2026 --subject incoming:photos-2026 --outcome keep-subject-only --plan
anonsync offer promotion apply otp_01Jmaya
```

### Why this matters

A weaker product shape would see that a single-use invitation succeeded once and then quietly treat the remote party as broadly trusted for later convenience.
This flow proves the archive wants a stricter contract: artifact lifetime first, claim success second, durable-trust promotion third, explicit non-effects fourth, and only then any later reuse story.

## Flow 159 — a named portable offer is redeemed by a different identity without silently becoming broad remembered trust

### Situation

- Mira creates a one-time offer for `incoming:tax-packet-2026`
- she copies the link into a message intended for `Noah`
- the actual redemption request arrives from `tablet-lapis`
- approval review can identify `tablet-lapis` clearly, but current policy does **not** want that alone to stand in for `this is the intended recipient and later broad trust is fine`

### Workbench path

1. The recipient-intent row shows:

```text
Named for Noah   Redeemed by tablet-lapis   Unexpected redeemer   No broad trust yet   Review mismatch
```

2. Opening `Review mismatch` renders the fixed inspection order from `113-offer-recipient-intent-and-redeemer-identity-boundary-interface-spec.md`:

   - offer artifact and sender intent
   - actual redeemer and proof
   - mismatch outcome and trust boundary
   - what definitely is not being claimed
   - admissible reviewed outcomes
   - receipts and proof links

3. The offer section says:

   - `offer -> off_01Jmira_tax_packet`
   - `delivery -> uri copied to messenger`
   - `recipient intent posture -> named-human-hint`
   - `intended recipient label -> Noah`
   - `next honest action -> Review mismatch`

4. The redeemer section says:

   - `actual redeemer -> tablet-lapis`
   - `proof basis -> approval-request fingerprint plus claim key proof`
   - `match class -> unexpected redeemer`
   - `current question -> should this unexpected redeemer be rejected, accepted for this subject only, or bound to one reviewed seat?`

5. The trust-boundary section says:

   - `mismatch outcome -> pending review`
   - `resulting promotion posture -> none yet`
   - `later reuse posture -> blocked until reviewed outcome exists`
   - `current answer -> successful redemption proof exists, but sender intent is not yet satisfied and no broader remembered approval has been created`

6. The non-effect section explicitly says:

   - a valid redemption request does not prove the sender meant the artifact for this redeemer
   - approval-time identity proof does not by itself widen trust beyond the reviewed outcome
   - accepting this redeemer for this subject would still not silently authorize later unrelated subjects
   - this review does not itself bind a path or materialize bytes beyond the already-reviewed claim path

7. Mira chooses `Accept for this subject only` rather than `Accept as expected` or any broader promotion outcome.

8. The receipt section records:

   - the original offer artifact receipt proving the one-time offer existed
   - the claim/approval receipt proving `tablet-lapis` was the actual redeemer
   - the mismatch receipt proving `unexpected redeemer -> accepted subject only -> no broad trust promoted`

### CLI sketch

```text
anonsync offer recipient-intent list --seat laptop-mira --scope recent-offers
anonsync offer recipient-intent show --offer off_01Jmira_tax_packet --subject incoming:tax-packet-2026
anonsync offer recipient-intent prepare --offer off_01Jmira_tax_packet --subject incoming:tax-packet-2026 --outcome accept-subject-only --plan
anonsync offer recipient-intent apply orp_01Jmira
```

### Why this matters

A weaker product shape would see that the offer was valid, the requester proved an identity, and the subject could be admitted, then quietly let those facts masquerade as `the intended recipient got it` and maybe even `future trust is fine`.
This flow proves the archive wants a stricter contract: sender intent first, actual redeemer second, mismatch outcome third, trust boundary fourth, explicit non-effects fifth, and only then any later reuse story.


## Flow 160 — a two-use portable offer is redeemed by two identities and the third attempt fails without collapsing the trust story

### Situation

- Maya creates a portable offer for `incoming:photos-2026` with `redemption limit = 2`
- `tablet-lapis` redeems first and is accepted `subject only`
- `desktop-ash` redeems second and is explicitly promoted to broader remembered approval
- a third later attempt from `phone-cedar` hits the exhausted budget and is denied

### Workbench path

1. The redemption-ledger row shows:

```text
Use 2 of 2 consumed   Partially consumed -> now consumed   tablet-lapis subject only   desktop-ash broader   Attempt 3 budget denied
```

2. Opening `Review ledger` renders the fixed inspection order from `114-offer-redemption-ledger-and-multi-redeemer-trust-fanout-interface-spec.md`:

   - artifact budget and terminal posture
   - redemption attempt ledger
   - per-attempt trust fanout
   - what definitely is not being claimed
   - admissible reviewed outcomes
   - receipts and proof links

3. The budget section says:

   - `offer -> off_01Jmaya_photos_multi`
   - `budget class -> bounded multi use`
   - `limit -> 2 successful redemptions`
   - `consumed -> 2`
   - `remaining -> 0`
   - `terminal posture -> consumed`
   - `next honest action -> Reissue new artifact`

4. The attempt ledger says:

   - `attempt 1 -> tablet-lapis -> approved subject only -> consumed one`
   - `attempt 2 -> desktop-ash -> approved broader -> consumed one`
   - `attempt 3 -> phone-cedar -> budget denied -> consumed none`

5. The trust fanout section says:

   - `tablet-lapis -> no broader remembered approval; subject only`
   - `desktop-ash -> broader remembered approval authorized by explicit review`
   - `phone-cedar -> no trust created`

6. The non-claims section says:

   - `artifact exhaustion does not revoke desktop-ash's already-created remembered approval`
   - `desktop-ash broader trust does not imply tablet-lapis got the same outcome`
   - `phone-cedar denial does not mean the earlier successful attempts were suspicious`

### Why this matters

A weaker product shape would say only `link used twice` or `two peers accepted` and make the operator reconstruct which trust outcome came from which attempt.
This flow proves the archive wants a stricter contract: artifact budget first, ordered attempts second, trust consequence per attempt third, non-effects fourth, and only then any reissue or revocation decision.

## Flow 161 — repeated redeemer, shared budget, and honest slot treatment

### Situation

- Maya created a portable offer with `limit 2`
- `tablet-lapis` already redeemed slot 1 for subject `incoming:photos-2026`
- later `tablet-lapis` hits the same artifact again after a browser retry and then again for a nearby but separately governed subject
- the product must not flatten both later events into one vague `already approved` story

### Expected surface

1. The operator opens:

   - `anonsync offer redemption-equivalence show --offer off_01Jmaya_bundle --subject incoming:photos-2026 --attempt oat_01Jretry`

2. The review pane preserves this order:

   - artifact budget and current attempt
   - nearest comparable earlier attempt
   - equivalence class and accounting policy
   - what definitely is not being claimed
   - admissible reviewed outcomes
   - receipts and proof links

3. The first later attempt says:

   - `budget -> 1 of 2 consumed`
   - `compare to -> tablet-lapis attempt 1`
   - `equivalence -> replay equivalent`
   - `policy -> collapse transport replay`
   - `slot effect -> collapse into slot 1`
   - `next honest action -> record replay receipt only`

4. A later attempt for a separately governed subject says:

   - `budget -> still 1 of 2 consumed before decision`
   - `compare to -> tablet-lapis attempt 1`
   - `equivalence -> same known peer new subject`
   - `policy -> consume per successful subject admission`
   - `slot effect -> consume new slot if approved`
   - `next honest action -> review and decide`

5. The non-claims section says:

   - `same redeemer does not by itself prove this should collapse`
   - `consuming a second slot does not imply the redeemer was suspicious`
   - `collapsing the replay does not widen remembered approval`

### Why this matters

A weaker product shape would say only `link used again by Maya's tablet` and force the operator to guess whether that burned the remaining budget.
This flow proves the archive wants a stricter contract: compare to a real earlier attempt, classify equivalence honestly, state the governing accounting policy, then say slot effect explicitly.


## Flow 162 — exhausted artifact, narrowed successor, and honest budget reset

### Situation

- Maya created a two-use portable offer for `incoming:family-album-2026`
- slot 1 went to `tablet-lapis`
- slot 2 was consumed by a carefully reviewed but broader-than-ideal redemption path
- Maya now wants to admit `Noah-laptop`, but the archive has already concluded the old artifact should not be stretched any further
- the product must not pretend that copying a fresh link is self-explanatory

### Expected surface

1. The operator opens:

   - `anonsync offer reissue-lineage show --predecessor off_01Jalbum_multi --subject incoming:family-album-2026`

2. The review pane preserves this order:

   - predecessor posture and why it stopped being the right artifact
   - successor scope and relation to predecessor
   - budget reset and carry-forward policy
   - what definitely is not being carried forward
   - admissible reviewed outcomes
   - receipts and proof links

3. The predecessor section says:

   - `predecessor -> off_01Jalbum_multi`
   - `terminal posture -> budget exhausted`
   - `reissue reason -> budget exhausted plus earlier broader-than-ideal redemption history`
   - `next honest action -> review successor boundary before issue`

4. The successor section says:

   - `requested outcome -> issue narrowed successor`
   - `successor relation -> narrowed successor`
   - `sender intent -> reviewed seat expected`
   - `approval policy -> all peers require approval`
   - `trust promotion default -> subject only`

5. The budget section says:

   - `budget reset posture -> fresh budget island`
   - `predecessor slot history -> explanation only`
   - `carried forward -> same governed subject label`
   - `not carried forward -> old remaining budget (none), old mismatch tolerance, old broader trust default`

6. The non-claims section says:

   - `issuing the successor does not erase earlier redemption receipts`
   - `same governed subject does not imply same budget family`
   - `remembered approval from earlier peers does not auto-admit Noah through the successor`
   - `new encoding would not have been enough here; this is a genuine successor boundary`

### Why this matters

A weaker product shape would say only `link expired/used up, create new link` and leave the operator to reconstruct whether the replacement artifact really started a fresh story.
This flow proves the archive wants a stricter contract: predecessor posture first, successor relation second, budget reset and non-carry facts third, and only then issuance of the replacement artifact.


## Flow 163 — browser landing page preview is not the same thing as authoritative local intake

Actors:

- **Ava** — folder owner issuing a portable offer
- **Ben** — receiver clicking the offer from a chat message
- **AnonSync** — the local product on Ben's machine

Goal:

Ben should be able to accept convenient browser/app handoff without losing the ability to tell what was merely previewed outside the app, what any external surface actually observed, and what only became authoritative after local inspection.

Initial conditions:

- Ava created a portable offer for subject `Research Photos`
- the offer is delivered to Ben via a chat message containing an HTTPS wrapper link
- Ben's browser has previously been allowed to launch AnonSync for this protocol family
- the delivery wrapper exposes a landing page that can preview folder name and approximate size

Steps:

1. Ben clicks the link in chat.
2. The browser opens a landing page that shows `Research Photos` and an approximate size hint.
3. Because Ben already allowed protocol launch earlier, the browser auto-hands the link to AnonSync.
4. AnonSync records a **delivery event** immediately before any claim is prepared.
5. The intake drawer shows a compact row:
   - `Received via: Browser auto-handoff`
   - `Preview said: Research Photos, approx size only`
   - `External touch: landing-page hit, fragment stayed local`
   - `Parsed locally: pending`
   - `Authoritative now: preview only`
6. Ben opens the intake explanation pane.
7. The explanation pane shows two separate blocks:
   - **Preview surface** — browser landing page, hint-only metadata, no trust or claim semantics implied
   - **Authority boundary** — app has not yet parsed the artifact; no claim/trust consequence has been established
8. Ben chooses `Inspect locally`.
9. AnonSync parses the artifact and updates the row:
   - `Received via: Browser auto-handoff`
   - `Preview said: Research Photos, approx size only`
   - `External touch: landing-page hit, fragment stayed local`
   - `Parsed locally: subject, expiry, sender-intent posture, redemption budget`
   - `Authoritative now: locally inspected`
10. The pane explicitly states non-effects:
    - browser preview did not prove byte availability
    - auto-launch did not prove fresh approval in this moment
    - local inspect did not yet grant local claim or broader remembered trust
11. Ben exports a delivery-handoff receipt for later audit.

Expected outcome:

- Ben gets browser/app convenience without letting `opened link` collapse preview, transport, parsing, and trust into one vague story
- delivery provenance remains inspectable even after later claim or approval work begins
- later support/debug/audit work can point to one durable receipt instead of browser folklore


## Flow 164 — wrapper link, protocol handoff, and QR are one canonical artifact until semantics change

Actors:

- Alice shares one portable offer for `Research Photos`
- Ben receives a copied browser wrapper link in chat
- Ben also later scans the QR code for that same share on another seat

Preconditions:

- Alice exported one offer through three carriers: wrapper URL, QR, and protocol handoff
- no scope, expiry, approval, or intended-recipient policy changed between those exports
- Ben already has one delivery event from browser click and one from QR scan

Steps:

1. Ben opens the offer detail page after both delivery events exist.
2. AnonSync shows one **Canonical artifact** row and two **Carrier observed** rows.
3. The wrapper link row renders:
   - `Carrier: wrapper URL`
   - `Authority: delivery wrapper`
   - `Equivalence: same canonical artifact`
4. The QR row renders:
   - `Carrier: QR payload`
   - `Authority: authority-bearing alias`
   - `Equivalence: same canonical artifact`
5. Ben opens `Why same/not same`.
6. The explanation says:
   - shared semantic fields match
   - wrapper-only differences are delivery mechanics, not offer semantics
   - no fresh budget island was created
   - no successor lineage was created
7. Ben exports a carrier-alias receipt.
8. Later, Alice issues a narrowed successor with shorter expiry.
9. Ben receives a new wrapper link that looks similar.
10. AnonSync now renders:
    - old wrapper link -> `same canonical artifact` under the old offer
    - new wrapper link -> `successor not alias`
11. The explanation states that carrier shape looked similar, but governed semantics changed, so collapse would be dishonest.

Expected outcome:

- carrier convenience stays useful without letting wrapper shape or QR format stand in for artifact identity
- budget, trust, and lineage consequences attach to the canonical offer, not whichever carrier happened to be seen last
- successor issuance remains explicit even when the transport shell looks familiar


## Flow 165 — landing-page hints orient the operator without becoming authority truth

Scenario:

- Alice shares a folder with Ben through a normal Sync link
- Ben first sees the offer through a browser landing page, and later the local app parses the offer

Preconditions:

- the offer has one canonical artifact identity already known after local parse
- the landing path showed a folder label and approximate size as recognition hints
- the authority-bearing payload stayed sealed until the local app parsed it

Steps:

1. Ben clicks the wrapper link in a browser.
2. AnonSync records a delivery event and one carrier alias.
3. Before local parse completes, the intake surface renders:
   - `Preview hints: folder label, approx size`
   - `Sealed until parse: artifact id, authority-bearing fields, policy-bearing fields`
   - `Authoritative now: none yet`
   - `Not enough yet: no claim/trust/budget inference from preview alone`
4. Ben opens `Why not enough yet`.
5. The explanation says:
   - preview hints help recognition only
   - the current carrier is still only preview-level for several important fields
   - local parse is required before canonical field semantics can be cited
6. The local app parses the artifact.
7. The same surface now renders:
   - `Preview hints: unchanged`
   - `Sealed until parse: none for already-parsed fields`
   - `Authoritative now: canonical artifact id, policy-bearing fields`
   - `Still not enough: approval and later trust not yet granted`
8. Ben exports a field-partition receipt.
9. Later claim review cites the exact authoritative-after-parse fields it relied on.

Expected outcome:

- landing-page preview remains useful without pretending to authorize later actions
- sealed fields remain explainable instead of mysterious
- later claim/trust/budget surfaces can cite the exact field classes they actually used


## Flow 166 — label-and-size familiarity stays recognition-only until omitted governance fields are cleared

Scenario:

- Alice shares a portable offer for `Research Photos`
- Ben receives the wrapper link in chat and first sees only the browser preview

Preconditions:

- the browser preview shows a folder label and approximate size
- the product knows the preview omitted permission class, approval posture, expiry policy, and use-count policy
- Ben has not yet run local parse inside AnonSync

Steps:

1. Ben clicks the wrapper link.
2. The intake row renders immediately:
   - `Preview showed: Research Photos, approx size`
   - `Missing governance: permissions, approval, expiry, use count`
   - `Enough for: recognition`
   - `Not enough for: governance or trust`
   - `Next action: Inspect locally`
3. Ben says `This looks like the right share.`
4. The `Why not enough yet` drawer explains:
   - the preview is sufficient to recognize the likely subject
   - it is not sufficient to know whether the offer is read-only, read-write, owner-capable, expiring soon, or near budget exhaustion
   - no trust or claim outcome may cite the browser preview as proof of those omitted facts
5. Ben chooses `Inspect locally`.
6. AnonSync parses the artifact and updates the row:
   - `Missing governance: none from artifact parse`
   - `Enough for: recognition, offer-governance inspection`
   - `Not enough for: approval still required`
7. Ben exports a preview-sufficiency receipt.
8. Later approval review cites the locally parsed fields and explicitly does **not** cite browser familiarity as governance proof.

Expected outcome:

- recognition stays useful without turning into stealth policy inference
- omitted governance fields become visible product truth instead of invisible absence
- later approval or claim receipts can prove they did not rely on preview familiarity alone
## Flow — browser preview to local parse without premature acceptance

1. Operator clicks a portable offer in a browser.
2. Browser surface shows only preview-visible hints.
3. Offer row appears as `Current rung: recognition only` with `Missing: permissions, expiry` and `Next: inspect locally`.
4. Operator continues into local inspect.
5. Local app parses the artifact.
6. Same row advances to `Current rung: locally parsed, review still needed`.
7. Surface now shows newly available policy fields while preserving the earlier preview facts.
8. Primary action becomes `Prepare claim`, not `Accept`.
9. Receipt chain proves preview, parse, and claim remained separate.

## Flow — parsed portable offer to reviewed claim

1. Operator opens a parsed-but-unreviewed portable offer.
2. Detail pane shows:
   - what arrived
   - what was visible at preview
   - what parse added
   - what is still blocked
3. Operator selects local path, role, and materialization mode.
4. Surface advances to `Current rung: claim prepared`.
5. Drift or blocker checks are re-run.
6. Apply commits the local outcome.
7. Final receipts prove:
   - preview did not imply acceptance
   - parse did not imply acceptance
   - claim preparation did not imply apply
   - apply committed the reviewed local outcome only


## Revision addendum — issuance and publication flows

### Canonical flow: reviewed portable-offer issuance

1. Operator clicks `Share` or `Issue offer`.
2. Surface opens a composer draft instead of immediately emitting a carrier artifact.
3. Operator reviews audience, preview-visible fields, sealed-until-parse fields, offered role, approval posture, expiry, and redemption budget.
4. Surface renders issuance non-effects (`no trust widened yet`, `no path bound remotely`, `no ambient publication implied`).
5. Operator issues the offer and receives an issuance receipt.

### Canonical flow: reviewed constellation publication

1. Operator opens a subject and chooses `Publish to members`.
2. Surface renders the current publication state per target member or class.
3. Operator chooses arrival posture (`announced only`, `claim review required`, `encrypted only`, etc.) without implying path bind.
4. Surface renders authority effects and non-effects.
5. Operator applies the publication plan and receives a publication receipt.


## Revision addendum — publication matrix and role-first adoption flows

### Canonical flow: inspect living publication truth as a matrix

1. Operator opens `Publication matrix` for a subject family or constellation view.
2. Surface renders explicit subject × member cells instead of ambient member badges.
3. Operator selects one cell.
4. Cell detail shows current posture, provenance kind, unresolved local work, authority effect, and latest receipt.
5. Operator either keeps the cell, overrides it, or reverts it to template.

### Canonical flow: role-first arrival on one member

1. Operator opens an announced or claim-review-required arrival from the inbox or matrix.
2. Surface first shows admissible roles for that member and subject.
3. Operator chooses `observer`, `writer`, `encrypted replica`, or another admissible role.
4. Only then does the surface offer path and materialization choices suitable for that role.
5. Apply commits the reviewed adoption and emits a receipt proving role, path, and byte posture remained separate choices.


## Revision addendum — publication-delta and member-policy flows

### Canonical flow: preview publication delta before apply

1. Operator edits a publication template, subject publication, or override.
2. Surface does not jump straight to apply.
3. Instead it renders a delta preview over the affected subject × member cells.
4. Each affected row states `before`, `after`, `authority delta`, `local work delta`, and `why this cell is affected`.
5. Unchanged cells may be collapsed but remain countable and inspectable.
6. Operator applies the reviewed delta and receives one receipt that cites the previewed delta set.

### Canonical flow: inspect and change one member's future-arrival defaults

1. Operator opens a member card.
2. Surface shows relationship, current publication counts, future-arrival defaults, default roots, exceptions, and latest receipts.
3. Operator chooses `Review member policy`.
4. Review pane states clearly what this change affects in the future and what it does **not** rewrite now.
5. If the change would alter existing subject/member cells, the flow opens the publication-delta preview automatically.
6. Apply commits the reviewed member-policy change and emits a receipt.


## Flow 94 — inspect a just-applied publication change without confusing it with recall

Problem: the operator recently narrowed or withdrew publication and now needs to know what exactly changed, who has observed it, and whether any stronger recall claim is still unsupported.

### Goals

- inspect the reviewed mutation after apply
- tell `applied locally` from `observed by target`
- jump to retained-copy review instead of over-reading withdrawal

### Expected surface

1. The operator opens `Publication history` and selects one recent mutation row.
2. The mutation pane shows:
   - mutation kind and initiating review
   - source delta preview and applied cell count
   - per-member observation rows
   - explicit non-effects including `does not prove retained-copy removal`
3. The operator may choose:
   - `Wait for observation`
   - `Open member arrival review`
   - `Open retained-copy review`
   - `Export mutation receipt`

### Good outcome

The operator can prove what changed, what has been observed, and what still remains outside the scope of this mutation ledger.

## Flow 95 — draft a member-policy edit from the card without silently committing it

Problem: the operator wants to change one member's future-arrival defaults quickly, but the product must not let an inline toggle silently commit a semantic change whose precedence or retroactivity is unclear.

### Goals

- allow fast editing from the member card
- keep inheritance and explicit null visible
- escalate to wider review only when warranted

### Expected surface

1. The operator changes a compact control on the member policy card.
2. The card enters `draft prepared` state rather than `saved`.
3. Opening the draft shows:
   - changed fields
   - current and requested inheritance mode
   - precedence ladder for each changed field
   - representative simulation cases
   - explicit non-effects on current state
4. If zero existing cells are affected and no conflicts exist, a compact review sheet may offer `Apply future-only change`.
5. Otherwise the flow escalates to full editor and, when needed, the publication-delta preview.

### Good outcome

Convenience is preserved, but no semantic member-policy change is committed without one reviewed draft that explains precedence and retroactivity honestly.


## Revision note — two more canonical flows

This revision adds two canonical review flows that the CLI and workbench must both support:

1. **Explain one concrete arrival**
   - start from a visible `(subject, member)` cell
   - open the arrival-causality explanation
   - inspect eligibility source, claim/approval path, winning role cause, winning path cause, and winning byte-posture cause
   - compare with nearby counterfactuals if needed
   - export an explanation receipt if the answer must be preserved

2. **Preview future arrivals for a member-policy draft**
   - start from a member-policy draft
   - inspect current-cell impact classification
   - inspect representative future-arrival scenarios
   - inspect widening versus narrowing callouts
   - either apply, recompute, or open the touched-current-subject review if the draft is not truly future-only


## Revision addendum — convergence and intervention flows

The canonical flows now need two more endgame branches after publication or arrival review:

1. **Inspect convergence window**
   - open from any pending mutation row, matrix cell, or arrival card
   - review strongest verdict, fresh evidence, stale/missing evidence, and blocked claims
   - either keep waiting, open intervention review, or close as superseded

2. **Run wait-vs-intervene review**
   - open when a convergence window remains open and more than one plausible next move exists
   - inspect recommended action, nearby non-recommended actions, blocked unsafe actions, and what evidence would change the verdict
   - emit one decision receipt instead of encouraging reconnect folklore or setting toggles as ritual


## Flow 96 — inspect a pending gap without falling into troubleshooting archaeology

Problem: the operator sees that a subject/member cell remains unresolved and the current recommendation is not simply `wait`, but the product must not force them to reconstruct the ambiguity from scattered route, source, local, and policy clues.

### Goals

- group fresh evidence and missing evidence on one page
- preserve several live hypotheses without losing one primary uncertainty
- recommend one bounded probe without silently mutating anything

### Expected surface

1. The operator opens `Convergence evidence` from a convergence window or decision sheet.
2. The bundle shows:
   - desired state and current unresolved gap
   - primary uncertainty plus nearby hypotheses
   - evidence-family rows for announcement, route, liveness, source, local prerequisites, policy, and resource health
   - missing/stale rows kept separate from negative rows
   - one recommended bounded probe
   - explicit `still not proven` notes
3. The operator may choose:
   - `Run recommended probe`
   - `Export evidence packet`
   - `Return to wait-vs-intervene`

### Good outcome

The operator can explain what is actually unknown, what is already known, and why the next probe is justified without opening support docs or inventing ritual.

## Flow 97 — record an intervention and prove whether it changed anything

Problem: the operator has a justified next action, but the product must not let that action dissolve into vague `tried again` history or accidental collateral change.

### Goals

- bound every material intervention by explicit scope
- state what the attempt is forbidden to touch
- force a fresh after-action verdict

### Expected surface

1. The operator starts an intervention attempt from the decision sheet or evidence bundle.
2. The attempt page shows:
   - chosen action and target gap
   - justification receipt
   - scope and forbidden collateral changes
   - preconditions
   - live/outcome artifacts
3. When the attempt completes, the product automatically renders a post-action recompute block showing:
   - verdict before → after
   - changed or unchanged primary uncertainty
   - next strongest recommendation
4. The operator may choose:
   - `Close and return to convergence`
   - `Open new evidence bundle`
   - `Open next intervention`

### Good outcome

A later operator can prove what was tried, why it was justified, what it was not allowed to change, and whether it actually moved the system.


## Flow 83 — approve a heavier diagnostic probe without silently widening capture

1. The operator opens an unresolved diagnostic incident from the convergence evidence bundle.
2. The product explains why ordinary evidence refresh is no longer enough.
3. The operator reviews a probe plan showing:
   - uncertainty trigger
   - included classes
   - excluded classes
   - intrusiveness and expected cost
   - auto-stop boundary
   - what the probe still cannot prove
4. The operator approves the probe or sends it back for a lighter plan.
5. The resulting capture stays local-only by default and returns to the incident as reviewed staged evidence.

CLI sketch:

```text
anonsync diagnostic probe plan --incident dgi_01J... --kind transfer-sample --for 5m --plan
anonsync diagnostic probe approve dpp_01J...
anonsync diagnostic probe receipt dpp_01J...
```

## Flow 84 — disclose a minimized escalation packet to a named recipient

1. The operator starts from a sealed evidence bundle or probe result.
2. The product asks what unresolved question the outbound packet is meant to help answer.
3. The operator chooses the recipient class.
4. The packet review shows included artifacts, omitted artifacts, redaction decisions, and recall-limit warnings.
5. The operator seals the manifest and sends the packet.
6. The product stores a durable disclosure receipt.

CLI sketch:

```text
anonsync escalation packet draft --incident dgi_01J... --recipient trusted-operator --question "interpret repeated route contradiction"
anonsync escalation packet review eep_01J...
anonsync escalation packet send eep_01J...
```


## Flow additions from rev0147

### Remembered approval reopened by material change

1. operator opens remembered approval family
2. product shows trigger row and due clock state
3. product states current reuse posture (`guarded` or `frozen-pending-reapproval`)
4. operator chooses `reapprove same scope`, `reapprove narrowed`, `freeze until fresh`, `revoke`, or `mark non-material with receipt`
5. product records reapproval receipt and updates current lineage head if needed

### Current shareable head from retained packet family

1. operator opens outgoing artifact family
2. product shows retained members, tips, operational head, and shareable head
3. product preserves warnings if latest tip is not frozen or audience-correct
4. operator opens shareable head or freezes current tip as new shareable head
5. product records shareable-head receipt


## Flow 167 — keep eligible-seat continuity visible while requiring explicit rerequest on a newer approval basis

**Intent:** prove that AnonSync does not need one vague reviewer/approver badge to represent seat relevance, live request state, completed review, and later rerequest all at once.

### Situation

- `Maya → Photos-2026` is pending on the operator's constellation
- `Laptop-Admin` and `Studio-Server` remain eligible approval seats
- `Laptop-Admin` previously reviewed the earlier approval basis for the same subject
- since then, the current approval basis changed enough that the prior review no longer binds automatically
- the operator wants the product to keep seat continuity visible without pretending a current live ask already exists

### Workbench path

1. `Approvals` shows a row:

```text
Maya → Photos-2026   Seats: Laptop-Admin reviewed, Studio-Server eligible   Active: rerequest needed   Re-request   Details
```

2. Opening review shows, in order:

   - current approval basis
   - seat roster and present eligibility
   - current active request state
   - latest review witness versus current basis
   - request, rerequest, clear, or switch-seat actions
   - receipt promise

3. The pane makes these facts explicit:

   - `Laptop-Admin` remains eligible and historically relevant
   - no live request currently targets the new basis
   - the older review witness belongs to the previous basis only
   - the honest next step is `Re-request on current basis` or `Switch to narrower seat`

4. The operator chooses `Re-request on current basis` for `Laptop-Admin`.

5. Apply emits a coordination receipt proving:

   - the seat remained on the roster throughout
   - the previous reviewed basis did not silently remain current
   - a fresh explicit rerequest was opened for the newer basis
   - `Studio-Server` remained eligible but not currently requested

### CLI sketch

```text
anonsync approval coordination show aprq_01J...
anonsync approval request rerequest aprq_01J... --seat mem_laptop_admin --basis apb_01K... --reason basis-drift --plan
anonsync approval coordination receipt show apcr_01K...
```

### Why this matters

A weaker product shape would have either hidden `Laptop-Admin` after the older review completed or silently marked it pending again on the newer basis.
This flow proves the archive wants a different coordination contract:

- seat continuity may survive completed review
- current request state is separate from seat relevance
- later basis drift yields explicit rerequest-needed truth
- a fresh current ask requires a fresh explicit witness


## Flow additions from rev0148

### Approval coordination split

1. operator opens a pending approval with more than one relevant seat
2. product shows eligible-seat roster separately from live current request state
3. if no seat is currently requested, the row says `eligible, no active request` rather than `waiting on review`
4. if a prior review bound an older basis, the row says `rerequest needed`
5. operator explicitly opens or reopens a live request and receives a coordination receipt


## Flow additions from rev0149

### External guidance stays reviewable even after the live source changes

1. operator opens a vendor help-center article or ticket reply from an incident
2. product records the live source row and fetches one local snapshot
3. operator freezes one exact excerpt set as the local review basis
4. product translates part of that basis into a bounded probe or recipe while preserving unsupported residue
5. days later the live source redirects or changes text
6. product records a drift-check row and says whether follow-up is needed
7. older local translation and basis receipts still point to the original snapshot and excerpt set rather than silently inheriting the newer page


## Flow additions from rev0151

### Copy or share a frozen packet without pretending the recipient already has it

1. operator opens the current shareable head for an escalation packet family
2. product shows available channels: clipboard, download, web-share, attachment export
3. operator picks `Clipboard` from local web
4. product records one outbound channel execution row:
   - `channel -> clipboard-text`
   - `observed -> clipboard updated locally`
   - `witness -> none beyond local completion`
   - `claim ceiling -> copied`
   - `forbidden labels -> sent, delivered, received`
5. hours later the same packet is moved through mobile `Web Share`
6. product records a second execution row and preserves platform variance if the surface only proved `share invoked`
7. only after a same-product redeem or imported recipient acknowledgment does the current claim ceiling rise above those weaker channel truths


## Flow additions from rev0152

### Refresh a previously shared packet without forcing manual lineage diff

1. operator opens an escalation-packet family that already has one prior disclosed head and one newer frozen shareable head
2. product shows three adjacent surfaces:
   - current shareable head
   - carryforward verdict against the prior disclosed head
   - compact delta ledger
3. the verdict says `refresh-in-place` rather than just `new version`
4. the delta ledger says:
   - question prompt unchanged
   - recipient class unchanged
   - one fresh route snapshot added
   - timeline window refreshed to newer timestamps
5. product generates one visible refresh notice:
   - `Same incident packet family; prior question unchanged; added one fresh route snapshot and newer timeline slice.`
6. operator chooses `Send new head with refresh notice`
7. outbound execution and later delivery witness remain separate from the carryforward verdict itself
8. if a later packet widens audience or changes authority scope, the next verdict becomes `reopen-required` and the compact refresh note path is blocked


## Flow additions from rev0153

### Show who actually owns background startup without confusing it with current health

1. operator opens ordinary status on a Linux host after a recent service migration
2. product shows runtime bridge first:
   - `runtime: healthy now`
   - `claim ceiling: current runtime only`
3. operator opens `Startup owner`
4. product shows candidate rows:
   - user service → `enabled`
   - desktop autostart → `conditional / TryExec failed last boot`
   - system service → `missing`
5. product states:
   - `effective owner -> user service`
   - `duplicate risk -> none now`
   - `recent drift -> duplicate cleared yesterday`
   - `current runtime correlation -> matches effective owner`
6. if current runtime had been manual-only, the same flow would instead say `runtime healthy now, startup owner missing`
7. operator can now answer both `is it working now?` and `who will bring it back later?` without reading raw service-manager or desktop-startup state by hand


## Flow additions from rev0154

### Refuse a stale packet issue instead of silently inheriting the newer basis

1. operator reviewed an escalation-packet issue yesterday against:
   - shareable head `pkt_01K4...`
   - approval basis `apb_01K7...`
2. overnight, one newer packet head `pkt_01K5...` becomes current and the approval basis reopens to `apb_01K8...`
3. operator presses `Issue current packet` from the older reviewed surface
4. product does **not** silently bind that click onto the newer packet or newer approval basis
5. instead it records a stale-attempt row showing:
   - expected shareable head `pkt_01K4...`
   - current shareable head `pkt_01K5...`
   - expected approval basis `apb_01K7...`
   - current approval basis `apb_01K8...`
   - verdict `reissue-needed`
6. the pane offers:
   - `Compare old and current basis`
   - `Reissue on current basis`
   - `Cancel old reviewed action`
7. operator chooses `Reissue on current basis`
8. product opens a new reviewed action that may carry forward selected prose and recipients, but it still points at the newer packet head and newer approval basis explicitly
9. apply later emits a reissue receipt proving the newer basis was reviewed, rather than pretending the older click silently covered it


## Flow additions from rev0155

### Refuse a reviewed support packet after recipient retarget instead of silently following the new destination

1. operator previously reviewed a frozen escalation packet for recipient target:
   - `support-vendor / ticket mailbox A`
2. before send, the operator edits the destination to:
   - `community forum paste`
3. product compares the reviewed target rows with the current target rows
4. product does **not** silently treat the old review as permission for the new destination
5. instead it records a target-guard row showing:
   - expected target `ticket mailbox A`
   - current target `public forum post`
   - verdict `widened-target`
   - next action `retarget reissue required`
6. the pane offers:
   - `Compare old and current target`
   - `Reissue for new target`
   - `Keep old target`
   - `Cancel old action`
7. operator chooses `Reissue for new target`
8. product opens a new reviewed action that may carry forward the packet family and selected prose, but it still points at the new public destination explicitly
9. old copied/downloaded history remains attached to the old target only, and later send emits a retarget-reissue receipt proving the wider destination was explicitly re-reviewed

## Flow additions from rev0156

### Keep the older vendor-facing packet current until the queued newer one actually executes

1. operator opens an escalation-packet family for recipient target `support-vendor / ticket mailbox A`
2. product shows four adjacent truths:
   - current shareable head `pkt_01K8...`
   - queued issue item `qi_01K9... -> pkt_01K8... -> mailbox A -> queued`
   - current issued head for mailbox A `pkt_01K7...`
   - current issued surface snapshot `iss_01K7...`
3. product explains that the newer packet is already the current head for new reuse, but it is **not yet** the current outward surface for the vendor because the queued issue item has not executed
4. operator may still open carryforward and refresh-note surfaces comparing `pkt_01K7...` with `pkt_01K8...`
5. when the queue later records execution, the disclosure register updates:
   - `last issue execution -> iex_01K9...`
   - `current issued head -> pkt_01K8...`
   - `current issued surface snapshot -> iss_01K8...`
6. if no vendor acknowledgment has arrived yet, delivery witness remains separate and may still read `none beyond issue execution`
7. operator can now answer both `what artifact is current to send next?` and `what artifact is currently in force outwardly for this vendor?` without manual lineage archaeology



## Flow 168 — withdraw and replace an already-issued vendor packet without pretending recall

Problem: an older escalation packet was already issued outwardly by email to a vendor mailbox. A newer corrected packet now exists, but the operator needs the product to say what is current for future reuse, what correction notice now controls interpretation of the older packet, and why stale-copy risk still remains.

```text
$ anonsync artifact correction show --family pkt_vendor_01KA... --target mailbox:vendor-a
Outward correction register: corrreg_01KA...

Current outward state
  current issued head ........ pkt_01K9_old
  current shareable head ..... pkt_01KA_new
  active correction notice ... none
  correction mode ............ pending-correction
  residual reliance .......... email-non-recallable
  claim ceiling .............. internal-decision-only

Why this is not auto-fixed
  - newer packet exists locally
  - newer packet has not been issued yet
  - no correction notice has been sent
  - no recipient acknowledgment exists

Next honest actions
  [1] Prepare replacement notice
  [2] Issue newer packet
  [3] Leave older packet historical only
```

```text
$ anonsync artifact correction prepare-notice --family pkt_vendor_01KA... --corrects pkt_01K9_old --replacement pkt_01KA_new --target mailbox:vendor-a
Prepared correction notice: corrn_01KA...

Correction mode
  supersede-with-replacement

Recipient-safe text
  "Use the attached replacement packet instead of the earlier packet sent on Mar 20. The earlier packet should no longer be relied on."

Recall limits
  - email copies already delivered cannot be recalled by this action
  - recipient acknowledgment would strengthen the claim ceiling later
```

```text
$ anonsync artifact correction issue-notice corrn_01KA...
Correction transition receipt: corrt_01KA...

Issued
  correction notice .......... corrn_01KA...
  replacement artifact ....... pkt_01KA_new
  correction mode ............ supersede-with-replacement
  residual reliance .......... older-copy-may-still-circulate
  claim ceiling .............. replacement-issued
```

```text
$ anonsync artifact correction import-ack pkt_vendor_01KA... --source vendor_reply.eml
Correction transition receipt: corrt_01KB...

Upgraded proof
  recipient acknowledgment ... imported
  residual reliance .......... recipient-confirmed-old-copy-ignored
  claim ceiling .............. recipient-ack
```

Why this matters:

1. The newer packet becoming current for future reuse does not silently erase the older issued packet's historical role.
2. The correction notice becomes its own outward artifact with its own receipts.
3. Residual stale-copy posture stays visible until stronger proof arrives.
4. `we sent a replacement` does not have to impersonate `the recipient definitely understood the correction`.



## Flow 169 — same-thread vendor reply does not yet prove exact replacement acknowledgment

Problem: a vendor replies `got it` in the same email thread after an older packet was corrected and a replacement packet was issued. The reply is useful evidence, but the product should still say whether that acknowledgment binds only to the family/thread or to one exact correction/replacement object.

```text
$ anonsync ack show --family pkt_vendor_01KA... --target mailbox:vendor-a
Recipient acknowledgment binding: ackbind_01KB...

Imported acknowledgment
  source ..................... msg_01KB_reply
  sender match ............... exact-target
  conversation continuity .... same-thread
  acknowledged object ........ ambiguous
  binding evidence ........... generic-reply
  binding exactness .......... family-only
  claim ceiling .............. recipient-ack-family-only

What the product may say
  - the vendor replied in the expected thread
  - the reply is useful acknowledgment evidence
  - the product cannot yet prove whether the vendor acknowledged:
      * the older packet
      * the correction notice
      * the replacement packet

Stronger proof needed
  - quoted correction notice text
  - explicit replacement packet id/digest
  - same-product successor redemption
```

```text
$ anonsync ack classify --family pkt_vendor_01KA... --target mailbox:vendor-a --ack msg_01KB_reply --bind replacement-artifact:pkt_01KA_new
Refused: stronger proof required
Reason:
  generic same-thread reply is not exact object binding
```

```text
$ anonsync ack import --family pkt_vendor_01KA... --target mailbox:vendor-a --from redeem_01KC_successor
Imported acknowledgment: acksrc_01KC...
Updated binding:
  acknowledged object ........ replacement-artifact
  binding evidence ........... same-product-successor-observed
  binding exactness .......... same-product-exact
  claim ceiling .............. same-product-successor-exact
```

The operator can now distinguish:

- `we got a reply in the right lane`
- `we got a stronger exact successor proof`
- `the correction register may now strengthen exactness honestly`

without letting a generic thread reply impersonate exact replacement acknowledgment.


## Flow 78 — classify one human reply inside a broader target lane without pretending the whole target acknowledged

Goal:

- import a useful same-thread or same-ticket reply
- preserve exact object acknowledgment if it exists
- keep actor scope, delegation scope, and audience ceiling honest instead of flattening them into one `acknowledged` chip

Suggested flow:

```text
anonsync ack show --family vendor-packet --target support@vendor.example
anonsync ack import --family vendor-packet --target support@vendor.example --from ./reply.eml
anonsync ack scope show --family vendor-packet --target support@vendor.example
anonsync ack scope classify --family vendor-packet --target support@vendor.example --relation member-of-target-audience
anonsync ack receipt show acr_01J...
```

Expected semantics:

- the imported reply may classify the acknowledged object as exact if the correction notice or replacement artifact is quoted precisely
- the same reply may still remain only `actor responded` or `one audience member responded`
- the surface preserves raw actor, visible sender lane, target relation, delegation evidence, object binding, and audience ceiling as separate answers
- later stronger proof may upgrade target-lane or audience-wide scope without rewriting the original weaker import

Expected operator answers from the interface alone:

- who exactly replied
- whether the reply came from the target lane itself or only from one actor inside a broader lane
- what exact object that reply acknowledged, if any
- whether the current truth is actor-only, lane-level, one-member-of-audience, or genuinely wider
- what stronger proof would justify promoting the audience ceiling



## Flow 170 — automatic mailbox or ticket reply stays useful without impersonating human acknowledgment

Problem: an escalation packet is issued to `support@vendor.example` and AnonSync later imports two reply-shaped artifacts: first an automatic out-of-office response, then a ticket-system auto-create notice. Both artifacts are useful, but the product should still say that the lane reacted automatically rather than pretending a human reviewed the packet.

```text
$ anonsync ack show --family vendor-packet --target support@vendor.example
Acknowledgment summary
  object exactness ........... family-only
  target scope ............... target-lane-probable
  authorship ceiling ......... unknown
```

```text
$ anonsync ack authorship import --family vendor-packet --target support@vendor.example --from ./vacation-reply.eml
Imported authorship row: ackauth_01KD...

Reply authorship
  visible lane ............... support@vendor.example
  authorship class ........... automation-authored
  automation kind ............ vacation-reply
  human material ............. machine-template-only
  human proof strength ....... none
  authorship ceiling ......... machine-lane-reaction-only

What the product may say
  - the target lane emitted an automatic reply
  - the reply is useful operational evidence
  - no human acknowledgment is proved yet
```

```text
$ anonsync ack authorship import --family vendor-packet --target support@vendor.example --from ./ticket-auto-create.eml
Imported authorship row: ackauth_01KE...

Reply authorship
  visible lane ............... vendor ticket system
  authorship class ........... automation-authored
  automation kind ............ ticket-auto-create
  human material ............. machine-template-only
  human proof strength ....... none
  authorship ceiling ......... ticket-opened-or-routed

What the product may say
  - the request appears to have entered the vendor support lane
  - a case id was created
  - no human-reviewed response is proved yet
```

```text
$ anonsync ack authorship classify --ack msg_01KE_ticket --ceiling human-response-probable
Refused: stronger proof required
Reason:
  ticket auto-create notice is machine-authored and does not prove human review
```

```text
$ anonsync ack import --family vendor-packet --target support@vendor.example --from ./agent-reply.eml
$ anonsync ack authorship show --family vendor-packet --target support@vendor.example
Reply authorship
  latest stronger row ........ ackauth_01KF...
  authorship class ........... human-authored
  human proof strength ....... structural-human-proof
  authorship ceiling ......... human-response-probable
```

The operator can now distinguish:

- `the mailbox reacted automatically`
- `the ticket system opened or routed the request`
- `a human later appears to have replied`

without letting the first two truths impersonate the third.


## Flow 171 — human vendor reply requests a changed packet without pretending acceptance

Problem: an escalation packet was issued to `support@vendor.example`. A named human agent replies in the same lane and references the exact packet, but asks for one fuller route snapshot and a less-redacted attachment before the vendor will continue. The product should preserve that this was a real human reply while still saying the current request is not yet accepted.

```text
$ anonsync ack show --family vendor-packet --target support@vendor.example
Acknowledgment summary
  object exactness ........... object-exact
  target scope ............... target-lane-probable
  authorship ceiling ......... human-response-probable
  reply stance ............... unknown
```

```text
$ anonsync ack stance import --family vendor-packet --target support@vendor.example --from ./agent-reply.eml
Imported reply-stance row: ackst_01KG...

Reply stance
  visible lane ............... support@vendor.example
  reply stance ............... requests-artifact-change
  blocking effect ............ follow-up-required
  follow-up class ............ issue-corrected-artifact
  accepted scope ceiling ..... understanding-only
  stronger reply needed ...... corrected-artifact-response

What the product may say
  - a human replied in the target lane
  - the current packet was reviewed enough to request a more complete resend
  - the current request is not yet accepted as-is
```

```text
$ anonsync ack stance classify --ack msg_01KG_agent --stance accepted-current-request
Refused: stronger proof required
Reason:
  imported reply requested one changed packet and therefore cannot count as acceptance of the current packet
```

```text
$ anonsync artifact refresh compare --family vendor-packet --target support@vendor.example
Carryforward verdict
  prior issued head .......... pkt_01KF...
  current shareable head ..... pkt_01KH...
  delta ledger ............... route snapshot widened; redaction narrowed for one attachment
  refresh note ............... blocked
  stronger follow-up ......... issue corrected packet
```

```text
$ anonsync ack stance show --family vendor-packet --target support@vendor.example
Reply stance
  current strongest row ...... ackst_01KG...
  reply stance ............... requests-artifact-change
  blocking effect ............ follow-up-required
  smallest next move ......... issue corrected packet
```

The operator can now distinguish:

- `a human really replied`
- `the reply bound to the right packet`
- `the reply still requested changes before acceptance`
- `the smallest honest next move is corrected reissue, not closure or success`

without letting human response proof impersonate acceptance of the current outward artifact.


## Flow 172 — exact human reply approves one quoted excerpt but leaves packet remainder open

Problem: a corrected vendor packet was reissued with three meaningful changes: a narrowed redaction in the timeline section, a widened route snapshot attachment, and a clarified startup-owner note. A named human agent replies in the same ticket lane and explicitly quotes only the timeline paragraph, saying that section now looks correct. The product should preserve that this is exact, human, and useful while still refusing to claim whole-packet acceptance.

```text
$ anonsync ack show --family vendor-packet --target support@vendor.example
Acknowledgment summary
  object exactness ........... object-exact
  target scope ............... target-lane-probable
  authorship ceiling ......... human-response-probable
  reply stance ............... acknowledges-understanding
  referent coverage .......... unknown
```

```text
$ anonsync ack referent import --family vendor-packet --target support@vendor.example --from ./agent-quote-reply.eml
Imported reply referent row: ackrf_01KH...

Reply referent coverage
  visible lane ............... support@vendor.example
  referent scope ............. quoted-excerpt-only
  request coverage ceiling ... one-slice-only
  remainder posture .......... remainder-unmentioned
  stronger proof needed ...... whole-packet-or-all-items reply

What the product may say
  - a human replied in the target lane
  - the quoted timeline paragraph appears accepted
  - the widened route snapshot and startup-owner note remain open
```

```text
$ anonsync ack referent classify --ack msg_01KH_agent --coverage whole-artifact
Refused: stronger proof required
Reason:
  imported reply quoted only one timeline excerpt and did not speak about the route attachment or startup-owner note
```

```text
$ anonsync ack stance show --family vendor-packet --target support@vendor.example
Reply stance
  current strongest row ...... ackst_01KH...
  reply stance ............... acknowledges-understanding
  blocking effect ............ follow-up-required
  smallest next move ......... issue narrowed follow-up or request whole-packet confirmation
```

```text
$ anonsync artifact refresh compare --family vendor-packet --target support@vendor.example
Carryforward verdict
  current issued head ........ pkt_01KH...
  approved slices ............ timeline paragraph only
  open remainder ............. route attachment; startup-owner note
  stronger follow-up ......... subset-safe note or explicit whole-packet confirmation
```

The operator can now distinguish:

- `the reply bound to the right packet`
- `a human really replied in the target lane`
- `the human only approved one quoted slice`
- `the rest of the packet still needs explicit answer`

without letting exact quoted feedback impersonate whole-packet acceptance.


## Flow 173 — later slice-only approval does not clear an older whole-packet blocker

Problem: a vendor lane already contains one exact human reply that requested a widened route attachment before the current packet could be accepted. After the operator reissues a corrected packet, the same named human later replies only about the timeline paragraph, quoting that slice and saying it now looks good. The product should preserve that the newer reply is real and useful while still refusing to claim that the whole-packet blocker is gone.

```text
$ anonsync ack series show --family vendor-packet --target support@vendor.example
Reply series register
  latest arrival ............. msg_01KJ_quote
  current whole head ......... ackst_01KJ_block
  current subset heads ....... timeline-paragraph:ackst_01KJ_quote
  superseded replies ......... none
  contradiction warning ...... later-narrow-reply-does-not-clear-older-block
  stronger resolution needed . explicit whole-packet reply
```

```text
$ anonsync ack show --family vendor-packet --target support@vendor.example
Acknowledgment companions
  object exactness ........... object-exact
  target scope ............... target-lane-probable
  authorship ceiling ......... human-response-probable
  reply stance ............... acknowledges-understanding
  referent coverage .......... one-slice-only
```

```text
$ anonsync ack series classify-head --family vendor-packet --target support@vendor.example --reply msg_01KJ_quote
Refused: no unique whole-artifact head
Reason:
  latest imported reply only approved the quoted timeline paragraph
  older whole-packet request-changes head still governs unresolved route attachment acceptance
```

```text
$ anonsync ack series show --family vendor-packet --target support@vendor.example --verbose
Reply series register
  represented actor .......... agent@vendor.example
  latest arrival ............. msg_01KJ_quote
  current whole head ......... ackst_01KJ_block
    stance ................... request-changes
    coverage ................. whole-artifact with named blocker
  current subset head ........ ackst_01KJ_quote
    stance ................... acknowledges-understanding
    coverage ................. timeline paragraph only
  open remainder ............. route attachment
  next honest action ......... request explicit whole-packet answer or submit corrected route attachment
```

The operator can now distinguish:

- `the newest imported reply is useful`
- `the newest imported reply only approved one slice`
- `an older whole-packet blocker is still the operative head`
- `the lane therefore has progress without closure`

without forcing current reply truth to be reconstructed from raw thread order.
