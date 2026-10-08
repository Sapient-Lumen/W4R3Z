# ChatGPT proof preflight

`proof-preflight` is the offline gate to run before any live ChatGPT checkpoint attempt.
It exists because we cannot always run the live proof, but we can still prove the tree is
ready and avoid drifting into stale selectors or fake live claims.

Run it from the project root:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-preflight --pretty
```

It checks four things:

1. Static tree readiness: ChatGPT-only host permission, ChatGPT adapter, native-host template,
   surface oracle, proof rehearsal, and evaluator are present.
2. Active surface contract: the saved known-good fixture still satisfies the active ChatGPT
   surface contract.
3. Optional current surface report: when supplied with `--surface-report`, the current
   Tampermonkey/console report must satisfy the active contract.
4. Offline proof rehearsal: the evaluator path must return
   `rehearsal-harness-ok-not-live`.

Successful output has this verdict:

```text
ready-for-live-operator-attempt-not-a-live-proof
```

That verdict is intentionally not a support claim. It means the harness is ready for a guarded
operator-run live attempt once ChatGPT access is available. A live proof still requires the
checkpoint prompt, exact assistant reply, live evidence pack, ledger, schema validation, bundle
audit, evaluator output, and privacy review.
