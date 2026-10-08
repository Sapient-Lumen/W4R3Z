# rev0212 vault split, release guard, and cube refactor

rev0212 turns the rev0211 warning into an executable safety boundary. The riskiest unfinished task was not another doctrine page; it was the possibility that a genuine raw counterparty or person-subject artifact could be copied into `examples/artifacts/` and then bundled by a normal handoff release.

The correction is now concrete: live-counterparty evidence staging defaults to an external private vault, public release surfaces carry only a challengeable hash/failed-gate shell, and `package_release.py` fails closed if live-candidate raw payloads or private-vault directories appear inside the release tree.

## What changed

`tools/stage_live_evidence_drop.py` now treats `collection_context=live-counterparty` differently from dry-runs and fixtures. Synthetic controls can still be staged under `examples/artifacts/` for reproducible regression tests, but live candidates are copied to a private vault outside the archive root. Their public ledger locator is `private-vault://...`, and their source locator is redacted to `private-source-redacted:sha256:...`.

`tools/vault_release_guard.py` is a shared release-tree scanner. It rejects private/raw vault prefixes inside the archive, non-synthetic payloads under `examples/artifacts/`, live-candidate ledgers that point at public payloads, and live-candidate ledgers that leak source locators.

`tools/package_release.py` calls the guard before mutating `RELEASE-MANIFEST.json`, refreshing `MANIFEST.sha256`, or writing a zip. This makes the protection part of the packaging path rather than a note for a careful maintainer.

`tools/audit_private_evidence_vault_split.py` validates the policy and public-shell schemas, calls the guard, and performs a synthetic live-counterparty staging test in a temporary external vault. The test confirms that the raw bytes stay outside the archive tree while the public ledger keeps a checkable hash commitment.

## Reliance effect

No live receipt is created. The archive still has a zero computed live floor. This revision makes it safer to attempt the first real artifact later; it does not substitute for that artifact.

The rule is now:

**A real payload may be staged only outside the release tree. A public release may include hash, size, MIME type, private-vault URI, failed-gate state, and challenge path. It may not include raw bytes, secret source paths, counterparty secrets, or a live-floor claim.**

## Cube refactor

This is also a small code refactor. Release safety is no longer duplicated between prose, lint, and packaging. The release guard is a single module reused by both audit and package creation. That reduces the chance that future revisions pass lint but package an unsafe tree through a separate path.

The followthrough queue was updated to close `FT-0211-PRIVATE-EVIDENCE-VAULT-SPLIT` because the vault exclusion, public shell schema/example, stage-tool mode, packaging guard, release audit, and synthetic exclusion dry-run now exist. The first real artifact remains open; the vault split is only a precondition.

## Next pressure point

The next high-risk unfinished work is no longer the vault split. It is the first deliberately small real-world artifact pilot. The pilot should be designed to fail safely if necessary: external private vault, public shell, LEAP candidate, custody record, verifier adapter, non-host retention, response/intake path only after gates, failed-gate summary if blocked, and computed-floor recomputation at the end.
