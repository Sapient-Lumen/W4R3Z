# Runtime research notes — rev0090

## Question

After rev0089, is generated-token provenance enough to make cached-decode public traces replayable?

## Finding

No. Hugging Face `GenerationConfig` documents `max_new_tokens` as generated-token count independent of prompt length, `do_sample` as the sampling switch, `num_beams` as beam-search width, and `use_cache` as the cached key/value decode switch. The same documentation classifies generation modes: greedy decoding is `num_beams=1` and `do_sample=False`; beam search is `num_beams>1` and `do_sample=False`; sampling is `do_sample=True`. The generation strategies guide also describes greedy search as selecting the most likely next token and sampling as random selection from the probability distribution.

## Implication for the cube

A trace that records `generation_do_sample=false` and generated-token digests can still be a false green if it inherited `num_beams>1` or multiple return sequences from model configuration. The trace would bind the emitted sequence but not the actual decision procedure that produced that sequence. That is enough to corrupt replay expectations, quality comparisons, and future sparse-vs-dense timing comparisons.

## Change made

rev0090 adds `greedy_cached_decode_generation_config_v1` and advances the public trace claim version to `public_trace_claim_v12`. Public cached-decode traces now require canonical generation config JSON, digest verification, `do_sample=false`, `num_beams=1`, `num_return_sequences=1`, `use_cache=true`, and `generation_max_new_tokens == decode_steps_requested`. The new audit rejects a forged beam-count bundle while leaving Q/K/V tensors and dense reference unchanged.

## Sources checked

- Hugging Face Transformers text generation docs: https://huggingface.co/docs/transformers/en/main_classes/text_generation
- Hugging Face Transformers generation strategies guide: https://huggingface.co/docs/transformers/en/generation_strategies
- Hugging Face Transformers generation configuration source notes: https://github.com/huggingface/transformers/blob/main/src/transformers/generation/configuration_utils.py
