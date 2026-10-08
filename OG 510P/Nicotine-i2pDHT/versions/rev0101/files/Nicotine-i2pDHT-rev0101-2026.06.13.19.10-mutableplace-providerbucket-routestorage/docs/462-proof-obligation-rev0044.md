# Proof obligation — rev0044

The current proof obligation is that the cube can reject dangerous joined-boundary cases before any real network side effect exists.

Required proof lane:

```sh
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/test_rev0044_compartmentfirewall_controlreceipt_foldbridge.py
```

Full lane:

```sh
scripts/ci/run_python_cloudtainer_lane.sh
```

Expected evidence: compartment firewall accepts only exact joined public/closed modes; receipt memory rejects drift, replay, fork, rollback, bad signature, and unaccepted joined reports; foldbridge passes.
