# Wake from amnesia — rev0029

Start here after forgetting the cube:

1. Read `docs/279-rev0029-checkpointlane-egressmeter-foldseal.md`.
2. Read `docs/280-checkpoint-lane-restart-pressure.md`.
3. Read `docs/281-egress-meter-metadata-budget.md`.
4. Read `docs/282-dispatch-join-misbind-egress.md`.
5. Read `docs/283-foldseal-audit-refactor.md`.
6. Run `tests/test_rev0029_checkpoint_egress_dispatch_foldseal.py`.

Core memory:

```text
Restart summaries, egress budgets, and bound dispatch intents are not interchangeable safety reports.
```

The cube is still DHT-first, consumer-agnostic, and no-network.
