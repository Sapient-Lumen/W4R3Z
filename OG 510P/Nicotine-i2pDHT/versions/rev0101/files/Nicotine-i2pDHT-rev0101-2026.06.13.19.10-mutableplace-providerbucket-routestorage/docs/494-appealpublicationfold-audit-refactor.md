# Appeal/publication fold audit and branchlet refactor

The audit lane in rev0047 is `appealpublicationfold.py`.

It pins the active current-revision path:

- `witnessappealmesh.py`
- `publicationledger.py`
- `bridgequenchlane.py`
- `appealpublicationfold.py`
- `tests/test_rev0047_appeal_publication_quench.py`
- docs `490` through `494`

It also checks that the sibling rev0046 public-bridge branchlets were preserved under `artifacts/branchlets/rev0046_public_bridge_branchlets/` instead of becoming hidden alternate history.

The fold keeps rev0046 `moderationfold` as predecessor history and requires foldmap, foldregistry, and surfaceledger to know rev0047.
