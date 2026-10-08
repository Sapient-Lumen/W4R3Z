# Release manifest

The packaged GlassTTY zip now embeds a root-level `RELEASE-MANIFEST.json`.

## Purpose

The release manifest makes the handoff archive self-describing instead of forcing a recipient to infer what the zip contains by inspection alone.

## Current contract

The embedded manifest records:

- archive name / root
- revision and packaging timestamp when available
- file count
- per-file path, size, and SHA-256 digest

## Working rule

`RELEASE-MANIFEST.json` inside the produced zip is the review surface that matters. Any extracted working-tree copy is residue and should be overwritten on the next package build.

## Package posture

`bash scripts/package-release.sh <repo> <archive.zip>` now regenerates the embedded release manifest for the staged tree and runs `python scripts/verify-package.py <archive.zip>` on the produced bundle. Set `GLASSTTY_PACKAGE_STRICT_VERIFY=1` when you want package generation itself to fail on verification drift.
