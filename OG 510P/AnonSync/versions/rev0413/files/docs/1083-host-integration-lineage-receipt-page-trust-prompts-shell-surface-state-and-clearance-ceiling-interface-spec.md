# Host-integration lineage receipt page, trust prompts, shell-surface state, and clearance ceiling interface spec

## Purpose

Host integration is continuity-bearing.
It crosses trust prompts, mutates host-visible surfaces, and may leave survivors even after removal.

AnonSync therefore needs one durable receipt for any meaningful host-integration action.

## Receipt questions

Every receipt in this family must answer:

1. **What package trust posture existed at the moment of action?**
2. **What host mutation scope was accepted, refused, or partially applied?**
3. **What shell surfaces were intended and what proof class did they achieve?**
4. **What clearance scope was requested or achieved?**
5. **What stronger sentence was blocked?**

## Receipt sections

### 1) Decision summary

Show:

- decision class (`accepted`, `accepted-with-warning`, `held`, `blocked`, `retracted`)
- operator intent
- host seat / runtime
- reviewed timestamp

### 2) Trust snapshot

Show:

- package origin
- signer reputation class
- trust prompts crossed or refused
- whether bypass/unblock/elevation was involved

### 3) Host-mutation snapshot

Show:

- artifacts added/removed
- shell surfaces requested
- service/helper surfaces touched
- whether the action widened or narrowed host integration scope

### 4) Proof and clearance snapshot

Show:

- shell activation proof class at issuance
- removal/clearance class at issuance
- known survivors
- pending restart/reboot/helper-release invalidators

### 5) Strong language block

Preserve both:

- strongest safe sentence
- blocked stronger sentence

Examples of blocked stronger sentences:

- `the package is fully trusted on this host`
- `Explorer/Finder integration is active everywhere`
- `clean uninstall removed all traces`
- `program gone means shared subject data is gone`

## Public object

### `host_integration_lineage_receipt`

Fields:

- `host_integration_lineage_receipt_id`
- `seat_ref`
- `runtime_ref`
- `decision_class`
- `operator_intent`
- `package_origin`
- `signer_reputation_class`
- `trust_prompts_crossed[]`
- `host_mutation_scope[]`
- `shell_surface_targets[]`
- `shell_activation_proof_class`
- `clearance_class_at_issuance`
- `known_survivor_classes[]`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `invalidators[]`
- `issued_at`

## Main surface

A compact receipt row should read like one of these:

- `accepted with warning · low-reputation signer bypassed · shell activation still below proof ceiling`
- `held · requested clean uninstall stronger than survivor evidence`
- `accepted · host mutation authorized · Explorer/Finder proof still pending restart`
- `blocked · package provenance weaker than requested trust sentence`

## Event language

Use phrases such as:

- `host-integration receipt issued`
- `trust prompt crossing recorded`
- `shell proof state preserved`
- `clearance ceiling recorded`
- `stronger sentence blocked`

Avoid phrases such as:

- `install complete`
- `extension good`
- `clean uninstall done`

## Design tests

The receipt fails if any of these remain true:

- later operators cannot tell whether the package merely launched or actually crossed OS trust/consent barriers
- shell proof state is lost and only install/removal success remains
- survivor classes are absent from the durable record
- the receipt forgets the blocked stronger sentence about trust or removal
