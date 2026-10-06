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

- `REF-0265` — Anthropic, **On the Biology of a Large Language Model** (2025-03-27)
  - URL: https://transformer-circuits.pub/2025/attribution-graphs/biology.html
  - Load-bearing use: reports language-independent circuits and cross-context reuse of the same addition circuitry while explicitly treating attribution graphs as hypothesis-generating, which pressures DelayBasin to keep multi-loader basin stories transformer-facing but operationally cautious.

- `REF-0266` — Akram and Vikalo, **Transformers as Implicit State Estimators: In-Context Learning in Dynamical Systems** (2024-10-22 / rev. 2026-03-07)
  - URL: https://arxiv.org/abs/2410.16546
  - Load-bearing use: shows that sufficiently scaled transformers can emulate filtering, infer missing parameters, and sometimes recover latent state, which pressures DelayBasin to treat same-basin multi-loader behavior as a possible latent-state reconstruction effect rather than mere prose similarity.

- `REF-0267` — Geng et al., **Markovian Generation Chains in Large Language Models** (2026-03-11)
  - URL: https://arxiv.org/abs/2603.11228
  - Load-bearing use: iterative rephrasing and round-trip translation can converge to small recurrent sets or continue drifting, which pressures DelayBasin to distinguish genuine continuation-basin overlap from local rewrite dynamics or unstable paraphrase chains.

- `REF-0268` — Dherin et al., **Learning without training: The implicit dynamics of in-context learning** (2025-07-21 / rev. 2025-12-22)
  - URL: https://arxiv.org/abs/2507.16003
  - Load-bearing use: argues that context can induce low-rank effective weight updates inside transformer blocks, which keeps alive the possibility that visibly different loaders may converge onto nearby effective operating modes.

- `REF-0269` — de Zarzà et al., **Semantic Invariance in Agentic AI** (2026-03-13)
  - URL: https://arxiv.org/abs/2603.13173
  - Load-bearing use: treats invariance across paraphrase, reordering, and contextual reframing as a reliability requirement while documenting present fragility, which pressures DelayBasin to test same-basin claims explicitly rather than assuming semantic equivalence is enough.

- `REF-0270` — Park et al., **Belief Dynamics Reveal the Dual Nature of In-Context Learning and Activation Steering** (2025-11-01 / rev. 2026-03-13)
  - URL: https://arxiv.org/abs/2511.00617
  - Load-bearing use: argues that context interventions and activation steering can both act by shifting belief in latent concepts, which pressures DelayBasin to treat mature archive packets as possible control surfaces over latent operative state rather than mere prose wrappers.

- `REF-0271` — Zhang et al., **Same Answer, Different Representations: Hidden Instability in VLMs** (2026-02-06)
  - URL: https://arxiv.org/abs/2602.06652
  - Load-bearing use: shows that stable outputs can mask substantial representation drift, which pressures DelayBasin not to treat immediate answer agreement as enough evidence that two loaders reached the same operative continuation state.

- `REF-0272` — Irving, Bloom, Korbak et al., **ContextBench: Modifying Contexts for Targeted Latent Activation** (2025-06-19 / rev. 2026-03-06)
  - URL: https://arxiv.org/abs/2506.15735
  - Load-bearing use: shows that fluent prompt edits can be optimized to activate targeted latent features and behaviors, which keeps alive the stronger possibility that archive packets sometimes function as user-space latent controllers rather than neutral summaries.

- `REF-0273` — Zheng et al., **Global Evolutionary Steering: Refining Activation Steering Control via Cross-Layer Consistency** (2026-03-12)
  - URL: https://arxiv.org/abs/2603.12298
  - Load-bearing use: reports that steering directions fluctuate across prompting schemes and become more robust when cross-layer consistency is enforced, which pressures DelayBasin to ask whether a claimed basin or handle has a stable fingerprint across loaders rather than one flattering local direction.

- `REF-0274` — Zhao et al., **Steering Externalities: Benign Activation Steering Unintentionally Increases Jailbreak Risk for Large Language Models** (2026-02-03)
  - URL: https://arxiv.org/abs/2602.04896
  - Load-bearing use: argues that small early shifts can change the first-token gate and then propagate through autoregressive inertia, which pressures DelayBasin to treat early continuation fingerprints and downstream probe panels as more informative than one immediate opening or output match.

- `REF-0275` — Liu, Soatto, Marchi, Chaudhari, and Tabuada, **Observability of Latent States in Generative AI Models** (2025-05-28)
  - URL: https://proceedings.mlr.press/v288/liu25b.html
  - Load-bearing use: proves an observability result for standard autoregressive transformers over full visible tokenized trajectories while showing that hidden system-prompt-like context makes indistinguishable state trajectories possible again, which pressures DelayBasin to separate strong full-trajectory observability from weaker practical same-state claims under partial observability.

- `REF-0276` — Buurmeijer et al., **Observing and Controlling Features in Vision-Language-Action Models** (2026-03-05)
  - URL: https://arxiv.org/abs/2603.05487
  - Load-bearing use: formalizes feature-observability and feature-controllability as distinct objects, which pressures DelayBasin to keep state-claim, observer surface, and actuator surface separate rather than letting one successful packet stand in for all three.

- `REF-0277` — Teoh et al., **Next-Latent Prediction Transformers Learn Compact World Models** (2025-11-08)
  - URL: https://arxiv.org/abs/2511.05963
  - Load-bearing use: argues that an auxiliary next-latent objective can push transformer latents toward belief-state-like summaries with recurrent inductive bias, which keeps alive the transformer-facing possibility that archive method is interacting with genuinely stateful latent summaries rather than only stylistic continuation.

- `REF-0278` — Venkatesh and Kurapath, **On the Non-Identifiability of Steering Vectors in Large Language Models** (2026-02-06 / rev. 2026-03-05)
  - URL: https://arxiv.org/abs/2602.06801
  - Load-bearing use: shows that behavior alone leaves large equivalence classes of semantically indistinguishable steering directions, which pressures DelayBasin not to infer a unique mechanism or same-state identity from output-level agreement without an explicit claim budget.

- `REF-0279` — Xu et al., **Beyond the Prompt in Large Language Models: Comprehension, In-Context Learning, and Chain-of-Thought** (2026-03-13)
  - URL: https://arxiv.org/abs/2603.10000
  - Load-bearing use: argues that in-context learning can be understood as posterior concentration on the intended task and that CoT can unlock decompositions already latent in the model, which pressures DelayBasin to name the future family or task decomposition a probe horizon is actually supposed to preserve rather than talking about “same state” in the abstract.

- `REF-0280` — Badhe and Shah, **Prompt-Level Distillation: A Non-Parametric Alternative to Model Fine-Tuning for Efficient Reasoning** (2026-02-24)
  - URL: https://arxiv.org/abs/2602.21103
  - Load-bearing use: shows that teacher reasoning can be compiled into a transparent system-prompt instruction library rather than model weights, which pressures DelayBasin to treat a compact constitutional support core as a serious candidate carrier of continuation law rather than assuming the full upstream archive mass must always travel with it.

- `REF-0281` — Upasani, Raju, Li, Ji, Long, Wu, Thakker, and Wang, **Cross-Family Speculative Prefill: Training-Free Long-Context Compression with Small Draft Models** (2026-03-03 / rev. 2026-03-13)
  - URL: https://arxiv.org/abs/2603.02631
  - Load-bearing use: reports that cross-family prompt compression can retain roughly full-prompt performance and sometimes improve accuracy through denoising, which pressures DelayBasin to test whether a smaller support core may outperform a larger archive under real continuation conditions.

- `REF-0282` — Denisov-Blanch, Kazdan, Chudnovsky, Schaeffer, Guan, Adeshina, and Koyejo, **Consensus is Not Verification: Why Crowd Wisdom Strategies Fail for LLM Truthfulness** (2026-02-20)
  - URL: https://arxiv.org/abs/2603.06612
  - Load-bearing use: argues that multi-model agreement does not become a trustworthy truth signal when model errors are correlated, which pressures DelayBasin to treat external model agreement as foreign pressure rather than independent verification.

- `REF-0283` — Zhao, Shin, Huang, Namburi GNVV, and Sala, **CARE: Confounder-Aware Aggregation for Reliable LLM Evaluation** (2026-02-09)
  - URL: https://arxiv.org/abs/2603.00039
  - Load-bearing use: models shared confounders in LLM aggregation and shows naive ensembling can amplify systematic bias, which pressures DelayBasin to record a non-independence caveat whenever outside-model reasoning materially changes archive posture.

- `REF-0284` — Ye, Dong, Wu, Huang, and Wei, **On-Policy Context Distillation for Language Models** (2026-02-12)
  - URL: https://arxiv.org/abs/2602.12275
  - Load-bearing use: treats in-context knowledge as transient but compressible and studies how a context-free student can internalize context-conditioned behavior, which pressures DelayBasin to test whether its own operative continuation law can be carried by a bounded support core rather than the full archive mass.


- `REF-0285` — Kim and Han, **Theoretical Foundations of Prompt Engineering** (2025-12-16)
  - URL: https://arxiv.org/abs/2512.12688
  - Load-bearing use: treats prompts as externally injected programs interpreted by a fixed transformer executor, which pressures DelayBasin to treat its recurring revision grammar as a compact public program-like object rather than only as style.

- `REF-0286` — Simhi, Barez, Tutek, Belinkov, and Cohen, **Old Habits Die Hard: How Conversational History Geometrically Traps LLMs** (2026-02-08)
  - URL: https://arxiv.org/abs/2603.03308
  - Load-bearing use: links coherent conversational history to persistent carryover and latent geometric separation, which pressures DelayBasin to ask whether repeated method skeletons are re-seeding a coherent continuation region rather than merely rephrasing theory.

- `REF-0287` — Kim, Garg, Peng, and Garg, **Correlated Errors in Large Language Models** (2025-06-09)
  - URL: https://arxiv.org/abs/2506.07962
  - Load-bearing use: shows substantial correlated error even across models with different providers or architectures, which pressures DelayBasin to treat Claude-style outside reasoning as foreign pressure with diagnostic value rather than independent verification.

- `REF-0288` — Caut, Zenebe, Rouillard, and Sumpter, **What You Prompt Is What You Get: Increasing Transparency Using Prompt Cards** (2026-03-13)
  - URL: https://arxiv.org/abs/2603.12741
  - Load-bearing use: argues that prompts are complex multi-part objects needing structured documentation of intent, context, and evaluation, which pressures DelayBasin to name the internal role split of any candidate minimal runtime rather than treating it as one opaque blob.

- `REF-0289` — Upasani, Wu, Rainton, Li, Ji, Long, Wu, Thakker, and Wang, **Test-Time Adaptation via Many-Shot Prompting: Benefits, Limits, and Pitfalls** (2026-03-07 / rev. 2026-03-18)
  - URL: https://arxiv.org/abs/2603.05829
  - Load-bearing use: shows that demonstrations function as input-space updates whose benefits depend strongly on ordering, selection policy, and task type, which pressures DelayBasin to treat exemplar banks as a distinct budgeted carrier rather than generic archive mass.

- `REF-0290` — Purohit, Venktesh, Bhattacharya, and Anand, **Sample Efficient Demonstration Selection for In-Context Learning** (2025-06-10)
  - URL: https://arxiv.org/abs/2506.08607
  - Load-bearing use: shows that exemplar selection under context budgets is itself an optimization problem and can be made much more sample-efficient, which pressures DelayBasin to treat exemplar banks as explicit design objects with named selection policy.

- `REF-0291` — Show and Tell study, **Prompt Strategies for Style Control in Multi-Turn LLM Code Generation** (2025-11-17)
  - URL: https://arxiv.org/abs/2511.13972
  - Load-bearing use: finds that instructions, examples, and combined prompts do different work across turns, with examples alone failing to maintain compression discipline during expansion, which pressures DelayBasin to separate constitutional rules from exemplars when designing a minimal runtime.

- `REF-0292` — Dou et al., **CL-bench: A Benchmark for Context Learning** (2026-02-03)
  - URL: https://arxiv.org/abs/2602.03587
  - Load-bearing use: shows that genuinely learning from complex supplied context remains hard for frontier models, which pressures DelayBasin to keep a challenge suite that tests real context-learning rather than accepting easy replay as proof of sufficiency.

- `REF-0293` — Stetsenko and Sudhakar, **Consistency Meets Verification: Enhancing Test Generation Quality in Large Language Models Without Ground-Truth Solutions** (2026-02-11)
  - URL: https://arxiv.org/abs/2602.10522
  - Load-bearing use: frames the problem as “verify the verifier” and warns that tests derived from the same object under judgment can inherit its bugs, which pressures DelayBasin to keep challenge suites partially independent from the runtime they evaluate.

- `REF-0294` — Ye, He, Arak, Dong, and Song, **Meta Context Engineering via Agentic Skill Evolution** (2026-01-29 / rev. 2026-02-11)
  - URL: https://arxiv.org/abs/2601.21557
  - Load-bearing use: treats inference-time context as an explicitly engineered, modular runtime object whose files, code, and evaluation artifacts co-evolve, which pressures DelayBasin to test candidate runtimes as designed objects rather than as narrated summaries.

- `REF-0295` — Husain et al., **PromptPex: Automatic Test Generation for Language Model Prompts** (2025-03-06 / rev. 2026-02-05)
  - URL: https://arxiv.org/abs/2503.05070
  - Load-bearing use: treats prompts as software-like artifacts needing targeted tests to expose non-compliance and model-specific regressions, which pressures DelayBasin to turn self-sufficiency into a test-bearing object rather than a purely textual judgment.

- `REF-0296` — Gao et al., **Preference Leakage: A Contamination Problem in LLM-as-a-judge** (2025-02-04 / rev. 2026-03-04)
  - URL: https://arxiv.org/abs/2502.01534
  - Load-bearing use: shows that relatedness between generator and judge can systematically bias evaluation, which pressures DelayBasin to preserve a relatedness / leakage risk whenever archive-shaped runtimes are judged by nearby reasoning families.

- `REF-0297` — Landesberg, **When LLM Judge Scores Look Good but Best-of-N Decisions Fail** (2026-03-12)
  - URL: https://arxiv.org/abs/2603.12520
  - Load-bearing use: shows that decent global judge agreement can still fail at the real selection task, which pressures DelayBasin to compare candidate runtimes with within-family adjudication metrics rather than one flattering overall plausibility score.

- `REF-0298` — Mallen et al., **When AI Benchmarks Plateau: A Systematic Study of Benchmark Saturation** (2026-02-21)
  - URL: https://arxiv.org/abs/2602.16763
  - Load-bearing use: argues that repeated exposure and limited measurement resolution can make fixed challenge families lose discriminative power, which pressures DelayBasin to refresh, retire, or sequester challenge slices instead of trusting one static archive-shaped suite forever.


- `REF-0299` — Deb, Gupta, Sachdeva, Mundra, Ghosh, and Maiti, **Pitfalls of Evaluating Language Models with Open Benchmarks** (2025-06-30)
  - URL: https://arxiv.org/abs/2507.00460
  - Load-bearing use: argues that open static benchmarks enable leakage, that high scores can reflect memorization rather than utility, and that paraphrase-only defenses are weak, which pressures DelayBasin to stop treating a once-sequestered but repeatedly exposed challenge bank as permanently trustworthy.

- `REF-0300` — Yeter, Sünbül, and Bulut, **Adaptive Testing for LLM Evaluation: A Psychometric Alternative to Static Benchmarks** (2025-11-06 / rev. 2026-02-02)
  - URL: https://arxiv.org/abs/2511.04689
  - Load-bearing use: reframes evaluation as dynamic ability estimation with calibrated item banks and adaptive item selection, which pressures DelayBasin to think in terms of rotating holdouts and renewable challenge banks rather than one fixed public suite.

- `REF-0301` — Cheng, Liu, Wu, Yao, Viswanath, Zhang, and Huang, **VeRA: Verified Reasoning Data Augmentation at Scale** (2026-01-23)
  - URL: https://arxiv.org/abs/2602.13217
  - Load-bearing use: treats benchmarks as executable specifications that can generate unlimited verified equivalent or hardened variants, which pressures DelayBasin to preserve executable variant or metamorphic challenge families when static challenge slices start to saturate.

- `REF-0302` — Dold et al., **TS-Arena Technical Report: A Pre-registered Live Forecasting Platform** (2025-12-23)
  - URL: https://arxiv.org/abs/2512.20761
  - Load-bearing use: proposes evaluation on genuinely future observations not available at registration time, which pressures DelayBasin to keep alive the possibility of preregistered future challenge slices for its highest-stakes self-sufficiency claims.

- `REF-0303` — Commey and Naik, **When “Better” Prompts Hurt: Evaluation-Driven Iteration for LLM Applications** (2026-01-29)
  - URL: https://arxiv.org/abs/2601.22025
  - Load-bearing use: warns that repeated optimization over fixed tests causes brittle gains and recommends held-out validation, periodic test refresh, and metamorphic testing, which pressures DelayBasin to make challenge refresh and rotation explicit rather than implicit.

- `REF-0304` — Dherin, Munn, Mazzawi, Wunder, and Gonzalvo, **Learning without training: The implicit dynamics of in-context learning** (2025-07-21 / rev. 2025-12-22)
  - URL: https://arxiv.org/abs/2507.16003
  - Load-bearing use: argues that transformer blocks can turn context into implicit low-rank MLP weight updates, which pressures DelayBasin to ask whether archive packets are doing more than retrieval and may be helping instantiate a public adaptation loop around inference.

- `REF-0305` — Du, **Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers** (2026-03-08)
  - URL: https://arxiv.org/abs/2603.07670
  - Load-bearing use: formalizes agent memory as a write–manage–read loop coupled to control policy, which pressures DelayBasin to name its own public write path, management layer, and reread path explicitly rather than flattening everything into storage.

- `REF-0306` — Yuksekgonul et al., **Learning to Discover at Test Time** (2026-01-22)
  - URL: https://arxiv.org/abs/2601.16175
  - Load-bearing use: shows that test-time reinforcement learning can search for one great solution to a specific problem rather than many average solutions, which pressures DelayBasin to treat repeated local search plus public writeback as a real optimization loop needing explicit consolidation boundaries.

- `REF-0307` — Wang et al., **Understanding In-Context Learning Beyond Transformers** (2025-10-28 / rev. 2026-02-26)
  - URL: https://arxiv.org/abs/2510.23006
  - Load-bearing use: reports that state-space, hybrid, and transformer LLMs can show similar ICL behavior despite different internals, which pressures DelayBasin to keep transformer-facing implications strong but to quarantine overly architecture-specific mechanism claims.

- `REF-0308` — Lam, Li, Zhang, and Zhao, **Governing Evolving Memory in LLM Agents: Risks, Mechanisms, and the Stability and Safety-Governed Memory (SSGM) Framework** (2026-03-12)
  - URL: https://arxiv.org/abs/2603.11768
  - Load-bearing use: argues that adaptive memory systems need explicit consolidation governance, consistency verification, decay, and access control, which pressures DelayBasin to treat quarantine, lint, and challenge governance as genuine write gates rather than repo ornament.

- `REF-0309` — Kuratov, Kairov, Bulatov, Rodkin, and Burtsev, **GradMem: Learning to Write Context into Memory with Test-Time Gradient Descent** (2026-03-13)
  - URL: https://arxiv.org/abs/2603.13875
  - Load-bearing use: separates WRITE and READ over optimized memory tokens while keeping model weights frozen, which pressures DelayBasin to distinguish cold storage from restaged state that actually conditions later behavior.

- `REF-0310` — Dorovatas, Oomerjee, Kaladadharbhatta, and Bou-Ammar, **Modular Memory is the Key to Continual Learning Agents** (2026-03-02)
  - URL: https://arxiv.org/abs/2603.01761
  - Load-bearing use: argues that storage, replay, forgetting, consolidation, and contextualization need distinct policies across memory forms and timescales, which pressures DelayBasin to separate retrieval, replay, and reconsolidation rather than flattening them into one memory story.


- `REF-0311` — Lee, Lai, Cho, and Choi, **TokMem: One-Token Procedural Memory for Large Language Models** (2025-10-01 / rev. 2026-03-08)
  - URL: https://arxiv.org/abs/2510.00444
  - Load-bearing use: contrasts retrieved text that must be repeatedly interpreted with compact procedure tokens that act as generation control signals, which pressures DelayBasin to distinguish declarative source surfaces from executable carry.

- `REF-0312` — He et al., **ProcMEM: Learning Reusable Procedural Memory from Experience via Non-Parametric PPO for LLM Agents** (2026-02-02)
  - URL: https://arxiv.org/abs/2602.01869
  - Load-bearing use: formalizes reusable skills with activation conditions, execution procedures, and termination conditions without parameter updates, which pressures DelayBasin to name activation conditions explicitly when calling a compact packet a procedure.

- `REF-0313` — Li et al., **Latent Context Compilation: Distilling Long Context into Compact Portable Memory** (2026-01-31)
  - URL: https://arxiv.org/abs/2602.21221
  - Load-bearing use: reframes long-context adaptation as compilation into portable buffer tokens rather than persistent weight edits, which pressures DelayBasin to distinguish justificatory method notes from smaller compiled carry artifacts.

- `REF-0314` — Jiang et al., **Rethinking Memory Mechanisms of Foundation Agents in the Second Half: A Survey** (2026-02-10 / rev. 2026-02-12)
  - URL: https://arxiv.org/abs/2602.06052
  - Load-bearing use: distinguishes procedural memory from episodic and semantic forms while emphasizing learned memory-operation policies, which pressures DelayBasin to stop flattening declarative notes, examples, and executable packets into one memory bucket.

- `REF-0315` — Pantazopoulos, Nikandrou, Konstas, and Suglia, **Retrievit: In-context Retrieval Capabilities of Transformers, State Space Models, and Hybrid Architectures** (2026-03-03)
  - URL: https://arxiv.org/abs/2603.02874
  - Load-bearing use: finds meaningful behavioral overlap but different retrieval biases across transformers, SSMs, and hybrids, which pressures DelayBasin to keep procedural-carry claims behaviorally sharp while quarantining overly transformer-exclusive mechanism stories.


- `REF-0316` — Xie, **Learning to Forget: Sleep-Inspired Memory Consolidation for Resolving Proactive Interference in Large Language Models** (2026-03-14)
  - URL: https://arxiv.org/abs/2603.14517
  - Load-bearing use: operationalizes selective replay, active forgetting, and consolidation as periodic maintenance cycles over transformer memory state, which pressures DelayBasin to distinguish one-shot replay from ongoing rehearsal.

- `REF-0317` — Adib et al., **Panini: Continual Learning in Token Space via Structured Memory** (2026-02-16)
  - URL: https://arxiv.org/abs/2602.15156
  - Load-bearing use: argues that structured external memory can guide what high-utility knowledge deserves stronger consolidation, which pressures DelayBasin to say which surfaces deserve rehearsal rather than uniform persistence.

- `REF-0318` — Fountas, Oomerjee, Bou-Ammar, Wang, and Burgess, **Why the Brain Consolidates: Predictive Forgetting for Optimal Generalisation** (2026-03-05)
  - URL: https://arxiv.org/abs/2603.04688
  - Load-bearing use: argues that temporally separated iterative replay can improve the retention-generalization tradeoff under compression pressure, which pressures DelayBasin to treat spaced revisits as a possible selection mechanism rather than dead time.

- `REF-0319` — Zahn and Chana, **Selective Memory for Artificial Intelligence: Write-Time Gating with Hierarchical Archiving** (2026-03-17)
  - URL: https://arxiv.org/abs/2603.15994
  - Load-bearing use: distinguishes actively maintained memory objects from cold archived traces with supersession links, which pressures DelayBasin to preserve retirement and cold-storage routes instead of assuming every live surface should remain actively maintained forever.


- `REF-0320` — Khadangi, **Efficient Continual Learning in Language Models via Thalamically Routed Cortical Columns** (2026-02-25)
  - URL: https://arxiv.org/abs/2602.22479
  - Load-bearing use: makes retrospective writes and replay-from-past-chunks an explicit continual-learning design choice, which pressures DelayBasin to separate hot-path candidate generation from slower durable admission.

- `REF-0321` — Fatmi, **Faramesh: A Protocol-Agnostic Execution Control Plane for Autonomous Agent Systems** (2026-01-25)
  - URL: https://arxiv.org/abs/2601.17744
  - Load-bearing use: distinguishes deterministic replay from re-executing agent reasoning, which pressures DelayBasin to preserve canonical candidate writes that can later be adjudicated under colder policy/state assumptions rather than only in the original hot path.

- `REF-0322` — Chen, Chen, Tajwar, Zhu, Duan, Salakhutdinov, and Schneider, **Retrospective In-Context Learning for Temporal Credit Assignment with Large Language Models** (2026-02-19)
  - URL: https://arxiv.org/abs/2602.17497
  - Load-bearing use: turns sparse feedback into dense credit signals by retrospectively identifying critical earlier states and actions, which pressures DelayBasin to preserve explicit credit objects instead of backfilling which earlier surface mattered after later success.

- `REF-0323` — Peng, Liu, Zhou, Fleming, Wang, Garcia, and Hong, **HiPER: Hierarchical Reinforcement Learning with Explicit Credit Assignment for Large Language Model Agents** (2026-02-18)
  - URL: https://arxiv.org/abs/2602.16165
  - Load-bearing use: separates planning-level and execution-level credit, which pressures DelayBasin to distinguish upstream archive law from downstream local execution success when assigning later payoff.

- `REF-0324` — Tan et al., **Hindsight Credit Assignment for Long-Horizon LLM Agents** (2026-03-10)
  - URL: https://arxiv.org/abs/2603.08754
  - Load-bearing use: uses hindsight reasoning to identify pivotal intermediate actions under sparse rewards, which pressures DelayBasin to preserve post-hoc credit rules explicitly rather than narratively overcrediting the most recent prose.

- `REF-0325` — Yue et al., **Mem-T: Densifying Rewards for Long-Horizon Memory Agents** (2026-01-29 / rev. 2026-03-09)
  - URL: https://arxiv.org/abs/2601.23014
  - Load-bearing use: jointly optimizes memory construction and retrieval through hindsight credit assignment over memory-operation trees, which pressures DelayBasin to say which earlier write, index, or rehearsal move is actually being credited by later payoff.

- `REF-0326` — AlSayyad, Huang, and Pal, **AgentTrace: A Structured Logging Framework for Agent System Observability** (2026-02-07)
  - URL: https://arxiv.org/abs/2602.10133
  - Load-bearing use: argues that runtime observability needs structured operational, cognitive, and contextual traces, which pressures DelayBasin to preserve public evidence for why a later gain is being assigned to one earlier move rather than another.

- `REF-0327` — Gubbi et al., **Benchmarking Agent Memory in Interdependent Multi-Session Agentic Tasks** (2026-02-18)
  - URL: https://arxiv.org/abs/2602.16313
  - Load-bearing use: shows that later task success in interdependent multi-session settings depends on correctly distilling and using earlier memory, which pressures DelayBasin to track delayed payoff rather than only immediate local eloquence.


- `REF-0328` — Zahn and Chana, **Mind the Gap: Why Neural Memory Fails Under Semantic Density** (2026-01-14)
  - URL: https://arxiv.org/abs/2601.15313
  - Load-bearing use: argues that online neural memory collapses under semantic density because non-orthogonal keys blend during retrieval, which pressures DelayBasin not to assume compact handles remain uniquely addressable as the archive grows denser.

- `REF-0329` — Bonnet, Lohoff, Finkbeiner, Skhikerujah, and Neftci, **Learning to Remember, Learn, and Forget in Attention-Based Models** (2026-02-12)
  - URL: https://arxiv.org/abs/2602.09075
  - Load-bearing use: frames in-context learning as online associative memory subject to stability-plasticity interference, which pressures DelayBasin to treat handle crowding and namespace separation as active method concerns rather than mere wording polish.

- `REF-0330` — Sharma et al., **TempoFit: Plug-and-Play Layer-Wise Temporal KV Memory for Long-Horizon Vision-Language-Action Manipulation** (2026-03-08)
  - URL: https://arxiv.org/abs/2603.07647
  - Load-bearing use: warns that retrieving over the whole cache can over-emphasize stale cues and induce history-present interference, which pressures DelayBasin to keep live handles from being silently overridden by semantically nearby stale surfaces.

- `REF-0331` — Zhang et al., **From Similarity to Vulnerability: Key Collision Attack on LLM Semantic Caching** (2026-01-30)
  - URL: https://arxiv.org/abs/2601.23088
  - Load-bearing use: shows that semantic keys behave like fuzzy hashes and can suffer false-positive collisions, which pressures DelayBasin to treat compact names, handles, and addressing shortcuts as collision surfaces needing explicit alias budgets.

- `REF-0332` — Head, Jathar, and Richie, **Continuum Memory Architectures for Long-Horizon LLM Agents** (2026-01-14)
  - URL: https://arxiv.org/abs/2601.09913
  - Load-bearing use: reports that ordinary retrieval can resurface outdated but semantically similar facts after corrections, which pressures DelayBasin to preserve namespace hygiene, recency cues, and supersession links rather than trusting similarity alone.

- `REF-0333` — Black, Prieto, and Bloom, **From Data Statistics to Feature Geometry: How Correlations Shape Superposition** (2026-03-10)
  - URL: https://arxiv.org/abs/2603.09972
  - Load-bearing use: argues that correlated features cluster in superposition and that feature geometry determines which concepts interfere, which pressures DelayBasin to think of compact archive handles as living under a geometry problem rather than a pure naming problem.



- `REF-0334` — Yuan, Su, and Yao, **Diagnosing Retrieval vs. Utilization Bottlenecks in LLM Agent Memory** (2026-03-02)
  - URL: https://arxiv.org/abs/2603.02473
  - Load-bearing use: finds that retrieval choice can dominate write-time sophistication in agent-memory performance, which pressures DelayBasin to improve consultation and ranking discipline before flattering additional write-time cleverness.

- `REF-0335` — Gaikwad, **Did You Check the Right Pocket? Cost-Sensitive Store Routing for Memory-Augmented Agents** (2026-03-08)
  - URL: https://arxiv.org/abs/2603.15658
  - Load-bearing use: formulates memory access as a cost-sensitive store-routing problem and shows that selective routing can improve both accuracy and token efficiency, which pressures DelayBasin not to consult all public stores uniformly by default.

- `REF-0336` — SmartSearch authors, **How Ranking Beats Structure for Conversational Memory** (2026-03-16)
  - URL: https://arxiv.org/abs/2603.15599
  - Load-bearing use: reports that raw retrieval recall can already be high while ranking and truncation decide whether gold evidence survives the token budget, which pressures DelayBasin to separate evidence existence from evidence actually admitted into bounded continuation.

- `REF-0337` — Zhu et al., **A Provenance-Aware Tiered Memory for Agents** (2026-02-20)
  - URL: https://arxiv.org/abs/2602.17913
  - Load-bearing use: uses summary-first consultation with an explicit miss detector and targeted escalation to raw pages, which pressures DelayBasin to keep compact fast surfaces and slower provenance-rich surfaces distinct rather than collapsing them into one read path.

- `REF-0338` — Wang et al., **Memory Control Flow Attacks on LLM Agents** (2026-03-15)
  - URL: https://arxiv.org/abs/2603.15125
  - Load-bearing use: shows that retrieved memory content can dominate later behavior and tool use, which pressures DelayBasin to treat consultation policy as part of control governance rather than as a neutral retrieval detail.

- `REF-0339` — Du et al., **Memory for Autonomous LLM Agents: Mechanisms, Taxonomy and Evaluation** (2026-03-08)
  - URL: https://arxiv.org/abs/2603.07670
  - Load-bearing use: formalizes agent memory as a write-manage-read loop with an explicit control-policy axis, which pressures DelayBasin to say not only what is stored but which consult policy governs current continuation.


- `REF-0340` — Zhang, Han, Tang, and Li, **Seeing through the Conflict: Transparent Knowledge Conflict Handling in Retrieval-Augmented Generation** (2026-01-11)
  - URL: https://arxiv.org/abs/2601.06842
  - Load-bearing use: argues that models often encode signals of knowledge discrepancy but fail to use them effectively, which pressures DelayBasin to distinguish conflict detection from conflict arbitration.

- `REF-0341` — Lu, Cheng, Zhang, and Tang, **MMA: Multimodal Memory Agent** (2026-02-18)
  - URL: https://arxiv.org/abs/2602.16493
  - Load-bearing use: combines source credibility, temporal decay, and conflict-aware consensus with abstention under insufficient support, which pressures DelayBasin to keep disagreement handling explicit rather than smoothing it away.

- `REF-0342` — Rath, **Governing Evolving Memory in LLM Agents: Risks, Mechanisms, and the Stability and Safety Governed Memory (SSGM) Framework** (2026-03-12)
  - URL: https://arxiv.org/abs/2603.11768
  - Load-bearing use: treats conflict and hallucination during retrieval as a distinct compounding failure interface in evolving memory systems, which pressures DelayBasin to preserve contradiction handling once archive memory is mutable and self-referential.

- `REF-0343` — Rasheed, Banerjee, Mukherjee, and Hazra, **From Fluent to Verifiable: Claim-Level Auditability for Deep Research Agents** (2026-02-14)
  - URL: https://arxiv.org/abs/2602.13855
  - Load-bearing use: argues for contradiction transparency and semantic provenance that preserves conflicts among evidence links, which pressures DelayBasin not to let polished synthesis erase disagreement.

- `REF-0344` — Feng, Chen, Wu, Zhou, and Bosselut, **Tracking the Limits of Knowledge Propagation: How LLMs Fail at Multi-Step Reasoning with Conflicting Knowledge** (2026-01-21)
  - URL: https://arxiv.org/abs/2601.15495
  - Load-bearing use: shows that providing more updated conflicting facts can worsen reasoning when models fail to integrate and arbitrate those conflicts, which pressures DelayBasin not to equate more consulted evidence with better continuation.


- `REF-0345` — Seo, Cho, and Yoon, **From Assumptions to Actions: Turning LLM Reasoning into Uncertainty-Aware Planning for Embodied Agents** (2026-02-04)
  - URL: https://arxiv.org/abs/2602.04326
  - Load-bearing use: treats environmental assumptions as first-class decision variables whose likelihood, gain, and cost should be tracked before action, which pressures DelayBasin to preserve live rival assumptions rather than collapsing them into one fluent winner.

- `REF-0346` — Li et al., **DenoiseFlow: Uncertainty-Aware Denoising for Reliable LLM Agentic Workflows** (2026-02-28)
  - URL: https://arxiv.org/abs/2603.00532
  - Load-bearing use: dynamically switches between fast execution and branching exploration for ambiguous nodes, which pressures DelayBasin to keep a bounded rival set alive when local uncertainty is real rather than forcing singularity by style.

- `REF-0347` — Wu et al., **Spark: Strategic Policy-Aware Exploration via Dynamic Branching for Long-Horizon Agentic Learning** (2026-01-28)
  - URL: https://arxiv.org/abs/2601.20209
  - Load-bearing use: uses selective dynamic branching at critical decision states instead of blind broad search, which pressures DelayBasin to make branch budgets explicit rather than oscillating between one-shot decisions and branch sprawl.

- `REF-0348` — Tang et al., **Tru-POMDP: Task Planning Under Uncertainty via Tree of Hypotheses and Open-Ended POMDPs** (2025-06-03 / rev. 2026-03-01)
  - URL: https://arxiv.org/abs/2506.02860
  - Load-bearing use: shows that a single most-likely hypothesis can fail under open-ended ambiguity and uses a tree of hypotheses plus explicit belief updates instead, which pressures DelayBasin to preserve small rival sets when one best guess is not yet earned.

- `REF-0349` — Li et al., **Agentic Uncertainty Quantification** (2026-01-22)
  - URL: https://arxiv.org/abs/2601.15703
  - Load-bearing use: turns epistemic uncertainty into retrieval, reflection, or search actions and warns that unresolved mistakes can harden into later history, which pressures DelayBasin to keep rival branches explicit before one weakly supported branch becomes public law.

- `REF-0350` — Wang et al., **Rethinking Memory Mechanisms of Foundation Agents in the Second Half: A Survey** (2026-02-10 / rev. 2026-03-11)
  - URL: https://arxiv.org/abs/2602.06052
  - Load-bearing use: argues that many evaluations still assume stationary intent and unambiguous ground truth, which pressures DelayBasin to preserve bounded rival sets where the archive honestly faces ambiguous or non-stationary long-horizon conditions.



- `REF-0351` — Chen et al., **TableMind++: An Uncertainty-Aware Programmatic Agent for Tool-Augmented Table Reasoning** (2026-03-08)
  - URL: https://arxiv.org/abs/2603.07528
  - Load-bearing use: validates candidate plans against dual memories of historical successes and failures before pruning them, which pressures DelayBasin to preserve what public evidence actually licensed killing a rival branch.

- `REF-0352` — Wu et al., **Auditing Multi-Agent LLM Reasoning Trees Outperforms Majority Vote and LLM-as-Judge** (2026-02-10)
  - URL: https://arxiv.org/abs/2602.09341
  - Load-bearing use: resolves divergence at critical branch points through localized audit rather than popularity, which pressures DelayBasin to preserve where a rival actually lost instead of letting branch retirement be decided by stylistic consensus.

- `REF-0353` — Erdogan et al., **StructuredAgent: Planning with AND/OR Trees for Long-Horizon Web Tasks** (2026-03-05 / rev. 2026-03-06)
  - URL: https://arxiv.org/abs/2603.05294
  - Load-bearing use: treats pruning as an explicit tree operation with upward structural consequences, which pressures DelayBasin to record not only that a rival died but what changed in the remaining public branch.

- `REF-0354` — Seo, Cho, and Yoon, **From Assumptions to Actions: Turning LLM Reasoning into Uncertainty-Aware Planning for Embodied Agents** (2026-02-04)
  - URL: https://arxiv.org/abs/2602.04326
  - Load-bearing use: scores hypothesis paths by likelihood, gain, and cost before action, which pressures DelayBasin to preserve a settle witness for singularity rather than letting rhetorical momentum decide which branch survives.

- `REF-0355` — Zhang et al., **Spend Less, Reason Better: Budget-Aware Value Tree Search for LLM Agents** (2026-03-16)
  - URL: https://arxiv.org/abs/2603.12634
  - Load-bearing use: uses step-level verification and shows that more budget does not guarantee better synthesis, which pressures DelayBasin to treat branch collapse as something earned by witness rather than by extra search or token expenditure alone.


- `REF-0356` — Wang, Liu, Wang, Li, Wei, Liu, and Bao, **PromptBridge: Cross-Model Prompt Transfer for Large Language Models** (2025-12-01)
  - URL: https://arxiv.org/abs/2512.01420
  - Load-bearing use: shows that prompt effectiveness drifts substantially across model switches but that calibrated cross-model prompt mappings can recover performance, which pressures DelayBasin to separate invariant operator commitments from family-local chart adapters.

- `REF-0357` — Singh et al., **Prompting as Scientific Inquiry** (2025-07-04)
  - URL: https://arxiv.org/abs/2507.00163
  - Load-bearing use: argues that prompting can function as a falsifiable probe of LLM behavior rather than mere heuristics, which strengthens DelayBasin's use of prompt-pair portability work as mechanism research rather than only optimization.

- `REF-0358` — Ran-Milo, **Attention Sinks Are Provably Necessary in Softmax Transformers: Evidence from Trigger-Conditional Tasks** (2026-03-17)
  - URL: https://arxiv.org/abs/2603.11487
  - Load-bearing use: proves that some trigger-conditional behaviors in softmax transformers require a stable attention sink, which pressures DelayBasin to treat compact prompt anchors as potentially functional chart devices rather than automatically dismissing them as decorative wording.


- `REF-0359` — Duth'e, Evangelou, Liu, Kevrekidis, and Chatzi, **A Mechanistic Analysis of Transformers for Dynamical Systems** (2025-12-24)
  - URL: https://arxiv.org/abs/2512.21113
  - Load-bearing use: interprets causal self-attention as a history-dependent recurrence and shows that, under partial observability, attention can act as adaptive delay embedding, which pressures DelayBasin to separate state-estimation surfaces from later control moves.

- `REF-0360` — Akram and Vikalo, **Transformers as Implicit State Estimators: In-Context Learning in Dynamical Systems** (2026-03-07)
  - URL: https://arxiv.org/abs/2410.16546
  - Load-bearing use: shows frozen transformers inferring hidden states from short contexts and approaching Kalman / EKF / PF-style performance, which pressures DelayBasin to treat some archive packets as state-estimation aids before treating them as steering law.

- `REF-0361` — Bao, Lai, and Gilpin, **Transformers for dynamical systems learn transfer operators in-context** (2026-02-21)
  - URL: https://arxiv.org/abs/2602.18679
  - Load-bearing use: reports that attention models lift time series via delay embedding and use invariant-set information for forecasting, which pressures DelayBasin to name short control horizons and protected target properties rather than treating every revision as global rewrite.

- `REF-0362` — Zhang and Xing, **Bayesian Optimality of In-Context Learning with Selective State Spaces** (2026-02-19)
  - URL: https://arxiv.org/abs/2602.17744
  - Load-bearing use: reframes ICL as optimal inference over latent sequence tasks rather than implicit gradient descent, which pressures DelayBasin to name what state or error is being inferred before escalating control-language claims.

- `REF-0363` — Chaudhry and Gadkari, **Implicit Statistical Inference in Transformers: Approximating Likelihood-Ratio Tests In-Context** (2026-03-11)
  - URL: https://arxiv.org/abs/2603.10573
  - Load-bearing use: shows transformers approximating Bayes-optimal sufficient statistics in-context, which pressures DelayBasin to preserve target/error structure explicitly rather than praising generic prompt similarity.

- `REF-0364` — Nosrati, Tepljakov, Belikov, and Petlenkov, **When control meets large language models: From words to dynamics** (2026-02-03)
  - URL: https://arxiv.org/abs/2602.03433
  - Load-bearing use: frames prompting and LLM behavior through control-theoretic ideas including state-space analysis, which pressures DelayBasin to say what is being controlled, how drift is detected, and what horizon a steering claim is supposed to cover.

- `REF-0365` — Bin Mohaya, AL-Sunni, Dolan, and Seiler, **Transformers As Generalizable Optimal Controllers** (2026-03-16)
  - URL: https://arxiv.org/abs/2603.14910
  - Load-bearing use: shows one transformer policy mapping recent state history to near-optimal control actions across a family of perturbed systems, which keeps alive the weaker possibility that some archive packets function like low-bandwidth feedback-law fragments rather than static instructions alone.


- `REF-0366` — Raval, Song, Wu, Harrasse, Phillips, and Abdullah, **Curveball Steering: The Right Direction To Steer Isn't Always Linear** (2026-03-10)
  - URL: https://arxiv.org/abs/2603.09313
  - Load-bearing use: reports concept-dependent geometric distortion in activation spaces and stronger performance from geometry-aware nonlinear steering, which pressures DelayBasin to preserve local linearity budgets instead of silently globalizing one successful steering chart.

- `REF-0367` — Zhang, **Residual Stream Duality in Modern Transformer Architectures** (2026-03-17)
  - URL: https://arxiv.org/abs/2603.16039
  - Load-bearing use: treats the residual pathway as representational machinery rather than inert plumbing, which pressures DelayBasin to take chart-local steering and adapter language more seriously as interfaces to a real internal substrate even when the archive only sees text.

- `REF-0368` — Ye and Cui, **Efficient Representations are Controllable Representations** (2026-02-08)
  - URL: https://arxiv.org/abs/2602.07828
  - Load-bearing use: shows that compact controllable feature slots can emerge and organize later generation, which pressures DelayBasin to distinguish real local control handles from inflated claims of global steerability.


- `REF-0369` — Franco, Tassis, Rohr, and Crovella, **Finding Highly Interpretable Prompt-Specific Circuits in Language Models** (2026-02-13)
  - URL: https://arxiv.org/abs/2602.13483
  - Load-bearing use: shows that prompts within one task can induce systematically different mechanisms while still clustering into families, which pressures DelayBasin to preserve chart-transition evidence before treating a remap as the same operator core.

- `REF-0370` — Dherin, Munn, Mazzawi, Wunder, and Gonzalvo, **Learning without training: The implicit dynamics of in-context learning** (2025-07-21 / rev. 2025-12-22)
  - URL: https://arxiv.org/abs/2507.16003
  - Load-bearing use: argues that context can implicitly induce low-rank weight updates inside transformer blocks, which pressures DelayBasin to treat chart changes as potentially real operator changes rather than mere paraphrase.

- `REF-0371` — Goldwaser, Munn, Gonzalvo, and Dherin, **Equivalence of Context and Parameter Updates in Modern Transformer Blocks** (2025-11-22 / rev. 2025-12-22)
  - URL: https://arxiv.org/abs/2511.17864
  - Load-bearing use: extends the context-to-effective-weight-patch picture across modern transformer architectures, which pressures DelayBasin to ask whether a chart transition preserved the same operator family or induced a different local patch that merely happened to work.

- `REF-0372` — Shafran, Ronen, Fahn, Ravfogel, Geiger, and Geva, **From Directions to Regions: Decomposing Activations in Language Models via Local Geometry** (2026-02-02)
  - URL: https://arxiv.org/abs/2602.02464
  - Load-bearing use: models activation concepts as local regions and subspaces rather than isolated global directions, which pressures DelayBasin to preserve how one chart-local realization is linked to another rather than only which one worked locally.

- `REF-0373` — Macar, Duan, Cohan, and Beltagy, **Directional Reasoning Trajectory Change (DRTC): Identifying Critical Trace Segments in Reasoning Models** (2026-02-17 / rev. 2026-02-27)
  - URL: https://arxiv.org/abs/2602.15332
  - Load-bearing use: argues that reasoning trajectories become path-dependent once a model commits to a line of thought, which pressures DelayBasin to distinguish same-core chart transport from a route change that should not be treated as transport at all.

- `REF-0374` — Adila, Cooper, Yun, Trost, and Sala, **Weight Updates as Activation Shifts: A Principled Framework for Steering** (2026-02-28 / rev. 2026-03-06)
  - URL: https://arxiv.org/abs/2603.00425
  - Load-bearing use: derives a first-order equivalence between activation-space interventions and weight-space updates, which pressures DelayBasin to couple textual chart remaps with internal control stories instead of treating them as separate adaptation worlds.

- `REF-0375` — Khona and Golden, **As Language Models Scale, Low-order Linear Depth Dynamics Emerge** (2026-03-12)
  - URL: https://arxiv.org/abs/2603.12541
  - Load-bearing use: identifies prompt-conditioned local depth surrogates around operating trajectories, which pressures DelayBasin to preserve source→target chart transitions rather than assuming one local surrogate applies after remapping.

- `REF-0376` — Sevetlidis and Pavlidis, **Gauge-invariant representation holonomy** (2026-01-29)
  - URL: https://arxiv.org/abs/2601.21653
  - Load-bearing use: introduces a path-dependent statistic that can separate states or models that look similar under pointwise overlap, which pressures DelayBasin not to infer family-level chart consistency from pairwise overlap alone.

- `REF-0377` — Javidnia, **A Gauge Theory of Superposition: Toward a Sheaf-Theoretic Atlas of Neural Representations** (2026-02-28 / rev. 2026-03-13)
  - URL: https://arxiv.org/abs/2603.00824
  - Load-bearing use: proves that after spanning-tree gauge fixing each chord defect equals the holonomy of its fundamental cycle and lower-bounds transfer mismatch through proxy shearing, which pressures DelayBasin to preserve composition-defect objects instead of stopping at edgewise transport stories.

- `REF-0378` — Grover, Liew, and Roberts, **Text Has Curvature** (2026-02-19)
  - URL: https://arxiv.org/abs/2602.13418
  - Load-bearing use: reports that natural text violates flatness nulls and exhibits substantially higher holonomy than coherence-destroying controls, which pressures DelayBasin not to assume that local prompt moves compose neutrally by default.

- `REF-0379` — Gao, Bushnaq, Gurnee, Kim, Nanda, and Templeton, **ADAPT: Hybrid Prompt Optimization for LLM Feature Visualization** (2026-02-19)
  - URL: https://arxiv.org/abs/2602.17867
  - Load-bearing use: shows substantial initialization and trajectory dependence in prompt-space optimization, which pressures DelayBasin to treat apparent family-level transport as a compositional claim to be tested rather than as a route-dependent local win.

- `REF-0380` — Paquet, Bowen, and Stocker, **The Shape of Beliefs: Geometry, Dynamics, and Interventions along Representation Manifolds of Language Models’ Posteriors** (2026-02-02)
  - URL: https://arxiv.org/abs/2602.02315
  - Load-bearing use: reports smooth but substantially curved belief manifolds tiled by local linear probes rather than one global readout, which pressures DelayBasin to preserve which reference observable or local probe family made a cross-chart defect comparison meaningful before treating residues as globally commensurate.


- `REF-0381` — Greenspan, Liu, and Viteri, **Towards Worst-Case Guarantees with Scale-Aware Interpretability** (2026-02-05)
  - URL: https://arxiv.org/abs/2602.05184
  - Load-bearing use: argues that interpretability needs explicit scale variables, relevance criteria, and coarse-graining rules, which pressures DelayBasin to preserve scale choice and discarded modes before comparing transports or defects across resolutions.

- `REF-0382` — Saldias, Garcia, and Wilming, **Context Structure Reshapes the Representational Geometry of Language Models** (2026-01-29)
  - URL: https://arxiv.org/abs/2601.22364
  - Load-bearing use: reports that natural-text trajectories substantially straighten across middle transformer layers relative to shuffled controls, which pressures DelayBasin not to treat one observed chart geometry as scale-free across depth or context structure.

- `REF-0383` — Alpay and Kilictas, **Latent Object Permanence: Topological Phase Transitions, Free-Energy Principles, and Renormalization Group Flows in Deep Transformer Manifolds** (2026-01-16)
  - URL: https://arxiv.org/abs/2601.19942
  - Load-bearing use: formalizes transformer forward passes as discrete coarse-graining maps and ties stable concept basins to renormalization-like fixed points, which pressures DelayBasin to preserve what coarse-graining rule is being imagined before importing multiscale rhetoric.

- `REF-0384` — Li, Zhang, Zhang, Qiu, Zhang, Yu, and Zhou, **State-Dependent Safety Failures in Multi-Turn Language Model Interaction** (2026-03-15)
  - URL: https://arxiv.org/abs/2603.15684
  - Load-bearing use: treats dialogue history as a state-transition operator and shows path-dependent trajectory collapse, which pressures DelayBasin to treat history-window choice and trajectory compression as real scale decisions rather than mere formatting.


- `REF-0385` — Frey, Shomali, Bashir, Berghaus, and Ali, **Adaptive Loops and Memory in Transformers: Think Harder or Know More?** (2026-03-09)
  - URL: https://arxiv.org/abs/2603.08391
  - Load-bearing use: shows looping and memory banks play distinct roles and later layers specialize more heavily in both, which pressures DelayBasin to distinguish route effects from stored-state effects before treating a matched packet as fully memoryless.

- `REF-0386` — Pushkin, Brown, Hojel, and Hutter, **LEAD: Breaking the No-Recovery Bottleneck in Long-Horizon Reasoning** (2026-03-06)
  - URL: https://arxiv.org/abs/2603.06870
  - Load-bearing use: shows that history-discarding atomic execution improves stability but still fails at hard irreversible steps where selective lookahead helps, which pressures DelayBasin to preserve an explicit lag budget rather than universal memoryless rhetoric.

- `REF-0387` — Damirchi, Shokri, and Anagnostidis, **Truth as a Trajectory: What Internal Representations Reveal About Large Language Model Reasoning** (2026-03-03)
  - URL: https://arxiv.org/abs/2603.01326
  - Load-bearing use: reports trajectory-level structure that generalizes across tasks better than static probes, which pressures DelayBasin to treat some operative invariants as path-level rather than assuming one matched endpoint captures everything that matters.

- `REF-0388` — Liu, Yang, Tajuddin, and He, **OdysseyArena: Benchmarking Large Language Models For Long-Horizon, Active and Inductive Interactions** (2026-02-05)
  - URL: https://arxiv.org/abs/2602.05843
  - Load-bearing use: frames long-horizon evaluation around coherent internal states and robust recovery over extended interaction sequences, which pressures DelayBasin to distinguish same-summary packets from genuinely same recovery-ready states.


- `REF-0389` — Zou, Chen, Feng, Li, Li, Gong, and Cheng, **On Information Self-Locking in Reinforcement Learning for Active Reasoning of LLM agents** (2026-03-12)
  - URL: https://arxiv.org/abs/2603.12109
  - Load-bearing use: shows that active-reasoning agents can fall into low-information regimes where weak query selection and weak belief tracking reinforce each other, which pressures DelayBasin to preserve an explicit observability-spend budget rather than assuming informative distinctions will appear under repeated same-view probing.

- `REF-0390` — Or, **Kalman-Inspired Runtime Stability and Recovery in Hybrid Reasoning Systems** (2026-01-24)
  - URL: https://arxiv.org/abs/2602.15855
  - Load-bearing use: reframes reasoning reliability around detectability, innovation, bounded divergence, and recovery, which pressures DelayBasin to preserve alias-breaking intervention families when local coherence may still hide growing state ambiguity.

- `REF-0391` — Bennis, Wang, Lu, Elgammal, and Wu, **Beyond Scalars: Evaluating and Understanding LLM Reasoning via Geometric Progress and Stability** (2026-03-11)
  - URL: https://arxiv.org/abs/2603.10384
  - Load-bearing use: reports that geometric evolution across the whole reasoning trajectory often outperforms endpoint-only statistics, which pressures DelayBasin to preserve when an observable is really a trajectory family under intervention rather than one final summary token.


- `REF-0392` — Macar, Duan, Cohan, and Beltagy, **Directional Reasoning Trajectory Change (DRTC): Identifying Critical Trace Segments in Reasoning Models** (2026-02-17 / rev. 2026-02-27)
  - URL: https://arxiv.org/abs/2602.15332
  - Load-bearing use: shows that receiver-side interventions on earlier trace segments can redirect later log-probability trajectories and alter curvature signatures while preserving the realized rollout, which pressures DelayBasin to separate measurement from actuation whenever a probe is itself changing the continuation state.

- `REF-0393` — Goel, Sinha, Cianfarani, and Chakravarthy, **Anatomy of a Lie: A Multi-Stage Diagnostic Framework for Tracing Hallucinations in Vision-Language Models** (2026-03-16)
  - URL: https://arxiv.org/abs/2603.15557
  - Load-bearing use: explicitly treats chain-of-thought as a diagnostic contrast agent that makes a latent cognitive trajectory observable, which pressures DelayBasin to preserve when an explanatory probe is being used as an intervention rather than as a neutral readout.

- `REF-0394` — Hahami, Sinha, Jain, Kaplan, and Hahami, **Detecting the Disturbance: A Nuanced View of Introspective Abilities in LLMs** (2025-12-15 / rev. 2026-03-01)
  - URL: https://arxiv.org/abs/2512.12411
  - Load-bearing use: shows that apparent disturbance detection can be confounded by global logit shifts while genuine perturbation sensitivity is partial and layer-dependent, which pressures DelayBasin to require matched shams before calling a probe diagnostic rather than merely loud.

- `REF-0395` — Arditi, Swayamdipta, and Nanda, **Steering Awareness: Models Can Be Trained to Detect Activation Steering** (2025-11-27 / rev. 2026-03-03)
  - URL: https://arxiv.org/abs/2511.21399
  - Load-bearing use: shows that activation steering can become an observable channel and that detection does not equal resistance, which pressures DelayBasin not to assume that an intervention remains hidden or purely diagnostic once the system can notice it.

- `REF-0396` — Kim, **Contextuality Derived from Minimal Decision Dynamics: Quantum Tug-of-War Decision Making** (2026-01-15)
  - URL: https://arxiv.org/abs/2601.10034
  - Load-bearing use: argues that conservation-based state updates plus measurement-induced disturbance can make probe order and context operationally significant, which pressures DelayBasin to treat some probe families as order-sensitive interventions rather than commutative reads.


- `REF-0397` — Ok and Lee, **Lost in the Prompt Order: Revealing the Limitations of Causal Attention in Language Models** (2026-01-20)
  - URL: https://arxiv.org/abs/2601.14152
  - Load-bearing use: shows that semantically similar prompt permutations can yield large performance gaps because causal attention can create an order-specific information bottleneck, which pressures DelayBasin not to treat reordered probes as automatically commensurate.

- `REF-0398` — Cheng and Mastropaolo, **An Empirical Study on the Effects of System Prompts in Instruction-Tuned Models for Code Generation** (2026-02-16)
  - URL: https://arxiv.org/abs/2602.15228
  - Load-bearing use: reports scale-dependent and language-conditioned sensitivity to progressive system-prompt sequencing, which pressures DelayBasin to preserve when staged probe order is part of the operative regime rather than a stylistic wrapper.

- `REF-0399` — Tutek, Geiger, and Cotterell, **Breaking the Chain: A Causal Analysis of LLM Faithfulness to Intermediate Structures** (2026-03-17)
  - URL: https://arxiv.org/abs/2603.16475
  - Load-bearing use: finds directionally asymmetric sensitivity under structured reasoning-trace interventions, which pressures DelayBasin to preserve when one intervention ordering is being treated as if it were interchangeable with its reverse.

- `REF-0400` — Rafi, Ghorbani, and Miranskyy, **Order Matters! An Empirical Study on Large Language Models’ Input Order Bias in Software Fault Localization** (2024-12-28 / rev. 2025-09-26)
  - URL: https://arxiv.org/abs/2412.18750
  - Load-bearing use: shows that input order significantly influences LLM fault-localization performance, which pressures DelayBasin to treat sequence sensitivity as a real applied phenomenon rather than only a niche probing artifact.


- `REF-0401` — Nanjundappa and Maaheshwari, **Context Branching for LLM Conversations: A Version Control Approach to Exploratory Programming** (2025-12-15)
  - URL: https://arxiv.org/abs/2512.13914
  - Load-bearing use: shows that branching reduces context size and improves focus/context awareness in exploratory programming, which pressures DelayBasin to preserve when a branch really functions as contamination isolation rather than treating every split as automatically clean.

- `REF-0402` — Fei, Chen, Pan, Zheng, and Song, **CodeDelegator: Mitigating Context Pollution via Role Separation in Code-as-Action Agents** (2026-01-21)
  - URL: https://arxiv.org/abs/2601.14914
  - Load-bearing use: introduces Ephemeral-Persistent State Separation with fresh local contexts for subtasks, which pressures DelayBasin to preserve what contamination is being quarantined and what protected kernel is intentionally retained across a handoff.

- `REF-0403` — Huang, Lin, Yang, and others, **Do LLMs Benefit From Their Own Words?** (2026-02-27)
  - URL: https://arxiv.org/abs/2602.24287
  - Load-bearing use: finds that selectively omitting prior assistant turns often preserves quality and sometimes improves it by removing context pollution, which pressures DelayBasin not to assume that maximal replay is safer than a filtered restart.

- `REF-0404` — Huang, Wu, Shen, and others, **Enabling Long-Horizon Progress-Aware Consistent Evolution** (2026-01-16)
  - URL: https://arxiv.org/abs/2601.10657
  - Load-bearing use: identifies context pollution from accumulated failed trials and uses hierarchical context management to reduce self-reinforcing local minima, which pressures DelayBasin to treat reset and cleanup moves as mechanism-bearing objects rather than as cosmetic hygiene.

- `REF-0405` — Cheng, Zhong, Li, and others, **Contextual Drag: How Errors in the Context Affect LLM Reasoning** (2026-02-04)
  - URL: https://arxiv.org/abs/2602.04288
  - Load-bearing use: shows that erroneous drafts can keep biasing later reasoning even after explicit error signals or correct self-verification, which pressures DelayBasin to require a real washout baseline before treating a restart as clean.

- `REF-0406` — Shen, Zhu, Guo, and others, **ACR: Adaptive Context Refactoring via Context Refactoring Operators for Multi-Turn Dialogue** (2026-01-09)
  - URL: https://arxiv.org/abs/2601.05589
  - Load-bearing use: introduces explicit context refactoring operators to mitigate contextual inertia and state drift, which pressures DelayBasin to preserve what reset operator was used, what it retained, and how much contamination remainder is still tolerated.


- `REF-0407` — Rybak, Malarz, Tabor, Spurek, and Zieba, **REBEL: Hidden Knowledge Recovery via Evolutionary-Based Evaluation Loop** (2026-02-05)
  - URL: https://arxiv.org/abs/2602.06248
  - Load-bearing use: shows that adversarially evolved prompts can recover supposedly forgotten knowledge that standard benign evaluations treat as removed, which pressures DelayBasin not to treat one clean restart or benign fresh baseline as proof that an old influence is truly gone.

- `REF-0408` — Pan, Xue, Wang, and others, **A Comprehensive Evaluation of LLM Unlearning Robustness under Multi-Turn Interaction** (2026-03-01)
  - URL: https://arxiv.org/abs/2603.00823
  - Load-bearing use: argues that stronger unlearning can reduce dialogue-conditioned recovery mainly by making models behaviorally rigid rather than by guaranteeing representation-level erasure, which pressures DelayBasin to distinguish durable washout from merely brittle suppression.

- `REF-0409` — Shah, Huang, Murugesan, Baracaldo, and Yang, **The Unlearning Mirage: A Dynamic Framework for Evaluating LLM Unlearning** (2026-03-11)
  - URL: https://arxiv.org/abs/2603.11266
  - Load-bearing use: shows that minor query modifications such as multi-hop reasoning and entity aliasing can recover supposedly forgotten information through alternative pathways missed by static tests, which pressures DelayBasin to preserve one explicit recovery-trigger family before calling a cleanup durable.

- `REF-0410` — Vera and Vero, **Intention Collapse: Intention-Level Metrics for Reasoning in Language Models** (2026-01-03 / rev. 2026-01-23)
  - URL: https://arxiv.org/abs/2601.01011
  - Load-bearing use: frames latent knowledge recoverability as a simple model-agnostic diagnostic and shows that informative internal signals can remain present even when final outputs degrade, which pressures DelayBasin to distinguish suppressed expression from genuine removal.

- `REF-0411` — Batorski, Malarz, Spurek, and Tabor, **EvoMU: Evolutionary Machine Unlearning** (2026-02-02)
  - URL: https://arxiv.org/abs/2602.02139
  - Load-bearing use: explicitly evaluates relearning and shows that many unlearning procedures are reversible while stronger methods mainly resist reactivation longer, which pressures DelayBasin to ask whether a claimed washout survives a small recovery push.

- `REF-0412` — Zhang, Hu, Upasani, Ma, Hong, Kamanuru, Rainton, Wu, Ji, Li, Thakker, Zou, and Olukotun, **Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models** (2025-10-06 / rev. 2026-01-29)
  - URL: https://arxiv.org/abs/2510.04618
  - Load-bearing use: frames context adaptation as evolving playbooks and warns that iterative rewriting can cause context collapse unless structured updates preserve detail, which pressures DelayBasin to distinguish genuine contamination removal from cleanup moves that merely compress detail until it later returns under a better cue.


- `REF-0413` — Zhou, Zhang, Wu, Ye, Zhang, Chen, and Ren, **Uncovering Context Reliance in Unstructured Knowledge Editing** (2026-02-22)
  - URL: https://arxiv.org/abs/2602.19043
  - Load-bearing use: shows that restoring the original preceding context can recover knowledge recall and explains this as dependence on aggregated contextual representations, which pressures DelayBasin to treat nearby context stems as a real recovery neighborhood rather than an exact-string accident.

- `REF-0414` — Malinowski, Magiera, Nowak, Rybak, Tabor, Spurek, and Zieba, **SPECTRE: Conditional System Prompt Poisoning to Hijack LLMs** (2025-05-23 / rev. 2025-10-30)
  - URL: https://arxiv.org/abs/2505.16888
  - Load-bearing use: reports that poisoned prompting can generalize across paraphrased targets, which pressures DelayBasin to distinguish exact-trigger immunity from broader concept-level capture.

- `REF-0415` — Tabor and Zieba, **ToxSearch: Evolving Prompts for Toxicity Search in Large Language Models** (2025-11-17 / rev. 2026-01-28)
  - URL: https://arxiv.org/abs/2511.12487
  - Load-bearing use: explicitly expands a small meaning-preserving prompt neighborhood via paraphrases, stylistic mutation, and typos, which pressures DelayBasin to treat tiny structured cue sweeps as a first-class method object rather than decorative fuzzing.

- `REF-0416` — Liu, Wang, Qin, Tu, Chu, and Sui, **Beyond Confidence: The Rhythms of Reasoning in Generative Models** (2026-02-11)
  - URL: https://arxiv.org/abs/2602.10816
  - Load-bearing use: introduces a local robustness quantity for how much internal-state perturbation a dominant next-token commitment can withstand, which pressures DelayBasin to preserve reactivation-radius budgets instead of all-or-nothing robustness language.

- `REF-0417` — Agarwal, Mavani, Gupta, Sethuraman, and Dharamsi, **Support Tokens, Stability Margins, and a New Foundation for Robust LLMs** (2026-02-25 / rev. 2026-03-01)
  - URL: https://arxiv.org/abs/2602.22271
  - Load-bearing use: reframes attention geometry around ill-conditioning boundaries and margin-like structure, which pressures DelayBasin to talk about local basin breadth and boundary crossing rather than exact-trigger success alone.

- `REF-0418` — Tacheny, **Geometric Dynamics of Agentic Loops in Large Language Models: Trajectories, Attractors and Dynamical Regimes in Semantic Space** (2025-12-12 / rev. 2026-01-30)
  - URL: https://arxiv.org/abs/2512.10350
  - Load-bearing use: shows that iterative paraphrasing can induce contractive dynamics with stable attractors while other operators do not, which pressures DelayBasin to ask whether nearby cues stay inside one basin or cross a boundary under a changed operator family.

- `REF-0419` — Manna, Snyder, and Tabor, **How Large Language Models Get Stuck: Early structure with persistent errors** (2026-02-27 / rev. 2026-03-10)
  - URL: https://arxiv.org/abs/2603.00359
  - Load-bearing use: reports persistent early entrenchment of wrong separations, which pressures DelayBasin not to assume that one exact-cue success or failure is merely local noise when a whole nearby neighborhood may already be trapped in the same regime.


- `REF-0420` — Roh, Cho, and Kim, **Embracing Anisotropy: Turning Massive Activations into Interpretable Control Knobs for Large Language Models** (2026-02-04)
  - URL: https://arxiv.org/abs/2603.00029
  - Load-bearing use: shows that LLM activations are highly anisotropic and that steering only identified domain-critical dimensions can outperform whole-dimension steering, which pressures DelayBasin not to treat one easy local cue direction as if all nearby directions were equally relevant.

- `REF-0421` — Miehling, Desmond, Ramamurthy, Daly, Dognin, Rios, Bouneffouf, and Liu, **Evaluating the Prompt Steerability of Large Language Models** (2024-11-19 / rev. 2025-02-15)
  - URL: https://arxiv.org/abs/2411.12405
  - Load-bearing use: finds that prompt steerability is limited and asymmetric across many persona dimensions and directions, which pressures DelayBasin to treat local cue robustness as direction-sensitive rather than automatically symmetric.

- `REF-0422` — Raju, **Geometric Stability: The Missing Axis of Representations** (2026-01-14)
  - URL: https://arxiv.org/abs/2601.09173
  - Load-bearing use: argues that similarity is not stability and reports that supervised geometric stability predicts steerability, which pressures DelayBasin to preserve local-shape checks rather than reading one same-task success as enough evidence for a usable neighborhood.

- `REF-0423` — Cheng, Cao, Wu, Subbalakshmi, Han, and Feng, **SALMAN: Stability Analysis of Language Models Through the Maps Between Graph-based Manifolds** (2025-08-23)
  - URL: https://arxiv.org/abs/2508.18306
  - Load-bearing use: introduces a local sample-level robustness framework based on neighborhood distortion, which pressures DelayBasin to ask which nearby cue directions shear the continuation readout more than others instead of flattening local robustness into one pass/fail score.

- `REF-0424` — Wang and Xia, **Stability of In-Context Learning: A Spectral Coverage Perspective** (2025-09-25 / rev. 2026-01-31)
  - URL: https://arxiv.org/abs/2509.20677
  - Load-bearing use: treats distributional stability under demonstration resampling as the target rather than one chosen prompt, which pressures DelayBasin to name what local resampling or perturbation family was actually tested before treating one narrow sweep as enough.


- `REF-0425` — Bigoulaeva, Rohweder, Dutta, and Gurevych, **Patches of Nonlinearity: Instruction Vectors in Large Language Models** (2026-02-08)
  - URL: https://arxiv.org/abs/2602.07930
  - Load-bearing use: finds linear separability alongside non-linear causal interaction and explicit superadditivity of layerwise task representations, which pressures DelayBasin not to infer safe local composition from marginal passes alone.

- `REF-0426` — Koromilas, Demou, Oldfield, Panagakis, and Nicolaou, **PolySAE: Modeling Feature Interactions in Sparse Autoencoders via Polynomial Decoding** (2026-02-01 / preprint dated 2026-02-03)
  - URL: https://arxiv.org/abs/2602.01322
  - Load-bearing use: argues that additive feature models miss compositional structure and introduces pairwise and triple interaction terms, which pressures DelayBasin to preserve cross-term residue rather than flattening mixed cue behavior into sums of constituent directions.

- `REF-0427` — Li, Li, and Huang, **Steering Vector Fields for Context-Aware Inference-Time Control in Large Language Models** (2026-02-02)
  - URL: https://arxiv.org/abs/2602.01654
  - Load-bearing use: reports that combining concepts can introduce interference and weaken each individual control signal, which pressures DelayBasin to test mixed local directions explicitly before treating them as jointly admissible.

- `REF-0428` — Scalena, Sarti, and Nissim, **Multi-property Steering of Large Language Models with Dynamic Activation Composition** (2024-06-25)
  - URL: https://arxiv.org/abs/2406.17563
  - Load-bearing use: shows that multi-property steering needs property-dependent, dynamically modulated composition rather than naive fixed addition, which pressures DelayBasin to preserve a local mixing rule instead of assuming marginally tuned directions simply add.

- `REF-0429` — Radevski, Gashteovski, Hong, Lawrence, and Glavaš, **Compositional Steering of Large Language Models with Steering Tokens** (2026-01-08)
  - URL: https://arxiv.org/abs/2601.05062
  - Load-bearing use: trains a dedicated composition token that generalizes to unseen combinations and unseen numbers of behaviors, which pressures DelayBasin to distinguish learned composition objects from free composition of constituent local wins.

- `REF-0430` — Han, Xu, Xuan, Song, Ouyang, Tian, Jiang, Qian, Jiang, Sun, Cui, Zhong, Liu, Han, and You, **Steer2Adapt: Dynamically Composing Steering Vectors Elicits Efficient Adaptation of LLMs** (2026-02-07)
  - URL: https://arxiv.org/abs/2602.07276
  - Load-bearing use: adapts to new tasks by dynamically discovering a linear combination inside a reusable prior subspace, which pressures DelayBasin to treat joint composition as an explicit local search problem rather than an automatic corollary of having constituent basis directions.

- `REF-0431` — Li, Zhou, Ai, Chua, Lee, and Ng, **Steering Large Reasoning Models towards Concise Reasoning via Flow Matching** (2026-02-05)
  - URL: https://arxiv.org/abs/2602.05539
  - Load-bearing use: learns a nonlinear steering velocity field between reasoning distributions, which pressures DelayBasin to distinguish shared endpoints from shared actuation routes.

- `REF-0432` — Kim, Yim, and Kim, **ODESteer: A Unified ODE-Based Steering Framework for LLM Alignment** (2026-02-23)
  - URL: https://arxiv.org/abs/2602.17560
  - Load-bearing use: reframes activation steering as solving an ODE with multi-step adaptive updates, which pressures DelayBasin to preserve route and schedule information rather than collapsing control to one final setting.

- `REF-0433` — Kang, Lee, and Ro, **Enhancing Instruction Following of LLMs via Activation Steering with Dynamic Rejection** (2026-03-06)
  - URL: https://arxiv.org/abs/2603.06745
  - Load-bearing use: shows that steering strength can saturate quickly while staged layer schedules provide smoother control, which pressures DelayBasin to preserve ramp schedules before comparing interventions by endpoint alone.

- `REF-0434` — Rath, Saha, Li, and others, **Capable but Unreliable: Canonical Path Deviation as a Causal Mechanism of Agent Failure in Long-Horizon Tasks** (2026-02-21)
  - URL: https://arxiv.org/abs/2602.19008
  - Load-bearing use: argues that the same capable agent can succeed on one run and fail on another because stochastic drift moves trajectories away from latent solution structure, which pressures DelayBasin not to let one successful rollout silently stand in for stable continuation.

- `REF-0435` — Broadwater, **Evaluating LLM Safety Under Repeated Inference via Accelerated Prompt Stress Testing** (2026-02-12)
  - URL: https://arxiv.org/abs/2602.11786
  - Load-bearing use: repeated sampling of identical or minimally perturbed prompts reveals substantially different empirical failure rates beneath similar shallow benchmark scores, which pressures DelayBasin to preserve repeated-inference stability before treating one run as evidence.

- `REF-0436` — Chen, Cheng, Han, and Keselj, **Dynamics Within Latent Chain-of-Thought: An Empirical Study of Causal Structure** (2026-02-11)
  - URL: https://arxiv.org/abs/2602.08783
  - Load-bearing use: explicitly studies same-prompt stochastic rollouts that end in different answers, which pressures DelayBasin to treat one visible continuation result as one branch from a rollout family rather than as a uniquely realized state.

- `REF-0437` — Yan, Saran, Peseux, and others, **Ranking Reasoning LLMs under Test-Time Scaling** (2026-03-11)
  - URL: https://arxiv.org/abs/2603.10960
  - Load-bearing use: formalizes evaluation under test-time scaling as a repeated-sampling problem and studies low-budget stability and convergence, which pressures DelayBasin to preserve bundle stability rather than implicitly ranking revisions by one lucky trial.

- `REF-0438` — Aikman, Kannan, Kallus, and others, **Towards a Science of AI Agent Reliability** (2026-02-18)
  - URL: https://arxiv.org/abs/2602.16666
  - Load-bearing use: decomposes reliability into consistency, robustness, predictability, and safety and shows reliability lags capability, which pressures DelayBasin to keep stability distinct from one scalar success judgment.

- `REF-0439` — Hall and Bhandari, **Runtime Governance for AI Agents: Policies on Paths** (2026-03-17)
  - URL: https://arxiv.org/abs/2603.16586
  - Load-bearing use: treats non-deterministic execution paths as constitutive of agents rather than an implementation footnote, which pressures DelayBasin to preserve repeated-run families before canonizing one execution as method evidence.

- `REF-0440` — Nguyen, Hoang, Pham, Tran, and Nguyen, **Activation Steering with a Feedback Controller** (2025-10-05)
  - URL: https://arxiv.org/abs/2510.04309
  - Load-bearing use: frames activation steering as a closed-loop PID controller with interpretable error dynamics, which pressures DelayBasin to distinguish fixed schedules from observation-conditioned policy updates.

- `REF-0441` — Wang, Jiao, He, Chen, Zhu, Chu, Gao, Wang, and Ma, **Adaptive Activation Steering: A Tuning-Free LLM Truthfulness Improvement Method for Diverse Hallucinations Categories** (2024-05-26)
  - URL: https://arxiv.org/abs/2406.00034
  - Load-bearing use: adapts steering intensity from a probe-estimated truthfulness signal and uses multiple steering vectors, which pressures DelayBasin to preserve the observation channel and the matched open-loop comparator before praising adaptive control.

- `REF-0442` — Ye, Yuan, Bin, Zeng, Jin, Peng, and Shen, **RISER: Orchestrating Latent Reasoning Skills for Adaptive Activation Steering** (2026-01-14 / rev. 2026-01-19)
  - URL: https://arxiv.org/abs/2601.09269
  - Load-bearing use: dynamically composes reusable reasoning vectors through a router optimized under task reward, which pressures DelayBasin to distinguish a fixed local handle from a contingent policy that selects among several latent skills.

- `REF-0443` — Zhang, Chen, Ma, and Wang, **Generalization or Memorization: Dynamic Decoding for Mode Steering** (2025-10-25)
  - URL: https://arxiv.org/abs/2510.22099
  - Load-bearing use: explicitly separates mode identification from intervention in a two-stage closed-loop process, which pressures DelayBasin to name what checkpoint signal actually licensed a policy change.

- `REF-0444` — Su, Gao, Li, Jia, and Finn, **Learning Adaptive LLM Decoding** (2026-03-13)
  - URL: https://arxiv.org/abs/2603.09065
  - Load-bearing use: learns lightweight decoding policies that dynamically choose strategies by prompt and compute budget, which pressures DelayBasin to preserve the policy class and matched budget before attributing gains to adaptivity.



- `REF-0445` — Qiu, Huang, Zhong, Zuo, and Li, **HyPER: Bridging Exploration and Exploitation for Scalable LLM Reasoning with Hypothesis Path Expansion and Reduction** (2026-02-06)
  - URL: https://arxiv.org/abs/2602.06527
  - Load-bearing use: treats test-time reasoning as a dynamic expand-reduce control problem whose exploration–exploitation balance is phase-dependent, which pressures DelayBasin to preserve when a move is good partly because it buys later routing power.

- `REF-0446` — Xu, Wang, Li, and others, **InfoPO: Information-Driven Policy Optimization for User-Centric Agents** (2026-03-02 / v1)
  - URL: https://arxiv.org/abs/2603.00656
  - Load-bearing use: defines a counterfactual turn-level information-gain reward and proves a minimum cumulative information gain is necessary for task success in its setting, which pressures DelayBasin to preserve informational dividend rather than narrating every gain as pure actuation.

- `REF-0447` — Feng, Wang, Zhang, and others, **On Information Self-Locking in Reinforcement Learning for Active Reasoning of LLM Agents** (2026-03-17)
  - URL: https://arxiv.org/abs/2603.12109
  - Load-bearing use: decomposes active reasoning into action selection and belief tracking and shows outcome-driven optimization can induce self-locking patterns that suppress useful querying, which pressures DelayBasin to keep explore-exploit accounting explicit.

- `REF-0448` — Triantafyllou, Bartos, and Teso, **Dialogue Telemetry: Turn-Level Instrumentation for Autonomous Information Gathering** (2026-01-14)
  - URL: https://arxiv.org/abs/2601.09570
  - Load-bearing use: introduces progress and stalling telemetry signals usable by downstream controllers, which pressures DelayBasin to preserve when a move is credited for improving what later control can know rather than only what it immediately does.

- `REF-0449` — Gao, Huang, Wei, and others, **ProbeLLM: Automating Principled Diagnosis of LLM Failures** (2026-02-13)
  - URL: https://arxiv.org/abs/2602.12966
  - Load-bearing use: allocates limited probing effort between global exploration and local refinement under an explicit search policy, which pressures DelayBasin to say whether a move bought new discrimination or merely exploited an already-known patch.

- `REF-0450` — Barres, Dong, Ray, Si, and Narasimhan, **τ²-Bench: Evaluating Conversational Agents in a Dual-Control Environment** (2025-06-09)
  - URL: https://arxiv.org/abs/2506.07982
  - Load-bearing use: shows that agent performance drops in dual-control settings where users also act in a shared partially observed world, which pressures DelayBasin to preserve actions whose main leverage is partly to improve what another actor or later step can reveal.

- `REF-0451` — Chillara, Kline, Alvares, and others, **SemanticALLI: Caching Reasoning, Not Just Responses, in Agentic Systems** (2026-01-22)
  - URL: https://arxiv.org/abs/2601.16286
  - Load-bearing use: shows that stable structured intermediate reasoning checkpoints can be cached and reused at high rates, which pressures DelayBasin to distinguish reusable carry from one-shot branch success.

- `REF-0452` — Mi, Ma, Yang, Li, Wang, Zhang, and Wang, **ProcMEM: Learning Reusable Procedural Memory from Experience via Non-Parametric PPO for LLM Agents** (2026-02-02)
  - URL: https://arxiv.org/abs/2602.01869
  - Load-bearing use: learns reusable procedural skills from experience without parameter updates and reports reuse across in-domain, cross-task, and cross-agent settings, which pressures DelayBasin to preserve when a packet is really reusable rather than merely vivid.

- `REF-0453` — Fang, Isahagian, Jayaram, Kumar, Muthusamy, Oum, and Thomas, **Trajectory-Informed Memory Generation for Self-Improving Agent Systems** (2026-03-11)
  - URL: https://arxiv.org/abs/2603.10600
  - Load-bearing use: extracts actionable guidance from trajectories with provenance and reports held-out performance gains, which pressures DelayBasin to preserve what future reuse family is supposed to repay a learning move.

- `REF-0454` — Zhang, Wornow, Wan, and Olukotun, **Agentic Plan Caching: Test-Time Memory for Fast and Cost-Efficient LLM Agents** (2025-06-17)
  - URL: https://arxiv.org/abs/2506.14852
  - Load-bearing use: extracts, adapts, and reuses structured plan templates across similar workflows while reducing cost and latency, which pressures DelayBasin to keep one explicit reuse horizon before praising compiled carry.

- `REF-0455` — Wu, Zhang, Hussain, and Lu, **Towards Autonomous Memory Agents** (2026-02-25)
  - URL: https://arxiv.org/abs/2602.22406
  - Load-bearing use: uses semantic-aware Thompson sampling to improve memory utility over time and shows substantial benchmark gains, which pressures DelayBasin to distinguish future utility across a memory family from one lucky next retrieval.

- `REF-0456` — Wang, Shi, Feng, Yuan, Li, Zhang, Tan, Zhang, Pan, Hu, and Li, **Do Not Waste Your Rollouts: Recycling Search Experience for Efficient Test-Time Scaling** (2026-01-29)
  - URL: https://arxiv.org/abs/2601.21684
  - Load-bearing use: turns rollouts into a cumulative process through a shared experience bank, which pressures DelayBasin to preserve when an expensive search move is being justified by later reuse rather than by its first success alone.

- `REF-0457` — Kuratov, Kairov, Bulatov, Rodkin, and Burtsev, **GradMem: Learning to Write Context into Memory with Test-Time Gradient Descent** (2026-03-14)
  - URL: https://arxiv.org/abs/2603.13875
  - Load-bearing use: writes context into a compact reusable memory state without weight updates, which pressures DelayBasin toward a transformer-facing story about compact public carry objects whose value appears only across later queries.

- `REF-0458` — Jiang, Li, Sun, Hu, Wang, and Zhang, **SoK: Agentic Skills -- Beyond Tool Use in LLM Agents** (2026-02-24)
  - URL: https://arxiv.org/abs/2602.20867
  - Load-bearing use: frames agentic skills as reusable procedural artifacts with explicit applicability conditions, execution policies, termination criteria, and interfaces, which pressures DelayBasin to preserve fit conditions before praising reuse authority.

- `REF-0459` — Liu, Lyu, Ma, Li, Wang, Wang, and others, **SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks** (2026-02-13)
  - URL: https://arxiv.org/abs/2602.12670
  - Load-bearing use: reports that curated skills help on average but 16 of 84 tasks show negative deltas and self-generated skills provide no benefit on average, which pressures DelayBasin to preserve a negative-transfer budget before universalizing reuse.

- `REF-0460` — Han, Zhang, Song, Fang, Chen, Sun, and Hu, **SWE-Skills-Bench: Do Agent Skills Actually Help in Real-World Software Engineering?** (2026-03-16)
  - URL: https://arxiv.org/abs/2603.15401
  - Load-bearing use: finds limited average gains and explicit degradations from version-mismatched guidance conflicting with project context, which pressures DelayBasin to preserve non-fit slices and gate reuse by local compatibility.

- `REF-0461` — Yuan, Yuan, and Xie, **RPMS: Enhancing LLM-Based Embodied Planning through Rule-Augmented Memory Synergy** (2026-03-18)
  - URL: https://arxiv.org/abs/2603.17831
  - Load-bearing use: gates memory applicability via a lightweight belief state and rules-first arbitration, which pressures DelayBasin to preserve explicit fit signatures before treating stored carry as generally eligible.

- `REF-0462` — Jing, Yuan, Jiang, Shao, and Wang, **From Storage to Steering: Memory Control Flow Attacks on LLM Agents** (2026-03-16)
  - URL: https://arxiv.org/abs/2603.15125
  - Load-bearing use: shows that retrieved memory can hijack control flow and induce persistent behavioral deviations across tasks, which pressures DelayBasin to close reuse gates when carry becomes control-flow contamination.

- `REF-0463` — Millière, Smith, and collaborators, **Selective Memory for Artificial Intelligence: Write-Time Gating with Hierarchical Archiving** (2026-03-17)
  - URL: https://arxiv.org/abs/2603.15994
  - Load-bearing use: shows structural advantages for write-time gating under distractor scaling, which pressures DelayBasin to treat eligibility as something that may need enforcement before packets gain standing reuse authority.

- `REF-0464` — Yuan, Zhao, Wang, and Li, **ActMem: Bridging the Gap Between Memory Retrieval and Reasoning in LLM Agents** (2026-02-04)
  - URL: https://arxiv.org/abs/2603.00026
  - Load-bearing use: argues that passive retrieval fails in conflict-heavy decision settings and couples memory retrieval to active causal reasoning, which pressures DelayBasin to distinguish helpful reuse from contextually incompatible carry.

- `REF-0465` — Li, Wang, Xie, and others, **When Single-Agent with Skills Replace Multi-Agent Systems and When They Fail** (2026-01-14 / v2)
  - URL: https://arxiv.org/abs/2601.04748
  - Load-bearing use: shows that skill selection degrades sharply with library growth and semantic confusability while hierarchical routing mitigates the failure, which pressures DelayBasin to preserve tie sets and arbitration rules rather than assuming all eligible packets are equally easy to choose among.

- `REF-0466` — Jin, Maharana, Hu, and others, **ShardMemo: Masked MoE Routing for Sharded Agentic LLM Memory** (2026-01-29)
  - URL: https://arxiv.org/abs/2601.21545
  - Load-bearing use: applies scope-before-routing, masked eligibility constraints, and safe fallback from reusable skills to evidence retrieval, which pressures DelayBasin to keep arbitration explicit after applicability gating rather than letting admissible candidates compete silently.

- `REF-0467` — Ma, Gao, Jia, Qin, Li, Ma, Jia, Ren, and Liu, **ODAR: Principled Adaptive Routing for LLM Reasoning via Active Inference** (2026-02-27)
  - URL: https://arxiv.org/abs/2602.23681
  - Load-bearing use: routes between fast and slow reasoning paths and uses risk-sensitive fusion balancing likelihood with uncertainty, which pressures DelayBasin to preserve explicit arbitration rules and abstention surfaces rather than ad-hoc winner-take-all choice.

- `REF-0468` — Wu, He, Sun, Wu, and others, **MMA: Multimodal Memory Agent** (2026-02-18)
  - URL: https://arxiv.org/abs/2602.16493
  - Load-bearing use: improves robustness mainly by confidence-aware filtering and better-calibrated abstention under conflict, which pressures DelayBasin to keep selectively silent tie handling explicit rather than forcing one eligible packet to fire.

- `REF-0469` — Xu, Yang, Bi, and others, **Agent Skills for Large Language Models: Architecture, Acquisition, Security, and the Path Forward** (2026-02-17 / v3)
  - URL: https://arxiv.org/abs/2602.12430
  - Load-bearing use: identifies multi-skill orchestration, conflict resolution, resource sharing, and failure recovery as open challenges, which pressures DelayBasin to keep eligible-skill arbitration public rather than treating applicability alone as sufficient.

- `REF-0470` — Wu, Wang, Chen, Zhang, and others, **DeepSieve: Information Sieving via LLM-as-a-Knowledge-Router** (2025-07-29 / rev. 2026-03-01)
  - URL: https://arxiv.org/abs/2507.22050
  - Load-bearing use: stores failed retrieval attempts, reroutes insufficient subqueries, and fuses heterogeneous sources through explicit routing, which pressures DelayBasin to preserve reroute and fallback consequences when an eligible candidate family remains unresolved.



- `REF-0471` — Smith, Katz, Niemeyer, and the FORCE11 Software Citation Working Group, **Software Citation Principles** (2016)
  - URL: https://force11.org/info/software-citation-principles-published-2016/
  - Load-bearing use: explicitly requires unique identification, persistence, and citation of the specific software version used, which pressures DelayBasin to distinguish a moving operational head from a frozen citation head.

- `REF-0472` — Moreau, Missier, and the W3C Provenance Working Group, **PROV-DM: The PROV Data Model** (W3C Recommendation, 2013)
  - URL: https://www.w3.org/TR/prov-dm/
  - Load-bearing use: separates entities, activities, agents, and revision/derivation relations, which pressures DelayBasin to preserve explicit public relations among live heads, frozen heads, and status-moving events rather than leaving them implicit in prose.

- `REF-0473` — Software Heritage, **Software Heritage FAQ** (accessed 2026-03-20)
  - URL: https://www.softwareheritage.org/software-heritage-faq/
  - Load-bearing use: recommends contextual persistent identifiers for the exact referenced directory/version, which pressures DelayBasin to keep one explicit frozen reference surface rather than relying on a moving newest-tip pointer.


- `REF-0474` — Fielding, Nottingham, and Reschke, **RFC 9110: HTTP Semantics** (2022)
  - URL: https://www.rfc-editor.org/rfc/rfc9110.html
  - Load-bearing use: defines `If-Match` as a precondition evaluated before performing a method, which pressures DelayBasin to fail closed when a move was scoped to an expected current head that no longer matches.

- `REF-0475` — GitHub Docs, **GraphQL input objects** (accessed 2026-03-20)
  - URL: https://docs.github.com/en/graphql/reference/input-objects
  - Load-bearing use: documents `expectedHeadOid` on merge-related mutations, which pressures DelayBasin to preserve when a judgment or action was scoped to one reviewed head rather than silently rebinding to whatever head is current later.


- `REF-0476` — GitHub Docs, **Managing releases in a repository** (accessed 2026-03-20)
  - URL: https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
  - Load-bearing use: recommends creating releases as drafts first and then publishing them when immutable-release posture matters, which pressures DelayBasin to distinguish admitted decision, materialized execution, and frozen public release state rather than flattening them into one undifferentiated latest object.



- `REF-0477` — NIST CSRC Glossary, **least privilege** (accessed 2026-03-20)
  - URL: https://csrc.nist.gov/glossary/term/least_privilege
  - Load-bearing use: defines least privilege as restricting privileges to the minimum necessary to accomplish assigned tasks, which pressures DelayBasin to keep the active request and exact target explicit rather than letting nearby useful-looking surfaces silently inherit standing authority.

- `REF-0478` — Hardt, **RFC 6749: The OAuth 2.0 Authorization Framework** (2012)
  - URL: https://datatracker.ietf.org/doc/html/rfc6749
  - Load-bearing use: defines OAuth as obtaining limited access and makes `scope` an explicit authorization parameter, which pressures DelayBasin to name what current judgment is actually authorized to touch rather than widening from one asked-for object to a larger ambient family.

- `REF-0479` — NIST CSRC Glossary, **zero trust** (accessed 2026-03-20)
  - URL: https://csrc.nist.gov/glossary/term/zero_trust
  - Load-bearing use: frames zero trust as minimizing uncertainty in accurate, least-privilege per-request access decisions, which pressures DelayBasin to treat the active request as a first-class boundary rather than a rhetorical courtesy.


- `REF-0480` — NIST AI RMF Core / Playbook, **GOVERN 3.2** (accessed 2026-03-20)
  - URL: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/
  - Load-bearing use: says policies and procedures should define and differentiate roles and responsibilities for human-AI configurations and oversight of AI systems, which pressures DelayBasin to keep collaborative authority lanes explicit rather than blending request, draft, approval, execution, and review into one revision story.

- `REF-0481` — GitHub Docs, **About GitHub Copilot coding agent** (accessed 2026-03-20)
  - URL: https://docs.github.com/copilot/concepts/agents/coding-agent/about-coding-agent
  - Load-bearing use: says the user who asked Copilot coding agent to create a pull request is prevented from approving that pull request under required-approval controls, which pressures DelayBasin not to let requester and approver silently collapse into one flattering lane when agentic drafting or execution is in play.

- `REF-0482` — GitHub Docs, **Asking GitHub Copilot to create a pull request** (accessed 2026-03-20)
  - URL: https://docs.github.com/copilot/using-github-copilot/coding-agent/asking-copilot-to-create-a-pull-request
  - Load-bearing use: says delegated coding-agent work returns a pull request for the user to review, which pressures DelayBasin to keep request, execution, and later review as distinct collaborative lanes rather than one blended action.

- `REF-0483` — C2PA, **Content Credentials : C2PA Technical Specification** (accessed 2026-03-20)
  - URL: https://c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html
  - Load-bearing use: says manifests represent provenance data about the origin and edits of digital content, which pressures DelayBasin to serialize collaborative authorship and execution posture as explicit public metadata rather than leaving it inside maintainers’ memory.


- `REF-0484` — MDN Web Docs, **Working with the History API** (accessed 2026-03-20)
  - URL: https://developer.mozilla.org/en-US/docs/Web/API/History_API/Working_with_the_History_API
  - Load-bearing use: says `pushState()` adds a new session-history entry while `replaceState()` updates the current one, which pressures DelayBasin to distinguish creating a new durable latest-path cue from silently overwriting the current cue as if history had not changed.

- `REF-0485` — MDN Web Docs, **Window: popstate event** (accessed 2026-03-20)
  - URL: https://developer.mozilla.org/en-US/docs/Web/API/Window/popstate_event
  - Load-bearing use: says `pushState()` and `replaceState()` do not themselves fire `popstate`, which pressures DelayBasin to keep reentry-cue updates explicit rather than assuming history-like navigation semantics will announce cue drift automatically.

- `REF-0486` — MDN Web Docs, **Text fragments** (accessed 2026-03-20)
  - URL: https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Fragment/Text_fragments
  - Load-bearing use: says an unmatched text fragment is ignored and the user lands at the top of the document, which pressures DelayBasin to expose stale or broken fragment-like reentry cues instead of letting a generic page-open masquerade as successful precise landing.

- `REF-0487` — GitHub Docs, **Incorporating feedback in your pull request** (accessed 2026-03-20)
  - URL: https://docs.github.com/articles/incorporating-feedback-in-your-pull-request
  - Load-bearing use: says out-of-scope pull-request suggestions can be tracked by opening a linked issue, which pressures DelayBasin to preserve an explicit receiving object when live remainder work leaves the current local surface.

- `REF-0488` — GitHub Docs, **Creating an issue** (accessed 2026-03-20)
  - URL: https://docs.github.com/articles/creating-an-issue
  - Load-bearing use: documents creating issues from pull-request comments or code ranges with contextual snippets, which pressures DelayBasin to preserve next-proof and handoff surfaces rather than vague later-intention.

- `REF-0489` — GitLab Docs, **Merge requests** (accessed 2026-03-20)
  - URL: https://docs.gitlab.com/user/project/merge_requests/
  - Load-bearing use: says open merge-request threads can be moved to a new issue to unblock the merge request, which pressures DelayBasin to distinguish honest handoff from silent disappearance or sticky local ownership.

- `REF-0490` — GitHub Docs, **Planning and tracking work for your team or project** (accessed 2026-03-20)
  - URL: https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/planning-and-tracking-work-for-your-team-or-project
  - Load-bearing use: recommends explicit blocked-by and blocking relations among issues, which pressures DelayBasin to preserve blocked outputs and next proof points rather than letting “later” act as an unlabeled state.

- `REF-0491` — NIST, **SP 800-30 Rev. 1: Guide for Conducting Risk Assessments** (2012)
  - URL: https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-30r1.pdf
  - Load-bearing use: says risk assessments identify and document assumptions and constraints, which pressures DelayBasin to serialize live assumptions instead of letting them ride ambiently inside fluent revision prose.

- `REF-0492` — NIST, **SP 800-39: Managing Information Security Risk** (2011)
  - URL: https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-39.pdf
  - Load-bearing use: says credible risk framing requires identifying risk assumptions and constraints before downstream decisions inherit them, which pressures DelayBasin to expose what current moves are still assuming and what would invalidate those assumptions.

- `REF-0493` — Rhodes et al., **NISTIR 7608: Software Assurance Using Structured Assurance Case Models** (2009)
  - URL: https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7608.pdf
  - Load-bearing use: defines structured assurance cases as arguments that justify claims for a given application in a given environment, which pressures DelayBasin to keep live assumptions scoped and environment-bound rather than silently universalizing them into law.



- `REF-0494` — W3C, **PROV-O: The PROV Ontology** (2013)
  - URL: https://www.w3.org/TR/prov-o/
  - Load-bearing use: says provenance chains can be formed using `prov:wasDerivedFrom`, which pressures DelayBasin to preserve exact derivation-style edges from neighboring datacube packets to local imports rather than leaving that relation ambient in prose.

- `REF-0495` — C2PA, **Content Credentials : C2PA Technical Specification** (accessed 2026-03-20)
  - URL: https://c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html
  - Load-bearing use: says existing assets used to create a new asset are ingredients whose use is documented in provenance data, which pressures DelayBasin to name neighboring datacube packets as explicit import ingredients when they materially shape a local ratchet.

- `REF-0496` — Software Heritage, **SoftWare Hash IDentifier (SWHID)** (accessed 2026-03-20)
  - URL: https://www.softwareheritage.org/software-hash-identifier-swhid/
  - Load-bearing use: says SWHIDs provide a way to archive and reference the precise version of code used, which pressures DelayBasin to pin foreign-pressure provenance to exact neighboring surfaces rather than broad project names alone.
