# Wake from amnesia — rev0042

Start with `docs/434-rev0042-multiservice-cooldown-keyoperator.md`.

Read the current implementation in this order:

1. `multiservice.py` — shared-router action pressure across sibling services.
2. `profilecooldown.py` — emergency freeze/cooldown memory and recovery evidence.
3. `operatorkey.py` — operator-key rotation and recovery.
4. `announcementrepair.py` — post-bridge-disable catalog/announcement repair.
5. `controlplanefold.py` — audit/refactor visibility.

Then run:

```sh
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_rev0042_multiservice_cooldown_keyoperator.py
bash scripts/ci/run_python_cloudtainer_lane.sh
```

Current mental model: rev0041 handled stopping/resuming one router-backed service; rev0042 asks what breaks when several services share the same router/profile/operator authority.
