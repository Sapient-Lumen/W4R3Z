# Uninstall clearance review page, program removal, settings residue, shell release, and shared-data survivor interface spec

## Purpose

The host-integration contract sheet publishes the current footprint.
This page decides what a requested removal action will actually clear.

The practical review question is:

> when the operator says `remove this`, are they asking to remove the app binary, clear settings, release shell hooks, remove service state, or erase all sync residue and hidden archives?

Current official Resilio docs still expose all the raw ingredients:

- full silent removal is not possible on Windows
- manual steps may include Control Panel, deletion of Program Files residue and registry entries, and a reboot because File Manager may still hold DLLs loaded
- service installs have separate service-storage locations depending on runtime principal
- uninstall does not delete previously shared folders
- hidden `.sync/Archive` residue may survive and should be removed manually if desired
- Finder Extension on macOS may need to be quit before the app can be removed cleanly

AnonSync should make the clearance review first-class rather than burying it in uninstall prose.

## When this page appears

Render this review when any of the following is true:

- the user requests uninstall or removal from a host
- a repair action requires removing and reinstalling host integration
- service and interactive footprints coexist
- shell hooks or helper processes may still hold files in use
- the operator asks for `clean uninstall`, `remove all traces`, or equivalent

## Review sections

### 1) Removal intent class

Show:

- binary/app removal
- settings/state-root removal
- helper/service removal
- shell-hook release
- shared-subject/data erasure
- log/debug residue removal

Verdicts:

- `program-only`
- `program-plus-settings`
- `host-footprint-clearance`
- `full-data-erasure`
- `intent-ambiguous`

### 2) Survivor map

Show:

- shared folders that will remain
- hidden archives / `.sync` survivors
- service storage survivors
- registry/preferences survivors
- logs/debug residue survivors

Verdicts:

- `known-survivors`
- `no-known-survivors-in-scope`
- `survivor-scan-incomplete`

### 3) Release fit

Show:

- shell DLL / extension release state
- helper-process or Finder-extension release state
- whether reboot/relaunch/quit is required
- whether the host is still holding removable files open

Verdicts:

- `ready-to-clear`
- `restart-pending`
- `reboot-pending`
- `helper-still-running`
- `unknown`

### 4) Clearance-language fit

Show:

- what the product can safely say after the chosen action
- what it cannot safely say

Examples:

- safe: `program removed; subject data remains`
- blocked: `all traces removed`

### 5) Review decision

Return one of:

- `proceed`
- `proceed-with-survivor-warning`
- `hold-for-release-step`
- `block-stronger-claim`

## Main surface

A compact result should read like one of these:

- `program and settings removal requested; shared folders and archive survivors remain out of scope`
- `clearance held until shell hooks are released`
- `service storage still survives under a different runtime principal`
- `blocked stronger claim: host footprint may shrink, but full residue erasure is not yet proven`

## Required copy blocks

### Survivor warning

`Removing the application is weaker than clearing all host and subject residue. Shared folders, hidden archives, service state, or registry/preferences may survive.`

### Hold for release

`The host is still holding integration artifacts in use. Release Finder/Explorer/helper state first, then recompute clearance.`

### Stronger-claim block

`This review cannot truthfully promise that all traces are gone. Narrow the claim or expand the clearance scope.`

## Event language

Use phrases such as:

- `clearance review prepared`
- `survivor map published`
- `shell-hook release pending`
- `stronger removal sentence blocked`

Avoid phrases such as:

- `clean uninstall complete`
- `everything deleted`
- `fully wiped`

## Design tests

The page fails if any of these remain true:

- uninstall still implies subject-data erasure by default
- reboot-required hook release is not preserved in the review
- service-storage survivors under another principal are invisible
- hidden archive survivors are absent from the removal contract
