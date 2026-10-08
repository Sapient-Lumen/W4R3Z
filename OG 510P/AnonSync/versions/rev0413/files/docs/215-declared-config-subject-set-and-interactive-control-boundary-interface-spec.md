# Declared-config subject set and interactive-control boundary interface spec

## Purpose

The archive already had settings-layer collapse, baseline rollout, and channel-parity language.
What it still lacked was one dedicated interface contract for a sharper seam exposed by current official Resilio docs:

> when a declarative config file names the subjects and policies up front, what exactly is the relationship between that declared world and the operator’s live interactive control surface?

Current official Resilio docs still say configuration mode is useful for applying the same settings across many machines.
They also still say config mode can set up only **Standard** folders, that non-default `storage_path` creates settings there, and that if shared folders are specified in the config file the **WebUI is disabled** and those configured folders override what was previously added from WebUI.

That is not just `headless is different`.
It is a branch in authority and mutability.

## Core decision

AnonSync should treat declarative control as a **declared branch**, not as an invisible override of the live interactive world.
A declaration may be authoritative, advisory, or import-only — but it must never silently replace the interactive subject set.

At minimum the product should distinguish:

- `declared-authoritative`
- `declared-advisory`
- `declared-import-preview`
- `interactive-live`
- `mixed-with-reviewed-overrides`

## Why this matters

Current official Resilio docs still expose four seams AnonSync should not inherit:

- config-declared subjects can override earlier interactive subjects
- interactive control may disappear once config-declared shares exist
- declarative mode is limited to a narrower capability family than the full product surface
- moving `storage_path` can quietly create another settings world while still feeling like `the same app with a config`

So AnonSync should keep one harder rule:

> a declarative branch may constrain or drive the live node, but the operator must always be able to inspect the declared-vs-live diff before that branch becomes effective.

## Fixed review order

Every declaration import or activation surface should render the same sections in the same order:

1. **Declaration origin**
2. **Declared-vs-live subject graph**
3. **Capability envelope delta**
4. **Mutability boundary**
5. **Activation choice**
6. **Declaration receipt**

### 1) Declaration origin

This section should show:

- declaration source (file, bundle, generated baseline, imported service profile)
- declared root / declared state scope
- whether the declaration is fresh, already active, or only previewed
- who authored or supplied it if known

The operator must be able to answer: **where did this declared world come from?**

### 2) Declared-vs-live subject graph

This section should show:

- subjects currently live
- subjects declared
- overlaps
- declared additions
- declared removals
- declared replacements or policy narrowing

The operator must be able to answer: **what would this declaration add, remove, replace, or shadow?**

### 3) Capability envelope delta

This section should show:

- capabilities expressible in the declaration
- capabilities already used by the live set that the declaration cannot represent directly
- whether any live subject would be degraded, frozen, or converted by activation

The operator must be able to answer: **does the declaration speak the full language of the live node, or only a narrower subset?**

### 4) Mutability boundary

This section should show:

- what remains interactively editable after activation
- what becomes declaration-owned
- whether the declaration is strict, mergeable, or advisory
- what later local changes would become drift instead of ordinary edits

The operator must be able to answer: **what can I still change interactively after this branch becomes active?**

### 5) Activation choice

This section should offer only explicit choices such as:

- `activate as authoritative baseline`
- `activate as advisory baseline`
- `import for diff only`
- `activate on empty state only`
- `block because live capabilities would be degraded silently`

The product must not use a vague `run with config` control as the only explanation.

### 6) Declaration receipt

This section should show:

- declaration identity
- live graph before activation
- live graph after activation or refusal
- mutability class
- drift policy
- capability losses accepted or blocked

## Public objects

### `declaration_branch`

Fields:

- `declaration_branch_id`
- `source_ref`
- `declared_subjects[]`
- `declared_policy_refs[]`
- `declared_state_root_ref`
- `mutability_class`
- `capability_envelope`
- `created_at`

### `declaration_activation_review`

Fields:

- `declaration_activation_review_id`
- `declaration_branch_ref`
- `live_graph_ref`
- `graph_delta_summary`
- `capability_delta_summary`
- `mutability_boundary_summary`
- `recommended_activation_mode`
- `generated_at`

## Main surface

A compact banner should read like:

- `declared branch preview · 3 adds · 1 removal · 2 live-only capabilities blocked`
- `authoritative declaration active · local drift reviewed, not silently overwritten`
- `import refused · declaration cannot represent current live capabilities honestly`

## Event language

Use phrases such as:

- `declaration would shadow 4 live subjects`
- `declaration is narrower than current live capability envelope`
- `interactive editing remains allowed for local overrides only`
- `declaration imported for diff, not activated`

Avoid phrases such as:

- `Web UI disabled`
- `config applied`
- `settings overridden`

Those describe mechanics, not trustworthy meaning.

## CLI shape

```text
anonsync declaration preview ./node.baseline.json
anonsync declaration review ./node.baseline.json
anonsync declaration activate <review> --mode advisory
anonsync declaration receipt <id>
```

## Edge cases

### Declaration points at another state root

That is a branch boundary, not a simple config apply.
It must reopen continuity review.

### Live node is empty

The product may streamline activation, but still must state whether the declaration becomes authoritative or merely seeds live state.

### Declaration cannot express live subject class

Activation should block unless the operator explicitly accepts a reviewed degradation or conversion path.

## Non-clone reason

Current official Resilio docs still make declarative control feel like a useful rollout trick while letting it disable interactive control, override prior interactive inventory, and narrow the representable capability set.
AnonSync should instead keep declarations and live control in one inspectable relationship so operators never have to guess whether a config file quietly replaced the world they thought they were operating.
