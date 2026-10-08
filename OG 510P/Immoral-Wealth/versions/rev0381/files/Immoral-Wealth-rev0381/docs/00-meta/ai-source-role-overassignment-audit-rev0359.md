---
status: source_role_overassignment_audit
revision_current: rev0370
generated_at: 2026-06-18T14:06:00Z
---

# AI source-role overassignment audit — rev0359

Finding: broad `source_ids` still behave like discovery references, not proof. Rev0359 raises locator-bound verified claim edges to 20 and keeps the legacy 6793 mechanical associations explicitly noncertifying.

| Source | Used-by-field count | Verified claim edges | Risk flag |
|---|---:|---:|---|
| S521 | 48 | 0 | overassigned_discovery_source |
| S522 | 48 | 0 | overassigned_discovery_source |
| S523 | 47 | 0 | overassigned_discovery_source |
| S524 | 47 | 0 | overassigned_discovery_source |
| S525 | 47 | 0 | overassigned_discovery_source |
| S526 | 47 | 1 | converted_to_verified_edges |
| S531 | 41 | 0 | overassigned_discovery_source |
| S532 | 40 | 0 | overassigned_discovery_source |
| S528 | 39 | 0 | overassigned_discovery_source |
| S527 | 38 | 1 | converted_to_verified_edges |
| S529 | 38 | 0 | overassigned_discovery_source |
| S530 | 38 | 1 | converted_to_verified_edges |
| S463 | 35 | 0 | overassigned_discovery_source |
| S464 | 33 | 0 | overassigned_discovery_source |
| S465 | 32 | 0 | overassigned_discovery_source |
| S504 | 29 | 0 | overassigned_discovery_source |
| S516 | 29 | 3 | converted_to_verified_edges |
| S517 | 29 | 0 | overassigned_discovery_source |
| S518 | 29 | 0 | overassigned_discovery_source |
| S519 | 29 | 0 | overassigned_discovery_source |
| S520 | 29 | 0 | overassigned_discovery_source |
| S533 | 28 | 0 | overassigned_discovery_source |
| S534 | 28 | 0 | overassigned_discovery_source |
| S535 | 28 | 1 | converted_to_verified_edges |
| S536 | 28 | 1 | converted_to_verified_edges |
| S537 | 28 | 0 | overassigned_discovery_source |
| S397 | 27 | 0 | overassigned_discovery_source |
| S435 | 27 | 0 | overassigned_discovery_source |
| S434 | 26 | 0 | overassigned_discovery_source |
| S436 | 26 | 0 | overassigned_discovery_source |

## Refactor rule

Do not count a source assignment as evidence of a premise unless it has a verified claim edge with an exact locator, relationship code, does-not-prove boundary, contrary-evidence need, and reversal rule.
