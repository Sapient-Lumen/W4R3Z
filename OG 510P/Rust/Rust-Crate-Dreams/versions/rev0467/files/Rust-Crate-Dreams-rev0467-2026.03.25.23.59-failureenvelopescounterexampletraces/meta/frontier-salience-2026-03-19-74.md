# Frontier salience snapshot — 2026-03-19 (74)

This pass did **not** add another MCP SDK, another general agent runtime, or a generic API gateway.
It sharpened a neglected but increasingly leverageable deployment lane:

- **P-0071 MCP Guard Kit** — because MCP now has real Rust SDK/protocol substrate, but still lacks one boring contract for transport exposure, auth boundaries, and risky-operation guards.

## Main judgment

The next worthy move here was **not** another SDK.
That substrate now exists.

The sharper missing layer is the **deployment guard / review contract** above today’s substrate, especially once three more facts are kept explicit:

- **transport exposure truth** — what is local-only, what is remotely reachable, whether origin validation and bind posture are honest;
- **auth-boundary truth** — whether OAuth/resource indicators/audience binding are really enforced, and whether token passthrough is explicitly blocked;
- **operation-guard truth** — what tools/resources/prompts/sampling paths require approval, limits, or redaction.

That move is better grounded now because:

- the MCP docs list official SDK tiers and Rust is now an official Tier 2 SDK;
- the official Rust SDK has crossed into 1.x and is actively adding auth/transport work;
- the specification and security docs now name concrete attack classes and concrete MUST/SHOULD behaviors;
- the 2026 roadmap explicitly names enterprise readiness as a priority area;
- the reference-server repository explicitly warns that its servers are educational, not production-ready;
- and the interceptor extension exists only as an experimental proposal, which means the demand for guard hooks is real but not yet solved normatively.

So the gap is no longer “Rust can talk MCP.”
The gap is that teams still rarely get a **reviewable MCP deployment-security promise** above the SDK.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually use?”
2. **P-0525 Crate Diagnosis Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0524 Crate Example Surface Pack Kit** — still one of the highest-leverage first-success lanes.
4. **P-0520 Crate Lifecycle Surface Pack Kit** — still a strong product-level support surface.
5. **P-0484 Toolchain & Target Support Contract Kit** — still crucial for real machines and real targets.
6. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.
7. **P-0027 text-input-kit** — still one of the clearest end-user product-engineering opportunities.
8. **P-0087 UI Accessibility Doctor Kit** — still a strong authoring-side semantic-quality lane.
9. **P-0515 Crate Off-Ramp Pack Kit** — now one of the clearest survivability / supportiveness follow-ons.
10. **P-0071 MCP Guard Kit** — now promoted because official MCP substrate and security guidance exist, but the deployment guard layer remains under-productized.
11. **P-0392 MCP Protocol Conformance, Transcript & Capability Kit** — still strong, especially for compatibility/evidence bugs rather than deployment guardrails.
12. **P-0012 Desktop ShipKit** — still a strong desktop release/adoption lane.
13. **P-0197 Text Layout & Shaping Conformance Kit** — still a strong cross-stack correctness lab.
14. **P-0466 Python Wheel ABI & Free-Threading ShipKit** — still one of the clearest foreign-package shipping-contract opportunities.
15. **P-0168 Rust Android Mobile Kit** — still a strong mobile/library-shipping lane.
16. **P-0206 Wasm Component Contract & Conformance ShipKit** — still one of the clearest Wasm contract opportunities.

## Why this won over adjacent candidates right now

- It beat another **MCP SDK/host** idea because the official SDK substrate is already real.
- It beat a broader **agent security platform** because the sharper missing value is the compact Rust crate/workflow layer, not a whole product.
- It beat a pure **MCP transcript/conformance** follow-on because the archive already has P-0392 in that lane, while deployment guardrails were still underspecified.
- It beat more **foreign-package shipping** work because this pass needed another strong modern protocol/product-support candidate outside the current packaging cluster.

## What changed in the archive

Added:
- `entries/2026-03-19-254.md`
- `meta/frontier-salience-2026-03-19-74.md`
- `meta/mcp-guard-kit-product-plan-2026-03-19.md`
- `meta/mcp-guard-kit-lane-boundaries-2026-03-19.md`
- `fixtures/mcp-guard-kit/README.md`
- `fixtures/mcp-guard-kit/transport-exposure.receipt.schema.json`
- `fixtures/mcp-guard-kit/auth-boundary.receipt.schema.json`
- `fixtures/mcp-guard-kit/operation-guard.contract.schema.json`
- `fixtures/mcp-guard-kit/scenarios/localhost_http_origin_validation_missing/`
- `fixtures/mcp-guard-kit/scenarios/remote_proxy_token_passthrough_and_missing_audience_binding/`
- `fixtures/mcp-guard-kit/scenarios/tool_sampling_enabled_without_approval_or_loop_limits/`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/mcp-guard-kit.md`
- `meta/known-existing.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `fixtures/mcp-guard-kit/malicious-output-cases.md`

## What this pass deliberately did not do

It did **not** collapse:

- MCP SDK/runtime implementation,
- transcript/conformance evidence,
- deployment guard contracts,
- host/product trust UX,
- and experimental interceptor design

into one fake “MCP support” story.
