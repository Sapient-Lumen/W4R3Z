# Open questions — rev0147

- No real TinyLlama trace exists yet.
- No selector/evaluation/handoff chain over a real trace exists yet.
- No named-hardware sparse-vs-dense timing exists yet.
- On a capable machine, do the bounded runtime requirements install cleanly across CPU-only and CUDA environments? If not, the next refactor should split `torch` install guidance from the capture-surface requirements rather than loosening the Transformers bound.
- Once the first trace exists, does the preflight handoff materially reduce wall-clock compared with the direct one-shot fallback?
