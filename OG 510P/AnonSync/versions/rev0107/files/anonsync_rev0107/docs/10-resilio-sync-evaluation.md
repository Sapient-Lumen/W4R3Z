# Resilio Sync evaluation (deeper pass, revised yet again)

## Bottom line

Resilio Sync is still a serious reference point.
Its official help center shows Sync v3 releases through `3.1.2.1076` on `31/Oct/2025`, and Resilio's v3 rollout documents also say that Sync v3 functionality is fully available for non-commercial use behind v3 licensing/activation.
So any AnonSync case that depends on “Resilio is abandoned”, “its good features are still gated away from most users”, or “it has no control surface” is weak.

The better question is this:

> Which Resilio ideas are strong enough to preserve, and which exact semantics are the strongest reasons not to clone it?

This revision answers that more operationally.


## Fair preserve / adapt / reject matrix

### Preserve almost as-is

- selective materialization as a first-class product idea
- encrypted-untrusted replicas as an important topology, not a niche afterthought
- device identity and fingerprint legibility
- the basic idea that a personal-device mesh can be made very convenient

### Adapt heavily

- linking, because Resilio's own docs still say linked devices automatically make all folders visible everywhere and allow broader future approval reach than AnonSync should want
- standing approval memory, because current docs still let prior trust, future sharing, and later arrival handling sit too close together
- approval-reuse policy, because current docs still keep `approved before` auto-connect and share-dialog `all peers still need approval` as separate facts instead of one precedence contract
- default location and path adoption, because current custom-location flows still require `Disconnected` workarounds on linked devices and still let duplicate-name fallback land as indexed sibling folders
- per-device read-only behavior, because linked-device convenience still pushes operators toward manual key/disconnect rituals when they want narrower rights
- file availability, because placeholders, `Clear`, and ghost-file warnings still tell the truth in pieces instead of through one action contract

### Reject outright

- identity takeover semantics when linking already-initialized devices
- ambient share visibility as the default blast radius of personal convenience
- any UI contract that lets `visible here` masquerade as `durably fetchable later`
- any action surface that preserves the same `Fetch` or `Remove from device` verb across unlike risk classes


## Latest evidence from this pass

This pass slightly strengthens the case for taking Resilio seriously and slightly sharpens the case for not cloning it.

What got stronger on Resilio's side:

- the official changelog still shows a live v3 line through `3.1.2.1076`, with `3.1.0` in July 2025 adding file-download priority and fixing the previously non-clickable `can't download file` status
- linked-device and selective-sync docs still describe a genuinely useful convenience mesh with automatic folder visibility and placeholders that support fetch-on-demand
- linked-device path-placement docs still provide real convenience via default roots and later `Connect`, which means the product is solving a real problem rather than an imaginary one
- mobile docs still expose a real local-space control through `Clear synced files` / storage clearing rather than forcing a full disconnect

What still argues against cloning the surface:

- linked devices still default toward ambient visibility of all folders across the constellation
- custom location for linked folders still depends on putting the target device into `Disconnected` and reconnecting share by share
- linked-device read-only still routes through a Standard-folder/manual-key/manual-location ritual instead of being a first-class per-member outcome
- ghost-file and no-source-peer guidance still confirms that a visible name can outlive any current byte witness
- current approval docs still say later pending folders can auto-connect after prior approval and that approval can be remembered by identity across future sharing, which is convenient but keeps remembered trust and later arrival handling too entangled
- current approval-time detail is still not the same thing as one later authorization trace for which exact remembered-trust node actually caused the current lower-friction arrival
- current share-dialog security still says `Only new peers` may reuse old approval while `All peers` still forces a new approval when connecting to another shared folder, which means approval reuse policy is real but still split away from later-arrival explanation
- current linked-device docs also still make certificate takeover, hidden-device return, and non-remote unlinking real parts of the identity model, which means old remembered approval can outlive a changed constellation without one first-class family-rebase surface
- current share-dialog docs still treat expiry period and use-count as offer-artifact controls while other current docs still say approval is retained with identity and approval mints certificate-backed access, which means artifact lifetime and durable trust promotion still have to be reconstructed from several places instead of one boundary contract

The resulting AnonSync decision is narrower and stronger than before:

> do borrow Resilio's materialization mechanics and convenience ambition, but do not clone a surface where action truth, invitation lifetime, and trust provenance still depend on mode, memory, menu, or troubleshooting-page reconstruction.

---

## What Resilio still does unusually well

### 1) It remains maintained enough to matter

Resilio still publishes official Sync v3 release notes, with 3.0.x across 2024-2025 and 3.1.x through late 2025.
That means AnonSync is reacting to a living product, not a dead one.

Implication:

- differentiation must be principled, not dismissive

### 2) The bar is not just “old Free vs old Pro” anymore

Resilio's Sync v3 help pages say the product is available free of charge for non-commercial use and that functionality is fully available for non-commercial use.
That matters because the real competitive bar is a modern convenience-rich product, not a historically more limited free tier.

Implication:

- AnonSync cannot justify itself by assuming formerly premium convenience remains out of reach for ordinary personal users

### 3) Its materialization model is still excellent product design

Resilio's device-facing sync states — `Disconnected`, `Selective Sync`, and `Synced` — answer a very human question directly:

> “How much of this share exists here right now?”

That is more than a UI flourish.
It is a compact user mental model for space, availability, and intent.

AnonSync should keep this idea, though with clearer names and machine-readable state.

### 4) Selective Sync remains one of the best ideas in this category

Selective Sync keeps the directory visible while materializing only requested content and leaving the rest as placeholders.
That is strong because it decouples:

- visibility of a dataset
- membership in a share
- physical materialization of content

This is worth borrowing almost verbatim at the product level, even if AnonSync chooses different placeholder mechanics at first.

### 5) Encrypted folders encode a real and valuable topology

Resilio's encrypted-folder flow supports a practical deployment pattern:

- trusted device stores plaintext
- untrusted device stores ciphertext only
- later trusted device can recover through the encrypted intermediary

That is a real feature, not marketing garnish.
It is one of the strongest reasons AnonSync should include encrypted-untrusted replicas early.

### 6) Advanced folders introduced meaningful PKI-based permissions

Official docs say Standard folders use randomly generated keys while Advanced folders use digital certificates and support features such as on-the-fly permission changes, revoke, owner semantics, and better peer identity treatment.
That is a substantive architectural improvement, not merely a licensing distinction.

This is one of the places where Resilio got the product direction right.

### 7) Linking genuinely reduces user friction

Resilio's linking flow is powerful for personal-device meshes.
Official docs emphasize that linked devices automatically gain visibility of all Sync folders, that approvals can be broadened across linked devices, and that sync mode can be chosen per linked device.
That convenience is real.
We should not understate it.

### 8) It is more scriptable and configurable than a lazy critique suggests

Resilio does expose configuration mode, Linux CLI behavior, Windows command-line switches, WebUI configuration, LAN-only tuning, and power-user preferences.
So the honest criticism is **not** “Resilio cannot be automated.”

### 9) Its invitation controls are useful, but their afterlife is still too implicit

Current share-dialog docs still expose genuinely useful controls: links can expire after a chosen period and can also be limited to a chosen number of uses.
At the same time, other current docs still say approval is retained with a person's identity for later sharing, and link-flow docs still describe approval as minting certificate-backed access.

The important point is not that Resilio is wrong to have both of those facts.
The point is that operators still lack one first-class answer to a sharper question:

> did this one-time or expiring invitation merely admit this one subject, or did it also create durable remembered approval for later unrelated subjects?

AnonSync should keep expiring/use-limited invitation controls.
It should not clone a surface where the operator has to infer durable trust promotion from separate link, approval, and later auto-connect docs.
The honest criticism is narrower:

- the control surface is partial
- important concepts are distributed unevenly across UI, config, startup flags, and support articles
- the most capable trust semantics are not consistently available from every surface

### 9) Its convenience model still leans on default locations and mode side effects

Resilio's own help docs say that when linked devices are in `Selective Sync` or `Synced` mode, new folders are automatically put into the default folder location. If you want a custom location for a newly visible linked folder, the documented workaround is to switch that device into `Disconnected` mode and then manually click `Connect` for each desired folder. If a same-named folder already exists, Sync can create another copy with an added index.

That is a very revealing product signal.
Resilio *does* offer a fix, but the fix depends on knowing that four separate concepts are coupled together:

- share visibility from linked devices
- local acceptance of that visibility
- default synchronization mode
- default path placement

AnonSync should break those apart.
Visibility should not imply path creation, and path choice should not require a device-global mode change just to handle one share safely.

### 9a) Arrival visibility and local claim still collapse into path creation ritual

Resilio's current docs make this seam especially visible now. `Sync Private Identity & Linking My Devices` says that once devices are linked, every new folder added on one device becomes automatically available on the others and that all linked folders are visible and accessible across the linked set. `Synchronization Modes` and `Folder Types and Management` then say disconnected folders are still shown as future-action objects with no local path, while `Disconnecting and Removing Folders` says removing such a folder removes it from all linked devices. `Folders are duplicating with an index (i) in their name` adds that if a linked arrival lands in the default location and a same-name path already exists, Sync will create a duplicate-index directory. And the custom-location article still routes careful placement through `Disconnected` first, then `Connect`.

That combination is convenient, but it means four operator-different questions still live too close together:

- did this share merely become visible here
- has this machine accepted it yet
- has a local path actually been chosen and bound
- is the operator acting only for this machine or retracting visibility for sibling linked devices too

AnonSync should not inherit that collapse.
It should keep announcement, claim, bind, and wider withdraw as separate public acts.


### 9b) Remembered approval and later arrival handling still sit too close together

Resilio's current docs now make this seam very explicit. `Folder Types and Management` says pending folders can automatically connect if that user has approved you before. `Sync functionality in detail` says the product retains approval with a person's identity so the next shared folder may not need approval again. And `Sync Private Identity & Linking My Devices` says a remote user can choose to automatically approve all your linked devices for future sharing after approving one.

That is real convenience.
It is not yet one truthful contract for what happened when a new arrival later appears on this machine.
A later arrival that matched prior approval is not automatically the same as:

- a fresh local claim decision
- a reviewed path bind on this machine
- a decision to materialize bytes now
- a decision to widen future approval again

AnonSync should therefore split those facts apart.
Remembered approval may explain why an arrival skips identity re-vetting or lands in a lower-friction queue, but it should not silently masquerade as `safe to connect here now`.


### 9c) Later-arrival causality still requires reconstruction

This is the explanation seam this revision cares about most.
Resilio's current docs still make the operator reconstruct later-arrival causality from several places at once. `Sync Private Identity & Linking My Devices` says linked devices automatically make all folders available and that a remote user can choose to auto-approve all linked devices for future sharing after approving one. `Folder Types and Management` says pending folders can automatically connect if that user approved you before. `Sync functionality in detail` says retained approval means the next shared folder with that person may not need approval. And the linked-device placement docs still route careful custom location through `Disconnected` and later `Connect`, with default-folder behavior and duplicate-index fallback living elsewhere.

That is good convenience.
But it still means the operator question `why is this here in this state on this machine?` is not answered by one first-class explanation surface.
The operator still has to reconstruct whether a subject is here because of:

- ambient linked-device announcement
- remembered approval
- standing seat template / default root
- local claim
- later placement review
- or some combination of the above

AnonSync should do better.
The product should preserve the convenience mechanics while insisting on one causal explanation surface that says, in order, what stage is true now, what standing memory influenced it, what did not happen yet, and what narrower governing fact would have changed.


### 9e) Trust provenance still requires later authorization archaeology

This is the trust-trace seam this revision cares about most.
Resilio's current docs still give pieces of the story without turning them into one later proof surface. `Comprehensive guide to syncing (Desktop-Desktop)` says approval review shows name, IP address, fingerprint, and approval request receipt date at approval time. `Sync functionality in detail` says approval can be retained with a person's identity and approvals can be issued from any linked device. `Sync Private Identity & Linking My Devices` says a remote user can choose to auto-approve all linked devices for future sharing after approving one. `Folder Types and Management` says later pending folders can automatically connect if that user approved you before.

That is useful provenance material.
It is not yet one first-class answer to the operator question `which exact approval act are we reusing right now?`
The operator still has to reconstruct whether a later convenience came from:

- the original approval on one seat
- a broader linked-device horizon chosen at that time
- a later touch-like reaffirmation in practice
- or a trust memory that would no longer authorize the same subject under today's reality

AnonSync should do better.
The product should keep origin approval, later trust mutations, and subject-specific authorization trace as explicit public objects, so a later arrival can point to one exact remembered-trust node instead of merely inheriting a vague `approved before` story.

### 9d) Standing-policy retroactivity still lacks one explicit impact preview

This is the mutation seam this revision cares about most.
Resilio's current docs still make the retroactivity boundary reconstructive instead of first-class. `Selective Sync` says the selected linked-device mode applies to newly added folders and that current ones remain as they are. `Sync Private Identity & Linking My Devices` and `Folder Types and Management` still describe remembered approval and later pending-folder auto-connect. The custom-location, duplicate-index, and Android `Simple Mode` docs still describe standing placement defaults that shape where later arrivals land.

That is useful convenience.
But it still means the operator question `what exactly will this settings change alter?` is not answered by one first-class preview.
The operator still has to reconstruct whether a standing edit changes:

- future unseen arrivals only
- already announced but unclaimed drafts
- currently claimed but unbound subjects
- already bound shares
- current local bytes
- remembered approval scope

AnonSync should do better.
The product should preserve the convenience mechanics while insisting on one policy-delta preview that says, in order, which subject classes move, which named examples illustrate that move, what definitely stays untouched, and what receipt later proves the reviewed retroactivity boundary.


### 9f) Descendant liveness still requires present-tense reconstruction

This is the descendant-liveness seam this revision cares about most.
Resilio's current docs still make the operator reconstruct present-tense descendant reality from several surfaces at once. `Synchronization Modes` says selective-sync fetch requires that at least one peer that has the files is online. `My files don't sync` says the peers list distinguishes online peers from peers ever connected, with disconnected peers shown separately. `How to clear offline devices? (desktop only)` says hidden offline devices are only hidden and can later reappear. `Disconnecting and Removing Folders` says disconnected folders remain future-action objects and can later be reconnected. `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time.` adds the explicit ghost-file case where a visible name outlives any current source bytes.

That is honest peer-to-peer reality.
But it still means the operator question `which descendant is actually alive enough to justify convenience now?` is not answered by one first-class surface.
The operator still has to reconstruct whether a descendant is:

- merely part of the remembered-trust family
- recently witnessed alive
- only hidden/offline historical lineage
- reappeared but not yet proven as a byte source or approval seat
- or effectively explanation-only despite still being visible in family history

AnonSync should do better.
The product should preserve the convenience mechanics while insisting on one descendant-liveness surface that says, in order, family posture, liveness class, confidence class, current honest role, what definitely is *not* being claimed, and which receipts prove that posture.

### 9g) Descendant action eligibility still requires role archaeology

This is the role-eligibility seam this revision cares about most.
Resilio's current docs still make the operator reconstruct present-tense descendant capability from several surfaces at once. `Sync Private Identity & Linking My Devices` says you can approve a request from any linked device where the folder is in `Selective Sync` or `Synced` mode. `User Management` says all devices linked to one identity act as Owners. `Folder Types and Management` says a later pending folder can auto-connect if that user approved you before and one of their devices is online. `Synchronization Modes` says fetch still requires at least one online peer that actually has the files.

That is useful convenience.
But it still means the operator question `which descendant may honestly act for this subject right now?` is not answered by one first-class surface.
The operator still has to reconstruct whether a currently live descendant is:

- merely a remembered family member with no current subject capability
- live enough to count as a byte source for this subject
- live enough to count as an approval-capable seat for this subject
- eligible for one role but blocked for the other
- or explanation-only even though linked ownership or old approval memory still exists

AnonSync should do better.
The product should preserve the convenience mechanics while insisting on one descendant-capability surface that says, in order, which subject is in question, which role is being evaluated, whether that role is actually eligible now, what proof or blocker produced that answer, what definitely is *not* being claimed, and which receipts prove the outcome.


### 9h) Approval-reuse precedence still requires policy archaeology

This is the reuse-precedence seam this revision cares about most.
Resilio's current docs still make the operator reconstruct subject-level approval reuse from several surfaces at once. `Folder Types and Management` says a later pending folder can automatically connect if that user approved you before. `Sync functionality in detail` says approval can be retained with a person's identity so the next shared folder may not need approval again. `Sync Private Identity & Linking My Devices` says a remote user can choose to automatically approve all your linked devices for future sharing after approving one. But `Sync Share Dialog (Desktop)` also says the share dialog can be set so `Only new peers` reuse old approval while `All peers` still require a new approval when connecting to another shared folder.

That is real convenience and real caution.
But it still means the operator question `does this exact subject actually permit reuse of that old approval here?` is not answered by one first-class surface.
The operator still has to reconstruct whether lower-friction approval is happening because of:

- standing remembered approval that is still fresh enough to matter
- linked-device broadening of who counts as approved
- a share/offer policy that allows reuse for known peers
- or a stricter share/offer policy that still requires fresh approval for everyone

AnonSync should do better.
The product should preserve the convenience mechanics while insisting on one approval-reuse precedence surface that says, in order, what standing match exists, what this subject's reuse policy is, which rule wins, what definitely is *not* being claimed, and which receipt later proves that precedence outcome.

### 9e) Remembered approval still behaves too much like timeless trust

This is the trust-lifecycle seam this revision cares about most.
Resilio's current docs still make remembered approval feel more durable than inspectable. `Sync functionality in detail` says that by default you only need to approve a person once because the product retains approval with that person's identity. `Sync Private Identity & Linking My Devices` says a remote user can choose to automatically approve all your linked devices for future sharing after approving one. `Folder Types and Management` says pending folders can automatically connect if that user approved you before. `User Management` adds that all devices linked to one identity act as Owners. `What's the difference between Standard and Advanced folders?` explains that Advanced folders store certificates of previously dealt-with users so the product can treat `old` and `new` peers differently.

That is real convenience.
But it still means the operator question `is this remembered trust still fresh enough to reuse now?` is not answered by one first-class surface.
The operator still has to reconstruct whether prior approval should keep acting like live convenience memory after:

- long dormancy
- linked-device growth
- role/scope widening
- identity rotation or re-linking
- repeated ignored later arrivals

AnonSync should do better.
The product should preserve the convenience mechanics while insisting on one remembered-trust freshness surface that says, in order, what scope was granted, when it was last reviewed and last used, what is cooling it now, what it may still authorize, and which reviewed outcome keeps, narrows, freezes, or revokes that memory.


### 10) Its selective-sync delete semantics are useful, but easy to conflate

Resilio's docs say Selective Sync uses placeholders, that previously synced files can revert to placeholders when deleted, and that the UI distinguishes `Remove from this device` from `Remove from all devices`. Its power-user preferences even include toggles like disabling `Remove from all devices` for selective-sync shares.

This is not evidence that the product is poorly designed. It is evidence that materialization control and distributed deletion are close enough to confuse users unless the surface is very explicit.

AnonSync should therefore avoid ambiguous deletion semantics in its own control surface.
Operators should see separate verbs for:

- fetching content
- evicting local content
- removing local materialization only
- deleting from the replicated share

### 10a) Its read-only remediation still depends too much on mode and checkbox memory

Resilio's docs say a read-only peer that adds, deletes, or modifies files can stop synchronization for that file unless `Overwrite any changed files` is enabled. Those same docs say the option can restore deleted files and revert modified ones, but added files remain local and unsynced. Folder-preferences docs then add another caveat: the option is disabled for read-only folders with Selective Sync on.

That is a real product seam.
The product does offer remediation, but the operator still has to reconstruct behavior from several moving parts:

- permission class
- mount/materialization mode
- whether a destructive auto-remediation option is enabled
- whether the local evidence should be preserved, reverted, or just left blocking progress

AnonSync should instead surface local drift on non-authoritative mounts as first-class deviation cases with explicit remediation state and reviewable resolution actions.

### 11) Ownership across linked devices is broader than we should want

Resilio's docs explicitly say that when data is shared across your own devices linked to one identity, all of those devices act as Owners.
That is convenient for personal use, but it also collapses what AnonSync should keep distinct:

- being in the same personal constellation
- being allowed to write
- being allowed to re-share
- being allowed to revoke others

AnonSync should not inherit that collapse by default.

### 12) Its restore story still leaks implementation details into the user contract

Resilio's Archive feature is genuinely useful: when a peer updates or deletes a file, other peers can keep the old or deleted copy in `.sync/Archive`, and the default retention is 30 days on desktops and 1 day on mobiles. But the restore flow is still manual: you browse a hidden directory or a desktop UI action, move or copy files back yourself, and the docs warn that Sync should already be running or the restored file may be re-archived on the next rescan as older than the current version.

That is not a fatal flaw. It is a strong signal that restore is still partly modeled as a filesystem ritual instead of a supported control-surface operation.

AnonSync should do better here:

- file history should be queryable
- restore targets and scope should be explicit
- restore should not require knowing hidden on-disk conventions
- restore should emit the same audit/events model as other high-signal mutations

### 13) Important operator state still leaks through hidden service files

Resilio's docs say each synced folder receives a hidden `.sync` folder, that this folder is critical for syncing, and that deleting or moving it causes a `Service files missing` error. The same docs also place `IgnoreList` and `Archive` inside that hidden service directory. Ignore rules are case-sensitive and Resilio explicitly says it is advisable — but not compulsory — to keep the same `IgnoreList` on all peers to avoid confusion about share-size differences.

That is a revealing product signal.
It means important policy and recovery behavior is still partly modeled as:

- hidden files inside the share
- peer-local conventions that may drift
- support knowledge about which service artifacts are safe to touch

AnonSync should reject that as operator contract.
Implementation files may exist, but their meaning should be exposed through supported objects such as:

- ignore-rule sets
- history/versioning policy
- service-health findings
- drift status between intended and observed rule state

### 14) Conflict handling is documented, but still too file-ritual-oriented

Resilio's docs explicitly warn users not to simply delete a `.Conflict` file or folder, because doing so deletes the corresponding real file or folder on the remote peer. Its power-user preferences also document `fix_conflicting_paths`, and warn that disabling it can leave the share unsynced and produce unpredictable results.

This is useful honesty from the vendor.
It is also strong evidence that conflict handling is still too close to magic filenames and support-article lore.

AnonSync should instead model conflicts as first-class cases with:

- stable IDs
- explicit kind (`content`, `case`, `delete-vs-modify`, `path-mapping`)
- candidate versions or paths
- safe resolution actions
- audit and event records for the chosen resolution

### 14a) Rollback provenance is still fragmented across History, Archive, and filename ritual

Resilio's docs say the desktop main view has a `History` section that shows general syncing activity for the last 30 days, and separate Archive docs say Archive itself does **not** record which peer changed a file. Those same docs say restore is manual through a desktop action or the hidden `.sync/Archive` directory, and warn that Sync should already be running or an older restored file may simply be archived again on rescan. A separate FAQ adds that if an offline peer later comes online, its version can override later online edits and the overwritten versions are then placed in Archive.

That combination is revealing.
The product does preserve useful evidence and rollback material, but the operator still has to reconstruct one recovery story from several different surfaces:

- a short-lived generic History view
- a hidden Archive layout
- timestamp/online-state behavior that decides which version wins
- conflict filenames or support steps when pathname semantics collide

AnonSync should not clone that shape.
A serious control surface should instead publish one explicit rollback model with:

- durable history entries that name source peer, cause, capture time, retention horizon, and confidence
- restore candidates that state allowed scopes (`local`, `device`, `share-plan`) and overwrite risk directly
- conflict cases that name whether the issue is content concurrency, delete-vs-modify, or path/capability mapping
- rollback receipts that prove which candidate won, what lost, what scope changed, and what proof or settlement policy was attached

### 15) Linked-device least privilege and compatibility still reveal product seams

Resilio's docs say that linked devices under one identity act as Owners for data shared across your own devices, and the documented way to achieve a read-only linked-device result is to use a Standard folder with a Read Only key and manual disconnect/re-add steps.
At the same time, the v3 FAQ says v2 and v3 preserve synchronization compatibility, but linked devices under one identity should all be updated to v3 to avoid license conflicts; the linking guide separately warns that mixed-version linking can lead to lost access to Sync UI and shares configuration.

That combination is revealing.
The product offers real convenience, but two important operator questions still fall out of the main model:

- how do I keep a personal device mesh convenient **without** collapsing least privilege into owner-like authority?
- how do I preview compatibility and downgrade risks **before** linking or adopting a device into the constellation?

AnonSync should treat both as first-class interface concerns.

### 16) Approval memory and delegated approver scope are still too implicit

Resilio's own docs say that by default you only need to approve a person once, because the product retains a certificate with that identity and future folder sharing can then skip approval. The same docs say a remote user can choose to automatically approve all of your linked devices for future sharing after approving one of them, and that you can approve a new peer from any linked device where the folder is already in `Selective Sync` or `Synced` mode. Standard-folder docs separately say that a peer can share the key it has without limitations.

That is not a trivial UX detail.
It means there is a real product concept hiding behind convenience language:

- remembered approval
- delegated future approval
- approver scope across linked devices
- authority that can outlive the original one-off interaction

Resilio benefits from that convenience, but the model is still too implicit for the product AnonSync should become.
AnonSync should expose future approval as a supported object with explicit scope, expiry, approver set, and maximum role.

### 16a) Unknown-contact admission and future introductions still blur into convenience

Resilio's docs say that once devices are linked, all folders become available on all linked devices, that a remote user can choose to automatically approve all of your linked devices for future sharing after approving one device, and that you can approve new peers from any linked device where the folder is already active. The same linking guide still warns that linking already-initialized devices can cause one device to lose its certificate and take over the other device's configured shares.

That combination is revealing.
Resilio has solved a real convenience problem, but it still smears together several things AnonSync should keep distinct:

- relationship memory
- pending contact admission
- future approval scope
- own-device convenience
- successor or replacement continuity

A narrower comparison helps here. Syncthing's docs keep introducer behavior explicit rather than ambient, and its REST API exposes pending remote devices as their own records that can later be removed or ignored. That does **not** make Syncthing AnonSync's model, but it does validate the idea that “unknown peer pending queue” and “bounded automatic introductions” are real first-class seams, not UI garnish.

AnonSync should therefore expose:

- contact records separate from grants
- pending-peer records separate from links
- introduction policy separate from ordinary linking
- successor continuity separate from both ordinary linking and raw device replacement

### 16b) Device linking still needs its own blast-radius review surface

Resilio's docs say that when you link one already-configured device to another, the new device can take the identity name and fingerprint of the other device and receive all of that device's configured shares. The same linking docs say all folders become visible and accessible on all linked devices, that remote users may choose to auto-approve all linked devices for future sharing after approving one of them, and that custom placement of linked folders depends on switching the whole target device into `Disconnected` mode and then clicking `Connect` share by share. Separate docs add that Linux uses WebUI by default, and one destructive-action safety preference is explicitly ignored in Linux WebUI.

That means `link device` is not one small operation. It potentially carries:

- identity continuity or takeover consequences
- constellation membership and default-visibility consequences
- immediate incoming-share visibility delta
- future approval reach across multiple members
- per-device path-placement consequences
- surface-specific safety differences

AnonSync should therefore treat device joining as a first-class reviewed blast-radius decision. The operator should be able to tell, before apply:

- whether this is an ordinary join, a migration, or a replacement workflow instead
- which member class and defaults the candidate will receive
- how many shares become visible immediately and in what posture
- whether any approval, re-share, revoke, or successor authority expands
- whether compatibility, release, or channel differences should block the join

### 17) Share governance is still too coarse and share-type-dependent

Resilio's docs are clear that in Advanced folders only users with `Owner` permission can invite others or revoke access, while linked devices under one identity all act as Owners for your own-device syncing. Those same docs also say Standard folders have no Owner concept and peers can re-share the key they have without limitation, and local-share docs say Owner access is not possible there and changing access can require remove-and-re-share ritual.

That combination is revealing.
The product has real authority semantics, but they are still spread across:

- one overloaded `Owner` concept in Advanced folders
- no stewardship concept at all in Standard folders
- linked-device convenience that fans authority out very broadly
- local-share edge cases where governance must be reconstructed by re-sharing

AnonSync should not copy that shape.
It should separate:

- data mutation rights
- grant / revoke authority
- delegation bounds
- succession / handoff when a steward departs

A product that wants to be inspectable should expose those as explicit supported state, not as a byproduct of whichever share type happened to be chosen.

### 18) Read-only safety is still bundled too tightly with mode and share-type quirks

Resilio's own docs say read-only peers do support one-way sync, but they also say local attempts to update a file on a read-only peer will stop synchronization for that file. The same docs position `Overwrite any changed files` as the preventative answer: rename, delete, and content edits are reverted, while added files stay local and unsynced. Folder-preferences docs add that this option is potentially destructive, disabled for read-only folders with Selective Sync on, and config-mode docs expose it again as `overwrite changes`. Encrypted-folder docs go further and say encrypted backup peers are read-only, have `Overwrite any changed files` always activated, and do not support Selective Sync.

That is a real product seam.
Resilio clearly has three different concerns in play:

- what authority a peer has (`ro`, `rw`, `owner`, encrypted-only)
- whether local changes should propagate
- what should happen **locally** after an accidental add / modify / delete on a non-authoritative target

But the public surface still bundles them too much.
Depending on how the share was created and mounted, the operator can end up with:

- file-level sync stopping until reviewed
- destructive auto-revert behavior
- preserved but unsynced added files
- selective-sync caveats that remove the overwrite option entirely
- encrypted-replica behavior where overwrite is forced on and selective sync is unavailable

Syncthing's documented send-only / receive-only folder types are useful as a contrast, because they separate propagation posture from local-remediation actions like `Override Changes` and `Revert Local Changes` more explicitly.
AnonSync should go one step further and make local deviation policy a first-class supported object.

---

## Where we should *not* clone Resilio

### 1) Linking expands trust more broadly than AnonSync should allow

This is the most important divergence.
Resilio's docs say that once devices are linked, all folders become visible and accessible on all linked devices, and future approvals can be broadened across linked devices.
That is convenient, but it ties together:

- identity linkage
- access-surface expansion
- approval policy
- default replication posture

AnonSync should separate those concerns.
Linking should create a relationship, not an authority explosion.

### 2) Linking can also replace identities in ways we should explicitly reject

Resilio's linking guide says that if two already-running Sync installations with different certificates are linked, one device can lose its certificate, take the other's certificate, remove Advanced folders from the app, and copy in folders from the other instance.

That is a bright red design signal for AnonSync.
Even if some users tolerate it, this is the opposite of the identity model we should want.

AnonSync should adopt the rule:

> linking never overwrites a local identity; replacement is always a separate, explicit recovery workflow.

### 3) Standard vs Advanced reveals a split product model

Resilio's docs make clear that Standard and Advanced folders have different semantics, and the configuration-mode docs explicitly say that config mode can create only Standard folders, not Advanced folders. Folder preferences are also explicitly desktop-only in the help docs.
That means the product's most capable trust/permission model is not uniformly available across control surfaces or platforms.

This is exactly the kind of split AnonSync should avoid.
If a concept matters, it must exist consistently in:

- CLI
- daemon API
- config/import format
- future UI/TUI

### 4) LAN-only behavior is supported, but not clean enough

Resilio documents how to force LAN-only operation by disabling tracker and relay, enabling LAN multicast, and in some cases clearing cached public endpoint state by temporarily setting peer-expiration to `0`, restarting, then restoring the previous value.
That is useful, but it also shows that transport policy is partly hidden behind retained state and operational workaround.

AnonSync should make discovery and transport state inspectable objects:

- what discovery policy is active
- what addresses were learned
- what cached endpoints exist
- why a given transport path was chosen
- what to clear when changing policy

### 4a) Route controls still blur together publication, dialing, and fallback

Resilio's docs give a careful operator enough information to reconstruct the network model:

- tracker use publishes share-related reachability information so peers can learn each other's IP:ports
- LAN discovery announcements carry ShareIDs plus IP:port on the local network
- predefined hosts are direct dial targets that can work with tracker, relay, and LAN search disabled
- relay use changes the data path when direct reachability fails

That is useful documentation, but it still leaves one crucial product question under-modeled:

> what exactly am I authorizing the product to publish, to whom, and via which infrastructure?

The problem is not merely that Resilio has tracker/relay/LAN/predefined-host knobs.
The problem is that those knobs still mostly speak the language of **transport success**, while a privacy-respecting operator often needs the language of **topology exposure**:

- which services learn this device's public address
- which services learn that this ShareID exists here
- whether the product will announce publicly but dial privately
- whether relays are public, private, or fully forbidden
- whether route fallback can widen metadata exposure even if file contents stay encrypted

AnonSync should not collapse those questions into one discovery toggle.
Publication, dialing, and fallback should be distinct inspectable outcomes.

### 4aa) Disclosure residue still lacks one durable contract

Even with those docs in hand, the operator still has to reconstruct one more privacy-critical truth from scattered lines:

- tracker-oriented discovery reveals public/local addresses plus share-related inventory to discovery infrastructure
- LAN announcements reveal `ShareID` and `IP:port` to the local broadcast domain
- predefined hosts still reveal self to those specific targets even when ambient discovery is otherwise off
- narrowing later may stop future publication without obviously clearing already learned or cached state

That is workable support knowledge.
It is not one operator-facing disclosure contract.
Syncthing's security docs are better at naming the leakage trade-off directly, because they explicitly say global and local discovery reveal device ID and listening-port information and what disabling them costs.
AnonSync should go further still and publish one first-class audience/fact/residue model with receipts.

### 4b) Operators still reconstruct too many decisions from symptoms

Resilio's current docs are helpful, but the explanation path is still scattered.
Folder Preferences says peers are found through tracker, LAN search, predefined hosts, and optional relay fallback. The ports/protocols article explains that Sync learns tracker and relay addresses, publishes local/public addresses and share lists to the tracker, then tries direct TCP/UDP peer connections before switching to relay if necessary. The relay article says a relay-connected peer is shown by a relay icon in the peer list. The main-view and troubleshooting docs say users should click the `X of Y peers` link to inspect peer state and then work through tracker, relay, multicast, firewall, or multi-NIC troubleshooting when things are not connecting.

That is enough to operate the product carefully. It is not yet a strong operator contract. The product is still asking the user to move between:

- final symptoms in the peer list
- route knobs in preferences
- retained-state caveats in support articles
- troubleshooting lore about which candidate path probably failed

For AnonSync, the lesson is not that peer icons are bad. The lesson is that peer icons are insufficient. A serious interface should surface a decision trace for important outcomes such as:

- why a relay route won instead of a direct route
- which direct candidates were tried and why they were rejected
- which publication facts made the chosen route possible
- whether cached endpoints or stale policy state influenced the result
- why a later policy tightening did or did not change the active path

### 4c) Pause and schedule still blur temporary override versus durable intent

Resilio does support useful runtime suppression controls. The docs describe both a global pause button and per-folder pause controls, and the scheduler can apply weekly bandwidth limits or a `Paused` state for selected day/hour cells.

That is real product value. It is not yet a clean operator contract. The same docs also say that when Sync is paused, or scheduled as paused:

- zero-sized files still sync
- file deletions still sync
- new files are still rescanned and indexed
- scheduled-paused peers may still upload to non-paused peers while not downloading

This means “pause” is doing something narrower and stranger than the plain-language label suggests. It mostly suppresses byte transfer, but not all observable share activity, and not always symmetrically. The bandwidth story is also split: Sync Preferences says bandwidth limits apply only to Internet connections by default, and LAN rate limiting requires a separate `rate_limit_local_peers` power-user setting.

For AnonSync, the lesson is not “never pause.” The lesson is that a privacy-respecting operator surface should distinguish at least:

- temporary transfer quiesce
- drain / upload-only shutdown preparation
- temporary throttling
- durable discovery / routing / grant policy
- what expires automatically versus what becomes standing configuration

If the user has to remember that a maintenance window still permits delete propagation, still changes share size through rescans, and may require a different power-user knob for LAN rate limiting, the interface is still overloaded.

There is another useful lesson hiding here. Resilio's support guidance for faster sync still pushes operators toward directness-first tactics such as UPnP/port forwarding and predefined hosts when they want speed. That is evidence that speed pressure is real, not hypothetical. For AnonSync, the answer should not be “pretend nobody will want this.” The answer should be a first-class temporary direct-speed lease that keeps the exception visible and time-bounded instead of letting it silently become the default WAN posture.


### 5) Recovery is not first-class enough

Resilio explicitly says cloning a Sync instance with plain copies, drive cloners, `dd`, or Time Machine is unsupported and may cause strange behavior.
That is understandable from a support perspective, but it leaves a product gap.
Users still need:

- device replacement
- state backup
- trust graph migration
- disaster recovery

AnonSync should not normalize “do a clean install and re-share everything” as the main answer.
Recovery should be a product feature.

### 5a) Storage-root and service-profile transitions still look too much like identity magic

Resilio's official docs also show a second recovery seam. The Linux guide says storage defaults to a hidden `.sync` folder under the current working directory if you do not set it explicitly. The Windows service troubleshooting guide says that switching the service to `Local System` creates a different storage root, starts with no previously added shares, and requires re-adding / re-sharing data from that new context. The stolen-device guidance separately recommends unlinking, regenerating identity, reinstalling, and re-sharing.

Those are honest documents, but together they reveal that several important things are still tightly coupled in practice:

- storage root
- service profile / runtime user
- identity continuity
- share inventory
- recovery posture

AnonSync should expose those seams directly. Operators should be able to inspect, export, move, attach, or replace state roots and service profiles as supported workflows rather than discovering them indirectly through missing shares or a new WebUI context.

### 5b) Clean-install versus migrate behavior proves that state transitions need their own receipts

Resilio's service-install guidance is especially revealing here. On Windows service install, choosing migration keeps existing shares, while choosing a clean installation means re-sharing or reconnecting folders from a new context. The cloning article separately says plain copies and drive-cloner style duplication are unsupported.

That combination means operators are crossing a real state boundary even when the UI language can still feel like “same app, new mode”.

For AnonSync, the implication is strict:

- root attach must be distinct from root creation
- move-root must be distinct from import-state
- service-profile switch must prove whether it opens the same root or a different one
- every such transition should leave behind a snapshot, a report, and an audit trail


### 5c) Path binding, repair, and preservation still collapse into reconnect ritual

A deeper pass over Resilio's docs reveals another seam that matters just as much as storage-root handling. Linked-device guidance says that if a device is in `Selective Sync` or `Synced` mode, newly visible folders go into the default folder location; choosing a custom location requires putting the device into `Disconnected` mode and then manually connecting each desired folder. The reconnect guide separately says the proposed path may differ from the original and can create a duplicate-index directory, even while telling the operator to ignore a non-empty destination warning if they mean to reconnect the old directory. Move/rename guidance says path continuity is only supported inside fairly narrow drive or parent-folder boundaries, otherwise the operator gets `Folder not found`.

The recovery side is just as revealing. `Service files missing` guidance still tells the operator to make sure nothing important is in archive, delete `.sync`, remove the share, and add it back. Archive restore remains manual and hidden-directory-oriented, and the docs note that restore back into live sync behavior depends on Sync already running.

Those are not random rough edges. Together they show that four different things are still too entangled:

- visible share identity
- local bound path
- hidden binding/service markers
- preservation / history posture

AnonSync should keep those as separate public state. A moved path, broken marker, detach, or restore should not force the operator to choose between “pretend this is a brand-new mount” and “remember the right filesystem ritual.”

### 5d) Successor cutover is still spread across installer, service, link, uninstall, and theft rituals

A still deeper pass over Resilio's docs exposes one more continuity seam. One article says cloning a Sync instance with plain copies, drive cloners, `dd`, or Time Machine is unsupported. Another says Windows service install offers `migrate settings and uninstall existing Sync client` versus `clean installation`, where the clean path requires re-sharing and reconnecting existing folders. Troubleshooting then says that switching the service to `Local System` opens a different storage folder, shows no old shares, and requires re-add/re-share from that new context. Linked-device docs separately warn that linking two already-initialized devices can make one lose its certificate and take over the other's configured folders. Uninstall guidance says to unlink identity and remove remaining Standard shares first or the old instance will merely remain visible as offline elsewhere, while hidden `.sync/Archive` bytes still need manual deletion. Stolen-device guidance escalates still further to backup, remove shares, unlink identity, remove storage state, reinstall, regenerate identity, relink, and reshare.

Those are honest documents, but together they reveal that cutover meaning is still too scattered in practice. The operator still has to reconstruct whether the action is really:

- successor continuity
- same-root runtime re-home
- fresh install from a new state root
- active revocation and residue cleanup
- unsupported clone-like takeover

AnonSync should not leave that reconstruction work to memory. A serious product should expose one reviewed cutover model that says, before apply, which predecessor is being replaced, what continuity is claimed, what runtime/state target will open, which grants or approvals rewrite, what residue still needs revocation or later cleanup, and what receipt will later prove the outcome.

### 6) The interface story is still fragmented even when the feature list is good

A careful reading of the docs shows a pattern:

- some controls live in share preferences
- some in advanced preferences / power-user settings
- some in config files
- some in startup flags
- some in WebUI-specific or platform-specific instructions
- some are desktop-only
- some support notes explain how cached state changes the result

That does not make Resilio bad.
It does, however, make it the wrong model for a product whose main reason to exist is inspectable control.

### 6a) Its control surfaces are still split in exactly the wrong places

The current official docs make the asymmetry clearer than a quick feature list does.
Resilio does have configuration mode, startup switches, WebUI, share preferences, and power-user settings.
But the sharp edges line up badly with the most important semantics:

- configuration mode can apply preconfigured parameters, but the docs also say it can set up only **Standard** folders, not **Advanced** folders
- the documented Windows “CLI” is primarily startup and environment switching (`/config`, `/webui`, `/storage`, `/minimized`) rather than a full operational control plane
- WebUI is the default UI on Linux and Windows service installs, yet some actions still work differently there, including share-link opening, and remote listen / HTTPS posture often depends on config-file edits
- LAN-only operation is supported, but the official procedure still spans share preferences, power-user settings, `sync.conf`, restart, and even clearing cached global addresses by temporarily changing peer-expiration behavior

This is the deeper reason AnonSync should not copy the control-surface model even while borrowing product ideas.
A product cannot claim inspectable trust if its strongest semantics only exist cleanly in one mode while other modes fall back to startup flags, support-article rituals, or weaker share types.

AnonSync should therefore hold a stricter line:

- the same share/governance model must be addressable from CLI, API, config import/export, and future workbench surfaces
- read-only projections for convenience are fine, but mutation semantics must resolve to the same public objects everywhere
- “advanced mode” should mean extra visibility or expert workflows, not access to a different trust system

### 6b) Safety rails disappearing on Linux/WebUI is exactly the kind of asymmetry we should reject

Resilio's own docs say the `disable_remove_from_all_devices` power-user preference is ignored in Linux WebUI. The configuration-mode docs also say that if shared folders are set in `sync.conf`, WebUI is disabled, and that config mode can create only Standard folders. That matters because the WebUI docs also say WebUI is the default and only interface on Linux-based machines, including NAS environments.

This is more than a nuisance. It means a safety-oriented or capability-rich control can quietly vanish on the very surface many serious Linux users actually inhabit.

AnonSync should therefore require:

- cross-surface parity for safety-critical guardrails
- no dangerous verb whose scope changes by projection
- no “headless” mode that silently drops the strongest trust or review semantics

### 6c) Incoming acceptance still depends too much on reconnect ritual, device-wide mode flips, and path-memory

Resilio's docs are unusually candid here, and that is useful. They say linking devices makes every new folder automatically available on all linked devices with full read-write access. They also say that when a linked device is in `Selective Sync` or `Synced` mode, new folders land in the default folder, and that choosing a custom location instead requires switching that whole device into `Disconnected` mode first. Separate reconnect docs then say that reconnect proposes a default path that may differ from the original path, can create a new directory there, and adds an index if a same-named folder already exists. The pre-populated-folder docs add another ritual: click `Connect`, point at the existing directory, and explicitly ignore the non-empty-folder warning.

That is not a condemnation of Resilio's intentions. It is a very specific product warning:

- `visible here` is too easy to blur into `accepted locally here`
- one share's safe placement can require a device-wide mode change
- reconnect semantics still rely on operator memory about the previous path
- non-empty-path adoption is still too close to `click through and hope`

AnonSync should therefore reject the very idea that `Connect` is the public abstraction here. The public abstraction should be a reviewed claim or adoption intake surface that makes the local outcome explicit before apply.

### 7) Least privilege should not require a weaker share type or manual ritual

Resilio's docs show a particularly sharp seam here:

- linked devices acting as Owners is the default personal-mesh convenience
- read-only across linked devices requires dropping to a Standard-folder/read-only-key flow
- Standard folders then lose on-the-fly permission changes and stronger user/owner semantics

That is too much product-model switching for one everyday intent.
AnonSync should preserve one coherent share/grant model while still allowing per-device roles like `readonly-viewer`, `mirror`, or `encrypted-cache`.

### 8) Compatibility warnings should appear before commitment, not after surprise

Resilio's own upgrade/linking docs are candid that linked mixed-version constellations are a bad idea and can cause licensing/configuration trouble.
That is helpful documentation, but the product lesson is sharper:

- link/share/adopt flows should have a supported preflight stage
- preflight should report blockers, warnings, and feature downgrades
- the operator should not need to discover compatibility hazards only after linking or upgrading

### 9) Device-list cleanup and trust retirement are still too easy to confuse

Resilio's docs now make an awkward distinction very explicit:

- you cannot remotely unlink another linked device
- clearing an offline device only hides it from view and the same device will reappear if it comes back online
- uninstall guidance says that if you do not unlink/remove first, the old instance simply keeps showing up as offline on other peers
- changing identity means unlinking locally and generating a new certificate, which also removes Advanced folders from that Sync instance

Those are understandable product choices in isolation, but together they leave too much operator meaning trapped in ritual:

- was this just cosmetic cleanup?
- did we actually revoke trust?
- is the old device still allowed to reconnect if it comes back online?
- was this a replacement with continuity, or a brand-new identity?

Syncthing is helpful here not because it solves everything, but because its public model is crisper in two important ways:

- the device ID is directly derived from the public key / certificate material
- generating or validating config does not silently replace an existing device certificate
- explicit ignored-device state exists as configuration, rather than pretending visibility cleanup and trust retirement are the same thing

That suggests a sharper AnonSync rule:

> retiring, ignoring, revoking, replacing, and rotating are not UI variants of one action; they are different state transitions with different security and continuity consequences.

---

### 10) Share stewardship should not depend on an overloaded Owner bit or share-type ritual

Resilio's docs show a useful but awkward split:

- Advanced folders use `Owner` as the place where write access, grant authority, and revoke authority come together
- linked personal devices broaden that owner-equivalent power across the whole linked set
- Standard folders have no Owner concept and let peers re-share keys without the same bounded governance model
- local shares cannot carry Owner at all and may need remove/re-share steps to change authority

That is enough to build real workflows, but it is too coarse and too mode-dependent for AnonSync's thesis.
The product should let an operator answer more exact questions:

- who may change data?
- who may grant or revoke others?
- who may delegate further?
- who is allowed to hand stewardship to a successor?
- what happens if the current steward leaves or is retired?

If those answers still depend mainly on whether the share happened to be “Advanced”, “Standard”, or “local”, the interface model is not explicit enough.

### 11a) Convergence still arrives through symptoms, warnings, and support lore more than one settlement contract

Resilio's docs are candid about several distinct states that operators must mentally combine:

- `My files don't sync` tells users to inspect `X of Y peers`, status warnings, sync history, and per-peer file queues
- `Time difference` says freshness decisions depend on converted GMT modification times and that more than 600 seconds of skew blocks transfer, with mobile devices even showing an empty list instead of files
- the watcher-exhaustion warning says local changes may no longer be noticed immediately and will only upload after manual or periodic rescan
- `Some internal tasks are taking time to complete` says hidden read/hash/merge/dedup work may still be active even when the system can later recover on its own

Those are individually reasonable diagnostics.
Together they reveal a missing public contract:

- is the share merely idle right now?
- is it fully caught up against currently reachable peers?
- which peer or witness set is actually required for the intended action?
- is change detection degraded such that “looks settled” is weaker than usual?
- is hidden background work still changing the answer?
- how fresh is the evidence, and how long may it be reused before it goes stale?
- would a cutover / backup / relocation be acting on trustworthy state or on provisional state?

Syncthing is helpful as a contrast because its public REST and event surfaces explicitly expose folder state, `need*` counts, completion percentages, and folder-completion events.
That is still not a perfect settlement theorem, but it is much closer to a product that treats convergence as supported machine state instead of peer-list inference.

AnonSync should go further and make settlement confidence first-class.
It should also make *the readiness bar itself* first-class, so the product can say not only “current convergence is medium confidence” but “cutover policy remains blocked because quiet window has not elapsed” or “backup policy is satisfied because the missing cold replica is explicitly non-required.”

### 11b) File-system and path semantics still leak through conflicts, toggles, and folklore

Resilio's docs still expose an awkward truth about cross-platform syncing: important behavior at the filename and filesystem boundary is partly explained after the fact through conflict files and power-user toggles.
Official docs say conflicts can arise from case-insensitive filesystems, decomposed Unicode, prohibited symbols, linked junctions, and re-adding folders that already contain conflict artifacts.
They also document toggles such as `ignore_symlinks`, `normalize_unicode_paths`, `sync_extended_attributes`, `fix_conflicting_paths`, and `sync_max_time_diff`.

That is useful honesty from the product.
It is also evidence that a serious operator surface should not make people infer compatibility from emergent conflict names or hidden advanced settings.

The deeper problem is not just “some platforms differ.”
The deeper problem is that several distinct questions are easy to conflate:

- can these peers represent the same pathnames without collision
- do they agree on Unicode normalization behavior
- will symbolic links, junction-like entries, xattrs, or ACL-adjacent metadata behave the same way
- what timestamp skew or filesystem granularity will block or distort transfer
- whether a warning is merely advisory, auto-correctable, or a hard blocker for safe adoption

Syncthing is not perfect here either, but its docs point in a cleaner direction.
They explicitly document what kinds of metadata are or are not synchronized, note that support depends on OS and filesystem, expose case-sensitivity safety checks as `caseSensitiveFS`, and expose Unicode normalization handling as `autoNormalize`.
That is still configuration-heavy, but it is much closer to an inspectable public model than conflict-file folklore.

So AnonSync should not clone Resilio's posture here.
It should treat filesystem/path semantics as first-class compatibility state.

## What this forces AnonSync to do

The non-cloning case is now specific enough to generate requirements.

### Requirement 1 — linking must be relationship-only by default

Device linking may simplify discovery and policy installation.
It must **not** automatically imply global folder visibility, owner-equivalent power, or future auto-approval unless those outcomes are explicit policy objects.

### Requirement 2 — replacement must be a recovery workflow, never a side effect

The product must distinguish clearly between:

- adding a device
- linking a device
- replacing a lost device
- rotating or revoking identity

Those must not collapse into one fuzzy “connect this thing” flow.

### Requirement 3 — advanced trust semantics must not be surface-specific

If AnonSync has an advanced trust model, it must be available uniformly from:

- CLI
- daemon API
- config import/export
- future UI/TUI

No “the real model exists in UI only” split.
No “config mode can only express the weaker share type” split either.

### Requirement 4 — policy changes must expose retained-state consequences

Changing route/discovery policy must show:

- which live settings changed
- which cached state remains
- whether cache clear is recommended or required
- which peers or shares are affected

### Requirement 5 — incoming handling must be per-share, not hidden behind a device-wide default

The product should distinguish clearly between:

- seeing that a share exists
- accepting or rejecting it for this device
- choosing a local path
- choosing a materialization mode

No operator should need to flip an entire device into a different linked-folder default mode just to place one share carefully.

### Requirement 5a — announcement visibility, local claim, and local path creation must be separate public acts

Resilio's current linked-device docs now make the arrival seam explicit enough that the archive should name it directly.
A share may become visible on this machine before this machine has chosen a path, role, or local storage posture.
The product should therefore expose, separately:

- visible here without local path bind
- deferred here without local path bind
- hidden here only
- claim in review
- claimed and bound here
- withdrawn by wider authority

If `remove` can mean both `hide on this machine` and `withdraw from constellation`, or if `connect` can silently mean both `claim` and `bind`, the interface is not explicit enough.

### Requirement 6 — restore must be a supported interface, not a support ritual

Operators should be able to ask for file history and restore through normal CLI/API surfaces.
The contract must make explicit:

- what candidate versions exist
- whether restore is local-only or replicated back into the share
- whether a plan/review step is required
- which audit/event records were produced

If restore requires hidden archive spelunking, the product has not really exposed the model.

### Requirement 7 — provenance must be queryable

Operators should be able to answer questions like:

- why does this linked group have this auto-grant?
- which profile created this policy?
- which recovery workflow rebound this grant?
- why is this route still being chosen?

If those answers are buried in folklore, the product has already started drifting toward the thing it claims to improve.

### Requirement 8 — ignore and history policy must not live as hidden-service-file folklore

Operators should be able to inspect and change ignore/versioning behavior through supported surfaces.
At minimum the product should expose:

- the effective ignore rules for a share
- whether rule drift exists across peers or local policy layers
- where history/versioning is stored and retained
- whether service-state damage requires repair

Hidden implementation files may still exist on disk, but they should not be the only serious control surface.

### Requirement 9 — conflicts must be first-class records with safe resolution paths

Operators should be able to inspect conflicts as structured cases rather than infer the situation from filenames alone.
The contract should make explicit:

- what conflicted
- which candidates exist
- which resolution would stay local vs affect the replicated share
- which resolution was chosen and why

If the safe answer is still “rename things in the filesystem carefully and hope you understood the support article,” the model is not explicit enough.

### Requirement 10 — path binding must be explicit and compared before merge

Resilio's official docs say a local folder rename only affects that device, moving a share is limited by platform and drive boundaries, reconnect can propose a different default path and create a duplicate-index directory, and connecting a pre-populated folder can merge content while letting the latest timestamp win when same-named files differ.
Syncthing's FAQ reacts in the opposite direction: it says there is no direct move workflow, recommends remove/move/re-add, and warns that if devices are not already in sync the winner after a move can be unpredictable.

Those are two different product choices, but they reveal the same missing contract:

- share identity
- local path binding
- existing on-disk contents
- conflict policy during adoption or relocation

should not be implicitly braided together.

AnonSync should therefore treat adoption into a non-empty path and relocation of an existing mount as compared, reviewable actions.
At minimum the product should expose:

- whether the target path is empty, already bound, or contains service markers for this share or some other share
- which files are identical locally and remotely
- which files are local-only
- which files are remote-only
- which paths are true collisions requiring policy or manual review
- which winner policy would apply, if any
- whether the action is safe only when fully in sync first

If the safe answer is still “point it at the folder and trust the reconnect dialog” or “remove/re-add and hope you timed it correctly,” the interface is not explicit enough.

### Requirement 10a — pre-existing material reconciliation must be its own reviewed act, not a `Folder not empty` warning

Resilio's newer docs make this seam even clearer than the earlier move/reconnect discussion alone. The `Folder not empty` article says the warning appears both when adding into an existing directory and when reconnecting to a directory that was syncing before, and that files already present in the receiving folder may be deleted or overwritten. The pre-populated-folder FAQ says Sync hashes both trees, merges other files, and lets the latest timestamp win when same-named files differ. The encrypted-folder docs then add a materially different case: a non-empty target should not be used at all because ordinary existing files will be ignored, while previously encrypted files with the same encrypted key can still be re-synced and moved to Archive.

That means one small confirmation box is hiding several operator-different outcomes:

- same-lineage reuse of a previously bound target
- harmless merge of identical plus remote-only material
- same-path divergence where chronology and authority both matter
- encrypted-target misuse where existing bytes are not part of an ordinary merge story at all

AnonSync should therefore expose non-empty-target reconciliation as its own reviewed object.
At minimum the product should expose:

- target lineage posture (`same-lineage-likely`, `same-lineage-unproven`, `foreign-local-tree`, `encrypted-target-mismatch`)
- counts for identical, local-only, remote-only, same-path-divergent, and path-collision classes
- chronology confidence and whether any winner ranking comes only from timestamp evidence
- preservation and quarantine posture for pre-existing local material
- whether encrypted/annex reuse is blocked, reviewed, or safely reusable
- which admissible outcomes exist: bind identical-only, merge remote-only, reviewed replacement, reviewed preserve-and-quarantine, or block

If the safe answer is still “click OK”, “ignore the warning”, or “latest timestamp wins”, the interface is not explicit enough.

### Requirement 10b — placeholder visibility and retrievable bytes must be separate public facts

Resilio's newer docs make this seam unusually explicit too. `Selective Sync` says enabling it means the device receives placeholder information rather than full bytes, and that linked-device Selective Sync can leave all new files presented as `.rsl` placeholders. `What Is an RSLS File?` then says reverting a file to placeholder preserves copies on other peers — but warns that if you and all other peers do this, you can end up with placeholders only and no actual file. `Sync Interface on iOS devices` adds that `Clear synced files` can turn all synced files on the device back into placeholders. Finally, the ghost-file warning article says a peer may announce new or updated files, other peers may merge that tree later, and by then the source may already have reverted to placeholder or removed the bytes entirely, leaving a stale announcement that no peer can now satisfy.

That means one apparently simple user-facing state can hide several operator-different realities:

- visible name plus a confirmed durable full-copy witness elsewhere
- visible name backed only by this local full copy
- visible name backed only by an offline source that may or may not return
- visible name announced in the tree even though no peer now has the bytes
- placeholder-clearing or eviction action that would silently create a placeholder-only universe

AnonSync should therefore expose fetchability and source backing as their own reviewed object.
At minimum the product should expose:

- namespace/materialization posture separately from byte retrievability posture
- full-copy witness summary (`local-only`, `remote-confirmed`, `multi-source-confirmed`, `offline-only`, `none-known`)
- fetchability posture (`fetchable-now`, `fetchable-when-source-returns`, `local-last-copy`, `ghost-risk`, `not-fetchable`)
- eviction safety posture and whether the requested action would remove the last known full copy
- whether a stale announcement should be preserved, re-witnessed, quarantined, or retired from visibility claims
- which admissible actions exist: keep pinned, fetch now, evict safely, defer until another witness exists, or mark as ghost/stale announcement

If the safe answer is still “it shows up, so it must be available”, “just clear synced files”, or “ignore the warning and hope a source returns”, the interface is not explicit enough.

### Requirement 11 — linked-device convenience must preserve least privilege

Operators should be able to keep a personal-device constellation convenient while still assigning distinct roles such as:

- primary writable device
- read-only viewer
- receive-only mirror
- encrypted replica

No routine intent should require falling back to a weaker share type or manual key ceremony just to avoid owner-like authority.

### Requirement 12 — preflight must be a first-class control surface

Before linking a device, accepting an invite, adopting a share, or applying a role that may degrade capability, the product should support a preview that reports:

- blockers
- warnings
- compatibility/version-family hazards
- feature downgrades
- permission/authority consequences

If the safest answer still lives mainly in release notes, upgrade FAQs, or tribal memory, the operator surface is not explicit enough.

### Requirement 13 — approval memory must be explicit, scoped, and revocable

If the product wants “approve once” convenience, it should still make the remembered approval visible as first-class state.
Operators should be able to inspect:

- which peer or identity was previously approved
- what future shares that approval can cover
- which local devices are allowed to exercise it
- what maximum role or permission it can imply
- when it expires, was used, or was revoked

That is how AnonSync keeps convenience while refusing ambient trust drift.

### Requirement 14 — destructive actions must expose preservation evidence

Before evicting, removing locally, deleting from the share, or restoring back into replicated state, the operator should be able to inspect a preservation report that says:

- what will remain on this device after the action
- how many known plaintext replicas remain and whether any are currently reachable
- whether the remaining copies are only encrypted replicas
- whether version history exists for this path and on which peers
- whether history retention or size caps make that rollback path weaker than it looks
- whether policy blocks the action or requires an elevated acknowledgement because preservation would become too weak

If the operator still has to remember “this menu item is safe, that filesystem delete is not, and the hidden archive may or may not keep a copy depending on file size and platform”, the interface is not explicit enough.

### Requirement 15 — topology policy must expose disclosure, not just route preference

A discovery policy should answer not only:

- can peers connect?
- which route wins?

but also:

- which infrastructure learns this device/share reachability?
- which announcements are local-only vs private-infrastructure-only vs public-infrastructure-visible?
- whether a policy publishes addresses, only dials known targets, or does both
- which fallback step would widen metadata exposure if direct connection fails

If an operator cannot distinguish “announce publicly, dial privately, relay only as last resort” from “never announce publicly at all”, the control surface is still too coarse for the product thesis.

### Requirement 16 — temporary operational changes must be explicit leases

The product should model maintenance intent separately from durable policy.
Operators should be able to inspect:

- what target is under an override
- whether the override blocks upload, download, announcement, or only new transfer starts
- whether scans, indexing, and delete propagation continue
- when the override expires automatically
- who created it and why
- what durable policy resumes when it ends

If a surprising state still gets explained mainly as “that share is paused, except deletions still go through and this LAN rate limit lives somewhere else,” the contract is still too implicit for AnonSync's thesis.

### Requirement 17 — retirement, ignore, revoke, replace, and rotate must be separate supported workflows

Operators should be able to ask for one of these intents explicitly:

- hide an offline device from ordinary views without changing trust
- ignore or suppress future unsolicited contact from a device or identity
- revoke active grants / approval memory / route publication tied to a device
- replace a dead device with a successor while preserving selected continuity
- rotate identity material without pretending it was just cosmetic cleanup

The product should make visible for each retirement action:

- whether the old device can still reconnect
- whether any grants or approval-memory records still reference it
- whether the action is cosmetic, suppressive, revoking, or continuity-preserving
- whether a successor device inherits any role, share visibility, or recovery posture
- what remote cleanup remains impossible until peers observe the retirement

If the operator still has to remember that “hide” is not “unlink”, “unlink” is not “replace”, and “new identity” quietly means “new certificate plus share fallout”, the trust model is not explicit enough.

### Requirement 18 — share stewardship must be explicit, bounded, and transferable

The product should not rely on one coarse Owner bit to carry every governance meaning.
Operators should be able to inspect for each share:

- who currently has data-write rights
- who currently has grant / revoke authority
- whether delegation is allowed and with what bounds
- whether a steward can nominate or pre-approve a successor
- whether a handoff requires quorum, review, or plan/apply
- what happens to grants and approval-memory records if the current steward departs

The product should also support a first-class stewardship record or plan that makes clear:

- the current steward set
- the candidate successor set
- the exact authority to be transferred
- what will remain non-transferable
- what recovery or retirement preconditions must already be satisfied
- which audit and event records will explain the handoff later

If the answer is still “make them Owner”, “re-share with a different key”, or “switch share type and do it again”, the contract is still too coarse for AnonSync's reason to exist.

### Requirement 19 — local deviation policy must be explicit on non-authoritative mounts

The product should not make operators infer local-remediation behavior from a mix of permission level, mount mode, and share type.
For any role or mount that is not supposed to authoritatively propagate local edits, operators should be able to inspect:

- whether local adds are preserved, quarantined, auto-reverted, or blocked pending review
- whether local content edits are preserved-and-flagged, turned into conflict material, or auto-reverted
- whether local deletes are treated as re-fetch, preserved absence pending review, or auto-revert
- whether the system keeps pulling remote updates while local deviation exists
- whether deviation causes a warning, a blocked path, or a review-required state
- whether any part of the policy is forced by capability limits rather than chosen intentionally

The product should also expose that policy in plans, explain surfaces, and role profiles so the operator can answer before attach:

- what happens if someone accidentally edits a supposedly read-only copy
- whether the policy will silently destroy those local edits
- whether a receive-only mirror can keep local forensic evidence without propagating it
- whether an encrypted replica is forced into stricter remediation because of its trust posture
- what exact event or audit record will show that deviation was detected or auto-remediated

If the answer is still “depends whether overwrite is on”, “depends whether selective mode disables the checkbox”, or “depends which share type you happened to start from”, the contract is still not explicit enough.

### Requirement 19a — file intent must survive mode changes, placeholder state, and surface changes

The product should let operators answer, for any file-affecting action:

- is this fetching bytes, evicting bytes, removing local visibility, deleting from the share, restoring locally, or restoring to the share
- which scope would the action touch
- what preservation posture remains afterward
- whether any local deviation case already changes the meaning or risk of the action

If the answer still depends on whether the mount is currently placeholder-visible, whether a read-only checkbox is active, or which surface exposed the action, the contract is still too implicit.

### Requirement 19b — non-authoritative local drift must be a public case, not a warning string

The product should not merely say that a read-only or mirror target is “out of sync”.
It should expose a first-class deviation case that makes explicit:

- what local action occurred
- what remediation policy applies
- whether remote progress is continuing, blocked for the path, or blocked for the mount
- whether local evidence was preserved, copied aside, reverted, or quarantined
- which operator actions can resolve the case next

If the operator still has to infer that state from stalled transfers, read-only caveats, or context-menu behavior, the interface is not explicit enough.

### Requirement 20 — filesystem compatibility must be a first-class preflight and runtime surface

Case-only collisions, Unicode-normalization mismatches, prohibited symbols, symlink/junction handling, metadata support, and clock/filesystem quirks should not surface only as later conflict files or support-article discoveries.

AnonSync should expose:

- local filesystem profiles for each mount target
- peer/share compatibility reports that classify findings as `ok`, `auto-correctable`, `warning`, or `blocked`
- explicit policy about symlink handling, path normalization, and metadata classes
- explainable downgrade or auto-rewrite behavior where normalization or metadata stripping is unavoidable
- durable findings when a mount is operating under reduced filesystem fidelity

That is a stronger answer than either copying Resilio's folklore-heavy model or merely inheriting Syncthing's advanced-setting vocabulary.

### Requirement 21 — settlement confidence must be explicit and queryable

A sync product should not force operators to guess whether a share is really safe to treat as settled.
At minimum the product should expose:

- transfer completion counts and source availability separately
- whether current convergence is based on healthy continuous change detection or degraded periodic rescan
- whether clock-skew findings make freshness comparison unreliable or blocked
- whether hidden merge / hash / dedup work is still in progress
- whether the daemon considers the share `idle`, `converged`, `degraded-converged`, `blocked`, or `unknown`
- whether a requested barrier such as cutover / backup / relocate / restore has stronger preconditions than ordinary idle status

Resilio's own docs show why this matters: peer counts and status warnings are only part of the picture, watcher exhaustion weakens freshness detection, excessive time difference blocks transfer and can hide files on mobile, and internal background tasks may still be running even when the product can eventually recover.
If the operator still has to combine those clues manually before asking “can I trust this share as a clean handoff point?”, the interface is not explicit enough.

### Requirement 21b — settlement barriers and receipts must be explicit

A sync product should not stop at emitting one convergence report.
If high-signal actions depend on settlement, the product should also expose:

- named settlement/readiness policies per intent
- explicit required-source or witness-set rules
- maximum evidence age and quiet-window requirements
- reusable readiness barriers that can say which clause failed
- settlement receipts proving what evidence standard an action used at apply time

Resilio's current docs show why this matters: troubleshooting still tells operators to combine `X of Y peers`, status warnings, sync history, per-peer queues, invalid-time warnings, watcher exhaustion, background-task caveats, and even “ghost file” warnings where announcement outlived source availability. Those clues are useful, but they still leave the answer to “safe enough for cutover under *which* rule?” outside the product model.

AnonSync should therefore let operators ask two distinct questions:

- what is the current convergence evidence?
- does that evidence satisfy the chosen readiness rule for this action right now, and if so for how long?

If the operator still has to translate a medium-confidence convergence report into an informal cutover decision with no barrier object or later receipt, the interface is not explicit enough.

### Requirement 22 — namespace projection and suppression must be explicit

A sync system should distinguish at least four questions:

- is this path part of the share namespace that peers learn about?
- if content is suppressed, do peers still learn the directory shape?
- on this mount, should the path be omitted, shown as placeholder/metadata-only, or fully materialized?
- when a tighter rule is added later, does it leave already-indexed structure visible, require review, or retract it?

Resilio's own docs say `IgnoreList` lives in hidden `.sync`, is case-sensitive, will not work with files that have already been synced, and that once Sync has scanned and indexed the directory tree its structural information is stored in the database and always passed to other peers until the share is disconnected. The same family of docs says Selective Sync presents new files as placeholders, deleting a synced local copy can revert it to a placeholder, and removing the Selective Sync share removes placeholders from that device's filesystem. Those behaviors are individually understandable, but together they still blur ignore, namespace visibility, and materialization. They also say xattrs bypass `IgnoreList` and require `StreamsList`, while separately shared nested subfolders disable Selective Sync and create extra indexing work. That strengthens the case that projection cannot be left as an incidental side effect of hidden control files or share-topology tricks.

AnonSync should therefore expose:

- share-level projection rules that decide namespace announcement/suppression
- mount-level projection rules that decide `omit`, `placeholder`, `metadata-only`, or `full` local visibility
- path-test surfaces that answer both questions together for a concrete path
- tighten behavior that says whether already-indexed or already-materialized paths are left alone, reviewed, evicted safely, or blocked pending operator review

If the operator still has to remember that “ignore later stops bytes but not already-indexed structure” while separate placeholder rules still decide what appears locally, the interface is not explicit enough.


### Requirement 23 — bundled privacy transports must still be explicit operator state

If AnonSync ships Tor and I2P inside the product, that does **not** justify making them magical.

The product still needs explicit operator-visible state for:

- which transport engine is present
- whether it is compiled in or activated from an embedded payload
- whether it is currently cold, warming, ready, degraded, or failed
- whether a route was rejected because policy forbade it, because the runtime was cold, or because bootstrap failed
- whether the daemon is using a long-lived transport session or some more transient route strategy

Otherwise “privacy transport support” would remain marketing language rather than a public contract.

### Requirement 24 — Linux-first must name support tiers, not just a philosophy

Saying “Linux is first-class” is still too soft unless the archive names the real v1 support boundary.

AnonSync should therefore publish at least:

- which Linux filesystems are first-class for correctness claims
- which filesystems are probeable but only best effort
- which metadata/ACL/xattr/symlink guarantees are required for strong support
- which environments should surface warnings or blocks before share adoption

That is part of the non-cloning case too.
Resilio can chase broader convenience.
AnonSync earns its keep by being more explicit about what it will support well before it claims broad platform parity.

### Requirement 25 — exposure, dialing, and temporary direct exceptions must be separate supported surfaces

Resilio's current docs make it clear that serious route control exists, but it is spread across multiple mental models:

- tracker / relay / direct path behavior in the network article
- `known_hosts`, `use_tracker`, `use_relay`, and `tunnel_protocols` in power-user preferences
- LAN-only support guidance that still requires cache-clearing rituals if an Internet path was learned before

That is real capability.
It is also exactly the kind of fragmented operator contract AnonSync should not clone.

AnonSync should expose at least four distinct supported surfaces:

- a **publication profile** that answers who can learn this device/share reachability and through which infrastructure
- a **dial policy** that answers which route classes may actually be attempted and in what preference order
- **known-host records** that answer which peer-pinned direct paths are allowed without turning on ambient public direct
- **route leases** that answer which temporary exceptions are active right now and when they end

If the operator still has to reconstruct “what will be published?” by combining one screen, one hidden preference, one cache fact, and one troubleshooting article, the route surface is still too implicit.

### Requirement 26 — peer-pinned direct paths should exist without enabling ambient public direct

Resilio's `folder_defaults.known_hosts` preference is a good clue.
There is real value in saying:

> “I trust **this** peer at **this** address for **this** share or policy window.”

That is not the same thing as saying:

> “public clearnet direct is generally allowed now.”

AnonSync should therefore support peer-pinned direct admission as a first-class concept with:

- peer scope and optional share scope
- explicit provenance and reason
- optional expiry
- visible interaction with the base privacy policy
- explainable effective state when the pin is the reason a route became eligible

That gives AnonSync a better answer than either extreme:

- not “never use direct, ever”
- not “enable public direct and hope the operator remembers why”

### Requirement 27 — temporary bulk-speed exceptions should be bounded by more than vibes

The archive already decided that WAN clearnet direct must not be the default.
This pass adds the stronger follow-through:

- a temporary direct exception should normally carry a **TTL**
- it should also be able to carry an optional **byte cap** or other exhaustion condition
- the route surface should say whether the exception ended because time expired, byte budget was consumed, or the operator canceled it

That matters because “temporary” often stops being temporary when the only bound is human memory.
A bulk-seeding window that automatically collapses after 250 GiB or 90 minutes is much more honest than a toggle the user meant to undo later.

### Requirement 28 — Linux-local semantics should outrank network-share convenience

Resilio's own docs are useful here too.
They say SMB setups can lose immediate notifications and fall back to rescans, that some NAS/SMB patterns can lose or corrupt files, that symlink behavior is platform-dependent, and that xattr syncing still depends on whitelists and hidden service files such as `.sync/StreamsList` and `.sync/Streams`.

That does **not** mean Resilio is bad.
It means AnonSync should resist the temptation to treat remote/network-share convenience as the main design center.

Linux-first should continue to mean:

- local Linux filesystems are the correctness bar
- network filesystems are explicit warning-tier or best-effort targets unless proven otherwise
- metadata fidelity, watcher quality, symlink policy, and xattr contract are supported surfaces, not service-directory folklore


## What this now says about the interface

### Interface conclusion 1 — the home surface must be a review queue, not just a share list

Resilio's convenience works partly because it gives users a compact operational picture quickly.
Its weakness is that important differences still hide behind mode side effects, linked-device assumptions, or support-article knowledge.

AnonSync should therefore make the home surface a first-class review queue that can summarize:

- pending peers
- incoming shares
- degraded routes or privacy runtimes
- blocked transfers or degraded settlement
- plans awaiting apply
- successor / retirement reviews

### Interface conclusion 2 — one share view must answer five distinct questions

A share page should let an operator answer, without jumping across disconnected surfaces:

- is the share merely visible here, or adopted into a path
- how much data is actually local here now
- who has authority over it
- which route and exposure posture is effective
- what destructive actions are safe or unsafe right now

This is one of the strongest anti-clone lessons in the whole archive.
Resilio is capable, but it still makes operators reconstruct too much of that answer set indirectly.

### Interface conclusion 2a — claim and adoption need one intake pane, not several `Connect` dialogs

The way in should have the same discipline the archive now demands for the way out.

The intake surface should always show, in one stable order:

- what became visible or was offered
- what this machine is about to accept locally
- which path and filesystem contract are being chosen
- whether authority is widening or only local visibility is changing
- what blockers, drift, or follow-up still exist
- which receipt will later prove the accepted outcome

Otherwise the product will drift back toward exactly the Resilio seam the archive is trying to avoid: features that are individually useful, but whose acceptance meaning still depends on which surface produced the `Connect` prompt.

### Interface conclusion 2b — the product needs an announced-share inbox, not auto-created default-path folklore

A serious operator product should have one stable place where a machine can see newly visible shares without pretending they are already bound locally.
That inbox should keep these distinctions explicit:

- visible here
- claimed here
- bound here
- hidden here only
- withdrawn wider by authority

Otherwise the product drifts back toward the Resilio shape where a newly visible share can too easily become a default-path artifact, a duplicate-index directory, or a cross-device `remove` story before the operator has clearly chosen which of those outcomes they actually wanted.

### Interface conclusion 3 — destructive and rollback actions need proof panels, not naked verbs

Resilio's docs around selective-sync delete, archive restore, hidden service files, conflict files, and generic History are all telling the same story: destructive or recovery-relevant operations are too easy to misunderstand when the system surface is thinner than the real state model.

AnonSync should treat preservation reports, convergence reports, compatibility reports, exposure reports, and rollback/conflict reports as part of the interface itself.

### Interface conclusion 4 — least privilege must stay legible even in personal-device convenience flows

The interface cannot merely *support* least privilege in the daemon.
It has to show it.

That means a linked-device or personal-constellation view must still make these visibly distinct:

- relationship membership
- share grants
- remembered future approval
- successor carry-forward policy
- temporary route or maintenance overrides

### Interface conclusion 5 — replacement and succession need their own operator surface

If replacement, continuity, and authority carry-forward remain buried under backup/recover subcommands, the interface will still feel like a support workflow instead of a supported workflow.

AnonSync should therefore reserve dedicated interface space for:

- replace this device
- revoke this device
- ignore future contact
- carry forward limited continuity
- review exactly what survives the handoff

### Interface conclusion 6 — recovery material needs its own custody page, not just export verbs

If recovery artifacts remain visible only as files on disk or subcommands in help text, operators will still be forced to reconstruct the real story from export success, stale notes, and hidden state assumptions.

AnonSync should therefore reserve dedicated interface space for:

- workflow-scoped recovery posture
- bundle custody class and hidden dependency state
- invalidated versus current recovery material
- continuity claims before a bundle is consumed
- receipts for export, verification, invalidation, and recovery-byte import

### Interface conclusion 7 — share detail needs one binding/preservation spine

The share view should not make operators visit one page for mount state, another for restore, another for hidden-path troubleshooting, and a fourth for reconnect folklore.
A trustworthy surface should answer in one place:

- where the share is bound now
- what path the operator expects it to live at
- whether the binding is healthy, missing, or drifted
- what preservation or history posture survives right now
- which action preserves continuity: compare, repair, relocate, detach, or restore

### Interface conclusion 8 — successor cutover needs one dedicated page, not installer-choice archaeology

If same-person continuity still depends on remembering whether this was a service migration, clean install, state-root switch, certificate takeover, or stolen-device reset, the interface has not exposed the model.

AnonSync should therefore reserve dedicated interface space for:

- predecessor and candidate comparison
- continuity carry-forward summary
- state-root and runtime target truth
- share / grant / approval rewrite scope
- residue and revocation obligations
- receipt-backed proof of the cutover actually applied

### 16b) Storage pressure, reclaim, and retention still depend on scattered support knowledge

Resilio's current docs still distribute storage truth across several separate surfaces.
Synchronization-mode docs say Selective Sync uses placeholders and takes up minimal hard-drive space, and linked-device docs say you can click a `Sync All` device and see its storage status.
Archive docs separately say old or deleted copies live in hidden `.sync/Archive`, stay for 30 days on desktops and 1 day on mobiles by default, can be kept forever with `sync_trash_ttl=0`, and only support manual restore.
Power-user preferences add `free_space_warning_threashold`, `log_size`, `log_ttl`, and `max_file_size_for_versioning`.
The troubleshooting page separately says syncing can stop when the downloading device runs out of free space and tells operators to inspect hidden `.!sync` remnants manually.
Storage-folder and uninstall docs then add that databases, logs, profiler output, and archived service data live in separate storage paths and may continue consuming space after uninstall unless manually removed.
An iOS-only storage-management page splits usage into app data and user data and allows clearing local files, but that is still not the general product contract.

That combination is revealing.
The product does have real space-saving features and real retention controls, but the operator still has to reconstruct one storage story from several disconnected ideas:

- placeholder-visible namespace versus full local bytes
- hidden archive/version retention
- state/database/log/profiler growth
- low-space warnings and hard stops
- temp-remnant cleanup rituals
- platform-specific storage screens

AnonSync should not clone that shape.
A serious control surface should instead publish one storage-budget model with:

- durable space ledgers by byte class
- explicit budget policy and pressure thresholds
- reclaim plans that say what classes would free space and what retention/provenance would be weakened
- reclaim receipts that prove what actually changed


### 16c) Capability-bearing offers still depend on type-specific sharing ritual

Resilio's current docs still distribute portable-authority truth across several separate concepts.
The desktop share dialog says Standard folders can be shared by key while Advanced folders use links or QR, and explicitly says the major difference between keys and links is the approval mechanism. The same dialog adds security options such as expiry period and use-count limits for links.
The link-structure article then explains that a shared link carries folder metadata, a temporary key, and expiration time, and that approval results in a new certificate and ACL entry.
The Standard-vs-Advanced comparison separately says Standard folders let a peer share the key it has without limitation, while only Owners can share Advanced folders and on-the-fly permission changes require the stronger Advanced model.
The comprehensive guide still frames manual sharing as choosing key, link, or QR because they have different flow and functionality, and the local-share article separately adds that local shares inherit source permissions and can require remove-and-re-share ritual to change access.

That combination is revealing.
The product does have useful portable sharing mechanisms and some good security controls, but the operator still has to reconstruct one capability story from several disconnected ideas:

- share type versus delivery mechanism
- approval-bearing artifact versus no-approval artifact
- expiry and redemption budget
- redelegation and onward-sharing rights
- the eventual local outcome when the receiver consumes the artifact

AnonSync should not clone that shape.
A serious control surface should instead publish one offer-artifact model with:

- one normalized manifest regardless of whether the artifact is delivered as file, URI, QR, or clipboard string
- explicit approval posture and peer-pinning rules
- explicit redelegation policy and redemption budget
- claim receipts that prove what local outcome later consumed the artifact

### 16d) Attention and acknowledgement still depend on scattered channels and support navigation

Resilio's current docs still distribute operator attention across several separate surfaces.
`My files don't sync` tells the user to inspect the `Peers` column, click warnings in the `Status` column, search Sync History, and inspect per-peer queues.
The `Core warnings` page separately groups tracker, free-space, identity, time-difference, and service-file issues.
The Linux guide still says there is no tray icon and notifications do not appear outside the Sync UI.
A separate browser-warning page explains the self-signed WebUI trust prompt.
Even the older change log is revealing: notifications were synchronized across devices and new notifications were added for folder-permission and licensing changes, which shows that delivery mechanics were yet another distinct attention surface.

That combination is revealing.
The product does have useful warnings and useful notifications, but the operator still has to reconstruct one attention story from several disconnected ideas:

- report-like findings on object pages
- queue placement in the main UI
- history search
- OS-specific or browser-specific prompts
- platform-specific absence of tray/system notifications
- acknowledgement behavior that is mostly implicit rather than receipt-bearing

AnonSync should not clone that shape.
A serious control surface should instead publish one attention contract with:

- explicit attention policy that maps report severity, freshness, and subject class into workbench lanes and delivery channels
- durable attention events that record what became actionable, where it was delivered, and why it was escalated or deduplicated
- acknowledgement and snooze receipts that prove whether the operator only changed presentation or actually resolved the underlying subject
- headless-safe parity so Linux-first and automation-heavy deployments do not lose semantic truth just because they lack a desktop shell

### 16e) Control access still depends too much on bind-address lore, browser ritual, and storage-folder surgery

Resilio's current docs are revealing here in a way that goes beyond “the WebUI exists”.
The WebUI docs say it is the default and only interface on Linux-based machines and the default UI for Windows service installs, with localhost listen by default and LAN exposure achieved through `0.0.0.0` or unchecking `Allow connection from this device only`.
The same docs say workstation passwords are optional, cookies last only for the browser session, and HTTPS is configured through config-file options that commonly produce self-signed trust warnings.
A separate browser-warning article then recommends a browser override shortcut or HSTS-clearing as the practical escape hatch.
A separate password-reset article says one reset path deletes settings files in the storage folder, which resets preferences and duplicates the device in `My devices`, while another path injects credentials via config.
Finally, the service-troubleshooting doc shows that changing service user can move the storage folder and therefore the state universe the operator is actually administering.

That combination is useful support knowledge.
It is not one trustworthy control-access contract.
The operator still has to reconstruct one answer from several disconnected ideas:

- loopback versus LAN bind state
- browser-session cookie lifetime
- optional versus compulsory password posture
- self-signed HTTPS and browser trust-warning behavior
- config-file credential injection
- storage-root side effects when service context changes

AnonSync should not clone that shape.
A serious control surface should instead publish one control-access model with:

- explicit endpoint objects that say local-only, SSH-forwarded, reverse-proxied, or reviewed-exposed LAN posture directly
- explicit token and session objects so browser access, CLI access, and automation access do not masquerade as one thing
- hostcheck / proxy-trust posture that is inspectable instead of hidden in deployment folklore
- access receipts so exposure, issuance, rotation, and revocation stay auditable without mutating unrelated daemon state

### 16f) Recovery material still depends too much on saved-key ritual, storage-folder continuity, and unsupported clone instincts

Resilio's current docs make this seam unusually visible.
`Cloning Sync` says plain-copy cloning of the Sync instance is not supported.
`Sync Storage folder` then says configuration, auxiliary settings, and share databases live in the storage folder and moving that state depends on config-mode knowledge.
`Encrypted folders` says encrypted-node recovery works only if the operator saved the RW/RO keys and did not remove the encrypted folder from Sync so the database remains the same, and local decrypt still requires the secret, encrypted folder path, output path, and the database path.
`How do I reset my WebUI password?` adds another revealing wrinkle: one repair path deletes settings files from the storage folder, which resets preferences and duplicates the device in `My devices`, while another path injects credentials through config mode to avoid that collateral state change.

That combination is useful support knowledge.
It is not one durable recovery-material contract.
The operator still has to reconstruct one answer from several disconnected ideas:

- is this workflow portable or still daemon-bound
- which keys or wrapped secrets were actually saved
- whether database continuity is still required
- which state-root or identity changes would invalidate older material
- what continuity the recovery path would preserve if later consumed

AnonSync should not clone that shape.
A serious control surface should instead publish one recovery-material model with:

- workflow-scoped recovery posture rather than one generic “backup exists” claim
- explicit custody classes for portable-secret, split-secret, metadata-only, and daemon-bound recovery artifacts
- explicit invalidation when rotation, retirement, or state-root changes weaken older bundles
- recovery receipts that prove export, verification, invalidation, and consumption without treating the artifact file itself as the whole story


### 16g) Release truth still depends too much on edition-family caveats, mixed-version warnings, and platform-specific update pages

Resilio's current docs make this seam uncomfortably explicit.
`Updating Sync to latest version` explains how desktop builds notice or install updates, but that is not the whole compatibility story.
`Updating installation to Resilio Sync v3` says only Home/Free/Pro-style installs may update and that Sync Business must not be updated to v3 because configured shares can be lost even if files stay on disk.
The Linux/NAS install pages repeat the same warning across platform-specific articles.
The linking guide separately warns that mixing v2 and v3 in one linked-device constellation can conflict on licensing and lead to lost access to UI and share configuration.
The changelog then carries still more migration lore in release-note form.

That combination is useful support knowledge.
It is not one durable release-compatibility contract.
The operator still has to reconstruct one answer from several disconnected ideas:

- what edition/family this subject is really on
- whether an available target is merely newer or actually supported
- whether linked-device or peer constellations are mixed in a way that remains operationally risky
- whether rollback is safe, schema-risky, or unsupported
- which warnings belong to the daemon, the bundled runtime, the peer constellation, or only one client channel

AnonSync should not clone that shape.
A serious control surface should instead publish one release model with:

- explicit release posture for daemon, runtime bundles, and peer constellations
- reviewed upgrade plans that name edition change, channel change, schema change, cutover scope, and rollback posture directly
- mixed-version or mixed-edition constellation findings that remain visible instead of hiding in FAQ prose
- release receipts that prove checks, accepted compatibility boundaries, applied upgrades, and recorded rollbacks




### 16h) Effective policy still depends too much on settings-layer archaeology

Current Resilio docs still make operators reconstruct effective behavior from several different configuration layers rather than one public precedence model.
The ordinary Preferences page carries scheduler, bandwidth limits, default folder locations, and device-wide defaults, while explicitly noting that bandwidth limits apply only to Internet traffic unless `rate_limit_local_peers` is changed in power-user preferences.  
Folder Preferences then carries per-folder relay, tracker, LAN search, predefined hosts, archive, overwrite, and file-download-priority choices.  
Synchronization mode can be changed per folder in Folder Preferences, but the device-wide default connect-folder mode lives elsewhere under Preferences.  
Power-user preferences add more defaults and exceptions, including `folder_defaults.transfer_priority`, `rate_limit_local_peers`, and a `disable_remove_from_all_devices` option that the docs explicitly say is ignored in Linux WebUI.  
Config mode adds yet another layer by allowing Advanced/Power User parameters to be injected again through startup configuration.  
Most revealingly, the current file-download-priority docs say a global default can affect both existing and new shares, but once a share's priority was manually altered it stops following later global changes “even if the priority was later manually set back to None.”

That is useful support knowledge.
It is not one trustworthy operator contract.

AnonSync should instead publish one effective-policy surface with:

- explicit defaults profiles and policy bindings rather than scattered hidden convenience presets
- per-field origin showing whether the current value comes from built-in default, defaults profile, pinned policy, imported config, temporary override, or schedule window
- a visible difference between `inherit`, `disable`, `clear`, and `pin to none`
- previewable defaults changes that say which existing subjects are still inheriting and which are pinned out
- receipts proving when a subject was intentionally pinned away from inheritance or intentionally returned to it

A narrower comparison helps here too. Syncthing's config API explicitly exposes defaults objects such as `/rest/config/defaults/folder` and `/rest/config/defaults/device`, which does not solve every usability problem but does validate the idea that defaults themselves should be first-class API state instead of settings-page folklore.



### Requirement 44 — effective policy, inheritance, and reset semantics must be one explicit contract

If the operator still has to combine global preferences, per-share preferences, power-user keys, startup config, surface-specific gaps, and manual-reset folklore to answer “why is this value in force here, and what would change if I altered the default?”, the product has not actually exposed its policy contract.

AnonSync should instead publish one public effective-policy model with explicit defaults profiles, explicit policy bindings, per-field origin, explicit `inherit` versus `pin` versus `disable` semantics, previewable defaults changes for inheriting subjects, and durable policy receipts that prove later why the value changed.

### 16i) Diagnostics and supportability still depend too much on storage-path lore, hidden toggles, and manual evidence ritual

Resilio's current docs make this seam unusually visible.
`Collecting debug logs manually` and `Collecting debug logs automatically` still tell the operator to enable debug logging in advanced settings, use a special tray gesture, or create `debug.txt` containing `FFFFFFFF` in the storage folder, then reproduce the issue for a while and attach or send the resulting logs.
`Sync Storage folder` then explains that the very folder containing configuration, auxiliary settings, databases, and logs varies by desktop, config-mode, and service-profile context.
`Collecting crash reports, mini-dumps and core dumps` separately adds OS-specific dump paths and manual crash-collection steps.
The `Send info to Support team` section groups iperf, log-size tuning, debug logs, and crash/core dump collection as separate support rituals.
Even the support posture is revealing: the docs say direct technical support is available only for Business customers, and for Sync v3 direct technical support is not available.

That combination is useful support knowledge.
It is not one durable diagnostic-evidence contract.
The operator still has to reconstruct one answer from several disconnected ideas:

- what problem or incident is actually being investigated
- which debug depth is active and whether it will expire
- where logs, configs, databases, and dumps live under the current service/profile/storage-root posture
- what evidence classes were collected versus intentionally omitted
- what secrets, peer identifiers, paths, or addresses were redacted before anything left the machine
- what proof remains later that evidence was sealed, exported, or destroyed

AnonSync should not clone that shape.
A serious control surface should instead publish one diagnostic-evidence model with:

- explicit incident objects that own troubleshooting scope and requested evidence classes
- explicit temporary diagnostic-depth changes with receipts and expiry
- explicit evidence bundles with visible collection scope, redaction posture, sensitivity findings, and seal/export state
- explicit evidence receipts that prove later what was collected, shared, or destroyed


### Requirement 45 — diagnostics and supportability must be one explicit incident/evidence/redaction contract

If the operator still has to combine hidden storage paths, manual debug toggles, crash-dump rituals, event scraping, and support-form instructions to answer “what evidence did we collect for this problem, at what depth, with what redaction, and what actually left the machine?”, the product has not actually exposed its diagnostic contract.

AnonSync should instead publish one public diagnostic model with explicit incidents, explicit temporary diagnostic-depth changes, explicit evidence bundles, explicit redaction profiles, and durable evidence receipts that prove collection, sealing, export, and destruction.

### 16j) Temporary operator intent still depends too much on sticky settings edits and cleanup memory

Resilio's current docs still expose a scattered temporary-exception story.
`Can I force Sync to do local network (LAN) syncing only...` tells the operator to disable tracker/relay, then clear cached global endpoint state by setting peer-expiration to `0`, restarting, and setting it back afterward.
`Sync Preferences` and `Running Sync on schedule` then split runtime control again between scheduler cells, bandwidth limits, and a separate `rate_limit_local_peers` power-user setting when LAN should obey the same cap.
`How can I improve data transfer/sync speed?` adds still more temporary speed ritual through predefined hosts, port-forwarding, and `lan_encrypt_data` changes.
The diagnostics docs repeat the same pattern: enable debug logging in advanced settings or via `debug.txt`, reproduce the issue, then remember to clean up later.

That is not one trustworthy temporary-exception contract.
The operator still has to reconstruct several things from scattered docs and cleanup memory:

- what durable baseline existed before the exception
- which exact effect is active now versus merely requested originally
- whether the exception ends by time, byte budget, manual cancellation, or “remember to set it back later”
- whether two temporary changes overlap in surprising ways
- what proof remains later that the exception was renewed, expired, exhausted, or converted into durable policy

AnonSync should not clone that shape.
A serious control surface should instead publish one override-lease model with:

- shared lease grammar across route, activity, diagnostics, access, and other temporary exception families
- explicit baseline-versus-effective comparison
- explicit expiry or exhaustion conditions with receipts
- explicit no-expiry acknowledgement when an operator intentionally keeps a risky exception alive
- explicit conversion-to-durable-policy actions instead of silent baseline mutation


### Requirement 46 — temporary exceptions must share one visible lease lifecycle

If the operator still has to combine scheduler folklore, power-user keys, config-file edits, route-specific exceptions, debug toggles, and remembered cleanup steps to answer “is this risky posture temporary, what baseline did it mask, and when does it end?”, the product has not actually exposed its exception contract.

AnonSync should instead publish one public override-lease model with explicit family, scope, baseline/effective comparison, expiry or exhaustion semantics, no-expiry acknowledgement, lease-conflict explanation, and durable override receipts for create/renew/expire/cancel/convert actions.

### 16k) Linked-device convenience still collapses membership, visibility, owner power, and approval reach

Resilio's current docs are still unusually candid about how much authority is hidden inside the linked-device convenience story.
`Sync Private Identity & Linking My Devices` says linked devices automatically share one folder list, that all folders become visible and accessible on all linked devices, and that a remote user can optionally approve all of your linked devices for future sharing after approving one.
`User Management` separately says that when data is shared across your own devices linked to one identity, all of those devices act as Owners.
`Sync functionality in detail` adds that you can approve new peers from any linked device where the folder is already active, while `Folder Types and Management` says removing a disconnected folder removes it from all linked devices.
The same linking guide warns that mixed v2/v3 linked constellations can conflict on licensing and cost access to UI or share configuration.

That is powerful convenience, but it is not one trustworthy authority model.
The operator still has to reconstruct several separate truths from scattered docs:

- whether a member merely sees a share or also mutates it
- whether owner-like re-share power came from one share, one class of member, or ambient same-identity status
- whether one approval widened only to this device or to the whole personal constellation
- whether a disconnect/remove action is local, per-share, or constellation-wide
- whether a mixed-version or mixed-capability constellation is still safe enough to treat as one convenience set

AnonSync should not clone that shape.
A serious control surface should instead publish one personal-constellation and authority-domain model with:

- first-class constellation records and per-member classes
- explicit default visibility posture per member
- explicit share-scoped authority-domain views that compare mutate/re-share/approve/succeed powers across members
- explicit approval-scope limits for cross-member convenience
- explicit constellation receipts for membership, class, visibility, and scope changes


### 16l) Exit and decommission still depend too much on overloaded remove and uninstall ritual

Resilio's current docs still spread one operator question across several different articles:

- clear offline device hides it from the list, but does not unlink it, and it will reappear if it comes back online
- unlink from identity is local-only and cannot remotely unlink other devices
- disconnect folder is local-ish and may remove placeholders, while reconnect may propose a new path or create a duplicate directory
- remove folder affects linked devices, but the same folder may still live on other remote devices not linked to the same identity
- uninstall guidance says to unlink identity and remove remaining Standard shares first or the old instance will simply remain visible as offline elsewhere, and hidden `.sync/Archive` data still needs manual cleanup
- stolen-device guidance escalates to backup, remove shares, unlink, delete storage state, reinstall, regenerate identity, and reshare

That is not one trustworthy exit model. It is a family of adjacent rituals.
AnonSync should expose one explicit exit contract that says:

- what authority ended
- what visibility/publication ended
- what local bytes or hidden history remained
- what continuity or recovery posture was intentionally preserved
- what residue still remains remotely, offline, or time-delayed after apply

### Requirement 48 — exit intent, continuity, and residue must be one explicit contract

A privacy-respecting sync product should not be more honest about admission than it is about departure.
Hide, detach, revoke, decommission, replace, and erase are different state transitions with different trust, storage, disclosure, and continuity consequences.
The public interface should make that unavoidable.


### 16m) Linux/WebUI/config-mode parity is still too weak for safety-critical exit controls

Resilio's current docs make one more seam unusually explicit.
`Guide to Linux, and Sync peculiarities` says Linux uses the WebUI rather than a native GUI.
`Configuring WebUI` says ordinary Linux workstation settings can be changed in the WebUI, while `Running Sync in configuration mode` says config mode can create only Standard folders and that if shared folders are declared in the config file the WebUI is disabled.
`Power user preferences` then adds that `disable_remove_from_all_devices` is ignored in Linux WebUI.
Taken together, that means a Linux-first or config-heavy operator cannot safely assume that the strongest destructive-action guardrails and share semantics are uniformly available across surfaces.

That is not just a documentation annoyance.
It is a product-architecture warning.
If safety-critical behavior differs by channel, then “the interface” is not one trustworthy contract.
AnonSync should not clone that shape.
A Linux-first system especially should instead guarantee that device retirement, share detachment, decommission, and local-residue cleanup all compile to the same daemon model and the same mandatory review grammar regardless of whether the operator entered from GUI, WebUI, TUI, or CLI.

### Requirement 49 — safety-critical destructive controls must have channel parity

If a dangerous action becomes weaker, more ambiguous, or less reviewable on Linux/WebUI/config-heavy deployments, then the product does not really have a public safety contract.
AnonSync should require one shared exit-review model across surfaces, with only layout changing — never semantics, scope truth, or residue truth.

### Requirement 50 — personal-device convenience must use one explicit constellation and authority-domain contract

If the operator still has to infer from linked-device folklore whether “my devices” means visible here, writable here, owner-like here, approvable from here, or removable everywhere, the product has not actually exposed its authority boundary.

AnonSync should instead publish one public constellation model with explicit membership, member class, visibility defaults, approval-scope limits, share-scoped authority-domain explanation, mixed-constellation compatibility findings, and durable constellation receipts for membership/scope changes.



### 16n) Compromise response still depends too much on unlink, uninstall, regenerate, and reshare ritual

Resilio's current docs make one more trust seam unusually explicit.

`If your device is stolen` recommends a sequence that runs through backup, remove shares, unlink devices from the current identity, remove synced data from storage, reinstall Sync, regenerate identity, relink devices, and reshare folders.
`How to clear offline devices?` separately says clearing only hides the device from view and that if it comes back online it will reappear and continue as before.
`Sync Private Identity & Linking My Devices` adds that you cannot remotely unlink other devices.
`How to uninstall Sync?` then adds more cleanup ritual: remove settings, manually remove service-storage folders, and remember that hidden `.sync/Archive` bytes are not removed automatically.

That is not one trustworthy compromise model.
It is several adjacent rituals that an operator has to mentally compose while under stress.

The operator still has to reconstruct several separate truths from scattered docs:

- whether the system is merely hiding an offline row or actually revoking future authority
- whether live sessions, grants, offers, or route publication are frozen now or only after several later steps
- whether identity rotation is required or merely suggested
- whether a successor can preserve continuity safely or whether the correct action is a clean break
- what residue still remains locally, remotely, or time-delayed even after the urgent steps complete

AnonSync should not clone that shape.
A serious control surface should instead publish one compromise-containment and trust-rotation model with:

- one explicit incident-grade case object for suspected or confirmed compromise
- one fixed review grammar for freeze-now, revoke-now, rotate-later, and successor-continuity decisions
- explicit residue findings for offline-peer memory, provider TTLs, preserved local bytes, and still-valid portable artifacts
- explicit receipts proving what was contained immediately versus what still needed observation or follow-up
- explicit separation between cosmetic device-list cleanup and real trust retirement


### Requirement 51 — compromise containment and trust rotation must share one incident-grade contract

If the operator still has to combine hide-row cleanup, local-only unlink, uninstall notes, identity-regeneration ritual, access-token cleanup, and remembered reshare steps to answer “what did we freeze, what did we revoke, what did we rotate, and what still remains exposed?”, the product has not actually exposed its compromise contract.

AnonSync should instead publish one public incident-grade model with explicit trigger scope, explicit immediate freeze effects, explicit revocation and rotation work, explicit continuity-versus-clean-break posture, explicit residue/observation findings, and durable containment receipts that preserve the difference between suspicion, action taken, and unresolved residue.


### 16o) Dormant-peer return still depends too much on peer counters, clock warnings, and archive aftermath

Resilio's current docs make one more operator seam unusually explicit.

`How to clear offline devices?` says clearing only hides an offline device and that if it ever comes back online it will reappear and continue sharing as before.
`Sync Main View (Desktop)` says peer counts include offline peers and that a peer is only disconnected from the folder after 7 days offline, with the threshold configurable in power-user settings.
`What if several people make changes to the same file?` says that if a peer edits while offline and later comes online, its version can take priority over versions proposed earlier by online peers, with overwritten versions then moved to Archive.
`"Time difference" error` adds that file recency depends on modification-time comparison converted to GMT and that peers more than 600 seconds apart trigger warnings; mobile can even show an empty list instead of files.
`Cannot download files / ... no source peers online for too long time` then adds a separate “ghost file” condition where announcement outlived real source availability.

That is not one trustworthy re-entry model.
It is a family of adjacent status clues and after-the-fact consequences.
The operator still has to reconstruct several separate truths from scattered docs:

- whether the returning subject is merely visible again or is resuming writable authority
- whether chronology can be trusted enough to accept its version claims
- whether the subject's announced bytes are still materially obtainable or already ghosted
- whether this looks like harmless dormancy, suspicious reappearance, or a successor/cutover problem in disguise
- whether the safest next action is resume, quarantine, merge review, or containment review

AnonSync should not clone that shape.
A serious control surface should instead publish one dormant-peer re-entry and stale-state review model with:

- one explicit re-entry case object for long-offline or chronology-uncertain return
- one fixed review grammar for dormancy, chronology confidence, authority posture, divergence/source reality, and admissible actions
- explicit escalation paths from benign re-entry into compromise or successor-cutover review when evidence warrants it
- explicit receipts proving whether the subject resumed, stayed quarantined, was downgraded to read-only observation, or was diverted into another workflow


### Requirement 52 — dormant-peer re-entry and stale-state replay must share one reviewed contract

If the operator still has to combine hidden-row cleanup, offline-peer counters, archive history, invalid-time warnings, and ghost-file/source-absence messages to answer “is this returning subject safe to trust, safe to resume as writer, or actually something I must quarantine or escalate?”, the product has not actually exposed its re-entry contract.

AnonSync should instead publish one public re-entry model with explicit dormancy facts, explicit chronology confidence, explicit re-entry authority posture, explicit divergence/source-availability findings, explicit admissible next actions, and durable re-entry receipts that preserve the difference between harmless return, guarded resume, suspicious reappearance, and blocked replay.


### 16p) Destructive replay still depends too much on pause folklore, optional archive, and overwrite ritual

Resilio's current docs make one more operator seam unusually explicit.

`How to pause syncing` says pause stops only bits downloads/uploads, while deletions still sync and new files are still rescanned and indexed.
`Folder Preferences` says that when a Read & Write peer changes or deletes a file, the same change or deletion is applied on other peers, with old copies moved to `.sync/Archive` by default for 30 days — but that Archive can be disabled, and then deleted files are no longer copied there.
The same preferences page says `Overwrite any changed files` for Read-Only folders is potentially destructive and disabled when Read-only shares use Selective Sync.
`Is one-way synchronization possible?` adds more mode-dependent behavior: in read-only sync, deleted files may be restored, edited files reverted, renamed files can be re-downloaded under the older name, while added files stay local and unsynced.

That is not one trustworthy destructive-replay model.
It is a mix of transfer pause, retention preference, permission/mode quirks, and after-the-fact recovery behavior.

The operator still has to reconstruct several separate truths from scattered docs:

- whether the current pause or maintenance posture actually prevents destructive propagation or only delays bytes
- how much local state would be deleted, reverted, or re-downloaded if replay proceeds now
- whether any recoverable copy still exists locally and for how long
- whether this is routine mirror maintenance or a suspicious delete/overwrite wave that should escalate
- whether the safest next step is freeze, guarded apply, read-only downgrade, stronger witness collection, or compromise handling

AnonSync should not clone that shape.
A serious control surface should instead publish one destructive-replay and delete-wave review model with:

- one explicit destructive-replay case object for high-signal remote delete, overwrite, or revert waves
- one fixed review grammar for trigger/scope, destructive effect summary, preservation/recoverability, authority/source confidence, admissible actions, and receipt promise
- explicit separation between transfer pause, preservation posture, and destructive consent
- explicit escalation paths into compromise or stale-return review when source confidence is weak or behavior looks suspicious
- explicit receipts proving what replay scope was accepted, frozen, narrowed, or diverted


### Requirement 53 — destructive replay and delete-wave consent must share one reviewed contract

If the operator still has to combine pause semantics, archive toggles, read-only overwrite checkboxes, selective-sync caveats, and manual restore lore to answer “what exactly will be deleted or replaced if I let sync continue from here?”, the product has not actually exposed its destructive-replay contract.

AnonSync should instead publish one public destructive-replay model with explicit trigger scope, explicit destructive-effect summary, explicit preservation/recoverability findings, explicit authority/source-confidence posture, explicit admissible actions, and durable destructive-replay receipts that preserve the difference between ordinary progress, guarded destructive consent, frozen propagation, and escalated suspicion.

### 16q) Conflict adjudication still depends too much on filename folklore, manual cleanup dance, and hidden path toggles

Resilio's current docs make one more operator seam unusually explicit.

`Conflict files in Sync` says operators must not simply delete a `.Conflict` file or folder because doing so deletes the corresponding real file or folder on the remote peer.
The same article says safe removal still involves finding a healthy file, moving it outside the syncing tree, deleting the conflict-named entries, and copying the healthy file back.
It also shows conflict suffixes proliferating when folders are re-added or conflict files are renamed into fresh collisions.
`Power user preferences` adds more path-dependent semantics: `fix_conflicting_paths` can suppress conflict-file creation while leaving the share unsynced and “unpredictable”, while `normalize_unicode_paths`, `ignore_symlinks`, and `sync_max_time_diff` all shape whether a path problem is normalized, skipped, delayed, or broken.

That is not one trustworthy conflict-adjudication model.
It is a mixture of suffix names, manual cleanup choreography, and advanced path/clock switches.

The operator still has to reconstruct several separate truths from scattered docs:

- whether the real class is content concurrency, delete-vs-modify, case/unicode/path collision, or another compatibility mismatch
- which candidate can safely win on this target and which candidate is only locally recoverable
- whether resolution is local-only, replicated, or actually blocked by portability/fidelity risk
- what will happen to the loser after apply and whether a preserved copy is the last easy recovery path
- whether the safest next action is resolve now, defer, preserve-both, portability repair, stale-return review, or compromise review

AnonSync should not clone that shape.
A serious control surface should instead publish one conflict-adjudication and path-collision review model with:

- one explicit review grammar for trigger/class, candidates/authority, compatibility reality, loser handling/scope, admissible actions, and receipt promise
- explicit separation between conflict naming artifact and actual semantic class
- explicit loser-handling truth before resolution instead of after-the-fact rollback archaeology
- explicit escalation paths into filesystem portability, stale-return, or compromise review when the safest next step is not ordinary adjudication
- explicit receipts proving which candidate won, which candidate lost, what scope changed, and what preservation still survived


### Requirement 54 — conflict adjudication and path-collision resolution must share one reviewed contract

If the operator still has to combine `.Conflict` suffixes, “safe remove” dance, re-add/reindex folklore, and power-user path toggles to answer “what exactly is conflicting here, which candidate is safe to pick, and what happens to the loser?”, the product has not actually exposed its conflict-resolution contract.

AnonSync should instead publish one public conflict-adjudication model with explicit semantic class, explicit candidate and authority posture, explicit compatibility reality, explicit loser-handling/scope truth, explicit admissible next actions, and durable conflict receipts that preserve the difference between local cleanup, replicated winner selection, deferred review, and diverted portability or trust workflows.

### 16r) Same-host local derivation still hides too much topology, lifecycle, and target-tier meaning behind one convenience action

Resilio's current docs make one more seam unusually explicit.

`Sharing a folder locally` says one share can be synced to other folders on the same computer, including USB and network paths, and that the local share connects only to one peer: self.
The same article warns not to choose a subdirectory or parent of the source because that creates syncing loops.
It also says local shares inherit source permissions, cannot receive `Owner`, can require remove-and-re-share ritual to change access in Advanced shares, are downgraded automatically when the source permission is downgraded, are removed when the source is disconnected or removed, and do not automatically reconnect when the source later returns.
The article further says local shares cannot be locally re-shared again, may fan one source out to several local targets, and only get data from the source share—so if the source only has placeholders, the local share will not have the file either.
`Can I move or rename a syncing folder?` sharpens the point by showing that even ordinary path continuity is still bounded by platform and topology limits.

That is not one trustworthy local-derivation model.
It is a mixture of path picking, loop warnings, inherited permissions, source-coupled lifecycle, and target-tier convenience.

The operator still has to reconstruct several separate truths from scattered docs:

- whether the action is really a local mirror, cache branch, export-like derivative, or blocked loop
- whether the target is strong local storage, removable media, or a warning-tier network target
- whether the derivative can write back, only narrow source authority, or will silently lose mutability if source permission changes
- whether source detach/removal means the derivative persists, freezes, or disappears from the product
- whether placeholder-heavy or partial source state weakens the target's byte-availability promise
- whether fanout across multiple local targets changes the safety story enough to require explicit review

AnonSync should not clone that shape.
A serious control surface should instead publish one local-derivation and self-edge review model with:

- one explicit review grammar for source/target, topology/loop risk, authority+lifecycle coupling, materialization+target-tier reality, admissible derivations, and receipt promise
- explicit separation between same-host derivation, remote adoption, and mere export/copy semantics
- explicit target-tier truth so USB/network-reviewed targets cannot masquerade as ordinary local-native mounts
- explicit lifecycle coupling truth before apply instead of remove/re-share or reconnect folklore after the fact
- explicit receipts proving what source/target relationship was created, what authority it inherited, and what source changes later remain coupled to it

### Requirement 55 — same-host derivation and self-edge topology must share one reviewed contract

If the operator still has to combine `sync local folders`, parent/child loop warnings, inherited-permission caveats, source-removal side effects, and placeholder dependence to answer “what exactly am I creating on this machine, is the topology safe, and what happens when the source changes?”, the product has not actually exposed its local-derivation contract.

AnonSync should instead publish one public local-derivation model with explicit source/target truth, explicit topology and loop-risk posture, explicit authority/lifecycle coupling, explicit materialization and target-tier reality, explicit admissible derivations, and durable derivation receipts that preserve the difference between a safe local derivative, a narrowed cache/export branch, and a blocked self-edge.


### 16s) Live authority mutation still depends too much on folder class, owner folklore, and remove/re-share ritual

Resilio's current docs make one more seam unusually explicit.

`What's the difference between Standard and Advanced folders?` says only Advanced folders support on-the-fly permission changes, only Owners can share Advanced folders with others, Standard folders can be re-shared by any peer who has the key it has, and Standard folders cannot be upgraded in place—they must be removed and re-added as Advanced.
`User Management` says live permission changes among Read Only, Read & Write, and Owner are available only for Advanced folders, linked same-identity devices all act as Owners, and `Disconnect` revokes future access while leaving already-synced files in place.
`Sharing a folder locally` says a local share cannot receive `Owner`, changing local-share access for Advanced shares requires remove-and-re-share ritual, and source permission downgrades automatically flow down to the derivative.
`Running Sync in configuration mode` says config mode can set up only Standard folders, and if shared folders are set in the config file the WebUI is disabled.

That is not one trustworthy authority-mutation model.
It is a mixture of folder class, share dialog, owner status, linked-device convenience, local-share exception, disconnect semantics, and surface loss.

The operator still has to reconstruct several separate truths from scattered docs:

- whether a requested access change is a live mutation, a revoke-plus-byte-preserve action, or a remove-and-re-share migration
- whether the change widens only write authority, also widens re-share or revoke reach, or quietly broadens to owner-equivalent power through same-identity linkage
- whether local derivatives, linked members, or approval memory will narrow automatically, remain as-is, or need separate follow-up review
- whether the current surface can actually express the desired authority state or forces a weaker folder class or config-only representation
- whether `Disconnect` means bytes remain, future updates stop, or authority was truly retracted across all relevant edges
- whether the right next step is widen, narrow, freeze, revoke, rebind, or migrate authority substrate entirely

AnonSync should not clone that shape.
A serious control surface should instead publish one authority-mutation and grant-boundary review model with:

- one explicit review grammar for trigger/current authority, desired boundary delta, active subject fallout, authority-substrate effects, admissible mutations, and receipt promise
- explicit separation between write authority, delegation/share reach, revoke power, and byte-retention consequences
- explicit local-derivative and linked-member fallout before apply instead of after-the-fact remove/re-share archaeology
- explicit substrate/migration truth when imported or legacy authority representations cannot express the requested state cleanly
- explicit receipts proving what authority changed, what remained unchanged, what follow-up subjects were narrowed or preserved, and what bytes were intentionally left in place


### Requirement 56 — authority mutation and grant-boundary changes must share one reviewed contract

If the operator still has to combine Standard-vs-Advanced folder class, Owner folklore, linked-device owner broadening, local-share re-share caveats, config-mode limits, and `Disconnect` semantics to answer “what exactly is changing here, who gains or loses what authority, and what bytes or dependents remain afterward?”, the product has not actually exposed its access-change contract.

AnonSync should instead publish one public authority-mutation model with explicit current-authority truth, explicit desired boundary delta, explicit active-subject and dependent fallout, explicit authority-substrate/migration effects, explicit admissible mutations, and durable mutation receipts that preserve the difference between narrowing writes, stripping delegation, freezing future access, revoking active grants, and migrating away from a weaker authority substrate.


### 16t) Nested shares, overlap, and topology transitions still hide too much graph meaning behind separate caveats

Resilio's current docs make one more seam unusually explicit.

`Is it possible to share a nested folder separately?` says a parent and child folder can both be shared, but only if both have Read & Write or Owner permissions, both disable Selective Sync, the child is indexed separately in addition to as a subfolder of the parent, and peers with only the parent do not seed peers that only have the child. It also says child edits still propagate onward through the parent share, and that the nesting creates heavy load because the child is indexed and rescanned twice.
`Sharing a folder locally` separately warns not to create a local share in a source subdirectory or parent because that creates syncing loops.
`Can I move or rename a syncing folder?` says rename affects only the local device, Windows and macOS moves are limited to the same drive, Linux moves are limited to within the Sync parent folder, and otherwise the operator falls back to disconnect/reconnect-style path repair.
`Running Sync in configuration mode` adds Linux-only `directory_root_policy`, `dir_whitelist`, and the rule that preconfigured shares disable WebUI entirely.

That is not one trustworthy topology model.
It is a mixture of nested-share exception, double indexing, propagation side effects, local self-edge loop warnings, path continuity limits, and config-root ritual.

The operator still has to reconstruct several separate truths from scattered docs:

- whether two graph subjects are truly disjoint, nested, overlapping, or only apparently separate
- whether changes propagate independently, piggyback through a parent, or require full re-download / rebind behavior after a move
- whether Selective Sync, placeholder behavior, or target/root policy is silently disallowed by the chosen topology
- whether a requested path change is ordinary local rename, reviewed rebind, blocked overlap, or escape from an allowed root
- whether the safest next step is nest intentionally, flatten, rebind, split the graph, or reject as loop risk

AnonSync should not clone that shape.
A serious control surface should instead publish one overlap, containment, and graph-topology review model with:

- one explicit review grammar for trigger/graph subjects, containment+propagation shape, path+root-boundary effects, admissible topology actions, and receipt promise
- explicit separation between nested-share topology, same-host derivation, cross-share move, and root-boundary escape
- explicit propagation-shape truth before apply instead of after-the-fact double-indexing or child-via-parent folklore
- explicit root-boundary and surface-availability truth before apply instead of config-mode path ritual after the fact
- explicit receipts proving which graph relation was accepted, which propagation semantics were expected, what path/root restrictions were reviewed, and what follow-up still remained

### Requirement 57 — overlap, containment, and topology transitions must share one reviewed graph contract

If the operator still has to combine nested-share caveats, parent/child loop warnings, move/reconnect folklore, and config-mode root restrictions to answer “what exactly is the graph relationship here, how will changes propagate, and is this path transition actually safe?”, the product has not actually exposed its topology contract.

AnonSync should instead publish one public topology-review model with explicit graph subjects, explicit containment and propagation shape, explicit path/root-boundary effects, explicit admissible topology actions, and durable topology receipts that preserve the difference between safe nesting, blocked overlap, reviewed rebind, and rejected root escape.

### 16u) Writer contention and quiescence still depend too much on status badges, hidden delay files, and separate SMB caveats

Resilio's current docs make one more seam unusually explicit.

`Locked files` says the status column can show locked files and open their paths, but Sync cannot tell which application actually holds the lock and the operator is pushed toward Process Monitor plus restart ritual.
`Setting Delay Time For Syncing` says Office/AutoDesk/Adobe-style save contention is handled by editing a `FileDelayConfig` JSON file in the storage folder and restarting Sync, with a default delay of 10 seconds.
`Power user preferences` adds `recheck_locked_files_interval` and warns that too-frequent rechecks of many locked files may cause high CPU usage.
`Sync and SMB file shares` says SMB-backed folders may lose immediate notifications and fall back to full rescans unless both sides support SMB 3.0, that broken locks can persist after network or app failure, and that mixed direct access outside Samba can damage files or roll changes back.

That is not one trustworthy contention model.
It is a mixture of lock-status badges, hidden delay JSON, retry tuning, notification downgrade, and mixed-writer caveats.

The operator still has to reconstruct several separate truths from scattered docs:

- whether a path is merely waiting behind an intentional delay profile or is actually blocked by another writer
- whether the present protection is delay-only, retry-only, upload hold, or a stronger freeze that should stop dangerous propagation
- whether freshness is still trustworthy or only periodic-rescan best effort while contested writes continue
- whether the current risk is ordinary slowdown, overwrite/rollback risk, or genuine corruption risk on warning-tier storage
- whether the safest next step is wait, preserve local writes, freeze propagation, or move the workload off a mixed SMB/NAS topology entirely

AnonSync should not clone that shape.
A serious control surface should instead publish one writer-contention and quiescence review model with:

- one explicit review grammar for trigger/scope, writer+lock reality, notification+filesystem posture, quiesce+propagation effects, admissible actions, and receipt promise
- explicit separation between transient burst-save delay, confirmed lock pressure, mixed external-writer risk, and degraded-notification uncertainty
- explicit quiesce truth before apply instead of after-the-fact retry, restart, or hidden-delay folklore
- explicit escalation points into filesystem-fidelity, topology, or destructive-replay review when contention is only a symptom of a larger risk
- explicit receipts proving which contention was reviewed, what coordination action was chosen, what propagation was held back, and what follow-up still remained

### Requirement 58 — writer contention and quiescence must share one reviewed coordination contract

If the operator still has to combine locked-file badges, hidden delay JSON, retry-interval tuning, and SMB mixed-access caveats to answer “who is writing here, what is currently delayed or frozen, and when may safe propagation resume?”, the product has not actually exposed its contention contract.

AnonSync should instead publish one public contention-review model with explicit contested scope, explicit writer and lock reality, explicit notification/filesystem posture, explicit quiesce and propagation effects, explicit admissible actions, and durable contention receipts that preserve the difference between harmless burst-save delay, guarded upload hold, full bidirectional freeze, and escalation because current freshness or mixed-access posture is not honest enough.

### 16v) Capacity fit and scale admission still depend too much on warnings, advanced toggles, and re-add folklore

Resilio's current docs make one more seam unusually explicit.

`Out of memory` says Sync keeps the whole tree of files and folders in memory, needs roughly 1.5–2 KB of RAM per file/folder, and the practical way to reduce RAM is to remove the biggest folders from all peers and add them back so a new database is built.
`Agent run out of system notify watchers` says watcher exhaustion is common on Linux with many files and subdirectories, and once the limit is reached updates are learned only by manual or periodic rescans.
`Some internal tasks are taking time to complete` says hashing, scanning, merging, dedup, reading, and writing may simply be heavy because there are many files or because disk/network are busy.
`My files don't sync` adds more scattered fit clues: UTF-8 filename assumptions, path-length limits, out-of-space conditions, notification loss that may need restart or `touch`, filesystem errors, and a `devices cannot merge folder trees` condition that often ends in remove-and-re-add ritual.
`Power user preferences` piles on more scale-sensitive knobs: `prioritize_initial_indexing` for huge folders with millions of files, `parallel_indexing` that may drive heavy CPU and disk usage, `enable_file_system_notifications`, and free-space reserve settings.

That is not one trustworthy host-fit model.
It is a mixture of warnings, advanced preferences, degraded freshness hints, and re-add folklore.

The operator still has to reconstruct several separate truths from scattered docs:

- whether a host is comfortable, guarded, or simply not honest enough for the requested subject and mode
- whether the real pressure is RAM, watchers, indexing cost, free space, or path portability
- whether proceeding should mean full adoption, selective/materialized narrowing, metadata-only visibility, subtree narrowing, reclaim-first, or outright rejection on this host
- whether change detection will stay continuous or degrade to periodic rescans from the start
- whether the safest next step is host-fit review, topology/fidelity review, or support ritual instead of `Add folder` or `Connect`

AnonSync should not clone that shape.
A serious control surface should instead publish one capacity-fit and scale-admission review model with:

- one explicit review grammar for subject+intended role, local capacity+index cost, freshness+notification posture, portability+path blockers, admissible modes, and receipt promise
- explicit separation between comfortable scale, guarded host fit, degraded-freshness admission, reclaim-first posture, and blocked-on-this-host outcomes
- explicit host-fit truth before apply instead of after-the-fact out-of-memory, watcher, or re-add folklore
- explicit handoff into topology, fidelity, or storage review when scale pressure is only part of the real problem
- explicit receipts proving which host-fit facts were reviewed, what local mode was accepted, what degraded posture was knowingly tolerated, and what follow-up still remained

### Requirement 59 — capacity fit and scale admission must share one reviewed host-fit contract

If the operator still has to combine out-of-memory notes, watcher warnings, generic internal-task slowdowns, huge-folder indexing toggles, and re-add folklore to answer “can this machine honestly carry this subject and under what local mode?”, the product has not actually exposed its host-fit contract.

AnonSync should instead publish one public capacity-fit review model with explicit subject role, explicit local capacity/index cost, explicit freshness and notification posture, explicit portability/path blockers, explicit admissible modes, and durable fit receipts that preserve the difference between comfortable adoption, guarded narrowing, reclaim-first staging, and honest rejection on the current host.


### 16w) First control entry and bring-up still depend too much on install mode, startup flags, and activation ritual

Resilio's current docs make one more seam unusually explicit.

`Important before updating to Resilio Sync 3.0.0`, `Licensing in Resilio Sync 3.0`, and the v3 changelog show that edition family, activation model, and supported architecture materially affect what kind of install or update is even honest.
`Running Sync in configuration mode` and `Guide to Linux, and Sync peculiarities` then show that headless/server bring-up depends on startup flags and config-file fields such as `--storage`, `--identity`, `--license`, and `--webui.listen`, with localhost default, LAN exposure via `0.0.0.0` or specific interfaces, and even shutdown risk if the chosen interface is not actually present.
`How to apply license key and share license seats` adds still more first-entry ritual: on headless systems identity creation and license application are separate steps.
`Cloning Sync` separately says plain copying an instance is unsupported.

That is useful support knowledge.
It is not one trustworthy bring-up contract.

The operator still has to reconstruct several separate truths from scattered docs:

- whether startup is creating fresh state, reopening known durable state, importing/recovering state, or accidentally opening the wrong control universe
- whether identity posture is new, retained, successor-sensitive, or only inspectable pending stronger review
- what control endpoint is about to exist, where it listens, and who can reach it
- whether the case is ordinary local-only startup or a continuity-sensitive / exposure-sensitive decision that deserves review before the daemon becomes ordinary background fact
- whether the honest next step is verify root, narrow exposure, choose another host role, or stop instead of simply `Start` or `Open WebUI`

AnonSync should not clone that shape.
A serious control surface should instead publish one bring-up and control-entry review model with:

- one explicit review grammar for host role+runtime target, state+continuity choice, identity+relationship posture, control+network posture, blockers+bootstrap dependencies, and receipt promise
- explicit separation between fresh local-only start, attach existing state, recover/import state, successor-sensitive continuity, and blocked bring-up
- explicit first-control truth before apply instead of after-the-fact bind-address, config-file, or activation folklore
- explicit handoff into state-root, recovery, release, or control-access review when startup ambiguity is only part of the real problem
- explicit receipts proving which continuity and exposure facts were reviewed, what first-entry posture was accepted, and what follow-up still remained

### Requirement 60 — bring-up and first control entry must share one reviewed contract

If the operator still has to combine activation notes, startup flags, bind-address lore, storage-path memory, and unsupported clone warnings to answer “what exactly am I opening, under which continuity story, and how is control exposed?”, the product has not actually exposed its bring-up contract.

AnonSync should instead publish one public bring-up review model with explicit host role, explicit state/continuity choice, explicit identity posture, explicit control and network posture, explicit blockers/dependencies, and durable bring-up receipts that preserve the difference between fresh local-only start, attach known root, recover/import, successor-sensitive continuity, and honest stop-before-open.

### 16x) Browser-mediated control is still too dependent on client quirks, trust-bypass ritual, and stateful repair folklore

Resilio's current docs expose one more interface seam that matters especially for Linux-first operation.

`Configuring WebUI` says WebUI is the default and only interface on Linux-based machines and the default UI for Windows service installs, that share links do not open directly through WebUI, and that link intake should instead happen by manual paste through `+ > Enter a key or link`.
`There’s no Share button in Web UI…` adds that some browsers or ad blockers can make the `Share` button disappear.
`Browser warning "Your connection is not private"` then normalizes self-signed trust bypass through click-through, HSTS clearing, or even typing `thisisunsafe`.
`How do I reset my WebUI password?` adds an even sharper repair seam: one reset path deletes `settings.dat` and `settings.dat.old`, resets global preferences, and duplicates the device in `My devices`, while another path injects credentials through config mode to avoid those side effects.

That is useful support knowledge.
It is not one trustworthy control-integrity contract.

The operator still has to reconstruct several separate truths from scattered docs:

- whether a missing control is truly forbidden or just missing in the current browser/client posture
- whether browser trust is degraded because of certificate posture, HSTS/browser memory, or a real endpoint mismatch
- which control actions still have a safe fallback path outside the current browser session
- whether regaining control authority changes only credentials or also resets preferences, duplicates device records, or mutates other durable state
- whether Linux/headless administration is actually browser-dependent in practice even when the product nominally supports CLI/config routes

AnonSync should not clone that shape.
A serious control surface should instead publish one browser-independent control-integrity and auth-repair model with:

- one explicit capability manifest for high-signal actions and the channels that may render them honestly
- one explicit integrity-report model for browser incompatibility, content blocking, self-signed distrust, hostcheck mismatch, and session-expiry confusion
- one explicit auth-repair case model with bounded collateral effect and durable receipts
- explicit fallback from browser/workbench to CLI/TUI/API without changing the action's meaning
- explicit separation between control repair and broader bring-up/state-root transitions when the fix would actually touch durable state

### Requirement 61 — browser-mediated control must degrade into explicit capability, integrity, and repair state

If the operator still has to combine disappearing buttons, manual link-paste folklore, unsafe browser overrides, and storage-folder credential surgery to answer “what action is really unavailable here, why, and can I regain control without changing anything else?”, the product has not actually exposed its control-integrity contract.

AnonSync should instead publish one public model with explicit control-capability manifests, explicit control-integrity reports, explicit auth-repair cases, browser-independent fallback channels, and durable repair receipts that preserve the difference between client degradation, trust/bootstrap failure, session expiry, true policy denial, and broader reviewed state transition.

### 16y) Visible control sessions still do not amount to one reviewed mutation-authority contract

A final Resilio pass exposes one more Linux-first interface seam that matters.

`Configuring WebUI` says WebUI is the default and only interface on Linux-based machines, that workstation passwords are optional, that browser cookies last only for the browser session, and that login/password can be defined in config and later stored in Sync settings.
`Guide to Linux, and Sync peculiarities` says Linux/headless startup depends on `--storage`, `--identity`, and `--webui.listen`, with loopback default unless the operator deliberately widens bind posture.
`Sync Service Troubleshooting on Windows` adds an even sharper discontinuity: switching the service to `Local System` opens a different storage folder, the old folders are gone from view, and the operator must re-add and re-share them.

That is useful support knowledge.
It is not one trustworthy mutation-authority contract.

The operator still has to reconstruct several separate truths from scattered docs:

- whether a currently visible browser/workbench session is only good enough to inspect or is really trusted for high-signal apply
- whether remembered password acceptance or config-injected credentials amount to fresh mutation proof or merely reopened inspectability
- whether the active control universe changed because service user or storage root changed under the same apparent product
- whether a dangerous mutation should be blocked on renewed authority, broader review, or honest stop

AnonSync should not clone that shape.
A serious control surface should instead publish one reviewed mutation-gate model with:

- one explicit gate result telling whether the attempted mutation is ready, grant-required, re-auth-required, broader-review-required, or blocked
- one explicit short-lived mutation-grant object bound to action family, subject scope, endpoint, channel, active state root, freshness, and receipt promise
- explicit separation between ordinary inspect sessions and reviewed mutation authority
- explicit invalidation when endpoint, state root, or integrity posture drifts
- explicit hand-off from generic elevation into broader review families when the requested change is really bring-up, compromise, destructive replay, or successor work

### Requirement 62 — non-trivial mutation must have an explicit reviewed authority object, not ambient browser/session continuity

If the operator still has to combine open browser tabs, remembered passwords, config-file credential tricks, service-account/storage-root accidents, and generic confirm dialogs to answer “am I actually authorized to apply this mutation right now, for this subject, through this endpoint, under this state root?”, the product has not actually exposed its mutation-authority contract.

AnonSync should instead publish one public model with explicit mutation-gate results, explicit short-lived mutation grants, explicit channel/endpoint/state-root binding, explicit invalidation on drift, and durable receipts that preserve the difference between inspectability, ordinary session continuity, explicit reviewed elevation, and broader review-required state transitions.

### 16z) Host-local target ownership still depends too much on hidden marker state, duplicate-instance caveats, and delete-and-re-add ritual

Another Resilio pass exposes one more same-host interface seam that matters.

`Service files missing / Cannot identify destination folder` says every synced folder gets a hidden `.sync` folder whose ID is critical for synchronization, that deleting or corrupting it suspends sync, and that the same error can appear if two Sync instances use the same folder on one computer or on one external disk.
The same article says the recovery path is to make sure nothing important remains in archive, delete `.sync`, remove the share, and add it back.
`Selected folder is already added to Sync` says the same `.sync/ID` marker is how Sync decides a folder is already present on one device.
`Cloning Sync` separately says plain-copy cloning of an instance is unsupported.

That is useful support knowledge.
It is not one trustworthy host-local custody contract.

The operator still has to reconstruct several separate truths from scattered docs:

- whether a discovered target belongs to the currently active local state universe, a different service/profile/root, or some foreign/stale lineage
- whether an external disk or moved path is being treated as same-lineage continuation, unsupported clone instinct, or active multi-instance collision
- whether the safe next step is reuse, attach, successor claim, inspect-only preservation, or hard stop
- whether deleting hidden internal state would merely clean residue or destroy the last straightforward evidence of prior ownership

AnonSync should not clone that shape.
A serious operator surface should instead publish one reviewed target-custody model with:

- one explicit target-custody record telling whether a path is empty, same-lineage, foreign-managed, stale-managed, degraded, or ambiguous
- one explicit binding-collision case describing why a requested claim is guarded, blocked, or continuity-sensitive
- explicit lineage and state-root/service-profile references when ownership can be proven
- explicit preservation requirements before marker rewrite or cleanup
- explicit custody receipts proving how a path was claimed, blocked, or cleaned up

### Requirement 63 — non-trivial path claims must have an explicit reviewed target-custody contract, not hidden-marker folklore

If the operator still has to combine non-empty-path prompts, hidden `.sync` folders, `already added` checks, same-host collision caveats, external-disk memory, and delete-and-re-add ritual to answer “who already owns this target, under which continuity story, and what is the safe next step?”, the product has not actually exposed its host-local custody contract.

AnonSync should instead publish one public model with explicit target-custody records, explicit binding-collision cases, explicit lineage/state-root references, explicit preservation-before-cleanup posture, and durable custody receipts that preserve the difference between ordinary same-lineage continuation, reviewed successor/re-home work, foreign-marker inspection, and blocked local collision.

### 16aa) Safety-critical control meaning still drifts too much by channel

One more Resilio pass exposes a distinct interface seam that matters especially for Linux-first operation.

`Guide to Linux, and Sync peculiarities` says Linux has no GUI and that share-link intake and license activation happen through `Enter a key or link` in the WebUI.
`Configuring WebUI` says WebUI is the default and only interface on Linux-based machines.
`Running Sync in configuration mode` says config mode can create only Standard folders and that if shared folders are specified in config the WebUI is disabled.
`Sync doesn't start when opening Link in browser` says opening a share link is impossible in WebUI and must instead be handled by manual paste.
`There's no Share button in Web UI…` says browser incompatibility or ad blockers can make the Share button disappear.
`Power user preferences` then adds that `disable_remove_from_all_devices` is ignored in Linux WebUI.

That combination is revealing.
The product does not merely have browser quirks.
The meaning of some control actions still depends too much on which channel the operator happened to use:

- whether the action is visible at all
- whether the strongest safety guard exists in this channel
- whether the channel can perform the same folder/authority class or only a weaker substitute
- whether the operator can continue the same review in another client or must reconstruct the action from lore

AnonSync should not clone that shape.
A serious control surface should instead publish one surface-capability and channel-parity model with:

- one server-declared capability identity for each high-signal action
- explicit channel states for `supported`, `inspect-only`, `degraded-but-handoffable`, and `unavailable`
- explicit cross-channel handoff objects that preserve subject, review family, mutation gate, and receipt promise
- a fixed rule that degraded channels may not invent weaker apply paths just because richer chrome is missing
- Linux/headless parity strong enough that `try another client` is never the real product contract

### Requirement 64 — safety-critical actions need one channel-parity contract

If the operator still has to infer from Linux/WebUI/config-mode caveats whether a dangerous action exists, whether it is weakened here, or whether some richer client is the only place where the full review grammar appears, the product has not actually exposed its channel-parity contract.

AnonSync should instead require one shared action identity across browser/workbench, CLI, TUI, and API-backed control, with only layout changing — never the action's blast radius, review grammar, admissible outcomes, or receipt meaning.

### Requirement 65 — cross-channel continuation must preserve the same reviewed action

If the operator still has to restart a dangerous action from scratch after channel failure or client degradation, the product has not actually exposed its handoff contract.

AnonSync should instead publish one public review-handoff model that preserves the requested action, subject, review family, gate truth, and receipt promise whenever the action safely continues in another channel, and that explicitly reopens broader review when channel change would alter trust, endpoint, or state-root meaning.


### 16ab) Runtime-seat changes still depend too much on install mode, service account, and mapped-path folklore

One more Resilio pass exposes a distinct same-host seam.

`Running Sync as a service on Windows` says the service can run as current user, `Local System`, or `Local Service`, and that install choices split into migrated state versus clean installation.
`Sync Service Troubleshooting on Windows` says mapped drive letters are unavailable to the service because services do not receive interactive logon mapping, that the UNC workaround loses file-update notifications and falls back to full rescan or restart, and that switching the service to `Local System` opens a different storage folder with no prior shares visible until the operator re-adds and re-shares them.
`Sync Storage folder` separately says the storage path changes again by service account.
`Guide to Linux, and Sync peculiarities` adds that Linux has no OS integration and requires more manual configuration than desktop seats.

That combination is revealing.
The same machine can still present materially different control worlds depending on which runtime seat is active:

- whether the same durable state root is still open or a different storage root silently became active
- whether the same target paths are even reachable from this seat
- whether path access now depends on degraded UNC or similar workaround rather than native local semantics
- whether change detection remains continuous or has silently degraded to rescan-only best effort
- whether the honest next step is preserve same state, migrate with reviewed rebind, or admit that this is really a clean-seat start

AnonSync should not clone that shape.
A serious operator surface should instead publish one execution-seat and seat-switch model with:

- one explicit execution-seat object describing service profile, runtime principal, visible path world, and notification/freshness posture
- one reviewed seat-switch case describing requested continuity intent, reachable-target delta, freshness/substrate downgrade, and fallout
- explicit difference between `same root / same seat-class`, `same root / new principal`, `same state but rebind required`, and `clean-seat start`
- explicit receipts proving whether a switch preserved inventory truth or deliberately opened a different runtime world

### Requirement 66 — runtime-principal and service-seat changes must share one reviewed continuity/reachability contract

If the operator still has to combine install-mode choices, service-account changes, missing mapped drives, UNC workarounds, storage-folder lore, and re-add/re-share ritual to answer “am I still operating the same state world, what paths did I lose, and did freshness degrade?”, the product has not actually exposed its execution-seat contract.

AnonSync should instead publish one public model with explicit execution-seat objects, explicit seat-switch reviews, explicit path-reachability and notification/freshness deltas, explicit migrated-state versus clean-seat outcomes, and durable seat-switch receipts that preserve the difference between continuity-preserving runtime change, reviewed rebind, and honest fresh runtime world.

## Where Resilio is still probably the better choice

The archive should also stay honest about where Resilio still looks stronger.

Resilio is probably still the better fit if the operator mainly wants:

- maximum automatic speed from ordinary clearnet direct paths
- a polished, convenience-heavy, multi-platform consumer experience
- less interest in inspectable policy, route provenance, or recovery governance
- less concern about default metadata exposure on WAN routes

That matters because the right AnonSync argument is **not** “Resilio is bad.”
It is:

> Resilio is strong at a different set of defaults, and AnonSync should exist only if it is willing to choose a sharper privacy/control model all the way down.

### 16ad) Control state still bleeds too directly into the live share tree

Resilio's current docs expose a different seam that is easier to normalize away because it is so old-fashioned.
`What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?` says every synced folder gets a hidden `.sync` directory that is critical for syncing, stores the folder ID, and contains `Archive`, `IgnoreList`, and `StreamsList`; the same article also says files ending with `.!sync` live in the share while a download is in flight.
`Ignoring files in Sync (Ignore List)` says `IgnoreList` itself lives inside hidden `.sync`, is case-sensitive, does not work for files that have already been synced, and that once structural information has been scanned and indexed it stays in Sync's database and is passed to other peers until the share is disconnected.
`Alt Streams and Xattrs in Sync` says xattrs are controlled through `.sync/StreamsList`, cannot be ignored through `IgnoreList`, and may spill into `.sync/Streams` stub files when the local filesystem cannot represent them directly.
`Using Archive for file versioning and restoring deleted files` says rollback/restore still routes through the hidden `.sync/Archive` path outside desktop UI convenience.
`Service files missing / Cannot identify destination folder` then says repair can still mean `make sure you don't have any important data in the archive`, delete `.sync`, and add the share back.

That is useful support knowledge.
It is not yet one public layout contract.

The practical consequence is that five different byte classes keep collapsing together:

- ordinary user data
- share identity and policy state
- rollback/history retention bytes
- in-flight transfer residue
- metadata-carry artifacts that only exist because one filesystem cannot represent another cleanly

If the operator still has to remember that `.sync` is both marker and service store, that Archive is hidden path state not just history UI, that xattr carry-forward may create stub files, that `IgnoreList` is policy but also a hidden file in the share, and that interrupted transfer residue may still look like a funny filename inside the tree, the product is not explicit enough.

AnonSync should instead publish one public share-layout model with:

- one explicit live-namespace guarantee for what the ordinary mounted tree should mean
- one explicit annex/control-state location for share identity, policy mirrors, portability artifacts, and temp residue
- one explicit residue-class model for history, temp-transfer, metadata-carry, and legacy-import bytes
- one reviewed migration/cleanup path so legacy in-tree managed bytes can be preserved, relocated, or retired honestly
- durable layout receipts proving whether the user tree is clean, mixed by explicit acceptance, or still carrying legacy managed state

### Requirement 44a — live namespace and managed sync state must stay visibly separate

If the operator still has to combine hidden `.sync` semantics, manual Archive browsing, `IgnoreList` timing caveats, `StreamsList`/xattr spillover behavior, and `.!sync` residue to answer “which bytes are my files, which bytes are sync machinery, and what can I safely clean?”, the product has not actually exposed its share-layout contract.

AnonSync should instead publish one public model with explicit live-namespace guarantees, explicit annex placement, explicit residue classes, explicit migration and cleanup reviews, and durable layout receipts that preserve the difference between ordinary user data, rollback/history bytes, temp/in-flight residue, metadata-carry artifacts, and legacy managed state.

### 16ac) Human labels, cryptographic authority, and same-person continuity are still coupled too tightly

Resilio's own docs expose another seam that matters more than it first appears.
`Can I change the name of my Sync identity?` says the chosen identity name is used to generate the digital certificate, so there is no simple rename path; changing the name requires unlinking the current identity and creating a new certificate, which removes Advanced folders from that instance and forces relink work elsewhere.
`Sync Private Identity & Linking My Devices` says each installation gets a unique certificate generated from the selected identity name, that linked devices can auto-approve all linked devices for future sharing, that linking one configured device into another can cause the latter to take the former's identity name, fingerprint, and configured shares, and that linking two already-running devices can make one lose its certificate entirely.
The same guide says mixed v2/v3 linking can conflict on licensing and cost access to UI and share configuration, and that you cannot remotely unlink other devices.

That is useful support knowledge.
It is not yet one public continuity model.

The practical consequence is that four different truths keep collapsing together:

- a harmless label correction
- peer-visible renaming for recognition
- same-person convenience linking
- real authority replacement with grant and approval fallout

If the operator still has to remember that fixing a typo means `unlink`, that `same name` is not `same certificate`, that convenience linking can overwrite the losing device's continuity story, and that future approvals may still key off the wider linked constellation, the interface is not explicit enough.

AnonSync should instead publish one public naming/identity model with:

- mutable human-facing labels separated from stable subject handles and cryptographic authority
- explicit alias history so old names remain searchable without pretending authority changed
- reviewed same-person continuity cases that say whether the candidate is the same authority, a successor-supported new authority, or an unrelated subject with a familiar name
- explicit grant/constellation fallout before any continuity claim is accepted
- durable identity-label receipts proving whether the action was cosmetic relabeling, peer-visible rename, or real authority replacement


### 16ae) Speed, compatibility, and troubleshooting knobs still rewrite semantics too quietly

Resilio's current docs expose one more seam that is easy to underestimate because the settings look `advanced` rather than dangerous.
`Power user preferences` says `lazy_indexing` means a remote placeholder rename will not work and the file will not be renamed accordingly on the source peer.
The same page says `prefer_net_over_disk_operations` re-downloads files instead of counting differences, `direct_torrent_enabled` can make small transfers faster but interrupted transfers start again from the beginning, `enable_file_system_notifications` can be disabled, `fix_conflicting_paths` can suppress conflict-file creation while leaving the share unsynced and `unpredictable`, and `prioritize_initial_indexing` delays syncing for huge pre-seeded folders until rescans finish.
`What happens when file is renamed` says rename preservation depends on `Archive`; without it, bytes are re-synced again.
`How soon does synchronization start?` and `Agent run out of system notify watchers` say immediate detection depends on filesystem notifications and that watcher loss forces periodic or manual rescan.
`Sync and SMB file shares` says notifications may not work on older SMB setups and that mixed access outside SMB can damage files or roll changes back.

That is useful support knowledge.
It is not yet one public semantic-fallback contract.

The practical consequence is that five different truths keep collapsing together:

- faster operation
- weaker or slower change detection
- rename continuity versus delete-plus-new-copy fallback
- diff-preserving transfer versus whole-file resend or non-resumable fast path
- honest conflict/verification posture versus suppressed or deferred proof

If the operator still has to remember that one `performance` setting affects rename fidelity, another affects resumability, another weakens detection freshness, and another can suppress conflict artifacts while the share quietly stops being trustworthy, the interface is not explicit enough.

AnonSync should instead publish one public semantic-runtime model with:

- one explicit contract describing current detection, rename continuity, delta-transfer, verification, and degraded-target posture
- one reviewed optimization/fallback case for any non-trivial change marketed as speed or compatibility work
- one explicit difference between semantic-neutral tuning and meaning-changing downgrade
- explicit degraded-target findings so network-share, watcher, or mixed-access realities cannot masquerade as ordinary local semantics
- durable optimization receipts proving which guarantees were preserved, weakened, or later restored

### Requirement 67 — non-trivial optimization and compatibility changes must share one reviewed semantic-fallback contract

If the operator still has to combine power-user toggles, watcher warnings, SMB caveats, rename folklore, and troubleshooting notes to answer `what guarantee got weaker when I accepted this faster or more compatible mode?`, the product has not actually exposed its semantic-runtime contract.

AnonSync should instead publish one public model with explicit semantic-runtime contracts, explicit optimization reviews, explicit guarantee deltas, explicit degraded-target scope, and durable receipts that preserve the difference between harmless tuning, reviewed semantic downgrade, and later restoration of stronger guarantees.


### 16af) Revocation and removal still over-promise recall too easily

Resilio's current docs expose one more seam that is easy to underestimate because the verbs sound ordinary.
`User Management` says `Disconnect` revokes future updates for the selected peer, but all files that have already been synchronized remain in that folder.
`Disconnecting and Removing Folders` says removing a folder from linked devices stops showing it on the linked identity set, yet it may still remain on remote devices that are not linked to that identity.
`Sync Private Identity & Linking My Devices` says linked devices get universal access and that linked devices effectively act as owners of the personal constellation's shares.
`Encrypted folders` says encrypted backup peers keep encrypted bytes, always force `Overwrite any changed files`, cannot use Selective Sync, may still help reseed only if the right keys were preserved and database continuity remains intact, and cannot restore deleted files from encrypted Archive back to others because they are read-only and follow the delete state.

That is useful support knowledge.
It is not yet one public recall contract.

The practical consequence is that several different claims still blur together:

- future updates stopped
- authority narrowed
- hidden from my linked surfaces
- retained bytes still exist somewhere else
- preserved encrypted backup still matters for recovery
- stronger remote delete or copy-recall claim was actually observed

If the operator still has to remember that `removed` may only mean `no longer shown here`, that `revoked` may still mean `bytes remain`, and that a retained encrypted replica may still be the last useful reseed path even after ordinary access was narrowed, the interface is not explicit enough.

AnonSync should instead publish one public retained-copy model with:

- explicit retained-replica posture for each peer or peer set
- one reviewed recall case whenever future authority and already-retained bytes both matter
- one explicit difference between `future updates stopped`, `retained copy attested`, `remote delete requested`, and `remote delete observed`
- explicit recovery-usefulness findings so encrypted backup or read-only retained storage cannot masquerade as ordinary collaborators or ordinary erasure
- durable recall receipts proving what changed now and what stronger claim still depends on later peer observation

### Requirement 68 — non-trivial revocation and removal changes must share one reviewed retained-copy and recall contract

If the operator still has to combine disconnect notes, linked-device scope, encrypted-backup caveats, and peer memory to answer `who still has bytes from this share and what exactly did my revoke/remove action prove?`, the product has not actually exposed its recall truth.

AnonSync should instead publish one public model with explicit retained-replica postures, explicit recall reviews, explicit byte-retention verdicts, explicit recovery-usefulness findings, and durable receipts that preserve the difference between future authority stop, retained-copy attestation, delete request, and observed stronger recall.


### 16ag) Authority rotation still splits trust epochs too quietly

Resilio's current docs expose one more seam that is easy to underestimate because the verbs look ordinary.
`What's the difference between Standard and Advanced folders?` says Standard folders use randomly generated keys while Advanced folders use PKI/certificates, that Standard peers can share the key they have without the same bounded owner model, that on-the-fly permission changes are not possible for Standard folders, and that changing permissions means removing and re-adding the share with a new key. The same page says Standard folders cannot be converted into Advanced without removing and re-adding them.
`Key structure and flow` then says a key change on one peer is not distributed automatically and that peers with the old key continue syncing with each other while no longer syncing with the peer who changed the key.
`Sharing a folder locally` adds that some local-share permission changes also require remove-and-re-share ritual, that local-share access can be lowered by a remote owner, and that reconnecting a source share does not automatically reconnect the derived local share.

That is useful support knowledge.
It is not yet one public authority-rotation contract.

The practical consequence is that several different truths still blur together:

- new authority was issued
- old authority still exists and may still work
- some peers moved to the new boundary while others remain on the old one
- some derivatives or local shares must be rebuilt rather than mutated in place
- some old portable artifacts or copied keys now point at superseded authority
- the strongest honest claim may be only `mixed epoch`, not `everyone now uses the new boundary`

If the operator still has to remember that one share class supports live mutation, another requires re-share ritual, and a rotated key may leave an older peer set quietly syncing among itself, the interface is not explicit enough.

AnonSync should instead publish one public authority-epoch model with:

- explicit share-authority epochs and stale-capability postures
- one reviewed epoch-rotation case whenever share authority material or share class changes non-trivially
- one explicit difference between `new epoch issued`, `old epoch quarantined`, `mixed epoch`, and `observed new epoch only`
- explicit derivative/local-share migration findings so reissue and rebuild obligations cannot masquerade as surprising exceptions
- durable rotation receipts proving what authority became current, what stale material remained, and what convergence still depends on later observation

### Requirement 69 — non-trivial share-authority changes must share one reviewed epoch-rotation and stale-capability contract

If the operator still has to combine folder-class caveats, key-flow notes, local-share exceptions, and re-share ritual to answer `which authority generation is actually current, what old capability still exists, and did the swarm converge to the new boundary yet?`, the product has not actually exposed its authority-rotation truth.

AnonSync should instead publish one public model with explicit share-authority epochs, explicit rotation reviews, explicit stale-capability findings, explicit derivative migration findings, explicit convergence verdicts, and durable receipts that preserve the difference between newly issued authority, mixed-epoch migration, quarantined old authority, and observed clean convergence.

## Final judgment

Resilio Sync remains strong enough that cloning it naïvely would produce an impressive but strategically muddled product.
The better move is narrower and more opinionated:

> preserve Resilio's best user-facing ideas, but replace its trust-broadening linkage semantics and fragmented operator surface with explicit policies, explicit disclosure/publication contracts and exposure reports, explicit known-host records, explicit route leases for temporary direct exceptions, explicit provenance, explicit recovery, explicit preservation reports for destructive actions, explicit retirement records for trust-changing device exits, explicit stewardship records for share governance and handoff, explicit deviation policies and deviation cases for non-authoritative local edits, explicit filesystem-compatibility reports before real paths are bound, explicit projection policies that separate share namespace announcement from local mount visibility, explicit file-intent receipts that keep local removal, replicated delete, and restore scope distinct, and explicit convergence reports that separate idle status from trustworthy settlement confidence, and explicit portability/fidelity contracts that keep pathname, metadata, notification, and support-tier truth visible after bind instead of only at preflight time, and explicit storage-budget contracts that keep materialized bytes, archive/history cost, temp remnants, and reclaim scope visible instead of leaving low-space behavior to folklore, and explicit offer-artifact contracts that keep delivery encoding, approval posture, redelegation, and later claim consumption visible instead of burying authority semantics inside type-specific share rituals, and explicit attention contracts that keep report meaning, lane placement, delivery channels, and acknowledgement receipts visible instead of scattering operator urgency across badges, history search, and platform-specific notifications, and explicit recovery-material contracts that keep bundle custody, hidden dependencies, invalidation, and continuity claims visible instead of leaving disaster readiness to saved-key ritual and storage-folder memory, and explicit release-posture contracts that keep version, channel, edition family, schema epoch, constellation skew, and rollback posture visible instead of leaving upgrade truth to platform-specific download pages and changelog archaeology, and explicit policy-origin contracts that keep defaults profiles, pinned values, imports, overrides, and return-to-inheritance semantics visible instead of leaving effective behavior to settings-layer archaeology, and explicit diagnostic-evidence contracts that keep incident scope, debug depth, redaction posture, bundle contents, and export/destruction receipts visible instead of leaving troubleshooting to storage-path lore, hidden toggles, and support ritual, and explicit override-lease contracts that keep temporary widening, baseline/effective comparison, expiry or exhaustion, and conversion-to-durable-policy visible instead of leaving short-lived operator intent to sticky settings edits and cleanup memory, and explicit constellation/authority-domain contracts that keep convenience membership, per-member visibility, owner-like power, approval reach, and constellation-wide blast radius visible instead of hiding them inside ambient same-identity linkage, and explicit approval-seat contracts that keep the current acting member, one-subject versus future approval horizon, and safer narrower alternatives visible instead of hiding them inside linked-device owner folklore and remembered auto-approval, and explicit dormant-peer re-entry contracts that keep long-offline return, chronology confidence, replay authority, source reality, and escalation-to-compromise-or-cutover visible instead of leaving stale return behavior to peer counters, invalid-time warnings, archive aftermath, and hide/reappear device folklore, and explicit authority-mutation contracts that keep current authority, desired boundary delta, dependent fallout, substrate migration, and byte-retention consequences visible instead of leaving live access changes to folder-class and remove/re-share ritual, and explicit topology-review contracts that keep graph overlap, containment, propagation shape, path/root-boundary consequences, and safe rebind versus blocked-loop decisions visible instead of leaving nested, overlapping, or moved shares to separate FAQs and reconnect folklore, and explicit contention/quiescence contracts that keep contested scope, writer reality, notification weakness, quiesce posture, and safe resume conditions visible instead of leaving lock pressure and mixed external-writer risk to badges, hidden delay files, retry knobs, and SMB troubleshooting lore, and explicit capacity-fit contracts that keep subject role, host resource posture, indexing cost, freshness guarantees, and admissible local modes visible instead of leaving large-subject admission to memory notes, watcher warnings, advanced toggles, and re-add folklore, and explicit bring-up contracts that keep host role, continuity choice, identity posture, control entry, and startup blockers visible instead of leaving first control to installer, config-file, or activation ritual, and explicit target-custody contracts that keep path markers, owner lineage, removable-media reuse, collision risk, and cleanup evidence visible instead of leaving same-host ownership truth to hidden `.sync` state, duplicate-instance caveats, and delete-and-re-add folklore, and explicit share-layout contracts that keep ordinary live files, managed control bytes, rollback/history retention, metadata-carry sidecars, and temp-transfer residue visibly separate instead of leaving the operator to learn `.sync`, `.sync/Archive`, `.sync/Streams`, and `.!sync` as cleanup folklore, and explicit authority-epoch contracts that keep newly issued share authority, stale capability residue, derivative/local-share migration, and mixed-epoch convergence visible instead of leaving key rotation, share upgrade, and re-share fallout to folder-class archaeology.




### Requirement 29 — contacts, pending peers, and future introductions must be separate public state

Unknown or newly introduced peers should not silently become trusted, linked, or visible-share-bearing just because the operator wanted convenience elsewhere in the constellation. Contact memory, pending-peer admission, ignore/quarantine, and bounded introduction policy should all be separate supported objects.

### Requirement 30 — successor continuity must be reviewed rather than inherited by convenience

Device replacement should be able to carry forward exactly the right things — perhaps some grants, perhaps no future approvals, perhaps limited contact memory — without pretending that successor continuity is the same as either linking or identity takeover.

### Requirement 31 — safety-critical guardrails must have cross-surface parity

If an action needs a guardrail on one surface, it needs an equivalent guardrail on all first-class surfaces. Linux/web workbench users should not lose destructive-action safety or trust review semantics just because they are not inside a richer desktop app.

### Requirement 32 — storage root, identity root, and service profile must be first-class state

Operators should be able to inspect where durable state lives, which runtime/service profile is using it, what identity and share inventory are attached to it, and what import/move/replace workflow is supported. “Why did all my shares disappear?” is evidence of a broken state model, not a documentation gap.

### Requirement 33 — warnings must collapse into a common report language

A mature AnonSync surface should not force operators to juggle unrelated warning badges, power-user toggles, support notes, and implicit drift. Compatibility, preservation, exposure, convergence, comparison, and plan-drift findings should render through one shared report/intervention grammar with explicit freshness, severity, scope, and next-safe action.

### Requirement 34 — filesystem semantic fidelity must be a durable contract, not a one-time warning

Resilio's current docs make this gap unusually concrete.
One article says SMB shares can work, but notifications may fall back to full folder rescan unless both sides support SMB 3.0, and mixed access outside Samba can damage files or roll changes back.
Another says Windows does not support soft links, hard links, or symbolic links and may produce `.Conflict` artifacts, while Unix syncs the link but not the target folder.
Another says xattrs only sync through a hidden `.sync/StreamsList` whitelist and may spill into `.sync/Streams` service storage when the local filesystem cannot represent them directly.
Another says the hidden `.sync` folder is critical enough that deleting or corrupting it suspends synchronization and the repair story becomes remove/re-add.
The general troubleshooting page adds UTF-8 filename requirements, path-length limits, permissions failure, merge-tree failure, and notification-loss rescans as more separate caveats.

That is useful support knowledge.
It is not yet one public operator contract.

AnonSync should therefore expose, for every adopted mount that matters:

- a mount-scoped fidelity contract describing what pathname, metadata, notification, and support-tier semantics are actually promised on that path right now
- an explicit portability policy describing which rewrites, drops, blocks, or virtualization rules were chosen intentionally
- a drift surface that says when the contract weakened because permissions changed, notifications degraded, the path became a network share, or the underlying filesystem changed
- a durable receipt proving which downgrade or warning-tier semantics the operator knowingly accepted

If the operator still has to combine one compare report, one SMB article, one symlink article, one hidden-service-file article, and one troubleshooting page to answer “what semantics survive on this mount?”, the interface is not explicit enough.


### Requirement 35 — state-root transitions must be plan-bearing and receipt-bearing

Attach, move, export, import, profile-switch, and identity-root replacement work should all produce explicit transition reports, snapshots, and audit receipts. Launch flags, service installers, and background-mode switches are not an acceptable substitute for a public operator model.

### Requirement 36 — bound path, visible share, and preservation posture must remain separate public state

A share should be able to stay visible while no local path is bound. A broken path should be repairable without forcing share re-creation. Preservation posture should be queryable before detach, cleanup, or restore. If a product still routes those decisions through reconnect prompts, hidden marker files, or remove/re-add ritual, it has not actually exposed the model.

### Requirement 37 — file intent, deviation, and restore scope must render through one explicit action model

A user should never need to remember that one file gesture means local space reclamation, another means replicated deletion, a third means read-only remediation, and a fourth means hidden-history restore depending on mode or surface.
The product should render those as one public model with explicit intent, explicit scope, explicit preservation proof, and durable receipts.

### Requirement 37a — successor cutover and state re-home must share one reviewed transition grammar

Replacing a device, re-homing a state root, or switching into a runtime profile that could open different durable state should not force the operator to reconstruct meaning from installer labels, missing shares, or stale device rows. Non-trivial cutover work should expose one fixed review grammar with:

- predecessor and candidate
- continuity carry-forward
- state-root and runtime target
- share / grant / authority rewrite
- residue and revocation
- receipt promise

If the operator still has to infer from “migrate settings”, “clean install”, “link device”, or “old instance shows offline” what continuity story actually happened, the product has not exposed the model.


### Requirement 38 — runtime activity truth must be explicit, phase-scoped, and schedule-aware

If the operator still has to remember that a paused share may keep indexing, a scheduled pause may still allow deletes or upload asymmetry, and LAN throttling depends on a separate advanced switch, the product has not actually exposed its runtime control model.

AnonSync should instead make activity phase truth, one-shot overrides, and recurring windows render through one explicit matrix with one explanation surface.

### Requirement 39 — rollback provenance and conflict resolution must be one first-class timeline model

If the operator still has to combine a short-lived activity view, hidden archive paths, offline-wins overwrite folklore, and magic `.Conflict` filenames to answer “what happened here and how do I safely recover?”, the product has not actually exposed its rollback contract.

AnonSync should instead publish one public timeline model with durable history entries, restore candidates, conflict cases, and rollback receipts.


### Requirement 40 — storage pressure, reclaim scope, and retention cost must be one first-class budget model

If the operator still has to combine placeholder intuition, hidden `.sync/Archive` growth, power-user warning thresholds, storage-folder lore, and manual `.!sync` cleanup steps to answer “what is consuming local space and what can I free safely?”, the product has not actually exposed its storage contract.

AnonSync should instead publish one public budget model with durable space ledgers, explicit byte classes, explicit pressure cases, reclaim plans that keep local reclaim distinct from replicated delete, and reclaim receipts that prove what was freed and what retention posture changed.


### Requirement 41 — capability-bearing offers must use one explicit artifact and claim-receipt model

If the operator still has to remember that one portable artifact implies approval, another bypasses it, another can expire, another can be re-shared freely, and another needs remove-and-re-share ritual to change access, the product has not actually exposed its capability contract.

AnonSync should instead publish one public offer-artifact model with normalized manifests across delivery encodings, explicit approval and peer-pinning posture, explicit redelegation policy, bounded redemption budgets, and claim receipts that prove what local outcome later consumed the artifact.


### Requirement 42 — throughput truth must be one explicit transfer-policy and budget model

If the operator still has to combine route icons, generic performance charts, Internet-only-vs-LAN rate-limit caveats, relay articles, power-user protocol knobs, queue-priority heuristics, and storage-folder delay files to answer “why is this transfer using this path at this speed right now?”, the product has not actually exposed its transfer contract.

AnonSync should instead publish one public transfer model with explicit transfer policy, explicit throughput budgets, explicit queue lanes and suspension causes, explicit route-cost posture, and inspectable transfer explanations that say whether the bottleneck is route policy, budget cap, fairness, delay profile, source absence, or disk backpressure.

### Requirement 43 — attention, escalation, and acknowledgement must be one explicit contract

If the operator still has to combine a status column, queue cards, history search, browser trust prompts, Linux WebUI-only notifications, and client-specific badges to answer “what needs action now, what can wait, and what did my acknowledgement actually change?”, the product has not actually exposed its attention contract.

AnonSync should instead publish one public attention model with explicit attention policy, explicit workbench-lane placement, explicit delivery-channel outcomes, and durable acknowledgement/snooze receipts that distinguish presentation-only change from true resolution of the underlying subject.

### Requirement 44 — subject naming and authority continuity must stay visibly separate

If the operator still has to remember that a typo fix means unlinking, that the same name does not prove the same authority, that convenience linking can rewrite the losing device's continuity story, and that future approvals may still travel across a wider linked constellation, the product has not actually exposed its naming/identity contract.

AnonSync should instead publish one public model with mutable labels, alias history, stable subject handles, explicit authority continuity reviews, and receipts that prove whether an action was only cosmetic relabeling or a real trust/continuity change.



### Requirement 70 — observer/read-only semantics must decompose into visibility, local-write, serve, and projection truth

Resilio's current docs still make this gap unusually concrete.
`Is one-way synchronization possible?` says a read-only peer receives the folder but if it updates, adds, or deletes files those changes are not propagated and synchronization for the changed file is stopped.
`Folder Preferences` then says `Overwrite any changed files` can instead revert local changes, including added files, but that helper is disabled when Selective Sync is on.
`User Management` says linked devices under one identity all act as Owners, while `How to create a Read Only folder while syncing across linked devices?` says creating read-only behavior across linked devices requires dropping to a Standard-folder/read-only-key ritual.
`Sharing a folder locally` adds that local shares inherit only the source share's permissions, cannot receive Owner, and in some Advanced-share cases require remove-and-re-share to change local-share access.

That is useful support knowledge.
It is not yet one public operator contract.

AnonSync should therefore expose, for every observer-style or read-only posture that matters:

- a durable observer-posture contract describing visible names/bytes, local-write consequences, onward-serving rights, and the repair mode actually available
- an explicit boundary statement showing which parts of that posture come from share authority, selective-materialization, local derivation, or share-class/runtime limits
- a reviewed posture-change surface that says whether the operator is really narrowing authority, only changing local projection, or doing both
- a durable receipt proving exactly what `read only`, `viewer`, or `observer` meant on that subject at the time it was accepted or repaired

If the operator still has to combine one one-way-sync article, one folder-preferences article, one linked-device workaround, and one local-share caveat to answer “what can this replica actually do?”, the interface is not explicit enough.



### 16ah) File availability still reads more like scattered feature ritual than one answer surface

Resilio's current docs still give a lot of useful operator detail, but they do it in pieces.
`Selective Sync` explains placeholders and on-demand materialization.
`What Is an RSLS File?` explains that reverting to placeholders requires making sure another device still has the full copy.
`Sync Interface on iOS devices` and `Storage Management on iOS` explain that `Clear synced files` or storage cleanup can turn local synced files back into placeholders when Selective Sync is on.
The ghost-file warning article explains that the tree may still advertise a file even when nobody now has the bytes.

That means one ordinary operator question — `what is the truth of this file right now?` — still depends on stitching together several different pages and surfaces.
The product is telling the truth, but not yet in one place.

AnonSync should therefore reject the idea that file availability is merely a mode label plus a few contextual actions.
It should instead specify one concrete answer surface for every file or subtree that matters.

### Requirement 71 — file availability must be a concrete interface contract, not just a conceptual model

It is not enough for AnonSync to say, in the abstract, that namespace visibility, local residency, full-copy witnesses, and fetchability are different truths.
The operator surface should also define exactly how that answer is rendered.

At minimum every serious file/subtree availability surface should provide:

- one compact answer strip that always states visibility, local residency, witness posture, fetchability posture, and safest next step in the same order
- one review drawer/page that expands into requested action, current truth, witness evidence, admissible actions, and receipt promise
- one subtree table that preserves per-row risk classes instead of flattening a mixed subtree into one bulk label
- one batch rule that splits `safe to evict`, `re-witness first`, and `ghost/stale` classes before apply
- one receipt model proving later which witness/fetchability truth was reviewed when a fetch, evict, pin, or stale-announcement action was taken

If the operator still has to infer from a placeholder icon, a grayed-out row, a mobile `Clear synced files` command, and a later warning whether the bytes are safely retrievable, the interface is not explicit enough.


### Requirement 71a — the primary verb must change when the availability risk class changes

A truthful availability surface does not stop at reporting state.
It must also change its offered action when the meaning changes.

At minimum that means:

- `fetchable-now` may offer `Fetch now` or `Evict safe rows`
- `local-last-copy` should change the primary verb to `Pin locally` or `Create another witness`
- `ghost-risk` should change the primary verb to `Retire stale announcement` or `Keep visible with warning`
- `history-backed-only` should surface `Restore from history` rather than pretending ordinary swarm `Fetch` is still honest
- mixed selections should label only the safe subset they can mutate, for example `Evict 24 safe rows`, instead of overclaiming with one cheerful `Apply to all`

If the operator still sees the same optimistic action label after the product has already discovered that the path is guarded, last-copy, ghosted, or history-only, the interface is not explicit enough.

### Interface conclusion 9 — file availability needs one sentence-shaped answer strip and one mixed-risk review table

The archive should now treat file availability as a first-class interface pattern in its own right.
The concrete rule is:

> every serious file/subtree surface should be able to answer, in one sentence-shaped strip, what is visible, what is local, who still witnesses full bytes, whether fetch is honest right now, and what the safest next action is.

Without that, `selective`, `placeholder`, `available on demand`, `clear`, `remove from device`, and `fetch` will keep reading like a family resemblance of useful actions instead of one explicit operator model.

## 16ai) Approval convenience still blurs the acting seat and future blast radius

Resilio's current docs still make this gap unusually concrete.
`Sync Private Identity & Linking My Devices` says all folders become visible across linked devices, that a remote user can choose to automatically approve all linked devices for future sharing after approving one, and that pending requests can be approved from any linked device where the folder is already active.
`User Management` says all linked devices under one identity act as Owners.
`Comprehensive guide to syncing (Desktop-Desktop)` still says linking devices gives full RW access across the linked set.

Those are useful convenience features.
They are not yet one trustworthy explanation of:

- which exact reviewed member is speaking at approval time
- whether the approval is only for this current share or also creates future standing authority
- whether a narrower seat or narrower horizon is available from the same moment
- whether the operator is approving as one current device steward or effectively changing future constellation behavior

AnonSync should therefore expose, for every approval-worthy request that matters:

- a durable approval-request object that names the subject, the candidate seats, and the requested role
- a reviewed approval-seat surface that says which member is speaking and why that seat is admissible
- an explicit approval-horizon section that keeps `approve once` distinct from `approve for reviewed future scope`
- a durable receipt proving acting seat, horizon, and later-expiring or revocable future memory

If the operator still has to remember that the request was approved from one linked device, that all linked devices act as owners, and that one checkbox may now widen future approvals for the whole linked set, the interface is not explicit enough.

### Requirement 72 — approval surfaces must show the acting seat and approval horizon explicitly

If the operator still has to combine linked-device lore, owner semantics, remembered approval behavior, and peer-list convenience to answer `which member is speaking, for what exact scope, and did I approve only this request or also future requests?`, the product has not actually exposed its approval contract.

AnonSync should instead publish one public model with explicit approval requests, explicit acting-seat review, explicit approval horizons, explicit narrower-seat alternatives, and durable receipts that preserve the difference between current-subject approval, bounded future approval, denial, and withdrawn/stale requests.


## 16aj) Resilio's three linked-device modes still compress too many local truths into one label

Resilio's current docs still make this seam unusually concrete.
`Sync Private Identity & Linking My Devices`, `Folder Types and Management`, and `Sync functionality in detail` still present `Disconnected`, `Selective Sync`, and `Synced` as the main linked-device local-state answer.
At the same time, `How to manually set the location of the folders synced across linked devices`, `Folders are duplicating with an index (i) in their name.`, and `Settings on mobile platforms` still show that those labels are also doing work for future-arrival handling, default-path behavior, custom-location workflow, and collision fallback.
If a device remains in `Selective Sync` or `Synced`, new arrivals go to the default location; custom placement requires switching the seat to `Disconnected` first and later clicking `Connect`; and same-name arrivals can produce indexed duplicate directories.

Those are not fatal flaws.
They are evidence that one friendly mode label is still carrying several different truths at once:

- is the share merely announced here, or actually claimed here
- is there a local bind/path here yet, and who chose it
- are bytes absent, placeholder-backed, or fully materialized
- what will this seat do with future arrivals by default
- whether the current path was reviewed, auto-chosen, or collision-adjusted

AnonSync should therefore reject one monolithic local-share mode switch.
It should instead publish one public local-presence model with explicit current-share posture, explicit future-arrival default policy, explicit path provenance, and receipts that prove which of those changed.

### Requirement 73 — local share posture and future-arrival policy must not collapse into one `mode`

If the operator still has to infer from one mode label whether this share is only announced, already claimed, already bound, placeholder-backed, fully materialized, or merely subject to a future-arrival default, the product has not actually exposed its local-state contract.

AnonSync should instead publish one public model with:

- an explicit current-share local-presence posture covering announcement, claim, bind, byte posture, and path provenance
- an explicit arrival-default policy covering what this seat will do with later arrivals from the same reviewed scope
- explicit transition reviews that keep `change current share here` distinct from `change future arrivals here`
- durable receipts that prove whether an action changed only the current subject, only future defaults, or both


- current docs still say that when a linked device is in `Selective Sync` or `Synced`, newly arriving folders go to the default folder, and if the same name already exists there Sync adds an index to the new folder
- current docs still tell operators who want a custom location to switch the device to `Disconnected` first and only then use `Connect` to choose the path

## 16ak) Standing arrival defaults still hide future behavior behind scattered mode/default/simple-mode ritual

Resilio's current docs still make this seam unusually concrete.
`Sync Private Identity & Linking My Devices` and `Synchronization Modes` still present `Disconnected`, `Selective Sync`, and `Synced` as standing linked-device defaults.
`How to manually set the location of the folders synced across linked devices?` and `Folders are duplicating with an index (i) in their name.` still say that when `Selective Sync` or `Synced` are in force, new linked-device arrivals go to the default folder, and that custom placement requires switching the device to `Disconnected` and later using `Connect`.
`Settings on mobile platforms` still says that when Android `Simple mode` is enabled, all new shares go to the default folder location and same-name collisions pick up `(1)`.

Those are useful conveniences.
They are also evidence that one seat's standing future-arrival behavior is still spread across several knobs rather than one reviewed policy object.

The practical consequence is that the operator can still change a standing device default and only later discover that they also changed:

- whether later arrivals announce only or connect immediately
- which drafted root or default path later arrivals will propose
- whether same-name collisions may silently drift toward duplicate suffix fallback
- whether mobile behavior differs only because one simplification toggle stayed on
- whether any currently visible but still-unclaimed arrivals now inherit the new template

AnonSync should therefore not let standing future-arrival behavior hide inside a mode selector, a default-folder field, or a mobile simplification toggle.
It should instead publish one explicit standing-template policy with one explicit governance review that previews effect buckets for:

- future unseen arrivals
- currently announced but unclaimed arrivals
- currently claimed but unbound arrivals
- currently bound shares

And it should make one conservative choice explicit:

- changing the standing template should not refresh existing drafts unless the operator explicitly asks for that outcome
- changing the standing template must never silently relocate already bound shares

### Requirement 74 — standing future-arrival templates must be explicit reviewed seat policy, not scattered convenience toggles

If the operator still has to combine mode lore, default-folder settings, mobile `Simple mode`, reconnect ritual, and duplicate-index folklore to answer `what will this seat do with the next matching arrival, and what existing subjects definitely stay untouched?`, the product has not actually exposed its standing default contract.

AnonSync should instead publish one public model with:

- an explicit standing seat-template object naming admission posture, drafted root/path template, collision default, byte suggestion, and governed scope
- an explicit template-governance review showing effect buckets and pinned exceptions
- explicit draft-refresh choice for currently announced but unclaimed arrivals
- durable receipts proving which standing policy changed and which current subjects were guaranteed unchanged

## Sharper conclusion from this pass

The reason not to clone Resilio is now even less about capability and even more about contract shape.
Resilio clearly proves that remembered default roots, automatic arrivals, low-friction later connection, and future-only standing defaults are useful.
What AnonSync should not copy is the way *path suggestion*, *path commitment*, *collision fallback*, and *standing future-arrival defaults* still live inside one convenience story.

AnonSync should therefore preserve:

- suggested default roots/templates as convenience
- low-friction arrival review
- explicit selective/full materialization choices after bind

But it should reject:

- any path commitment that happens only because a mode/default says so
- any duplicate `(1)` fallback that pretends an unrelated collision is a harmless naming detail
- any review surface that makes operators use `disconnect`/`connect` folklore to explain where a share really belongs
- any standing seat-default story that makes operators infer future-arrival behavior from scattered mode, default-root, or `Simple mode` toggles instead of one reviewed policy object


## 16al) Standing defaults still lack one first-class history of which version handled which subject

Resilio's current docs still make this seam unusually concrete.
`Synchronization Modes` and `Selective Sync` still say the chosen linked-device mode applies to newly added folders while current ones remain as they are.
`Folder Types and Management` still says previously approved peers can have later pending folders auto-connect.
`Sync Private Identity & Linking My Devices` still says a remote user can choose to auto-approve all linked devices for future sharing after approving one, and that all folders become visible across linked devices.
`How to manually set the location of the folders synced across linked devices?` and `Settings on mobile platforms` still keep later placement behavior tied to default roots and mobile simplification settings.

That is real convenience.
But once a seat's standing defaults have changed more than once, the operator still lacks one obvious first-class answer to:

- which exact standing-policy version handled this arrival or draft
- whether this subject is still carrying a grandfathered outcome from an older policy version
- what changed since that version
- which receipt or event proves the relevant policy transition

AnonSync should therefore not stop at policy previews.
It should also publish one public lineage contract for every meaningful standing-policy family.

### Requirement 75 — standing policy must have explicit lineage and per-subject attribution

If the operator still has to compare current settings with remembered earlier modes, earlier approval scope, or earlier default roots to answer `which policy version handled this subject?`, the product has not actually exposed its standing-default contract.

AnonSync should instead publish one public model with:

- explicit standing-policy versions with effective intervals and supersession links
- explicit lineage entries summarizing what changed and what definitely did not
- explicit subject-policy attribution objects showing which version handled an arrival, draft, match, claim, or bind
- explicit current-versus-applied compare views so the operator can see whether the subject matches current policy or is grandfathered
- durable receipts proving both the policy transition and the subject stage attributed to that version



## 16av) Multi-carrier share convenience still leaves canonical artifact identity too implicit

Current Resilio docs still make the remaining seam concrete without yet turning it into one explicit contract.
`Link structure and flow` says a Sync link uses an `https://link.resilio.com/...#...` wrapper, that the landing page may rewrite that wrapper into `btsync://` so the Sync app can open it, and that parameters after `#` are not actually sent to the Resilio server.
`Sync Share Dialog (Desktop)` says the same folder may be shared as a link or QR code and copied into e-mail or messenger, while the desktop syncing guide says links can be clicked in a browser, pasted into Sync manually, or delivered through ordinary channels.
Taken together, those current docs still leave one missing operator answer once several carriers for the same invitation are in flight:

- whether browser wrapper URL, protocol rewrite, QR rendition, and copied text are the same portable artifact or several
- whether re-encoding the same offer for another carrier started a fresh budget island or merely created another alias
- whether the last-seen carrier is authority-bearing or only a delivery wrapper
- when a familiar-looking carrier is actually a later successor with changed scope or policy instead of just another alias of the old offer

AnonSync should preserve the useful part — practical multi-carrier sharing.
It should not clone a surface where carrier form silently stands in for canonical artifact identity.
The product should publish one explicit carrier-alias equivalence surface that says, in order, canonical artifact now, carrier observed here, other known aliases, why same/not same, what definitely did not change, and the receipt proving that judgment.

### Requirement 85 — canonical artifact identity must stay separate from carrier convenience

If the operator still has to combine wrapper URL shape, QR screenshots, copied text, and browser/app history to answer `is this the same offer?`, the product has not actually exposed portable-offer truth.

AnonSync should instead publish one public model with:

- explicit carrier kinds such as `wrapper-url`, `protocol-url`, `qr-payload`, `clipboard-text`, `mail-body-copy`, and `local-file-envelope`
- explicit carrier-authority postures such as `authority-bearing`, `delivery-wrapper`, `preview-only-copy`, `truncated`, and `ambiguous`
- explicit equivalence postures such as `same canonical artifact`, `same artifact delivery-only alias`, `same artifact authority-bearing alias`, `successor not alias`, and `cannot prove yet`
- explicit normalization basis so clients can explain what semantic fields matched and which differences were delivery-only
- explicit non-effects so delivery-only re-encoding never silently creates fresh budget, fresh trust lineage, or successor lineage
- durable carrier-alias receipts proving why several different-looking carriers were collapsed into one canonical offer or forked into a successor instead


## Conclusion addendum from this pass

The reason not to clone Resilio is now even less about raw capability and even more about long-lived operator truth.
Resilio clearly proves that standing defaults, remembered approval, automatic visibility, and low-friction later arrivals are useful.
What AnonSync should not copy is the way an operator still has to reconstruct policy history from today's settings and scattered help-center lore.

AnonSync should therefore preserve:

- seat-level convenience for later arrivals
- strong selective materialization and low-friction claim flows
- future-only standing-policy edits and practical defaults

But it should reject:

- any design where today's current standing setting is expected to explain every older subject still present
- any design where grandfathered drafts or paths are discoverable only by comparing current state with memory
- any design where a later policy edit lacks a versioned lineage and per-subject attribution surface


## 16am) Standing defaults still need one first-class drift and realignment surface after policy changes

Resilio's current docs still make this seam unusually concrete.
`Selective Sync` still says linked-device mode changes apply to newly added folders while current ones remain as they are.
`Sync Private Identity & Linking My Devices` and `Folder Types and Management` still say all folders become visible across linked devices, and prior approval can let later pending folders auto-connect.
`How to manually set the location of the folders synced across linked devices?` still keeps later placement behavior tied to default roots plus `Disconnected`/`Connect` ritual.

That is genuine convenience.
But after the operator changes standing defaults a few times, the remaining estate can now contain a mixture of:

- older drafted arrivals that still reflect prior path templates
- newer arrivals that follow the current mode/default policy
- already bound subjects that differ intentionally from today's policy
- subjects that are merely stale-looking and should actually be refreshed

Current docs explain the ingredients of that difference, but they still do not appear to expose one first-class answer to:

- which current subjects now differ from the current standing policy
- which of those differences are intentional grandfathering versus accidental drift
- which are safe to refresh in one batch and which require stronger review
- which reviewed receipt proves that a difference was kept on purpose instead of just being forgotten

AnonSync should therefore not stop at policy lineage.
It should also publish one public drift and realignment contract.

### Requirement 76 — standing-policy families need explicit drift classification and reviewed realignment

If the operator still has to compare `current policy`, `applied policy then`, and the current subject row to decide whether a difference is intentional, refreshable, or risky, the product has not actually exposed its long-lived standing-default contract.

AnonSync should instead publish one public model with:

- explicit drift-population views for each meaningful standing-policy family
- explicit per-subject drift classes such as `matches-current`, `grandfathered`, `refresh-eligible`, `subset-review-required`, and `pinned-exception`
- explicit realignment review plans that separate safe draft refresh from stronger bind/materialization review
- explicit exception-pin receipts proving that a non-current outcome was intentionally kept
- explicit non-effects so realignment never pretends to rebind or rematerialize subjects that were not actually reviewed



## 16av) Multi-carrier share convenience still leaves canonical artifact identity too implicit

Current Resilio docs still make the remaining seam concrete without yet turning it into one explicit contract.
`Link structure and flow` says a Sync link uses an `https://link.resilio.com/...#...` wrapper, that the landing page may rewrite that wrapper into `btsync://` so the Sync app can open it, and that parameters after `#` are not actually sent to the Resilio server.
`Sync Share Dialog (Desktop)` says the same folder may be shared as a link or QR code and copied into e-mail or messenger, while the desktop syncing guide says links can be clicked in a browser, pasted into Sync manually, or delivered through ordinary channels.
Taken together, those current docs still leave one missing operator answer once several carriers for the same invitation are in flight:

- whether browser wrapper URL, protocol rewrite, QR rendition, and copied text are the same portable artifact or several
- whether re-encoding the same offer for another carrier started a fresh budget island or merely created another alias
- whether the last-seen carrier is authority-bearing or only a delivery wrapper
- when a familiar-looking carrier is actually a later successor with changed scope or policy instead of just another alias of the old offer

AnonSync should preserve the useful part — practical multi-carrier sharing.
It should not clone a surface where carrier form silently stands in for canonical artifact identity.
The product should publish one explicit carrier-alias equivalence surface that says, in order, canonical artifact now, carrier observed here, other known aliases, why same/not same, what definitely did not change, and the receipt proving that judgment.

### Requirement 85 — canonical artifact identity must stay separate from carrier convenience

If the operator still has to combine wrapper URL shape, QR screenshots, copied text, and browser/app history to answer `is this the same offer?`, the product has not actually exposed portable-offer truth.

AnonSync should instead publish one public model with:

- explicit carrier kinds such as `wrapper-url`, `protocol-url`, `qr-payload`, `clipboard-text`, `mail-body-copy`, and `local-file-envelope`
- explicit carrier-authority postures such as `authority-bearing`, `delivery-wrapper`, `preview-only-copy`, `truncated`, and `ambiguous`
- explicit equivalence postures such as `same canonical artifact`, `same artifact delivery-only alias`, `same artifact authority-bearing alias`, `successor not alias`, and `cannot prove yet`
- explicit normalization basis so clients can explain what semantic fields matched and which differences were delivery-only
- explicit non-effects so delivery-only re-encoding never silently creates fresh budget, fresh trust lineage, or successor lineage
- durable carrier-alias receipts proving why several different-looking carriers were collapsed into one canonical offer or forked into a successor instead


## Conclusion addendum from this pass

The reason not to clone Resilio is now even less about raw capability and even more about how long-lived change is operationalized.
Resilio clearly proves that standing defaults, automatic visibility, later auto-connect, and low-friction arrival handling are useful.
What AnonSync should not copy is the way the operator still has to infer, after several standing-policy edits, which live differences are intentional and which deserve refresh.

AnonSync should therefore preserve:

- standing seat defaults and remembered convenience as operator aids
- strong selective materialization and low-friction arrival flows
- future-only policy changes and practical defaults

But it should reject:

- any design where `current settings` plus lineage is considered enough operational truth after the estate has drifted
- any design where a mix of grandfathered subjects, safe refresh candidates, and risky bind cases collapses into one vague `Reconnect` or `Apply defaults` story
- any design where intentional divergence lacks a durable exception or keep-grandfathered receipt


## 16an) Remembered approval and intentional exceptions still lack one first-class review-horizon contract

Resilio's current docs still make this seam unusually concrete.
`Sync functionality in detail` still says you only need to approve a person once by default because Sync retains a certificate with their identity for later sharing.
`Sync Private Identity & Linking My Devices` still says a remote user can choose to auto-approve all linked devices for future sharing after approving one, and that all folders become visible across linked devices.
`Folder Types and Management` still says previously approved peers can have later pending folders auto-connect when one of their devices is online.

That is real convenience.
But once remembered approval and intentional older outcomes exist for a while, current docs still do not appear to expose one explicit review-horizon answer to:

- which remembered approval or intentional exception is still considered healthy
- which is nearing its review horizon or overdue for reconsideration
- whether horizon reach means silent auto-connect, silent continued grandfathering, or a visible re-review queue
- which receipt proves that an older non-current outcome was renewed deliberately rather than simply left behind

AnonSync should therefore not stop at drift and realignment.
It should also publish one public exception-aging and re-review contract.

### Requirement 77 — intentional non-current outcomes need explicit aging, renewal, and re-review

If the operator still has to combine `approved once`, linked-device auto-approval, later auto-connect, current drift rows, and memory to answer `is this old exception still intentionally allowed, when must it be reviewed again, and what happens when that horizon is reached?`, the product has not actually exposed its long-lived standing-memory contract.

AnonSync should instead publish one public model with:

- explicit review-horizon state for each pinned exception or reviewed keep-grandfathered outcome
- explicit aging classes such as `healthy`, `due-soon`, `overdue`, `blocked`, and `no-expiry-acknowledged`
- explicit re-review plans that separate `renew under same exception`, `return to current policy`, and `keep without expiry` into distinct reviewed outcomes
- explicit non-effects so horizon reach never silently rebinds paths, rematerializes bytes, or widens authority without review
- durable receipts proving whether an intentional divergence was renewed, intentionally allowed to continue without expiry, or returned to current policy



## 16av) Multi-carrier share convenience still leaves canonical artifact identity too implicit

Current Resilio docs still make the remaining seam concrete without yet turning it into one explicit contract.
`Link structure and flow` says a Sync link uses an `https://link.resilio.com/...#...` wrapper, that the landing page may rewrite that wrapper into `btsync://` so the Sync app can open it, and that parameters after `#` are not actually sent to the Resilio server.
`Sync Share Dialog (Desktop)` says the same folder may be shared as a link or QR code and copied into e-mail or messenger, while the desktop syncing guide says links can be clicked in a browser, pasted into Sync manually, or delivered through ordinary channels.
Taken together, those current docs still leave one missing operator answer once several carriers for the same invitation are in flight:

- whether browser wrapper URL, protocol rewrite, QR rendition, and copied text are the same portable artifact or several
- whether re-encoding the same offer for another carrier started a fresh budget island or merely created another alias
- whether the last-seen carrier is authority-bearing or only a delivery wrapper
- when a familiar-looking carrier is actually a later successor with changed scope or policy instead of just another alias of the old offer

AnonSync should preserve the useful part — practical multi-carrier sharing.
It should not clone a surface where carrier form silently stands in for canonical artifact identity.
The product should publish one explicit carrier-alias equivalence surface that says, in order, canonical artifact now, carrier observed here, other known aliases, why same/not same, what definitely did not change, and the receipt proving that judgment.

### Requirement 85 — canonical artifact identity must stay separate from carrier convenience

If the operator still has to combine wrapper URL shape, QR screenshots, copied text, and browser/app history to answer `is this the same offer?`, the product has not actually exposed portable-offer truth.

AnonSync should instead publish one public model with:

- explicit carrier kinds such as `wrapper-url`, `protocol-url`, `qr-payload`, `clipboard-text`, `mail-body-copy`, and `local-file-envelope`
- explicit carrier-authority postures such as `authority-bearing`, `delivery-wrapper`, `preview-only-copy`, `truncated`, and `ambiguous`
- explicit equivalence postures such as `same canonical artifact`, `same artifact delivery-only alias`, `same artifact authority-bearing alias`, `successor not alias`, and `cannot prove yet`
- explicit normalization basis so clients can explain what semantic fields matched and which differences were delivery-only
- explicit non-effects so delivery-only re-encoding never silently creates fresh budget, fresh trust lineage, or successor lineage
- durable carrier-alias receipts proving why several different-looking carriers were collapsed into one canonical offer or forked into a successor instead


## Conclusion addendum from this pass

The reason not to clone Resilio is now even less about raw capability and even more about lifecycle truth.
Resilio clearly proves that remembered approval, later auto-connect, linked-device convenience, and strong selective materialization are useful.
What AnonSync should not copy is the way long-lived remembered convenience still lacks one explicit review-horizon, renewal, and re-review surface.

AnonSync should therefore preserve:

- remembered convenience where it materially reduces routine friction
- strong selective materialization and low-friction arrival handling
- practical standing defaults and future-reaching review where the operator truly asked for them

But it should reject:

- any design where intentional non-current outcomes can sit forever without a visible aging state
- any design where reaching a review horizon silently mutates binds, bytes, or authority instead of opening reviewed next steps
- any design where `approved once` or `keep grandfathered` is treated as enough audit story for later months of behavior

## 16ao) Constellation mutation still lacks one explicit remembered-trust rebase surface

This is the trust-family seam this revision cares about most.
Resilio's current docs still make the problem concrete without yet turning it into one public contract. `Sync Private Identity & Linking My Devices` says all linked devices automatically get all folders, a remote user can auto-approve all linked devices for future sharing after approving one, approvals can be issued from any linked device where the folder is active, linking already-initialized devices can cause one device to lose its certificate and take over the other's identity and configured shares, and you still cannot remotely unlink other devices. `User Management` still says all devices linked to one identity act as Owners. `How to clear offline devices? (desktop only)` says clearing an offline linked device only hides it from view and that it will reappear and continue sharing if it later comes back online.

That is powerful convenience.
It is also a very specific reason not to clone the surface.
The operator question `does this old remembered approval still travel unchanged after the constellation underneath it changed?` is still not answered by one first-class rebase surface.
The operator still has to reconstruct whether old trust should:

- continue unchanged across the current descendant set
- cool or freeze for hidden/reappeared members
- split into child families after certificate takeover or re-link
- require fresh approval for some descendants while preserving historical explanation for past matches
- or revoke entirely

AnonSync should do better.
The product should preserve the convenience mechanics while insisting on one explicit family-rebase surface that says, in order, what mutation triggered re-evaluation, which descendants still inherit the family, which do not, what definitely is not happening automatically, and what receipt later proves the split/freeze/fresh-required outcome.

### Requirement 78 — remembered approval must expose family split/rebase after constellation mutation

If the operator still has to combine approval history, linked-device lists, hidden-offline state, unlink/relink lore, and identity-epoch memory to answer `does this old approval still apply to this changed device constellation, and to which descendants?`, the product has not actually exposed its long-lived trust-boundary contract.

AnonSync should instead publish one public model with:

- explicit rebase rows for remembered-approval families affected by constellation or identity mutation
- explicit mutation classes such as `linked-device-added`, `hidden-device-reappeared`, `certificate-takeover`, `unlink-observed`, and `identity-epoch-changed`
- explicit descendant postures such as `inherits unchanged`, `inherits cooled`, `inherits frozen`, `fresh required`, `split into child family`, `revoked`, and `unknown`
- explicit reviewed outcomes that keep `carry one family forward`, `split into child families`, `freeze descendants`, `require fresh approval for selected descendants`, and `revoke family` distinct
- explicit non-effects so rebase work never pretends to renew trust freshness, claim arrivals, bind paths, or materialize bytes on its own
- durable rebase receipts proving what changed, for whom, and why



## 16av) Multi-carrier share convenience still leaves canonical artifact identity too implicit

Current Resilio docs still make the remaining seam concrete without yet turning it into one explicit contract.
`Link structure and flow` says a Sync link uses an `https://link.resilio.com/...#...` wrapper, that the landing page may rewrite that wrapper into `btsync://` so the Sync app can open it, and that parameters after `#` are not actually sent to the Resilio server.
`Sync Share Dialog (Desktop)` says the same folder may be shared as a link or QR code and copied into e-mail or messenger, while the desktop syncing guide says links can be clicked in a browser, pasted into Sync manually, or delivered through ordinary channels.
Taken together, those current docs still leave one missing operator answer once several carriers for the same invitation are in flight:

- whether browser wrapper URL, protocol rewrite, QR rendition, and copied text are the same portable artifact or several
- whether re-encoding the same offer for another carrier started a fresh budget island or merely created another alias
- whether the last-seen carrier is authority-bearing or only a delivery wrapper
- when a familiar-looking carrier is actually a later successor with changed scope or policy instead of just another alias of the old offer

AnonSync should preserve the useful part — practical multi-carrier sharing.
It should not clone a surface where carrier form silently stands in for canonical artifact identity.
The product should publish one explicit carrier-alias equivalence surface that says, in order, canonical artifact now, carrier observed here, other known aliases, why same/not same, what definitely did not change, and the receipt proving that judgment.

### Requirement 85 — canonical artifact identity must stay separate from carrier convenience

If the operator still has to combine wrapper URL shape, QR screenshots, copied text, and browser/app history to answer `is this the same offer?`, the product has not actually exposed portable-offer truth.

AnonSync should instead publish one public model with:

- explicit carrier kinds such as `wrapper-url`, `protocol-url`, `qr-payload`, `clipboard-text`, `mail-body-copy`, and `local-file-envelope`
- explicit carrier-authority postures such as `authority-bearing`, `delivery-wrapper`, `preview-only-copy`, `truncated`, and `ambiguous`
- explicit equivalence postures such as `same canonical artifact`, `same artifact delivery-only alias`, `same artifact authority-bearing alias`, `successor not alias`, and `cannot prove yet`
- explicit normalization basis so clients can explain what semantic fields matched and which differences were delivery-only
- explicit non-effects so delivery-only re-encoding never silently creates fresh budget, fresh trust lineage, or successor lineage
- durable carrier-alias receipts proving why several different-looking carriers were collapsed into one canonical offer or forked into a successor instead


## Conclusion addendum from this pass

The reason not to clone Resilio is now even less about raw capability and even more about trust-family continuity under change.
Resilio clearly proves that identity-level convenience, later auto-connect, and linked-device breadth are useful.
What AnonSync should not copy is the way remembered trust can remain too monolithic even after certificate takeover, hidden-device return, or other constellation change.

AnonSync should therefore preserve:

- remembered convenience where it materially reduces routine friction
- explicit identity/fingerprint posture and later provenance
- practical linked-device ergonomics where they do not blur trust boundaries

But it should reject:

- any design where old remembered approval silently follows a changed constellation without a reviewed branch/split/freeze decision
- any design where hidden-device return or certificate takeover is just device-list housekeeping instead of trust-family fallout
- any design where future reuse and historical explanation are treated as the same thing after the underlying identity/device shape has changed

## 16aq) Portable offers still leave sender intent versus actual redeemer too reconstructive

This is the last portable-offer seam this revision cares about most.
Current Resilio docs still make the problem concrete without yet turning it into one first-class contract. `Sync Share Dialog (Desktop)` says a share link can be copied to clipboard and pasted into messenger or e-mail, and that with approval disabled any peer who gets the link will connect automatically. `Comprehensive guide to syncing (Desktop-Desktop)` says the key or link can be sent using any convenient and trusted way. `Link structure and flow` then says the actual redeemer sends its locally generated public key, the approval dialog shows that redeemer's user name and fingerprint, and successful approval mints certificate-backed access and an ACL entry.

That is good security relative to the actual requester.
It is also a very specific reason not to clone the surface.
The operator question `who was this offer meant for, who actually redeemed it, did that mismatch matter, and what trust did that exact redemption create?` is still not answered by one first-class surface.
The operator still has to reconstruct whether:

- the offer was intentionally portable-open or only casually forwarded
- the sender had one expected recipient in mind
- the actual requester matched that expectation exactly, loosely, or not at all
- a mismatch was accepted only for this subject or silently promoted into broader remembered approval
- later convenience traces back to the exact redeemer or only to folklore about the old offer

AnonSync should do better.
The product should preserve portable link convenience while insisting on one explicit recipient-intent and redeemer-identity surface that says, in order, what the sender meant, who actually redeemed, how strong the match claim is, what mismatch outcome was reviewed, what definitely is not being implied, and what receipt later proves the durable-trust boundary.

### Requirement 79 — portable-offer redemption must expose sender intent, actual redeemer, and mismatch outcome explicitly

If the operator still has to combine `copied link`, approval-dialog history, and later remembered approval to answer `who was this offer for, who really redeemed it, and did I intentionally let that redemption create durable trust anyway?`, the product has not actually exposed its portable-offer trust-boundary contract.

AnonSync should instead publish one public model with:

- explicit recipient-intent posture for every portable offer that can be forwarded or redeemed by possession
- explicit actual-redeemer identity with named proof basis such as approval-request fingerprint, claim proof, or reviewed family evidence
- explicit match classes such as `matches reviewed seat`, `matches expected family`, `matches hint only`, `unexpected redeemer`, `forwarded redeemer`, and `unknown`
- explicit reviewed outcomes that keep `accept as expected`, `accept subject only`, `accept reviewed seat only`, `reject mismatch`, `reissue for named recipient`, and `freeze explanation only` distinct
- explicit non-effects so accepting one mismatch never silently binds a path, materializes bytes, or promotes broader remembered approval beyond the reviewed outcome
- durable receipts proving the offer artifact, the actual redeemer, the mismatch decision, and any later trust-promotion or trust-freeze result



## 16av) Multi-carrier share convenience still leaves canonical artifact identity too implicit

Current Resilio docs still make the remaining seam concrete without yet turning it into one explicit contract.
`Link structure and flow` says a Sync link uses an `https://link.resilio.com/...#...` wrapper, that the landing page may rewrite that wrapper into `btsync://` so the Sync app can open it, and that parameters after `#` are not actually sent to the Resilio server.
`Sync Share Dialog (Desktop)` says the same folder may be shared as a link or QR code and copied into e-mail or messenger, while the desktop syncing guide says links can be clicked in a browser, pasted into Sync manually, or delivered through ordinary channels.
Taken together, those current docs still leave one missing operator answer once several carriers for the same invitation are in flight:

- whether browser wrapper URL, protocol rewrite, QR rendition, and copied text are the same portable artifact or several
- whether re-encoding the same offer for another carrier started a fresh budget island or merely created another alias
- whether the last-seen carrier is authority-bearing or only a delivery wrapper
- when a familiar-looking carrier is actually a later successor with changed scope or policy instead of just another alias of the old offer

AnonSync should preserve the useful part — practical multi-carrier sharing.
It should not clone a surface where carrier form silently stands in for canonical artifact identity.
The product should publish one explicit carrier-alias equivalence surface that says, in order, canonical artifact now, carrier observed here, other known aliases, why same/not same, what definitely did not change, and the receipt proving that judgment.

### Requirement 85 — canonical artifact identity must stay separate from carrier convenience

If the operator still has to combine wrapper URL shape, QR screenshots, copied text, and browser/app history to answer `is this the same offer?`, the product has not actually exposed portable-offer truth.

AnonSync should instead publish one public model with:

- explicit carrier kinds such as `wrapper-url`, `protocol-url`, `qr-payload`, `clipboard-text`, `mail-body-copy`, and `local-file-envelope`
- explicit carrier-authority postures such as `authority-bearing`, `delivery-wrapper`, `preview-only-copy`, `truncated`, and `ambiguous`
- explicit equivalence postures such as `same canonical artifact`, `same artifact delivery-only alias`, `same artifact authority-bearing alias`, `successor not alias`, and `cannot prove yet`
- explicit normalization basis so clients can explain what semantic fields matched and which differences were delivery-only
- explicit non-effects so delivery-only re-encoding never silently creates fresh budget, fresh trust lineage, or successor lineage
- durable carrier-alias receipts proving why several different-looking carriers were collapsed into one canonical offer or forked into a successor instead


## Conclusion addendum from this pass

The reason not to clone Resilio is now even less about raw capability and even more about offer redemption truth.
Resilio clearly proves that portable sharing plus fingerprint-based approval review are useful.
What AnonSync should not copy is the way sender intent, actual redeemer identity, and durable trust promotion still have to be reconstructed from separate share, approval, and later reuse surfaces.

AnonSync should therefore preserve:

- portable offer mechanics that work through ordinary channels
- strong approval-time identity/fingerprint review
- certificate-backed durable trust where the operator truly chose it

But it should reject:

- any design where `whoever redeemed it successfully` silently stands in for `who I meant this for`
- any design where accepting an unexpected redeemer for one subject quietly creates broader remembered approval for later unrelated subjects
- any design where a historical offer cannot be traced back to one actual redeemer and one explicit mismatch outcome


## 16ar) Multi-use portable offers still leave budget consumption versus per-redeemer trust too reconstructive

Current Resilio docs still make the problem concrete without yet turning it into one first-class contract. `Sync Share Dialog (Desktop)` says a peer who gets the link may connect automatically when approval is disabled, previously approved peers may be granted access automatically under `Only new peers`, `All peers` can still require fresh approval for another shared folder, and a link may be used only `N` times, with each `N+1` attempt by whoever failing. `Link structure and flow` then says the actual requester sends a public key, approval identifies that requester by user name and fingerprint, and successful approval generates certificate-backed access plus an ACL entry.

Taken together, those current docs still leave one missing operator answer once a portable offer has more than one possible use:

- which exact attempts consumed the artifact's shared budget
- which redeemer hit each attempt slot
- which attempts were auto-admitted, freshly approved, rejected, expired, or budget denied
- which successful attempt created which later remembered approval or only subject-local trust
- whether the safest next action is to keep using the partially consumed artifact or reissue a clean new one

AnonSync should preserve the useful part — explicit offer budgets and portable convenience — while refusing the reconstructive part.
The product should publish one explicit redemption-ledger surface that says, in order, artifact budget, ordered attempts, per-attempt budget effect, per-attempt trust consequence, explicit non-effects, and receipts proving the whole chain.

### Requirement 80 — multi-use portable offers must expose a redemption ledger and per-attempt trust fanout

If a portable artifact can be redeemed more than once, the product must render:

- total redemption limit, consumed count, remaining count, and terminal posture (`active`, `partially consumed`, `consumed`, `expired`, `revoked`, `superseded`)
- one ordered attempt ledger naming actual redeemer, proof basis, attempt outcome, and whether that attempt consumed budget
- one per-attempt trust result naming whether the success stayed subject only, seat only, broader, frozen, or explanation only
- one honest distinction between `rejected`, `expired denied`, and `budget denied`
- one prominent safe action when mixed history suggests `reissue new artifact` is safer than stretching the old one further
- durable receipts proving artifact budget state and the trust consequence of each successful attempt

What AnonSync should borrow is the useful part of count-limited portable offers.
What AnonSync should not copy is the way a human can otherwise end up reconstructing from use-count settings, approval dialogs, and later trust memory which identities actually consumed the artifact and what trust survived from each.

### Requirement 81 — artifact budget and trust meaning must never collapse into one generic link status

A surface that says only `link active`, `link used twice`, or `accepted by 2 peers` is not enough.
AnonSync should instead keep artifact-budget truth and per-redemption trust truth adjacent but distinct.

That means:

- partially consumed is its own stable state rather than a hidden counter under `still active`
- a failed over-budget attempt must stay visibly different from a reviewed rejection
- later remembered approval must trace back to one exact successful attempt, not merely to the artifact as a whole
- dense/mobile surfaces may compress counts, but they may not collapse several redeemers into one vague accepted audience

## 16at) Flat `N uses by whoever` budgets still leave redemption-equivalence accounting too reconstructive

Current Resilio docs still make the remaining seam concrete without yet turning it into one explicit contract.
`Sync Share Dialog (Desktop)` says a link may be used only `N` times, with each `N+1` attempt by whoever failing; says `Only new peers` may reuse prior approval automatically; and says `All peers` can still force fresh approval for another shared folder.
`Link structure and flow` and the desktop syncing guide still say the actual requester is identified during approval and successful approval mints certificate-backed access plus an ACL entry.

Taken together, those current docs still leave one missing operator answer once a portable artifact has more than one relevant attempt in history:

- whether a later attempt is just a replay of an already-accounted admission
- whether the same reviewed seat hitting the artifact again should collapse into the earlier slot or consume another one
- whether a different descendant in the same remembered family should count as equivalent enough to collapse
- whether a known/approved redeemer arriving for a genuinely new governed subject should still consume a fresh slot
- when the safest next action is no longer `keep using the same artifact`, but `issue a new artifact and stop stretching the old one`

AnonSync should preserve the useful part — bounded-use portable offers and approval reuse where genuinely intended — while refusing the reconstructive part.
The product should publish one explicit redemption-equivalence surface that says, in order, remaining budget, closest earlier comparable attempt, equivalence class, governing accounting policy, slot effect, non-effects, and receipts proving the decision.

### Requirement 82 — multi-use artifacts must expose redemption-equivalence and slot-treatment explicitly

If a portable artifact may be hit more than once by the same redeemer, a related redeemer, or a known redeemer on a new subject, the product must render:

- which earlier attempt is being compared against
- the current equivalence class (`replay equivalent`, `same reviewed seat`, `same reviewed family`, `same known peer new subject`, `distinct reviewed seat`, `unexpected distinct redeemer`, `unknown`)
- the governing accounting policy (`collapse replay`, `collapse reviewed seat repeat`, `consume per reviewed seat`, `consume per successful subject admission`, `require new artifact after first success`, or another equally explicit class)
- whether the current attempt collapses into an earlier slot, consumes a fresh slot, or is blocked pending reissue
- what trust, if any, may still survive without changing slot count
- durable receipts proving the equivalence judgment and resulting slot treatment

### Requirement 83 — `already approved` must not silently answer the slot-accounting question

A surface that says only `already approved`, `same person`, or `known device` is not enough.
AnonSync should instead keep identity familiarity and budget accounting adjacent but distinct.

That means:

- same-human or same-family hints do not prove same reviewed seat
- same reviewed seat does not automatically imply the governed subject is equivalent enough to collapse
- consuming a fresh slot does not automatically imply the redeemer was suspicious or unexpected
- requiring a new artifact does not revoke earlier successful admissions or their receipts


### 10) Reissue still needs an explicit predecessor/successor boundary

Current Resilio docs still say a share link can expire after `N` days, can be limited to `N` uses, and that after expiry new peers need a **new link from the folder owner**.
At the same time, current approval docs still say you only need to approve a person once by default because Sync retains a certificate with their identity, while a stricter setting can still require approval every time for another shared folder.
That is useful, but it still leaves one governance seam too reconstructive:

> when the next safe step is `get a new link`, is that new artifact merely a fresh delivery wrapper, a clean budget reset, a narrowed invitation, or a broader continuation of remembered trust?

AnonSync should keep easy reissue.
It should not clone a surface where successor-artifact meaning has to be inferred from old expiry badges, remembered approval, and later behavior.
The product should expose one explicit predecessor/successor lineage boundary so operators can see what carried forward, what definitely did not, and whether the replacement artifact started a genuinely fresh invitation story.


## 16au) Browser landing pages and app handoff still leave preview authority too reconstructive

Current Resilio docs still make the problem concrete without yet turning it into one first-class contract.
`Link structure and flow` says a clicked Sync link first opens a landing page on the Resilio website that shows only basic folder info such as folder name and approximate size; if the browser has seen Sync links before, the page may immediately transfer the link into the Sync app; and the parameters after `#` are not actually sent to Resilio's server.
`Comprehensive guide to syncing (Desktop-Desktop)` says the default browser may ask permission to run the external Sync application and may remember that choice.
Those current docs are genuinely helpful, but they still leave one operator question too reconstructive:

- how the artifact arrived here in the first place
- what was merely previewed on an external surface before the local app inspected anything
- whether any external service saw only a wrapper URL, only a landing-page hit, or the full authority-bearing artifact
- whether app launch happened automatically because of old browser permission or because of a fresh explicit action now
- which values are still just hints and which are authoritative after local inspection

AnonSync should do better.
The product should preserve the convenience while insisting on one explicit delivery/handoff surface that says, in order, how the artifact arrived, what the preview surface showed, what any external surface could really see, how the local app received it, what is authoritative now, what definitely is not implied, and what receipt later proves the whole boundary.

### Requirement 84 — delivery provenance and preview authority must be explicit for portable offers

If the operator still has to combine `clicked link`, browser launch memory, landing-page preview, and later local inspect state to answer `how did this arrive, what was only previewed, and what is authoritative now?`, the product has not actually exposed its portable-offer intake truth.

AnonSync should instead publish one public model with:

- explicit delivery-channel classes such as `browser auto-handoff`, `browser confirmed launch`, `clipboard paste`, `QR scan`, and `local file open`
- explicit preview-surface classes and preview-field lists so `folder name` and `approx size` remain visibly hint-level unless later inspection proves them
- explicit external-touch posture such as `wrapper only`, `landing page saw request only`, `full artifact exposed`, and `local only`
- explicit preview-authority classes that keep `preview only`, `artifact derived unreviewed`, `locally parsed`, `locally inspected`, and `receipt backed` distinct
- explicit non-effects so browser auto-open, landing-page display, or QR preview never silently claim trust, byte availability, or claim readiness
- durable delivery-handoff receipts proving how the artifact crossed surfaces and when authority actually became local and inspectable



## 16av) Multi-carrier share convenience still leaves canonical artifact identity too implicit

Current Resilio docs still make the remaining seam concrete without yet turning it into one explicit contract.
`Link structure and flow` says a Sync link uses an `https://link.resilio.com/...#...` wrapper, that the landing page may rewrite that wrapper into `btsync://` so the Sync app can open it, and that parameters after `#` are not actually sent to the Resilio server.
`Sync Share Dialog (Desktop)` says the same folder may be shared as a link or QR code and copied into e-mail or messenger, while the desktop syncing guide says links can be clicked in a browser, pasted into Sync manually, or delivered through ordinary channels.
Taken together, those current docs still leave one missing operator answer once several carriers for the same invitation are in flight:

- whether browser wrapper URL, protocol rewrite, QR rendition, and copied text are the same portable artifact or several
- whether re-encoding the same offer for another carrier started a fresh budget island or merely created another alias
- whether the last-seen carrier is authority-bearing or only a delivery wrapper
- when a familiar-looking carrier is actually a later successor with changed scope or policy instead of just another alias of the old offer

AnonSync should preserve the useful part — practical multi-carrier sharing.
It should not clone a surface where carrier form silently stands in for canonical artifact identity.
The product should publish one explicit carrier-alias equivalence surface that says, in order, canonical artifact now, carrier observed here, other known aliases, why same/not same, what definitely did not change, and the receipt proving that judgment.

### Requirement 85 — canonical artifact identity must stay separate from carrier convenience

If the operator still has to combine wrapper URL shape, QR screenshots, copied text, and browser/app history to answer `is this the same offer?`, the product has not actually exposed portable-offer truth.

AnonSync should instead publish one public model with:

- explicit carrier kinds such as `wrapper-url`, `protocol-url`, `qr-payload`, `clipboard-text`, `mail-body-copy`, and `local-file-envelope`
- explicit carrier-authority postures such as `authority-bearing`, `delivery-wrapper`, `preview-only-copy`, `truncated`, and `ambiguous`
- explicit equivalence postures such as `same canonical artifact`, `same artifact delivery-only alias`, `same artifact authority-bearing alias`, `successor not alias`, and `cannot prove yet`
- explicit normalization basis so clients can explain what semantic fields matched and which differences were delivery-only
- explicit non-effects so delivery-only re-encoding never silently creates fresh budget, fresh trust lineage, or successor lineage
- durable carrier-alias receipts proving why several different-looking carriers were collapsed into one canonical offer or forked into a successor instead


## Conclusion addendum from this pass

The reason not to clone Resilio is now even less about raw capability and even more about delivery truth.
Resilio clearly proves that browser/app convenience, landing-page previews, and fragment-not-sent link structure are useful.
What AnonSync should not copy is the way `opened in browser` can still sit too close to a vague trust story, or the way wrapper URL, protocol rewrite, QR, and copied text can still feel like separate things without one explicit canonical artifact identity.

AnonSync should therefore preserve:

- practical portable-link delivery through ordinary channels
- clear local-app handoff when the operator really wants convenience
- privacy-preserving separation between wrapper request and authority-bearing fragment where the channel allows it

But it should reject:

- any design where browser preview metadata silently counts as authoritative offer truth
- any design where remembered protocol-launch convenience silently stands in for fresh operator intent or later trust
- any design where the operator cannot tell what external surfaces actually observed during delivery
- any design where carrier convenience silently stands in for canonical artifact identity


## Requirement 86 — preview hints must stay separate from sealed authority-bearing fields

If the operator still has to combine landing-page memory, QR screenshots, copied text, and later app behavior to answer `what did I actually know before local parse?`, the product has not actually exposed portable-offer truth.

AnonSync should instead publish one public model with:

- explicit field semantic roles such as `human-hint`, `artifact-identity`, `delivery-routing`, `authority-bearer`, and `policy-control`
- explicit field exposure postures such as `preview-visible`, `sealed-unparsed`, `locally-parsed-authoritative`, and `delivery-wrapper-only`
- explicit field authority postures such as `hint-only`, `supporting-but-not-sufficient`, `authoritative-after-parse`, and `non-governing`
- explicit later-decision mappings so claim/trust/budget surfaces can say which field classes they actually relied on
- explicit non-inference summaries so previewed label or approximate size never silently stands in for recipient match, byte availability, or approval truth
- durable field-partition receipts proving what was visible, where, and with what authority class

## Conclusion addendum from this pass

The reason not to clone Resilio is now even less about raw capability and even more about field authority truth.
Resilio clearly proves that minimal portable links, landing-page hints, and `#`-fragment separation are useful.
What AnonSync should not copy is the way name/size hints, wrapper mechanics, and sealed authority-bearing fields can still feel like one blended story without one explicit public partition.

AnonSync should therefore preserve:

- practical portable-link delivery through ordinary channels
- useful recognition hints before local parse where policy allows them
- privacy-preserving separation between wrapper request and authority-bearing payload where the channel allows it

But it should reject:

- any design where previewed hints silently count as authoritative claim/trust/budget truth
- any design where sealed authority-bearing fields remain mysterious rather than explicitly named as `not yet parsed`
- any design where alias equivalence erases field-exposure history
- any design where later governance decisions cannot cite the exact field classes they relied on


## Requirement 87 — minimal previews must declare decision sufficiency and omitted governance fields

If a portable-offer preview shows only basic folder info while other current product surfaces still govern permission level, approval policy, expiry, and use-count, the operator should not have to guess whether the preview is enough for anything beyond recognition.

AnonSync should instead publish one public model with:

- explicit preview sufficiency by decision domain (`recognition`, `routing`, `governance`, `trust`)
- explicit omitted-governance field classes such as permission, approval posture, expiry, use count, and trust-promotion policy
- explicit unsafe-inference summaries so `looks familiar` never silently means `safe to proceed`
- explicit next-action language such as `Inspect locally`, `Recognition only`, or `Approval review still required`
- durable preview-sufficiency receipts proving that later governance actions did not rely on preview familiarity alone

## Conclusion addendum from this pass

The reason not to clone Resilio is now even less about field visibility alone and even more about decision sufficiency.
Resilio clearly proves that a small preview can be useful: folder name and approximate size are enough to orient a human before the app takes over. But the same current docs still keep permission level, approval policy, expiration, and use-count controls elsewhere, so a human can easily over-read the preview unless the product makes omission and insufficiency explicit.

AnonSync should therefore preserve:

- quick human-recognition hints before full local parse where policy allows them
- compact delivery previews that do not require a giant review form just to get oriented
- later local parse and review steps for the real governance story

But it should reject:

- any design where a familiar label/size preview silently stands in for permission or approval truth
- any design where omitted governance fields stay invisible rather than being named as missing
- any design where `looks right` becomes the de facto admission policy
