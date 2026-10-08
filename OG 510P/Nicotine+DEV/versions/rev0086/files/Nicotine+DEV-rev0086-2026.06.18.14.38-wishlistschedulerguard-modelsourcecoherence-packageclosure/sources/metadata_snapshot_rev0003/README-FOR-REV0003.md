# Nicotine+ upstream source bundle for rev0003

Please upload this whole archive to ChatGPT. For rev0003, it should be unpacked under:

`sources/upstream-current-and-future/`

Expected source lanes:

- `source-trees/github-tag-3.3.10/` — current stable tag baseline.
- `source-trees/github-branch-3.3.x/` — supported 3.3.x / 3.3.11 release-candidate lane.
- `source-trees/github-branch-master/` — future 3.4.0.dev1/default development lane.
- `pypi/` — PyPI 3.3.10 sdist/wheel provenance, if pip download succeeded.
- `metadata/` — ls-remote, branch/tag, release, milestone, issue, and PR snapshots.
- `SHA256SUMS` — content verification.

Do not edit these directories after fetching; create a new bundle if you need a fresher snapshot.
