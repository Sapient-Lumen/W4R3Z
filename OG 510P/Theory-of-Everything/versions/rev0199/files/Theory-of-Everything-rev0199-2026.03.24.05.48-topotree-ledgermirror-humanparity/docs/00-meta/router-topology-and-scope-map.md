# Router topology and scope map

Purpose: canonical human mirror for router hierarchy, parent/child ownership, ordered child-lane scope, and one-level reopen discipline. `ROUTER-TOPOLOGY.json` is the machine-readable source for the same parent→child graph and child-order ledger, and the bullet tree below should mirror that ledger exactly. Use this when a revision needs to know which router owns a burden, where a broad surface should stop, and which subordinate lane should be opened next.

## Shared rule

Broad stable, restart, and program surfaces should name the highest matching router that already carries the burden cleanly.
Deepen only the directly touched child surface.
Do not restate a whole parent → child lane tree inline when this map plus the owning router already make the next step explicit.
The `## Topology` bullet tree is not a sketch; it should mirror ROUTER-TOPOLOGY.json exactly as the human-readable parent/child order surface for that ledger.

## Topology

- `docs/40-model/current-head-control-router.md`
  - `docs/40-model/spine.md`
  - `docs/40-model/cross-family-pressure-router.md`
    - `docs/40-model/candidate-bridges.md`
    - `docs/40-model/invariant-matrix.md`
    - `docs/40-model/discriminator-wedges.md`
  - `docs/40-model/empirical-contact-burden-router.md`
    - `docs/40-model/observer-record-minimum.md`
    - `docs/40-model/witness-borrowing-ladder.md`
    - `docs/40-model/witness-package-burden-router.md`
      - `docs/40-model/witness-package-subgate-stack.md`
      - `docs/40-model/witness-closure-gate-family-frame.md`
      - `docs/40-model/current-family-readout-router.md`
        - `docs/40-model/family-b-burden-router.md`
          - `docs/40-model/thermodynamic-gravity-assumption-audit.md`
          - `docs/40-model/non-equilibrium-observable-record-map.md`
          - `docs/40-model/family-b-witness-climb-audit.md`
          - `docs/40-model/family-b-beyond-equilibrium-gate.md`
        - `docs/40-model/family-c-burden-router.md`
          - `docs/40-model/family-c-witness-closure-gate.md`
          - `docs/40-model/family-c-identifiability-stack.md`
          - `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
      - `docs/40-model/local-law-vs-cosmological-package-vs-witness-package-split.md`
  - `docs/40-model/broad-toe-credit-router.md`
    - `docs/40-model/completion-bid-credit-stack.md`
    - `docs/40-model/local-law-vs-cosmological-package-vs-witness-package-split.md`
    - `docs/40-model/vacuum-energy-burden-router.md`
      - `docs/40-model/local-law-vs-cosmological-boundary-split.md`
      - `docs/40-model/cosmological-constant-debt-split-audit.md`
      - `docs/40-model/vacuum-energy-proposal-class-stack.md`
      - `docs/40-model/vacuum-energy-proposal-class-family-frame.md`
    - `docs/40-model/witness-package-burden-router.md`
    - `docs/40-model/current-family-readout-router.md`

## Scope shortcuts

- Open `docs/40-model/current-head-control-router.md` for default re-entry into the archive's present model posture.
- Open `docs/40-model/cross-family-pressure-router.md` when the issue is bridge-family comparison pressure rather than default head control.
- Open `docs/40-model/empirical-contact-burden-router.md` when the issue is observer / record minimum plus witness-side empirical-contact burden.
- Open `docs/40-model/broad-toe-credit-router.md` when the issue is integrated three-book credit rather than default head control.
- Open `docs/40-model/current-family-readout-router.md` when the issue is the bounded family-B versus strongest-current family-C readout rather than the whole witness or broad-credit lane.
- Open `docs/40-model/vacuum-energy-burden-router.md` when the issue is the cosmological-constant / vacuum-energy burden family rather than the whole broad-credit lane.
- Open `docs/40-model/witness-package-burden-router.md` when the issue is witness borrowing, stage order, and closure gating rather than the whole empirical-contact or broad-credit lane.

## Maintenance rule

If a parent router, child router, or subordinate home changes ownership, order, or scope, update this map and `ROUTER-TOPOLOGY.json` in the same revision. Router `## Ordered route` blocks should match the ledger's ordered `children` arrays exactly, and each router's subtree in `## Topology` should mirror that same child order exactly.
If a change leaves the hierarchy untouched, keep the edit in the local surface and do not widen the map by commentary.
