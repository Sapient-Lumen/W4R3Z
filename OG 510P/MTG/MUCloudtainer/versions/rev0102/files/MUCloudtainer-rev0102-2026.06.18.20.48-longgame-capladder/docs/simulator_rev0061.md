# simulator rev0061

rev0061 makes no gameplay semantic change.  It adds a mechanism-ablation experiment and one validator refactor.

## Experiment

The new panel asks whether the replicated `cf34_counter_wall` result depends on active Jace/Brainstorm, dense Counterspell, or merely the passive 60-card buffer against a 40-card opponent.

Entry point:

```bash
PYTHONPATH=. python scripts/run_rev0061_mechanism_ablation.py
```

## Result in one line

The all-Island 60-card target still beats the 40-card Overlord opponent in a majority of the small rev0061 cells, especially at life 40.  This indicates the current local claim is mainly a library-buffer/self-decking phenomenon.

## Semantics

No card rules, legal-action generation, hidden-information boundary, reward convention, or C++ transition microkernel semantics changed in rev0061.

## Validation entry points

```bash
PYTHONPATH=. python scripts/run_rev0061_mechanism_ablation.py
PYTHONPATH=. python scripts/run_rev0061_artifact_audit.py
PYTHONPATH=. python -m pytest -q
PYTHONPATH=. python run_smoke.py
PYTHONPATH=. python scripts/audit_cube.py
```
