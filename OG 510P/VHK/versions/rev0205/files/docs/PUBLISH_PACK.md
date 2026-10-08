# Publish pack

`vhk gen-publish-pack <project_dir>` turns VHK's internal planning + claim audit
surfaces into a public-facing release/support note for real projects.

Artifacts:

- `docs/VHK_PUBLIC_SUPPORT.md`
- `docs/VHK_INSTALL_QUICKSTART.md`
- `docs/VHK_PUBLISH_PLAN.json`
- `scripts/vhk_refresh_publish_pack.sh`
- `build/publish/<bundle-name>/README.md`
- `build/publish/<bundle-name>/vhk_publish_handoff.json`
- `build/publish/<bundle-name>/refresh_publish_inputs.sh`
- `build/publish/<bundle-name>/bundle_release.sh`

## Why this exists

VHK already knew how to:

- plan Linux-native surfaces
- generate operator/release/support/portability packs
- turn support claims into an auditable target matrix
- embed claim snapshots into bundle manifests

But a bundle recipient or README reader still had to infer the public support
story from internal docs.

The publish pack closes that gap by generating:

- a public support note that can travel with release notes or bundles
- a short install quickstart for recipients/operators
- machine-readable publish metadata for future websites/catalogs
- a refresh script that regenerates the surrounding packs, bundles the project,
  and records `vhk inspect-bundle` output
- a reviewable publish handoff tree under `build/publish/<bundle-name>/` that
  keeps copied support/install docs, bundle commands, and stage references
  together
- an optional stage-bundle handoff when `--bundle-target-profile <profile>` is
  used, so public release/install docs can point at one reviewed release lane
  instead of always re-zipping the whole repo

## Design intent

This is not a fake “universal Linux support” badge generator.

It is intentionally explicit about:

- which desktop/session lanes are reference/supported/caveated/experimental
- what proof artifacts stronger claims depend on
- what deployment boundaries still matter (remappers, portals, services,
  helper daemons, WM integrations)
- what public language should stay caveated so README/release prose does not
  overclaim beyond the audited matrix

## Artifact shape

The publish JSON plan is expected to preserve the existing planner structure and
add:

- `public_support_matrix`
- `recommended_rollout`
- `language_guardrails`
- `publish_headline`
- `publish_summary`
- `publish_paths`
- `publish_commands`
- `bundle_release_story`
- `publish_handoff`
- `publish_artifacts`

The markdown artifacts are expected to be audience-facing:

- `VHK_PUBLIC_SUPPORT.md` is for bundle recipients, README snippets, release
  notes, and support pages
- `VHK_INSTALL_QUICKSTART.md` is the short install/review handoff for operators
  or users trying a shared bundle
- `build/publish/<bundle-name>/README.md` is the ship/review handoff for the
  maintainer who is about to regenerate, inspect, and distribute the chosen
  bundle

## Relationship to bundle metadata

If the publish docs are present when `vhk bundle` runs, the embedded
`bundle_support_metadata` snapshot now records whether those public docs are
present in the archive.

That lets `vhk inspect-bundle` tell a recipient not only what the project
claims, but also whether the bundle actually carries the public support/install
artifacts that explain those claims.

## Stage-bundle aware publish flow

When `vhk gen-publish-pack <project_dir> --bundle-target-profile <profile_id>` is used:

- `VHK_PUBLISH_PLAN.json` records `bundle_release_story.bundle_kind = release-stage`
- publish commands switch from `vhk bundle` to `vhk bundle-stage`
- the generated refresh script regenerates that target stage lane first via
  `vhk gen-release-stage-pack --target-profile <profile_id>`
- the public support/install docs name the chosen stage profile explicitly

This keeps the public support story attached to the same reviewed stage payload
that a maintainer is actually about to hand to someone.

## Publish handoff tree

The publish pack now also materializes a reviewable handoff tree under
`build/publish/<bundle-name>/`. It is intentionally small and explicit:

- `payload/docs/` copies the current public support/install docs plus the
  machine-readable publish plan
- `refresh_publish_inputs.sh` reruns `vhk gen-publish-pack` from the project
  root so the copied docs can be refreshed in one command
- `bundle_release.sh` runs the prebundle commands, creates the deterministic
  bundle, and records inspect output under `dist/`
- when `--bundle-target-profile <profile>` is used, `payload/release-stage/`
  also carries the chosen lane's `README.md` and `vhk_release_stage.json` so the
  publish handoff still points at one reviewed stage story instead of a vague
  repo-wide bundle

## Relationship to distribution pack

`vhk gen-distribution-pack` now builds directly on top of the publish handoff.
It reuses the same `bundle_release.sh`, copied support docs, bundle name, and
optional release-stage target profile, then materializes AppImage/Flatpak
skeletons under `build/publish/<bundle-name>/distribution/`.

That keeps packaging metadata downstream of the reviewed publish story instead
of letting package manifests drift away from what the maintainer actually chose
to ship.
