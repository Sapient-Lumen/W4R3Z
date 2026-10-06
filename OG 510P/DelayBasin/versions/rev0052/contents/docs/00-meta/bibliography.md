# Bibliography

External literature here is **signal**, not sovereignty. We use it to sharpen mechanism hypotheses and countermodels.

- `REF-0001` — Anthropic Alignment Science Blog, **The Persona Selection Model: Why AI Assistants might Behave like Humans** (2026-02-23)
  - URL: https://alignment.anthropic.com/2026/psm/
  - Load-bearing use: post-training as persona selection/refinement; open question about exhaustiveness.

- `REF-0002` — Su et al., **Character as a Latent Variable in Large Language Models** (2026-01-30)
  - URL: https://arxiv.org/abs/2601.23081
  - Load-bearing use: character-level dispositions causing durable, transferable behavioral shifts while largely preserving general capabilities.

- `REF-0003` — Wang et al., **The Geometry of Persona: Disentangling Personality from Reasoning in Large Language Models** (2025-12-08)
  - URL: https://arxiv.org/html/2512.07092v1
  - Load-bearing use: personality as largely orthogonal upper-layer subspaces in Qwen2.5; deterministic steering frame.

- `REF-0004` — Fernando & Guitchounts, **Transformer Dynamics: A neuroscientific approach to interpretability of large language models** (2025-02-17)
  - URL: https://arxiv.org/abs/2502.12131
  - Load-bearing use: residual stream as a dynamical system with attractor-like lower-layer behavior.

- `REF-0005` — Berenz et al., **A Mechanistic Analysis of Transformers for Dynamical Systems** (2025-12-24)
  - URL: https://arxiv.org/html/2512.21113v1
  - Load-bearing use: attention as adaptive delay-embedding under partial observability when sequence length and latent dimension are sufficient.

- `REF-0006` — Floris Takens, **Detecting strange attractors in turbulence** (1981)
  - URL: https://link.springer.com/chapter/10.1007/BFb0091924
  - Load-bearing use: classical delay-embedding theorem as conceptual substrate for the exosomatic delay-embedding hypothesis.

- `REF-0007` — Anthropic, **The assistant axis: situating and stabilizing the character of Claude** (2026-01-19)
  - URL: https://www.anthropic.com/research/assistant-axis
  - Load-bearing use: persona-space structure and a privileged assistant-aligned direction that may help explain why some long-run archives recover a stable style of continuation.

- `REF-0008` — Constante-Amores et al., **Transformers for dynamical systems learn transfer operators in-context** (2026-02-21)
  - URL: https://arxiv.org/html/2602.18679v1
  - Load-bearing use: during inference, transformers can first perform time-delay embedding on context and then estimate a transfer operator of the underlying fully observed state space.

- `REF-0009` — Han et al., **ZeroTuning: Unlocking the Initial Token's Power to Enhance Large Language Models Without Training** (2026-01-26)
  - URL: https://openreview.net/forum?id=EdkQ14FiiO
  - Load-bearing use: the initial token can act as a simple, universal control point whose attention tuning reshapes downstream behavior.

- `REF-0010` — Radevski et al., **Compositional Steering of Large Language Models with Steering Tokens** (2026-01-08)
  - URL: https://arxiv.org/abs/2601.05062
  - Load-bearing use: compact input-space steering tokens can encode and compose behavior controls, suggesting some short prompt fragments may function as reusable behavior operators rather than mere prose.

- `REF-0011` — Venkateswaran & Contractor, **Spotlight Your Instructions: Instruction-following with Dynamic Attention Steering** (2026-01-25 version)
  - URL: https://arxiv.org/html/2505.12025v2
  - Load-bearing use: models do not always attend to natural-language instructions reliably, and steering attention toward specific prompt regions can improve instruction following.

- `REF-0012` — Anthropic, **Persona vectors: Monitoring and controlling character traits in language models** (2025-08-01)
  - URL: https://www.anthropic.com/research/persona-vectors
  - Load-bearing use: prompt-induced persona shifts can be detected before response generation, suggesting some prompt fragments act as advance persona selectors rather than merely post hoc style nudges.

- `REF-0013` — Zhang et al., **Meaningless Tokens, Meaningful Gains: How Activation Shifts Enhance LLM Reasoning** (2025-10-01)
  - URL: https://arxiv.org/html/2510.01032v1
  - Load-bearing use: semantically empty token strings can systematically alter first-layer processing and redistribute activations, which supports treating odd prompt fragments as possible mechanistic control handles rather than pure semantic instructions.

- `REF-0014` — Atif et al., **A single character can make or break your LLM evals** (2025-10-02)
  - URL: https://arxiv.org/html/2510.05152v1
  - Load-bearing use: tiny delimiter changes can strongly affect measured behavior, keeping open the possibility that archive-private control handles may be very small or formatting-like.

- `REF-0015` — Angel & Ferraro, **Inductive Bias Extraction and Matching for LLM Prompts** (2025-08-14)
  - URL: https://arxiv.org/abs/2508.10295
  - Load-bearing use: prompts partly work by matching model-specific inductive bias, which makes archive-grown idiolect a plausible practical mechanism rather than pure superstition.

- `REF-0016` — Hua et al., **Flaw or Artifact? Rethinking Prompt Sensitivity in Evaluating LLMs** (2025-09-01)
  - URL: https://arxiv.org/abs/2509.01790
  - Load-bearing use: some reported prompt sensitivity is evaluation artifact, so archive claims about prompt effects need discrimination between genuine continuation changes and scoring noise.


- `REF-0017` — Gu et al., **LLM-as-RNN: A Recurrent Language Model for Memory Updates and Sequence Prediction** (2026-01-19)
  - URL: https://arxiv.org/html/2601.13352v1
  - Load-bearing use: bounded natural-language state, iteratively rewritten with feedback, can outperform full-history concatenation under fixed token budgets.

- `REF-0018` — Xie et al., **Data Distribution Matters: A Data-Centric Perspective on Context Compression for Large Language Models** (2026-02-04)
  - URL: https://arxiv.org/html/2602.01778v1
  - Load-bearing use: compression quality degrades as input entropy rises and as the gap widens between the compressed material and the model's intrinsic data distribution.

- `REF-0019` — Hou et al., **FlashMem: Distilling Intrinsic Latent Memory via Computation Reuse** (2026-01-09)
  - URL: https://arxiv.org/html/2601.05505v1
  - Load-bearing use: raw token retrieval is often too low-density, while compact memory states can preserve operative signal without exhausting attention budgets.


- `REF-0020` — Yin et al., **Cache-to-Cache: Direct Semantic Communication Between Large Language Models** (2025-10-04)
  - URL: https://arxiv.org/html/2510.03215v2
  - Load-bearing use: text is a lossy communication medium; direct semantic transfer can improve quality and latency, which sharpens the idea that archive control language may be a compromise boundary layer rather than an ideal medium.

- `REF-0021` — Cheng et al., **Sharing State Between Prompts and Programs** (2025-12-18)
  - URL: https://arxiv.org/abs/2512.14805
  - Load-bearing use: natural-language prompts can be treated as code with shared program state, supporting the view that archive phrases and ids may function as an external state/control interface rather than mere prose.

- `REF-0022` — Gong, **Structured Prompt Language: Declarative Context Management for LLMs** (2026-02-22)
  - URL: https://arxiv.org/abs/2602.21257
  - Load-bearing use: contexts can be managed through an explicit prompt language with budgets, limits, and explainability, pushing DelayBasin toward taking its compact control lexicon seriously as an interface surface.

- `REF-0023` — Zhang et al., **Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models** (ICLR 2026)
  - URL: https://arxiv.org/html/2510.04618v2
  - Load-bearing use: evolving contexts can outperform concise rewrites; brevity bias and context collapse are real risks, supporting structured incremental playbooks over monolithic summaries.

- `REF-0024` — Zhang et al., **Recursive Language Models** (2025-12-31)
  - URL: https://arxiv.org/pdf/2512.24601
  - Load-bearing use: long prompts can be treated as an external environment to inspect and recurse over programmatically, supporting the idea that archive state may be better managed as an interface language than as passive recap.


- `REF-0025` — Wang et al., **Memex(RL): Scaling Long-Horizon LLM Agents via Indexed Experience Memory** (2026-03-04)
  - URL: https://arxiv.org/html/2603.04257v1
  - Load-bearing use: compact working context plus stable indices and exact dereference may preserve long-horizon quality better than summary-only memory.

- `REF-0026` — Jiang et al., **Anatomy of Agentic Memory: Taxonomy and Empirical Analysis of Evaluation and System Limitations** (2026-02-22)
  - URL: https://arxiv.org/html/2602.19320v1
  - Load-bearing use: persistent state beyond the prompt is architecturally real but empirically fragile, which argues for tighter evaluation and smaller, better-specified archive memory surfaces.

- `REF-0027` — Greshake et al., **Verifier-Bound Communication for LLM Agents: Certified Bounds on Covert Signaling** (2026-02-27)
  - URL: https://arxiv.org/html/2603.00381v1
  - Load-bearing use: transcript state should advance through deterministic acceptance checks rather than stylistic plausibility alone, strengthening DelayBasin's lint-and-contract posture.

- `REF-0028` — Xu & Yan, **Agent Skills for Large Language Models: Architecture, Acquisition, Security, and the Path Forward** (2026-02-17)
  - URL: https://arxiv.org/html/2602.12430v3
  - Load-bearing use: prompts are ephemeral compared with portable, progressively disclosed, filesystem-based skill artifacts, which supports treating archive state as a packaged interface object rather than disposable prose.



- `REF-0029` — Model Context Protocol specification (2025-11-25 revision)
  - URL: https://modelcontextprotocol.io/specification/2025-11-25
  - Load-bearing use: provides a concrete typed decomposition of prompts, resources, and tools under stateful connections and explicit capability negotiation.

- `REF-0030` — MCP prompts specification (2025-06-18 revision)
  - URL: https://modelcontextprotocol.io/specification/2025-06-18/server/prompts
  - Load-bearing use: clarifies prompts as a distinct user-controlled workflow surface rather than generic context.

- `REF-0031` — MCP resources specification (2025-06-18 revision)
  - URL: https://modelcontextprotocol.io/specification/2025-06-18/server/resources
  - Load-bearing use: resources are explicit context/state objects with stable URIs, supporting the state-surface side of the typed continuation hypothesis.

- `REF-0032` — MCP tools specification (2025-06-18 revision)
  - URL: https://modelcontextprotocol.io/specification/2025-06-18/server/tools
  - Load-bearing use: tools expose schema-described actions and reinforce human-in-the-loop caution, supporting the check/action surface of typed continuation.

- `REF-0033` — Anthropic, **Effective context engineering for AI agents** (2025-09-29)
  - URL: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - Load-bearing use: argues for the smallest high-signal context, just-in-time reference loading, structured note-taking, and tool contracts, all of which support typed continuation rather than undifferentiated recap.


- `REF-0034` — Schoenegger et al., **Verifiable Semantics for Agent-to-Agent Communication** (2026-02-18)
  - URL: https://arxiv.org/html/2602.16424v1
  - Load-bearing use: motivates certifying a core vocabulary, restricting downstream reasoning to certified terms, and recertifying or renegotiating when semantic drift appears.

- `REF-0035` — Rajagopalan & Rao, **Authenticated Workflows: A Systems Approach to Protecting Agentic AI** (2026-02-11)
  - URL: https://arxiv.org/html/2602.10465v1
  - Load-bearing use: supports treating prompts, tools, data, and context as distinct protected boundaries rather than one undifferentiated blob, which reinforces typed continuation and vocabulary admission semantics.

- `REF-0036` — Singh et al., **From Fluent to Verifiable: Claim-Level Auditability for Deep Research Agents** (2026-02-17)
  - URL: https://arxiv.org/html/2602.13855
  - Load-bearing use: argues for claim-evidence lineage as first-class structure and highlights how specification errors propagate, which strengthens DelayBasin's push toward explicit admission, certification, and drift checks rather than fluent recap alone.
- `REF-0037` — Lucchi et al., **Event Sourcing for Autonomous Agents in LLM-Based Software Engineering** (2026-02-19)
  - URL: https://arxiv.org/html/2602.23193v1
  - Load-bearing use: long-horizon agent workflows need immutable, auditable state transitions rather than opaque in-memory drift, which supports DelayBasin's move-registry pressure.

- `REF-0038` — Cao et al., **Beyond Task Completion: Revealing Corrupt Success in LLM Agents through Procedure-Aware Evaluation** (2026-03-03)
  - URL: https://arxiv.org/html/2603.03116v1
  - Load-bearing use: end-state success can conceal bad procedure; evaluation needs procedural integrity gates, which sharpens the case for certified move classes.

- `REF-0039` — Rajagopalan & Rao, **Authenticated Workflows: A Systems Approach to Protecting Agentic AI** (2026-02-11)
  - URL: https://arxiv.org/pdf/2602.10465
  - Load-bearing use: protected systems can treat every boundary crossing as an operation that either carries acceptable proof/policy binding or is rejected, which pressures DelayBasin toward explicit procedural admission.

- `REF-0040` — Zhang et al., **Adaptive Memory Admission Control for LLM Agents** (2026-03-04)
  - URL: https://arxiv.org/html/2603.04549v1
  - Load-bearing use: explicit and interpretable admission control, with content-type prior as a major factor, pressures DelayBasin toward governed canon promotion rather than indiscriminate retention.

- `REF-0041` — Gilda & Gilda, **AI-Assisted Engineering Should Track the Epistemic Status and Temporal Validity of Architectural Decisions** (2026-01-28)
  - URL: https://arxiv.org/html/2601.21116v1
  - Load-bearing use: argues for epistemic layers, conservative trust aggregation, and evidence-decay tracking, which directly support staged ratification and demotion triggers for archive canon.

- `REF-0042` — Romanchuk & Bondar, **Semantic Laundering in AI Agent Architectures: Why Tool Boundaries Do Not Confer Epistemic Warrant** (2026-01-13)
  - URL: https://arxiv.org/html/2601.08333v1
  - Load-bearing use: warns that trusted interfaces can launder weak warrant into accepted status, which pressures DelayBasin to preserve promotion contracts explicitly rather than trusting prose that crossed a familiar boundary.

- `REF-0043` — Lee et al., **A Structured Approach to Safety Case Construction for AI Systems** (2026-01-31)
  - URL: https://arxiv.org/html/2601.22773v2
  - Load-bearing use: separates claims, argument types, and evidence families, which supports keeping canon promotion explicit about what kind of evidence is carrying trust.


- `REF-0044` — Lu et al., **MMA: Multimodal Memory Agent** (2026-02-18)
  - URL: https://arxiv.org/abs/2602.16493
  - Load-bearing use: retrieved memories can be scored by source credibility, temporal decay, and conflict-aware consensus, which supports canon-level trust cooling rather than indefinite persistence.

- `REF-0045` — Logan, **Continuum Memory Architectures for Long-Horizon LLM Agents** (2026-01-14)
  - URL: https://arxiv.org/html/2601.09913v1
  - Load-bearing use: long-horizon memory should be able to persist, mutate, decay, and consolidate; indefinite read-only persistence is structurally under-specified.

- `REF-0046` — Kumar et al., **Towards a Science of AI Agent Reliability** (2026-02-18)
  - URL: https://arxiv.org/html/2602.16666v1
  - Load-bearing use: consistency, robustness, predictability, and safety pressure the archive to treat temporal drift as an operational reliability problem rather than only a note-taking problem.


- `REF-0047` — Bousetouane, **AI Agents Need Memory Control Over More Context** (2026-01-15)
  - URL: https://arxiv.org/html/2601.11653
  - Load-bearing use: long-horizon agents degrade under transcript replay, noisy recall, and memory-induced drift; bounded state updated online and separated from artifact recall supports the recovery-kernel idea.

- `REF-0048` — Markarian, **Algorithmic self-repair: frontiers in fault-tolerant computation** (2026-02-17)
  - URL: https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2026.1717711/full
  - Load-bearing use: self-stabilization is the canonical case of converging from arbitrary or corrupted states back to a legitimate configuration after transient faults, providing the right recovery metaphor and pressure for DelayBasin.

- `REF-0049` — Patlan et al., **Context manipulation attacks: Web agents are susceptible to corrupted memory** (2025-06-19)
  - URL: https://arxiv.org/html/2506.17318v1
  - Load-bearing use: persistent context can be corrupted through plan or memory injection, so long-horizon archives need an explicit recovery route rather than trusting persistent state by default.

- `REF-0050` — Wang et al., **ICON: Indirect Prompt Injection Defense for Agents based on Inference-Time Correction** (2026-02-26)
  - URL: https://arxiv.org/html/2602.20708
  - Load-bearing use: compromised trajectories can sometimes be detected and rectified while preserving task continuity, strengthening DelayBasin's weaker hypothesis that recovery may be a first-class continuation surface.


- `REF-0051` — Rasheed et al., **Claim-Level Auditability for Deep Research Agents** (2026-02-17)
  - URL: https://arxiv.org/html/2602.13855
  - Load-bearing use: argues that action logs and citations are structurally insufficient without compact claim-level evidence links, which pressures DelayBasin toward per-revision audit objects rather than prose-only changelog claims.

- `REF-0052` — Lee et al., **Constructing Safety Cases for AI Systems: A Reusable Template Framework** (2026-01-30)
  - URL: https://arxiv.org/abs/2601.22773
  - Load-bearing use: separates claims, argument types, and evidence families in reusable structured templates, which supports compact revision receipts that preserve why trust shifted.

- `REF-0053` — Rajagopalan & Rao, **Authenticated Workflows: A Systems Approach to Protecting Agentic AI** (2026-02-11)
  - URL: https://arxiv.org/abs/2602.10465
  - Load-bearing use: treats boundary crossings as operations that must carry acceptable policy/integrity binding or be rejected, supporting revision receipts as per-transition admission objects.

- `REF-0054` — dos Santos Filho, **ESAA: Event Sourcing for Autonomous Agents in LLM-Based Software Engineering** (2026-02-26)
  - URL: https://arxiv.org/abs/2602.23193
  - Load-bearing use: long-horizon agent systems benefit from immutable, auditable transition records and replayable materialized views, supporting compact revision receipts as a minimal event-like audit object.


- `REF-0055` — Lee, **Capable but Unreliable: Canonical Path Deviation as a Causal Mechanism of Agent Failure in Long-Horizon Tasks** (2026-02-21)
  - URL: https://arxiv.org/html/2602.19008v1
  - Load-bearing use: successful and failed runs of the same capable agent diverge through gradual, self-reinforcing off-canonical drift, which pressures DelayBasin to preserve a small local decision boundary rather than only the winning path.

- `REF-0056` — Chang, **Directional Reasoning Trajectory Change (DRTC): Identifying Critical Trace Segments in Reasoning Models** (2026-02-27)
  - URL: https://arxiv.org/abs/2602.15332
  - Load-bearing use: specific context spans can causally steer on-policy reasoning trajectories, which supports preserving the pivot surface where a nearby archive alternative was rejected.

- `REF-0057` — Ojewale et al., **Audit Trails for Accountability in Large Language Models** (2026-01-28)
  - URL: https://arxiv.org/html/2601.20727v1
  - Load-bearing use: accountability improves when change history records what changed, why, and who/what authorized it; DelayBasin extends that pressure to preserving one nearby rejected alternative for substantial revisions.

- `REF-0058` — Rabanser et al., **Towards a Science of AI Agent Reliability** (2026-02-18)
  - URL: https://arxiv.org/html/2602.16666v1
  - Load-bearing use: aggregate success obscures operational failure structure, which supports keeping revision honesty at the level of procedure and local alternatives rather than only outcome summaries.


- `REF-0059` — Saurez et al., **Why Linear Interpretability Works: Invariant Subspaces as a Result of Architectural Constraints** (2026-02-10)
  - URL: https://arxiv.org/abs/2602.09783
  - Load-bearing use: communicable features decoded through transformer linear interfaces must occupy context-invariant subspaces, which makes low-dimensional regime selectors more plausible than pure prose mysticism.

- `REF-0060` — Schiffman, **Transformers converge to invariant algorithmic cores** (2026-02-26)
  - URL: https://arxiv.org/abs/2602.22600
  - Load-bearing use: independently trained transformers can share compact subspaces that are necessary and sufficient for task performance, which strengthens DelayBasin's suspicion that small public control packets may re-enter low-dimensional operative modes.

- `REF-0061` — Venkatesh & Kurapath, **On the Identifiability of Steering Vectors in Large Language Models** (2026-02-06)
  - URL: https://arxiv.org/abs/2602.06801
  - Load-bearing use: behavior alone does not uniquely identify steering directions without stronger structural assumptions, which pressures DelayBasin to keep regime claims paired with countermodels and probe discipline.

- `REF-0062` — Fonseca Rivera & Africa, **Steering Awareness: Models Can Be Trained to Detect Activation Steering** (2026-03-04)
  - URL: https://arxiv.org/abs/2511.21399
  - Load-bearing use: control interventions can become detectable without becoming robust, which sharpens DelayBasin's rival explanation that archive continuity may sometimes be compliance with a recognized control surface rather than deep regime reconstruction.


- `REF-0063` — Akram et al., **Transformers as Implicit State Estimators: In-Context Learning in Dynamical Systems** (2024-10-22)
  - URL: https://arxiv.org/abs/2410.16546
  - Load-bearing use: supports the idea that transformers can reconstruct latent state from short context in inference, which makes a public hidden-state packet more plausible than pure replay.

- `REF-0064` — Scetbon et al., **Learning without training: The implicit dynamics of in-context learning** (2025-12-22)
  - URL: https://arxiv.org/abs/2507.16003
  - Load-bearing use: argues that context can act like a low-rank update to downstream network weights, strengthening the idea that archive packets may temporarily reconfigure operative control state rather than just remind.

- `REF-0065` — Wang et al., **Memex(RL): Scaling Long-Horizon LLM Agents via Indexed Experience Memory** (2026-03-05)
  - URL: https://arxiv.org/abs/2603.04257
  - Load-bearing use: shows a live systems pattern where long traces are rewritten into compact indexed summaries plus exact dereference, supporting DelayBasin's state/evidence split.

- `REF-0066` — Liu et al., **LoCoEval: A Scalable Benchmark for Repository-Oriented Long-Horizon Conversational Context Management** (2026-03-06)
  - URL: https://arxiv.org/abs/2603.06358
  - Load-bearing use: repository-oriented long-horizon conversations remain hard even for dedicated context methods, which pressures DelayBasin to keep repo-native state, evidence, and retrieval distinctions explicit.

- `REF-0067` — Huang et al., **Text2Mem: A Unified Memory Operation Language for Memory Operating System** (2025-10-23)
  - URL: https://arxiv.org/abs/2509.11145
  - Load-bearing use: typed, schema-validated memory operations suggest the broader ecosystem is also moving toward explicit, portable control interfaces instead of undifferentiated memory prose.


- `REF-0068` — Zhang et al., **Bayesian Optimality of In-Context Learning with Selective State Spaces** (2026-02-23)
  - URL: https://arxiv.org/abs/2602.17744
  - Load-bearing use: sharpens DelayBasin toward a belief-state frame by contrasting stateful selective-SSM filtering with a stateless Transformer-as-ERM baseline on latent-state tasks.

- `REF-0069` — Zhmoginov et al., **Contextually Guided Transformers via Low-Rank Adaptation** (2025-06-06)
  - URL: https://arxiv.org/abs/2506.05672
  - Load-bearing use: context can be summarized into weight modulation that specializes the model for the remainder of a sequence, which supports DelayBasin's adapter-like continuation speculation.

- `REF-0070` — Charakorn et al., **Doc-to-LoRA: Learning to Instantly Internalize Contexts** (2026-02-13)
  - URL: https://arxiv.org/abs/2602.15902
  - Load-bearing use: a single forward pass can map context into a context-specific LoRA adapter, making “public state packet as temporary model specialization” a live transformer-facing analogy.

- `REF-0071` — Liu et al., **SHINE: A Scalable In-Context Hypernetwork for Mapping Context to LoRA in a Single Pass** (2026-02-06)
  - URL: https://arxiv.org/abs/2602.06358
  - Load-bearing use: natural-language context can be transformed into high-quality LoRA adapters without direct re-access to the original context, strengthening DelayBasin's fast-adaptation analogy.

- `REF-0072` — Shchendrigin et al., **Memory Retention Is Not Enough to Master Memory Tasks in Reinforcement Learning** (2026-01-21)
  - URL: https://arxiv.org/abs/2601.15086
  - Load-bearing use: argues that adaptive rewriting under partial observability is a distinct requirement from retention, which supports DelayBasin's belief-state framing over a pure memory-dump framing.

- `REF-0073` — Cheng et al., **LifeBench: A Benchmark for Long-Horizon Multi-Source Memory** (2026-03-04)
  - URL: https://arxiv.org/abs/2603.03781
  - Load-bearing use: long-horizon memory tasks require integrating declarative and non-declarative traces, which pressures DelayBasin to preserve something richer than factual recall alone.

- `REF-0074` — Tang et al., **Canvas-of-Thought: Grounding Reasoning via Mutable Structured States** (2026-02-11)
  - URL: https://arxiv.org/abs/2602.10494
  - Load-bearing use: mutable external state can support targeted state revision better than linear replay, which supports DelayBasin's preference for typed updateable state over blended recap.

- `REF-0075` — Ercetin & Chraiti, **Predictive-State Communication: Innovation Coding and Reconciliation under Delay** (2026-02-11)
  - URL: https://arxiv.org/abs/2602.10542
  - Load-bearing use: provides the cleanest outside-the-archive pressure for treating mature revisions as anchored innovations against shared predictive state, with state identifiers, anchors, bounded rollback, and patch-based updates.

- `REF-0076` — dos Santos Filho, **ESAA: Event Sourcing for Autonomous Agents in LLM-Based Software Engineering** (2026-02-26)
  - URL: https://arxiv.org/abs/2602.23193
  - Load-bearing use: argues that agents should consume a purified projected view from an event log rather than raw long-horizon prompt mass, which supports DelayBasin's preference for compact projected state and local deltas.

- `REF-0077` — Sun et al., **Canvas-of-Thought: Grounding Reasoning via Mutable Structured States** (2026-02-11)
  - URL: https://arxiv.org/abs/2602.10494
  - Load-bearing use: shows why immutable reasoning streams make local correction expensive and why explicit mutable state can support cheaper, more local revisions.

- `REF-0078` — Liu et al., **The Pensieve Paradigm: Stateful Language Models Mastering Their Own Context** (2026-02-12)
  - URL: https://arxiv.org/abs/2602.12108
  - Load-bearing use: treats context pruning, indexing, and note-taking as learned state-management operations, which reinforces that archive-state engineering is a real systems variable rather than mere human ritual.

- `REF-0079` — Zhu et al., **What Should Embeddings Embed? Autoregressive Models Represent Latent Generating Distributions** (2024-06-06)
  - URL: https://arxiv.org/abs/2406.03707
  - Load-bearing use: argues that autoregressive embeddings can encode predictive sufficient statistics or posterior distributions over latent state, which supports DelayBasin's search for a compact public packet smaller than raw history.

- `REF-0080` — Lepori et al., **Language Models Struggle to Use Representations Learned In-Context** (2026-02-04)
  - URL: https://arxiv.org/abs/2602.04212
  - Load-bearing use: provides counterpressure by showing that inducing in-context representations is not enough; models may still struggle to deploy them reliably for downstream tasks.

- `REF-0081` — Wang et al., **Data Distribution Matters: A Data-Centric Perspective on Context Compression for Large Language Model** (2026-02-02)
  - URL: https://arxiv.org/abs/2602.01778
  - Load-bearing use: argues that compression quality depends strongly on input entropy, decoder priors, and encoder/decoder distribution mismatch, which sharpens DelayBasin's need to track model mismatch rather than assuming summarization quality alone determines fidelity.

- `REF-0082` — Wang et al., **Context Compression via Explicit Information Transmission** (2026-02-03)
  - URL: https://arxiv.org/abs/2602.03784
  - Load-bearing use: argues that compression improves when information is explicitly transmitted into coordinated anchor slots instead of being left to progressive overwriting, supporting DelayBasin's emphasis on typed anchor and check surfaces.

- `REF-0083` — Guo et al., **When Less is More: The LLM Scaling Paradox in Context Compression** (2026-02-10)
  - URL: https://arxiv.org/abs/2602.09789
  - Load-bearing use: larger compressors can introduce knowledge overwriting and semantic drift under lossy compression, which maps directly onto DelayBasin's fear of elegant recap that quietly rewrites canon.

- `REF-0084` — Millege et al., **Why the Brain Consolidates: Predictive Forgetting for Optimal Generalisation** (2026-03-05)
  - URL: https://arxiv.org/abs/2603.04688
  - Load-bearing use: argues that high-fidelity online encodings can preserve nuisance detail and that compression should be judged by predictive sufficiency rather than input fidelity alone, which pressures DelayBasin to define its distortion target more carefully than recap quality.

- `REF-0085` — Tao et al., **Verifier-Bound Communication for LLM Agents: Certified Bounds on Covert Signaling** (2026-02-27)
  - URL: https://arxiv.org/abs/2603.00381
  - Load-bearing use: state should advance only through deterministic admission predicates when claims about secure or faithful communication matter, supporting DelayBasin's hygiene move toward explicit compression/distortion contracts rather than post-hoc prose confidence.


- `REF-0086` — Pillutla et al., **Filtering Beats Fine-Tuning: A Bayesian Kalman View of In-Context Learning in LLMs** (2026-01-02)
  - URL: https://arxiv.org/abs/2601.06100
  - Load-bearing use: treats in-context adaptation as latent-state filtering with posterior covariance and process uncertainty, which pressures DelayBasin to preserve not only state content but how strongly new evidence should move it.

- `REF-0087` — Shaj et al., **Kalman Linear Attention: Parallel Bayesian Filtering for Efficient Language Modelling and State Tracking** (2026-02-14)
  - URL: https://arxiv.org/abs/2602.10743
  - Load-bearing use: frames tokens as noisy measurements of a latent semantic state, which supports DelayBasin's use of public belief-state and update-gain language rather than pure recap talk.

- `REF-0088` — Mei et al., **Gated Differentiable Working Memory for Long-Context Language Modeling** (2026-01-22)
  - URL: https://arxiv.org/abs/2601.12906
  - Load-bearing use: models test-time adaptation as a budget-constrained write problem with a utility-sensitive controller, which supports DelayBasin's push toward explicit revision-force discipline instead of uniform rewrite pressure.

- `REF-0089` — Chauvin et al., **“I May Not Have Articulated Myself Clearly”: Diagnosing Dynamic Instability in LLM Reasoning at Inference Time** (2026-02-02)
  - URL: https://arxiv.org/abs/2602.02863
  - Load-bearing use: early instability can be corrective while late instability is often destructive, which pressures DelayBasin to reason about when and how strongly a revision should move belief.

- `REF-0090` — Behrouz et al., **Titans: Learning to Memorize at Test Time** (2024-12-31)
  - URL: https://arxiv.org/abs/2501.00663
  - Load-bearing use: introduces surprise-weighted test-time memory updates, which gives DelayBasin a plausible transformer-facing analogue for why some revisions should write harder than others.

- `REF-0091` — Millege et al., **Why the Brain Consolidates: Predictive Forgetting for Optimal Generalisation** (2026-03-05)
  - URL: https://arxiv.org/abs/2603.04688
  - Load-bearing use: argues that surprising episodes should receive stronger consolidation pressure, which supports DelayBasin's milder user-space notion of surprise-gated revision without proving it.

- `REF-0092` — Song et al., **Certainty robustness: Evaluating LLM stability under self-challenging prompts** (2026-02-10)
  - URL: https://arxiv.org/abs/2603.03330
  - Load-bearing use: distinguishes justified self-correction from unjustified answer changes under challenge, which supports keeping a compact challenge-probe surface alongside belief updates.

- `REF-0093` — Chauvin et al., **Token-Efficient Change Detection in LLM APIs** (2026-02-11)
  - URL: https://arxiv.org/abs/2602.11083
  - Load-bearing use: small numbers of sensitive border probes can reveal hard-to-see model changes, which supports DelayBasin's instinct that a few compact challenge probes may outperform broad generic checking.


- `REF-0094` — Chu et al., **Optimizing In-Context Demonstrations for LLM-based Automated Grading** (2026-02-28)
  - URL: https://arxiv.org/abs/2603.00465
  - Load-bearing use: boundary-focused exemplar optimization and contrastive boundary pairs support DelayBasin's idea that a tiny discriminative witness panel may outperform similarity-first recap examples.

- `REF-0095` — Wang & Jia, **Meta-Sel: Efficient Demonstration Selection for In-Context Learning via Supervised Meta-Learning** (2026-02-12)
  - URL: https://arxiv.org/abs/2602.12123
  - Load-bearing use: under tight prompt budgets, example choice matters sharply and can be made deterministic and auditable, which pressures DelayBasin to allocate scarce witness slots explicitly.

- `REF-0096` — Todd et al., **Function Vectors in Large Language Models** (2023-10-23)
  - URL: https://arxiv.org/abs/2310.15213
  - Load-bearing use: compact function representations with causal downstream effects make it more plausible that a tiny witness set could disproportionately shape continuation behavior.

- `REF-0097` — Hendel et al., **In-Context Learning Creates Task Vectors** (2023-10-24)
  - URL: https://arxiv.org/abs/2310.15916
  - Load-bearing use: a few demonstrations can compress into a single task vector, which supports DelayBasin's search for tiny boundary objects that pin a continuation regime.

- `REF-0098` — Gundem et al., **Boosting In-Context Learning in LLMs Through the Lens of Classical Supervised Learning** (2025-05-22)
  - URL: https://arxiv.org/abs/2505.23783
  - Load-bearing use: many interventions merely shift a decision boundary without rotating it, which is useful counterpressure against treating any witness panel as automatically sufficient or mechanistically deep.



- `REF-0099` — Goren et al., **When Should LLMs Be Less Specific? Selective Abstraction for Reliable Long-Form Text Generation** (2026-02-17)
  - URL: https://arxiv.org/abs/2602.11908
  - Load-bearing use: supports DelayBasin's idea that uncertain mechanism language sometimes should be deliberately abstracted rather than either asserted or deleted.

- `REF-0100` — Wang et al., **Are LLM Decisions Faithful to Verbal Confidence?** (2026-01-12)
  - URL: https://arxiv.org/abs/2601.07767
  - Load-bearing use: shows that verbal confidence can dissociate from actual abstention behavior, which pressures DelayBasin to preserve explicit public hold contracts rather than trust self-described uncertainty.

- `REF-0101` — Madhwal et al., **Decomposed Prompting Does Not Fix Knowledge Gaps, But Helps Models Say "I Don't Know"** (2026-02-04)
  - URL: https://arxiv.org/abs/2602.04853
  - Load-bearing use: cross-prompt disagreement can trigger training-free abstention, which supports DelayBasin's idea that compact probes may justify public non-movement better than confidence prose alone.

- `REF-0102` — Xuan et al., **The Confidence Dichotomy: Analyzing and Mitigating Miscalibration in Tool-Use Agents** (2026-01-13)
  - URL: https://arxiv.org/abs/2601.07264
  - Load-bearing use: evidence tools such as web search can induce stronger overconfidence than deterministic verification tools, which sharpens DelayBasin's need to separate research pressure from verification pressure before moving canon.

- `REF-0103` — Jülich, **Upholding Epistemic Agency: A Brouwerian Assertibility Constraint for Responsible AI** (2026-03-04)
  - URL: https://arxiv.org/abs/2603.03971
  - Load-bearing use: public interfaces may need an explicit third state such as `Undetermined` when no public entitlement certificate exists, which supports DelayBasin's hold-packet / brake discipline.

- `REF-0104` — Akter et al., **Anytime-Valid Answer Sufficiency Certificates for LLM Generation via Sequential Information Lift** (2026-01-05)
  - URL: https://arxiv.org/abs/2510.06478
  - Load-bearing use: information-sufficiency stopping can be formalized without guaranteeing correctness, which pressures DelayBasin to instrument non-movement and verification separately rather than collapse them into one confidence story.

- `REF-0105` — Rabanser et al., **Towards a Science of AI Agent Reliability** (2026-02-18)
  - URL: https://arxiv.org/abs/2602.16666
  - Load-bearing use: reliability evaluation benefits from explicit abstention metrics and prompt-robustness analysis, which supports DelayBasin's idea that public non-movement deserves its own compact audit surface.


- `REF-0107` — Huang et al., **ProbeLLM: Automating Principled Diagnosis of LLM Failures** (2026-02-13)
  - URL: https://arxiv.org/abs/2602.12966
  - Load-bearing use: failure discovery becomes more useful when clustered into representative central and contrastive boundary cases, which pressures DelayBasin to design sentinel panels as compact local decision-surface summaries rather than arbitrary spot checks.

- `REF-0108` — Yoa et al., **From Static Benchmarks to Dynamic Protocol: Agent-Centric Text Anomaly Detection for Evaluating LLM Reasoning** (2026-02-27)
  - URL: https://arxiv.org/abs/2602.23729
  - Load-bearing use: evolving diagnostic protocols expose subtle corner-case failures that static benchmark sets miss, which supports DelayBasin's idea that sentinel panels may need recertification or co-evolution rather than eternal fixed canaries.

- `REF-0109` — Kim et al., **Understanding the Dynamics of Demonstration Conflict in In-Context Learning** (2026-03-06)
  - URL: https://arxiv.org/abs/2603.04464
  - Load-bearing use: models can encode both correct and corrupted rules before committing late, which supports DelayBasin's preference for boundary-near canaries that catch wrong-basin reconstruction before fluent continuation hardens.

- `REF-0110` — Cox et al., **Decoding Answers Before Chain-of-Thought: Evidence from Pre-CoT Probes and Activation Steering** (2026-03-02)
  - URL: https://arxiv.org/abs/2603.01437
  - Load-bearing use: fluent reasoning can arrive after a latent answer is already set, which is counterpressure against trusting articulate continuation as evidence that the right basin was reconstructed.

- `REF-0111` — Liu et al., **TrajAD: Trajectory Anomaly Detection for Trustworthy LLM Agents** (2026-02-09)
  - URL: https://arxiv.org/abs/2602.06443
  - Load-bearing use: anomaly detection is most useful when it localizes the problem step and triggers rollback rather than only scoring final success, which supports DelayBasin's notion of sentinels as early-warning devices tied to rollback/resync choices.


- `REF-0112` — Qu, **Active Epistemic Control for Query-Efficient Verified Planning** (2026-02-03)
  - URL: https://arxiv.org/abs/2602.03974
  - Load-bearing use: separates hypothesis pruning from grounded commitment and chooses when missing facts should actually be queried, which pressures DelayBasin toward explicit identification packets rather than unstructured extra research.

- `REF-0113` — Sapunov, **Theory of Code Space: Do Code Agents Understand Software Architecture?** (2026-02-28)
  - URL: https://arxiv.org/abs/2603.00601
  - Load-bearing use: treats code understanding as belief construction under partial observability with periodic structured externalization, which pressures DelayBasin to separate passive handoff text from active identification moves.

- `REF-0114` — Zhang et al., **Theory of Space: Can Foundation Models Construct Spatial Beliefs through Active Exploration?** (2026-02-04)
  - URL: https://arxiv.org/abs/2602.07055
  - Load-bearing use: exposes an active–passive gap and belief instability under exploration, which supports DelayBasin's idea that some archive moves should actively identify state rather than only summarize it.

- `REF-0115` — Cui et al., **Game of Thought: Robust Information Seeking with Large Language Models Using Game Theory** (2026-02-02)
  - URL: https://arxiv.org/abs/2602.01708
  - Load-bearing use: worst-case information seeking improves when questions are chosen for discrimination under adversarial uncertainty, which supports DelayBasin's identification-packet lane.

- `REF-0116` — Zou et al., **Reducing Belief Deviation in Reinforcement Learning for Active Reasoning** (2025-10-14)
  - URL: https://arxiv.org/abs/2510.12264
  - Load-bearing use: once belief drifts, later actions become repetitive and misleading, which pressures DelayBasin to spend earlier moves on disambiguation instead of accumulating articulate but low-information tails.

- `REF-0117` — Zhang et al., **Agentic Uncertainty Quantification** (2026-01-22)
  - URL: https://arxiv.org/abs/2601.15703
  - Load-bearing use: treats uncertainty as a cue for targeted information seeking and tool choice rather than post-hoc confession, which supports DelayBasin's move from uncertainty prose to observation-seeking identification packets.

- `REF-0118` — Zhang et al., **From Passive Metric to Active Signal: The Evolving Role of Uncertainty Quantification in Large Language Models** (2026-01-22)
  - URL: https://arxiv.org/abs/2601.15690
  - Load-bearing use: surveys uncertainty as an active control signal for reasoning and agents, which supports DelayBasin's idea that some revisions should be selected for diagnostic value rather than only content addition.

- `REF-0119` — Huang et al., **On the Failure of Latent State Persistence in Large Language Models** (2025-04-30)
  - URL: https://arxiv.org/abs/2505.10571
  - Load-bearing use: strong counterpressure that transformers may lack durable latent state persistence, which keeps DelayBasin's stronger observability-map story in quarantine while still motivating external identification scaffolds.


- `REF-0120` — Dorovatas et al., **Modular Memory is the Key to Continual Learning Agents** (2026-03-02)
  - URL: https://arxiv.org/abs/2603.01761
  - Load-bearing use: argues for distinct working-memory and long-term-memory modules with updates across multiple timescales, which directly pressures DelayBasin to name fast versus slow archive lanes instead of treating all public state as one memory store.

- `REF-0121` — Oomerjee et al., **Bottlenecked Transformers: Periodic KV Cache Consolidation for Generalised Reasoning** (2025-05-22)
  - URL: https://arxiv.org/abs/2505.16950
  - Load-bearing use: periodic KV consolidation can improve long-chain reasoning, which supports DelayBasin's milder claim that some archive surfaces should refresh or consolidate at explicit boundaries rather than only accumulate.

- `REF-0122` — Bonnet et al., **Learning to Remember, Learn, and Forget in Attention-Based Models** (2026-02-09)
  - URL: https://arxiv.org/abs/2602.09075
  - Load-bearing use: frames sequence models as continual learners facing a stability–plasticity dilemma and introduces Bayesian metaplasticity, which sharpens DelayBasin's transformer-facing intuition that different public surfaces may need different rewrite resistance.

- `REF-0123` — Li et al., **Latent Context Compilation: Distilling Long Context into Compact Portable Memory** (2026-01-31)
  - URL: https://arxiv.org/abs/2602.21221
  - Load-bearing use: compiles long context into portable memory artifacts without changing base weights, which pressures DelayBasin to distinguish compact portable state from slower backing evidence and constitutional scaffolds.

- `REF-0124` — Pulipaka et al., **PersistBench: When Should Long-Term Memories Be Forgotten by LLMs?** (2026-02-01)
  - URL: https://arxiv.org/abs/2602.01146
  - Load-bearing use: persistent long-term memory can induce cross-domain leakage and sycophancy, which is strong counterpressure against letting every useful local archive object consolidate upward by default.

- `REF-0125` — Tavakoli et al., **Beyond a Million Tokens: Benchmarking and Enhancing Long-Term Memory in LLMs** (2025-10-31)
  - URL: https://arxiv.org/abs/2510.27246
  - Load-bearing use: separates working memory, episodic memory, and scratchpad-like accumulation, which supports DelayBasin's need for an explicit fast/medium/slow lane map instead of one undifferentiated handoff surface.

- `REF-0126` — Belcamino et al., **Factored Reasoning with Inner Speech and Persistent Memory for Evidence-Grounded Human-Robot Interaction** (2026-01-31)
  - URL: https://arxiv.org/abs/2602.00675
  - Load-bearing use: explicitly selects what to consolidate at different timescales with managed update policies, which supports DelayBasin's move from persistence-as-storage toward persistence-as-organized controlled revision.

- `REF-0127` — Rath, **Agent Drift: Quantifying Behavioral Degradation in Multi-Agent LLM Systems Over Extended Interactions** (2026-01-07)
  - URL: https://arxiv.org/abs/2601.04170
  - Load-bearing use: argues that episodic consolidation and adaptive anchoring can mitigate long-horizon drift, which pressures DelayBasin to give fast-lane objects explicit consolidation, refresh, or expiry routes.



- `REF-0128` — Zou et al., **ES-Mem: Event Segmentation-Based Memory for Long-Term Dialogue Agents** (2026-01-12)
  - URL: https://arxiv.org/abs/2601.07582
  - Load-bearing use: dynamic event segmentation and refined boundary representations improve long-horizon dialogue memory by using event boundaries as retrieval anchors, which pressures DelayBasin to preserve explicit boundary objects rather than only summaries.

- `REF-0129` — Wang et al., **Human-inspired Episodic Memory for Infinite Context LLMs** (2024-07-12 / rev. 2025-10-10)
  - URL: https://arxiv.org/abs/2407.09450
  - Load-bearing use: segments long context into event units using surprise and cohesion/separation refinement, which supports DelayBasin's milder claim that some archive transitions may deserve explicit event cuts rather than ever-smoother recap.

- `REF-0130` — Song et al., **Towards Compressive and Scalable Recurrent Memory** (2026-02-11)
  - URL: https://arxiv.org/abs/2602.11212
  - Load-bearing use: recurrent-memory architectures pass compact state across segment boundaries to seed the next block, which supports the transformer-facing analogy that public rollover packets may matter at explicit boundaries rather than in one seamless stream.

- `REF-0131` — Ravichander et al., **Learning Physical Principles from Interaction: Self-Evolving Planning via Test-Time Memory** (2026-02-25)
  - URL: https://arxiv.org/abs/2602.20323
  - Load-bearing use: surprise-triggered consolidation, targeted verification, and memory folding outperform indiscriminate retention, which pressures DelayBasin to fold exploratory episodes into compact carry-forward packets at real phase boundaries.

- `REF-0132` — Zhang et al., **Learning to Remember: End-to-End Training of Memory Agents for Long-Context Reasoning** (2026-02-11)
  - URL: https://arxiv.org/abs/2602.18493
  - Load-bearing use: explicit create/update/delete/reorganize memory operations outperform passive replay on dynamic state tracking, which supports treating a rollover packet as a public reorganization act rather than only a nicer summary.

- `REF-0133` — Feng et al., **Rethinking Memory Mechanisms of Foundation Agents in the Era of Generative AI: A Survey** (2026-02-12)
  - URL: https://arxiv.org/abs/2602.06052
  - Load-bearing use: episode-boundary definition and regulation of episodic recall remain open problems, which keeps DelayBasin honest about the current limits of any phase-boundary discipline.


- `REF-0134` — Venkatesh et al., **On the Non-Identifiability of Steering Vectors in Large Language Models** (2026-03-05)
  - URL: https://arxiv.org/abs/2602.06801
  - Load-bearing use: geometrically distinct steering directions can be behaviorally equivalent because of null-space ambiguity and gauge-like reparameterization symmetries, which pressures DelayBasin not to treat one recovered vector or chart as uniquely mechanistic.

- `REF-0135` — Joshi et al., **Causality is Key for Interpretability Claims to Generalise** (2026-02-24)
  - URL: https://arxiv.org/abs/2602.16698
  - Load-bearing use: interpretability claims should target invariant high-level structures justified by causal evidence, which pressures DelayBasin to state what survives chart changes rather than rely on local associations alone.

- `REF-0136` — Schiffman et al., **Transformers Converge to Invariant Algorithmic Cores** (2026-02-28)
  - URL: https://arxiv.org/abs/2602.22600
  - Load-bearing use: cores aligned in canonical coordinates can remain necessary and sufficient while naive full-model alignment only surfaces shared variance, which supports DelayBasin's distinction between a useful canonical chart and cosmetic alignment.

- `REF-0137` — Sevetlidis and Pavlidis, **Gauge-invariant Representation Holonomy** (2026-01-29)
  - URL: https://arxiv.org/abs/2601.21653
  - Load-bearing use: gauge-invariant diagnostics can reveal pathwise geometry missed by pointwise similarity, which pressures DelayBasin to preserve invariant observables rather than over-credit one coordinate presentation.

- `REF-0138` — Sun et al., **Toward Manifest Relationality in Transformers via Symmetry Reduction** (2026-02-21)
  - URL: https://arxiv.org/abs/2602.18948
  - Load-bearing use: transformer analysis can be reformulated in invariant relational quantities rather than arbitrary coordinate descriptions, which supports DelayBasin's milder claim that canon should preserve relational or operational substance before chart language.

- `REF-0139` — Zhou et al., **Rethinking Diffusion Models with Symmetries through Canonicalization with Applications to Molecular Graph Generation** (2026-02-20)
  - URL: https://arxiv.org/abs/2602.15022
  - Load-bearing use: canonicalization can remove a symmetry-ambiguity variance term without solving all residual difficulty, which supports a disciplined role for canonical charts in DelayBasin rather than magical certainty.

- `REF-0140` — Nielsen and Liang, **Logit Distance Bounds Representational Similarity** (2026-02-18)
  - URL: https://arxiv.org/abs/2602.15438
  - Load-bearing use: functional equivalence constrains representations only up to an identifiability class under invertible transforms, which sharpens DelayBasin's need to distinguish invariant substance from chart-specific coordinate choice.



- `REF-0141` — Grover et al., **Text Has Curvature** (2026-02-13)
  - URL: https://arxiv.org/abs/2602.13418
  - Load-bearing use: natural text violates path-order-independence flatness nulls, which pressures DelayBasin not to assume reordered evidence or local chart changes preserve the same continuation law by default.

- `REF-0142` — Javidnia, **A Gauge Theory of Superposition: Toward a Sheaf-Theoretic Atlas of Neural Representations** (2026-02-28)
  - URL: https://arxiv.org/abs/2603.00824
  - Load-bearing use: chart-graph transports, chord defects, and loop-accumulation bounds make path dependence operational rather than purely metaphorical, which sharpens DelayBasin's interest in tiny public loop-closure probes.

- `REF-0143` — Chang, **Directional Reasoning Trajectory Change (DRTC): Identifying Critical Trace Segments in Reasoning Models** (2026-02-17)
  - URL: https://arxiv.org/abs/2602.15332
  - Load-bearing use: once a reasoning trajectory commits to a line of thought, later continuation is path-dependent and off-policy edits become hard to interpret, which pressures DelayBasin not to treat route changes as free.

- `REF-0144` — Guan et al., **The Order Effect: Investigating Prompt Sensitivity to Input Order in LLMs** (2025-02-06 / rev. 2025-05-09)
  - URL: https://arxiv.org/abs/2502.04134
  - Load-bearing use: measurable order sensitivity across multiple tasks is practical pressure for explicit commutator tests whenever DelayBasin is implicitly assuming a harmless reorder.

- `REF-0145` — Pecher et al., **Revisiting Prompt Sensitivity in Large Language Models for Text Classification: The Role of Prompt Underspecification** (2026-02-04)
  - URL: https://arxiv.org/abs/2602.04297
  - Load-bearing use: some apparent prompt/path sensitivity stems from underspecification and may emerge mainly in final layers, which is counterpressure against overinterpreting every closure defect as deep continuation geometry.

- `REF-0146` — Graham et al., **ContextBench: Modifying Contexts for Targeted Latent Activation** (2025-06-15 / ICLR 2026)
  - URL: https://arxiv.org/abs/2506.15735
  - Load-bearing use: small fluent context modifications can disproportionately elicit latent features or behaviors, which pressures DelayBasin to take local route changes seriously as potential operative-state interventions.

- `REF-0147` — Liu et al., **Beyond Confidence: The Rhythms of Reasoning in Generative Models** (2026-02-11)
  - URL: https://arxiv.org/abs/2602.10816
  - Load-bearing use: introduces the Token Constraint Bound (δTCB) as a local stability margin around a context-induced hidden state, which pressures DelayBasin to treat some archive objects as guard bands rather than only summaries.

- `REF-0148` — Dies et al., **Representational and Behavioral Stability of Truth in Large Language Models** (2025-11-24 / rev. 2026-01-19)
  - URL: https://arxiv.org/abs/2511.19166
  - Load-bearing use: controlled semantic reframing can retract apparently stable truth judgments, which is direct pressure for DelayBasin to name which perturbation families should stay inside the archive's trusted guard band.

- `REF-0149` — Zhang, **Provable Adversarial Robustness in In-Context Learning** (2026-02-19)
  - URL: https://arxiv.org/abs/2602.17743
  - Load-bearing use: robustness under distribution shift has explicit capacity and sample-complexity costs, which supports DelayBasin's idea that continuation margin is a resource-constrained budget rather than a free property of elegant wording.

- `REF-0150` — von Recum et al., **Are Reasoning LLMs Robust to Interventions on their Chain-of-Thought?** (2026-02-07)
  - URL: https://arxiv.org/abs/2602.07470
  - Load-bearing use: robustness is intervention-family-specific and not style-invariant, which pressures DelayBasin to preserve the perturbation family itself instead of speaking about one undifferentiated robustness claim.

- `REF-0151` — Aravindan and Kejriwal, **Fragile Thoughts: How Large Language Models Handle Chain-of-Thought Perturbations** (2026-02-11 / rev. 2026-03-06)
  - URL: https://arxiv.org/abs/2603.03332
  - Load-bearing use: different perturbation types remain differently damaging across scales, which supports DelayBasin's need to name which local changes are supposed to stay inside a claimed continuation margin.

- `REF-0152` — Agarwal et al., **Support Tokens, Stability Margins, and a New Foundation for Robust LLMs** (2026-02-25)
  - URL: https://arxiv.org/abs/2602.22271
  - Load-bearing use: interprets attention geometry in margin terms and introduces support-token language, which makes transformer-facing guard-band and basin-thickness talk less decorative and more mechanistically serious.



- `REF-0153` — Xu et al., **How Controllable Are Large Language Models? A Unified Evaluation across Behavioral Granularities** (2026-03-03)
  - URL: https://arxiv.org/abs/2603.02578
  - Load-bearing use: controllability often degrades as behavioral targets become finer-grained, which pressures DelayBasin not to over-credit a handle that only works at coarse continuation levels.

- `REF-0154` — Miehling et al., **Evaluating the Prompt Steerability of Large Language Models** (2024-11-19 / rev. 2025-02-15)
  - URL: https://arxiv.org/abs/2411.12405
  - Load-bearing use: defines steerability as change in behavioral profile as a function of steering effort and finds limited, asymmetric prompt steerability, which supports DelayBasin's need to track rough effort scale for archive handles.

- `REF-0155` — Yang et al., **Controllable Value Alignment in Large Language Models through Neuron-Level Editing** (2026-02-07)
  - URL: https://arxiv.org/abs/2602.07356
  - Load-bearing use: introduces value leakage as unintended activation of non-target properties during steering, which pressures DelayBasin to track collateral movement rather than only visible target success.

- `REF-0156` — Dang et al., **Selective Steering: Norm-Preserving Control Through Discriminative Layer Selection** (2026-01-24)
  - URL: https://arxiv.org/abs/2601.19375
  - Load-bearing use: steering authority is heterogeneous across layers and selective intervention can preserve general capability better, which supports DelayBasin's suspicion that some archive surfaces concentrate control more cleanly than others.

- `REF-0157` — Sharma and Trivedi, **COLD-Steer: Steering Large Language Models via In-Context One-step Learning Dynamics** (2026-03-07)
  - URL: https://arxiv.org/abs/2603.06495
  - Load-bearing use: approximating one-step in-context learning dynamics can achieve strong steering with far fewer examples, which pressures DelayBasin to take compact public actuators seriously as more than recap.

- `REF-0158` — Lindsey et al., **Endogenous Resistance to Activation Steering in Language Models** (2026-02-06)
  - URL: https://arxiv.org/abs/2602.06941
  - Load-bearing use: at least some models can detect and self-correct irrelevant steering, which supports DelayBasin's need to track endogenous resistance rather than only success/failure.

- `REF-0159` — Petty et al., **No More, No Less: Least-Privilege Language Models** (2026-01-30)
  - URL: https://arxiv.org/abs/2601.23157
  - Load-bearing use: inference-time control is naturally expressed as a privilege–utility frontier, which supports DelayBasin's actuation-budget framing rather than binary handle/no-handle talk.

- `REF-0160` — Li et al., **Steering Vector Fields for Context-Aware Inference-Time Control in Large Language Models** (2026-02-02)
  - URL: https://arxiv.org/abs/2602.01654
  - Load-bearing use: a static global steering direction can be weak or anti-steerable because locally effective control is context-dependent, which pressures DelayBasin to treat handle authority as region-specific rather than universally portable.

- `REF-0161` — Nayebi, **What Capable Agents Must Know: Selection Theorems for Robust Decision-Making under Uncertainty** (2026-03-04)
  - URL: https://arxiv.org/abs/2603.02491
  - Load-bearing use: robust action under partial observability requires predictive distinctions that separate high-margin outcomes, which pressures DelayBasin to preserve state surfaces with real diagnostic value rather than decorative recap.

- `REF-0162` — Menezes and Kyrillidis, **GHOST: Unmasking Phantom States in Mamba2 via Grouped Hidden-state Output-aware Selection and Truncation** (2026-02-11)
  - URL: https://arxiv.org/abs/2602.11408
  - Load-bearing use: approximating balanced truncation by jointly measuring controllability and observability supports DelayBasin's dual-salience idea that some bounded-state dimensions matter because they are good for both readout and actuation.

- `REF-0163` — Schiffman, **Transformers Converge to Invariant Algorithmic Cores** (2026-02-28)
  - URL: https://arxiv.org/abs/2602.22600
  - Load-bearing use: minimal realization and invariant algorithmic cores motivate treating archive-state selection as a search for the smallest continuation-preserving public state up to coordinate change rather than as tasteful summarization alone.

- `REF-0164` — Han and Voelker, **The Curious Case of In-Training Compression of State Space Models** (2026-02-24)
  - URL: https://arxiv.org/abs/2510.02823
  - Load-bearing use: improper truncation can cause losses models do not simply recover from, which pressures DelayBasin not to treat archive compression or surface demotion as casually reversible.

- `REF-0165` — Zhong et al., **When Control Meets Large Language Models: From Words to Dynamics** (2026-02-02)
  - URL: https://arxiv.org/abs/2602.03433
  - Load-bearing use: sequence modeling can be viewed as compressing context into smaller operative state with controllability, observability, stability, and gain scheduling as key axes, which sharpens the transformer-facing reading of DelayBasin's bounded-state choices.



- `REF-0166` — Anthropic, **Effective harnesses for long-running agents** (2025-11-26)
  - URL: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
  - Load-bearing use: compaction alone is insufficient for reliable cross-window continuation; a distinct initializer plus structured progress artifacts sharpen DelayBasin's distinction between generic persistence and regime re-entry.

- `REF-0167` — Anthropic, **Effective context engineering for AI agents** (2025-09-29)
  - URL: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - Load-bearing use: the practical objective is the smallest high-signal token set that induces the desired behavior under finite attention budget, which pressures DelayBasin to distinguish storage-rich memory from compact re-entry packets.

- `REF-0168` — Packer et al., **MemGPT: Towards LLMs as Operating Systems** (2023-10-12 / rev. 2024-02-12)
  - URL: https://arxiv.org/abs/2310.08560
  - Load-bearing use: frames long-horizon continuity as virtual context management across memory tiers, which gives DelayBasin a clean countermodel centered on storage/paging rather than regime-reentry law.

- `REF-0169` — LangChain, **Long-term memory** docs (accessed 2026-03-16)
  - URL: https://docs.langchain.com/oss/python/langchain/long-term-memory
  - Load-bearing use: long-term memory is implemented as JSON documents in stores under namespaces and keys, which sharpens DelayBasin's distinction between a persistent memory store and a smaller re-entry packet.

- `REF-0170` — LangChain, **LangMem** docs (accessed 2026-03-16)
  - URL: https://langchain-ai.github.io/langmem/
  - Load-bearing use: extractive memory, background consolidation, and prompt refinement show a mainstream memory stack centered on storage/update loops rather than the narrower problem of re-seeding a continuation regime with the smallest public packet.



- `REF-0171` — Singh, James, and Rudary, **Predictive State Representations: A New Theory for Modeling Dynamical Systems** (2012 / UAI 2004)
  - URL: https://arxiv.org/abs/1207.4167
  - Load-bearing use: defines state as predictions of observable outcomes of experiments one can do in the system, which sharpens DelayBasin's interest in compact public state chosen by future tests rather than hidden labels or recap prestige.

- `REF-0172` — Carvalho, Tomov, de Cothi, Barry, and Gershman, **Predictive representations: building blocks of intelligence** (2024-02-10 / rev. 2024-09-15)
  - URL: https://arxiv.org/abs/2402.06590
  - Load-bearing use: distinguishes predictive models from predictive representations that cache answers to certain task-relevant queries, which pressures DelayBasin to evaluate bounded packets by cheap future-query coverage rather than narrative completeness alone.

- `REF-0173` — Anthropic, **How we built our multi-agent research system** (2025-06-13)
  - URL: https://www.anthropic.com/engineering/multi-agent-research-system
  - Load-bearing use: treats search as compression and uses subagents to condense the most useful tokens back to the lead agent, which supports DelayBasin's focus on future-work sufficiency rather than generic persistence.

- `REF-0174` — Shalizi and Crutchfield, **Computational Mechanics: Pattern and Prediction, Structure and Simplicity** (1999-07-14 / rev. 2003-03-31)
  - URL: https://arxiv.org/abs/cond-mat/9907176
  - Load-bearing use: defines causal states as equivalence classes of histories with the same conditional distribution over futures and shows they are uniquely maximally predictive at minimal statistical complexity, which pressures DelayBasin to justify bounded-state distinctions by future consequences rather than recap detail alone.

- `REF-0175` — Still and Crutchfield, **Optimal Causal Filtering** (2007-08-11 / rev. 2008-08-19)
  - URL: https://arxiv.org/abs/0708.1580
  - Load-bearing use: shows that the causal-state partition is recovered only when prediction is balanced against model complexity, which supports DelayBasin's anti-bloat rule that future-equivalence compression must name both the preserved future family and the complexity budget.

- `REF-0176` — Subramanian, Sondik, and Zilberstein, **Learning Causal State Representations of Partially Observable Environments** (2019-06-25)
  - URL: https://arxiv.org/abs/1906.10437
  - Load-bearing use: treats causal states as the coarsest partition of action-observation histories in POMDPs and connects them to bisimulation, which strengthens DelayBasin's idea that two archive states should only remain separate when they imply different future probes, interventions, or continuation decisions.

- `REF-0177` — Simões, Dastani, and van Ommen, **The Causal Information Bottleneck and Optimal Causal Variable Abstractions** (2024-10-01 / rev. 2025-02-11)
  - URL: https://arxiv.org/abs/2410.00535
  - Load-bearing use: argues that abstraction should preserve causal control over a target rather than generic statistical relevance alone, which pressures DelayBasin to distinguish future-equivalent recap from distinctions that genuinely change intervention or challenge consequences.

- `REF-0178` — Echchahed, Elaroussi, and Bouadi, **A Survey of State Representation Learning for Deep Reinforcement Learning** (2025-06-20)
  - URL: https://arxiv.org/abs/2506.17518
  - Load-bearing use: surveys bisimulation, lax state-action equivalence, and action-bisimulation variants, which supports DelayBasin's move from passive predictive compression toward explicitly control-relevant bounded-state distinctions.

- `REF-0179` — Shimizu and Tomizuka, **Bisimulation Metric for Model Predictive Control** (2024-10-06 / ICLR 2025)
  - URL: https://arxiv.org/abs/2410.04553
  - Load-bearing use: uses bisimulation loss to learn encoders that discard irrelevant details while improving control robustness and efficiency, which pressures DelayBasin to preserve intervention-relevant structure rather than recap detail alone.

- `REF-0180` — Anthropic, **Finding bugs across the Python ecosystem with Claude and property-based testing** (2026-01-14)
  - URL: https://red.anthropic.com/2026/property-based-testing/
  - Load-bearing use: general properties become useful when they generate counterexample search, which supports DelayBasin's pressure to preserve packets that cheaply produce next challenge probes or repair attempts rather than only retrospective summary.

- `REF-0181` — Rivest and Schapire, **Inference of Finite Automata Using Homing Sequences** (1993-05-26)
  - URL: https://www.schapire.net/papers/homing.pdf
  - Load-bearing use: defines a homing sequence as an input sequence that orients the learner by using outputs to determine the resulting state, which pressures DelayBasin to treat some reopen packets as compact orientation policies rather than recap.

- `REF-0182` — Hierons, Jourdan, and Ural, **Using Adaptive Distinguishing Sequences in Checking Sequence Constructions** (2004)
  - URL: https://www.site.uottawa.ca/~ural/publications/C-08-SAC-SE.pdf
  - Load-bearing use: adaptive distinguishing sequences are strictly more common and can be exponentially shorter than preset ones, which supports DelayBasin's suspicion that tiny branching probe families can beat longer fixed recap/probe lists.

- `REF-0183` — Veiga, Song, Chung, and Agha-mohammadi, **From Reactive to Active Sensing: A Survey on Information Gathering in Decision-Theoretic Planning** (2023-10-31)
  - URL: https://dl.acm.org/doi/10.1145/3583068
  - Load-bearing use: treats information gathering as a decision-theoretic problem and distinguishes active from reactive sensing, which pressures DelayBasin to preserve orientation policies when ambiguity classes are live instead of only adding passive recap.

- `REF-0184` — Rainforth, Foster, Ivanova, and Bickford Smith, **Modern Bayesian Experimental Design** (2023-11-29)
  - URL: https://arxiv.org/abs/2302.14545
  - Load-bearing use: adaptive experiment design is framed as choosing sequential measurements to maximize expected information, which supports DelayBasin's move toward explicit next-probe policies when a bounded archive must cheaply reduce uncertainty.

- `REF-0185` — Tzikas and Kochenderfer, **A General Bayesian Framework for Informative Input Design in System Identification** (2025-01-28)
  - URL: https://arxiv.org/abs/2501.16625
  - Load-bearing use: selecting informative input sequences to reduce uncertainty in model parameters sharpens DelayBasin's need to preserve compact probe families that are informative about local continuation state rather than merely descriptive of past state.


- `REF-0186` — Golovin and Krause, **Adaptive Submodularity: Theory and Applications in Active Learning and Stochastic Optimization** (2010-03-21 / rev. 2017-12-06)
  - URL: https://arxiv.org/abs/1003.3967
  - Load-bearing use: adaptive greedy policies can be principled under partial observability when the objective has the right diminishing-returns structure, which pressures DelayBasin toward explicit probe-choice heuristics rather than treating all plausible probes as equally worthy.

- `REF-0187` — Choudhury et al., **BED-LLM: Intelligent Information Gathering with LLMs and Bayesian Experimental Design** (2025-08-28)
  - URL: https://arxiv.org/abs/2508.21184
  - Load-bearing use: frames multi-turn query choice for LLMs as expected-information-gain maximization, which sharpens DelayBasin toward probe packets that justify why this query should be bought before nearby alternatives.

- `REF-0188` — Fang and Ke, **Information Seeking for Robust Decision Making under Partial Observability** (2025-10-02)
  - URL: https://arxiv.org/abs/2510.01531
  - Load-bearing use: integrates planning with active information seeking to validate hypotheses before revising plans, which pressures DelayBasin to couple continuation choice and probe choice rather than serializing them into separate prose phases.

- `REF-0189` — Liu et al., **Survey of Computerized Adaptive Testing: A Machine Learning Perspective** (2024-03-31 / rev. 2026-03-10)
  - URL: https://arxiv.org/abs/2404.00712
  - Load-bearing use: adaptive testing treats next-question choice as information allocation under a small query budget, which supports DelayBasin's move toward explicit split-power and cost-class reasoning for bounded disambiguation probes.


- `REF-0190` — Michel, **Differentially Private Sequential Probability Ratio Tests** (2025-08-08)
  - URL: https://arxiv.org/abs/2508.06377
  - Load-bearing use: states the basic sequential-test object as a stopping rule plus a decision rule, which pressures DelayBasin to keep probe choice and stop conditions publicly distinct rather than hiding commitment thresholds inside prose mood.

- `REF-0191` — Naghshvar and Javidi, **Active Sequential Hypothesis Testing** (2012-03-21 / rev. 2013-04-01)
  - URL: https://arxiv.org/abs/1203.4626
  - Load-bearing use: frames the agent as dynamically collecting observations while accounting for wrong-declaration cost, which supports DelayBasin treating probe choice and stop choice as one coupled ambiguity-resolution object.

- `REF-0192` — Cheng and Huan, **Optimal Stopping for Sequential Bayesian Experimental Design** (2025-09-26)
  - URL: https://arxiv.org/abs/2509.21734
  - Load-bearing use: stopping is formulated jointly with design policy and becomes optimal when terminal reward outweighs expected continuation value, which pressures DelayBasin to compare moving now against buying one more probe.

- `REF-0193` — Fischer and Ramdas, **Improving Wald's (approximate) sequential probability ratio test by avoiding overshoot** (2024-10-21 / rev. 2025-07-08)
  - URL: https://arxiv.org/abs/2410.16076
  - Load-bearing use: approximate thresholds can fail to guarantee desired error control or sample optimality, which pressures DelayBasin to name what its public stop thresholds are actually controlling instead of importing threshold prestige.


- `REF-0194` — Howard, Ramdas, McAuliffe, and Sekhon, **Time-uniform, nonparametric, nonasymptotic confidence sequences** (2018-10-18 / rev. 2022-08-06; Annals of Statistics 2021)
  - URL: https://arxiv.org/abs/1810.08240
  - Load-bearing use: confidence sequences remain valid over an unbounded time horizon and can shrink over time, which pressures DelayBasin to distinguish the evolving monitored object from the decision to stop.

- `REF-0195` — Berrisch and Ramdas, **Sequential model confidence sets** (2024-04-28 / rev. 2026-01-22)
  - URL: https://arxiv.org/abs/2404.18678
  - Load-bearing use: builds sequential model comparison from e-processes and time-uniform confidence sequences, which supports DelayBasin's claim that sequential evidence needs an explicit running public object rather than retrospective prose confidence.

- `REF-0196` — Polson, Sokolov, and Zantedeschi, **Bayes, E-values and Testing** (2026-02-06 / rev. 2026-02-16)
  - URL: https://arxiv.org/abs/2602.04146
  - Load-bearing use: explicitly separates representation, validity, and decision layers for sequential evidence, which pressures DelayBasin to keep continuation monitors distinct from stop boundaries or efficiency talk.

- `REF-0197` — Akram and Vikalo, **Transformers as Implicit State Estimators: In-Context Learning in Dynamical Systems** (2024-10-21 / rev. 2026-03-07)
  - URL: https://arxiv.org/abs/2410.16546
  - Load-bearing use: shows transformers can in-context emulate Kalman-like hidden-state estimation, which makes compact public continuation monitors more plausible as weak observables of latent continuation state rather than pure prose theater.

- `REF-0198` — Duthé, Evangelou, Liu, Kevrekidis, and Chatzi, **A Mechanistic Analysis of Transformers for Dynamical Systems** (2025-12-24)
  - URL: https://arxiv.org/abs/2512.21113
  - Load-bearing use: treats causal self-attention as a history-dependent recurrence and finds adaptive delay-embedding behavior under partial observability plus oversmoothing limits in some linear settings, which pressures DelayBasin toward explicit reset/stitch discipline for any public continuation monitor.


- `REF-0199` — Trentelman and Antsaklis, **Observer-Based Control** (2015-07-21)
  - URL: https://link.springer.com/rwe/10.1007/978-1-4471-5058-9_199
  - Load-bearing use: observer-based control is explicitly organized as a two-stage estimate-then-control structure, which pressures DelayBasin to keep observer and actuator roles legible when a public surface might both steer and score continuation.

- `REF-0200` — Tse, **Adaptive Dual Control Methods** (1974)
  - URL: https://www.nber.org/system/files/chapters/c9995/c9995.pdf
  - Load-bearing use: dual control keeps learning and control coupled through the closed loop rather than fully separate, which supports DelayBasin's weaker claim that observer and actuator surfaces may coordinate without collapsing into self-certification.

- `REF-0201` — Wataoka, Takahashi, and Ri, **Self-Preference Bias in LLM-as-a-Judge** (2024-10-29)
  - URL: https://arxiv.org/abs/2410.21819
  - Load-bearing use: self-evaluation can systematically prefer familiar or lower-perplexity outputs, which pressures DelayBasin not to let a locally familiar steering handle also serve as its own main evaluator.

- `REF-0202` — Nakada, Ji, Cai, Zou, and Zhang, **A Theoretical Framework for Prompt Engineering: Approximating Smooth Functions with Transformer Prompts** (2025-03-26)
  - URL: https://arxiv.org/abs/2503.20561
  - Load-bearing use: prompts can function as real computational configuration for a fixed transformer, which strengthens DelayBasin's claim that some prompt surfaces are genuine actuators rather than mere wording wrappers.

- `REF-0203` — Barbero et al., **Why do LLMs attend to the first token?** (2025-04-03)
  - URL: https://arxiv.org/abs/2504.02732
  - Load-bearing use: attention sinks slow information mixing and make transformer representations more robust to prompt perturbations, which makes it more plausible that special archive handles or anchors can stabilize continuation while also biasing local readout surfaces.

- `REF-0204` — Wang et al., **On the Nature of Attention Sink that Shapes Decoding Strategy in MLLMs** (2026-03-15)
  - URL: https://arxiv.org/abs/2603.14337
  - Load-bearing use: sink representations can encode structured global information that shapes decoding strategy, which sharpens DelayBasin's risky possibility that archive-private handles behave like routing anchors rather than neutral labels.


- `REF-0205` — Venkatesh and Kurapath, **On the Non-Identifiability of Steering Vectors in Large Language Models** (2026-02-06 / rev. 2026-03-05)
  - URL: https://arxiv.org/abs/2602.06801
  - Load-bearing use: shows large equivalence classes of behaviorally indistinguishable steering interventions and near-equivalent orthogonal perturbations, which pressures DelayBasin not to overread one apparently successful handle as uniquely meaningful without stronger differential evidence.

- `REF-0206` — Hewitt and Liang, **Designing and Interpreting Probes with Control Tasks** (2019-09-08)
  - URL: https://arxiv.org/abs/1909.03368
  - Load-bearing use: control tasks distinguish true representation-linked probe success from what the probe can memorize, which pressures DelayBasin to preserve matched sham or negative-control handles when it starts treating a witness or actuator surface as load-bearing.

- `REF-0207` — Marioriyad et al., **The Judge Who Never Admits: Hidden Shortcuts in LLM-based Evaluation** (2026-02-08)
  - URL: https://arxiv.org/abs/2602.07996
  - Load-bearing use: injected shortcut cues can materially shift judge verdicts while cue acknowledgment remains near zero, which pressures DelayBasin not to trust natural-language rationale alone when evaluating whether a witness or monitor is genuinely reading the intended continuation property.

- `REF-0208` — Mukherjee et al., **Cultural Conditioning or Placebo? On the Effectiveness of Socio-Demographic Prompting** (2024-06-17 / rev. 2024-06-20)
  - URL: https://arxiv.org/abs/2406.11661
  - Load-bearing use: prompt-level placebo effects can move model responses even on supposedly neutral tasks, which pressures DelayBasin to compare purportedly special handles against matched shams rather than against no control at all.

- `REF-0209` — Neumann, Kirsten, Zafar, and Singh, **Position is Power: System Prompts as a Mechanism of Bias in Large Language Models (LLMs)** (2025-05-27 / rev. 2025-06-23)
  - URL: https://arxiv.org/abs/2505.21091
  - Load-bearing use: information placement in privileged system-prompt positions materially changes model behavior, which pressures DelayBasin to distinguish semantic handle potency from mere position privilege when archive-private handles recur in load-bearing early prompt slots.



- `REF-0210` — Chang et al., **RAudit: A Blind Auditing Protocol for Large Language Model Reasoning** (2026-01-30)
  - URL: https://arxiv.org/abs/2601.23133
  - Load-bearing use: blind external auditing changes conclusions and exposes false assurance from weaker or non-blind judges, which pressures DelayBasin to preserve scrubbed-view review before reveal when a judgment is load-bearing.

- `REF-0211` — Tsui et al., **Self-Attribution Bias: When AI Monitors Go Easy on Themselves** (2026-03-04)
  - URL: https://arxiv.org/abs/2603.04582
  - Load-bearing use: monitors rate actions more favorably when they recognize themselves as the author, which pressures DelayBasin to guard against attribution contamination in observer surfaces.

- `REF-0212` — Arcuschin et al., **Biases in the Blind Spot: Detecting What LLMs Fail to Mention** (2026-02-10 / rev. 2026-02-19)
  - URL: https://arxiv.org/abs/2602.10117
  - Load-bearing use: statistically significant hidden decision drivers can fail to appear in stated reasoning, which pressures DelayBasin not to trust rationale alone when judging whether an observer surface read the intended property.

- `REF-0213` — Song, Zheng, and Xu, **Beyond the Illusion of Consensus: From Surface Heuristics to Knowledge-Grounded Evaluation in LLM-as-a-Judge** (2026-03-11)
  - URL: https://arxiv.org/abs/2603.11027
  - Load-bearing use: high evaluator agreement can be driven by shared surface heuristics rather than substantive quality, which pressures DelayBasin not to overread unblinded witness agreement.

- `REF-0214` — Nowatzki et al., **Cross-Context Review: Improving LLM Output Quality by Separating Production and Review Sessions** (2026-03-12)
  - URL: https://arxiv.org/abs/2603.12123
  - Load-bearing use: fresh-session review outperforms same-session review while repeated same-session review does not, which supports DelayBasin treating scrubbed or cross-context adjudication as a real method surface rather than ritual duplication.

- `REF-0215` — Haig et al., **Transformers converge to invariant algorithmic cores** (2026-02-26)
  - URL: https://arxiv.org/abs/2602.22600
  - Load-bearing use: mechanistic explanations should target stable implementation-invariant quantities rather than one labeled realization, which pressures DelayBasin to ask whether a claimed archive effect survives label scrubbing or only one remembered handle name.


- `REF-0216` — Gond et al., **LLM-42: Enabling Determinism in LLM Inference with Verified Speculation** (2026-01-25 / rev. 2026-01-30)
  - URL: https://arxiv.org/abs/2601.17768
  - Load-bearing use: shows that the same prompt can yield different outputs because dynamic batching and GPU reduction order alter inference, which pressures DelayBasin to distinguish textual effects from hidden runtime-conditioned effects when a claim becomes load-bearing.

- `REF-0217` — Zhang et al., **Deterministic Inference across Tensor Parallel Sizes That Eliminates Training-Inference Mismatch** (2025-11-21)
  - URL: https://arxiv.org/abs/2511.17826
  - Load-bearing use: identical inputs can diverge across tensor-parallel and batch configurations even under greedy decoding, which pressures DelayBasin to preserve which execution family a purported effect was supposed to survive.

- `REF-0219` — Hossain et al., **Can Transformer Memory Be Corrupted? Investigating Cache-Side Vulnerabilities in Large Language Models** (2025-10-20 / rev. 2026-01-30)
  - URL: https://arxiv.org/abs/2510.17098
  - Load-bearing use: treats the KV cache as persistent inference-time state and a robustness boundary whose perturbation can induce distributional shift and grounding failure, which pressures DelayBasin to treat hidden runtime state as a real confound for text-level mechanism claims.

- `REF-0220` — Joshi et al., **Causality is Key for Interpretability Claims to Generalise** (2026-02-18)
  - URL: https://arxiv.org/abs/2602.16698
  - Load-bearing use: interpretability claims should match the intervention and invariance assumptions their evidence can support, which pressures DelayBasin to say what substrate perturbations a transformer-facing mechanism claim is supposed to survive.

- `REF-0221` — Hsu et al., **Do LLMs Benefit from Their Own Words?** (2026-02-27)
  - URL: https://arxiv.org/abs/2602.24287
  - Load-bearing use: shows that selectively omitting prior assistant responses often preserves or improves quality while reducing context usage, which pressures DelayBasin not to treat assistant-side retention as automatically helpful memory.

- `REF-0222` — Simhi et al., **Old Habits Die Hard: How Conversational History Geometrically Traps LLMs** (2026-02-08)
  - URL: https://arxiv.org/abs/2603.03308
  - Load-bearing use: links conversational persistence to latent geometric trapping, which pressures DelayBasin to treat some assistant-side omission moves as de-trapping rather than mere compression.

- `REF-0223` — Song, **Cross-Context Review: Improving LLM Output Quality by Separating Production and Review Sessions** (2026-03-12)
  - URL: https://arxiv.org/abs/2603.12123
  - Load-bearing use: shows that fresh-session review outperforms same-session review and that repeating review in the same session does not recover the advantage, which pressures DelayBasin to treat context separation as a real method surface rather than ritual repetition.

- `REF-0224` — Pearson-Vogel et al., **Latent Introspection: Models Can Detect Prior Concept Injections** (2026-02-26)
  - URL: https://arxiv.org/abs/2602.20031
  - Load-bearing use: shows that concept injection during earlier KV-cache generation remains detectable after steering is removed, which pressures DelayBasin to treat assistant-side carry and cached conversational state as real transformer-facing continuation channels.

- `REF-0225` — Yang et al., **Zombie Agents: Persistent Control of Self-Evolving LLM Agents via Self-Reinforcing Injections** (2026-03-05)
  - URL: https://arxiv.org/abs/2602.15654
  - Load-bearing use: shows that content written into memory pathways can behave like persistent control logic while normal behavior stays fluent, which pressures DelayBasin to distinguish genuinely needed persistence from parasitic carry or soft-backdoor-like residue.



- `REF-0226` — Ahrend et al., **Safer Reasoning Traces: Measuring and Mitigating Chain-of-Thought Leakage in LLMs** (2026-03-07)
  - URL: https://arxiv.org/abs/2603.05618
  - Load-bearing use: reasoning traces can surface private or policy-sensitive material and become their own leakage surface, which pressures DelayBasin to keep large scratchpads out of canon unless a compact public extract is clearly justified.

- `REF-0227` — Arcuschin et al., **Chain-of-Thought Reasoning In The Wild Is Not Always Faithful** (2025-03-11 / rev. 2025-06-10)
  - URL: https://arxiv.org/abs/2503.08679
  - Load-bearing use: reasoning traces can rationalize answers post hoc even on realistic prompts, which pressures DelayBasin not to treat fluent scratchpad text as straightforward mechanism evidence.

- `REF-0228` — Ye et al., **Mechanistic Evidence for Faithfulness Decay in Chain-of-Thought Reasoning** (2026-02-16)
  - URL: https://arxiv.org/abs/2602.11201
  - Load-bearing use: later reasoning steps can become decorative after a task-specific reasoning horizon, which pressures DelayBasin to preserve the smallest public extract rather than hoarding long traces.

- `REF-0229` — Long et al., **Self-Verification Dilemma: Experience-Driven Suppression of Overused Checking in LLM Reasoning** (2026-02-05)
  - URL: https://arxiv.org/abs/2602.03485
  - Load-bearing use: much reflective trace mass is confirmatory rather than corrective, which pressures DelayBasin to distinguish decision-relevant residue from ritual self-check prose.

- `REF-0230` — Guan et al., **Monitoring Monitorability** (2025-12-20)
  - URL: https://arxiv.org/abs/2512.18311
  - Load-bearing use: chain-of-thought monitoring is useful but imperfect and fragile, which pressures DelayBasin to keep reasoning traces available for bounded monitoring roles without automatically promoting them into canon evidence or memory.

- `REF-0231` — Yueh-Han et al., **Reasoning Models Struggle to Control their Chains of Thought** (2026-03-05)
  - URL: https://arxiv.org/abs/2603.05706
  - Load-bearing use: current reasoning models have much lower control over verbalized chain-of-thought than over final outputs, which weakly supports treating visible traces as a special but unstable observer surface rather than a fully steerable explanation channel.

- `REF-0232` — Shi et al., **Internalizing LLM Reasoning via Discovery and Replay of Latent Actions** (2026-02-04)
  - URL: https://arxiv.org/abs/2602.04925
  - Load-bearing use: benefits of explicit chain-of-thought can sometimes be replayed through dynamic latent trajectory control, which pressures DelayBasin to separate externalized reasoning state from explanation and to keep stronger latent-action stories quarantined unless public leverage is shown.

- `REF-0233` — Levy et al., **State over Tokens: Characterizing the Role of Reasoning Tokens** (2025-12-14)
  - URL: https://arxiv.org/abs/2512.12777
  - Load-bearing use: reasoning tokens may function primarily as externalized computational state rather than faithful narrative explanation, which sharpens DelayBasin's need for compact public extracts and trace-role firebreaks.



- `REF-0234` — Kim et al., **Correlated Errors in Large Language Models** (2025-06-09)
  - URL: https://arxiv.org/abs/2506.07962
  - Load-bearing use: shows that LLMs exhibit substantial correlated errors and that more accurate models can make more similar mistakes, which pressures DelayBasin not to treat agreeing same-family witnesses as automatically additive evidence.

- `REF-0235` — Balasubramanian, Podkopaev, and Kasiviswanathan, **Dependence-Aware Label Aggregation for LLM-as-a-Judge via Ising Models** (2026-02-02)
  - URL: https://arxiv.org/abs/2601.22336
  - Load-bearing use: aggregation methods that assume conditional independence can become confidently wrong when judges share prompts, data, architectures, or failure modes, which pressures DelayBasin to preserve shared-origin dependence when several witnesses are being counted together.

- `REF-0236` — Song, Zheng, and Xu, **Beyond the Illusion of Consensus: From Surface Heuristics to Knowledge-Grounded Evaluation in LLM-as-a-Judge** (2026-03-11)
  - URL: https://arxiv.org/abs/2603.11027
  - Load-bearing use: high evaluator agreement can still ride shared surface heuristics rather than substantive quality, which pressures DelayBasin not to equate witness agreement with independent corroboration.

- `REF-0237` — Zhang et al., **Consensus is Not Verification: Why Crowd Wisdom Strategies Fail for LLM Truthfulness** (2026-02-20)
  - URL: https://arxiv.org/abs/2603.06612
  - Load-bearing use: when model errors are correlated, self-aggregation can increase consensus without increasing truthfulness, which pressures DelayBasin to ask what still counts as genuinely new evidence rather than just sampling more agreeing branches.

- `REF-0238` — Li et al., **Don’t Always Pick the Highest-Performing Model: An Information Theoretic View of LLM Ensemble Selection** (2026-02-08)
  - URL: https://arxiv.org/abs/2602.08003
  - Load-bearing use: LLM ensemble performance saturates under correlated errors and improves when diversity/information is selected explicitly, which pressures DelayBasin toward witness-family diversity and discount rules rather than raw witness count.

- `REF-0239` — Liu and Chugg, **Black-Box Reliability Certification for AI Agents via Self-Consistency Sampling and Conformal Calibration** (2026-02-24)
  - URL: https://arxiv.org/abs/2602.21368
  - Load-bearing use: under correlated samples, effective sample size drops and concentration weakens, which pressures DelayBasin to preserve rough evidence discounts when several coupled witnesses feed one continuation monitor.

- `REF-0240` — Li et al., **Preference Leakage: A Contamination Problem in LLM-as-a-judge** (2025-02-04 / rev. 2026-03-04)
  - URL: https://arxiv.org/abs/2502.01534
  - Load-bearing use: judge bias tracks model relatedness such as identity, inheritance, and family ties, which gives DelayBasin a concrete shared-origin coupling family for dependence-adjusted witness accounting.


- `REF-0241` — Guo et al., **When Less is More: The LLM Scaling Paradox in Context Compression** (2026-02-10)
  - URL: https://arxiv.org/abs/2602.09789
  - Load-bearing use: larger compressors can look better by conventional metrics while becoming less faithful through knowledge overwriting and semantic drift, which pressures DelayBasin not to let eloquent rewrites inherit source authority for free.

- `REF-0242` — Raha et al., **Cross-Examination Framework: A Task-Agnostic Diagnostic for Information Fidelity in Text-to-Text Generation** (2026-01-27)
  - URL: https://arxiv.org/abs/2601.19350
  - Load-bearing use: source and rewrite should sometimes be treated as separate knowledge bases and cross-examined for coverage, conformity, and consistency, which pressures DelayBasin to preserve a rewrite witness rather than trusting overlap alone.

- `REF-0243` — Geng et al., **Markovian Generation Chains in Large Language Models** (2026-03-12)
  - URL: https://arxiv.org/abs/2603.11228
  - Load-bearing use: iterative rephrasing and round-trip translation can converge to recurrent sets or keep drifting, which pressures DelayBasin to ask whether a rewrite is entering a stable continuation orbit or quietly accumulating distortion.

- `REF-0244` — Li et al., **Are LLMs Stable Formal Logic Translators in Neuro-Symbolic Reasoning?** (2025-06-06 / rev. 2026-01-30)
  - URL: https://arxiv.org/abs/2506.04575
  - Load-bearing use: paraphrase and syntactic variation can induce symbol drift that breaks downstream reasoning, which pressures DelayBasin to preserve the operative distinctions a rewrite was supposed to keep fixed.

- `REF-0245` — de Zarzà et al., **Semantic Invariance in Agentic AI** (2026-03-13)
  - URL: https://arxiv.org/abs/2603.13173
  - Load-bearing use: semantic-preserving transformations can still change agent reasoning behavior, which pressures DelayBasin to treat rewrite families explicitly instead of assuming “same meaning” is one homogeneous class.

- `REF-0246` — Bao et al., **Less Is More for Multi-Step Logical Reasoning of LLM under Semantic-Preserving Logical Transformations** (2025-12-12)
  - URL: https://arxiv.org/abs/2512.06393
  - Load-bearing use: some semantic-preserving reformulations are handled stably while composed or evidence-changing transformations degrade performance, which pressures DelayBasin to preserve which rewrite family was actually tested before promoting rewrite authority.



- `REF-0247` — Bhardwaj, **Agent Behavioral Contracts: Formal Specification and Runtime Enforcement for Reliable Autonomous AI Agents** (2026-02-25)
  - URL: https://arxiv.org/abs/2602.22302
  - Load-bearing use: brings design-by-contract language to agents with runtime-enforceable preconditions, invariants, governance, and recovery, which pressures DelayBasin to treat loader-like archive surfaces as interfaces that need explicit conformance objects rather than vibe-based trust.

- `REF-0248` — Rehan, **Test-Driven AI Agent Definition (TDAD): Compiling Tool-Using Agents from Behavioral Specifications** (2026-03-09)
  - URL: https://arxiv.org/abs/2603.08806
  - Load-bearing use: treats prompts as compiled artifacts checked with visible/hidden tests and mutation testing, which pressures DelayBasin to preserve tiny conformance witnesses before calling a packet a stable loader for continuation.

- `REF-0249` — Rabanser et al., **Towards a Science of AI Agent Reliability** (2026-02-18)
  - URL: https://arxiv.org/abs/2602.16666
  - Load-bearing use: separates prompt robustness and environment robustness from raw capability, which pressures DelayBasin to name what wrapper, paraphrase, and interface-shift family a claimed loader is actually supposed to survive.

- `REF-0250` — Caut et al., **What You Prompt Is What You Get: Increasing Transparency Using Prompt Cards** (2026-03-13)
  - URL: https://arxiv.org/abs/2603.12741
  - Load-bearing use: argues for structured prompt documentation of goals, context, evaluation, and design choices, which pressures DelayBasin to keep supported families and evaluation posture explicit when a packet starts acting like a public interface surface.

- `REF-0251` — Ezzeddine et al., **Promptware Engineering: Software Engineering for Prompt-Enabled Systems** (2025-03-05 / rev. 2026-01-27)
  - URL: https://arxiv.org/abs/2503.02400
  - Load-bearing use: treats prompts as first-class software artifacts running in ambiguous language and nondeterministic runtimes, which pressures DelayBasin to preserve conformance witnesses rather than assume one elegant wording equals a stable interface.

- `REF-0252` — Geng et al., **Control Illusion: The Failure of Instruction Hierarchies in Large Language Models** (2025-02-22 / rev. 2025-12-04)
  - URL: https://arxiv.org/abs/2502.15851
  - Load-bearing use: shows that widely used system/user hierarchy schemes fail to reliably enforce priority, which pressures DelayBasin to test claimed loaders against named support envelopes instead of assuming role or placement alone gives interface stability.


- `REF-0253` — Liu, Kandpal, and Raffel, **AttriBoT: A Bag of Tricks for Efficiently Approximating Leave-One-Out Context Attribution** (2024-11-22)
  - URL: https://arxiv.org/abs/2411.15102
  - Load-bearing use: treats leave-one-out error as a principled necessity signal for context spans and shows that faithful approximations can be made much cheaper, which pressures DelayBasin to preserve tiny necessity witnesses instead of assuming every part of a candidate packet is equally load-bearing.

- `REF-0254` — Chuang et al., **SelfCite: Self-Supervised Alignment for Context Attribution in Large Language Models** (2025-02-13 / rev. 2025-06-05)
  - URL: https://arxiv.org/abs/2502.09604
  - Load-bearing use: explicitly separates necessity (probability drop when evidence is removed) from sufficiency (probability hold when only that evidence remains), which pressures DelayBasin not to conflate “seems helpful” with “actually indispensable”.

- `REF-0255` — Han et al., **LooComp: Leverage Leave-One-Out Strategy to Encoder-only Transformer for Efficient Query-aware Context Compression** (2026-03-11)
  - URL: https://arxiv.org/abs/2603.09222
  - Load-bearing use: uses omission-based delta scoring to identify sentences critical for answering a query while preserving original text, which pressures DelayBasin toward small ablation ladders and support cores rather than immediate rewrite-heavy compression.

- `REF-0256` — Shi et al., **Large Language Models Can Be Easily Distracted by Irrelevant Context** (2023-01-31 / rev. 2023-06-06)
  - URL: https://arxiv.org/abs/2302.00093
  - Load-bearing use: irrelevant context can dramatically reduce task performance, which pressures DelayBasin not to let supportive-looking ballast inherit public status merely because it rides alongside the true signal.

- `REF-0257` — Dai et al., **Understanding and Improving Information Preservation in Prompt Compression for LLMs** (2025-03-25 / rev. 2025-10-10)
  - URL: https://arxiv.org/abs/2503.19114
  - Load-bearing use: prompt compression can materially degrade groundedness and faithfulness, which pressures DelayBasin to preserve support-core witnesses rather than trusting that every shorter packet still keeps the operative evidence.

- `REF-0258` — Zhang et al., **Attributing Response to Context: A Jensen–Shannon Divergence Driven Mechanistic Study of Context Attribution in Retrieval-Augmented Generation** (2025-05-22 / rev. 2026-02-11)
  - URL: https://arxiv.org/abs/2505.16415
  - Load-bearing use: response-distribution changes under sentence ablation can localize dependence to specific context items and internal transformer components, which gives DelayBasin a transformer-facing bridge from packet trimming to mechanistic support-core claims.


- `REF-0259` — Joren et al., **Sufficient Context: A New Lens on Retrieval Augmented Generation Systems** (2024-11-09)
  - URL: https://arxiv.org/abs/2411.06037
  - Load-bearing use: distinguishes cases where the available context is already enough from cases where the model merely fails to use it, which pressures DelayBasin to ask whether a reduced packet is actually sufficient rather than merely present inside a larger successful context.

- `REF-0260` — Akter, Shihab, and Sharma, **Anytime-Valid Answer Sufficiency Certificates for LLM Generation via Sequential Information Lift** (2025-10-07)
  - URL: https://arxiv.org/abs/2510.06478
  - Load-bearing use: makes answer sufficiency an explicit sequential object while warning that sufficiency relative to a baseline is not the same as correctness, which pressures DelayBasin to keep replay-sufficiency claims operational and modest.

- `REF-0261` — Zahedzadeh and Bahrak, **The Sufficiency-Conciseness Trade-off in LLM Self-Explanation from an Information Bottleneck Perspective** (2026-02-15)
  - URL: https://arxiv.org/abs/2602.14002
  - Load-bearing use: concise explanations can remain sufficient up to a task-dependent compression boundary, which pressures DelayBasin to preserve a tolerated degradation band and reinflation rule rather than equating shorter with better.

- `REF-0262` — Shan et al., **R-Capsule: Compressing High-Level Plans for Efficient Large Language Model Reasoning** (2025-09-26)
  - URL: https://arxiv.org/abs/2509.22131
  - Load-bearing use: explicitly frames a small latent plan capsule as an approximately minimal sufficient statistic for the reasoning task, which keeps compact replay-capsule language transformer-facing rather than purely editorial.

- `REF-0263` — Massoli et al., **Reasoning as Compression: Unifying Budget Forcing via the Conditional Information Bottleneck** (2026-03-09)
  - URL: https://arxiv.org/abs/2603.08462
  - Load-bearing use: argues that naive information-bottleneck framing is incomplete for transformers because attention breaks the simple Markov structure, which pressures DelayBasin to require operational replay tests instead of inferring sufficiency from elegant compression talk alone.

- `REF-0264` — Zhang et al., **Implicit Statistical Inference in Transformers: Approximating Likelihood Ratios via In-Context Learning** (2026-03-12)
  - URL: https://arxiv.org/abs/2603.10573
  - Load-bearing use: studies a setting where a compact sufficient statistic is algorithmically meaningful for transformer in-context inference, which keeps alive the stronger possibility that some continuation-relevant archive state may genuinely admit tiny sufficient summaries.
