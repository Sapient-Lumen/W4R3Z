# Resilio host integration, signer trust, shell activation, and uninstall-clearance fragmentation evaluation

## Why this pass exists

The archive already had stronger language for runtime worlds, control exposure, service promotion, and ingress mutation.
What it still did not own tightly enough was one very ordinary host-facing seam:

> when a user says `install this`, `make it show up in Finder/Explorer`, or `remove it cleanly`, what exactly is being trusted, what host surfaces are being mutated, what shell affordances are only partially active, and what residue can survive even after the program is gone?

Current official Resilio docs still make that seam materially real.
They now say all of the following at once:

- Windows Defender SmartScreen may block the installer because a new code-signing certificate does not yet have enough reputation, and users may need `More info` → `Run anyway` or the file `Unblock` property to proceed.
- Silent Windows installation still triggers User Account Control, and if the user accepts, the install creates Program Files contents, icons, startup menu items, Windows Explorer context-menu items, and registry entries.
- Silent Windows removal is not fully possible; the operator may still need Control Panel, manual deletion of Program Files residue, deletion of registry entries, and even a reboot because File Manager may keep shell-extension DLLs loaded.
- Windows shell surfaces are conditional: context menu items appear only for files on NTFS, require Selective Sync for share-specific items, depend on shell-extension DLL presence and registration, and may even require `EnableLUA=1`.
- macOS Finder surfaces are also conditional: the extension may need to be toggled in Extensions/Finder Extensions, Finder relaunched, Sync restarted, and `pluginkit` repair used; other apps can conflict for the same extension space.
- Uninstall guidance still says removing the program does not delete previously shared folders, and hidden `.sync/Archive` residue can survive and grow until removed manually.

That is good candor.
It is also a strong reason not to clone the present contract.
One ordinary operator answer — `is the product installed, trusted, integrated into host shell surfaces, and truly cleared from this machine?` — still depends on combining:

- SmartScreen troubleshooting
- silent-install instructions
- shell-extension troubleshooting
- uninstall instructions
- command-line switch notes that still separate install, no-install, silent start, and minimized start

AnonSync should keep the distinctions and refuse the archaeology.

## Hard product decisions locked by this pass

1. **Host integration is not the same as program presence.**
2. **Signer trust, OS consent, shell-surface activation, and uninstall clearance are separate truths.**
3. **A successful installer launch is weaker than accepted host mutation, and accepted host mutation is weaker than proven shell-surface activation.**
4. **Program removal is weaker than clearance; clearance is weaker than subject-data erasure.**
5. **Every host-integration change needs a receipt that preserves trust prompts crossed, shell surfaces touched, residue left behind, and blocked stronger sentence.**

## What current Resilio still gets right

Current official docs still publish several truths worth borrowing.

- **Signer trust is admitted as a distinct problem.** The SmartScreen article still says a new certificate can trigger untrusted-app warnings.
- **OS consent is treated as real.** Silent install still says Windows UAC will ask permission to change system configuration.
- **Host mutations are named.** The silent-install article still enumerates icons, Program Files contents, startup menu items, Explorer context-menu items, and registry entries.
- **Shell integration is conditional, not magic.** Finder/Explorer surface docs still admit filesystem requirements, registration requirements, extension toggles, and extension conflicts.
- **Uninstall incompleteness is admitted.** Resilio still says full silent removal is not possible on Windows and that shell DLLs may require reboot before deletion.
- **Shared-data survivors are admitted.** The uninstall article still says uninstall does not delete previously shared folders and that `.sync/Archive` may require manual removal.

That is useful product honesty.
Resilio does not fully pretend that `installed`, `shows context menu`, and `gone` are the same state.

## Where current Resilio still stays too article-shaped

### 1. Trust and host mutation still split across separate stories

SmartScreen explains signer reputation.
Silent install explains UAC and host mutation.
CLI notes explain launch mode differences.
The operator still has to merge those to answer whether the app is merely present or actually trusted and host-authorized.

### 2. Shell-surface activation still looks like troubleshooting instead of contract truth

The official docs say Finder/Explorer surfaces depend on Selective Sync, NTFS, extension registration, extension toggles, Explorer/Finder restart, and sometimes `EnableLUA`.
Those are not random repairs.
They are the activation contract for host shell affordances.

### 3. Removal and clearance still blur

Program removal, settings removal, registry cleanup, shell-DLL release, service storage cleanup, and `.sync/Archive` survivor cleanup are all different truths.
Current docs preserve them, but not in one review family.

### 4. Shared-subject survival still hides behind uninstall language

The uninstall article says the program is removed but previously shared folders stay accessible in the file browser.
That is materially important.
The operator should not need to infer whether `gone` means `app gone`, `shell hooks gone`, or `all sync residue gone`.

### 5. Host integration still lacks one stronger-sentence boundary

Current docs never really give the operator one stable product-owned sentence for what may safely be claimed:

- `trusted to install`
- `host-authorized`
- `shell-integrated`
- `cleanly removed`
- `all residue erased`

The distinctions exist, but the claim ceiling still does not live in one page family.

## The tighter non-clone decision

Borrow Resilio's candor that SmartScreen reputation, UAC approval, Explorer/Finder extension state, NTFS eligibility, DLL registration, uninstall incompleteness, and `.sync/Archive` survivor residue are materially different truths.
Do **not** clone a product contract where the operator still has to merge installer warnings, command-line docs, shell-extension troubleshooting, and uninstall articles to answer whether a runtime is trusted, host-integrated, shell-active, or truly cleared.

## What AnonSync should do instead

AnonSync should treat **host integration** as one first-class reviewed family.
Every serious `install`, `enable shell surfaces`, `repair Explorer/Finder hooks`, `remove from this machine`, or `clear integration residue` flow should answer five things in one place:

1. **trust posture** — signer reputation, package provenance, and whether OS trust prompts were satisfied
2. **host mutation scope** — what host surfaces were changed or are about to change
3. **shell activation proof** — whether Finder/Explorer/context surfaces are merely intended or actually active
4. **clearance scope** — what removal clears, what survives, and what may need reboot or manual cleanup
5. **safe language** — what the product may and may not say about `installed`, `integrated`, `removed`, and `gone`

## New page obligations from this pass

The archive now needs five more workflow-owned pages:

- **Host integration contract sheet**
- **Installer trust review**
- **Shell-surface activation proof**
- **Uninstall clearance review**
- **Host-integration lineage receipt**

Those pages should sit beside runtime-world, service, and control-audience pages — not underneath installer FAQ and troubleshooting alone.
