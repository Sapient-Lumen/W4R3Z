## Revision addendum — ciphertext custody, decrypt prerequisites, and encrypted-Archive ceilings after rev0211

Current official Resilio docs are still candid that ciphertext-only custody on untrusted devices is a real product pattern: the active v3 line still runs through `3.1.2.1076`; encrypted folders still exist specifically to keep data on an untrusted peer without revealing plaintext; encrypted destinations still must not be casually non-empty; same-lineage encrypted residue can still be re-synced and moved to Archive; encrypted nodes are still read-only, forced-overwrite, and without Selective Sync; onward sharing from those nodes is still encrypted-only; and later recovery still depends on saved RW/RO keys plus intact database continuity, or on an explicit CLI-style decrypt path.
That is good product honesty.
The ordinary operator problem is still page shape.
Current Resilio still spreads one everyday encrypted-node answer across encrypted-folder guidance, read-only behavior notes, ordinary pre-populated connect guidance, and CLI-style recovery instructions.
AnonSync should therefore copy the candor and replace the page family with four ordinary surfaces:

- `487` for **Encrypted target admission**
- `488` for **Ciphertext custody**
- `489` for **Decrypt recovery**
- `490` for **Encrypted Archive limit**

## Revision addendum — volume capability, metadata fidelity, and degraded fallback after rev0210

Current official Resilio docs are still candid that target volumes are not semantically interchangeable: the active v3 line still runs through `3.1.2.1076`; the maintained xattr docs still keep StreamsList as a real whitelist; FAT32 still lacks alt-stream support; fallback stubs in `.sync/Streams` still stand in when metadata cannot be stored natively; Windows shell actions still depend on NTFS support for alternate streams; and old-but-still-official fix history still records CIFS/SMB no-stream weirdness, exFAT attribute trouble, FAT32 noise, and xattr-delivery bugs.
That is good product honesty.
The ordinary operator problem is still page shape.
Current Resilio still spreads one everyday answer across xattr docs, shell-affordance troubleshooting, hidden-sidecar notes, and old changelog archaeology.
AnonSync should therefore copy the candor and replace the page family with four ordinary surfaces:

- `482` for **Volume capability**
- `483` for **Metadata fidelity**
- `484` for **Affordance ceiling**
- `485` for **Volume repair**

## Latest addendum — capability gates, entitlement basis, and missing-control truth after rev0199

Current official Resilio docs still show a practical product line through `3.1.2.1076`, and they still make a serious case for borrowing capability candor rather than hiding it.
They still repeatedly tell the truth that some features differ by line, entitlement, folder class, seat role, and surface.
They also still tell the truth that a seat can inherit capability from an owner, lose it with the owner, or appear licensed yet still narrow in practice when the host role mismatches the entitlement.

What they still do not make easy enough is one ordinary answer to:

- why is this capability present on this seat and missing on that one?
- what exact basis currently makes this seat entitled?
- is this action absent because of version, entitlement, subject class, surface, or seat rights?
- what exactly stopped when this seat lost Pro behavior, and what bytes or history survived?

That is another strong reason to **adapt, not clone**.
AnonSync should copy Resilio's candor about capability gating and live downgrade side effects, but refuse any interface contract where those answers still depend on cross-reading per-feature availability notes, folder-class comparisons, licensing notes, lost-license troubleshooting, and v3 FAQ prose.


## Latest addendum — byte-presence verbs, placeholder scope, and archive replay after rev0192

Current official Resilio docs still show a practical product line through `3.1.2.1076`, and they still make a serious case for borrowing selective materialization, placeholder vocabulary, folder-level disconnect, and retained-history pragmatism.
What they still do not make easy enough is one ordinary answer to:

- what exactly materializes when I fetch this file, subtree, or disconnected subject?
- what exactly disappears only here when I reclaim local space or disconnect this seat?
- when does Delete mean local reclaim versus global delete?
- when does a retained version from history truly replay, and when does it simply fall back into history again?

That is another strong reason to **adapt, not clone**.
AnonSync should copy Resilio's practicality about placeholders and archive honesty, but refuse any interface contract where byte-presence truth still depends on cross-reading synchronization modes, RSLS instructions, disconnect notes, Archive notes, and overwrite FAQs.

## Latest addendum — seat lineage, identity replacement, and reset/rehome impact after rev0191

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **seat lineage / identity replacement / roster residue / reset impact**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer can depend on:

- whether two already-running installs are being linked in a way that causes certificate takeover
- whether a confusing row is actually hidden-but-still-linked, duplicated by one reset path, or merely offline after uninstall
- whether a credential reset preserves identity and preferences or duplicates device rows and resets globals
- whether a service-world or storage-root move is continuity-preserving or really a fresh empty world that needs re-share and reconnect

So the tighter non-clone line is:

> borrow Resilio's certificate-backed seat identity and its honesty about reset side effects, but refuse any product contract where `is this the same seat?`, `what exactly will this reset preserve?`, and `why does this row look duplicated?` still require archaeology across identity, recovery, service, and cleanup article families.

That yields four more ordinary product-owned pages:

- **Seat lineage**
- **Identity replacement**
- **Device roster**
- **Reset impact**

## Latest addendum — pending approval visibility, approver locus, and remembered-trust drift after rev0190

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **pending approval visibility / approver locus / remembered-trust scope**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer can depend on:

- whether the join happened by key, link, QR, or identity-linked automation
- whether the request is still pending because approval is genuinely outstanding, because remembered trust should have auto-approved later, or because the issuer never saw the request at all
- whether the operator is on the specific issuing seat or merely on a linked seat where the subject is present in `Selective Sync` or `Synced`
- whether the relevant truth is published in the share dialog, the pending-folder icon legend, the desktop guide, the identity guide, the link-flow article, or the route troubleshooting page

So the tighter non-clone line is:

> borrow Resilio's identity-backed approvals, fingerprint review, and remembered-trust convenience, but refuse any product contract where `why is this still pending?`, `who may decide it here?`, `what exactly am I approving?`, and `why did I not get prompted this time?` still require archaeology across article families.

That yields four more ordinary product-owned pages:

- **Pending claim**
- **Claim inspection**
- **Approval authority**
- **Approval memory**

# Resilio Sync evaluation (borrow-line and interface-grammar pass)

## Bottom line

Resilio Sync remains a serious reference point.
Current official docs still show:

- an active v3 line through `3.1.2.1076` in late 2025
- WebUI as the default path on Linux and Windows service installs
- practical link/QR/manual share delivery and linking flows
- disconnected / selective / synced mode language that still compresses real operator intent
- advanced-folder permissions and owner-class mutation
- local same-host share workflows
- encrypted folders for ciphertext-only custody on untrusted nodes
- multi-layer troubleshooting for routes, ports, relays, rates, scheduler, and installation
- transport reachability still spans preferences, power-user knobs, manual pins, and troubleshooting pages

So any AnonSync thesis that depends on `Resilio is abandoned`, `Resilio never solved convenience`, or `Resilio only has old desktop-sync ideas` is weak.

The right question is still:

> what current Resilio evidence gives us a good reason not to clone the interface contract, even while borrowing several of its strongest product ideas?

## Sharper conclusion

The answer is now simpler than it was a few revisions ago.

AnonSync should:

- **borrow** several Resilio product ideas more boldly
- **adapt** several useful Resilio workflows into stronger public objects
- **refuse** the exact clone whenever convenience still fuses distinct truths or spreads one everyday answer across too many surfaces

The product ideas worth stealing are real.
The truth-contract boundaries are real too.

## What Resilio still gets right

### 1) Byte-posture language

`Disconnected`, `Selective Sync`, and `Synced` remain some of the cleanest operator-facing names in the category.
They describe real byte posture differences that people actually reason about.

AnonSync should not reject that language merely to sound original.

### 2) Delivery convenience

Resilio is also right that share delivery needs more than one path:

- link/browser convenience
- QR handoff
- manual paste fallback

A serious sync product needs all three.

### 3) Linux and headless practicality

Resilio is right that a browser/local-web control surface is practical for Linux-heavy and service-heavy installs.
AnonSync should preserve that instinct rather than assuming a desktop shell is primary.

### 4) Encrypted intermediary use case

Resilio is right that ciphertext-only custody on a VPS/NAS/borrowed host is a first-class real-world need, not a weird edge case.

### 5) Same-host derivation is real work

Resilio is also right that users do create same-host downstream copies or side roots deliberately.
That family deserves first-class modeling.

## The best current non-clone reasons

### 1) Resilio's convenience often still arrives as fused state

Resilio's mode story is useful, but it still tends to pull several truths together:

- visibility of a share on a seat
- local path adoption
- current byte materialization
- future default posture for later arrivals
- sometimes even authority expectations

AnonSync should keep the useful byte-posture insight while refusing the fused state contract.

### 2) Several useful families still depend on caveat clusters

The local-share family is the strongest example.
Current docs are candid, but the operator still has to remember a cluster of caveats about:

- self-only peer relation
- owner limitations
- permission narrowing rules
- source-child dependence
- reconnect after source reconnect
- remove/re-share for some permission changes

That is a good reason to remodel the behavior as one lineage/continuity object instead of cloning the current family shape.

### 3) Some everyday answers still live across too many surfaces

The strongest examples remain:

- browser warning pages vs control-endpoint trust meaning
- browser-open handoff vs manual typed intake
- ordinary rates vs LAN exceptions vs scheduler vs config mode
- installation vs elevation/network consent vs runtime start vs control reachability

That is not a condemnation of Resilio.
It is simply a good reason not to inherit the exact interface contract.

## The four previously strong non-clone reasons still stand

### 1) Browser trust for local control still broadens into warning ritual

Current official docs still say Linux and service seats use WebUI as the default control path and that a self-signed certificate can trigger browser warnings.
That means browser control trust is still not one explicit product-owned endpoint-trust object.

AnonSync should therefore expose endpoint class, trust grade, exception posture, and certificate upgrade as one reviewed control-trust workflow.

### 2) Browser-open handoff still degrades into OS/browser ritual or generic paste fallback

Current official docs still say opening a link in a browser can fail and that WebUI cannot use that path, with manual paste into `Enter a key or link` used as the workaround.
That means browser-open is still not a fully reliable typed intake lane.

AnonSync should therefore treat deep-link handoff as an accelerator over one canonical typed intake workflow.

### 3) Rate policy still lives across several layers

Current official docs still say rate limits apply to internet traffic by default, not LAN, unless a power-user option changes that, and scheduler behavior adds another surface.
That means the effective answer still spans ordinary preferences, exception toggles, and schedule state.

AnonSync should therefore keep one effective rate-policy ledger that names the winning layer and surviving side effects.

### 4) Install and first-run readiness still fork across trust and startup moments

Current official docs still say SmartScreen warnings may appear because of code-signing trust state, that service or silent-install paths may still leave consent/startup work, and that install completion does not automatically equal ready control reachability.

AnonSync should therefore treat install and first-run as one attested readiness ladder with receipts.

## New sharpened borrow/adapt/reject view

### Borrow directly

AnonSync should copy these product ideas with little embarrassment:

- visible disconnected / selective / full byte posture
- link / QR / manual delivery triad
- browser-first local control on Linux/headless installs
- encrypted intermediary use case
- same-host derivation as a normal workflow

### Adapt instead of clone

AnonSync should preserve the use case but change the contract for:

- linked-device convenience
- advanced-folder authority editing
- local-share continuity
- browser-open intake
- rate and scheduler controls
- encrypted-node family behavior

### Refuse the clone line

AnonSync should not clone:

- one selector silently deciding visibility, adoption, materialization, and future defaults together
- browser certificate ritual as the main expression of endpoint trust
- successful link-open as proof of authoritative intake
- scattered rate truth across preferences, exceptions, schedule, and config surfaces
- `installed` or `service installed` impersonating `trusted, started, and reachable`

## Practical implication for interface work

This revision therefore treats the interface question as inseparable from the Resilio question.
If we are not cloning Resilio, the product needs better everyday page contracts than `we expose more truth somehow`.

That is why this pass adds focused interface specs for:

- share-list rows
- transfer lanes
- history / restore browser
- conflict inbox

Those are exactly the places where Resilio's strengths are worth learning from, but where AnonSync needs a stricter truth contract.

## Result

The archive now has a better answer to both halves of the pressure test.

### Why copy Resilio at all?

Because several of its product ideas are still very good.

### Why not clone it?

Because several of its most operator-important truths still arrive as fused selectors, caveat clusters, or multi-surface reconstruction tasks.

That is a concrete, current, and defensible reason.

## Four current clone-veto seams that still matter

The deeper current answer is not merely that Resilio has a few rough edges.
It is that four important operator questions still do **not** live in one stable product-owned page contract.

### 1) Control trust

Current official docs still show all of the following at once:

- WebUI as the default control path on Linux and Windows service installs
- self-signed certificate warnings when HTTPS is enabled without a custom certificate
- proceed-unsafely and HSTS-clearing rituals as part of the practical support story
- configuration-file certificate replacement as the stronger path

That means the product idea is right — browser/local-web control is useful — while the page contract is still weaker than AnonSync should accept.

### 2) Typed artifact intake

Current official docs still show deep-link/browser-open convenience, but they also still admit that:

- browser/OS handoff can fail
- WebUI cannot consume the direct link path
- manual paste into a generic intake box is the fallback

That means the delivery idea is right, but the canonical typed intake lane is still too implicit.

### 3) Effective rate truth

Current official docs still show that effective bandwidth posture can depend on:

- ordinary send/receive preferences
- the `rate_limit_local_peers` exception
- scheduler windows and the non-obvious activities that still continue under `Paused`
- configuration-mode declarations

That means the product has real capability, but the everyday answer is still reconstructed.

### 4) Install-to-ready bringup

Current official docs still show that the operator may have to reason separately about:

- package trust / OS reputation warnings
- elevation or service-install consent
- firewall or listener exposure state
- runtime start and browser reachability

That means `installed` and `ready` are still too easy to confuse.

## What this means for AnonSync

The correct response is not to sneer at Resilio.
The correct response is to say:

> we will borrow the useful behavior, but every refusal to clone must point at one better replacement page.

That is why this revision adds page contracts for:

- `Control trust`
- `Import artifact`
- `Rate policy`
- `Finish setup`

Those four pages are not decorative extras.
They are the replacement answer that makes the non-clone line respectable.

## Four further current clone-veto seams after the first page tranche

The earlier pass established that control trust, typed intake, effective rate truth, and install readiness still deserved replacement pages.
A further current Resilio reading shows four more seams just as clearly.

### 5) Byte posture versus future-default truth

Current official docs still use `Disconnected`, `Selective Sync`, and `Synced` in a way that is genuinely useful.
But they also still tie those selectors to default-folder behavior, manual connect flow, and later-arrival handling.
That means one strong idea is still carrying several orthogonal truths.

### 6) Encrypted custody versus recovery truth

Current official docs still make encrypted folders a compelling ciphertext-only intermediary pattern.
But they also still require the operator to remember saved keys, preserved database continuity, read-only posture, overwrite semantics, and CLI/offline decrypt paths.
That means the use case is strong while the page contract is still too caveat-shaped.

### 7) Same-host derivation versus lineage continuity

Current official docs still acknowledge same-host local copies as a real workflow.
But they also still explain it through a cluster of special rules about self-only topology, no owner grant, no nested loops, source-child dependence, and manual reattach after source reconnect.
That means the workflow is real while the continuity model is still not one ordinary page.

### 8) Archive usefulness versus safe-eviction truth

Current official docs still make Archive/versioning genuinely useful.
But they also still split the operator answer across hidden paths, UI availability differences, manual restore, timestamp caveats, and a separate History surface for peer authorship.
That means the capability is useful while the safe-eviction / real-recovery answer is still reconstructed.

## What this means for the next page contracts

That is why this revision adds four more replacement pages:

- `273` — Byte posture
- `274` — Encrypted custody
- `275` — Same-host lineage
- `276` — Fetchability

Together with `269` through `272`, the archive now has a stronger answer to `what exactly are we building instead of cloning Resilio?`


## Four further current clone-veto seams after the second-wave page tranche

A further pass on current official docs still leaves four ordinary questions that Resilio answers usefully but not yet with page contracts AnonSync should clone directly.

### 1) Identity linking versus control-plane takeover

Current linking docs still say one already-configured device can lose its certificate and take over another identity when linking two running instances, with Advanced folders removed from the app on the replaced side and harsher filesystem consequences on iOS.
That means `link device` still deserves explicit empty-seat, successor-import, and takeover language.

### 2) Existing-byte intake versus duplicate repair ritual

Current docs still say default-folder arrival plus same-name collision can create indexed duplicate directories, and the repair path often runs through `Disconnect` then `Connect` and manually selecting the intended path.
That is a strong sign that pre-existing-byte intake deserves one typed page rather than remembered sequence.

### 3) Mutable delegation versus hidden ceiling logic

Current docs still say on-the-fly rights changes are Advanced-only, Standard folders need remove/re-add, linked same-identity devices act as Owners, local children cannot receive Owner, and read-only local drift has special suspend/overwrite behavior.
That is useful power, but it still deserves one explicit rights-ceiling page.

### 4) Useful multi-plane naming versus one ambiguous `folder name`

Current docs still say a local custom name may diverge from the disk folder name, not propagate to linked devices, and yet different labels can be inserted into shared links or QR artifacts.
That flexibility is real.
It is also a strong reason to expose one Name planes page instead of one overloaded rename field.

These four seams are the reason this revision adds replacement pages `277` through `280`.


## Fourth-wave current answer after rev0168

A further current-doc pass shows a different kind of non-clone reason than the earlier trust, custody, and join work.
The strongest remaining issue is not that Resilio lacks useful ideas.
It is that several operator-important truths still live in hidden service material or power-user settings.

### 5) Hidden service material is real, but the page contract is too failure-first

Current docs still say every synced folder gets a hidden `.sync` directory, that deleting or moving it breaks synchronization, and that repair may require removing the share, checking Archive, deleting `.sync`, and re-adding the share.
Another current warning doc also says the same family of failure can come from two Sync instances touching the same folder or external drive.

The product instinct is correct: service material exists and matters.
The weak contract is that operators meet the truth mainly through hidden files and later damage.

### 6) Exclusion policy is strong product power, but still hidden as rule file semantics

Current IgnoreList docs still show real power:

- excluded files are not indexed
- excluded files are not counted in share size
- rules are case-sensitive
- defaults exist already
- peers may diverge intentionally and therefore observe different totals

That is a meaningful policy system.
But the ordinary answer still depends on a hidden UTF-8 rule file and remembered wildcard/root-scope syntax.

### 7) Mutation delay is useful, but still surfaced as storage-folder JSON

Current delay docs still show a valuable idea: some file classes should wait briefly before shipping.
They also still place the policy in FileDelayConfig under the storage folder, with direct JSON edits and restart ritual.
That is a fine escape hatch, not a page contract AnonSync should clone.

### 8) Queue priority is a good idea whose public explanation is still incomplete

The current v3.1.0 download-priority docs are honest in a revealing way.
They still say priority may come from per-share settings or a global power-user default, that local manual override stops following later global changes, that only up to 50,000 active files are prioritized, that some suspension exceptions exist, that non-splittable files do not fully obey strict prioritization, and that the UI list may still look alphabetical instead of true execution order.

That is exactly the kind of feature AnonSync should borrow more boldly while refusing the page contract.
The product idea is right.
The visible explanation surface is still too weak.

## Practical consequence for AnonSync

The fourth-wave answer should now be:

- borrow **explicit service material as a public concept**
- borrow **real exclusion policy with accounting consequences**
- borrow **file-class delay windows**
- borrow **queue-order control where it materially changes operator value**
- refuse any contract where those truths live mainly in hidden directories, text syntax, raw JSON, restart ritual, or execution-order exceptions that the visible list cannot explain

Together with `281` through `284`, the archive now has a stronger answer to `what are we building instead of cloning these Resilio seams?`


## Fifth current clone-veto seam that still matters after rev0169

The deeper current answer is now broader than trust/config families.
It is also that four more ordinary operator questions still do **not** live in one stable product-owned page contract.

### 1) Shell acceleration and parity

Current official docs still show all of the following at once:

- WebUI as the only default UI path on Linux-based machines and the default UI path for Windows service installs
- file-browser context actions that depend on Finder / Explorer extensions and filesystem capabilities
- extension-repair ritual on macOS and DLL/registration ritual on Windows
- platform limits such as NTFS-only context-menu availability

That means the convenience is real, but the semantic home of those actions is still too dependent on shell health.

### 2) Local dematerialization versus global destruction

Current official docs still show all of the following at once:

- `.rsls` placeholders as zero-byte names-only representations
- `Remove from this device` as a local byte-posture change
- deleting a placeholder with read-write access as permanent deletion from all peers
- a power-user control for `Remove from all devices` that is ignored in Linux WebUI
- disconnecting a folder removing local placeholder files

That means the convenience is real, but the gesture family still overloads materially different outcomes.

### 3) Restore access parity

Current official docs still show all of the following at once:

- Archive retention by default for 30 days on desktops and 1 day on mobiles
- manual-only restore
- desktop UI opening Archive directly while WebUI/Android rely on hidden `.sync/Archive`
- no Archive access on iOS
- timestamp/index semantics that still require operator interpretation

That means the recovery idea is real, but the restore contract is still too platform-asymmetric.

### 4) Filesystem-shape fidelity

Current official docs still show all of the following at once:

- Windows link-node families as unsupported and conflict-prone
- Unix symbolic links preserved as links while target folders are not implicitly synced
- xattr policy controlled by hidden `StreamsList`
- hidden `.sync/Streams` stubs when metadata cannot be stored natively
- bundle decomposition risk when xattr syncing is disabled

That means the fidelity idea is real, but the ordinary answer still lives across too many specialist surfaces.

## What this means for AnonSync after rev0169

The correct response is again not to sneer at Resilio.
The correct response is to say:

> we will borrow the useful behavior, but the product owes one ordinary page for shell capability, one for byte-action review, one for history access, and one for filesystem-shape audit.

That is the current, concrete, non-clone line.


## Sixth current clone-veto seam that still matters after rev0170

A further current Resilio pass shows a different remaining non-clone reason than the earlier trust, custody, queue, shell, and filesystem passes.
The strongest remaining issue is not raw transport.
It is that two still-ordinary operator questions are answered honestly only by hopping across several separate articles:

1. **who outside this mesh can learn what exact facts, with what plaintext ceiling?**
2. **which exact local state root defines this node right now, and is an existing root safe to attach or clone-risk?**

### 1) Infrastructure visibility is honest, but not one page

Current official docs still show all of the following at once:

- tracker communicates IP addresses, listening ports, and share IDs
- relay passes encrypted traffic without reading or storing plaintext
- link landing pages can count clicks while not receiving the anchor-fragment payload
- update checks, telemetry, and license/account services are separate points of contact
- these services can be narrowed or disabled through settings/config

That is a respectable architectural story.
It is also a strong reason not to clone the current page contract, because the ordinary answer still requires reconstructing one observer matrix from several separate security/help articles.

### 2) Service-role capability ceilings are still FAQ-shaped

Current official docs still show all of the following at once:

- Resilio team cannot see file content
- Resilio neither hosts nor caches ordinary Sync content
- relay cannot examine encrypted transit
- landing-page infrastructure does not see the unique folder-identification payload after `#`
- vendor infrastructure can still affect discovery, relay fallback, update awareness, or telemetry flow

That means the capability ceilings are described, but not through one ordinary service-role page that states what each service can observe, what it can influence, and what it can never do.

### 3) State-root continuity is real, but still support-shaped

Current official docs still show all of the following at once:

- the storage folder contains configuration, auxiliary settings, share database, logs, and identity details
- default storage location changes by OS, service user, package mode, and config mode
- config mode can create a `.sync` storage folder near the binary/current directory if no explicit `storage_path` is given
- switching a Windows service to another principal can create a new storage location and a seemingly empty inventory

That means local-world continuity is very real, but still not one ordinary page.
The operator still has to infer whether they are in the same world, a different default world, or a wrong-root empty branch.

### 4) Clone-safety versus attach/import still does not earn direct cloning

Current official docs still show all of the following at once:

- cloning a Sync instance is unsupported
- a different storage path creates a different settings world
- service storage changes can require re-add / re-share / reconnect work
- standard install is advised instead of copied-state continuity

That is a practical prohibition.
It is not the page contract AnonSync should clone.
AnonSync should instead let the operator review whether an existing root is same-world attach, successor import, stale backup, clean branch, or clone-risk.

## What this means for AnonSync after rev0170

The correct response is again not to sneer at Resilio.
The correct response is to say:

> we will borrow the architectural honesty, but the product now owes one page for infrastructure visibility, one for service role, one for state root, and one for attach-state review.

That is the current, concrete, non-clone line.



## Seventh current clone-veto seam that still matters after rev0171

A further current Resilio pass shows another remaining non-clone reason than the earlier visibility/state-root work.
The strongest remaining issue is that helper policy and background cadence are both reasonably honest, but still reconstructed from too many separate scope layers and support pages.

1. **what helper stack is actually in force for this subject after folder policy, seat policy, proxy posture, cache, and overrides are combined?**
2. **where did helper/bootstrap knowledge come from, and what stale residue still survives after narrowing?**
3. **which helpers does this peer pair really need, and what exact counterfactual would remove that dependence?**
4. **why is this host awake or stale right now, and which cadence loops are responsible?**

### 1) Helper policy is powerful, but still scope-scattered

Current official docs still show all of the following at once:

- folder preferences carry relay, tracker, LAN-search, and predefined-host controls
- those controls are desktop-only
- global proxy posture is configured elsewhere
- LAN-only operation can require both share-preference changes and config/power-user changes
- troubleshooting adds more route truth again through separate network articles

That is real flexibility.
It is also a strong reason not to clone the current page contract, because the ordinary answer still requires rebuilding one helper-policy stack from multiple places.

### 2) Bootstrap/catalog provenance is explicit, but still too article-shaped

Current official docs still show all of the following at once:

- helper bootstrap comes from `config.resilio.com/sync.conf`
- losing that catalog blocks ordinary tracker/relay discovery
- LAN-only narrowing can still require explicit cache clearing on each desktop
- predefined hosts can substitute for broader discovery in some environments

That means the bootstrap story is documented.
It is still not one ordinary page stating which catalog source is active, what cached residue remains, and what private or manual override replaced the default.

### 3) Pairwise helper dependence is reconstructable, but not one page

Current official docs still show all of the following at once:

- direct connection is preferred
- relay is used when direct connection is impossible
- trackers help peers learn addresses and share IDs
- proxies can create asymmetric directness and, if both peers are behind proxies, relay inevitability
- multiple NICs, multicast failure, and blocked listening ports all change what path is possible

That means pairwise dependence is real.
It is not one ordinary page that distinguishes `relay allowed` from `relay inevitable` or names the exact counterfactual needed for directness.

### 4) Host cadence and quiet-host tuning are still support-lore shaped

Current official docs still show all of the following at once:

- filesystem notifications are fastest but can fail on some storage classes or deep trees
- periodic rescan defaults to 600 seconds and can be changed, even to zero
- watcher exhaustion can force the system back to periodic rescan
- NAS quieting guidance recommends stretching rescan/refresh/save cadence and disabling logging
- peer demand can still wake the host despite local quieting changes

That is good operational honesty.
It is not one ordinary host-cadence page.
The operator still has to infer what is keeping the host awake or stale from a mixture of settings and troubleshooting articles.

## What this means for AnonSync after rev0171

The correct response is again not to sneer at Resilio.
The correct response is to say:

> we will borrow the helper flexibility and background-behavior honesty, but the product now owes one page for helper policy, one for bootstrap source, one for pairwise helper dependence, and one for host cadence.

That is the current, concrete, non-clone line.

## Revision addendum — capability gating, alert delivery, and kind chooser after rev0172

Current official Resilio docs still show a useful but scattered truth in another ordinary product seam:

- v3 requires activation, personal-device reuse is permitted for personal non-commercial use, and some older families remain fenced or risky
- v2/v3 preserve synchronization compatibility, but linked devices should all be on v3 to avoid license conflicts, and Sync Business cannot be updated to v3
- desktop, mobile, Android-permission, and Linux docs still split notification/approval-delivery truth across different surfaces
- creation meaning still depends on separate share dialogs, `+` menus, send/backup articles, and kind-specific platform/edition restrictions

That means the product ideas are useful, but the page contracts still do not earn cloning.

AnonSync should therefore add one-page answers for:

- **Capability source** — what this seat can do, where that capability came from, and what remote or expiry dependence remains
- **Compatibility gate** — whether the contemplated mix is safe, sync-only compatible, risky, or blocked
- **Alert delivery** — which carrier could actually deliver the event, which gate could suppress it, and how missed-event recovery works
- **Subject kind chooser** — what `sync`, `backup`, `send`, `ciphertext custody`, and `same-host derivation` really mean before commitment

## Revision addendum — health, repair, and evidence capture after rev0173

Current official Resilio docs still show another useful but scattered truth in an ordinary product seam:

- operators are expected to inspect status rows, peer columns, and warning links and then branch into troubleshooting articles
- locked files, delayed commit windows, SMB/direct mixed access, and weak change detection are all real but still reconstructed from several different docs
- repair guidance is practical but still split across `Database error`, `Service files missing`, `My files don't sync`, and related warnings
- crash and evidence capture still depends on storage-folder discovery, service-account path differences, restart/reproduction ritual, and self-serve support boundaries

That means the product ideas are useful, but the page contracts still do not earn cloning.

AnonSync should therefore add one-page answers for:

- **Issue home** — what family this symptom belongs to, what evidence floor exists, and the first safe action
- **Environment conflict** — whether this is lock pressure, foreign-writer risk, weak notifications, or a mixture
- **Repair plan** — the least-destructive repair ladder with copy-safety proof and environment preconditions
- **Crash capture** — what private evidence exists, what more capture requires, and what later becomes a frozen disclosure packet


## Revision addendum — path continuity, relocation, disconnected presence, and rename explanation after rev0174

Current official Resilio docs still show another useful but scattered truth in an ordinary product seam:

- folder rename is local-only and should not be confused with a stable shared title
- path moves are not all equivalent: cross-volume or cross-partition moves can break ordinary tracking and fall into `Folder not found`
- disconnected folders are still meaningful product objects even though they have no local path
- custom arrival placement still depends on `Disconnected` / `Connect` ritual and default-folder behavior, including `(1)` duplicate cleanup stories
- the same `Folder not empty` warning can mean either a harmless reconnect to the old location or a materially risky merge into unrelated pre-existing bytes
- remote rename/move consequences are honest, but still explained separately through Archive/hash replay rather than one ordinary action-owned page

That means the product ideas are useful, but the page contracts still do not earn cloning.

AnonSync should therefore add one-page answers for:

- **Share path** — where the subject is actually bound here, on what storage/volume facts, and whether in-place relocation is eligible
- **Relocate review** — whether a path change is same-lineage, cross-domain rebind, repair, or continuity-breaking peer reset
- **Disconnected share** — what still exists in pathless presence, what reconnect choices remain, and what wider removal scope would be accepted
- **Rename / move explanation** — what changed locally, what peers are expected to observe, and whether replay depends on retained history or archive state


## Revision addendum — surface parity, external edit, background delivery, and mobile storage after rev0175

Current official Resilio docs still show another useful but scattered truth in an ordinary product seam:

- Linux/WebUI, desktop, Android, and iOS do not expose the same action families, and Resilio is better than average at admitting it
- iOS external-app editing is copy-based and requires explicit save-back into Sync
- Android background delivery is conditional, desktop hidden-window delivery stays active, Linux headless control is WebUI-shaped, and iOS background transfer is unavailable
- Android `Simple Mode` and mobile share settings materially change path choice, visibility, and local-storage behavior
- iOS storage, downloads, shared-link residue, and local clearing semantics still span several distinct pages and surfaces

That means the product ideas are useful, but the page contracts still do not earn cloning.

AnonSync should therefore add one-page answers for:

- **Surface capability** — what this surface can really do now, what it cannot, and why
- **External edit review** — whether another app gets a live bind or a copy, and what save-back contract applies
- **Background delivery** — whether unattended send/receive is continuous, conditional, foreground-only, or blocked
- **Mobile storage** — where bytes live locally, what each cleanup verb removes, and whether the bytes are reacquirable later

## Revision addendum — capture scope, sink choice, landed proof, and source cleanup after rev0176

Current official Resilio docs still show another useful but scattered truth in an ordinary product seam:

- mobile capture and backup are real first-class workflows, not mere renamings of ordinary sync
- Android can back up virtually any reachable data while iOS is limited to Camera Roll because of app-sandbox access ceilings
- linked-device pickers, manual link delivery, Simple Mode defaults, and removable-storage/provider rules all change which sink is actually in the ingest relationship
- backup detail surfaces expose counts, pause/resume, and device lists, but the durable answer to `has this landed enough to delete from the source?` is still reconstructed rather than published
- deleting from the source after backup, pausing ingest, and disconnecting backup all preserve or stop different things, but those consequences still live across several articles

That means the product ideas are useful, but the page contracts still do not earn cloning.

AnonSync should therefore add one-page answers for:

- **Capture source** — what exact source domain is attached, what permission proves it, and what runtime caveat currently narrows it
- **Capture sink chooser** — which sinks participate, by what admission route, and under what storage/path constraints they count
- **Ingest landed proof** — whether a source item is merely discovered, in flight, landed, or safe for source cleanup under policy
- **Source cleanup review** — what source-side delete, pause, and disconnect preserve or stop right now


## Revision addendum — execution principal, permission grants, and blocked-path repair after rev0177

Current official Resilio docs still show another useful but scattered truth in an ordinary product seam:

- runtime principal is real product meaning, not an implementation detail, because Windows service install, Linux packages, NAS packages, and headless macOS all put Sync under different actors
- filesystem authority depends on host-specific grants such as group rw, folder-level grants for package-internal users, or stronger system accounts
- changing runtime principal or storage root can silently move the operator into a different local world with different visible inventory and different recovery obligations
- blocked-path repair is practical but still scattered across host-specific troubleshooting and permission notes rather than one product-owned page

That means the product ideas are useful, but the page contracts still do not earn cloning.

AnonSync should therefore add one-page answers for:

- **Execution principal** — what OS principal is acting now, why it won, and what disk authority it currently holds
- **Filesystem grant** — what exact owner/group/ACL/provider grant makes a path writable and where that proof is weak
- **Principal switch review** — whether a runtime-user or storage-root change stays in the same world or creates a successor world
- **Blocked-path repair** — what exact grant is missing, what rung is safest, and what retest proves recovery


## Fourteenth current clone-veto seam — reachability proof still needs replacement pages

Current official Resilio docs still do a respectable job of admitting that directness depends on real network conditions: configured listening ports, tracker/discovery reachability, relay fallback, LAN multicast/broadcast, manual endpoint pins, proxy posture, and even multiple-NIC conditions. That is good product honesty. It is still not one stable operator contract. The ordinary answers to `what endpoint is actually live`, `why is this peer pair relayed`, `what safe repair rung should I try first`, and `is this manual endpoint trustworthy enough to pin` still depend on hopping between Preferences, Folder Preferences, mobile helper settings, ports/protocols notes, and troubleshooting articles. AnonSync should therefore copy the candor, but replace the page shape with four fixed surfaces: listener endpoint, peer route proof, reachability repair review, and advertised endpoint review.


## Another current non-clone reason: chronology truth still lives across warnings, advanced settings, FAQ prose, and Archive ritual

A further current-doc pass reveals another strong reason not to clone Resilio's interface contract.
The product is actually fairly candid about chronology, but the candid truth still lives in too many different places.

Current official docs still say all of the following:

- the `Time difference` warning appears when a peer's internal clock or time-zone setting is wrong, with Sync comparing file modification time after converting peer times to GMT and allowing only a 600-second difference
- mobile devices can degrade to showing an empty list rather than files under the same invalid-time condition
- `sync_max_time_diff` remains a separate power-user preference with a default of 600 seconds
- `ignore_mtime_assign_errors` can leave the correct timestamp only in the database while the on-disk mtime becomes `current`
- if several people edit the same file, ordinary online chronology can be displaced by the latest file that comes online, so an offline peer can later overwrite a newer online edit, with overwritten versions moved to Archive
- manual Archive restore still depends on Sync already running; otherwise rescan can detect the restored older file and move it to Archive again as older

Those are not mere troubleshooting curiosities.
They describe one public operator truth family that deserves explicit product ownership.

### What to borrow

Borrow the honesty that:

- clock and time-zone validity materially gate transfer safety
- offline return is a different authority rule from clean online chronology
- database truth and filesystem truth can diverge for mtimes
- restore timing changes whether an extracted version becomes live or is archived again

### What not to clone

Do not clone the page contract where the operator must cross-read:

- a warning article for clock validity
- a power-user table for mtime fallback truth
- a FAQ for offline-winner semantics
- an Archive article for restore replay timing

### What AnonSync should replace it with

This revision therefore adds four ordinary replacement pages:

- **Clock authority**
- **Offline replay review**
- **Mtime integrity**
- **Restore replay review**

That is the right response: keep the candor, replace the interface ownership model.


## Semantic tradeoffs and hidden optimization truth after rev0180

Another current no-clone seam is now concrete.
Resilio's official docs are fairly candid that:

- read-only overwrite can be destructive and has class-specific outcomes for edits, renames, deletions, and added files
- placeholder deletion can mean local eviction or global destruction depending on access and verb
- hidden settings can remap placeholder deletion into safety-biased placeholder recreation
- deferred hashing and initial-index policies change when subjects are semantically ready for rename, dedup, and ordinary sync behavior
- some fast transfer paths accept whole-file restart on interruption

That is useful product honesty.
It is also a good reason not to clone the page contract, because one ordinary answer still requires stitching together a FAQ, Folder Preferences, the RSLS article, the power-user table, and the internal-tasks warning page.

The right AnonSync response is therefore:

- borrow the candor
- refuse the toggle-and-article ownership model
- replace it with four ordinary pages: **Read-only divergence**, **Placeholder removal**, **Hash readiness**, and **Transfer method**


## Revision addendum — footprint truth, metric contract, completeness confidence, and hidden residue

This revision pushes the Resilio evaluation further in another quiet but load-bearing place.
Current official docs are still candid that ignored files are not counted in the main `Size` column, placeholders are 0-byte stand-ins, `.sync` / Archive / StreamsList / `.!sync` are real managed byte families, and watcher / rescan / hashing policy can make a view provisional rather than final.
That is all worth borrowing.
What is still not worth cloning is the page contract that leaves the ordinary operator answer spread across IgnoreList, `.sync` internals, RSLS placeholder docs, folder-view columns, and change-detection/power-user articles.

The AnonSync replacement in this revision is four fixed pages:

- `333` for truthful **subject footprint**
- `334` for **metric contract** and drift explanation
- `335` for **completeness confidence**
- `336` for **service residue / clearance review**

The tighter doctrinal answer is:

> a sync product should never make `size`, `present`, `empty`, or `cleared` look self-explanatory when placeholders, exclusions, hidden service bytes, and provisional indexing are all real states.

## Revision addendum — topology, local edges, provider grants, and removable-target continuity

This revision pushes the Resilio evaluation further in another quiet but consequential place.
Current official docs are still candid that nested shares are real but come with seeding asymmetry and duplicated indexing; that same-host local shares are self-only, entitlement-bound, and source-coupled; that provider-backed removable storage needs a real root grant separate from ordinary path browsing; and that missing or returning targets can shift the honest answer between continuity, safe rebind, and dangerous merge.
That is all worth borrowing.
What is still not worth cloning is the page contract that leaves the ordinary operator answer spread across nested-share FAQs, local-share tips, Simple Mode / SD-card peculiarity docs, existing-folder warnings, and move/reconnect articles.

The AnonSync replacement in this revision is four fixed pages:

- `337` for **topology admission**
- `338` for **local edge meaning and entitlement cliffs**
- `339` for **provider grant proof and picker integrity**
- `340` for **removable-target continuity and safe rebind**

The tighter doctrinal answer is:

> a sync product should never make `add here`, `sync locally`, `store on SD`, or `reconnect` look self-explanatory when graph relation, route truth, grant proof, and return continuity are all real states.


## Further current clone-veto seam — share artifact family, requester approval, and mutable grants

Current official Resilio docs are again strong enough that AnonSync has to give a serious answer rather than a vague anti-clone posture.

### What is good and worth borrowing

Resilio is still right that:

- share capability family matters
- approval can be a real requester-review event rather than a decorative prompt
- requester identity evidence deserves visible fingerprints / proofs
- mutable grants and onward-share rights are not identical across every subject kind
- manual carrier flexibility (copy, QR, browser handoff, paste) is valuable in ordinary life

AnonSync should borrow that candor directly.

### What still should not be cloned

The ordinary operator answer is still fragmented.
Current docs still require cross-reading the Share dialog article, Key structure article, Link structure article, User Management article, and mobile sharing guides to answer four basic questions:

1. what exact capability artifact did I issue or import?
2. what approval model comes with that artifact, if any?
3. who is actually asking for access, and why did policy auto-approve or gate them?
4. what part of this grant can I still edit or revoke later, and what already-landed bytes remain outside that future-update boundary?

That means the product idea is good.
The page contract is still too scattered.

### Replacement pages added for this seam

This revision therefore adds four more replacement pages:

- `342` — Share capability
- `343` — Incoming share request
- `344` — Member access
- `345` — Manual claim

The deeper line stays the same:

> borrow Resilio's semantic candor; refuse page contracts that still make one ordinary answer depend on several article families.


## Further current clone-veto seam — subject class, impossible upgrade, linked read-only, and peer-row meaning

Current official Resilio docs are again strong enough that AnonSync has to give a serious answer rather than a vague anti-clone posture.

### What is good and worth borrowing

Resilio is still right that:

- subject class is real semantic structure rather than decoration
- some subject classes truly support richer identity, ownership, and mutable-right semantics than others
- some `upgrades` are actually successor cutovers and should be named that way
- some requested seat exceptions do not fit the current governance family and deserve a more honest separate ritual
- peer-list grouping should reflect what the product can actually prove about identity lineage

AnonSync should borrow that candor directly.

### What still should not be cloned

The ordinary operator answer is still fragmented.
Current docs still require cross-reading the Standard-vs-Advanced article, the Standard→Advanced upgrade how-to, the linked read-only how-to, User Management, and broader linking docs to answer five basic questions:

1. what class of subject is this?
2. what cliffs come with that class?
3. is `upgrade` a same-subject mutation or a successor cutover?
4. is `make this linked seat read-only` really a per-seat exception or a separate lower-governance subject?
5. what are peer rows actually grouping by in this class?

That means the product ideas are good.
The page contracts are still too scattered.

### Replacement pages added for this seam

This revision therefore adds four more replacement pages:

- `347` — Subject class
- `348` — Class upgrade review
- `349` — Linked read-only exception review
- `350` — Peer identity view

The deeper line stays the same:

> borrow Resilio's semantic candor; refuse page contracts that still make one ordinary answer depend on several how-tos and architecture notes.

## Further current clone-veto seam — performance visibility, bottleneck proof, and workload-shaped expectations

Current official Resilio docs are again strong enough that AnonSync has to give a serious answer rather than a vague anti-clone posture.

### What is good and worth borrowing

Resilio is still right that:

- live performance visibility belongs in the product, not just in logs
- per-peer transfer tables with RTT and protocol are useful, not overkill
- disk queue and disk load are real limits and should not be hidden behind `network slow` stories
- route class, peer asymmetry, and file shape materially change honest throughput expectations
- troubleshooting should expose counterfactual repair ideas such as direct path, predefined hosts, or low-priority-disk changes

AnonSync should borrow that candor directly.

### What still should not be cloned

The ordinary operator answer is still fragmented.
Current docs still require cross-reading the Performance Overview article, slow-speed troubleshooting, and preference/power-user notes to answer four basic questions:

1. what exact window and scope does this graph represent?
2. which peer/path is actually constraining progress right now?
3. is disk pressure local to Sync or mostly host-wide?
4. what throughput should I realistically expect from this workload before I start changing knobs?

That means the product ideas are good.
The page contract is still too scattered.

### Replacement pages added for this seam

This revision therefore adds four more replacement pages:

- `352` — Activity metrics
- `353` — Peer connection table
- `354` — Disk pressure
- `355` — Throughput expectation

The deeper line stays the same:

> borrow Resilio's semantic candor; refuse page contracts that still make one ordinary answer depend on charts, troubleshooting prose, and scattered settings memory.


### Diagnostic telemetry and evidence custody addendum

Current official Resilio docs are again strong enough that AnonSync has to give a serious answer rather than a vague anti-clone posture.

#### What is good and worth borrowing

Resilio is still right that:

- anonymous statistics, debug logs, profiler traces, and crash artifacts are different data families
- deeper capture should have an explicit enable step and sometimes a restart gate
- local artifact paths, rotation size, and retention windows are real product facts
- outbound log send is a real transfer with bundle size and completion risk, not a magical support button
- evidence collection guidance should acknowledge mobile-specific and hidden-storage-specific quirks

AnonSync should borrow that candor directly.

#### What still should not be cloned

The ordinary operator answer is still fragmented.
Current docs still require cross-reading the Power user preferences article, debug-log collection guides, mobile log guide, storage-folder article, and crash-report article to answer four basic questions:

1. what operational data classes exist before an incident?
2. what extra capture starts when I enable deeper diagnostics?
3. what exact evidence is leaving the node if I press `send logs`?
4. what artifacts remain locally, where, and for how long?

That means the product ideas are good.
The page contract is still too scattered.

#### Replacement pages added for this seam

This revision therefore adds four more replacement pages:

- `357` — Telemetry consent
- `358` — Profiler capture review
- `359` — Diagnostic send
- `360` — Local evidence retention

The deeper line stays the same:

> borrow Resilio's semantic candor; refuse page contracts that still make one ordinary answer depend on advanced settings tables, support how-tos, and hidden storage folklore.



## Further evaluation after rev0187 — control surfaces are strong ideas with weak page ownership

Another current Resilio pass strengthens the same main conclusion rather than weakening it.

Current official docs still show real product substance:

- a live v3 line with `3.1.2.1076`
- WebUI as the default path on Linux and on Windows service installs
- loopback-by-default listener posture with deliberate widening to LAN
- explicit browser-warning recovery guidance
- explicit password-reset side effects
- explicit browser-link fallback when WebUI cannot consume direct-open intake

That is not abandonment or product confusion.
It is real operator-oriented candor.

It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary control answer across WebUI setup docs, Linux/service notes, browser-warning recovery, password-reset instructions, installer trust pages, and browser-link troubleshooting.
So the product idea stays strong while the page contract still fails.

That is why this revision adds four narrower replacement pages:

- `362` Control launch
- `363` Control listener
- `364` Browser trust recovery
- `365` Control access recovery

These pages keep the Resilio practicality and reject the scattered explanation path.

## Further evaluation after rev0193 — namespace truth is still real, but still scattered

Another current Resilio pass strengthens the same main conclusion rather than weakening it.

Current official docs still show real product substance:

- a live v3 line with `3.1.2.1076`
- explicit conflict-file causes including case-insensitive collisions, unicode-form differences, prohibited symbols, linked junctions, and even storage/controller faults
- explicit warning not to casually delete `.Conflict` artifacts because they still correspond to real remote data
- explicit unsupported-link guidance on Windows, and explicit symlink-target exclusion guidance on Unix unless the target is added separately
- explicit invalid-name and path-length warnings in troubleshooting guidance
- explicit exposure of path-handling toggles like `fix_conflicting_paths` and `normalize_unicode_paths`

That is not vagueness or abandonment.
It is real operator-oriented candor.

It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary namespace answer across conflict docs, unsupported-entry docs, invalid-name warnings, move/rename limitations, troubleshooting notes, and power-user settings.
So the product idea stays strong while the page contract still fails.

That is why this revision adds four narrower replacement pages:

- `397` Namespace blockage
- `398` Conflict evidence
- `399` Unsupported entry
- `400` Portability repair

These pages keep the Resilio candor and reject the suffix-and-support reconstruction path.
## Further evaluation after rev0194 — freshness claims are useful, but still article-shaped

Another current Resilio pass strengthens the same main conclusion rather than weakening it.

Current official docs still show real product substance:

- a live v3 line with `3.1.2.1076`
- candid explanation that change detection precedes indexing and delivery rather than magic `instant sync`
- explicit periodic/startup/manual rescan truth
- explicit watcher-exhaustion downgrade truth
- explicit service-path notification-loss truth
- explicit admission that `Some internal tasks are taking time to complete` may still be recoverable background work

That is not abandonment or product confusion.
It is real operator-oriented candor.

It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary freshness answer across the synchronization-start FAQ, power-user settings, watcher warnings, service troubleshooting, internal-task warnings, and generic no-sync guidance.
So the product idea stays strong while the page contract still fails.

That is why this revision adds four narrower replacement pages:

- `402` Freshness basis
- `403` Detection downgrade
- `404` Rescan review
- `405` Change publication

These pages keep the Resilio candor and reject the FAQ-plus-warning reconstruction path.

## Further evaluation after rev0195 — motion truth is useful, but still article-shaped

Another current Resilio pass strengthens the same main conclusion rather than weakening it.

Current official docs still show real product substance:

- a live v3 line with `3.1.2.1076`
- candid explanation that scheduled `Paused` still allows zero-sized files, deletions, indexing, and some peer-serving behavior
- candid explanation that desktop background, headless Linux, Android task-killer risk, and iOS background absence are materially different runtime stories
- candid explanation that Android Auto Sleep and Battery Saver intentionally change participation posture
- candid explanation that hidden work such as hashing, block checking, local-block copy, compare, read, and write can make Sync look stalled before visible transfer resumes
- candid explanation that slowness can come from relay, many-small-files shape, remote-upload ceiling, disk / hardware limits, or security-software interference
- candid explanation that some unavailable downloads are not waiting at all because no peer still has full source bytes

That is not abandonment or product confusion.
It is real operator-oriented candor.

It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary motion answer across the schedule article, background/runtime notes, battery/network settings, slow-speed troubleshooting, source-unavailable warnings, and internal-task warnings.
So the product idea stays strong while the page contract still fails.

That is why this revision adds four narrower replacement pages:

- `412` Motion basis
- `413` Quiet window
- `414` Bottleneck cause
- `415` Resume catch-up

These pages keep the Resilio candor and reject the schedule-plus-warning reconstruction path.


## Further non-clone evidence after rev0197 — hidden subject spine and sidecar authority

Another current Resilio pass now tightens the argument in a different ordinary place:

- current docs still openly admit that a subject carries hidden product-owned state inside `.sync`
- current docs still split hidden families across identity, Archive, IgnoreList, StreamsList, and in-flight `.!sync` names
- current docs still make exclusion semantics depend on a hidden text sidecar and xattr carriage depend on a separate hidden whitelist sidecar
- current docs still let duplicate runtimes or unsupported instance cloning corrupt or confuse that hidden state
- current docs still make one repair path effectively `check Archive, delete .sync, remove/re-add`, which is continuity-recreation folklore rather than one product-owned continuity page

So one more strong no-clone reason is now clear:

> Resilio is still worth borrowing for its candor that sync subjects really do have hidden product-owned state, but not for the way ordinary answers about `what is payload`, `what is hidden product state`, `which sidecar is local policy`, `did continuity survive`, and `what hidden bytes are safe to touch` still live across FAQ pages, hidden text files, warning articles, troubleshooting notes, move/rename caveats, and cloning warnings.

AnonSync should therefore expose one visible subject-spine contract, one sidecar-policy page, one spine-integrity page, and one managed-hidden-bytes page instead of relying on hidden folders as the interface.


## Latest addendum — external recipes, command exactness, and postcondition proof after rev0202

Current official Resilio docs still show a practical product line, and they still make a serious case for borrowing procedural candor rather than pretending every repair can be one safe in-product click.
They still openly recommend outside-the-product acts like stopping Sync before `iperf3`, creating `debug.txt` in storage, restarting to make logging take effect, editing or supplying `sync.conf`, clearing HSTS or using a temporary browser bypass, deleting `settings.dat` for one password-reset lane, or rebuilding hidden service state when `.sync` continuity is lost.

What they still do not make easy enough is one ordinary answer to:

- what exact class of step this is
- what exact seat / runtime / path / hidden state it touches
- what had to be stopped or closed first
- what observation only proves the ritual happened
- what product-side reread actually proves success afterward
- whether the result preserved continuity or only recreated workable successor state

That is another strong reason to **adapt, not clone**.
AnonSync should copy Resilio's candor about external recipes and exact steps, but refuse any interface contract where those answers still depend on cross-reading support how-tos, browser-warning pages, config notes, and troubleshooting prose.

### Warning ownership, blast radius, and recovery-rung addendum

Current official Resilio docs still show an active v3 line through `3.1.2.1076`, and they are still candid that warning strings correspond to materially different realities:

- `Core warnings` still separates tracker loss, low space in the default-folder-location disk, failed folder-list / identity sync, and license-management disablement.
- `Some internal tasks are taking time to complete` still says the condition can be recoverable hidden work such as scanning, hashing, block checking, deduplication, merge, transfer, or writing rather than a hard stall.
- the watcher-exhaustion warning still says Sync can lose live notifications and fall back to manual or periodic rescan until the inotify limit is raised and Sync restarted.
- the ghost-file / `Cannot download files` warning still says a peer may have announced bytes that later disappeared into placeholder-only state and now no full source peer has them.
- `Database error` still suspends only the affected subject and still recommends a restart → disconnect/reconnect same destination → re-add ladder.
- `Service files missing` still treats `.sync` loss/corruption as continuity-bearing damage and explicitly says the fix creates a new synchronization instance.
- `Folder not found` and `Folder not empty` still mix same-lineage reconnect, risky merge into pre-existing bytes, and broader peer-reconnect fallout.
- `Time difference` still names clock/timezone invalidation and the 600-second threshold.

That is strong product candor.
What is still not worth cloning is the page contract.
The ordinary operator still has to reconstruct warning meaning across footer strings, share warnings, click-through details, standalone articles, and related-article hops.

AnonSync should therefore expose four fixed public surfaces whenever warning meaning is non-trivial:

1. **Warning page** — exact warning class, honest severity, strongest current claim, and first safe next move
2. **Blocker scope** — seat / subject / item / hidden-state blast radius and unaffected neighbors
3. **Recovery rung** — least-destructive next step, escalation proof, and continuity cost if a broader rung is taken
4. **Warning history** — first seen / last seen / acknowledged / suppressed / cleared-with-proof lineage so dismissal never impersonates repair

So the tighter line for this pass is:

> borrow Resilio's candor that warnings correspond to real degraded states; refuse any product contract where ordinary warning truth still depends on stitching together strings, one-off articles, and troubleshooting prose instead of one stable page family.

## Latest addendum — mobile capture-source, path-class, sink, and reacquire truth after rev0204

Current official Resilio docs still show a practical mobile story, and they still make a serious case for borrowing platform candor rather than pretending a phone is just a small desktop.
They still openly distinguish Camera Backup from ordinary sync, Android folder backup from iOS Camera Roll only, sandboxed iOS storage from Android path classes, Simple Mode fixed defaults from explicit location choice, SD-card root-grant flow from ordinary folder picking, and download-history residue from actual local bytes.

What they still do not make easy enough is one ordinary answer to:

- what exact source class is under review
- what exact path class is writable or only source-readable on this seat
- whether the selected peer is a collaborative peer or a durable-copy sink
- what later local clearing leaves behind as bytes, placeholders, history, or only receipts
- what current prerequsite still governs reacquireability

That is another strong reason to **adapt, not clone**.
AnonSync should copy Resilio's candor about mobile constraints and contracts, but refuse any interface shape where those answers still depend on hopping across Camera Backup, Android Backup, Simple Mode, SD-card, storage-management, file-sharing, and iOS-peculiarity articles.

## Latest addendum — compromised linked seats, narrowest cutoff, and residual authority after rev0205

Current official Resilio docs still show a practical product line, and they still make a serious case for borrowing incident candor rather than pretending a stolen seat is merely an offline row.
They still openly say that an unencrypted stolen linked seat may be able to view, modify, or remove data on other linked devices; that linked seats under one identity act as Owners; that `Disconnect` revokes future updates while leaving already-synchronized files in place; that remote unlink of other linked devices is unavailable; and that the documented response may expand into backup, unlink, storage-folder cleanup, reinstall, identity regeneration, relink, and reshare.

What they still do not make easy enough is one ordinary answer to:

- what exact live authority this suspect seat still carries now
- what exact cutoff can be bought narrowly per subject
- when broader cohort rotation is the honest next step rather than overreaction
- what exact sequence carries trusted survivors forward under a rebuilt epoch
- what already-landed bytes or residual authority still remain after the cutoff

That is another strong reason to **adapt, not clone**.
AnonSync should copy Resilio's candor about incident cost and residual risk, but refuse any interface shape where those answers still depend on hopping across a stolen-device note, identity-linking docs, user-management semantics, licensing behavior, and encrypted-peer guidance.

## Latest addendum — bounded handoff, open redemption, and residue truth after rev0206

Current official Resilio docs still show a practical product line, and they still make a serious case for borrowing candor about convenient file handoff rather than pretending every link is a live shared subject.
They still openly say that `Sharing single file` is a one-time one-way data transfer, that desktop links default to 3 days but may be made never-expiring, that `share_file_ttl` still shapes defaults, that anyone with the link can redeem it, that use count and device bans are unavailable, that changed content invalidates the current handoff and forces a new link, and that recipients may re-share without gaining power to change expiry.

What they still do not make easy enough is one ordinary answer to:

- is this live sync or only a bounded snapshot handoff
- who may redeem it and what ceiling that claim really has
- what exact lane or surface owns the receive path now
- what exact landed result will happen on collision
- what UI clearing, byte deletion, expiry, or stale-content invalidation actually leaves behind

That is another strong reason to **adapt, not clone**.
AnonSync should copy Resilio's candor about bounded handoff limits and residue, but refuse any interface shape where those answers still depend on hopping across the single-file article, Android/iOS sharing notes, receive-path defaults, and power-user history knobs.


## Diagnostic support-lane, log-route, and crash-custody addendum

Current official Resilio docs still make support and diagnostic truth simultaneously candid and scattered.
They still openly separate:

- `send_statistics` anonymous metrics from debug logging and profiler capture
- `log_size`, `log_ttl`, and `profiler_enabled` local-retention behavior
- debug-log activation through Settings/Preferences versus `debug.txt` in storage
- restart-needed capture activation versus already-live capture
- in-product `Contact support` send versus manual attachment / upload fallback
- mobile hidden-log ritual (`SNC.DBG.LOGS`) versus desktop file pickup
- crash report / mini-dump / core-dump collection paths and service-account variance

That is useful evidence.
It is also a strong reason not to clone the current page contract, because the ordinary answer still requires rebuilding one support/disclosure story from several articles.

AnonSync should instead publish four ordinary page families:

- **Support lane** — who can actually receive evidence here, and under what disclosure boundary
- **Log capture window** — what extra capture is active, what restart/hold-time is still required, and what residue is accumulating locally
- **Report send** — what exact packet leaves, by what route, under what size ceiling, with what fallback
- **Crash artifact** — which crash-evidence class exists, where it lives, and what remains local after export


## Revision addendum — space pressure, byte classes, and reclaim proof after rev0208

Another current Resilio pass exposed a storage seam that is too ordinary to remain article-shaped.

Current official docs still openly say that:

- `free_space_warning_threashold` defaults to `1024 MB` and can stop syncing files when the drive tied to the default folder location gets that low
- `disk_min_free_space` and `disk_min_free_space_gb` still offset that floor
- Selective Sync placeholders still materially reduce local byte residency while `Remove from this device` keeps peers intact only if another full source survives
- Archive still retains deleted/older copies for 30 days on desktops and 1 day on mobiles by default, while disabling Archive weakens that protection
- iOS storage still splits App Data from User data and still requires Selective Sync before clearing local files from a sync share
- mobile Cleanup still clears residual files and current debug logs
- storage folders and uninstall paths still preserve configuration, database, logs, dumps, and other managed bytes outside ordinary payload

That candor is useful.
The page shape is still wrong.
One ordinary answer still requires hopping across warnings, power-user settings, Sync-mode docs, Archive docs, mobile storage pages, storage-folder lore, and uninstall notes to answer four questions:

- what exact floor is active here now
- what exact byte classes are consuming local storage
- what safe-first reclaim action exists
- what exactly changed after apply

AnonSync should therefore keep the storage candor and replace the page shape with four ordinary product-owned pages:

- **Space pressure** — active floor, byte contributors, and safest first rung
- **Byte-class inventory** — payload, history, diagnostics, service state, and residue in one stable ledger
- **Reclaim preview** — expected freed bytes, non-effects, and retention cost before commit
- **Reclaim receipt** — observed byte delta, preserved truths, weakened truths, and residue after apply


## Revision addendum — network paths, protocol discipline, and freshness risk after rev0209

Another current Resilio pass exposed a remote-path seam that is too ordinary to remain article-shaped.

Current official docs still openly say that:

- SMB/network shares are a distinct path class with explicit limitations and peculiarities
- Sync and the actual runtime account still both need full permissions to the target folder or delivery can cease
- SMB-mounted paths may lack live notifications unless the stack is SMB 3.0+, and otherwise change discovery falls back to full rescans
- some file storages such as NFS or SMB2 mounted shares are not even supposed to provide working filesystem notifications, so freshness becomes rescan-grade by design
- lock behavior on network shares still depends on the SMB service / daemon implementation and on failure paths such as dropped connections or crashed apps
- mixed direct access plus Samba access on NAS-style setups can still damage files or roll back third-party changes
- Windows service UNC workarounds can still make a path reachable while losing live notifications and relying on rescan or restart instead
- changing service identity to gain access can still move state root and force re-add / re-share / reconnect work

That candor is useful.
The page shape is still wrong.
One ordinary answer still requires hopping across an SMB article, service troubleshooting, generic freshness notes, and release-fix memory to answer four questions:

- what exact path class is this
- which protocol is authoritative for mutation
- how fresh can this location honestly be
- should this remote path be admitted as a subject at all

AnonSync should therefore keep the candor and replace the page shape with four ordinary product-owned pages:

- **Network path class** — local vs mounted vs UNC-under-service plus watcher grade and runtime implications
- **Protocol discipline** — authoritative mutation lane, alternate lanes, and explicit corruption/rollback risk
- **Detection grade** — notification coverage, rescan fallback, restart sensitivity, and freshness ceiling
- **Network subject admission** — permission fitness, lock/daemon caveats, service identity consequences, and admit/reject receipt
