# Offline verification drill checklist

Synthetic-only checklist. This is not live election evidence, not certification, and not legal advice.

Use this checklist when a maintainer or outside reviewer needs to rehearse the release without network access.

- [ ] Verify the carrier ZIP with `scripts/verify_release_zip.py`.
- [ ] Extract with `scripts/extract_release_zip.py` into a new concrete output directory.
- [ ] Verify the extracted tree with `scripts/verify_manifest.py`.
- [ ] Run `tools/example_county_output_pack.py --json` and preserve the output.
- [ ] Run `tools/example_county_negative_control_runner.py --json` and confirm temporary tamper fixtures fail closed.
- [ ] Run `tools/release_go_no_go_pack.py --json` and confirm the decision is GO for synthetic release only.
- [ ] Preserve the command transcript, operator, timestamp, host context, and release ZIP SHA-256.
- [ ] Do not describe a successful drill as certification, live deployment evidence, outcome proof, or legal advice.
