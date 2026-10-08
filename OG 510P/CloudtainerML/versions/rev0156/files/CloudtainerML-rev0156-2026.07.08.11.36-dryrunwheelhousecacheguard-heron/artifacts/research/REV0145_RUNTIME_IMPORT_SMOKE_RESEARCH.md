# REV0145 runtime import/surface smoke research

Focus: avoid a costly late failure in the first real TinyLlama public trace path.

## Online basis

- Hugging Face Xet docs: `huggingface_hub` 0.32+ installs `hf_xet`; because TinyLlama weights are large and Xet-backed in current Hub flows, `hf_xet` importability should be proved in the capture runtime before download/materialization.
- Hugging Face Hub download docs: `snapshot_download` and cache materialization are an explicit phase; runtime import smoke belongs before that phase in the one-command runner.
- Hugging Face Hub local-cache docs: the selected local snapshot layout is the thing later capture gates bind to; rev0145 does not weaken that binding.
- Transformers Auto docs: Auto classes load model/tokenizer implementations through `from_pretrained`; the smoke checks `AutoTokenizer`, `AutoModelForCausalLM`, and the current Llama eager-attention surface before capture.

## Speculative risk read

The next likely completion failure is not lack of mission doctrine. It is a capable runner spending time/materialization bandwidth before proving that the exact Python runtime can import the capture stack and the hook surface this cube patches. REV0145 therefore turns the risk into an early receipt: `REV0145_PUBLIC_TRACE_RUNTIME_IMPORT_SMOKE.json`.

## Change made

- Added `tools/public_trace_runtime_import_smoke.py`.
- Wired it into `REV0145_BOOTSTRAP_PUBLIC_TRACE_ENV.sh` with `--require-project-venv`.
- Wired it into `REV0145_FIRST_REAL_TRACE_ONE_COMMAND.sh` before snapshot materialization.
- Included the smoke tool in the compact external runner packet.
