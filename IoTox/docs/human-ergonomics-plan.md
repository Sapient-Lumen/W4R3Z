# Human ergonomics plan

Status: second binary-native ergonomics gate implemented. Updated 2026-10-01.

IoTox already has many of the hard mechanisms that make a human product
possible: aliases, signed invitations, completion, sync doctor, config lint,
run-check, terminal profile templates, diagnostics export, storage readiness,
and the repository helper. The current revisions move the highest-value porch
commands into the product binary itself, so a normal operator can ask the
binary to teach, plan, preflight, and sequence without installing a second
control plane.

The guiding rule is:

```text
make the safe path short, but never make authority invisible
```

Every friendly command should either be read-only or print the exact underlying
`iotox` operations it will perform before it mutates anything. A porch may
teach, plan, preflight, and sequence. It must not silently create authority,
choose a remote path, enable sudo, certify a backup, or hide route/privacy
tradeoffs.

## What exists now

The useful human-facing pieces already in the tree are:

- `peer-alias-*` for owner-local names over Tox keys;
- `peer-invitation-*` for signed, inspectable, explicit friendship setup;
- `completion bash|zsh|fish` for command-name completion;
- `sync-doctor` and `sync-doctor-configured` for preflight and live headroom;
- `sync-create`, `sync-share`, `sync-status`, `sync-health`, `sync-repair`,
  `sync-conflicts`, `sync-history`, and restore-plan commands for daily sync;
- `terminal-shell-discover`, profile templates, profile lint/install/bind, and
  `terminal-sessions` for the SSH-like path;
- `host-capabilities`, `config-lint`, and `run-check` for deployment preflight;
- a short binary-native front door in `iotox help`, with the exhaustive
  inventory moved to `iotox help all`;
- binary/source provenance in `iotox doctor binary` and `iotox version
  --source`, so stale executable/source confusion is visible without reading
  build logs;
- binary-native topic help: `iotox help quickstart`, `iotox help sync`,
  `iotox help terminal`, `iotox help pairing`, `iotox help self`,
  `iotox help routes`, `iotox help evidence`, `iotox help shipping`,
  `iotox help support`, and `iotox help storage-readiness`;
- binary-native `iotox overview [--json]`, including the conservative
  `precious-data=blocked` product boundary;
- binary-native `iotox explain TOPIC` for table-driven failure guidance and
  stable next-step hints;
- binary-native `iotox readiness [sync|terminal|storage|routes|privacy] [--json]`;
- binary-native `iotox ship-check [sync|terminal|all] [stable|founder-preview] [--json]`
  for release-channel decisions;
- binary-native `iotox init plan` and `iotox init write-config` for canonical
  owner-private Agent config records;
- binary-native guided sync setup: `iotox sync plan-pair`, `iotox sync
  plan-mesh`, `iotox sync start`, and `iotox sync share`; and
- binary-native conflict guidance: `sync-conflicts-summary` and
  `sync-conflict-explain`;
- binary-native terminal setup planning: `iotox terminal doctor` and
  `iotox terminal profile plan shell|sudo|rescue`;
- binary-native pair-card porch over signed peer invitations;
- `diagnostics-export`/`diagnostics-inspect` plus binary-native
  `support-bundle plan|create|inspect` for content-free support bundles;
- person-multidevice porches, including recipe-first `iotox person quickstart`,
  for delivery cards, delegated send, transcript
  commit, receipt rollup, read-status, group status, background retry/expiry,
  Toxic bridge graduation, and person messenger graduation;
- resident-service porches for Agent/sync/Ratox and person worker systemd,
  NixOS, and MonsterNix-adapter review, including separate service-shape and
  service-reality receipts;
- `tools/iotox-repo.sh` for repository doctor/build/test/datacube/evidence and
  cleanup flows, plus release-plan/release-check command trails; and
- `tools/iotox-monsternix-adapter.sh` as an inert MonsterNix porch.

The command surface is still large enough that raw discoverability is itself a
problem. The native porch commands are the first answer: they do not replace
the flat stable commands, but they give humans small topic entrances and exact
next commands.

For the narrative product-discovery, red-team, and hope passes behind the next
ergonomic choices, see `docs/human-stories.md`. That document tells likely
operator stories first, doubts the repo's own feature instincts, imagines IoTox
at the edges of its best future, then extracts the smallest features that
reduce mistakes without hiding authority, backup, sudo, route, or
support-bundle boundaries.

## Highest-value ergonomic additions

### 1. Topic help and recipes

Implemented topic-scoped help without changing semantics:

```text
iotox help sync
iotox help terminal
iotox help pairing
iotox help self
iotox help storage-readiness
```

Each topic should include:

- the three to seven commands a human should try first;
- one safe dry-run or doctor command;
- one exact mutation example;
- the relevant nonclaim; and
- the document that owns the full detail.

The binary owns the canonical short topics. Future public scripts may still own
long-form host-specific recipes, but the first help entrypoint is native.

### 2. One command that answers “what is this Agent ready for?”

The current data exists in `status`, `sync-status`, `sync-health`,
`host-capabilities`, `run-check`, `diagnostics-export`, and
`storage-readiness`; this revision adds the compact front page:

```text
iotox overview
iotox overview --json
iotox ship-check all stable
```

The human view is content-free and compact. Offline Agents are reported without
failing:

```text
iotox-overview-v1
agent=offline
sync=offline jobs=0
terminal=offline sessions=0 live=0
storage-readiness=not-assessed
precious-data=blocked
```

This is not attestation. It is a local operator dashboard that joins existing
truth without leaking names, paths, messages, keys, or endpoints.

`ship-check` is stricter than readiness. Stable/no-concern mode fails closed
without a complete evidence manifest while sync precious-data and Ratox
fleet/daily-driver claims remain blocked; founder-preview mode can pass only
with explicit nonclaims.

### 3. Guided first-run porch

Implemented a binary-native, non-authoritative first-run path:

```text
iotox init plan --root PATH [--mode self] [--enable-sync] [--enable-terminal]
iotox init write-config --root PATH [--mode self] [--enable-sync] [--enable-terminal]
iotox config-lint PATH/agent.conf
iotox run-check --config PATH/agent.conf
iotox run --config PATH/agent.conf
```

`plan` prints the exact state files, directories, canonical config record, and
the underlying `iotox run ...` command. `write-config` creates owner-private
directories and a no-clobber `0600` canonical config file with the shared
AgentConfig encoder, then stable-read verifies it. It does not bootstrap
RecallRoot, grant authority, install a service, or enable sync/sudo by
surprise. Manual mode still requires explicit `--enable-terminal`; `--mode
self` is the deliberate product mode that selects Ratox host/controller by
default while leaving profiles, bindings, `interactive.terminal`, and sudo as
separate owner decisions.

This is the friendly replacement for making a new operator assemble
`--state`, `--identity`, `--authority-ledger`, `--command-store`, runtime,
diagnostics, aliases, route, sync-policy, and Ratox profile-store paths from
memory.

### 4. Pairing cards and reviewable setup bundles

Peer invitations are good, but humans still need a clearer “card”:

```text
iotox pair-card create OUTPUT --alias NAME --capabilities LIST --expires 1d
iotox pair-card inspect PATH
iotox pair-card accept PATH EXPECTED_STABLE_PRINCIPAL [--alias NAME]
```

Implemented as a native grouped porch over `peer-invitation-*`:

```text
iotox pair-card create OUTPUT [--expires SECONDS] [--alias NAME] [--capabilities LIST]
iotox pair-card inspect PATH [EXPECTED_STABLE_PRINCIPAL]
iotox pair-card accept PATH EXPECTED_STABLE_PRINCIPAL [--alias NAME|-]
```

The current card prints the underlying command and always preserves:

```text
authority-granted=0
```

Do not combine friendship acceptance and authority grant into one hidden
gesture. The ergonomic win is review and memory, not collapsing the security
boundary. A later fingerprint pass may add word fingerprints for out-of-band
comparison, but the first gate deliberately changes no artifact format.

### 5. Sync setup plans

The daily sync commands work, but read-write setup is a ceremony. This revision adds
native grouped setup commands that generate the exact sequence:

```text
iotox sync plan-pair NAMESPACE LOCAL_PATH FRIEND REMOTE_PATH read-write 30
iotox sync start NAMESPACE PATH read-write 30
cat RECALLROOT.txt | iotox sync share NAMESPACE FRIEND read-write
iotox sync plan-mesh NAMESPACE LOCAL_PATH FRIEND=REMOTE_PATH FRIEND=REMOTE_PATH 30
iotox sync graduation-check PATH read-write 30 --evidence NAME=LABEL ...
```

`plan-pair` runs `sync-doctor`, states whether the path is representable, shows
the local `sync-create`, shows the local `sync-share`, shows the reciprocal
remote `sync-create`, and keeps the remote path explicit. `plan-mesh` makes the
directional grants for multi-writer nodes visually obvious. `sync start` runs
the same doctor check before dispatching the existing `sync-create` mutation.
`sync graduation-check` is the fail-closed working-copy review target: it joins
local preflight, storage-readiness, versioned recovery custody, restore
drill, and recovery-runbook labels while still refusing
`precious-data-readiness`.

The grouped commands may use aliases and current friendship when a mutation
requires them. They must not choose a remote path or create remote policy.

### 6. Conflict and recovery guidance

Conflict semantics are correct but need a smaller human entrance. The current
binary adds guided reads:

```text
iotox sync-conflicts-summary NAMESPACE [RECORD_HEX]
iotox sync-conflict-explain NAMESPACE PATH [RECORD_HEX]
```

The first two commands now call the existing tree-v2 conflict operation when an
Agent is reachable and otherwise still print useful nonmutating guidance. The
output explains:

- which ordinary path is projected;
- how many alternatives exist;
- which writer generations produced them;
- which command shows the exact signed history; and
- how to resolve by making a normal edit after all branches are visible.

The recovery/readiness shortcut now exists in two layers:
`sync-dataset-readiness` runs or renders the restore drill, and
`sync graduation-check` records the content-free labels needed before a working
copy can be operator-attested. Both still refuse to call sync a backup or sole
system of record.

### 7. SSH-like terminal setup porch

The terminal machinery has the right safety posture; this revision adds the native
planning porch:

```text
iotox terminal doctor
iotox terminal profile plan shell owner-shell $USER
iotox terminal profile plan sudo owner-admin $USER
iotox terminal profile plan rescue owner-rescue $USER --shell /bin/sh --toolbox-dir /opt/iotox-toolbox
iotox terminal graduation-check --root PATH --peer PEER --evidence NAME=LABEL ...
```

The porch composes existing commands by printing exact commands:

- `host-capabilities`;
- `terminal-shell-discover`;
- `terminal-profile-shell-template`;
- `terminal-profile-toolbox-template`;
- `terminal-profile-lint`;
- `terminal-profile-install`;
- `terminal-profile-bind`; and
- `terminal-sessions`.

The sudo profile must remain separately named and explicitly requested. The
friendly flow should say “this enables the machine's existing sudo policy
inside the approved shell,” not “IoTox grants root.”

`terminal graduation-check` is the stricter daily-driver review target. It
aggregates daily control, stale profile checks, service supervision, reconnect
continuity, cgroup delegation, direct route loss, long soak, Tor/I2P route
evidence, sudo policy, security review, and the owner activation decision while
still reporting `repo-certified=0`.

### 8. Actionable errors and `explain`

Many IoTox failures are intentionally strict. Humans need the next step.
Implemented:

```text
iotox explain TOPIC
iotox explain last
```

Good errors should name the failing class and one safe next command:

```text
sync-create refused: source contains a symlink
why: symlinks are not represented by owner-mode-v2
next: run `iotox sync-doctor PATH read-write ...`
doc: docs/sync-doctor.md
```

The table now includes the same porch topics humans see in `iotox help`
(`quickstart`, `sync`, `terminal`, `pairing`, `service`, `self`, `person`,
`routes`, `evidence`, `shipping`, `support`, and `storage-readiness`) plus
specific refusal classes such as agent-offline, backup-independence,
conflict-resolution, friendship-not-authority, invalid namespace, missing
libsodium, pair-card authority, permission denial, forbidden route fallback,
precious-data readiness, unsupported sync source semantics, and terminal sudo.
Local control response errors now append a stable `hint-command=iotox explain
TOPIC` when the text matches a known class. It does not persist arbitrary stderr
for `explain last`; that remains explicit rather than inventing a hidden local
log.

### 9. Output modes

Keep the current line-oriented output, but make display intent explicit:

```text
--human       default, stable enough for people
--json        canonical structured output for scripts
--quiet       print only the primary token/path
--explain     append next-step hints
```

Do this gradually on high-use commands first: `status`, `peers`,
`sync-status`, `sync-health`, `sync-doctor`, `terminal-sessions`,
`host-capabilities`, `run-check`, and readiness/reporting tools.

### 10. Readiness badges for honest product use

Implemented a blunt “what may I reasonably use this for?” surface without
making users read every ADR:

```text
iotox readiness
iotox readiness sync
iotox readiness terminal
iotox readiness storage
iotox readiness routes
iotox readiness storage --json
```

Example categories:

```text
sync-working-copy=usable
sync-precious-data=blocked
terminal-daily-control=construction
storage-local-science=accepted
storage-media-certification=not-an-iotox-goal
backup-independence=blocked
routes-native=accepted
routes-tor=bounded
routes-i2p=bounded
```

The first gate is binary-native and intentionally underclaims from static
product facts plus a small live Agent check when available. The heavier
repository storage-readiness science remains in `tools/iotox-repo.sh
storage-readiness`. For a specific sync dataset or Ratox host, use
`sync graduation-check` and `terminal graduation-check` respectively; those
commands are operator-attestation porches, not hidden certification engines.
For a release decision, use `ship-check`; it is intentionally stricter than
readiness. For a founder-preview release candidate, use
`tools/iotox-repo.sh release-plan founder-preview` followed by
`tools/iotox-repo.sh release-check founder-preview --iotox /path/to/iotox` so
the binary product gate and repository packaging trail remain in sync.
For a stable candidate, add `tools/iotox-repo.sh stable-evidence-plan` and pass
the completed manifest to both `iotox ship-check all stable --evidence-manifest
PATH` and `tools/iotox-repo.sh release-check stable --evidence-manifest PATH`.
Long soaks are explicit stable evidence: sync needs a `sync.long-soak` receipt,
and Ratox operators should use `iotox terminal soak-plan`, retain a
`terminal soak-receipt`, and run `iotox terminal soak-verify` before placing it
under `terminal.long-soak` in the manifest.

## Secondary ergonomic tracks

### Documentation and packaging

- Add a true `docs/quickstart.md` with three recipes: pair two nodes, create a
  read-write sync, and create an SSH-like terminal profile. Implemented, with
  binary-native `iotox help quickstart`.
- Generate man pages from the command registry and topic help.
- Keep a one-page “if you are replacing Resilio Sync” guide that states what is
  ready, what is not backup-grade, and how to run a recovery drill.
  Implemented as `docs/replace-resilio-sync.md`.
- Keep `docs/edge-of-hope.md` and `docs/pragmatic-guardrails.md` paired: the
  first names the ideal, the second prevents the ideal from becoming a false
  readiness claim.
- Keep `docs/human-stories.md` current as the story-first filter for features:
  no feature should be added merely because it is possible if it makes a common
  human mistake easier.
- Make datacube exports include the quickstart and ergonomics plan near the top
  of the manifest.

### Names, fingerprints, and memory

- Show stable principals and Tox keys with optional word fingerprints.
- Let aliases carry private notes/tags in an owner-local signed store only if
  diagnostics never export them.
- Add `peer-fingerprint PEER` for out-of-band comparison during setup.

### Watch and notification surfaces

- `sync-watch NAMESPACE` now exists as a compact redaction-safe watch that
  composes live Agent status with the local operator freeze record.
- Next watch work: add `terminal-watch` and `route-watch`, then enrich sync
  progress lines so they distinguish transfer, CAS verification, projection,
  repair, and conflict preservation when the Agent exposes those phases.

### Host integration

- Make self-machine setup the default Ratox story: `--mode self` turns on the
  host/controller roles, and the profile/binding/authority steps decide what
  the owner can actually reach.
- Keep self-swarm setup native in the binary: `iotox self-swarm help`,
  `create-recall-stdin`, `join-recall-stdin`, `inspect`, `verify`,
  `grant-plan`, `grant-recall-stdin`, `retire-plan`, `retire-recall-stdin`,
  `revoke-retired-recall-stdin`, `floor-commit`, `floor-status`,
  `fanout-plan`, and `fanout` are the current reviewed path. ADR 0384's
  high-water floor and optional live route proof keep this native rather than
  shell-wrapper shaped. The next ergonomic lift is clearer summary output and
  redacted overview/support-bundle status.
- Add NixOS module examples and systemd user/service examples that call
  `run-check` before `run`. Implemented as `docs/deploy-nixos.md` and
  `docs/deploy-systemd.md`; these are examples, not a package manager.
- Keep MonsterNix admission read-only until it can preserve exact source,
  package, and proof receipts.
- Provide explicit “service disabled until config-lint and run-check pass”
  examples.

### Support and reporting

- Add `iotox support-bundle plan` as a wrapper around diagnostics export,
  readiness, overview, and host-capability summaries. Implemented.
- Require an inspect step before the bundle is shared. Implemented.
- Include “what this bundle does not prove” in the output. Implemented:
  support bundles are not remote attestation and not backup proof.

## Do not add

These would feel ergonomic but violate IoTox's product law:

- auto-granting authority when accepting a friendship invitation;
- remote-selected sync destination paths;
- remote-selected shell command, argv, profile, sudo bit, or port forward;
- implicit sync-as-backup language;
- automatic `sudo` profile creation during ordinary terminal setup;
- hidden route fallback from Tor/I2P to native;
- dynamic completion that queries or leaks private live state by default;
- generated configs that include RecallRoot phrases, private keys, or hidden
  environment requirements; and
- destructive cleanup without dry-run and exact reviewed targets.

## Suggested implementation order

1. [x] Add binary-native topic help/quickstart recipes.
2. [x] Add binary-native `overview`/readiness summaries from existing
   content-free state.
3. [x] Add binary-native guided sync setup for pair and three-node mesh
   ceremonies.
4. [x] Add binary-native terminal setup porch for shell, sudo, and rescue
   profiles.
5. [x] Add conflict explainers.
6. [x] Add binary-native readiness badges.
7. [x] Add pair-card porch.
8. [x] Add support-bundle and host-service examples.
9. [x] Split short root help from exhaustive `help all`, add person quickstart,
   and add binary/source provenance diagnostics.
10. [x] Add native help topics for routes, evidence, shipping, and support so
    product claims have a humane binary-native entrance.
11. Add structured output modes to more high-use commands.
12. Consider richer dynamic completion only where it remains local and
   authority-safe.

Items 1--10 are implemented. For the current post-implementation priority
filter, use the red-team candidate list in `docs/human-stories.md`: first
contact, short quickstart/Resilio guidance, phase-aware sync watch, emergency
sync pause/freeze, terminal stale-profile/rescue readiness, then fingerprints,
recovery planning, and mesh retirement.
