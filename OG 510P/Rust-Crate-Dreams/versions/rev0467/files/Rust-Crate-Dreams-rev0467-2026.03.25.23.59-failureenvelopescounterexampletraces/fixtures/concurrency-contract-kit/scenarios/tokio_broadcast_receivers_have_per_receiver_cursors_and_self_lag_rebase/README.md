Tokio `broadcast` gives receivers per-receiver progress over retained history and rebases a lagging receiver locally when it falls behind.
The fixture keeps per-receiver lag recovery separate from full replay and separate from shared-claim work queues.
