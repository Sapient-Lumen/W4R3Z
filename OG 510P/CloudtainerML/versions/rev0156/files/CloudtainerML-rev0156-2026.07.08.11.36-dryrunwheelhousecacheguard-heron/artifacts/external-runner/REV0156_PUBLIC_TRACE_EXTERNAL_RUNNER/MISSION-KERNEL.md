# Mission kernel — REV0156 / rev0156

CloudtainerML is a claim compiler. Current entrypoint: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`. The live path is a digest-bound TinyLlama public trace, not registry expansion. REV0156 removes two operational blockers/wastes before the first trace: dry-run now validates the real one-command wrapper without creating a venv, and the runtime bootstrap can use a wheelhouse while guarding against accidental Hugging Face cache duplication.
