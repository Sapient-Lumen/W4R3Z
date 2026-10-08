Tokio `watch` gives each receiver its own seen-state cursor over the shared latest value.
The fixture keeps independent local progress separate from fanout, latest-value memory, and future-only join semantics.
