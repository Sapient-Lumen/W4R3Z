# Hunt questions — rev0150

1. Can `BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh` reach snapshot materialization on a capable machine without dependency/version drift?
2. Does `REV0150_PUBLIC_TRACE_RUNTIME_REQUIREMENT_LOCK_AUDIT.json` stay `pass` inside the external runner before install?
3. Does `REV0150_PUBLIC_TRACE_RUNTIME_IMPORT_SMOKE.json` pass after bootstrap, with Transformers in the bounded `<5` line and the Llama eager attention surface present?
4. Does snapshot preparation bind the exact pinned TinyLlama commit and model.safetensors SHA-256 before local-only capture?
5. After capture, can selector-entry replay and handoff archive verification reproduce the receipt chain without touching network state?
