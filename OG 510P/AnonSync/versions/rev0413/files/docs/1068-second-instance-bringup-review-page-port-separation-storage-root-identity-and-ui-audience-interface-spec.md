# Second-instance bringup review page, port separation, storage root, identity, and UI audience interface spec

## Purpose

Starting a second runtime on one host should never feel like ticking `open another copy`.
The operator needs one reviewed answer to:

> what exactly must be separated for this second runtime to be safe, and what will still remain forbidden even if the process starts cleanly?

Current official Resilio docs still make this seam concrete by saying Linux later instances need manually assigned ports, storage/identity can be default-derived unless made explicit, loopback-vs-LAN WebUI changes audience, and the same-folder dual claim can still corrupt the first instance's `.sync` state.

AnonSync should therefore make **second-instance bringup** a first-class review page rather than a launch footnote.

## Review order

Every second-instance bringup review should render the same sections in the same order:

1. **Requested runtime separation**
2. **Port and audience plan**
3. **Storage / identity plan**
4. **Forbidden overlap set**
5. **Apply outcome ladder**

### 1) Requested runtime separation

Show:

- proposed namespace label
- source runtime if deriving from an existing one
- launch class (`portable-cli`, `service`, `current-user-daemon`, `debug`, `temporary-review`, `unknown`)
- whether the operator intends `distinct branch`, `same-world reopen`, `migration successor`, or `unclear`

This section must answer: **what kind of second runtime is being requested?**

### 2) Port and audience plan

Show:

- requested data listener port
- whether port is fixed, random, or inherited
- requested control listener audience (`loopback`, `specific-interface`, `lan-wide`, `disabled`)
- any collision with already-lived listeners
- whether DHCP/interface fragility could make the chosen audience fail at start

The operator must be able to answer: **will this runtime own a distinct listener namespace and who could control it?**

### 3) Storage / identity plan

Show:

- proposed storage root
- whether storage root is explicit or launch-path-derived
- proposed identity root / identity reuse posture
- whether license/config material is shared, copied, or separate
- whether the plan preserves or breaks same-user same-parameter continuity

The operator must be able to answer: **is this really a separate durable world or an accidental fork of another one?**

### 4) Forbidden overlap set

Show:

- all local subject roots already claimed by other runtimes
- external or removable volumes with continuity-bearing service state
- blocked same-path candidates
- blocked shared-storage-root candidates
- any paths that require `migrate`, `reattach`, or `safe-branch review` instead of immediate bind

The operator must be able to answer: **what remains forbidden even if the process starts?**

### 5) Apply outcome ladder

Allow only reviewed outcomes such as:

- `start distinct empty namespace`
- `start distinct namespace and import reviewed successor capsule`
- `start distinct namespace with no subject binds yet`
- `reject and open migration review`
- `reject and open branch review`
- `reject due to unresolved storage / path collision`

Never flatten all of those into `start anyway`.

## Public objects

### `second_instance_bringup_review`

Fields:

- `second_instance_bringup_review_id`
- `host_ref`
- `requested_namespace_ref`
- `requested_launch_class`
- `requested_distinction_intent`
- `requested_data_listener`
- `requested_control_audience`
- `requested_storage_root`
- `requested_identity_root`
- `forbidden_overlap_refs[]`
- `recommended_outcome`
- `blocked_stronger_sentence`
- `reviewed_at`

## Decision chips

Use chips such as:

- `listener separated`
- `storage explicit`
- `identity explicit`
- `audience widened`
- `same-path blocked`
- `external-state collision`
- `migration required`

Do not use vague chips like:

- `advanced`
- `custom`
- `expert mode`

## Receipt language

After apply, the resulting receipt should say things like:

- `second runtime started as distinct empty namespace with separate listener and storage roots`
- `second runtime started but subject claims remain blocked until migration review`
- `bringup rejected because requested subject path is already owned by another local runtime`

## Narrow surfaces

On narrow or terminal surfaces, the minimum preserved facts are:

- whether the runtime is truly distinct
- whether audience widened
- whether storage root is explicit
- whether any subject paths remain blocked
- what exact stronger sentence was refused

## Design tests

The page fails if any of these remain true:

- the operator can change listener/audience without seeing namespace collision risk
- storage-root choice can still hide behind a generic `custom path`
- successful process start can still be mistaken for safe subject ownership
- same-path prohibition still appears only after corruption or warning status

## Non-clone reason

Resilio's current docs still admit the right distinctions but leave the operator to assemble them from Linux guide notes, CLI storage semantics, WebUI audience rules, and repair prose.
AnonSync should publish the bringup review directly.
