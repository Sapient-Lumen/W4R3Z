# Online research notes — REV0103

This rev used current upstream docs to harden runtime provenance instead of adding another registry.

- Hugging Face Transformers documents model loading via `from_pretrained`; the capture path now records/passes an explicit `--torch-dtype` rather than inheriting dtype from defaults or shell history.
- Hugging Face Transformers documents selectable attention backends through `attn_implementation`; rev0103 keeps eager backend identity bound to runtime dtype/device identity.
- Hugging Face Transformers generation/cache docs show cache implementation is a configurable generation surface; rev0103 preserves the dynamic-cache contract from rev0101/rev0102.
- PyTorch CUDA Event docs describe events as timing/synchronization markers. rev0103 therefore records a timing-clock contract and synchronized wall-clock metadata, while still refusing to treat trace-capture elapsed time as named-hardware sparse-vs-dense promotion evidence.

Sources consulted:

- https://huggingface.co/docs/transformers/en/main_classes/model
- https://huggingface.co/docs/transformers/en/attention_interface
- https://huggingface.co/docs/transformers/en/main_classes/text_generation
- https://huggingface.co/docs/transformers/en/kv_cache
- https://docs.pytorch.org/docs/stable/generated/torch.cuda.Event.html
