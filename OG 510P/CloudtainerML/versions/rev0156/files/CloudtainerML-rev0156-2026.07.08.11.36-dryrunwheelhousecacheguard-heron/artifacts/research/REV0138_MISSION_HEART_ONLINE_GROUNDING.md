# REV0138 mission-heart online grounding

This note grounds the rev0138 deep read in external docs. It is context only, not CloudtainerML performance evidence.

## Hugging Face local identity matters

Transformers documents that a model can be loaded from a local directory when that directory contains the expected configuration; this supports CloudtainerML's insistence that the trace receipt bind the selected local path, not merely a model label. Source: Hugging Face Transformers model docs, lines 118 and 250-252 in the web read.

Hugging Face Hub download docs document `snapshot_download`, `cache_dir`, `local_dir`, `revision`, `local_files_only`, and dry-run/cache behavior. This supports the snapshot/materialization split and the local-only capture rule. Source: Hugging Face Hub download guide and file-download reference, lines 168-171 and 203-221 in the web read.

## TinyLlama is a reasonable first public-trace target, but not evidence by itself

The TinyLlama model card says the project uses a compact 1.1B Llama-style model and notes `transformers>=4.34` for use. This makes it a practical small public checkpoint, but the model card does not substitute for a digest-verified local snapshot or a CloudtainerML trace receipt. Source: TinyLlama Hugging Face model card, lines 187-193 in the web read.

## Attention/cache semantics must stay separated from speed baselines

Transformers cache docs say DynamicCache is the default and grows as generation progresses; the same docs warn that StaticCache can enable JIT but may waste masked tokens. This supports keeping dynamic-cache trace semantics separate from a later static/compiled timing lane. Source: Transformers cache strategies docs, lines 124-161 in the web read.

Transformers attention docs expose `attn_implementation` and warn that custom attention backends must register matching mask behavior or causal/padding/sliding constraints can be silently dropped. This directly supports CloudtainerML's score-path/mask-fidelity obsession. Source: Transformers attention interface docs, lines 126-139 and 212-217 in the web read.

## External attestation norms support digest-bound receipts

SLSA/in-toto materials emphasize provenance/attestations that downstream consumers can verify. CloudtainerML should borrow that pressure lightly: subject digests, materials, predicates, and replayable verification, without turning into a standards bureaucracy. Source: SLSA attestation model and SLSA/in-toto docs, lines 67-80 and 24-28 in the web read.
