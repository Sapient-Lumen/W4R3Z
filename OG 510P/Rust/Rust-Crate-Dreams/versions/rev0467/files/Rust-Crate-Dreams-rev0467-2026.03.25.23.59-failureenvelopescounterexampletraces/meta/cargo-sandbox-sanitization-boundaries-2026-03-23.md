# Cargo sandbox sanitization boundaries — 2026-03-23

This note keeps **P-0107 Cargo Sandbox & Capability Policy Kit** from collapsing ambient ingress, sanitization, and launcher routes into adjacent lanes.

## Within P-0107, keep these truths separate

1. **policy authority** — where the policy came from;
2. **actor capability scope** — which explicit powers were granted or denied;
3. **ambient input** — what env/path/toolchain/wrapper channels still reached the actor;
4. **sanitization mode** — how those channels were inherited, allowlisted, rewritten, or blocked;
5. **launcher route** — how the actor was actually wrapped or intercepted;
6. **enforcement mode** — observe/audit/enforce truth;
7. **exception ownership** — break-glass grants;
8. **policy drift** — what changed materially.

## Not P-0484 toolchain/target support

Toolchain auto-install posture and host/target route facts may appear as imported ingress context here, but **P-0484** still owns whole-project support posture and target-readiness claims.

## Not P-0508 delegated build topology

Build-script delegation may affect compile-time execution routes, but **P-0508** owns unit topology, output-lane ownership, and bridge posture, not ingress or sanitization truth.

## Not runtime authority or supply-chain scoring

A compile-time containment bundle may import security-sensitive context, but **P-0107** should not become:
- a runtime authority descriptor,
- a general package trust score,
- or a generic build reproducibility dashboard.

## Rule for future passes

When touching **P-0107** again, say explicitly whether the change is about:
- new ambient-input classes,
- stronger sanitization semantics,
- launcher-route comparability,
- or only adjacent-lane imports.
