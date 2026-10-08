# Cooperation benchmark cards should publish tool access, external state, and knowledge snapshot policy

A compact cooperation benchmark card is still too weak if the published result quietly depends on **which tools, which world snapshot, or which knowledge source the evaluated system could actually use**.
Even when the nominal task, evaluated subject, wrapper, judge, and scoring rule are fixed, a cooperation result can move because the tool catalog changed, distraction or helper tools were added, the environment was live instead of frozen, or the retrieval corpus came from a different snapshot.

Recent evaluation work makes the archive rule clear:

- `RS-GR-102` argues that agentic benchmarks are defined by a task in a specific environment with a given set of tools, so tool and environment setup belongs to benchmark validity rather than to invisible harness plumbing.
- `RS-GR-103` argues that current agent evaluations are confounded by toolset configurations and environmental dynamics, and that lack of standardized environmental data leads to non-reproducible results.
- `RS-GR-104` shows a concrete agent benchmark where performance varies with external tool access and where a reproducible sandbox is used to instantiate the environment identically across runs.
- `RS-GR-105` shows a state-snapshot paradigm that freezes the full operational context into an immutable persistence layer, which means environment snapshot policy is part of the evaluation contract.
- `RS-GR-106` shows that knowledge-grounded agent benchmarks can materially depend on private corpus construction plus retrieval configuration choices such as reranking, grep access, and write-tool permission.
- `RS-GR-107` shows that even adding distraction tools or scrambling tool descriptions can materially move benchmark scores, so the available tool surface is not a harmless implementation detail.

## Minimum contract

Whenever a retained cooperation result could change because of environment setup or external knowledge access, publish four short fields on the card or neighboring compact receipt:

1. **tool / capability catalog and access policy** — which tools or APIs were available, whether access was direct or had to be discovered from documentation, any hidden / distraction / helper tools, and any notable description or schema transformations;
2. **external environment / state snapshot posture** — frozen snapshot vs live service vs replayed log vs mocked simulator, what parts of the world state were fixed before each run, and whether temporal drift or live external updates were possible;
3. **knowledge base / retrieval corpus provenance and snapshot** — what corpus, docs, or policy store the agent could consult, the relevant snapshot or build date when known, whether retrieval was dense / sparse / filesystem / hybrid, and any major reranker or filter layer;
4. **reset / refresh / mutability policy** — whether tool state, world state, caches, and corpora were reset between attempts or subjects, whether the agent could write notes or mutate the accessible corpus, and whether any live refresh or asynchronous data updates were allowed during evaluation.

If the benchmark intentionally studies cooperation under a fixed frozen sandbox, say that directly.
If it intentionally studies cooperation over a live or evolving environment, say that directly too.

## Implementor consequence

Do not compare a fixed-tool benchmark, a distraction-tool benchmark, a live-service benchmark, a frozen-snapshot benchmark, and a different-corpus-snapshot benchmark as though they were the same cooperation object.
A retained result may still be useful under any of those regimes, but the comparison license should say which environment-and-knowledge contract it belongs to.
If the benchmark changes the tool surface, environment snapshot, or accessible corpus, that change should appear as part of the reported condition rather than as hidden evaluation plumbing.

## Archive consequence

Keep the retained object tiny.
One short tool-catalog / state-snapshot / corpus-provenance / reset-mutability quartet is enough.
That prevents future sessions from laundering tool availability, world-state drift, or knowledge-source changes into an inheritor-facing cooperation gain while still keeping the archive compact.
