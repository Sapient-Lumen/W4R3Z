# Online research notes — REV0102

Sources reviewed this turn:

- https://huggingface.co/docs/transformers/en/main_classes/tokenizer
- https://huggingface.co/docs/transformers/en/chat_templating
- https://huggingface.co/docs/transformers/en/main_classes/text_generation
- https://huggingface.co/docs/transformers/en/kv_cache

Findings used in this revision:

- Tokenizers prepare model inputs and can have fast/Rust and Python implementations, so public replay should record tokenizer surface facts.
- Chat-template guidance warns that special-token handling can be wrong or duplicated when templates and later tokenization are mixed; this trace explicitly records raw-prompt mode and `chat_template_applied=false`.
- Generation cache implementation remains a runtime semantic knob; rev0102 keeps the rev0101 dynamic-cache requirement.

Speculation: the final evidence packet will fail less often on math than on replayability: a missing prompt manifest, hidden tokenizer default, or implicit chat template can make a trace irreproducible even when dense parity passes.
