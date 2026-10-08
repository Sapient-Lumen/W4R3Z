# Epic Proposal: Lane Default Evidence Bundle (`cargo lane-evidence` + `lane-evidence-pack/v0`)

## One-sentence pitch
Give Rust’s emerging defaults corpus a portable evidence layer so default cards can be renewed from attached canon, registry, compatibility, support-envelope, maintenance, and freshness inputs instead of from folklore.

## Why this is worthy
The archive has already crossed one threshold:
it now publishes actual default cards.

That exposes the next bottleneck immediately.
A default card that cannot be renewed cheaply and honestly is not infrastructure yet.

Rust’s current official signals all support this:
- the ecosystem challenge is navigation and tacit knowledge, not just lack of libraries;
- docs remain canonical while LLM/editor mediation rises;
- crates.io exposes richer review signals than before;
- Cargo is growing plumbing around API, SBOM, time, and script workflows;
- malicious-crate response is moving toward durable advisory channels rather than noisy one-off blog posts;
- maintenance is now explicitly treated as strategic infrastructure.

## Deliverables
- `design/lane-default-evidence-bundle.md`
- `design/lane-default-evidence-pilot-program.md`
- `gaps/reviewable-default-evidence-and-renewal-receipts.md`
- one compact meta working set for future renewal edits
- at least one renewed/default-added card backed by the new evidence discipline
- optional thin tooling:
  - `cargo lane-evidence canon`
  - `cargo lane-evidence registry`
  - `cargo lane-evidence api`
  - `cargo lane-evidence support`
  - `cargo lane-evidence renew`
  - `cargo lane-evidence diff`
  - `cargo lane-evidence pack`

## Why now
- `pubtime` and `--publish-time` make time-aware review more plausible.
- Security tab and Trusted Publishing make registry evidence more importable.
- `public-dependency`, SBOM precursors, and semver-check work make API and supply-chain evidence more concrete.
- cargo-script provides a strong next bounded default-card candidate.
- safety-critical Rust makes clear that harder defaults need stronger evidence imports.

## First proof points
1. renew conservative internal CLI with an explicit evidence pack;
2. renew conservative HTTP/service with support-envelope imports;
3. add a script/repro/tiny-utility card as `default-with-caveats`;
4. only then attempt a public safety-tilted card.

## Non-goals
- one global crate score;
- replacing crates.io or Cargo;
- replacing package-admission, maintenance, or compatibility stacks;
- automatic freshness claims with no review owner.

## Strategic value
This is the move that turns default cards from “useful notes” into a renewable public control plane.
That is a more durable ecosystem contribution than merely publishing more recommendation prose.
