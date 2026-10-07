# Latest decision

_Generated from `release_queue/LATEST_DECISION.json`. Do not edit by hand; rerun `python3 -B publishing/render_queue_surfaces.py --root .` or `make rebuild-surfaces`._

Latest decision note:

- `release_queue/decisions/2026.06.18-1154-obschannel-counterexamples-modelbinding-validatorcut-no-publication.md`

Machine-readable companions:

- `release_queue/LATEST_DECISION.json`
- `release_queue/DECISION_INDEX.md`
- `release_queue/DECISION_INDEX.json`

Summary:

- Heading: Observation-channel counterexamples, model binding, and validator cut — no publication
- Date: 2026.06.18
- Time hint: 1154
- Kind: archive/control-surface pass
- Publication action: none
- Action class: structure_or_no_publication
- Summary: Rev0900 (`Anonymity-rev0900-2026.06.18.11.54-obschannel-counterexamples-modelbinding-validatorcut.zip`) repairs a release-adjacent inference that treated a scalar observation probability as an independent erasure channel. Equal per-secret reveal rates do not determine the conditional output law: an explicit three-secret cyclic-reveal mechanism has reveal probability one half for every secret, yet leaks one full bit and permits exact recovery with probability two thirds. The scalar-erasure calculation reports only 0.321928094887 bits and exact recovery 5/12, so it is not a certificate for that mechanism.
