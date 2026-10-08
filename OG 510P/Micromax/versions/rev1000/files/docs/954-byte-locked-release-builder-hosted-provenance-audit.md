# Byte-locked release builder and hosted provenance audit (rev0996)

## Why this became the second priority

Rev0995 could reproduce two wheels and a revision archive from one captured source,
but the publication lane still began by trusting whatever `pip`, `setuptools`, and
`pytest` happened to be installed. Version labels were recorded after the fact;
the bytes that supplied those programs were neither locked nor independently
verified. The local receipt was useful evidence, but it was unsigned and a hosted
runner discarded the produced files when the job ended.

That combination was a finish-line risk: a release could be internally
reproducible while the builder inputs remained mutable, and a configured
attestation could outlive neither an executed workflow nor its subjects. Rev0996
therefore finishes a narrow release lane rather than adding a general dependency
manager or release registry.

## Landing

### One exact source lock

`release/requirements-builder.txt` declares exactly seven projects with exact
versions and SHA-256 hashes:

- Python bootstrap policy: Python 3.13.14;
- `pip` 26.1.2 and `setuptools` 83.0.0;
- `pytest` 9.0.3 with `iniconfig` 2.3.0, `packaging` 25.0, `pluggy` 1.6.0, and
  `pygments` 2.20.0.

`tools/mxrelease.py` parses only the repository's deliberately narrow grammar:
`project==version` followed by one or more local SHA-256 hashes. URLs, markers,
extras, VCS/editable rows, options, duplicate projects, duplicate hashes, missing
hashes, extra lock files, undeclared runtime dependencies, and disagreement
between the lock and release policy fail closed. The lock, builder, release
workflow, and package-policy files are source-digested inputs to the receipt.

### Acquire bytes; do not grant authority to the downloader

`tools/mxbuilder.py` permits the ambient interpreter to run one acquisition
command: `pip download --require-hashes --only-binary=:all: --no-deps`. The
resulting directory is not trusted merely because pip accepted it. Micromax then
reopens every wheel from a stable regular inode and independently checks:

- no symlink or non-wheel extras;
- bounded file size, member count, member size, and total expanded size;
- safe raw POSIX member paths before normalization;
- no duplicate case-folded aliases, encryption, unsupported compression, or
  non-regular file entries;
- exactly one top-level `METADATA` file under its own byte ceiling;
- exact normalized project and exact version; and
- a SHA-256 digest authorized by the checked-in lock.

The complete wheel set must contain one and only one authorized wheel per locked
project. These bounds constrain corrupt/substituted archives; they do not turn
third-party package code into untrusted sandboxed code. The exact hashes are the
reviewed authority.

### Bootstrap without trusting an older installer

The builder creates a virtual environment with no pip. It safely extracts the
already verified pip wheel into that environment, using exclusive file creation
and the same member/resource checks. It then installs the other verified wheels
with package-index resolution disabled:

```text
pip install --no-index --find-links <verified-wheelhouse> \
  --require-hashes --only-binary=:all: --no-deps
```

On POSIX, the private wheelhouse is made read-only while installer code consumes
it. Every wheel is reopened and rehashed afterward, and the exact installed
project/version set must equal the lock. A same-UID hostile process can still
change permissions or interfere with the process; that is outside this
application-level builder boundary.

### Bind the release child to the observed bytes

The builder writes a self-digested receipt containing:

- the exact source lock descriptor;
- Python implementation/version;
- each wheel filename, size, project, version, and SHA-256;
- the exact installed versions;
- the acquisition/install/bootstrap boundary; and
- the verifier's resource ceilings and before/after identity result.

The release child receives the receipt path and digest in a sanitized environment.
`tools/mxrepro.py` validates the self digest, launch digest, source lock, wheel
set, installed set, network-boundary vocabulary, and verifier ceilings before it
accepts the builder as release evidence. It embeds the validated receipt snapshot
in the release run and sealed release receipt.

This binding detects ordinary replacement and accidental drift. It is not a
secret capability against same-UID process compromise and is not an operating-
system network sandbox.

### Least-authority hosted workflow

`.github/workflows/reproducible-release.yml` has two jobs:

- pull requests and ordinary non-tag pushes run the reproducible lane with only
  `contents: read`;
- manual dispatch and tag pushes run the same lane with the additional
  `id-token: write`, `attestations: write`, and `artifact-metadata: write`
  permissions needed for hosted provenance.

The privileged job attests the published reproducible wheel, release receipt,
run receipt, and exact revision ZIP, then uploads those same explicit files as a
30-day workflow artifact. Because the output directory begins with `.`, the
upload step opts into hidden files explicitly and fails if any subject is absent.
It does not upload the whole hidden directory.

All first-party actions are pinned to full commits and annotated with the reviewed
release:

- `actions/checkout` v7.0.1 —
  `3d3c42e5aac5ba805825da76410c181273ba90b1`;
- `actions/setup-python` v7.0.0 —
  `5fda3b95a4ea91299a34e894583c3862153e4b97`;
- `actions/attest` v4.2.0 —
  `f7c74d28b9d84cb8768d0b8ca14a4bac6ef463e6`; and
- `actions/upload-artifact` v7.0.1 —
  `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a`.

Checkout credentials are not persisted. An attestation is useful only when a
consumer verifies its signature, subject digest, repository, workflow, ref, and
source commit; merely configuring or generating one is not equivalent to that
consumer verification.

## Audit/refactor findings corrected

1. **Mutable builder authority.** The old lane proved installed version strings,
   not acquisition bytes. The new lane makes exact authorized wheel bytes the
   root of package-builder authority.
2. **Bootstrap recursion.** Installing the locked installer with an ambient older
   installer would leave a circular trust gap. The verified pip wheel is instead
   extracted through a small bounded reader before any package installation.
3. **Stale policy duplication.** `tools/mxaudit.py` previously inferred package
   policy from duplicated strings. It now consumes the executable
   `mxrelease.package_input_report()` and checks the concrete builder/hosted
   workflow surfaces.
4. **Privilege spread.** A single workflow job would grant OIDC/attestation
   authority to pull-request code. Verification and attestation are now separate
   jobs with distinct event predicates and permissions.
5. **Unretained subjects.** Attested runner files would otherwise disappear at
   job teardown. The exact subjects are retained with a commit-pinned upload
   action, explicit hidden-path permission, failure-on-missing, and bounded
   retention.
6. **Poisoned retry directory.** A fixed retained builder work directory made a
   second `make repro-release` fail after a prior attempt. The ordinary target
   now uses a fresh private temporary work tree; final output publication still
   refuses overwrite.
7. **Overclaiming “offline.”** Pip index resolution is disabled after acquisition,
   but the process is not placed in an OS network namespace. Code and receipts
   now name the narrower boundary truthfully.

## Open operational edges

- The hosted workflow owns a 20-minute whole-job deadline, but direct local
  `mxbuilder` bootstrap subprocesses still rely on their caller for a finite
  deadline. An internal phase owner should be added only with a reproduced hang
  and process-tree test, rather than by copying another timeout layer blindly.
- Final release publication is a no-overwrite sequence across several files, not
  a transactional directory swap. A filesystem failure after the first copy can
  leave an incomplete output set; absence of the final run receipt marks it
  incomplete, and the partial set must be removed before retry.

## Local evidence

The focused builder/release tests cover lock parsing, wheel byte and metadata
identity, unsafe/duplicate ZIP members, extraction budgets, receipt tampering,
environment sanitization, exact installed versions, workflow privilege split,
full action pins, retained-subject configuration, and retry-safe Makefile wiring.
The package-input report passes with one seven-entry lock and zero runtime
package dependencies.

This cloudtainer runs Python 3.13.5 while the declared lane requires Python
3.13.14. It also could not resolve PyPI during an attempted acquisition. The
builder correctly refuses the Python mismatch, so no local end-to-end builder
receipt, GitHub-hosted run, attestation, or retained workflow artifact is claimed.
The checked-in hashes were independently compared with the official PyPI JSON
records; execution still belongs to the hosted lane.

## What this does and does not prove

The landing provides source-bound exact builder inputs, bounded independent wheel
validation, index-disabled installation from a verified wheelhouse, deterministic
release construction, and a least-authority hosted attestation/retention
configuration.

It does **not** yet provide:

- an executed hosted receipt or attestation from this revision;
- public package or GitHub Release publication;
- a from-zero offline bootstrap;
- an OS network, process, filesystem, or same-UID adversary sandbox;
- a locked operating-system image, runner image, kernel, C library, or
  `setup-python` toolcache provenance beyond the pinned action/workflow identity;
- Windows or macOS builder receipts;
- cross-platform wheel equality beyond the configured Ubuntu 24.04/Python
  3.13.14 lane; or
- consumer-side attestation verification evidence.

The next publication step is therefore an executed tag/manual hosted run whose
retained files and attestation are downloaded and verified against the repository,
workflow, source commit, and receipt digests. Platform support should grow only
by adding similarly executed receipts, not by broadening prose.

## Primary online sources consulted

- Python 3.13.14 release:
  https://www.python.org/downloads/release/python-31314/
- pip secure-install guidance:
  https://pip.pypa.io/en/stable/topics/secure-installs/
- `pip download` command contract:
  https://pip.pypa.io/en/stable/cli/pip_download/
- PyPA wheel binary distribution specification:
  https://packaging.python.org/en/latest/specifications/binary-distribution-format/
- Official PyPI JSON records:
  https://pypi.org/pypi/pip/26.1.2/json
  https://pypi.org/pypi/setuptools/83.0.0/json
  https://pypi.org/pypi/pytest/9.0.3/json
  https://pypi.org/pypi/iniconfig/2.3.0/json
  https://pypi.org/pypi/packaging/25.0/json
  https://pypi.org/pypi/pluggy/1.6.0/json
  https://pypi.org/pypi/pygments/2.20.0/json
- GitHub's recommendation to pin actions to a commit SHA:
  https://docs.github.com/en/packages/managing-github-packages-using-github-actions-workflows/publishing-and-installing-a-package-with-github-actions
- Official action releases:
  https://github.com/actions/checkout/releases/tag/v7.0.1
  https://github.com/actions/setup-python/releases/tag/v7.0.0
  https://github.com/actions/attest/releases/tag/v4.2.0
  https://github.com/actions/upload-artifact/releases/tag/v7.0.1
- Artifact attestation generation and verification model:
  https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds
  https://docs.github.com/en/actions/concepts/security/artifact-attestations
- Upload-artifact retention, hidden-file, digest, and authenticated-download
  behavior:
  https://github.com/actions/upload-artifact
