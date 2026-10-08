# Resilio governance plane, override authority, and control-surface fragmentation evaluation

## Why this pass exists

The archive already had stronger doctrine for action surfaces, activation boundaries, effective seat posture, queue-governance provenance, and name-plane truth.
What it still lacked was one direct current Resilio evaluation for a narrower but important question:

> where does a value actually live, which surface may mutate it, which surface can merely witness it, which surface can override it, and when does a local manual override sever future inheritance from a stronger default plane?

Current official Resilio docs still show a useful, living product, but they also still show that one ordinary answer is spread across several article families at once:

- `Folder Preferences`
- `Power user preferences`
- `Running Sync in configuration mode`
- `Sync Service Troubleshooting on Windows`
- `File download priority`
- `Settings on mobile platforms`
- `Is there a Command Line Interface (CLI) for Resilio Sync on Windows?`

## Current official Resilio evidence that matters here

Current official docs still say all of the following:

- `Folder Preferences` is a **desktop-only** control surface for per-folder behavior.
- `Power user preferences` is a distinct advanced surface and even documents settings that are **ignored in Linux WebUI**.
- `File download priority` still shows a split between a **global default** (`folder_defaults.transfer_priority`) and a **per-share manual override**, and it still says a share that was manually set no longer follows later global changes even if the share is later set back to `None`.
- `Running Sync in configuration mode` still says config can include Advanced Preference parameters, can create only **Standard** folders rather than Advanced folders, and if shared folders are defined in config then **WebUI is disabled** and those configured folders override folders previously added from WebUI.
- `Sync Service Troubleshooting on Windows` still says service-specific config has to live in the **service storage folder**, that switching the service to **Local System** creates a different storage world with no old folders present, and that some WebUI audience changes require **service restart**.
- `Is there a Command Line Interface (CLI) for Resilio Sync on Windows?` still says CLI switches can force config mode, loopback-only WebUI, alternate storage path, or silent/minimized start.
- `Settings on mobile platforms` still shows a much narrower mutation surface than desktop: identity, general, and network settings are present there, but the richer desktop-only folder-preference and power-user planes are not described as mobile peers of those surfaces.

So current Resilio still contains a real but scattered answer to `where is the authority for this value, who changed it, what overrode what, and what surface can actually prove the live winner?`

## What Resilio still gets right

### 1) It is candid that not all settings live in one plane

The docs do not pretend that everything lives in one universal preferences page.
They openly describe desktop folder preferences, advanced power-user settings, config-file startup control, service-local config storage, CLI launch switches, and mobile settings.
That honesty is valuable.

### 2) It is candid that defaults, local overrides, and startup-authored values are different realities

The docs still admit that a per-share manual priority can sever inheritance from a global default, and that config-authored folders can replace folders previously added from WebUI.
That is important contract truth.

### 3) It is candid that service/runtime class changes can move the effective world

The docs still say switching service account or service storage can produce a new world with no previous folders visible, and that some WebUI listener changes require service restart.
That candor matters.

## Why this is still a good reason not to clone them

### 1) Control surfaces still overstate sameness

Current docs still make the operator combine UI help, power-user docs, config-mode docs, service troubleshooting, and feature pages to answer one ordinary question:

- where can this value be set?
- which plane wins if there is a conflict?
- is this share still inheriting the global default?
- can mobile or WebUI even see or change this value?
- is the value already live or only saved into a colder plane?

AnonSync should not inherit a contract where `setting exists` must silently carry all of that.

### 2) Manual detachment from defaults is still too easy to miss

Current Resilio still admits that a share can stop following the global default after a manual per-share change, and that setting the share back to `None` does not magically restore ordinary inheritance.
A serious sync product should not let `looks default again` impersonate `is inheriting live default again`.

### 3) Startup-config authorship still has too much hidden precedence

Current Resilio still says config-authored folder sets can disable WebUI and override previously added folders, and service storage can silently move the effective world.
That is too much hidden authorship for such an important truth.

## What AnonSync should do instead

AnonSync should make **governance plane** first-class.
Every meaningful value needs one stable answer for:

- authorship plane
- scope
- override precedence
- inheritance status
- current witness surface
- activation boundary
- next strongest safe sentence

The product should never let `Preferences`, `Advanced`, `Config`, `Service`, `CLI`, and `Mobile` blur into one vague control story.

## Hard decisions now locked

1. **Governance plane is first-class.**
   Every serious value must name its plane family: live UI, advanced UI, per-subject override, startup config, service storage, launch switch, or external host control.

2. **Default inheritance and manual detachment are different truths.**
   A value may be inheriting, manually detached, config-pinned, or unknown. `None` must not impersonate restored inheritance.

3. **Mutation surface and witness surface are different truths.**
   A surface may show the winner without being allowed to author it; a colder plane may author the winner without being visible on the current surface.

4. **Cold authorship stays visibly colder.**
   Config-file or service-storage ownership must never be flattened into ordinary same-surface preferences.

5. **World shift outranks label continuity.**
   If service account or storage root changes, the product must be willing to say `new governance world` even if some labels or paths look familiar.

## What this tranche adds to the archive

This revision adds five more first-class pages:

- **Governance-plane contract sheet**
- **Policy-authorship review**
- **Mutation-authority proof**
- **Governance-plane timeline**
- **Governance-plane lineage receipt**

Together they let AnonSync answer one ordinary operator question without archaeology:

> who really owns this value right now, who overrode whom, what surface can prove it, and what stronger sentence is still blocked?
