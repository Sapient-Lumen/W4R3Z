# Wake from amnesia — rev0031

Remember this revision as the **scope coupon** revision.

Risk being tested: a fact valid in one lane gets reused in another lane. The answer is threefold:

1. exact scope fence before join
2. obligation debt after provisional accept
3. decay mesh so evidence does not live forever

Run:

```text
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q tests/test_rev0031_scopefence_obligation_decay.py
```
