# Promotion contract registry

This registry records **promotion contracts**.
The point is not to attach ceremony to every sentence.
The point is to preserve how canon-level trust was granted or withdrawn.

## Contract patterns

- `PC-0001` — `minimal-canon-promotion`
  - Class: promotion-contract
  - Source status: quarantine, open-question synthesis, or weak canon
  - Target status: inferred, speculative but central, or accepted working discipline
  - Required fields:
    - evidence family,
    - temporal validity posture,
    - demotion trigger,
    - admission route,
    - wired canonical surface
  - Why it exists: prevents persuasive local prose from silently becoming canon without preserving the route by which trust was granted.
  - Dereference: `docs/10-method/promotion-contracts-and-staged-ratification.md`, `docs/20-constitution/claim-registry.md`

- `PC-0002` — `minimal-canon-demotion`
  - Class: promotion-contract
  - Source status: any canon-level status
  - Target status: weaker canon, open question, or quarantine
  - Required fields:
    - what failed,
    - whether the failure was evidential, temporal, semantic, or procedural,
    - replacement surface if any
  - Why it exists: canon that cannot be demoted cleanly is not trustworthy canon.
  - Dereference: `docs/10-method/promotion-contracts-and-staged-ratification.md`, `docs/90-quarantine/wild-speculations-2026-03-08.md`
- `PC-0003` — `decay-watch-ratification`
  - Class: promotion-contract
  - Source status: canon-level claim with explicit temporal exposure
  - Target status: canon plus decay-watch entry
  - Required fields:
    - temporal posture,
    - review horizon,
    - review trigger,
    - review route
  - Why it exists: promotion contracts that preserve temporal validity posture still need a compact place to remember which claims deserve scheduled skepticism.
  - Dereference: `docs/10-method/temporal-demotion-and-decay-patrol.md`, `docs/20-constitution/decay-watch-registry.md`
