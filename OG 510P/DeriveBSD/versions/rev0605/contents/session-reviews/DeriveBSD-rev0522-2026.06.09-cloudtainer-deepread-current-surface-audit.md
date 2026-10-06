# DeriveBSD rev0522 cloudtainer deep-read current-surface audit

Revision base: 2026-06-05r554
Package intent: preserve the r554 datacube while correcting stale front-door/current-surface evidence and recording cloudtainer-specific waste traps discovered during a deep read.

## Findings corrected in this cut

The first extraction used Python `zipfile.extractall()`, which lost the executable bits preserved inside the submitted archive. A permission-preserving extraction showed that the archive itself was sound and that release-critical executable-bit failures were an extraction artifact, not source corruption. This session keeps that as an operational warning: use `unzip`, or a custom extractor that restores `ZipInfo.external_attr`, before running tool hygiene.

The post-detach focus profile exposed two real documentation drift defects. `README.md` did not carry the ADR-0348/ADR-0349 front-door bullets required by the r504/r505 post-detach closure and launch-evidence checks. `docs/current/cube-schema-audit.md` was also stale and lacked the r522 `fixture-literal` token required by the scenario replay closure check.

The README also had a duplicate `2026-06-05r549` front-door bullet. This cut merges that duplicate so the top-level release surface is less noisy.

## Current-surface refresh

`docs/current/cube-schema-audit.md`, `docs/current/cube-schema-refactor-backlog.md`, `docs/current/cube-hygiene-checkset.md`, and `docs/current/hygiene-run-ledger.md` were refreshed to match the checked-in generated examples and the r554 hygiene surface. The refreshed audit keeps the important counts visible: 448 schemas, 467 examples, 25 const-heavy schemas, 33 runtime-contract-shaped schemas, 10 exact fixture schemas, 434 schemas with canonical examples, and 14 helper schemas without canonical examples.

The refactor backlog still points at 15 open items, including 7 priority-zero post-detach fixture-literal/runtime-contract splits. The high-value next step remains to keep splitting exact fixture literals out of runtime contracts before adding new post-detach receipt families.

## Waste traps observed

The full hygiene surface is too large for a naive interactive cloudtainer run. Release-critical, generated-surface, schema-cube-audit, and post-detach profiles are useful bounded gates; the full 369-check surface should be driven through resumable ledgers and chunked execution, not one long command.

Python bytecode caches are another local waste/corruption risk. Importing repository tools from ad hoc analysis created `tools/__pycache__`, which release-critical archive hygiene correctly rejected. Future cloudtainer sessions should run with `python -B` or `PYTHONDONTWRITEBYTECODE=1`, and should clean `__pycache__` before packaging.

## Validation notes

After the corrections, `python3 tools/hygiene.py --profile release-critical` passed 35/35 checks. The remaining warnings are front-door budget warnings for `docs/00-index.md` and `docs/99-llm-runbook.md`; they are not failures, but they mark ongoing front-door size debt.

The post-detach profile passed 39/39 checks using a resumable ledger. `schema-cube-audit` passed 3/3 checks and `generated-surface` passed 2/2 checks. A complete all-profile hygiene run was not finished in this cloudtainer because the interactive command window is a poor match for the full deep-contract profile.

## Recommended next corrections

Move the README front-door release bullets toward a generated or bounded surface, with `CHANGELOG.md` and `docs/00-index.md` remaining canonical for long history. Split or generate the oversized front-door documents so humans and agents are not forced to pay an 800 KiB read tax at session start.

Continue the r520 production-schema versus fixture-literal split on the seven priority-zero post-detach schemas before extending the lifecycle graph. Add an explicit external-attestation/export map to in-toto, SLSA, TUF, OCI Referrers, SPDX, and CycloneDX concepts so DeriveBSD receipts remain interoperable rather than purely bespoke.

The next host-critical milestone is still a real FreeBSD run: disposable media image creation, real mount/unmount/detach transcript, Capsicum-shaped worker launch with fd 3/fd 4/fd 5 evidence, and receipt binding to compiled worker and input digests. The Linux cloudtainer can audit the shape but should not claim FreeBSD execution.
