# Release stage pack

`vhk gen-release-stage-pack <project_dir>` turns release-deploy lanes into project-local staged payload trees.

It exists for the moment when a maintainer no longer wants only planning prose and now needs a concrete ship folder per target desktop lane.

The command writes:

- `docs/VHK_RELEASE_STAGE.md`
- `docs/VHK_RELEASE_STAGE_MATRIX.md`
- `docs/VHK_RELEASE_STAGE_PLAN.json`
- `scripts/vhk_refresh_release_stage.sh`
- `build/release-stage/<profile_id>/README.md`
- `build/release-stage/<profile_id>/install.sh`
- `build/release-stage/<profile_id>/verify.sh`
- `build/release-stage/<profile_id>/assemble_payload.sh`
- `build/release-stage/<profile_id>/vhk_release_stage.json`
- `build/release-stage/<profile_id>/payload/`

The lane stage tree keeps two truths visible:

1. what should be installed/verified on the host
2. which files/exports should be assembled into a payload for that lane

Follow-through:

- `vhk bundle-stage <project_dir> <out.zip> --target-profile <profile_id>` can now
  zip that lane root directly, so the reviewed stage tree is also the shareable
  handoff artifact
- `vhk inspect-bundle` will report embedded release-stage metadata for those
  lane bundles, which keeps the lane identity visible even before unpacking

This is intentionally project-local and conservative. It does not pretend that VHK can already emit perfect distro packages for every desktop family; it materializes a reviewable release tree first.
