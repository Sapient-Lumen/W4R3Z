from pathlib import Path

root = Path('/mnt/data/work_rev0312/src')
docs = root / 'docs'


def prepend(path: Path, text: str):
    old = path.read_text()
    path.write_text(text.rstrip() + "\n\n" + old)


def append(path: Path, text: str):
    old = path.read_text()
    if not old.endswith('\n'):
        old += '\n'
    path.write_text(old + '\n' + text.rstrip() + '\n')

new_docs = {
    '1012-resilio-invocation-profile-launch-switch-and-runtime-world-fragmentation-evaluation.md': '''# Resilio invocation profile, launch switch, and runtime-world fragmentation evaluation

## Why this pass exists

The archive already had strong pages for runtime seats, state roots, same-host namespaces, control surfaces, and mutation durability.
What it still did not own with one explicit current Resilio memo was a narrower but very ordinary operator seam:

> when I launch this thing with these flags, from this account, in this mode, what world am I actually starting, where will state live, what control exposure follows, and is this a quiet reopen or a different runtime entirely?

Current official Resilio docs still make that seam materially real.
They still say Windows launch switches such as `/config`, `/webui`, `/storage`, `/noinstall`, `/S`, and `/minimized` are available.
They still say Linux/headless launch flags such as `--config`, `--storage`, `--identity`, `--license`, `--nodaemon`, and `--webui.listen` materially change where state lives and who can reach control.
They still say a non-default `storage_path` in config mode creates settings there, that service config mode only works from the service storage, that a service-account switch can expose a new empty-looking world with a different storage folder, and that updating a non-default `/config` or `/storage` launch requires using the same command parameters and the same user to preserve configuration.

That is strong candor.
It is also a good reason not to clone the contract directly.

## What current Resilio still gets right

Current official docs still publish several truths worth borrowing:

- **Launch switches are admitted as semantic, not cosmetic.** The Windows CLI doc still says `/config` starts config mode, `/storage` changes the storage folder, `/webui` forces browser-open on loopback only, `/noinstall` avoids installation and uses the default app-data storage, `/S` hides the program interface, and `/minimized` suppresses the main window while leaving tray access.
- **Linux launch posture is candidly stateful.** The Linux guide still says `--storage` selects where settings, identity, and license live; without it, a `.sync` folder is created in the current directory; `--identity` and `--license` will also use that default storage unless a storage path is supplied; and `--nodaemon` changes whether the process backgrounds itself.
- **Control exposure is admitted as launch-shaped.** The Linux guide still says WebUI listens on `127.0.0.1` by default, can be widened to `0.0.0.0` or a specific interface, and can even fail hard if pinned to a specific interface that later is unavailable.
- **Config mode is admitted as a world selector.** The config-mode guide still says a non-default `storage_path` creates settings there, and service config mode works only when the config file is placed in the service storage.
- **Service-user shifts are admitted as storage-world shifts.** The Windows service troubleshooting guide still says switching to Local System yields a new storage folder, an empty-looking roster, and a re-add / re-share burden.
- **Update continuity is admitted as launch-discipline dependent.** The current v3 update guide still says non-default `/config` or `/storage` launches must be restarted with the same command parameters, and Linux binary installs must be relaunched with the same command-line parameters and the same user to preserve configuration.

That is all good product honesty.
Resilio does not pretend that `start the app` is one flat verb.

## Where current Resilio still stays too article-shaped

### 1) Invocation intent is still reconstructed from flags

The ordinary operator should not have to reconstruct from CLI help, Linux notes, config-mode notes, and service docs whether a launch means:

- same world, visible desktop window
- same world, quiet background session
- same world, loopback-only control endpoint
- same world, LAN-exposed control endpoint
- sibling world through a different storage root
- clean world through an implicit current-directory `.sync`
- service world through a different account
- config-owned world whose values outrank interactive edits

Yet that is still roughly how present-day Resilio explains the territory.

### 2) Hiddenness and sameness still blur together

`/S`, `/minimized`, service launch, headless Linux, and `/webui` browser-open all change what the operator can see.
But some of those are the same durable world made quieter, while others can surface a genuinely different storage or control world.
Current docs preserve that truth, but not as one stable invocation contract.

### 3) State-root choice still looks easier than it is

Current docs are candid that `/storage`, `--storage`, config `storage_path`, current-directory `.sync`, and service-user storage roots materially affect settings, identity, license, and databases.
That means launch itself can be a state-adoption act.
AnonSync should not clone any contract where storage-root selection still reads like a mere expert convenience.

### 4) Exposure and quietness still piggyback on flags instead of reviewed plans

`/webui` implies loopback-only reach.
`--webui.listen 0.0.0.0:8888` exposes LAN reach.
A pinned but unavailable interface can abort startup.
`/S` and `/minimized` change what the operator sees without changing the underlying need for stop truth, drain truth, and proof surfaces.
These are review-worthy launch effects, not only power-user lore.

### 5) Preservation through update still depends on remembered invocation ritual

Current official update docs still say continuity for non-default launches depends on relaunching with the same parameters and same user.
That is operationally correct.
It is also a strong sign that invocation profile is part of durable product truth and should not remain hidden in admin notes.

## What AnonSync should do instead

AnonSync should treat **invocation profile** as a first-class reviewed object.
Launching should still be fast when the decision is low-risk and same-world.
But the product should never pretend that state root, exposure, quietness, and world lineage are merely incidental.

The replacement contract should own five surfaces:

1. **Invocation profile contract sheet**
   - launch intent
   - invocation family
   - state-root authority
   - visibility grade
   - control exposure grade

2. **Launch review**
   - same-world reopen vs sibling-world fork vs clean-world start vs blocked overlap
   - state adoption / continuity effect
   - exposure and visibility deltas
   - required follow-up proofs

3. **Quiet-runtime proof**
   - hidden window vs tray vs service vs headless
   - what still runs
   - how control is reached
   - what stronger `stopped` or `not exposed` sentence is blocked

4. **Launch world preview**
   - chosen storage root
   - config-owned values
   - current-directory or implicit default roots
   - service-account or user-dependent world switch risk

5. **Invocation receipt**
   - reviewed intent
   - actual world opened
   - visibility and exposure posture
   - state-root lineage verdict
   - blocked stronger sentence

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that launch switches, storage roots, loopback-vs-LAN WebUI, service accounts, and same-parameter relaunch discipline materially change the runtime world. But it is not worth cloning the way operators still have to reconstruct, from CLI help, Linux notes, config-mode instructions, service troubleshooting, and update guides, whether a given launch is a quiet same-world reopen, a sibling runtime, a fresh storage world, or a newly exposed control endpoint.''',

    '1013-invocation-profile-contract-sheet-page-launch-intent-world-lineage-visibility-and-control-exposure-interface-spec.md': '''# Invocation profile contract sheet page — launch intent, world lineage, visibility, and control exposure

## Purpose

Show, in one durable place before or immediately after launch, the exact truths an operator may rely on about the runtime they are opening.

This page exists to answer:

- `what launch intent is being applied?`
- `which state world will this invocation use?`
- `how visible or hidden will the runtime be?`
- `what control exposure follows?`
- `what stronger continuity or safety sentence is blocked?`

## Required sections

### 1. Invocation header

Must show:

- invocation profile id
- invocation family (`desktop-visible`, `desktop-minimized`, `silent-background`, `service`, `headless`, `maintenance`, `recovery`, `other`)
- requested intent (`same-world reopen`, `new world`, `inspect only`, `service promotion`, `config-owned boot`, `other`)
- current verdict (`same-world`, `guarded`, `fork`, `blocked`, `unknown`)

### 2. World lineage block

Must show separate rows for:

- chosen state root
- identity lineage
- config authority class
- expected share / subject roster basis
- overlap or collision risk

Each row must publish:

- current value
- provenance
- confidence class
- whether it is safe to treat as same-world continuity

### 3. Visibility block

Must distinguish at least:

- foreground visible
- minimized but locally reachable
- hidden background runtime
- service runtime with external control channel
- headless runtime with local or remote workbench only
- inspect-only / no live mutation surface

This block must answer:

> what will the operator see, and what absence is merely projection absence rather than process absence?

### 4. Control exposure block

Must show:

- listener posture (`loopback-only`, `selected-interface`, `all-interfaces`, `none`, `unknown`)
- reachability scope (`local-seat-only`, `same-host`, `LAN-reviewed`, `broader-reviewed`, `unknown`)
- auth floor
- transport posture
- whether exposure came from standing policy, launch override, or ambient default

### 5. State-root authority block

Must show:

- explicit state-root path or authority handle
- whether the root is default, launch-overridden, config-owned, service-owned, or adopted from an earlier receipt
- whether launch would create a new root if absent
- whether launch is safe only because the root already exists and matches a prior world

### 6. Strongest safe sentence

Examples:

- `This launch reopens the same reviewed state world but with a quieter projection.`
- `This launch will open a sibling runtime because it points at a different state root.`
- `This launch keeps control loopback-only; it does not expose reviewed LAN control.`
- `This launch is blocked because the target root would collide with an existing runtime world.`

### 7. Blocked stronger sentence

Examples:

- `Hidden start means Sync is not really running.`
- `Using a different storage path is just a cosmetic convenience.`
- `Opening browser control means the endpoint is safely reachable from elsewhere.`
- `Foreground absence proves stop.`

## Interaction rules

- any invocation that is not obviously same-world must link to a dedicated review
- hidden or minimized starts must still keep stop-proof and exposure links visible
- world-lineage rows must remain exportable in text and CLI/TUI surfaces
- the page must not bury state-root authority or exposure behind advanced disclosure

## Receipt obligations

Any receipt derived from this page must preserve:

- reviewed invocation family
- requested intent
- world-lineage verdict
- visibility posture
- control-exposure posture
- strongest safe sentence
- blocked stronger sentence''',

    '1014-launch-review-page-same-world-reopen-sibling-fork-clean-start-and-blocked-overlap-interface-spec.md': '''# Launch review page — same-world reopen, sibling fork, clean start, and blocked overlap

## Purpose

Review a non-trivial launch before the product starts a runtime whose world, exposure, or continuity would otherwise be easy to misread.

This page exists to answer:

- `is this the same world or a different one?`
- `will launch preserve current continuity?`
- `is this a safe sibling runtime or a dangerous overlap?`
- `what exactly changes if I proceed?`

## Trigger classes

Open this review when any of the following is true:

- the chosen state root differs from the last reviewed root
- config authority outranks the current interactive world
- launch changes visibility and control exposure together
- service/user switch changes reachable storage or roster basis
- the target world is absent and would be created fresh
- the target world risks overlap with an already-running runtime

## Required sections

### 1. Requested launch

Must show:

- launch verb and origin surface
- requested invocation family
- requested state root or root-selection rule
- requested exposure posture
- whether the operator asked for same-world continuity explicitly

### 2. World comparison

Must compare current reviewed world and candidate world across:

- state root
- identity lineage
- subject roster basis
- config ownership
- runtime principal / service profile

The page must classify the candidate as exactly one of:

- `same-world reopen`
- `same-world quieter projection`
- `same-world exposure change`
- `sibling world`
- `clean world`
- `blocked overlap`
- `unknown; proof insufficient`

### 3. Continuity and fallout

Must publish:

- what continuity survives automatically
- what continuity weakens and why
- whether rebind, relink, or rereview will be required
- whether any existing receipts become weaker or stale

### 4. Exposure and visibility delta

Must show:

- before / after visibility
- before / after listener posture
- before / after auth floor and transport posture
- whether the change creates a wider observer class

### 5. Safe options

Must offer typed actions such as:

- `Proceed as same-world reopen`
- `Proceed and record sibling-world receipt`
- `Create clean world intentionally`
- `Narrow to inspect-only`
- `Abort and reopen current reviewed world`
- `Repair overlap before launch`

### 6. Strongest safe sentence

Examples:

- `Proceeding will create a sibling runtime world; it will not inherit current subject continuity automatically.`
- `Proceeding keeps the same world but widens control exposure and therefore needs a launch receipt.`
- `Launch is blocked until overlap with the existing runtime is resolved.`

### 7. Blocked stronger sentence

Examples:

- `This is just starting the app again.`
- `A different root still means the same node.`
- `Silent launch is harmless because no UI appears.`
- `A clean world can be treated as the same seat once it starts.`

## Action semantics

- `Proceed` must always emit a receipt
- `Abort` may emit a refusal receipt when the case was materially risky
- `Inspect only` must not silently widen exposure or create a fresh mutable world
- `Repair overlap` must route into the overlap / namespace family, not a generic settings editor

## CLI contract

```text
anonsync launch review --profile srv-lan-headless --root /srv/anonsync/state
anonsync launch explain --candidate maintenance-shell
anonsync launch adopt-root --receipt invr_01J...
anonsync launch receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- the operator can create a sibling world without seeing that lineage break
- a visibility-only change and a world-switch look identical
- a blocked overlap still looks like an ordinary `start` button
- exposure widening rides along with launch without a typed delta section''',

    '1015-quiet-runtime-proof-page-hidden-window-background-process-and-control-surface-truth-interface-spec.md': '''# Quiet runtime proof page — hidden window, background process, and control-surface truth

## Purpose

Prove what still exists and what still runs when a runtime is not visibly foregrounded.

This page exists to answer:

- `is the runtime merely quiet or actually absent?`
- `what control surface still exists?`
- `what work can still continue?`
- `what stronger stop or non-exposure sentence is blocked?`

## Required sections

### 1. Runtime quietness class

Must show exactly one current class:

- `foreground-visible`
- `minimized-visible`
- `window-hidden runtime active`
- `service runtime active`
- `headless runtime active`
- `process absent`
- `unknown`

### 2. Surviving surfaces

Must list each surviving surface with reachability and mutability truth:

- local workbench
- browser/local-web surface
n- remote-reviewed control surface
- CLI/TUI attachment
- tray or shell affordance
- none

### 3. Continuing work block

Must publish whether the runtime may still:

- transfer bytes
- publish deletions or structural updates
- index or rescan
- keep sockets/listeners open
- accept control requests
- auto-start later under standing policy

### 4. Quietness provenance

Must show whether quietness comes from:

- operator launch choice
- standing startup policy
- service profile
- headless deployment profile
- crash / abnormal absence
- unknown observation gap

### 5. Strongest safe sentence

Examples:

- `The main window is hidden, but the reviewed service runtime is still active and reachable through loopback control.`
- `This session is minimized only; it is not a stop state.`
- `No live control surface is currently proven, but the last reviewed autostart policy may reopen one later.`

### 6. Blocked stronger sentence

Examples:

- `No window means Sync is stopped.`
- `Silent launch means nothing can still move.`
- `Headless means uncontrolled.`
- `Tray absence proves process absence.`

## Interaction rules

- this page must be reachable from any `quiet`, `hidden`, `background`, or `service` status chip
- stop actions must link out to stop-proof / drain review rather than impersonating visibility changes
- receipt export must keep quietness provenance and continuing-work truth adjacent

## CLI examples

```text
anonsync runtime quietness show
anonsync runtime quietness prove --seat self
anonsync runtime quietness receipt <receipt>
```

## Non-clone conclusion

Resilio's present docs still make operators piece together silent start, minimized UI, service backgrounding, browser-open control, and headless Linux behavior from multiple articles.
AnonSync should instead let `quiet` answer one honest question in one place.''',

    '1016-launch-world-preview-page-state-root-selection-config-authority-and-implicit-world-creation-interface-spec.md': '''# Launch world preview page — state-root selection, config authority, and implicit world creation

## Purpose

Preview the exact runtime world a launch would open or create before start.

This page exists to answer:

- `which root or authority plane will own this launch?`
- `will launch reopen an existing world or create one implicitly?`
- `does config or service storage outrank my interactive expectation?`
- `what is the safe claim ceiling about continuity?`

## Required sections

### 1. Candidate world locator

Must show:

- explicit path, handle, or storage authority
- whether the locator came from default policy, launch override, config, service profile, or recovered receipt
- whether the world already exists and matches a prior reviewed world

### 2. Implicit creation risk

Must classify world creation as:

- `none; existing reviewed world`
- `create-if-missing in reviewed root`
- `implicit current-directory world`
- `implicit app-default world`
- `service-account world`
- `blocked because creation would collide or surprise`

### 3. Config authority ladder

Must show:

- interactive values that will be ignored because config owns them
- config-owned values that will replay at boot
- which controls become inspect-only under this world
- whether a config-owned subject set disables or narrows live control

### 4. World continuity verdict

Must publish:

- same world
- same world but stronger config plane
- sibling world
- clean world
- blocked overlap
- insufficient proof

### 5. Strongest safe sentence

Examples:

- `This launch reuses an existing reviewed state root under the same world lineage.`
- `This launch would create a fresh implicit world in the current directory.`
- `This launch points at a config-owned root whose values outrank current interactive expectations.`

### 6. Blocked stronger sentence

Examples:

- `Default storage is harmless because it will obviously pick the right state.`
- `Any config file beside the binary still means the same interactive world.`
- `Changing user or service account leaves the same root semantics intact.`

## Object model

### `launch_world_candidate`

Fields:

- `launch_world_candidate_id`
- `root_locator`
- `root_authority_class` (`default`, `launch-override`, `config-owned`, `service-owned`, `receipt-derived`, `unknown`)
- `creation_class` (`none`, `create-if-missing`, `implicit-current-dir`, `implicit-app-default`, `service-world`, `blocked`)
- `config_authority_class` (`none`, `partial`, `dominant`, `unknown`)
- `continuity_verdict`
- `generated_at`

### `launch_world_receipt`

Fields:

- `launch_world_receipt_id`
- `candidate_ref`
- `actual_world_ref`
- `root_authority_summary`
- `creation_summary`
- `continuity_summary`
- `recorded_at`

## Design tests

The model is not explicit enough if any of these remain true:

- the product can create a current-directory or app-default world without saying so
- config-owned values outrank the operator silently
- service-account storage changes look like empty-state accidents rather than different worlds
- world creation and world reopening share the same unqualified wording''',

    '1017-invocation-lineage-receipt-page-launch-intent-world-verdict-visibility-and-exposure-delta-interface-spec.md': '''# Invocation lineage receipt page — launch intent, world verdict, visibility, and exposure delta

## Purpose

Preserve durable proof of what launch was reviewed, what world actually opened, and what stronger sentence remained blocked.

## Receipt fields

Must preserve:

- receipt id
- reviewed invocation profile id
- launch origin surface and actor
- requested intent
- chosen world locator / authority class
- world-lineage verdict
- visibility posture before and after, if there was a prior world
- control-exposure posture before and after
- whether the world was reopened, forked, created fresh, narrowed to inspect-only, or blocked
- strongest safe sentence
- blocked stronger sentence
- follow-up obligations
- recorded time

## Required sections

### 1. What was reviewed

Show:

- launch request summary
- reviewed world candidate
- key deltas the operator saw before apply

### 2. What actually opened

Show:

- actual world handle
- actual visibility class
- actual control exposure class
- whether launch used the expected state root

### 3. Continuity ceiling

Show:

- same-world continuity proven
- same-world but quieter projection
- sibling world created
- clean world created
- launch blocked / not applied
- proof weakened by missing or stale observations

### 4. Residue and follow-up

Show:

- pending rebind or relink obligations
- pending exposure hardening or narrowing
- stop-proof or quiet-runtime proof links where relevant
- any receipts this one superseded or reopened

## Example summary lines

- `Reviewed same-world minimized reopen; same world opened; exposure unchanged.`
- `Reviewed LAN-exposed headless start; same root reused; control widened from loopback-only to reviewed LAN.`
- `Reviewed state-root override; sibling world created; prior continuity receipts remain local to the earlier world.`
- `Launch blocked due to overlap risk; no new world opened.`

## Interaction rules

- receipts must be exportable as text without losing world-lineage verdict
- later start/stop/exposure reviews must be able to cite this receipt directly
- a later launch may supersede this receipt, but must not rewrite it

## Non-clone conclusion

Resilio's present docs still require remembered launch ritual to explain later state continuity.
AnonSync should instead make every materially meaningful start produce a durable invocation receipt.'''
}

for name, content in new_docs.items():
    (docs / name).write_text(content.rstrip() + '\n')

prepend(root / 'README.md', '''## Revision addendum — invocation profile, launch truth, and runtime-world proof

This revision continues directly from `rev0311` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **Windows CLI launch switches, Linux/headless launch args, config-mode storage authority, service storage worlds, loopback-vs-LAN WebUI exposure, and update continuity for non-default launches**.
2. Tightens the non-clone line again: borrow Resilio's candor that launch flags and storage roots materially change runtime truth; refuse any contract where the operator still has to reconstruct `what world am I actually starting?` from CLI help, Linux notes, config-mode notes, service troubleshooting, and update instructions.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio invocation-profile truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: invocation profile contract sheet, launch review, quiet-runtime proof, launch world preview, and invocation lineage receipt.
5. Makes one hard product decision explicit: **launch intent becomes a first-class reviewed object whenever it can change world lineage, visibility truth, or control exposure**.
6. Makes another hard product decision explicit: **quietness, backgrounding, and browser-open control are separate truths from state-root continuity**.
7. Makes a third hard product decision explicit: **storage-root selection is state adoption, not a cosmetic convenience knob**.
8. Packages the result as another continuation archive whose new tranche makes the `invocation-profile / world-lineage / quiet-runtime-proof / launch-world-preview / durable-receipt` seam explicit in the reading order and page family.''')

prepend(docs / '00-status.md', '''## Revision addendum — invocation profile, launch switches, and runtime-world proof

This revision continues directly from `rev0311` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **Windows launch switches, Linux/headless launch args, config-owned storage roots, service storage worlds, loopback-vs-LAN control exposure, and update continuity for non-default launches**.
2. Tightens the non-clone line again: borrow Resilio's candor that launch is not one flat verb; refuse any contract where the operator still has to reconstruct `what world am I actually starting, and what control/exposure does that imply?` from several admin articles.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio invocation-profile truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: invocation profile contract sheet, launch review, quiet-runtime proof, launch world preview, and invocation lineage receipt.
5. Makes one hard product decision explicit: **launch intent becomes a first-class reviewed object whenever it can change world lineage, visibility truth, or control exposure**.
6. Makes another hard product decision explicit: **hidden/minimized/service/headless are projection postures, not reliable substitutes for stop or same-world claims**.
7. Makes a third hard product decision explicit: **storage-root choice is state adoption and world selection, not a cosmetic convenience**.
8. Packages the result as another continuation archive whose new tranche makes the `invocation-profile / launch-review / quiet-runtime-proof / launch-world-preview / durable-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present invocation contract**

This time the reason is especially clear around **Windows CLI flags that materially change storage, visibility, or listener scope; Linux defaults that can create a `.sync` world in the current directory; config-mode rules that can create settings in a non-default `storage_path`; service-account shifts that surface a different storage world; and update instructions that preserve continuity only if the operator relaunches with the same parameters and same user**.
Current official materials simultaneously show that:

- the current Windows CLI article still says `/config`, `/webui`, `/storage`, `/noinstall`, `/S`, and `/minimized` materially change how Sync starts.
- the current Linux guide still says `--storage` controls where settings, identity, and license live; without it a `.sync` folder is created in the current directory; `--identity` and `--license` also fall back to that storage unless explicitly redirected; and `--webui.listen` can widen control exposure or even cause shutdown if pinned to an unavailable interface.
- the current config-mode guide still says a non-default `storage_path` creates settings there and that service config mode works only from the service storage.
- the current Windows service troubleshooting guide still says switching to Local System yields a different storage folder and an empty-looking roster that must be re-added and re-shared.
- the current v3 update guide still says non-default `/config` or `/storage` launches must be restarted with the same parameters, and Linux binary installs must be relaunched with the same parameters and the same user to preserve configuration.

That candor is useful.
The invocation contract is the problem.
AnonSync should not clone a world where `start`, `silent`, `minimized`, `service`, `headless`, `browser-open`, and `use this storage root` still require article memory to know whether they preserve the same runtime world.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful distinctions between launch intent, world lineage, quietness, and control exposure are real, but the present contract still hides too much meaning across CLI help, Linux notes, config-mode instructions, service troubleshooting, and update ritual instead of owning invocation profile as one stable page family.**''')

prepend(docs / '10-resilio-sync-evaluation.md', '''## Revision addendum — Resilio invocation profile, launch ritual, and runtime-world fragmentation

Current official Resilio docs are still admirably candid that `starting Sync` is not one flat verb: the Windows CLI page still says `/config`, `/webui`, `/storage`, `/noinstall`, `/S`, and `/minimized` materially change startup shape; the Linux guide still says `--storage` chooses where settings, identity, and license live and that without it `.sync` is created in the current directory; that same Linux guide still says `--webui.listen` defaults to `127.0.0.1`, can widen to all interfaces, and can even shut Sync down if pinned to an unavailable interface; the config-mode guide still says a non-default `storage_path` creates settings there and that service config mode works only from service storage; the Windows service troubleshooting guide still says a Local System switch lands in a different storage folder with no old shares visible; and the current v3 update guide still says non-default `/config` or `/storage` launches and Linux binary installs preserve configuration only if relaunched with the same parameters and the same user. That is valuable operational honesty. It is also a strong non-clone signal, because one ordinary operator answer — `what runtime world am I actually starting, where will state live, and what visibility/exposure consequences follow?` — still depends on hopping between CLI help, Linux notes, config-mode instructions, service troubleshooting, and update ritual instead of one owned page family.

The tighter AnonSync response is therefore: treat **invocation profile** as a first-class reviewed object, make quietness separate from stop truth, make storage-root choice explicit world adoption, and require receipts whenever launch materially changes world lineage, visibility, or control exposure.''')

prepend(docs / '11-resilio-borrow-line-and-non-clone-scorecard.md', '''## Revision addendum — scorecard impact from invocation-profile fragmentation

**Borrow more strongly**

- the candid admission that launch flags and startup arguments can materially change state world and control exposure
- the admission that storage-root choice is not cosmetic
- the admission that loopback-only, selected-interface, and all-interface control listeners are materially different postures
- the admission that preserving configuration across update can depend on relaunching with the same parameters and same user

**Clone less strongly**

- any `start Sync` or `open UI` verb that hides which world is actually being opened
- any `silent` or `minimized` wording that lets visibility masquerade as stop or continuity truth
- any storage-path picker or launch override that does not read like state-world selection
- any product shape where service/headless/CLI/runtime differences still require remembered launch ritual

**New explicit no-clone test**

If an ordinary operator cannot answer `what world did this launch open, what stayed the same, what merely became quieter, and what control exposure now exists?` from one owned page family, the surface fails the AnonSync bar.''')

prepend(docs / '12-resilio-interface-clone-veto-tests-and-page-obligations.md', '''## Revision addendum — clone-veto obligations for invocation profile and launch truth

New veto test added here:

### Launch cannot hide world selection, quietness, or exposure

Reject any interface family where:

- `start` can silently open a different storage world
- hidden/minimized/service/headless projection can impersonate stop or same-world continuity
- browser-open or listener posture changes widen control exposure without one reviewed launch delta
- current-directory or app-default state-root creation can happen without explicit world-creation language
- update / relaunch continuity still depends on remembered parameter ritual instead of a receipt-backed invocation profile

Required AnonSync page family for this seam:

- **Invocation profile contract sheet**
- **Launch review**
- **Quiet runtime proof**
- **Launch world preview**
- **Invocation lineage receipt**''')

prepend(docs / '20-product-direction.md', '''## Revision addendum — product direction after rev0311: invocation profile becomes first-class

This pass locks in another product-direction rule:

- **launch intent is a first-class reviewed object whenever it can change world lineage, visibility, or control exposure**
- **quietness is never allowed to stand in for stop truth**
- **storage-root choice is state adoption, not a cosmetic convenience**
- **invocation receipts preserve which world actually opened so later operators do not need launch folklore**

In practical terms, AnonSync should still feel quick for obvious same-world reopens, but it should refuse Resilio's current burden where operators still have to infer from flags and startup context whether they reopened the same node, forked a sibling runtime, or widened control exposure.''')

prepend(docs / '40-architecture-decisions.md', '''## Revision addendum — architecture decisions for invocation profile

New decisions locked here:

1. the system models **invocation profile** as first-class state
2. the system models **world lineage**, **visibility posture**, and **control-exposure posture** as separate launch-time axes
3. state-root selection compiles to an explicit **world-authority class** rather than an incidental path string
4. hidden/minimized/service/headless starts are architecturally valid but must not weaken stop-proof semantics
5. receipts preserve the **actual world opened**, the **requested intent**, and the **stronger rejected sentence**

**Why:** Current Resilio docs are candid that launch flags, storage roots, loopback-vs-LAN WebUI, service accounts, and same-parameter relaunch discipline materially change runtime truth. Those distinctions are valuable; the scattered explanation path is not.''')

prepend(docs / '50-roadmap.md', '''## Revision addendum — roadmap pressure after rev0311: invocation profile and launch receipts

This tranche adds one more roadmap family that should now be treated as first-class rather than optional polish:

- explicit **invocation profile** surfaces for same-world reopen, sibling-world fork, clean-world start, and blocked overlap
- explicit **quiet-runtime proof** surfaces so minimized/service/headless never impersonate stop
- explicit **launch world preview** surfaces for storage-root authority, config ownership, and implicit world creation
- durable **invocation receipts** so update/relaunch continuity stops depending on remembered flags and service lore

A future milestone should count this family as done only when GUI, local web, and CLI/TUI can all answer the same launch-world question without requiring parameter folklore.''')

prepend(docs / 'sources.md', '''## Revision addendum — invocation profile, launch switches, and runtime-world proof after rev0311

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Windows CLI launch switches, Linux/headless startup arguments, config-mode storage authority, service storage worlds, loopback-vs-LAN WebUI exposure, and update continuity for non-default launches.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that launch flags and startup arguments materially change runtime world, state storage, visibility, and control exposure?

> where do those same current docs still show that the ordinary operator answer about `what world did I just start?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Is there a Command Line Interface (CLI) for Resilio Sync on Windows?` article, which still says `/config`, `/webui`, `/storage`, `/noinstall`, `/S`, and `/minimized` materially change startup behavior.
- Resilio's current `Guide to Linux, and Sync peculiarities` article, which still says `--storage` controls where settings, identity, and license live; that without it `.sync` is created in the current directory; that `--identity` and `--license` also fall back to that storage unless redirected; and that `--webui.listen` defaults to `127.0.0.1`, can widen to all interfaces, and can cause shutdown if pinned to an unavailable interface.
- Resilio's current `Running Sync in configuration mode` article, which still says a non-default `storage_path` creates settings there and that service config mode works only when the config file is placed in the service storage.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says switching to Local System yields a different storage folder, an empty-looking roster, and a re-add / re-share burden; and that service WebUI is loopback-only by default unless reconfigured.
- Resilio's current `Updating installation to Resilio Sync v3` article, which still says non-default `/config` or `/storage` launches and Linux binary installs preserve configuration only when relaunched with the same parameters and same user.

## Additional Resilio official sources emphasized in rev0312

- Is there a Command Line Interface (CLI) for Resilio Sync on Windows?  
  https://help.resilio.com/hc/en-us/articles/205506359-Is-there-a-Command-Line-Interface-CLI-for-Resilio-Sync-on-Windows

- Guide to Linux, and Sync peculiarities  
  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Updating installation to Resilio Sync v3  
  https://help.resilio.com/hc/en-us/articles/31194252837779-Updating-installation-to-Resilio-Sync-v3
''')
