# Host integration contract sheet page, installer trust, OS consent, shell surfaces, and clearance state interface spec

## Purpose

The archive already had pages for launch class, service world, and ingress exposure.
What it still lacked was one contract for the more ordinary workstation question:

> what exactly has this program been allowed to do to the host, which shell surfaces should exist, and what remains after a removal action?

Current official Resilio docs make the missing contract unusually obvious.
They still separate SmartScreen trust, UAC approval, shell-extension eligibility and activation, and uninstall residue.
That is not a single `installed` bit.
It is host integration.

AnonSync should therefore render one first-class **host integration contract sheet** before the operator is allowed to treat install, shell repair, or uninstall as a tiny utility action.

## Core decision

Every seat capable of mutating host integration must expose one explicit **host integration contract**.
It must say:

- what trust posture the package currently holds
- what host mutations were requested or accepted
- what shell surfaces are intended, eligible, and proven active
- what clearance class a removal action would actually achieve
- what stronger sentence the product must refuse

The product must never let `install`, `context menu missing`, or `uninstall` stand in for this truth.

## Fixed review order

Every host integration contract sheet should render the same sections in the same order:

1. **Package trust posture**
2. **Host mutation scope**
3. **Shell-surface activation**
4. **Clearance state**
5. **Strongest safe sentence**

### 1) Package trust posture

This section should show:

- package origin
- signer identity or absence
- reputation class (`established`, `new-or-low-reputation`, `unknown`, `rejected`)
- trust prompts encountered or expected
- whether OS-level block bypass was required

The operator must be able to answer: **what trust hurdles has this package crossed, and which are still external to the product?**

### 2) Host mutation scope

This section should show:

- program files created or removed
- startup/menu items created or removed
- shell extensions / Finder extensions touched
- registry or preference-store mutation class
- service or helper mutation class
- whether elevated consent is required

The operator must be able to answer: **what host surfaces changed, not just whether the app launched?**

### 3) Shell-surface activation

This section should show:

- surfaces requested (`Finder menu`, `Explorer context menu`, `overlay`, `share action`, `none`)
- eligibility gates (filesystem class, feature flags such as selective presence, OS extension settings)
- registration state
- proof state (`declared`, `registered`, `eligible`, `active`, `stale`, `conflicted`)
- restart/reboot requirements

The operator must be able to answer: **which shell affordances are actually active versus merely expected?**

### 4) Clearance state

This section should show:

- program-binary removal state
- settings/state-root removal state
- shell-hook release state
- residue survivors (shared folders, archives, service storage, registry keys, logs)
- whether reboot or manual cleanup is still pending

The operator must be able to answer: **what exactly would still remain on this host after removal?**

### 5) Strongest safe sentence

The contract sheet must always end with:

- **strongest safe sentence**
- **blocked stronger sentence**
- **why the stronger sentence is blocked**

Examples:

- strongest safe: `package launch was trusted after OS warning bypass; shell activation still unproven`
- blocked stronger: `the product is fully trusted and integrated everywhere on this host`

## Main surface

A compact card should read like one of these:

- `low-reputation signer warning crossed · elevated host mutation accepted · shell surfaces still pending proof`
- `program installed · Explorer integration requested · NTFS/registration proof missing`
- `app removed · service state and archive residue still survive`
- `shell activation blocked by host policy; install remains valid but not fully integrated`

## Required copy blocks

### Trust-forward copy

`Package presence is not yet host integration. Trust prompts crossed, host surfaces mutated, and shell affordances proven are separate facts.`

### Removal-forward copy

`Removing the program is weaker than clearing host integration residue. Shared data, hidden archives, helper state, or shell hooks may still survive.`

## Public object

### `host_integration_contract`

Fields:

- `host_integration_contract_id`
- `seat_ref`
- `runtime_ref`
- `package_origin`
- `signer_reputation_class`
- `trust_prompt_state`
- `host_mutation_scope[]`
- `shell_surface_targets[]`
- `shell_activation_state`
- `clearance_state`
- `survivor_classes[]`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `reviewed_at`

## Event language

Use phrases such as:

- `host integration contract prepared`
- `OS consent required`
- `shell activation still pending proof`
- `clearance weaker than full erasure`

Avoid phrases such as:

- `installed successfully`
- `extension fixed`
- `clean uninstall complete`
- `all traces removed`

Those lines are too strong and too flattening.

## CLI shape

```text
anonsync host contract show --seat self
anonsync host trust explain --runtime rt_01J...
anonsync host clearance show --seat self
```

## Design tests

The model is not explicit enough if any of these remain true:

- a package can be said to be `installed` without saying whether OS trust or elevation were actually crossed
- shell surfaces can be treated as active without proof of registration, eligibility, and shell uptake
- uninstall can still mean everything from binary removal to total residue erasure
- later operators cannot tell whether a reboot is required to release host hooks

## Non-clone reason

Current official Resilio docs still preserve the important distinctions, but they do so across SmartScreen notes, silent-install guidance, shell-extension troubleshooting, and uninstall instructions.
AnonSync should instead render trust posture, host mutation scope, shell activation, and clearance state as one stable reviewed object.
