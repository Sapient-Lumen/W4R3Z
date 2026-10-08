# Launch world preview page — state-root selection, config authority, and implicit world creation

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
- world creation and world reopening share the same unqualified wording
