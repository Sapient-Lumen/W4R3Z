# Frontier salience snapshot — 2026-03-21-158

This pass did **not** add another verifier, another evidence bundle, or another graphical standards wrapper.
It deepened **P-0503 Assurance Case Workbench Kit**.

## Why this frontier moved up

The current substrate now makes the missing layer much sharper:

- Rust’s 2026 flagship themes explicitly include **Safety-Critical Rust** with certified tooling, specifications, and evidence;
- the January 2026 safety-critical Rust post is explicit that ecosystem support thins as projects move toward higher criticality;
- the Rust Foundation’s Safety-Critical Rust Consortium explicitly names guidelines, linters, libraries, static analysis tools, and formal methods as in-scope;
- SACM now remains an active formal OMG standard for structured assurance cases, while the broader GSN ecosystem still shows how common standards-shaped argument views are;
- tools such as WebGSN, AssurancePlatform, and CertWare prove that assurance-case tooling exists, but not that Rust teams have one boring import/status/diff contract above Rust-native evidence bundles.

That combination means “we can export GSN” or “we gathered some evidence” is still too vague as a crate claim.
A worthy crate in this frontier should publish at least:

1. **claim-library basis truth**,
2. **import-policy truth**,
3. **assumption-ledger truth**,
4. **review-gate truth**,
5. **export-projection truth**.

## Main conclusion

Promote **P-0503** upward again, but keep it narrow.
The sharper next move is not another theorem prover, not another bundle format, and not a giant assurance portal.
It is a boring contract that keeps **claim basis**, **import policy**, **assumptions**, **review gate**, and **export projection** separately reviewable.

## Ranked near-term frontier from this pass

1. **P-0532 Async Runtime Assurance Profile Kit** — still strongest because runtime-family and qualification posture remain a live gap.
2. **P-0503 Assurance Case Workbench Kit** — strengthened because enough lower-layer evidence substrate now exists that a higher-layer review/import contract is the sharper missing layer.
3. **P-0485 Verification Campaign Workbench Kit** — remains strong because campaign bundles are still one of the most important feeders into assurance review.
4. **P-0256 Evidence Bundle Core Kit** — remains strong because portable assurance packs still want shared bundle substrate.
5. **P-0073 Async Replay Debugger Kit** — remains strong because incident evidence still needs a more honest replay contract.

## Keep these boundaries sharp

- **P-0503** is claim-library basis + import policy + assumption ledger + review gate + export projection truth.
- verification campaigns are separate.
- generic bundle substrate is separate.
- standards-native editors are separate.
- full certification workflow ownership is separate.

Do not let “assurance support” flatten those into one fake crate.
