## Revision addendum — ciphertext custody, recovery prerequisites, and encrypted-Archive ceilings after rev0211

Another current Resilio pass now sharpens one more non-clone seam:

- **encrypted target admission / ciphertext custody / decrypt recovery / encrypted Archive limit**

The current official docs are still useful because they openly treat ciphertext-only custody on untrusted machines as a real deployment pattern.
They also openly admit the hard ceilings: opaque nodes stay read-only, force overwrite behavior, lack Selective Sync, share onward only in encrypted form, and cannot replay deleted files back into the live share from encrypted Archive.
That candor is valuable.
The non-clone problem is that the ordinary answer to `is this target safe`, `can this node ever produce plaintext`, `what exact materials must survive`, and `why is encrypted Archive only evidence here` still lives across encrypted-folder caveats, read-only semantics, ordinary pre-populated-connect guidance, and support-shaped recovery instructions.

| Seam | Current Resilio value | AnonSync stance | Why not clone directly | Required AnonSync pages |
| --- | --- | --- | --- | --- |
| Encrypted target admission / ciphertext custody / decrypt recovery / encrypted Archive limit | Useful but scattered | **Adapt** | Current docs still spread opaque-node landing hygiene, hard capability ceilings, saved-material prerequisites, and history replay limits across several articles and caveat clusters | **Encrypted target admission**, **Ciphertext custody**, **Decrypt recovery**, and **Encrypted Archive limit** pages |

## Revision addendum — volume capability, metadata fidelity, and degraded repair after rev0210

Another current Resilio pass now sharpens one more non-clone seam:

- **volume capability / metadata fidelity / affordance ceiling / volume repair**

The current official docs are still useful because they openly say not every target volume can carry the same promises.
StreamsList still whitelists metadata carriage, FAT32 still lacks Windows alternate streams, fallback stubs still exist when metadata cannot be stored natively, and Windows shell actions still depend on NTFS.
That candor is valuable.
The non-clone problem is that the ordinary answer to `what can this target really carry`, `is metadata native or stub-backed`, `why is this action absent`, and `should I migrate or reformat` still lives across xattr docs, shell troubleshooting, hidden-sidecar notes, and old fix history.

| Seam | Current Resilio value | AnonSync stance | Why not clone directly | Required AnonSync pages |
| --- | --- | --- | --- | --- |
| Volume capability / metadata fidelity / affordance ceiling / degraded repair | Useful but scattered | **Adapt** | Current docs still spread filesystem-class truth, fallback metadata carriage, action prerequisites, and stronger-target decisions across architecture notes and troubleshooting | **Volume capability**, **Metadata fidelity**, **Affordance ceiling**, and **Volume repair** pages |

## Revision addendum — publication readiness, touch repair, and inbound-priority truth after rev0201

The archive should now treat one more Resilio line as explicitly `adapt, do not clone`:

- **publication readiness / authoring delay / touch repair / inbound priority**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer can depend on:

- whether detection came from filesystem notifications, periodic rescan, or manual rediscovery
- whether a file-class delay policy is active and where it came from
- whether another application is holding the file open
- whether `touch` would merely rediscover current bytes or advance chronology claims
- whether inbound order is inherited, locally frozen, queue-limited, transfer-class-constrained, or only cosmetically misrepresented

So the tighter scorecard entry is:

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Publication readiness / authoring delay / manual freshness repair / inbound urgency | Useful but scattered | **Adapt** | Current docs still spread `is this ready`, `why is this waiting`, `should I touch this`, and `why is this not first` across a FAQ, a delay how-to, a touch how-to, a locked-files article, a priority feature page, and power-user notes | **Publication readiness**, **Authoring delay**, **Touch repair**, and **Inbound priority** pages |

The more precise answer to `why not just clone Resilio here too?` is now:

> because the product idea is strong, but the interface contract still lets scattered timing and repair articles partially own ordinary publication truth.

## Revision addendum — capability gates, entitlement basis, and missing-control truth after rev0199

The archive should now treat one more Resilio line as explicitly `adapt, do not clone`:

- **capability availability / entitlement basis / gated action / Pro-function loss**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer can depend on:

- whether the feature page includes a version-availability footnote
- whether the subject is Standard or Advanced
- whether the seat is self-entitled, owner-inherited, shared-seat, family-scope, or only assumed to be covered
- whether the action is truly unavailable or only absent from the current surface
- whether a seat fell back because the owner expired, the seat was reclaimed, or the key moved elsewhere

So the tighter scorecard entry is:

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Capability gating / entitlement provenance / missing-control explanation / live Pro-function loss | Useful but scattered | **Adapt** | Current docs still spread `can I do this here`, `what exact right do I currently have`, `why is this control absent`, and `what just stopped working` across feature pages, folder comparisons, licensing notes, troubleshooting pages, and FAQ prose | **Capability availability**, **Entitlement basis**, **Gated action**, and **Pro-function loss** pages |

The more precise answer to `why not just clone Resilio here too?` is now:

> because the product idea is strong, but the interface contract still lets availability footnotes, license-owner lore, and troubleshooting pages partially own capability truth.

## Revision addendum — install eligibility, linked-cohort skew, and maintenance-lane truth after rev0198

The archive should now treat one more Resilio line as explicitly `adapt, do not clone`:

- **install target / linked cohort / upgrade gate / package lane**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer can depend on:

- whether the host role is workstation, server, NAS, or mobile
- whether the usage class is personal/family or business/commercial
- whether linked seats are mixed across v2 and v3
- whether the current install lane is default app install, service install, custom launch, or repository package
- whether `files survive` is being mistaken for `configuration survives`

So the tighter scorecard entry is:

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Install eligibility / linked-cohort uniformity / boundary-crossing continuity / package-lane ownership | Useful but scattered | **Adapt** | Current docs still spread `may this seat run this line, may this cohort mix versions, what survives the cutover, and who owns updates here?` across system requirements, update notes, FAQs, Linux/NAS install pages, and identity-linking warnings | **Install target**, **Linked cohort**, **Upgrade gate**, and **Package lane** pages |

The more precise answer to `why not just clone Resilio here too?` is now:

> because the product idea is strong, but the interface contract still lets package tables, platform warnings, and mixed-version linking caveats partially own release truth.


## Revision addendum — placeholder verbs, local reclaim, and archive replay after rev0192

| Resilio family | Product idea strength | Clone line | Why not clone the page contract | AnonSync replacement page |
| --- | --- | --- | --- | --- |
| Selective materialization / placeholders | Strong | **Borrow** | Byte-posture vocabulary is still excellent and worth preserving | Keep typed byte posture as a first-class product family |
| Fetch / materialize scope | Strong | **Adapt** | Current docs still hide future-descendant consequences in placeholder instructions rather than one review page | `392` Fetch intent |
| Local reclaim / disconnect | Strong but dangerous | **Adapt** | Current docs still make local eviction, placeholder drop, and folder detach too easy to blur together | `393` Local eviction |
| Delete gestures on placeholders | Strong but dangerous | **Do not clone** | Current docs still let ordinary delete meaning depend on access, target state, and surface kind | `394` Delete consequence |
| Archive restore / replay | Useful | **Adapt** | Retained history is valuable, but restore still remains manual and timestamp/runtime-sensitive | `395` Restore review |

The sharpened line is now even simpler:

> copy the selective-materialization practicality; refuse overloaded `Remove` and `Delete` semantics plus hidden-history replay folklore.

## Revision addendum — seat lineage, replacement, and reset-boundary truth after rev0191

The archive should now treat one more Resilio line as explicitly `adapt, do not clone`:

- **seat lineage / identity replacement / duplicate-row residue / reset impact**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer can depend on:

- whether linking will merely relate seats or replace one certificate with another
- whether a roster row is hidden, offline, duplicated by reset, or truly retired
- whether a reset stays in the same storage world or effectively creates a new one
- whether continuity preserved local bytes only, durable identity too, or neither

So the tighter scorecard entry is:

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Seat lineage / identity replacement / roster residue / reset impact | Useful but scattered | **Adapt** | Current docs still spread `is this the same seat, what did this reset preserve, and why does this row look duplicated?` across identity docs, password-reset docs, service install/troubleshooting, hide-device guidance, and uninstall/mobile-repair notes | **Seat lineage**, **Identity replacement**, **Device roster**, and **Reset impact** pages |

The more precise answer to `why not just clone Resilio here too?` is now:

> because the product idea is strong, but the interface contract still lets linking rituals, row-list folklore, and storage-root accidents partially own seat-continuity truth.

## Revision addendum — pending claim visibility, approval locus, and remembered-trust scope after rev0190

The archive should now treat one more Resilio line as explicitly `adapt, do not clone`:

- **pending approval / approver-locus truth / remembered-trust scope**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer can depend on:

- whether the request is visible as a pending folder, a peer-row request, or only as absence-of-auto-connect
- whether the approving seat is the original issuer or a linked seat with the subject materially present
- whether remembered trust from an earlier approval should silently suppress a fresh prompt
- whether the real blocker is route reachability rather than policy or identity mismatch

So the tighter scorecard entry is:

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Pending approval / request proof / approver locus / remembered trust | Useful but scattered | **Adapt** | Current docs still spread `why is this pending, who may approve it, and why did auto-approval happen or fail?` across share dialogs, guides, identity docs, folder icons, link-flow docs, and connectivity notes | **Pending claim**, **Claim inspection**, **Approval authority**, and **Approval memory** pages |

The more precise answer to `why not just clone Resilio here too?` is now:

> because the product idea is strong, but the interface contract still lets lane choice, seat presence, and remembered identity behavior partially own approval truth.

## Revision addendum — mutable-grant ceilings, revoke residue, and successor epochs after rev0189

The archive should now treat one more Resilio line as explicitly `adapt, do not clone`:

- **grant mutation / live artifact inventory / revocation residue / successor epoch planning**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer can depend on:

- whether the subject is Advanced or Standard
- whether the access path is a mutable certificate-backed grant or a raw key epoch
- whether the target is a direct member or a local derivative
- whether revocation is about future updates, already-landed bytes, or both
- whether a requested change is a real live edit or a `remove and re-share` successor ritual

So the tighter scorecard entry is:

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Grant mutation / artifact lifecycle / revoke residue / reissue boundary | Useful but scattered | **Adapt** | Current docs still spread `can I edit this in place, and what survives revoke?` across share dialogs, user management, class docs, local-share caveats, and key-flow notes | **Grant change**, **Issued access**, **Revocation scope**, and **Reissue plan** pages |

The more precise answer to `why not just clone Resilio here too?` is now:

> because the product idea is strong, but the interface contract still lets subject class, derivative quirks, and artifact-flow trivia partially own grant-lifecycle truth.

## Revision addendum — linked-family automation, carrier-specific approval, and resulting authority after rev0188

The archive should now treat one more Resilio line as explicitly `adapt, do not clone`:

- **linked-identity convenience / subject-family cliffs / claim-lane authority coupling**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer can depend on:

- whether the seat joined through linked identity or a one-subject claim
- whether the subject is Standard or Advanced
- whether the claim traveled by key or link
- whether approval memory applies only to links and only under certain policies
- whether onward sharing is a property of the current class, current grant, or both

So the tighter scorecard entry is:

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Linked identity / subject family / claim lane / onward share | Useful but coupled | **Adapt** | Current docs still spread `what authority will this create?` across identity guides, Standard-vs-Advanced docs, share dialogs, and exception how-tos | **Join consequence**, **Linked family**, **Onward share**, and **Claim lane** pages |

The more precise answer to `why not just clone Resilio here too?` is now:

> because the product idea is strong, but the interface contract still lets identity-linking, subject class, and carrier choice partially own authority truth.

## Revision addendum — current-surface capability truth and reviewed continuation after rev0187

The archive should now treat one more Resilio line as explicitly `adapt, do not clone`:

- **current-surface capability and channel continuation**

Resilio's current docs still show a practical product, but they also still show that one ordinary answer can depend on:

- whether the operator is on desktop app, WebUI, or a browser landing page
- whether the browser is allowed to launch the external app
- whether WebUI can consume the direct-link path at all
- whether a missing affordance is a role ceiling, browser incompatibility, or ad-block interference
- whether the operator is really continuing the same action after moving elsewhere

So the tighter scorecard entry is:

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Current-surface capability / browser-app handoff / missing-action diagnosis | Useful but scattered | **Adapt** | Current docs still spread `can I do this here?` across share dialogs, browser prompts, WebUI exceptions, browser compatibility notes, and manual fallback | **Action availability**, **Surface mismatch**, **Review handoff**, and **Resume action** pages |

The more precise answer to `why not just clone Resilio here too?` is now:

> because the product idea is strong, but the interface contract still lets browser behavior and surface kind partially own action truth.

# Resilio borrow line and non-clone scorecard

## Purpose

The archive has repeatedly said `do not clone Resilio wholesale`.
That is only a respectable decision if the boundary is explicit enough to survive pressure.
This document therefore asks a stricter question:

> on which exact lines should AnonSync borrow Resilio directly, on which lines should it adapt the idea but change the contract, and on which lines should it refuse the clone even if the feature is convenient?

The goal is not to score style points for divergence.
The goal is to make every non-clone choice earn itself.

## Current judgment

Resilio still deserves serious respect.
The current official docs still show an active v3 line, refreshed UI work, useful disconnected/selective/full sync modes, advanced-folder permission mutation, local same-host shares, encrypted folders for untrusted custody, and practical QR/browser/manual delivery.

So the correct AnonSync posture is not `be unlike Resilio`.
It is:

> steal the product ideas that compress real operator work, but refuse any interface contract that fuses distinct truths or hides trust expansion behind convenience defaults.

## Three buckets

### Bucket A — borrow directly

These are strong ideas whose product value survives translation into AnonSync mostly intact.

1. **Visible disconnected / selective / full byte postures**
2. **Easy folder delivery via link, QR, and manual paste**
3. **Per-peer permission differences instead of one flat share role**
4. **Encrypted custody on untrusted infrastructure**
5. **Local same-host derivation as a real workflow**
6. **Default browser UI for headless or Linux-heavy use**
7. **Concrete transfer troubleshooting that names real causes**

### Bucket B — adapt, do not copy verbatim

These are valuable ideas, but the Resilio shape still hides a load-bearing truth AnonSync wants to expose.

1. **Mode selection**
2. **Linked-device convenience**
3. **Advanced-folder authority editing**
4. **Browser-open handoff**
5. **Transfer/rate controls**
6. **Install and first-run readiness**
7. **Encrypted node behavior**
8. **Local-share repair and reattachment**

### Bucket C — do not clone

These are exact clone lines AnonSync should reject even if they look pleasantly familiar.

1. one mode selector silently deciding visibility, path adoption, and byte materialization together
2. browser trust explained as certificate-warning ritual rather than product-owned endpoint-trust state
3. link-open success being treated as authoritative intake rather than a convenience acceleration
4. permission changes that still require remove/re-share or family-specific folklore to understand side effects
5. rate posture reconstructed across ordinary preferences, scheduler, power-user toggles, and config mode
6. `installed` being allowed to impersonate `trusted, started, and reachable`
7. encrypted custody remaining a special share family instead of a more general custody / capability posture

## The scorecard

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Disconnected / selective / full sync | Strong | **Borrow** | This is one of Resilio's best compressions of real operator intent | Keep the byte-posture insight, but project it through explicit local presence and capability objects |
| Link / QR / manual invite delivery | Strong | **Borrow** | Delivery convenience is real and good | Keep all three intake paths |
| Browser/WebUI as default on Linux/service installs | Strong | **Borrow** | Web-first local control is correct for headless-heavy environments | Keep local web as first-class |
| Mode selector for linked devices | Mixed | **Adapt** | Resilio's mode choice still bundles visibility, path materialization, and future default behavior too tightly | Separate `visibility`, `adoption`, `materialization`, and `future default` into distinct inspectable fields |
| Linked devices under one identity | Mixed | **Adapt** | Linking is useful, but future auto-grant / auto-connect consequences become too ambient | Treat linking as relationship, not merged authority |
| Advanced-folder permissions and owner role | Useful | **Adapt** | The idea is good, but local-share and family-specific caveats still make authority continuity harder to read than it should be | Keep topology-aware authority editing with explicit ceilings and receipts |
| Local same-host shares | Useful | **Adapt** | Resilio documents real source-child quirks, permission limits, and reconnect rituals | Model same-host derivation as lineage, not a trick share subclass |
| Encrypted folder on untrusted node | Strong | **Adapt** | The use case is excellent, but the share family remains special-case and somewhat exception-shaped | Promote ciphertext-only custody to a more general subject posture |
| Browser-open handoff | Convenient | **Adapt** | Current docs still admit it can fail in browsers and WebUI, then fall back to generic paste | Treat browser-open as accelerator over one typed intake lane |
| Self-signed WebUI trust | Practical | **Do not clone** | Current docs still normalize browser-warning handling instead of product-owned trust state | Expose control endpoint class, trust grade, and upgrade path explicitly |
| Rate/scheduler/config layering | Capable | **Do not clone** | Current docs still spread the effective answer across several surfaces and exception knobs | One effective rate-policy ledger with winning layer and side effects |
| Install / first-run / service readiness | Pragmatic | **Do not clone** | Current docs still split package trust, consent, startup, and reachability into different moments | One readiness ladder with attestation receipts |
| Capability activation / right-to-run provenance | Useful | **Adapt** | Current docs still spread the answer across licensing, FAQ, update, expiry, and platform notes | One capability-source page with explicit local-vs-remote dependence |
| Cross-family update and linking compatibility | Important | **Do not clone** | Current docs still split sync compatibility, link risk, edition fences, and storage-preservation rules across separate pages | One compatibility gate page before join or update |
| Notifications and approval delivery | Useful | **Adapt** | Current docs still spread carrier truth across desktop prefs, mobile settings, OS permissions, and Linux UI-only caveats | One alert-delivery page with carrier matrix and miss recovery |
| Subject creation menu / kind chooser | Useful | **Adapt** | Current docs still express meaning through share dialogs, `+` menus, and platform-specific backup/send flows | One subject-kind chooser page with explicit contract differences |

## The strongest non-clone reasons

### 1) Resilio's best convenience still often arrives as fused state

The archive should gladly copy convenience.
It should not copy convenience **when the convenience hides which truth changed**.

The biggest example is still the device/share mode story.
`Disconnected`, `Selective Sync`, and `Synced` are genuinely useful operator concepts.
But the surrounding product shape still tends to mix:

- whether the share is merely visible
- whether a local path has been adopted
- whether bytes are present now
- whether future arrivals default into that same posture
- whether the current seat can widen authority

AnonSync should therefore keep the visible byte-posture idea while refusing the fused selector contract.

### 2) Resilio still solves some families through caveat clusters rather than one stable public object

The local-share family is the best example.
The docs are candid and useful, but they still explain behavior through a cluster of caveats:

- only one peer: self
- source-child dependence
- no nested loops
- owner limitations
- remove/re-share for certain permission changes
- reconnect after source reconnect

That is exactly the kind of behavior AnonSync should re-express as one lineage object with explicit continuity and repair rules.

### 3) Resilio still leaves several everyday truths spread across separate surfaces

The product is not broken because of this.
It is simply a good reason not to clone the interface contract.

The clearest examples remain:

- WebUI trust posture vs browser certificate warning
- browser-open handoff vs manual paste fallback
- global rate limits vs LAN exceptions vs scheduler vs config mode
- package install vs consent vs runtime start vs control reachability

AnonSync should therefore keep the everyday usefulness while tightening the public model.

## What we should copy more boldly

To avoid fake differentiation, the archive should say where Resilio is still plainly right.

### 1) Mode names that operators already understand

`Disconnected`, `Selective`, and `Full` are good operator language.
AnonSync should not avoid plain language merely to sound original.

### 2) Link/QR/manual triad

Resilio is right that human delivery must work across:

- browser-open convenience
- QR handoff
- plain copy/paste manual recovery

AnonSync should keep that triad and simply make the semantic intake lane stronger.

### 3) Encrypted intermediary as a first-class real-world use case

Resilio is right that users often want a cloud/VPS/NAS peer that stores ciphertext only.
AnonSync should keep that use case near the center of the product rather than burying it under future enterprise abstraction.

### 4) Linux/local-web practicality

Resilio is also right that a browser-first control surface is practical on Linux and service-heavy installs.
AnonSync should not retreat to a desktop-first assumption.

## Result

The archive now has a sharper answer when asked `why aren't we just cloning Resilio?`

The honest answer is:

> because the parts worth cloning are mostly **product ideas**, while the parts worth changing are the **truth contracts** around authority, intake, trust, continuity, and everyday review surfaces.

That is a good reason.
It is concrete enough to defend.

## Clone-veto tests

The archive now adds one stricter practical rule.
A Resilio-like page or workflow should be refused as a direct clone whenever it fails one or more of these tests:

1. **one ordinary operator question should have one stable page answer**
2. **one degraded state should have one explicit upgrade ladder**
3. **one convenience selector should not decide several orthogonal truths silently**
4. **one accelerator failure should degrade into one typed fallback, not folklore**
5. **one meaningful mutation should leave one product-owned receipt**

That means AnonSync does not need a mystical reason to diverge.
It only needs to show that the borrowed page would otherwise force the operator back into browser chrome, hidden toggles, support prose, or family-specific caveat memory.

## The immediate page replacements

This scorecard now maps directly to four replacement pages in the archive:

- `269` — Control trust
- `270` — Import artifact
- `271` — Rate policy
- `272` — Finish setup

Those page contracts are the practical answer to `if we are not cloning Resilio here, what exactly are we building instead?`

## Further scorecard pressure after the first replacement-page tranche

| Resilio family | Product idea strength | Clone line | Why not clone the page contract | AnonSync replacement page |
| --- | --- | --- | --- | --- |
| Mode / byte posture | Strong | **Adapt** | The posture language is good, but one selector still speaks for current share state and later default behavior together | `273` Byte posture |
| Encrypted folders | Strong | **Adapt** | Ciphertext-only custody is excellent, but recovery truth still depends on keys/database/CLI caveats | `274` Encrypted custody |
| Local same-host shares | Strong | **Adapt** | Same-host derivation is real, but continuity and repair still live in a caveat cluster | `275` Same-host lineage |
| Archive / versioning / restore | Useful | **Adapt** | Recovery is useful, but safe-eviction truth and restore routes still need cross-surface reconstruction | `276` Fetchability |

The scorecard's guiding line therefore gets sharper:

> when Resilio has a strong product idea but a weak page boundary, AnonSync should copy the idea and replace the page.


## Fourth-wave score lines after rev0168

| Resilio family | Product idea strength | Clone line | Why not clone the page contract | AnonSync replacement page |
| --- | --- | --- | --- | --- |
| Hidden `.sync` service material | Strong underlying need | **Adapt** | Identity-bearing runtime material is real, but current operators still learn too much through hidden folders and damage recipes | `281-service-material-page-integrity-damage-origin-and-rebind-receipt-interface-spec.md` |
| IgnoreList exclusions | Strong | **Adapt** | Exclusion policy is valuable, but a hidden case-sensitive rule file is too weak as the ordinary semantic home | `282-exclusion-policy-page-rule-editor-scope-and-impact-accounting-interface-spec.md` |
| FileDelayConfig mutation delay | Useful | **Adapt** | Delay windows are real product power, but storage-folder JSON plus restart ritual should not be the primary interface | `283-mutation-delay-page-file-class-batch-window-and-lock-avoidance-interface-spec.md` |
| Download priority (v3.1.0) | Strong | **Adapt** | Effective order, override inheritance, and exception behavior still outrun the visible list contract | `284-download-queue-page-effective-order-suspension-and-visible-vs-actual-truth-interface-spec.md` |

The sharpened line is now even simpler:

> when Resilio exposes a good operator idea through hidden files or hidden knobs, AnonSync should copy the idea and replace the operator page.


## Fifth-wave score lines after rev0169

| Resilio family | Product idea strength | Clone line | Why not clone the page contract | AnonSync replacement page |
| --- | --- | --- | --- | --- |
| Shell/file-manager accelerators | Strong | **Adapt** | Accelerators are useful, but current semantic reach still depends on extension health, volume class, and platform ritual | `285-shell-capability-page-acceleration-health-and-product-fallback-interface-spec.md` |
| Placeholder / remove gestures | Strong but dangerous | **Adapt** | Local evict, local presence drop, and share-wide deletion remain too easy to confuse | `286-byte-action-review-local-evict-vs-global-delete-and-last-copy-proof-interface-spec.md` |
| Archive / restore access | Useful | **Adapt** | History retention is useful, but current restore access and candidate interpretation remain platform-asymmetric and manual | `287-history-access-page-retention-candidate-stack-and-restore-parity-interface-spec.md` |
| Filesystem shape fidelity | Strong underlying need | **Adapt** | Link, metadata, invalid-name, and bundle risks remain fragmented across specialist docs and hidden policy files | `288-filesystem-shape-audit-page-link-metadata-invalid-name-and-bundle-risk-rollup-interface-spec.md` |

The sharpened line is now even simpler:

> when Resilio exposes a good operator idea through shell ritual, overloaded gestures, hidden restore paths, or specialist article archaeology, AnonSync should copy the idea and replace the page.


## Further scorecard lines after rev0170

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Vendor/service visibility honesty | Strong | **Adapt** | Resilio usefully documents tracker, relay, landing-page, update, telemetry, and account touch points, but the answer still lives across several different articles | `289-infrastructure-visibility-page-observer-fact-classes-and-plaintext-ceiling-interface-spec.md` |
| Service-role capability ceilings | Strong | **Adapt** | Resilio says the relay cannot read content and the vendor cannot remove user content, but the disablement/reliance answer is still FAQ-shaped rather than one ordinary page | `290-service-role-page-observer-power-and-disablement-boundary-interface-spec.md` |
| Storage-root / state-root reality | Strong underlying honesty | **Adapt** | Storage-root behavior is real and documented, but current meaning still depends on storage-path lists, config-mode defaults, and service troubleshooting | `291-state-root-page-active-world-identity-custody-and-clone-risk-interface-spec.md` |
| Unsupported cloning | Honest but blunt | **Adapt** | `Cloning not supported` is a useful warning, but it is not a reviewed continuity boundary for attach/import/successor/backup cases | `292-attach-state-page-existing-world-adoption-successor-proof-and-empty-branch-boundary-interface-spec.md` |

The sharpened line is now:

> when Resilio tells the truth about outside observers or local state continuity through several separate articles instead of one ordinary page, AnonSync should copy the honesty and replace the page.



## Further scorecard lines after rev0171

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Helper policy flexibility | Strong | **Adapt** | Resilio gives real tracker/relay/LAN/proxy/predefined-host control, but the effective answer still lives across folder prefs, global prefs, and troubleshooting | `293-helper-policy-page-tracker-relay-lan-proxy-known-host-and-scope-stack-interface-spec.md` |
| Bootstrap/catalog provenance | Honest but scattered | **Adapt** | Vendor catalog bootstrap, manual override, and route-cache residue are documented, but not as one operator page | `294-bootstrap-source-page-catalog-origin-cache-residue-and-private-override-interface-spec.md` |
| Pairwise helper dependence | Useful | **Adapt** | Resilio explains direct/relay/proxy/tracker behavior, but not through one page that proves which helper a peer pair actually needs now | `295-helper-dependence-page-subject-pairwise-helper-need-and-counterfactual-route-interface-spec.md` |
| Host cadence / quiet-host tuning | Honest support lore | **Adapt** | Rescan/watcher/logging/refresh/sleep tradeoffs are real, but still require support-article reconstruction instead of one ordinary cadence page | `296-host-cadence-page-notifications-rescan-refresh-save-logging-and-sleep-cost-interface-spec.md` |

The sharpened line is now:

> when Resilio exposes real helper or host-cadence truth only by making the operator hop between preference scopes and troubleshooting pages, AnonSync should copy the flexibility and replace the page.


### 4) Capability gating and kind creation are still too article-shaped

Current official docs still leave the operator to reconstruct one answer from licensing pages, FAQ pages, update instructions, notification settings, platform-permission docs, and separate sharing/backup articles.

AnonSync should therefore keep the useful capability families while refusing the exact current page contracts for right-to-run provenance, compatibility gates, alert delivery, and subject-kind choice.

## Further scorecard lines after rev0173

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Warning-driven issue classification | Useful | **Adapt** | Concrete warnings are valuable, but the ordinary answer still depends on clicking through rows and troubleshooting pages | `301-issue-home-page-symptom-family-evidence-floor-and-first-safe-action-interface-spec.md` |
| Foreign-writer / lock / weak-notify diagnosis | Strong candor | **Adapt** | Resilio is honest about locks, delay windows, SMB/direct mixed access, and weak detection, but the truth still spans several docs and hidden files | `302-environment-conflict-page-foreign-writer-lock-and-notification-confidence-interface-spec.md` |
| Repair ladders | Practical | **Adapt** | Restart / reconnect / re-add / delete-.sync recipes are useful, but one stable copy-safety ladder is still missing | `303-repair-plan-page-copy-safety-rungs-and-precondition-proof-interface-spec.md` |
| Crash and evidence capture | Honest but ritualized | **Adapt** | Logs and dumps are real, but current collection still starts in hidden storage, service-account paths, and reproduction ritual rather than one ordinary page | `304-crash-capture-page-private-freeze-manifest-and-service-account-origin-interface-spec.md` |

The sharpened line is now:

> when Resilio is honest about health and repair only by scattering the answer across warnings, KB ladders, hidden files, and service-account rituals, AnonSync should copy the candor and replace the page.


## Further scorecard lines after rev0174

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Active bind / path truth | Honest but too implicit | **Adapt** | Resilio tells the truth about local-only rename and move limits, but the ordinary answer still depends on path fields, defaults, and later errors | `305-share-path-page-current-bind-root-volume-and-relocation-eligibility-interface-spec.md` |
| Relocation and path repair | Practical | **Adapt** | Cross-volume moves, missing paths, and reconnects are all real, but the operator still reconstructs one answer from several docs and rituals | `306-relocate-review-page-same-lineage-cross-volume-and-peer-continuity-interface-spec.md` |
| Pathless disconnected presence | Useful concept | **Adapt** | `Disconnected` is a real state, but it still hides too much scope and future-action meaning behind one chip and a `Connect` button | `307-disconnected-share-page-pathless-presence-connect-choice-and-removal-scope-interface-spec.md` |
| Rename / move propagation explanation | Strong underlying honesty | **Adapt** | Archive/hash replay truth is useful, but it still lives apart from the action and receipt that need it most | `308-rename-move-explanation-page-local-path-change-remote-replay-and-archive-dependence-interface-spec.md` |

The sharpened line is now:

> when Resilio keeps path continuity honest only by splitting it across move/rename FAQs, disconnected-state behavior, duplicate-folder repair, and archive-replay explanation, AnonSync should copy the honesty and replace the pages.


## Further scorecard lines after rev0175

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Surface capability truth | Honest but article-shaped | **Adapt** | Resilio admits platform asymmetry, but the ordinary answer still depends on Linux peculiarities, Android/iOS UI docs, and separate behavior notes | `309-surface-capability-page-action-parity-and-reason-coded-gaps-interface-spec.md` |
| External edit semantics | Honest but too hidden | **Adapt** | iOS copy/edit/save-back truth is real, but it still lives in one platform tutorial instead of one ordinary review surface | `310-external-edit-review-page-copy-bind-saveback-and-duplicate-risk-interface-spec.md` |
| Background freshness | Real but scattered | **Adapt** | Continuous, conditional, and foreground-only delivery still require cross-reading background, battery, network, and platform pages | `311-background-delivery-page-suspend-gates-freshness-floor-and-catchup-risk-interface-spec.md` |
| Mobile storage and cleanup | Useful but split | **Adapt** | Sandbox, downloads, shared links, clear-local-files, and history residue remain spread across several mobile surfaces | `312-mobile-storage-page-sandbox-clearance-downloads-and-reacquireability-interface-spec.md` |

The sharpened line is now:

> when Resilio keeps cross-surface truth honest only by splitting it across Linux/WebUI peculiarities, Android settings, iOS edit/storage caveats, and background notes, AnonSync should copy the honesty and replace the pages.


## Additional scorecard line added in rev0178

### Reachability and route proof

- **Borrow:** visible listening port, direct-preferred language, relay fallback, manual endpoint pinning in constrained networks
- **Adapt:** one listener-proof page, one pairwise route-proof page, one least-destructive repair ladder, one endpoint-trust page
- **Do not clone:** preference-only port truth, troubleshooting-shaped directness explanations, and bare `IP:port` pins without provenance or freshness grade


## Additional current borrow/adapt boundary after rev0180

Current official docs also support one more now-clear line:

- **Borrow** the candor that destructive convenience and optimization have semantic cost.
- **Adapt** read-only overwrite, placeholder-evict safety rails, deferred readiness, and transfer-method choice into first-class pages.
- **Do not clone** a product contract where those meanings still live in a FAQ, Folder Preferences, RSLS instructions, power-user toggles, and warning prose.


## Further scorecard pressure after rev0183

| Resilio family | Product idea strength | Clone line | Why not clone the page contract | AnonSync replacement page |
| --- | --- | --- | --- | --- |
| Share artifact family (key / link / QR) | Strong | **Adapt** | Carrier flexibility is valuable, but artifact semantics still depend on folder class, approval path, and scattered support prose | `342-share-capability-page-artifact-family-approval-model-and-rights-ceiling-interface-spec.md` |
| Incoming requester approval | Strong | **Adapt** | Requester proof and approval reuse are valuable, but the ordinary answer still lives across link-flow and share-dialog docs | `343-incoming-share-request-page-requester-proof-auto-approval-basis-and-response-ladder-interface-spec.md` |
| Mutable member grants | Strong | **Adapt** | Live grant edits are useful, but editability fences and revoke scope still depend on subject kind and peer-list ritual | `344-member-access-page-grant-origin-editability-and-future-update-revocation-interface-spec.md` |
| Manual claim / paste / scan intake | Strong | **Adapt** | Carrier flexibility is useful, but approval-capable artifacts and raw capability material are still too easy to flatten into one generic intake box | `345-manual-claim-page-key-link-qr-equivalence-and-no-approval-warning-interface-spec.md` |

The sharpened line is now even simpler:

> when Resilio has a good capability idea but still spreads one ordinary answer across artifact docs, approval docs, and peer-management docs, AnonSync should copy the idea and replace the page.


## Further scorecard pressure after rev0184

| Resilio family | Product idea strength | Clone line | Why not clone the page contract | AnonSync replacement page |
| --- | --- | --- | --- | --- |
| Subject class (Standard vs Advanced) | Strong | **Adapt** | The class cliffs are real and worth exposing, but the ordinary answer still depends on architecture notes, not one stable page | `347-subject-class-page-capability-family-owner-model-and-mutation-cliffs-interface-spec.md` |
| Class upgrade | Honest but too terse | **Adapt** | Remove/re-add cutover truth is useful, but `upgrade` still hides successor-epoch meaning in a how-to | `348-class-upgrade-review-page-standard-to-advanced-cutover-and-peer-epoch-interface-spec.md` |
| Linked read-only workaround | Honest but too indirect | **Adapt** | The workaround reveals a real authority-model limit, but the operator still discovers it through a raw-key ritual rather than one explicit exception page | `349-linked-readonly-exception-page-owner-domain-breakout-and-separate-subject-warning-interface-spec.md` |
| Peer-row grouping by class | Strong | **Adapt** | Class-dependent grouping is real, but user-family vs device-row meaning still lives in examples and screenshots rather than one explicit list contract | `350-peer-identity-view-page-user-aggregate-vs-device-row-and-class-dependence-interface-spec.md` |

The sharpened line is now even simpler:

> when Resilio admits real class cliffs but still makes the operator learn them from how-tos, absent controls, and peer-list examples, AnonSync should copy the honesty and replace the pages.

## Revision addendum — performance observability, causal attribution, and expectation setting

Current official Resilio docs are usefully candid that graphs, peer-level RTT/protocol rows, disk queue/load, and workload shape all matter.
That is worth borrowing.
What is still not worth cloning is the contract that leaves the ordinary operator answer spread across a graph article, a slow-speed checklist, and preference folklore.

The AnonSync replacement in this revision is four fixed pages:

- `352` for **activity metrics**
- `353` for **peer connection table / causal attribution**
- `354` for **disk pressure**
- `355` for **throughput expectation**

The tighter doctrinal answer is:

> a sync product should never make `speed`, `latency`, `queue`, or `slow` look self-explanatory when route class, peer asymmetry, host-wide pressure, and file shape are all real states.



## Further score lines after rev0187

| Resilio family | Product idea strength | Clone line | Why not clone the page contract | AnonSync replacement page |
| --- | --- | --- | --- | --- |
| Browser-first local control | Strong | **Borrow** | Linux/service-heavy browser control is still the right instinct | Keep browser-first local control as a first-class surface |
| Listener exposure and bind widening | Strong | **Adapt** | Current docs are candid, but exposure truth still lives across setup, troubleshooting, and config snippets | `363` Control listener |
| Browser distrust / warning recovery | Useful | **Do not clone** | Current docs still normalize browser ritual, HSTS clearing, and config edits as the main explanation path | `364` Browser trust recovery |
| Web credential reset | Useful | **Do not clone** | Current docs still route one recovery path through settings-file deletion that duplicates devices and resets preferences | `365` Control access recovery |
| Browser-open link intake from control surfaces | Useful | **Adapt** | Current docs still admit WebUI cannot consume the direct-open path and fall back to generic manual paste | `362` Control launch plus `270` Import artifact |

The sharpened line is now simpler again:

> copy the browser-first practicality; refuse the browser-, config-, and filesystem-ritual ownership of ordinary control truth.

## Further score lines after rev0193

| Resilio family | Product idea strength | Clone line | Why not clone the page contract | AnonSync replacement page |
| --- | --- | --- | --- | --- |
| Conflict-file candor | Strong | **Adapt** | Current docs are candid that `.Conflict` artifacts are real data, but the ordinary answer still depends on suffix interpretation and troubleshooting prose | `398` Conflict evidence |
| Unsupported link / junction disclosure | Strong | **Adapt** | Current docs admit platform-dependent support and target exclusion, but the consequence still lives across separate link docs | `399` Unsupported entry |
| Invalid-name / portability warnings | Useful | **Do not clone** | Current docs still split invalid symbols, unicode/path-length limits, and rename/move fallout across one-off warnings and troubleshooting lists | `400` Portability repair |
| Share-stalling path policy toggles | Useful | **Do not clone** | Current docs still hide a real semantic choice (`emit conflict` versus `share won't sync`) in power-user settings | `397` Namespace blockage |

The tighter line is:

> when Resilio is honest about namespace risk but still makes the operator reconstruct it from suffixes, troubleshooting bullets, and advanced settings, AnonSync should copy the honesty and replace the pages.
## Further score lines after rev0194

| Resilio family | Product idea strength | Clone line | Why not clone the page contract | AnonSync replacement page |
| --- | --- | --- | --- | --- |
| Freshness basis / detection reality | Strong candor | **Adapt** | Current docs still say sync starts immediately, then qualify the claim across notifications, rescans, and caveat pages | `402` Freshness basis |
| Detection downgrade | Strong | **Adapt** | Watcher exhaustion, path-class loss, disabled notifications, and service-path downgrade still surface through separate articles instead of one page | `403` Detection downgrade |
| Rescan as operational repair | Useful | **Do not clone** | Rescan is real and worth keeping, but its scope, proof uplift, and non-effects still hide in FAQs and troubleshooting | `404` Rescan review |
| Changed-file publication state | Useful | **Adapt** | Current docs still make the operator reconstruct `detected vs indexed vs fetchable vs landed` from status/history/queue ritual and internal-task prose | `405` Change publication |

The sharpened line is now simpler again:

> copy the freshness candor; refuse the FAQ-, warning-, and folklore-shaped ownership of ordinary freshness truth.
## Further score lines after rev0195

| Resilio family | Product idea strength | Clone line | Why not clone the page contract | AnonSync replacement page |
| --- | --- | --- | --- | --- |
| Tracker / LAN / predefined-host decomposition | Strong candor | **Adapt** | Current docs are candid that discovery lanes differ, but the ordinary answer still depends on key-flow and settings docs instead of one stable page | `407` Reachability basis |
| Pair directness / relay fallback truth | Strong | **Adapt** | Current docs expose relay icons and direct-preferred logic, but the ordinary answer still depends on peer-list interpretation, speed notes, and troubleshooting prose | `408` Peer route |
| Connectivity repair ladder | Useful but too support-shaped | **Do not clone** | Current docs still bury the least-widening repair sequence inside `Peers aren't connecting` and slow-speed checklists | `409` Connectivity repair |
| Disclosure delta of route toggles | Useful but too hidden | **Do not clone** | Current docs still split tracker/LAN/known-host/relay observer consequences across security prose, key flow, and `LAN only` ritual | `410` Exposure widening review |

The tighter line is:

> when Resilio is honest about discovery lanes and relay reality but still makes the operator reconstruct route truth from settings, privacy notes, and troubleshooting prose, AnonSync should copy the honesty and replace the pages.

## Further score lines after rev0196

| Resilio family | Product idea strength | Clone line | Why not clone the page contract | AnonSync replacement page |
| --- | --- | --- | --- | --- |
| Scheduled quiet windows and partial-pause candor | Strong candor | **Adapt** | Current docs honestly describe that `Paused` still leaves some effects alive, but the ordinary answer still hides in one schedule article instead of one stable page | `413` Quiet window |
| Hidden-work / recoverable-backlog warnings | Strong | **Adapt** | Current docs admit hashing, block checks, compare, and disk work can dominate before visible transfer, but the ordinary answer still lives in warning prose | `412` Motion basis |
| Practical bottleneck families | Useful | **Do not clone** | Current docs still list relay, small files, remote-upload ceiling, disk, and security software as troubleshooting bullets instead of one causal page | `414` Bottleneck cause |
| Wake / resume / catch-up truth | Useful but too scattered | **Do not clone** | Current docs still split wake, battery, background, source-return, and overwrite risk across mobile, runtime, and warning articles | `415` Resume catch-up |

The tighter line is:

> when Resilio is honest about quiet windows, hidden work, and practical bottleneck families but still makes the operator reconstruct motion truth from schedules, runtime notes, and troubleshooting prose, AnonSync should copy the honesty and replace the pages.


## Addendum after rev0197 — hidden subject state, sidecars, and continuity spine

Another current Resilio pass now clarifies one more borrow/adapt/reject line.

### Borrow directly

AnonSync should copy these instincts with little embarrassment:

- admit that a sync subject has product-owned state in addition to payload bytes
- admit that history, metadata fallback, and in-flight residue are real managed families
- admit that continuity-bearing identifiers are ordinary operator concerns

### Adapt instead of clone

AnonSync should preserve the use case but change the contract for:

- exclusion and xattr policy sidecars
- hidden managed-byte browsing
- subject move / rehome continuity explanation

### Do not clone

AnonSync should reject these exact clone lines:

1. hidden `.sync` contents acting as the primary public explanation surface for subject state
2. local text sidecars acting as the main semantic home of exclusion and metadata carriage truth
3. `delete .sync and re-add` functioning as the ordinary continuity explanation instead of one explicit preserve-vs-recreate review
4. raw filesystem spelunking being required to understand Archive, `.!sync`, or stream stubs

The scorecard implication is simple: keep the candor, reject the hidden-folder-first page contract.


## Addendum after rev0200 — advanced overrides and hidden policy provenance

Another current Resilio pass now clarifies one more borrow/adapt/reject line.

### Borrow directly

AnonSync should copy these instincts with little embarrassment:

- admit that low-level settings can materially change safety, discovery, retention, and runtime cost
- admit that some important policy really does need an exact source and precedence story
- admit that restart and explicit clearance can be part of making a new truth actually true

### Adapt instead of clone

AnonSync should preserve the use case but change the contract for:

- advanced-override inspection and editing
- source precedence between visible UI, hidden advanced settings, and declared config
- retention / clearance controls for remembered peers and route facts
- runtime-bias tuning for disk, network, indexing, and integrity cost

### Do not clone

AnonSync should reject these exact clone lines:

1. a giant advanced-preferences table serving as the main public explanation surface for ordinary operator truth
2. config snippets silently outranking interactive surfaces without one current-state page naming that precedence
3. special-case help articles being required to learn that a narrower route claim still needs peer-memory clearance
4. performance-bias toggles being understandable only after reading side-effect prose in a low-level settings table

The scorecard implication is simple: keep the candor, reject the advanced-table-first page contract.


## Addendum after rev0202 — external recipes, exact targets, and postcondition proof

Another current Resilio pass tightens the scorecard in a new ordinary place:

- current docs still openly admit that some real fixes happen outside the product surface
- current docs still require exact commands, hidden-file operations, browser cache or trust changes, config edits, and restart rituals
- current docs still often prove only that the step *ran*, not that the product truth now holds
- current docs still make continuity-preserving repair and continuity-recreating reset too easy to confuse
- current docs still make the operator infer target scope from prose instead of one normalized target tuple

So one more strong no-clone reason is now clear:

> Resilio is still worth borrowing for its candor that some repairs are external, exact, and sometimes invasive, but not for the way ordinary answers about `what step this is`, `what it touches`, `what had to stop first`, and `what proves success afterward` still live across browser-warning docs, support how-tos, config notes, and troubleshooting articles instead of one stable page family.

The replacement page family added in this revision is:

- `442` External recipe
- `443` Command step
- `444` Off-product execution
- `445` Postcondition verification

## Revision addendum — warning ownership, blast radius, and recovery-rung truth after rev0203

The archive should now treat one more Resilio line as explicitly `adapt, do not clone`:

- **warning class / blocker scope / safest next rung / acknowledgment residue**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer can depend on:

- whether the warning is observer degradation, missing source, hidden-work backlog, local-state corruption, chronology failure, merge-risk, or identity failure
- whether the affected scope is one item, one subject, one seat, hidden continuity state, or linked identity state
- whether the safest next move is wait, inspect, same-lineage repair, recreate-successor repair, or escalation
- whether `Ignore`, `Hide`, or disabling delivery changed only visibility rather than truth

So the tighter scorecard entry is:

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Warning taxonomy / blast radius / repair rung / dismissal residue | Useful but scattered | **Adapt** | Current docs still spread `what kind of warning is this`, `how wide is it`, `what exact next rung is safest`, and `what did acknowledgement really change` across core-warning rows, one-off warning articles, troubleshooting prose, and hidden settings | **Warning page**, **Blocker scope**, **Recovery rung**, and **Warning history** pages |

The more precise answer to `why not just clone Resilio here too?` is now:

> because the product idea is strong, but the interface contract still lets warning strings, related-article hops, and dismissal folklore partially own degraded-state truth.

## Revision addendum — mobile capture-source, path-class, and reacquire truth after rev0204

The archive should now treat one more Resilio line as explicitly `adapt, do not clone`:

- **mobile source class / path class / durable sink / local-clear reacquireability**

Current official Resilio docs still show a useful product, but they also still show that one ordinary mobile answer can depend on:

- Camera Backup and Android Backup articles for source/delete contract
- Simple Mode and SD-card articles for writable-path truth
- storage-management and file-sharing articles for local-clear versus history residue
- iOS peculiarities and edit/save-back notes for copied-out working-file truth
- battery / autosleep notes for whether bytes can actually return later

So the tighter scorecard entry is:

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Mobile capture-source / path-class / sink / reacquire truth | Useful but scattered | **Adapt** | Current docs still spread `what source class is this`, `what path class is actually writable`, `what sink contract did I just create`, and `can I clear this now and honestly get it back later` across Camera Backup, Android Backup, Simple Mode, SD-card, storage-management, file-sharing, and iOS-peculiarity pages | **Capture source**, **Mobile path class**, **Capture sink**, and **Mobile reacquire** pages |

The more precise answer to `why not just clone Resilio here too?` is now:

> because the platform reality is real, but the interface contract still lets platform-specific articles partially own ordinary mobile truth.

## Revision addendum — compromised linked-seat containment and broader rotation truth after rev0205

The archive should now treat one more Resilio line as explicitly `adapt, do not clone`:

- **compromised seat / narrowest cutoff / broader rotation / residual authority**

Current official Resilio docs still show a useful product, but they also still show that one ordinary incident answer can depend on:

- whether the suspect seat was encrypted at rest
- whether it belonged to a linked-owner cohort
- whether per-subject `Disconnect` is sufficient or only future-facing
- whether remote unlink is unavailable and broader rotation is therefore necessary
- whether trusted survivors must relink and reshare under a new epoch
- what already-landed bytes and unresolved residue remain afterward

So the tighter scorecard entry is:

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Compromised linked-seat containment / broader rotation / residual authority | Useful but scattered | **Adapt** | Current docs still spread `what can this suspect seat still do`, `what is the narrowest believable cutoff`, `when is whole-identity rotation required`, and `what residual authority still remains afterward` across a stolen-device note, private-identity docs, user-management semantics, licensing behavior, and encrypted-peer guidance | **Compromised seat**, **Containment lane**, **Rotation rebuild**, and **Residual authority** pages |

The more precise answer to `why not just clone Resilio here too?` is now:

> because the incident candor is strong, but the interface contract still lets support rituals and related-article hops partially own compromise truth.

## Revision addendum — bounded handoff, redemption, and transfer-history residue after rev0206

The archive should now treat one more Resilio line as explicitly `adapt, do not clone`:

- **bounded file handoff / open redemption / receive inbox / transfer-history residue**

Current official Resilio docs still show a useful product, but they also still show that one ordinary file-send answer can depend on:

- whether the action created a bounded one-way transfer or a live shared subject
- whether expiry is sender-chosen desktop policy, mobile fixed policy, or already elapsed
- whether possession of the link is the only audience gate because use count and device bans do not exist
- whether the receive path is chooser-driven, defaulted, config-owned, or fixed by a mobile lane
- whether cleanup affects UI rows, local bytes, history, or only a stale claim

So the tighter scorecard entry is:

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Bounded handoff / open redemption / receive-path ownership / transfer-history residue | Useful but scattered | **Adapt** | Current docs still spread `is this live or bounded`, `who may redeem it`, `where will it land`, and `what survives after cleanup or expiry` across the single-file article, mobile sharing notes, receive-path defaults, and power-user transfer-history settings | **Bounded handoff**, **Redemption lane**, **Receive inbox**, and **Transfer history** pages |

The more precise answer to `why not just clone Resilio here too?` is now:

> because the product idea is strong, but the interface contract still lets convenient send/receive verbs hide the real snapshot, audience, landing-path, and residue truth.


## Revision addendum — support lane, log route, and crash custody after rev0207

The archive should now treat one more Resilio line as explicitly `adapt, do not clone`:

- **support lane / log capture window / report send / crash artifact custody**

Current official Resilio docs still show a useful product, but they also still show that one ordinary diagnostic answer can depend on:

- whether the seat is in self-serve/forum mode or a staffed support lane
- whether the operator enabled anonymous metrics, debug logs, profiler capture, or crash artifact collection
- whether restart and a non-trivial hold window are still required before evidence is meaningful
- whether packet delivery uses in-product send, manual attachment, mobile hidden-log extraction, or SSH/terminal dump workflow
- whether attachment ceilings, hidden paths, or service-account storage roots change what actually leaves
- what logs, profiler traces, or dumps still remain on disk afterward

So the tighter scorecard entry is:

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Support entitlement / diagnostic depth / send route / crash-artifact residue | Useful but scattered | **Adapt** | Current docs still spread `who can receive this`, `what capture is active`, `how does it leave`, and `what remains local afterward` across the power-user table, manual/automatic/mobile log guides, and crash/core-dump pages | **Support lane**, **Log capture window**, **Report send**, and **Crash artifact** pages |

The more precise answer to `why not just clone Resilio here too?` is now:

> because the diagnostic candor is strong, but the interface contract still lets support articles and send rituals partially own ordinary disclosure truth.


## Revision addendum — space pressure, byte classes, and reclaim proof after rev0208

The archive should now treat one more Resilio line as explicitly `adapt, do not clone`:

- **space pressure / byte-class inventory / reclaim preview / reclaim proof**

Current official Resilio docs still show a useful product, but they also still show that one ordinary storage answer can depend on:

- whether the active stop floor comes from the default warning threshold or additional reserve offsets
- whether the bytes are payload, placeholders, retained history, transfer/download residue, diagnostics, service-state files, or abnormal leftovers
- whether the safest reclaim step preserves continuity, weakens retention, or silently shifts to a different action family
- whether the operator can prove afterward that the right bytes changed and the right truths stayed intact

So the tighter scorecard entry is:

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Space pressure / byte classes / reclaim preview / reclaim proof | Useful but scattered | **Adapt** | Current docs still spread `what is consuming space`, `what will stop syncing`, `what safe-first reclaim exists`, and `what exactly changed afterward` across warnings, power-user settings, Sync-mode docs, Archive docs, mobile storage pages, storage-folder notes, and uninstall cleanup lore | **Space pressure**, **Byte-class inventory**, **Reclaim preview**, and **Reclaim receipt** pages |

The more precise answer to `why not just clone Resilio here too?` is now:

> because the storage candor is strong, but the interface contract still lets warning articles, hidden settings, and cleanup folklore partially own ordinary reclaim truth.


## Revision addendum — network paths, protocol discipline, and freshness risk after rev0209

The archive should now treat one more Resilio line as explicitly `adapt, do not clone`:

- **network path class / protocol discipline / detection grade / network-subject admission**

Current official Resilio docs still show a useful product, but they also still show that one ordinary remote-path answer can depend on:

- whether the bound path is local, SMB-mounted, UNC-entered under service, or otherwise outside ordinary local watcher assumptions
- whether mutations arrive through one authoritative protocol or a dangerous mixed direct-plus-Samba pattern
- whether this location has live notifications, rescan-only freshness, or restart-dependent publication
- whether the runtime account actually has durable write permission and stable lock behavior on this path

So the tighter scorecard entry is:

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Network path class / protocol discipline / detection grade / network-subject admission | Useful but scattered | **Adapt** | Current docs still spread `what path class is this`, `which mutation lane is authoritative`, `how fresh can this location honestly be`, and `should this remote path be admitted at all` across the SMB article, service troubleshooting, freshness notes, and old fix history | **Network path class**, **Protocol discipline**, **Detection grade**, and **Network subject admission** pages |

The more precise answer to `why not just clone Resilio here too?` is now:

> because the network-path candor is strong, but the interface contract still lets troubleshooting articles and path folklore partially own ordinary remote-storage truth.
