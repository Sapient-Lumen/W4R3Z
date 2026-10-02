# Script distribution and Monsternix adapter plan

Status: accepted product direction, not a second authority root.

IoTox remains one product executable. Bash and Nix should own the human-facing
entry path around that executable because they are inspectable, portable across
the target Linux systems we care about first, and already fit the repository's
evidence style. The script layer is allowed to guide, build, test, package,
clean, and start IoTox. It is not allowed to grant device authority, invent a
second sync signer, weaken profile policy, or silently install host services.

## What we are taking from Sandworm and MonsterNix

The local Sandworm copies show the right public shape: one readable file, a
strong Unicode top section, noob-first commands, explicit posture choices, and
warnings close to the command that can bite the operator.

MonsterNix shows the right host-integration shape:

- source/package admission is exact and receipt-backed;
- read-only `doctor`/`status`/`plan` commands come before mutation;
- mutation is explicit and usually has an `--execute`-style boundary;
- machine-specific paths, users, devices, services, and credentials belong to
  the machine adapter, not to the portable project;
- evidence is content-free unless the operator deliberately opens private
  content;
- experimental objects are discoverable but inert by presence.

IoTox should reuse those lessons without importing MonsterNix's authority model
into the device protocol.

## Script for everyone

The public script should be a repository and operator companion. The broader
future command tree should look like this once the guided mutating surfaces are
accepted:

```text
./iotox doctor
./iotox doctor --json
./iotox build
./iotox test quick
./iotox test full
./iotox test sandwurm-smoke
./iotox run --config PATH
./iotox run --state-root PATH --runtime-root PATH --network native
./iotox sync doctor PATH [one-writer|read-write] [INTERVAL_SECONDS]
./iotox sync start NAME PATH [one-writer|read-write] [INTERVAL_SECONDS]
./iotox sync share NAME FRIEND read-only|read-write
./iotox sync follow FRIEND NAME pull|verified
./iotox sync recovery-drill BACKUP_ROOT RESTORED_ROOT
./iotox terminal doctor
./iotox terminal profile create shell NAME
./iotox terminal profile create sudo NAME
./iotox terminal profile create rescue NAME
./iotox witness custody-drill SERVICE_ROOT CHECKPOINT SERVICE_PUBLIC_KEY_HEX
./iotox stable-evidence-plan
./iotox release plan founder-preview
./iotox release check founder-preview
./iotox datacube [OUTPUT_DIRECTORY]
./iotox clean
./iotox clean --apply
```

Default behavior:

- no mutation for `doctor`, `status`, `plan`, `help`, or `clean` without
  `--apply`;
- no implicit use of `$HOME` as an authority root;
- no secret in argv, environment, logs, datacubes, or evidence bundles;
- no remote-selected shell, argv, sync path, or sudo bit;
- route selection is explicit;
- every mutating command prints the underlying `iotox` command it will execute.

The first committed version is intentionally small:
`tools/iotox-repo.sh` implements `doctor`, `build`, `test quick`, `test full`,
`sync-recovery-drill`, `sync-loopback-custody-drill`,
`sync-dishonest-storage-drill`, `sync-dishonest-storage-matrix`,
`sync-log-writes-prefix-replay`, `sync-production-prefix-replay`,
`storage-readiness`, `witness-custody`,
`stable-evidence-plan`, `release-plan`, `release-check`, `datacube`, and
`clean` by launching existing repository tools and native product gates. It
does not yet wrap live sync namespace creation, terminal, service-manager, or
sudo setup. `sync-recovery-drill`, `sync-loopback-custody-drill`, the
dishonest-storage helpers, `storage-readiness`, and `witness-custody` are
evidence retention/status around already selected artifacts, local
prerequisites, or bounded storage-fault science, not backup certification,
witness deployment, storage-media certification, or independence claims. The
release helpers are similar: `stable-evidence-plan` prints the stable dossier
requirements, `current-stable-evidence` prints the accepted local manifest
pointer and digest, `release-plan` prints the command trail, and `release-check`
enforces clean-tree, syntax, and `iotox ship-check` channel semantics without
turning founder-preview into stable. The helper should not wrap every advanced
option. Its job is to make the correct ordinary path hard to miss.

The broader ergonomic queue is tracked in `human-ergonomics-plan.md`. Its first
script-level candidates are topic help/recipes, guided first-run config,
pairing cards, sync setup plans, terminal setup porches, readiness summaries,
and support-bundle review. Each must retain the rule above: print the exact
underlying `iotox` command and keep authority, sudo, routes, backup claims, and
remote paths explicit.

## Script for Monsternix

The Monsternix adapter should be a porch, not a fork. It should admit exact IoTox
source/package/proof objects into the MonsterNix object world and then let
MonsterNix perform its own host-specific projection, test, and switch ceremony.
The first committed IoTox-side script, `tools/iotox-monsternix-adapter.sh`, is
read-only. It runs `doctor` and `plan` so the boundary is visible before any
MonsterNix-side writer exists.

Expected shape:

```text
mnx iotox doctor
mnx iotox admit-source PATH
mnx iotox admit-package PATH
mnx iotox plan --device NAME
mnx iotox proof quick
mnx iotox proof sandwurm-smoke
mnx iotox project-service --device NAME
mnx iotox apply --device NAME --execute
mnx iotox datacube
```

The adapter may know about MonsterNix concepts such as candidates,
machine-specific service projections, proof receipts, and accepted switch gates.
It must not own IoTox's RecallRoot, device identity, signed authority ledger,
sync namespace policy, terminal profile contents, or route secrets.

## Boundaries to preserve

```text
IoTox binary
    owns protocol behavior, device identity, authority, sync, routes, terminal policy

public script
    owns human guidance, build/test orchestration, safe cleanup, datacube export

Monsternix adapter
    owns source/package admission, host projection, service-manager wiring, receipts

operator
    owns RecallRoot custody, recovery-custody evidence, sudo policy, deployment acceptance
```

If these boundaries blur, the scripts become dangerous. A friendly wrapper that
silently chooses state roots, service identities, network routes, sudo profiles,
or backup custody would be worse than no wrapper.

## Implementation order

1. Publish `docs/product-page.md` as the human top section.
2. Keep `tools/iotox-repo.sh` small and verify it as the public repository
   companion.
3. Promote `tools/iotox-monsternix-adapter.sh` only after MonsterNix accepts a
   concrete object/admission command contract.
4. Add guided sync commands after their printed underlying `iotox` commands match
   the current CLI exactly.
5. Add guided terminal profile commands after the shell/sudo/rescue profile docs
   and command registry agree.
6. Add completion for the script only from a closed descriptor registry or a
   static declared tree. Do not guess dynamic arguments.

The acceptance gate for each script feature is simple: dry-run truth, exact
printed underlying command, content-free evidence, and no hidden authority
creation.
