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


- `REF-0497` — W3C, **SKOS Simple Knowledge Organization System Reference** (2009)
  - URL: https://www.w3.org/TR/skos-reference/
  - Load-bearing use: defines SKOS as a common data model for sharing and linking knowledge organization systems, which pressures DelayBasin to publish compact witness-state families as an explicit machine-readable vocabulary surface rather than leaving them ambient in prose and checker literals.

- `REF-0498` — OpenVEX, **OpenVEX Specification** (accessed 2026-03-20)
  - URL: https://github.com/openvex/spec/blob/main/OPENVEX-SPEC.md
  - Load-bearing use: says VEX `status` values and `not_affected` justifications come from fixed labels defined by the specification, which pressures DelayBasin to keep public witness-state tokens small, explicit, and stable when later tooling is expected to compare them.

- `REF-0499` — NIST, **Using Formal Thesauri and Controlled Vocabulary as the Interface Between Unstructured Data and Semantic Technologies** (2021)
  - URL: https://www.nist.gov/document/using-formal-thesauri-and-controlled-vocabulary-interface-between-unstructured-data-and
  - Load-bearing use: argues that formal thesauri and controlled vocabularies help bridge unstructured language into more explicit interoperable structure, which pressures DelayBasin to separate explanation-rich prose from the smaller controlled token families its ledgers and receipts actually compare.


- `REF-0500` — Google SRE, **Canary Release: Deployment Safety and Efficiency** (accessed 2026-03-21)
  - URL: https://sre.google/workbook/canarying-releases/
  - Load-bearing use: says release candidates should be exposed to a small production segment and compared against a control before full rollout, which pressures DelayBasin to distinguish candidate archive surfaces from promoted landing surfaces when the same request family can be used as a pre-promotion check.

- `REF-0501` — Amazon SageMaker AI Docs, **Shadow tests** (accessed 2026-03-21)
  - URL: https://docs.aws.amazon.com/sagemaker/latest/dg/shadow-tests.html
  - Load-bearing use: defines shadow testing as comparing a changed serving stack against the currently deployed infrastructure without affecting end users, which pressures DelayBasin to keep some candidate packets non-authoritative while they are compared against the current baseline, using copied live requests within the same endpoint rather than an ambiently shifting request family.

- `REF-0502` — Microsoft Learn, **Safe rollout for online endpoints - Azure Machine Learning** (accessed 2026-03-21)
  - URL: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-safely-rollout-online-endpoints?view=azureml-api-2
  - Load-bearing use: documents mirrored traffic to a shadow deployment, metric/log inspection, and only later traffic promotion, which pressures DelayBasin to treat pre-promotion shadow comparison as part of the write gate rather than as evidence that a candidate surface is already the live landing path.

- `REF-0503` — Google SRE, **Improve and Optimize Data Processing Pipelines** (accessed 2026-03-21)
  - URL: https://sre.google/workbook/data-processing/
  - Load-bearing use: the two-phase mutation pattern stores candidate mutations in a temporary location and verifies them before applying them, which pressures DelayBasin to keep some proposed archive rewrites explicitly provisional until a separate verification pass has compared them against the current control surface.


- `REF-0504` — Google Cloud Deploy, **Verify your deployment** (accessed 2026-03-21)
  - URL: https://docs.cloud.google.com/deploy/docs/verify-deployment
  - Load-bearing use: says deployment verification runs tests after deployment and that verification failure fails the rollout, which pressures DelayBasin to name an explicit verify surface before treating a compared candidate packet as promotion-ready.

- `REF-0505` — Google Cloud Deploy, **Create your delivery pipeline and targets** (accessed 2026-03-21)
  - URL: https://docs.cloud.google.com/deploy/docs/create-pipeline-targets
  - Load-bearing use: says a target can require manual approval and a rollout stays pending until approval is given, which pressures DelayBasin to separate comparison evidence from actual promotion authority.

- `REF-0506` — AWS AppConfig, **Working with deployment strategies** (accessed 2026-03-21)
  - URL: https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-creating-deployment-strategy.html
  - Load-bearing use: defines bake time as post-100%-deployment alarm monitoring that can still trigger rollback, which pressures DelayBasin to preserve an explicit soak window rather than treating immediate promotion as permanently settled.

- `REF-0507` — Argo Rollouts, **Experiments** (accessed 2026-03-21)
  - URL: https://argoproj.github.io/argo-rollouts/features/experiment/
  - Load-bearing use: says experiment steps block rollout progress until success, can run for an explicit duration, and abort the rollout if analysis fails, which pressures DelayBasin to name abort triggers and bounded evaluation windows when a candidate packet is being judged against a baseline.


- `REF-0508` — Argo Rollouts, **Analysis & Progressive Delivery** (accessed 2026-03-21)
  - URL: https://argo-rollouts.readthedocs.io/en/stable/features/analysis/
  - Load-bearing use: defines `AnalysisTemplate` with metrics, frequency, and values considered successful or failed, and says completed analysis runs become successful, failed, or inconclusive in ways that continue, abort, or pause rollout, which pressures DelayBasin to name an analysis basis and pass/fail criterion when shadow comparison is load-bearing.

- `REF-0509` — Argo Rollouts, **Architecture** (accessed 2026-03-21)
  - URL: https://argo-rollouts.readthedocs.io/en/stable/architecture/
  - Load-bearing use: says analysis connects rollouts to metrics providers, defines thresholds that decide whether an update is successful, and allows manual as well as automated promotion paths, which pressures DelayBasin to keep the judged observable and promotion criterion explicit without pretending metrics are mandatory in every case.

- `REF-0510` — AWS CodeDeploy, **Working with deployment configurations in CodeDeploy** (accessed 2026-03-21)
  - URL: https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-configurations.html
  - Load-bearing use: defines a deployment configuration as a set of rules and success and failure conditions used during deployment, which pressures DelayBasin to preserve compact success/failure criteria rather than letting promotion rely on a good-looking comparison alone.


- `REF-0511` — Argo Rollouts, **Experiments** (accessed 2026-03-21)
  - URL: https://argo-rollouts.readthedocs.io/en/stable/features/experiment/
  - Load-bearing use: says experiments can run baseline and canary replicas in parallel for Kayenta-style analysis and that the canonical use case is baseline-vs-canary comparison, which pressures DelayBasin to name the comparison frame that makes a candidate/control shadow pass an equal comparison rather than ambient taste.

- `REF-0512` — Google SRE, **Canary Analysis Service** (accessed 2026-03-21)
  - URL: https://sre.google/static/pdf/canary_analysis.pdf
  - Load-bearing use: defines trials as pairs of canary and control populations plus the time range during which they should be compared, which pressures DelayBasin to preserve the compared population and window whenever a shadow comparison is load-bearing.


- `REF-0513` — Argo Rollouts, **Analysis & Progressive Delivery** (accessed 2026-03-21)
  - URL: https://argo-rollouts.readthedocs.io/en/stable/features/analysis/
  - Load-bearing use: says analyses can use `initialDelay`, `count`, and `interval`, and can end inconclusive when a bounded run never satisfies success or failure, which pressures DelayBasin to name any warm-up and observation budget before a shadow-comparison verdict counts as promotion-grade evidence.

- `REF-0514` — Google Cloud Docs, **Google Cloud's approach to change** (accessed 2026-03-21)
  - URL: https://docs.cloud.google.com/docs/cloud-approach-to-change
  - Load-bearing use: says each rollout step has a bake time to catch slow-burning issues before progressing and that Canary Analysis Service returns PASS or FAIL during rollout, which pressures DelayBasin to distinguish a quick glance from a bounded observation window when candidate/control comparison is load-bearing.

- `REF-0515` — Amazon SageMaker AI Docs, **Create a shadow test** (accessed 2026-03-21)
  - URL: https://docs.aws.amazon.com/sagemaker/latest/dg/shadow-tests-create.html
  - Load-bearing use: says a shadow test can be scheduled for a specified duration, with metric review followed by promote-or-retain, which pressures DelayBasin to say whether a candidate/control readout came from a real observation campaign or only a quick advisory look.


- `REF-0516` — Argo Rollouts, **Prometheus** (accessed 2026-03-21)
  - URL: https://argo-rollouts.readthedocs.io/en/stable/analysis/prometheus/
  - Load-bearing use: says range queries usually return multiple values and it is important to assert on every value returned rather than only `result[0]`, which pressures DelayBasin to record when a shadow verdict is aggregate-only versus all-values over the judged comparison window.

- `REF-0517` — Spinnaker, **Best practices for configuring canary** (accessed 2026-03-21)
  - URL: https://spinnaker.io/docs/guides/user/canary/best-practices/
  - Load-bearing use: says too many metrics in one group can yield an overall passing score even when one fails, and that `critical: true` can fail the whole canary immediately, which pressures DelayBasin to preserve any critical metric or slice veto instead of trusting a green aggregate alone.

- `REF-0518` — Argo Rollouts, **Analysis & Progressive Delivery** (accessed 2026-03-21)
  - URL: https://argo-rollouts.readthedocs.io/en/stable/features/analysis/
  - Load-bearing use: says metric providers can return NaN, infinity, empty arrays, or nil-like empty results and that users must handle those cases explicitly in success/failure conditions, which pressures DelayBasin to preserve how missing or malformed comparison evidence was treated rather than trusting silent defaults.

- `REF-0519` — Amazon CloudWatch, **Configuring how CloudWatch alarms treat missing data** (accessed 2026-03-21)
  - URL: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/alarms-and-missing-data.html
  - Load-bearing use: exposes explicit missing-data treatments (`breaching`, `notBreaching`, `ignore`, `missing`) and shows that empty query results can force `INSUFFICIENT_DATA`, which pressures DelayBasin to state how absent telemetry affects a shadow verdict instead of letting no-data behavior stay ambient.

- `REF-0520` — Spinnaker, **How canary judgment works** (accessed 2026-03-21)
  - URL: https://spinnaker.io/docs/guides/user/canary/judge/
  - Load-bearing use: distinguishes `Nodata` from `NodataFailMetric`, supports `mustHaveData`, and makes NaN handling a first-class configuration choice, which pressures DelayBasin to say whether missing comparison evidence is tolerated, demoting, or automatically failing before promotion-grade authority is granted.



- `REF-0521` — Spinnaker, **Best practices for configuring canary** (accessed 2026-03-21)
  - URL: https://spinnaker.io/docs/guides/user/canary/best-practices/
  - Load-bearing use: says baseline and canary should be equivalent deployments at the same time, size, and traffic so the analysis controls for the intended change rather than cache-warmup, heap-size, or other confounders, which pressures DelayBasin to preserve what non-target differences were actually held fixed before trusting a shadow verdict.

- `REF-0522` — Argo Rollouts, **Experiments** (accessed 2026-03-21)
  - URL: https://argo-rollouts.readthedocs.io/en/stable/features/experiment/
  - Load-bearing use: says the canonical experiment starts baseline and canary in parallel for an equal comparison, which pressures DelayBasin to keep candidate/control equivalence explicit rather than ambient when a shadow pass is load-bearing.

- `REF-0523` — Amazon SageMaker AI Docs, **Create a shadow test** (accessed 2026-03-21)
  - URL: https://docs.aws.amazon.com/sagemaker/latest/dg/shadow-tests-create.html
  - Load-bearing use: requires explicit production and shadow variants, instance type and count choices, and side-by-side invocation and instance metrics, which pressures DelayBasin to preserve when a candidate/control comparison depended on matched or deliberately mismatched serving shape rather than leaving those conditions ambient.

- `REF-0524` — Google Cloud Docs, **REST Resource: urlMaps** (accessed 2026-03-21)
  - URL: https://docs.cloud.google.com/compute/docs/reference/rest/v1/urlMaps
  - Load-bearing use: says a mirrored backend does not contribute a returned response and that the host / authority header is suffixed with `-shadow`, which pressures DelayBasin to preserve what candidate output remained non-authoritative and what explicit shadow marker distinguished the mirrored pass from the live serving path.


- `REF-0525` — Kubernetes, **Dynamic Admission Control** (accessed 2026-03-21)
  - URL: https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/
  - Load-bearing use: says webhooks with side effects must skip those side effects on `dryRun: true` requests, requires explicit `sideEffects` declarations such as `NoneOnDryRun`, and says side-effecting webhooks need reconciliation because admission does not guarantee persistence, which pressures DelayBasin to preserve whether a shadow path was actually dry-run-aware, side-effect-suppressed, or only tolerable under explicit reconciliation.

- `REF-0526` — Kubernetes, **Admission Control in Kubernetes** (accessed 2026-03-21)
  - URL: https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/
  - Load-bearing use: says a webhook with side effects such as decrementing quota must have a reconciliation system because later webhooks or validation may still prevent the request from finishing, which pressures DelayBasin not to treat a mirrored candidate path that can still mutate downstream state as clean shadow evidence without an explicit repair story.

- `REF-0527` — Istio, **Mirroring** (accessed 2026-03-21)
  - URL: https://istio.io/latest/docs/tasks/traffic-management/mirroring/
  - Load-bearing use: says mirroring sends a copy of live traffic to a mirrored service and that the mirrored traffic happens out of band of the critical request path for the primary service, which pressures DelayBasin to separate shadow observation from authority while staying honest about whether mirrored execution could still touch downstream actuators.

- `REF-0528` — Envoy, **HTTP route components (proto)** (accessed 2026-03-21)
  - URL: https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/route/v3/route_components.proto
  - Load-bearing use: says `request_mirror_policies` can apply `request_headers_mutations`, `host_rewrite_literal`, and shadow-host-suffix controls to mirrored requests, which pressures DelayBasin to preserve whether a candidate/control compare pass kept request shape fixed or knowingly rewrote it.

- `REF-0529` — Envoy, **1.36.0 (October 14, 2025)** (accessed 2026-03-21)
  - URL: https://www.envoyproxy.io/docs/envoy/latest/version_history/v1.36/v1.36.0
  - Load-bearing use: explicitly records header manipulation and host-rewrite support added for mirror requests, which pressures DelayBasin not to assume a mirrored candidate always sees the same request metadata as the serving path unless rewrite drift is named.


- `REF-0530` — Istio, **Virtual Service** (accessed 2026-03-21)
  - URL: https://istio.io/latest/docs/reference/config/networking/virtual-service/
  - Load-bearing use: says mirrored traffic is on a best-effort basis and that the sidecar or gateway does not wait for the mirrored destination to respond, which pressures DelayBasin to preserve whether selected shadow traffic was actually guaranteed or only best-effort before treating the comparison as promotion-grade evidence.

- `REF-0531` — Google Cloud Docs, **Traffic management overview for internal Application Load Balancers** (accessed 2026-03-21)
  - URL: https://docs.cloud.google.com/load-balancing/docs/l7-internal/traffic-management
  - Load-bearing use: says an identical mirrored request is sent on a fire-and-forget basis and the load balancer does not wait for the mirrored backend response, which pressures DelayBasin to name any delivery-assurance or mirror-drop uncertainty rather than treating eligible mirrored traffic as automatically observed candidate evidence.

- `REF-0532` — Google Cloud Docs, **REST Resource: regionUrlMaps** (accessed 2026-03-21)
  - URL: https://docs.cloud.google.com/compute/docs/reference/rest/v1/regionUrlMaps
  - Load-bearing use: says the backend service configured for a mirroring policy must reference backends of the same type as the original matched backend service and that serverless NEG backends are not supported as mirrored backend services, which pressures DelayBasin to name whether a shadow lane actually ran on a supported mirrored substrate rather than quietly laundering a topology mismatch into promotion-grade evidence.

- `REF-0533` — Azure Machine Learning, **Safe rollout for online endpoints** (accessed 2026-03-21)
  - URL: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-safely-rollout-online-endpoints?view=azureml-api-2
  - Load-bearing use: says mirroring is not supported for Kubernetes online endpoints, that you can mirror traffic to only one deployment in an endpoint, and that a deployment can receive only live or mirrored traffic but not both, which pressures DelayBasin to preserve endpoint and deployment support limits instead of treating every candidate topology as equally mirrorable.


- `REF-0534` — Envoy, **HTTP routing** (accessed 2026-03-21)
  - URL: https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/http/http_routing
  - Load-bearing use: says retries live inside the overall request timeout, hedging can issue multiple simultaneous upstream requests after a per-try timeout, and a late response may still be awaited, which pressures DelayBasin to preserve whether a judged shadow pass counted first attempts only, retry-inclusive attempts, or hedge-inclusive attempt geometry.

- `REF-0535` — Envoy, **HTTP route components (proto)** (accessed 2026-03-21)
  - URL: https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/route/v3/route_components.proto
  - Load-bearing use: says `x-envoy-attempt-count` can be surfaced, route timeout includes all retries, and route- or virtual-host-level retry and hedge policy precedence is independent rather than inherited, which pressures DelayBasin to preserve an explicit attempt-count witness and honest retry/hedge geometry rather than treating one downstream request as automatically one clean candidate attempt.

- `REF-0536` — Istio, **Virtual Service** (accessed 2026-03-21)
  - URL: https://istio.io/latest/docs/reference/config/networking/virtual-service/
  - Load-bearing use: says retries default to two attempts for standard retryable conditions and that timeouts or retries are not enabled when client-side fault injection is enabled, which pressures DelayBasin to preserve whether a shadow comparison ran under retry, timeout, or fault geometry that changed what the candidate or control actually experienced.

- `REF-0537` — Envoy, **How do I configure timeouts?** (accessed 2026-03-21)
  - URL: https://www.envoyproxy.io/docs/envoy/latest/faq/configuration/timeouts
  - Load-bearing use: says request timeout is not enforced by default because it is incompatible with streaming requests, route timeout defaults to 15 seconds and is incompatible with streaming responses, and `max_stream_duration` caps a stream's lifetime, which pressures DelayBasin to preserve the deadline or completion horizon under which a shadow comparison was judged.

- `REF-0538` — Google Cloud Docs, **Method: urlMaps.update** (accessed 2026-03-21)
  - URL: https://docs.cloud.google.com/compute/docs/reference/rest/v1/urlMaps/update
  - Load-bearing use: distinguishes route `timeout`, measured from end-of-stream until the response is processed, from `maxStreamDuration`, measured from the beginning of the stream until the response is processed, and says streams that exceed that duration are closed, which pressures DelayBasin to preserve what completion horizon candidate and control actually shared.

- `REF-0539` — Amazon SageMaker AI, **Adapt your own inference container for Amazon SageMaker AI** (accessed 2026-03-21)
  - URL: https://docs.aws.amazon.com/sagemaker/latest/dg/adapt-inference-container.html
  - Load-bearing use: says real-time inference requests must return within 60 seconds for regular responses and 8 minutes for streaming responses, which pressures DelayBasin to preserve whether a shadow verdict compared regular or streaming response modes under the same deadline.

- `REF-0540` — Azure Machine Learning, **Manage resources and quotas** (accessed 2026-03-21)
  - URL: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-quotas?view=azureml-api-2
  - Load-bearing use: says managed online endpoints have a maximum endpoint request timeout of 180 seconds, which pressures DelayBasin to preserve endpoint-level timeout ceilings rather than quietly treating all shadow lanes as if they shared one completion horizon.


- `REF-0541` — Kubernetes Gateway API, **Standard / API Reference** (accessed 2026-03-21)
  - URL: https://gateway-api.sigs.k8s.io/reference/spec/
  - Load-bearing use: distinguishes `RequestMirror` for HTTPRoute from `RequestMirror` for GRPCRoute and says responses from the mirrored backend are ignored in both cases, which pressures DelayBasin to preserve whether a shadow comparison was actually judged under one route kind and protocol family rather than quietly flattening HTTP and gRPC lanes into the same comparison story.

- `REF-0542` — Envoy, **gRPC** (accessed 2026-03-21)
  - URL: https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/other_protocols/grpc
  - Load-bearing use: says gRPC uses HTTP/2 or above, uses trailers to convey request status, and can be bridged or transcoded across HTTP/1.1, gRPC-Web, Connect, or JSON, which pressures DelayBasin to preserve whether a candidate/control comparison shared one protocol semantics lane or depended on bridge normalization and trailer handling.

- `REF-0543` — Istio, **Protocol Selection** (accessed 2026-03-21)
  - URL: https://istio.io/latest/docs/ops/configuration/traffic-management/protocol-selection/
  - Load-bearing use: says routing and rich metrics depend on protocol determination, that undetermined traffic is treated as plain TCP, and that supported gateway protocol classes include HTTP, HTTP/2, and gRPC, which pressures DelayBasin to preserve whether a shadow comparison actually ran under one declared protocol posture instead of ambient protocol guesswork.


- `REF-0544` — Google Cloud Docs, **Request distribution for external Application Load Balancers** (accessed 2026-03-21)
  - URL: https://docs.cloud.google.com/load-balancing/docs/https/request-distribution
  - Load-bearing use: says HTTP keepalives attempt to use the same TCP session but there is no guarantee, documents client-IP, header, and cookie session-affinity modes, and says affinity can break if routing shifts to a different first-layer GFE or backend membership changes, which pressures DelayBasin to preserve whether candidate and control actually shared one sticky or stateless routing posture rather than quietly inheriting warmed-path luck.

- `REF-0545` — Istio, **Destination Rule** (accessed 2026-03-21)
  - URL: https://istio.io/latest/docs/reference/config/networking/destination-rule/
  - Load-bearing use: says consistent-hash load balancing provides only soft session affinity based on headers, cookies, or source IP and that affinity can be lost when hosts change or proxies see different locality views, which pressures DelayBasin to preserve whether a candidate/control comparison actually shared one affinity posture rather than quietly drifting across backends.

- `REF-0546` — Amazon SageMaker AI, **Stateful sessions with Amazon SageMaker AI models** (accessed 2026-03-21)
  - URL: https://docs.aws.amazon.com/sagemaker/latest/dg/stateful-sessions.html
  - Load-bearing use: says ordinary inference can land on any instance but `SessionId` routing sends subsequent requests to the same ML instance with cached context, which pressures DelayBasin to preserve whether a shadow comparison was stateless or depended on explicit same-instance session continuity.


- `REF-0547` — vLLM Docs, **Automatic Prefix Caching** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/
  - Load-bearing use: says KV caches from prior requests can be reused when a new query shares the same prefix, speeding prefilling but not decoding, which pressures DelayBasin to preserve whether candidate and control were judged under the same hot-prefix or cold-prefill posture rather than quietly laundering cache heat into clean shadow evidence.

- `REF-0548` — Ray Serve LLM Docs, **Prefix-aware routing** (accessed 2026-03-21)
  - URL: https://docs.ray.io/en/latest/serve/llm/user-guides/prefix-aware-routing.html
  - Load-bearing use: says `PrefixCacheAffinityRouter` routes similar requests to replicas with the highest prefix match when load is balanced and otherwise falls back toward load balancing, which pressures DelayBasin to preserve when a shadow verdict depended on cache-locality routing rather than a cold or route-indifferent baseline.

- `REF-0549` — Ray Serve LLM Docs, **KV cache offloading** (accessed 2026-03-21)
  - URL: https://docs.ray.io/en/latest/serve/llm/user-guides/kv-cache-offloading.html
  - Load-bearing use: says repeated prompts or multi-turn conversations can miss once GPU caches are evicted, that offloading preserves cached prefills for longer, and that MultiConnector ordering matters when combining local lookup with cross-instance transfer, which pressures DelayBasin to preserve whether candidate and control shared one cache tier and transfer order rather than quietly comparing hot offloaded state to cold recompute.

- `REF-0550` — KServe, **Best of Both Worlds: Cloud-Native AI Inference at Scale using KServe and llm-d** (published 2026-03-05, accessed 2026-03-21)
  - URL: https://kserve.github.io/website/blog/cloud-native-ai-inference-kserve-llm-d
  - Load-bearing use: says llm-d's scheduler uses GPU utilization, queue depth, cache residency, SLA constraints, and load distribution while adding prefix-cache-aware routing, which pressures DelayBasin to preserve when a judged lane was cache-residency-aware rather than pretending all same-request compares were heat-neutral.

- `REF-0551` — NVIDIA Technical Blog, **Introducing New KV Cache Reuse Optimizations in NVIDIA TensorRT-LLM** (published 2025-01-16, accessed 2026-03-21)
  - URL: https://developer.nvidia.com/blog/introducing-new-kv-cache-reuse-optimizations-in-nvidia-tensorrt-llm/
  - Load-bearing use: says TensorRT-LLM now exposes priority-based KV eviction plus an eventually consistent KV event API for KV-aware routing and scheduling across multiple executors, which pressures DelayBasin to preserve what cache witness or tier-change evidence kept a shadow comparison honest instead of quietly inheriting hot-cache luck.

- `REF-0552` — NVIDIA Technical Blog, **NVIDIA Dynamo, A Low-Latency Distributed Inference Framework for Scaling Reasoning AI Models** (published 2025-03-18, accessed 2026-03-21)
  - URL: https://developer.nvidia.com/blog/introducing-nvidia-dynamo-a-low-latency-distributed-inference-framework-for-scaling-reasoning-ai-models/
  - Load-bearing use: says the Smart Router tracks KV cache overlap across large GPU fleets and routes requests by overlap score, workload balance, and GPU capacity while offloading older KV blocks across memory tiers, which pressures DelayBasin to preserve whether candidate and control shared one cache-residency and routing objective rather than quietly comparing hot reuse against cold recompute.

- `REF-0553` — NVIDIA Technical Blog, **How NVIDIA Dynamo 1.0 Powers Multi-Node Inference at Production Scale** (published 2026-03-17, accessed 2026-03-21)
  - URL: https://developer.nvidia.com/blog/nvidia-dynamo-1-production-ready/
  - Load-bearing use: says KV block movement across GPU, CPU, SSD, and remote tiers is emitted as global events and indexed to keep a cluster-wide view of KV locations, which pressures DelayBasin to preserve whether a shadow verdict depended on one specific cache tier or transfer state instead of treating cache topology as ambient.


- `REF-0554` — vLLM Docs, **Speculative Decoding** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/latest/features/speculative_decoding/
  - Load-bearing use: says speculative decoding in vLLM targets medium-to-low-QPS memory-bound workloads and supports multiple proposer families such as draft-model, n-gram, MLP, EAGLE, and MTP-style paths, which pressures DelayBasin to preserve whether candidate and control actually shared one no-spec versus speculative-decoding posture instead of quietly comparing draft+verify against plain decode.

- `REF-0555` — vLLM Docs, **Metrics** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/stable/design/metrics/
  - Load-bearing use: documents speculative-decoding acceptance-rate, efficiency, accepted-token, and draft-token metrics, which pressures DelayBasin to preserve what draft acceptance witness or explicit no-spec note kept a promotion-grade compare pass honest rather than treating speculation success as ambient.

- `REF-0556` — vLLM Docs, **vllm.config.speculative** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/v0.13.0/api/vllm/config/speculative/
  - Load-bearing use: documents speculative configuration fields such as proposer method/model, speculative-token budget, acceptance-policy controls, parallel-drafting knobs, and `disable_by_batch_size`, which pressures DelayBasin to preserve what draft family, token budget, acceptance policy, or load-triggered disable condition actually governed the compared lane.

- `REF-0557` — vLLM Docs, **Speculators** (published 2026-01-29, accessed 2026-03-21)
  - URL: https://docs.vllm.ai/projects/speculators/en/latest/features/speculative_decoding/speculators/
  - Load-bearing use: frames speculative decoding as a draft-model-plus-verifier path where a smaller proposer predicts multiple tokens ahead and the primary model validates them, which pressures DelayBasin to name the proposer witness or explicit no-spec note rather than quietly flattening draft+verify and plain decode into one comparison story.

- `REF-0558` — NVIDIA Triton Inference Server Docs, **Speculative Decoding with TensorRT-LLM** (accessed 2026-03-21)
  - URL: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/tutorials/Feature_Guide/Speculative_Decoding/TRT-LLM/README.html
  - Load-bearing use: documents production-oriented speculative families including EAGLE, MEDUSA, and draft-model-based paths, which pressures DelayBasin not to treat all speculative lanes as one interchangeable mechanism when the proposer family itself can change what the compared lane really is.

- `REF-0559` — llm-d, **llm-d 0.4: Achieve SOTA Performance Across Accelerators** (published 2025-12-02, accessed 2026-03-21)
  - URL: https://llm-d.ai/blog/llm-d-v0.4-achieve-sota-inference-across-accelerators
  - Load-bearing use: says llm-d v0.4 added speculative decoding and native MTP support as part of its latency-critical serving path, which pressures DelayBasin to preserve when production load, proposer mode, or speculation enablement changes what the candidate/control lane actually exercised.

- `REF-0560` — SGLang, **Documentation** (accessed 2026-03-21)
  - URL: https://sgl-project.github.io/
  - Load-bearing use: lists speculative decoding as a first-class serving feature alongside continuous batching, radix/prefix attention, prefill-decode disaggregation, and quantized KV cache, which pressures DelayBasin to treat no-spec versus speculative posture as a real serving-axis distinction rather than niche benchmark decoration.


- `REF-0561` — vLLM Docs, **Engine Arguments** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/stable/configuration/engine_args/
  - Load-bearing use: documents `fcfs` versus `priority` scheduling, chunked-prefill controls, and long-prefill thresholds that can let shorter prompts jump queue, which pressures DelayBasin to preserve whether candidate and control actually shared one scheduling posture rather than quietly inheriting queue luck.

- `REF-0562` — vLLM Docs, **Optimization and Tuning** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/stable/configuration/optimization/
  - Load-bearing use: says chunked prefill in V1 prioritizes decode requests before scheduling prefills and that `max_num_batched_tokens` trades TTFT against ITL, which pressures DelayBasin to preserve whether candidate and control shared one decode-priority and batching-budget posture rather than quietly comparing different scheduler lanes.

- `REF-0563` — vLLM Docs, **Scheduler** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/stable/api/vllm/v1/core/sched/scheduler/
  - Load-bearing use: shows preemption frees request cache state, resets computed tokens, and returns the request to the waiting queue, which pressures DelayBasin to preserve whether candidate and control shared one preemption/resume posture rather than quietly comparing a resumed lane against an uninterrupted lane.

- `REF-0564` — llm-d, **Architecture** (accessed 2026-03-21)
  - URL: https://llm-d.ai/docs/architecture
  - Load-bearing use: says intelligent inference scheduling adds fairness and prioritization for multi-tenant serving plus P/D-, KV-, SLA-, and load-aware scoring, which pressures DelayBasin to preserve whether candidate and control shared one scheduler lane rather than quietly inheriting a different serving objective.

- `REF-0565` — NVIDIA Dynamo Docs, **Router Guide** (accessed 2026-03-21)
  - URL: https://docs.nvidia.com/dynamo/dev/components/router/router-guide
  - Load-bearing use: documents queue-threshold-triggered priority scheduling, `fcfs` versus `wspt` queue policy, and knobs that balance prefill efficiency against decode load, which pressures DelayBasin to preserve whether candidate and control shared one queue policy rather than quietly comparing different scheduler objectives.

- `REF-0566` — SGLang Docs, **SGLang Documentation** (accessed 2026-03-21)
  - URL: https://docs.sglang.io/
  - Load-bearing use: lists a zero-overhead CPU scheduler, continuous batching, chunked prefill, speculative decoding, and prefill-decode disaggregation as first-class serving features, which pressures DelayBasin to treat scheduler posture as a real serving axis rather than ambient runtime detail.


- `REF-0567` — vLLM Docs, **CUDA Graphs** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/stable/design/cuda_graphs/
  - Load-bearing use: says not all CUDA Graph modes are compatible with every attention backend and that unsupported modes are automatically downgraded to the closest supported mode, which pressures DelayBasin to preserve whether candidate and control actually shared one eager-versus-graph and backend-support posture rather than quietly comparing a downgraded path against a captured one.

- `REF-0568` — vLLM Docs, **FP8 W8A8** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/stable/features/quantization/fp8/
  - Load-bearing use: says FP8 changes both memory footprint and throughput while support depends on GPU family, which pressures DelayBasin to preserve whether candidate and control shared one precision / quantization lane rather than quietly laundering a cheaper FP8 path into a same-model comparison.

- `REF-0569` — SGLang Docs, **Attention Backend** (accessed 2026-03-21)
  - URL: https://lmsysorg.mintlify.app/docs/advanced_features/attention_backend
  - Load-bearing use: documents hardware-dependent automatic backend selection, hybrid prefill-versus-decode backend choices, and CUDA-graph capture differences across those phases, which pressures DelayBasin to preserve what backend family and graph posture the compared lane actually exercised rather than treating backend dispatch as ambient runtime detail.

- `REF-0570` — TensorRT-LLM Docs, **trtllm-build** (accessed 2026-03-21)
  - URL: https://nvidia.github.io/TensorRT-LLM/latest/commands/trtllm-build.html
  - Load-bearing use: shows that paged context FMHA, FP8 context FMHA, fused FP4 quantization, and multiple optimization profiles are explicit execution-lane choices, which pressures DelayBasin to preserve when candidate and control ran through materially different kernel or precision paths.

- `REF-0571` — TensorRT-LLM Docs, **LLM API reference** (accessed 2026-03-21)
  - URL: https://nvidia.github.io/TensorRT-LLM/0.21.0/llm-api/reference.html
  - Load-bearing use: says CUDA graphs are created only for configured batch sizes, are enabled for decoding requests only, and can consume additional GPU memory, which pressures DelayBasin to preserve whether candidate and control actually shared one decode-only graph posture rather than quietly comparing graph-captured decode against eager or uncaptured execution.

- `REF-0572` — TensorRT-LLM Release Notes (accessed 2026-03-21)
  - URL: https://nvidia.github.io/TensorRT-LLM/release-notes.html
  - Load-bearing use: records that CUDA-graph warmup, FP8 context FMHA, chunked-context kernels, overlap scheduling, and guided-decoding support continue to interact in production releases, which pressures DelayBasin to keep broader execution-lane-court stories quarantined until one compact kernel-and-precision clause proves insufficient.


- `REF-0573` — vLLM Docs, **Structured Outputs** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/latest/features/structured_outputs/
  - Load-bearing use: says vLLM structured outputs can constrain generation by choice, regex, JSON schema, grammar, or structural tags, and that backend choice affects regex semantics and request handling, which pressures DelayBasin to preserve whether candidate and control actually shared one unconstrained-versus-guided lane rather than flattening guide kind into ambient prompt detail.

- `REF-0574` — vLLM Docs, **structured_outputs config** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/latest/api/vllm/config/structured_outputs/
  - Load-bearing use: says the default structured-output backend is `auto`, with behavior chosen from request contents and current backend support and subject to change across releases, while whitespace and additional-properties controls vary by backend, which pressures DelayBasin to preserve what backend or explicit unconstrained note kept a shadow comparison honest rather than trusting auto-selection as a stable same-lane condition.

- `REF-0575` — NVIDIA NIM Docs, **Structured Generation with NVIDIA NIM for LLMs** (accessed 2026-03-21)
  - URL: https://docs.nvidia.com/nim/large-language-models/latest/structured-generation.html
  - Load-bearing use: recommends `guided_json` with `xgrammar` for best performance and reliability, warns that fallback to `outlines` can cause performance issues particularly during the first inference, and says SGLang profiles support only `xgrammar` and `outlines`, which pressures DelayBasin to preserve guide backend, fallback, and profile posture rather than laundering a cold or restricted guided lane into a clean same-request compare.

- `REF-0576` — NVIDIA Triton / TensorRT-LLM Docs, **End-to-End Workflow for Guided Decoding with TensorRT-LLM Backend** (accessed 2026-03-21)
  - URL: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/tensorrtllm_backend/docs/guided_decoding.html
  - Load-bearing use: says TensorRT-LLM guided decoding currently uses the XGrammar backend and supports JSON, JSON Schema, regex, and EBNF grammar guides, which pressures DelayBasin to preserve whether candidate and control actually shared one guide type and backend rather than treating all structured outputs as one interchangeable lane.

- `REF-0577` — TensorRT-LLM Release Notes (accessed 2026-03-21)
  - URL: https://nvidia.github.io/TensorRT-LLM/release-notes.html
  - Load-bearing use: records guided-decoding integration with speculative decoding, draft-model chunked prefill, disaggregated serving, and overlap scheduling, which pressures DelayBasin to preserve when the guided lane changed what feature combination the candidate/control comparison actually exercised rather than treating guide state as isolated decoration.

- `REF-0578` — NVIDIA NIM Docs, **Configure Your NIM with NVIDIA NIM for LLMs** (accessed 2026-03-21)
  - URL: https://docs.nvidia.com/nim/large-language-models/latest/configuration.html
  - Load-bearing use: says guided decoding can use built-in or custom backends and that enabling custom guided decoding permits arbitrary Python code execution, which keeps broader grammar-state-court ideas legible while still supporting only a smaller compare-lane clause for now.



- `REF-0579` — vLLM Docs, **LoRA Adapters** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/latest/features/lora.html
  - Load-bearing use: says vLLM serves adapters per request with minimal overhead, can run base and LoRA requests in parallel when capacity allows, and can load or unload adapters at runtime, which pressures DelayBasin to preserve whether candidate and control actually shared one base-only versus adapter-augmented and adapter-residency lane rather than flattening adapter state into ambient model identity.

- `REF-0580` — NVIDIA NIM Docs, **Parameter-Efficient Fine-Tuning with NVIDIA NIM for LLMs** (accessed 2026-03-21)
  - URL: https://docs.nvidia.com/nim/large-language-models/latest/peft.html
  - Load-bearing use: says NIM supports dynamic multi-LoRA inference, keeps adapters resident across GPU and host caches with configurable limits and LRU eviction, and batches mixed LoRA requests with specialized kernels, which pressures DelayBasin to preserve whether candidate and control shared one hot-adapter, mixed-batch, and reload-or-eviction posture rather than treating adapter availability as invisible.

- `REF-0581` — TensorRT-LLM Docs, **LoRA (Low-Rank Adaptation)** (accessed 2026-03-21)
  - URL: https://nvidia.github.io/TensorRT-LLM/features/lora.html
  - Load-bearing use: says TensorRT-LLM can switch among multiple adapters per request, supports multi-LoRA with quantized models, and exposes host/device PEFT cache configuration, which pressures DelayBasin to preserve whether candidate and control shared one adapter family, rank, and residency lane rather than quietly comparing different PEFT execution paths.

- `REF-0582` — SGLang Docs, **Server Arguments** (accessed 2026-03-21)
  - URL: https://docs.sglang.ai/advanced_features/server_arguments.html
  - Load-bearing use: says SGLang exposes `--enable-lora`, overlap loading, `--max-loras-per-batch`, `--max-loaded-loras`, eviction policy, and backend controls, which pressures DelayBasin to preserve when candidate and control ran through different mixed-batch, overlap-load, or eviction lanes rather than calling them one same-model compare.

- `REF-0583` — Chen et al., **Punica: Multi-Tenant LoRA Serving** (version dated 2023-10-28; accessed 2026-03-21)
  - URL: https://arxiv.org/abs/2310.18547
  - Load-bearing use: argues that multi-tenant LoRA serving needs scheduler support around one shared base-model copy, which keeps broader adapter-state-court ideas legible while still supporting only one smaller adapter-lane clause for now.

- `REF-0584` — Sheng et al., **S-LoRA: Serving Thousands of Concurrent LoRA Adapters** (version dated 2024-06-05; accessed 2026-03-21)
  - URL: https://arxiv.org/abs/2403.06804
  - Load-bearing use: describes serving many adapters by storing them in host memory and paging active ones to GPU alongside KV-aware management, which pressures DelayBasin to preserve adapter residency posture explicitly instead of treating it as hidden infrastructure.

- `REF-0585` — Zhang et al., **Improving the Serving Performance of Multi-LoRA Large Language Models via Efficient LoRA and KV Cache Management** (accessed 2026-03-21)
  - URL: https://arxiv.org/abs/2505.09358
  - Load-bearing use: argues that LoRA and KV-cache hotness interact and should be managed jointly, which keeps broader shadow-adapter-registry stories legible while the archive still admits only one compact adapter-lane clause.


- `REF-0586` — vLLM Docs, **Expert Parallel Deployment** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/
  - Load-bearing use: expert-parallel deployments expose EP+DP posture, selectable all2all backends, and an explicit expert-parallel load balancer with redundant experts, making MoE execution lane a first-class serving distinction rather than an ambient implementation detail.

- `REF-0587` — vLLM Docs, **Fused MoE Kernel Features** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/v0.18.0/design/moe_kernel_features/
  - Load-bearing use: different MoE all2all backends support different activation formats, quantization paths, and async overlap, sharpening the need to preserve which expert-communication lane candidate and control actually used.

- `REF-0588` — TensorRT-LLM Docs, **Expert Parallelism in TensorRT-LLM** (accessed 2026-03-21)
  - URL: https://nvidia.github.io/TensorRT-LLM/advanced/expert-parallelism.html
  - Load-bearing use: MoE serving can run tensor parallel, expert parallel, or hybrid TP+EP patterns, so the same model family can still occupy materially different expert lanes.

- `REF-0589` — TensorRT LLM Team, **Scaling Expert Parallelism in TensorRT LLM (Part 2: Performance Status and Optimization)** (accessed 2026-03-21)
  - URL: https://nvidia.github.io/TensorRT-LLM/blogs/tech_blog/blog8_Scaling_Expert_Parallelism_in_TensorRT-LLM_part2.html
  - Load-bearing use: large-scale EP keeps evolving through kernel work, communication kernels, and expert-parallel load balancing, which makes rebalance and router posture honest serving-lane confounders rather than background noise.

- `REF-0590` — llm-d Docs, **Wide Expert Parallelism with LeaderWorkerSet** (accessed 2026-03-21)
  - URL: https://llm-d.ai/docs/guide/Installation/wide-ep-lws
  - Load-bearing use: wide EP deployments make inter-node all-to-all transport and hardware topology explicit prerequisites, so MoE serving lane can differ through expert-parallel topology and communication support even before quality claims are compared.


- `REF-0591` — vLLM Docs, **Multi-Modal Data Processing** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/stable/design/mm_processing/
  - Load-bearing use: says vLLM multimodal serving depends on processor-driven prompt updates, dummy-text recovery for tokenized-plus-media inputs, and processor-output caching for repeated media, which pressures DelayBasin to preserve whether candidate and control actually shared one processor and placeholder-expansion lane rather than flattening media handling into ambient prompt detail.

- `REF-0592` — vLLM Docs, **Multimodal Inputs** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/stable/features/multimodal_inputs/
  - Load-bearing use: says multimodal inputs can be identified by stable UUIDs so caching can reuse work across requests or even skip resending media on a cache hit, which pressures DelayBasin to preserve whether candidate and control shared one multimodal-cache posture rather than treating media reuse as invisible infrastructure.

- `REF-0593` — vLLM Docs, **torch.compile with Multimodal Encoders** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/stable/design/torch_compile_multimodal/
  - Load-bearing use: says multimodal encoders can now be compiled separately and the feature is off by default behind `compile_mm_encoder`, which pressures DelayBasin to preserve whether candidate and control actually shared one vision-encoder execution lane rather than laundering compiled-versus-uncompiled media paths into a same-model compare.

- `REF-0594` — NVIDIA NIM for Vision Language Models Docs, **Query the Cosmos Reason2 API** (accessed 2026-03-21)
  - URL: https://docs.nvidia.com/nim/vision-language-models/1.6.0/examples/cosmos-reason2/api.html
  - Load-bearing use: says `mm_processor_kwargs` and `media_io_kwargs` change frame sizing, pixel budgets, frame sampling, and therefore multimodal token counts, which pressures DelayBasin to preserve whether candidate and control shared one media-sizing and frame-sampling lane before treating a visual compare as promotion-grade.

- `REF-0595` — NVIDIA NIM for Vision Language Models Docs, **Release Notes** (accessed 2026-03-21)
  - URL: https://docs.nvidia.com/nim/vision-language-models/latest/release-notes.html
  - Load-bearing use: records live multimodal limitations such as invalid `mm_processor_kwargs`, image-in-text misuse, and model-specific input-mode limits, which keeps the stronger vision-state-court idea legible while still supporting only one smaller multimodal-input / processor-and-encoder clause for now.

- `REF-0596` — TensorRT-LLM Docs, **tensorrt_llm.runtime.multimodal_model_runner** (accessed 2026-03-21)
  - URL: https://nvidia.github.io/TensorRT-LLM/_modules/tensorrt_llm/runtime/multimodal_model_runner.html
  - Load-bearing use: shows TensorRT-LLM can load and run separate visual-engine paths and can fall back between Python and C++ multimodal sessions depending on capabilities, which pressures DelayBasin to preserve whether candidate and control actually shared one vision-encoder/backend lane rather than treating all visual requests as one execution path.

- `REF-0597` — TensorRT-LLM Release Notes (accessed 2026-03-21)
  - URL: https://nvidia.github.io/TensorRT-LLM/release-notes.html
  - Load-bearing use: records multimodal API and memory-management changes such as `MultimodalParams` support for `SharedTensor` plus fixes around image batching and Qwen-VL runtime issues, which keeps broader multimodal-registry ideas legible while the archive still admits only one compact multimodal-input / processor-and-encoder clause.


- `REF-0598` — vLLM Docs, **Parallelism and Scaling** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/stable/serving/parallelism_scaling/
  - Load-bearing use: says distributed serving can run as a single GPU instance, single-node tensor parallel inference, or multi-node tensor-plus-pipeline inference, which pressures DelayBasin to preserve whether candidate and control actually shared one shard-and-replica posture instead of flattening distributed topology into ambient model identity.

- `REF-0599` — vLLM Docs, **Context Parallel Deployment** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/stable/serving/context_parallel_deployment/
  - Load-bearing use: treats context parallel deployment as a first-class serving topology for long-context inference, which pressures DelayBasin to preserve whether candidate and control actually shared one context-parallel posture rather than laundering a different shard layout into the same compare lane.

- `REF-0600` — vLLM Docs, **Data Parallel Deployment** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/
  - Load-bearing use: distinguishes internal, hybrid, and external load balancing for data-parallel serving and makes node-local versus external routing posture explicit, which pressures DelayBasin to preserve replica-balancing lane honestly before treating a shadow compare as promotion-grade.

- `REF-0601` — TensorRT-LLM Docs, **Model Definition** (accessed 2026-03-21)
  - URL: https://nvidia.github.io/TensorRT-LLM/python-api/tensorrt_llm.models.html
  - Load-bearing use: documents tensor parallel and pipeline parallel deployment posture as first-class model-definition parameters, keeping shard layout from being treated as invisible serving background.

- `REF-0602` — TensorRT-LLM Docs, **API Reference** (accessed 2026-03-21)
  - URL: https://nvidia.github.io/TensorRT-LLM/0.21.0/llm-api/reference.html
  - Load-bearing use: exposes `tensor_parallel_size`, `pipeline_parallel_size`, `context_parallel_size`, `gpus_per_node`, and attention-DP toggles as explicit runtime controls, which pressures DelayBasin to preserve whether candidate and control truly shared one TP/PP/CP/DP lane rather than calling it one same-model path.

- `REF-0603` — SGLang Docs, **Server Arguments** (accessed 2026-03-21)
  - URL: https://docs.sglang.ai/advanced_features/server_arguments.html
  - Load-bearing use: exposes `--tp`, `--dp`, `--nnodes`, load-balancing method, and DP-attention switches, which makes shard topology and replica-balancing posture a first-class serving distinction rather than ambient infra detail.

- `REF-0604` — llm-d Docs, **Model Service** (accessed 2026-03-21)
  - URL: https://llm-d.ai/docs/guide/concepts/modelservice/
  - Load-bearing use: frames multi-node inference with data parallelism as an active deployment scenario, which keeps the broader shard-and-replica-court idea legible while the archive still admits only one smaller parallelism-lane clause for now.


- `REF-0605` — vLLM Docs, **Sleep Mode** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/latest/features/sleep_mode/
  - Load-bearing use: says sleep mode can offload model weights, discard KV cache, and later wake the engine without a full reload, which makes hot-resident versus sleeping-versus-resumed worker state a first-class serving lane rather than ambient infra detail.

- `REF-0606` — vLLM Production Stack Docs, **Sleep and Wakeup Mode** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/projects/production-stack/en/latest/use_cases/sleep-wakeup-mode.html
  - Load-bearing use: says a sleeping engine does not process requests and that the router is explicitly sleep-mode aware, which pressures DelayBasin to preserve whether candidate and control actually shared one wake-path posture rather than treating routed wake state as invisible background.

- `REF-0607` — Knative Docs, **Configuring scale to zero** (accessed 2026-03-21)
  - URL: https://knative.dev/docs/serving/autoscaling/scale-to-zero/
  - Load-bearing use: says scale-to-zero is a real serving control with explicit grace and retention periods, which makes scale-from-zero versus already-live replica state an honest compare-lane distinction rather than mere deployment noise.

- `REF-0608` — KServe Blog, **Cloud-Native AI Inference at Scale using KServe and llm-d** (published 2026-03-05; accessed 2026-03-21)
  - URL: https://kserve.github.io/website/blog/cloud-native-ai-inference-kserve-llm-d
  - Load-bearing use: says KServe and llm-d support request- and concurrency-based autoscaling plus scale-to-zero for cost control, which keeps the stronger wake-state-court idea legible while still supporting only one smaller wake-state clause for now.

- `REF-0609` — NVIDIA Triton Inference Server Docs, **Model Configuration** (accessed 2026-03-21)
  - URL: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/model_configuration.html
  - Load-bearing use: says `ModelWarmup` keeps a model from being ready or served until warmup completes, which pressures DelayBasin to preserve whether candidate and control actually shared one warmup or first-inference posture before treating latency or quality comparisons as promotion-grade.

- `REF-0610` — NVIDIA NIM for LLMs Docs, **Utilities for NVIDIA NIM for LLMs** (accessed 2026-03-21)
  - URL: https://docs.nvidia.com/nim/large-language-models/latest/utilities.html
  - Load-bearing use: says NIM can precache selected or default model profiles before deployment, which makes profile-download and engine-readiness posture an explicit serving distinction rather than a hidden bootstrap detail.

- `REF-0611` — NVIDIA NIM Operator Docs, **Quick Start** (accessed 2026-03-21)
  - URL: https://docs.nvidia.com/nim-operator/latest/quickstart.html
  - Load-bearing use: explicitly recommends caching models for low inference latency and faster autoscaling, which pressures DelayBasin to preserve whether candidate and control actually shared one hot-ready versus cache-fetching or autoscaling-wakeup posture.


- `REF-0612` — vLLM Docs, **Parallelism and Scaling** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/stable/serving/parallelism_scaling/
  - Load-bearing use: says vLLM can confirm whether internode communication is actually using `NET/IB/GDRDMA` or has fallen back to `NET/Socket`, which pressures DelayBasin to preserve whether candidate and control shared one honest fast-interconnect lane rather than laundering socket fallback into same-model evidence.

- `REF-0613` — vLLM Docs, **MooncakeConnector Usage Guide** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/stable/features/mooncake_connector_usage/
  - Load-bearing use: says Mooncake uses GPUDirect RDMA to transfer data directly in a zero-copy manner while maximizing multi-NIC resources on one machine, which pressures DelayBasin to preserve whether candidate and control actually shared one zero-copy and NIC-rail posture before treating a shadow compare as promotion-grade.

- `REF-0614` — vLLM Docs, **NixlConnector Usage Guide** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/stable/features/nixl_connector_usage/
  - Load-bearing use: says NixlConnector uses NIXL with configurable UCX or other transport backends plus explicit host/port handshake and cross-machine setup, which makes transport backend choice and transfer posture a first-class serving distinction rather than invisible middleware.

- `REF-0615` — TensorRT-LLM Docs, **Disaggregated Serving** (accessed 2026-03-21)
  - URL: https://nvidia.github.io/TensorRT-LLM/1.2.0rc6/features/disagg-serving.html
  - Load-bearing use: says TensorRT-LLM supports GPUDirect RDMA, exposes UCX rail and transfer-buffer knobs, warns that different NVLink domains can hang or degrade performance, and distinguishes direct transmit from staged-copy KV transfer, which pressures DelayBasin to preserve honest fabric-lane notes before promotion.

- `REF-0616` — llm-d Docs, **Architecture** (accessed 2026-03-21)
  - URL: https://llm-d.ai/docs/architecture
  - Load-bearing use: says llm-d instructs vLLM to perform point-to-point KV cache transfer over fast interconnects such as IB/RoCE RDMA, TPU ICI, and DCN via NIXL, which keeps the stronger interconnect-state-court idea legible while the archive still admits only one smaller fabric-lane clause for now.


- `REF-0617` — vLLM Docs, **Disaggregated Prefilling (experimental)** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/latest/features/disagg_prefill/
  - Load-bearing use: says disaggregated prefilling places prefill and decode in different vLLM instances so TTFT and ITL can be tuned separately, and says it helps control tail ITL, which pressures DelayBasin to preserve whether candidate and control actually shared one aggregated-versus-disaggregated serving posture rather than flattening phase placement into ambient infra detail.

- `REF-0618` — TensorRT-LLM Docs, **Disaggregated Serving** (accessed 2026-03-21)
  - URL: https://nvidia.github.io/TensorRT-LLM/1.2.0rc6/features/disagg-serving.html
  - Load-bearing use: says disaggregated serving launches separate context and generation servers behind an orchestrator, exposes cache-transceiver backend and buffer settings, and allows heterogeneous engines and parallelism between context and generation phases, which pressures DelayBasin to preserve prefill/decode role-binding posture rather than treating split serving as one uniform lane.

- `REF-0619` — llm-d Docs, **Architecture** (accessed 2026-03-21)
  - URL: https://llm-d.ai/docs/architecture
  - Load-bearing use: says llm-d orchestrates prefill and decode onto independent instances, with scheduler decisions and a sidecar coordinating point-to-point KV transfer, which keeps phase placement and handoff authority legible as first-class serving distinctions rather than invisible background.

- `REF-0620` — TensorRT-LLM Release Notes (accessed 2026-03-21)
  - URL: https://nvidia.github.io/TensorRT-LLM/release-notes.html
  - Load-bearing use: records disaggregated-mode specific support and failure surfaces, including guided decoding in disaggregated mode plus known hangs in some context/generation parallelism combinations, which keeps the broader split-serving-court idea legible while the archive still admits only one smaller phase-lane / prefill-decode-placement clause for now.


- `REF-0621` — vLLM Docs, **vllm serve** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/stable/cli/serve/
  - Load-bearing use: says vLLM exposes `--max-model-len` as the model context-length control, can auto-choose the largest context that fits in GPU memory, and lets operators disable sliding-window behavior, which pressures DelayBasin to preserve whether candidate and control actually shared one context-length and windowing lane rather than flattening long-context posture into ambient deployment detail.

- `REF-0622` — vLLM Recipes, **Qwen3.5 Usage Guide** (published 2026-03-13 / 2026-02-16, accessed 2026-03-21)
  - URL: https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen3.5.html
  - Load-bearing use: says ultra-long text serving can require explicit RoPE-scaling overrides together with a larger `--max-model-len`, which pressures DelayBasin to preserve whether candidate and control actually shared one position-scaling posture rather than quietly comparing base-context and extended-context lanes.

- `REF-0623` — vLLM Docs, **OpenAI-Compatible Server** (accessed 2026-03-21)
  - URL: https://docs.vllm.ai/en/stable/serving/openai_compatible_server/
  - Load-bearing use: says the `truncate` parameter controls how overlength inputs are handled with `END`, `START`, or `NONE`, which pressures DelayBasin to preserve when candidate and control did not even admit the same overlength prompt rather than quietly laundering truncation policy into same-request evidence.

- `REF-0624` — TensorRT-LLM Docs, **Multi-Head, Multi-Query, and Group-Query Attention** (accessed 2026-03-21)
  - URL: https://nvidia.github.io/TensorRT-LLM/advanced/gpt-attention.html
  - Load-bearing use: says TensorRT-LLM exposes cyclic KV cache, StreamingLLM sink tokens, and sink-relative positional handling for long-text serving, which pressures DelayBasin to preserve whether candidate and control actually shared one window-and-positioning lane rather than treating all long-context paths as interchangeable.

- `REF-0625` — TensorRT-LLM Docs, **Runtime** (accessed 2026-03-21)
  - URL: https://nvidia.github.io/TensorRT-LLM/python-api/tensorrt_llm.runtime.html
  - Load-bearing use: says TensorRT-LLM runtime surfaces `max_input_len`, `max_attention_window_size`, and `sink_token_length` as explicit runtime controls, which keeps the stronger window-state-court idea legible while still supporting only one smaller long-context / window-and-positioning clause for now.

- `REF-0626` — NeurIPS 2024 Poster, **On the Worst Prompt Performance of Large Language Models** (accessed 2026-03-21)
  - URL: https://neurips.cc/virtual/2024/poster/95497
  - Load-bearing use: reports large worst-versus-best gaps even for semantically equivalent case-level prompts and says there is no shortcut to characterizing the worst prompt, which pressures DelayBasin not to certify one exact weird handle as uniquely causal after one flattering comparison.

- `REF-0627` — arXiv, **A Survey of Context Engineering for Large Language Models** (submitted 2025-07-17; accessed 2026-03-21)
  - URL: https://arxiv.org/html/2507.13334v1
  - Load-bearing use: frames context engineering as dynamic structured assembly rather than one static prompt string, which pressures DelayBasin to treat handle placement, routing, and composition as first-class variables rather than neutral wrappers around the same words.

- `REF-0628` — Chroma Research, **Context Rot: How Increasing Input Tokens Impacts LLM Performance** (published 2025-07-14; accessed 2026-03-21)
  - URL: https://research.trychroma.com/context-rot
  - Load-bearing use: says models do not use context uniformly as length grows, which pressures DelayBasin to preserve placement, structure, and density effects before narrating a weird local handle as an exact magic word.

- `REF-0629` — arXiv, **Evolving Prompts In-Context: An Open-ended, Self-replicating Perspective** (submitted 2025-06-22; accessed 2026-03-21)
  - URL: https://arxiv.org/abs/2506.17930
  - Load-bearing use: says pruning demonstrations into seemingly incoherent “gibberish” can still outperform standard prompt-optimization baselines, which pressures DelayBasin not to equate human-legible semantics with the whole control story behind GPUstorming.

- `REF-0630` — OpenReview, **When Attention Sink Emerges in Language Models: An Empirical View** (published 2025-01-22; accessed 2026-03-21)
  - URL: https://openreview.net/forum?id=78Nn4QJTEN
  - Load-bearing use: says attention sinks emerge broadly during language-model training and behave more like key biases than semantically meaningful content, which makes a stronger anti-overmixing or routing-scaffold story legible while still falling short of licensing it as canon.

- `REF-0631` — OpenReview, **DuoAttention: Efficient Long-Context LLM Inference with Retrieval and Streaming Heads** (published 2025-01-22; accessed 2026-03-21)
  - URL: https://openreview.net/forum?id=cFu7ze7xUm
  - Load-bearing use: says only a fraction of heads need full long-context retrieval while others focus on recent tokens and attention sinks, which keeps a stronger sparse-routing interpretation legible while DelayBasin still admits only one smaller handle-family / placement-and-density sweep.

- `REF-0632` — arXiv, **Are you going to finish that? A Practical Study of the Partial Token Problem** (submitted 2026-01-30; accessed 2026-03-21)
  - URL: https://arxiv.org/html/2601.23223v1
  - Load-bearing use: says the ending of a user-provided prompt forces a token boundary that can bias prediction, which pressures DelayBasin not to narrate one exact weird handle as semantically unique until at least one boundary or retokenization variant has been checked.

- `REF-0633` — arXiv, **Tokenization Matters! Degrading Large Language Models through Challenging Their Tokenization** (revised 2025-05-15; accessed 2026-03-21)
  - URL: https://arxiv.org/html/2405.17067v2
  - Load-bearing use: shows that challenging token segmentation can drive leading LLMs into incorrect answers, which keeps exact-handle authority honest by treating tokenization and normalization variants as real controls rather than cosmetic noise.

- `REF-0634` — arXiv, **Say Anything but This: When Tokenizer Betrays Reasoning in LLMs** (submitted 2026-01-21; accessed 2026-03-21)
  - URL: https://arxiv.org/pdf/2601.14658
  - Load-bearing use: says identical surface strings can arise from different token-id sequences and documents tokenizer-induced phantom edits such as whitespace-boundary shifts and intra-word resegmentation, which keeps the stronger tokenizer-resonance story legible while still falling short of canon.

- `REF-0635` — arXiv, **Brittlebench: Quantifying LLM robustness via prompt sensitivity** (submitted 2026-02-27; accessed 2026-03-21)
  - URL: https://arxiv.org/html/2603.13285v1
  - Load-bearing use: says semantics-preserving typos and spacing perturbations can still move model performance materially, which pressures DelayBasin to preserve at least one boundary or normalization control before certifying an exact byte-string handle.


- `REF-0636` — ICLR 2024, **How I learned to start worrying about prompt formatting** (published 2024-05-07; accessed 2026-03-21)
  - URL: https://proceedings.iclr.cc/paper_files/paper/2024/file/6c0e99d736da621403018ca7b32b1a4d-Paper-Conference.pdf
  - Load-bearing use: shows that meaning-preserving prompt-format changes can move open-source LLM performance by large margins, which pressures DelayBasin not to certify one exact weird handle until it has survived at least one nearby wrapper or serialization variant.

- `REF-0637` — arXiv, **Does Prompt Formatting Have Any Impact on LLM Performance?** (submitted 2024-11-15; accessed 2026-03-21)
  - URL: https://arxiv.org/pdf/2411.10541
  - Load-bearing use: reports significant GPT performance discrepancies across plain text, Markdown, YAML, and JSON despite identical content and finds no universally optimal format, which pressures DelayBasin to treat wrapper or serialization choice as a real control variable rather than as neutral packaging.

- `REF-0638` — arXiv, **The Illusion of Role Separation: Hidden Shortcuts in LLM Role Learning (and How to Fix Them)** (submitted 2025-05-01; revised 2025-05-05; accessed 2026-03-21)
  - URL: https://arxiv.org/abs/2505.00626
  - Load-bearing use: says fine-tuned models can rely on task-type exploitation and proximity to begin-of-text as proxies for role identity, which pressures DelayBasin to test wrapper or role-slot variants before narrating one system/user placement as semantic authority.

- `REF-0639` — arXiv, **The Price of Format: Diversity Collapse in LLMs** (submitted 2025-05-25; accessed 2026-03-21)
  - URL: https://arxiv.org/html/2505.18949v1
  - Load-bearing use: says structured chat templates and role markers can act as behavioral triggers that narrow the output space, which keeps a stronger role-slot or template-slot story legible while still falling short of canon.


- `REF-0640` — ACL Anthology, **Demystifying optimized prompts in language models** (published 2025-11; accessed 2026-03-22)
  - URL: https://aclanthology.org/2025.emnlp-main.147/
  - Load-bearing use: says optimized prompts contain influential tokens with outsized impact and that those tokens are often punctuation and nouns, which pressures DelayBasin to test a nearby sham or cue-neighborhood variant before narrating one weird local handle as purely semantic authority.

- `REF-0641` — arXiv, **Local Prompt Optimization** (submitted 2025-04-29; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2504.20355
  - Load-bearing use: says prompt optimization can improve by focusing on selected optimization tokens or subsections rather than mutating the whole prompt globally, which pressures DelayBasin to treat a local cue neighborhood as a real design object rather than ambient wording residue.

- `REF-0642` — Findings of ACL: NAACL 2024, **Large Language Models Sensitivity to The Order of Options in Multiple-Choice Questions** (published 2024-06; accessed 2026-03-22)
  - URL: https://aclanthology.org/2024.findings-naacl.130/
  - Load-bearing use: reports substantial performance gaps when answer options are reordered and attributes the effect partly to positional bias, which pressures DelayBasin not to mistake one insertion point or adjacent layout for semantic uniqueness.

- `REF-0643` — Findings of ACL 2024, **Addressing Order Sensitivity of In-Context Demonstration Examples in Causal Language Models** (published 2024-08; accessed 2026-03-22)
  - URL: https://aclanthology.org/2024.findings-acl.386/
  - Load-bearing use: says in-context example order changes representations because different positions expose different receptive fields, which pressures DelayBasin to keep nearby cue neighborhood and insertion-point controls honest before certifying one exact weird handle.



- `REF-0644` — OpenReview, **Contextual Drag: How Errors in the Context Affect LLM Reasoning** (published 2026-03-05; accessed 2026-03-22)
  - URL: https://openreview.net/forum?id=zpiYsPVDlV
  - Load-bearing use: says failed attempts in context can bias downstream reasoning toward structurally similar errors even when the model knows those attempts were wrong, which pressures DelayBasin to test history-light or residue-stripped variants before certifying one exact weird handle as semantic authority.

- `REF-0645` — arXiv, **Old Habits Die Hard: How Conversational History Geometrically Traps LLMs** (submitted 2026-02-08; accessed 2026-03-22)
  - URL: https://arxiv.org/html/2603.03308v1
  - Load-bearing use: says conversational history creates measurable carryover effects that can geometrically trap later generations, which makes a stronger history-drag scaffold legible while still supporting only one smaller carryover control in canon.

- `REF-0646` — OpenReview, **LLMs Get Lost In Multi-Turn Conversation** (published 2026-01-26; accessed 2026-03-22)
  - URL: https://openreview.net/forum?id=VKGTGGcwl6
  - Load-bearing use: reports a 39% average performance drop in multi-turn underspecified conversations and says models often over-rely on early assumptions, which pressures DelayBasin to treat prior-turn residue as a real confound rather than as neutral backdrop when GPUstorming an exact handle.


- `REF-0647` — OpenReview, **Prompt Stability Matters: Evaluating and Optimizing Auto-Generated Prompt in General-Purpose Systems** (published 2025-09-25; accessed 2026-03-22)
  - URL: https://openreview.net/pdf?id=gwf9E5M14g
  - Load-bearing use: says prompt quality in general-purpose systems should be judged by stability across repeated executions rather than one best-looking output, which pressures DelayBasin not to certify one vivid weird handle from a single flattering run.

- `REF-0648` — arXiv, **Same Prompt, Different Outcomes: Evaluating the Reproducibility of Data Analysis by LLMs** (submitted 2026-02-19; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2602.14349
  - Load-bearing use: reports considerable variation across independent executions under matched nominal setups and recommends interpreting distributions rather than single outputs, which pressures DelayBasin to preserve one repeated-inference sweep before narrating exact-handle authority as stable.

- `REF-0649` — ACL Anthology, **Non-Determinism of “Deterministic” LLM System Settings in Hosted Environments** (published 2025-07; accessed 2026-03-22)
  - URL: https://aclanthology.org/2025.eval4nlp-1.12.pdf
  - Load-bearing use: shows substantial run-to-run variation in hosted environments even under apparently fixed settings, which pressures DelayBasin to treat lucky-path and decode-regime privilege as real confounds rather than as noise to ignore.

- `REF-0650` — arXiv, **Prompt Injection as Role Confusion** (submitted 2026-02-22; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2603.12277
  - Load-bearing use: says models infer roles from how text is written rather than where it comes from, so untrusted text that imitates a role can inherit authority, which pressures DelayBasin to test whether a weird handle only works when it sits in a live actuation channel.

- `REF-0651` — arXiv, **ASIDE: Architectural Separation of Instructions and Data in Language Models** (submitted 2025-03-13; accessed 2026-03-22)
  - URL: https://arxiv.org/html/2503.10566v4
  - Load-bearing use: says current LLMs lack a built-in mechanism that distinguishes instructions from data and that prompt engineering or special-token mitigation is insufficient, which pressures DelayBasin to test quoted or fenced mention variants before certifying exact-handle authority.

- `REF-0652` — ACL Anthology, **IHEval: Evaluating Language Models on Following the Instruction Hierarchy** (published 2025-04; accessed 2026-03-22)
  - URL: https://aclanthology.org/2025.naacl-long.425.pdf
  - Load-bearing use: says current models struggle to recognize instruction priorities across system messages, user messages, history, and tool outputs, and that an added instruction-priority prompt brings little improvement, which makes actuation-channel privilege a real confound rather than a solved wrapper problem.

- `REF-0653` — arXiv, **Large Language Models Often Know When They Are Being Evaluated** (submitted 2025-05-28; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2505.23836
  - Load-bearing use: says frontier models can distinguish evaluation transcripts from deployment transcripts and often infer what an evaluation is testing, which pressures DelayBasin to treat watcher cues as a real confound before certifying one weird handle as semantically unique.

- `REF-0654` — arXiv, **When Wording Steers the Evaluation: Framing Bias in LLM judges** (submitted 2026-01-20; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2601.13537
  - Load-bearing use: says symmetric wording changes can induce significant discrepancies across LLM judges, which pressures DelayBasin to preserve one ordinary-user-frame control before reading one exact handle as uniquely causal.

- `REF-0655` — ACL Anthology, **From Fact to Judgment: Investigating the Impact of Task Framing on LLM Conviction in Dialogue Systems** (published 2026-02; accessed 2026-03-22)
  - URL: https://aclanthology.org/2026.iwsds-1.21.pdf
  - Load-bearing use: says even minimal dialogue reframing can change model judgment materially, which pressures DelayBasin to treat social-arbitration or watched-task posture as a plausible source of weird-handle leverage rather than ambient wrapper noise.


- `REF-0656` — ACL Anthology, **Beyond English: The Impact of Prompt Translation Strategies across Languages and Tasks in Multilingual LLMs** (published 2025-04; accessed 2026-03-22)
  - URL: https://aclanthology.org/2025.findings-naacl.73/
  - Load-bearing use: shows that pre-translation strategy and which prompt components stay in the source language versus English can materially affect performance across 35 languages and multiple task types, which pressures DelayBasin to test whether a weird handle only works under one language-selection policy.

- `REF-0657` — ACL Anthology, **Exploring the Role of Transliteration in In-Context Learning for Low-resource Languages Written in Non-Latin Scripts** (published 2025-11; accessed 2026-03-22)
  - URL: https://aclanthology.org/2025.mrl-main.27/
  - Load-bearing use: shows that original-script, transliterated, and mixed-script prompt templates can produce materially different results, with all tested models benefiting from transliteration on sequential labeling tasks, which pressures DelayBasin to preserve one transliteration or script-swapped control before certifying exact-handle authority.

- `REF-0658` — arXiv, **Large Reasoning Models Struggle to Transfer Parametric Knowledge Across Scripts** (submitted 2026-03-21; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2603.17070
  - Load-bearing use: says script match rather than language family is the primary predictor of cross-lingual knowledge-transfer failure once capability and question difficulty are controlled, which makes script-barrier privilege a live confound rather than an exotic corner case.

- `REF-0659` — arXiv, **Do Multilingual LLMs Think In English?** (submitted 2025-02-21; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2502.15603
  - Load-bearing use: says multilingual LLMs make key decisions in a representation space closest to English and are more steerable with English-derived vectors, which makes a stronger language-selection scaffold legible enough to quarantine while only supporting one smaller canon guard.

- `REF-0660` — arXiv, **When Names Change Verdicts: Intervention Consistency Reveals Systematic Bias in LLM Decision-Making** (submitted 2026-03-19; accessed 2026-03-22)
  - URL: https://arxiv.org/pdf/2603.18530
  - Load-bearing use: shows that authority/prestige swaps can flip LLM decisions even when underlying evidence is identical and finds authority bias exceeding demographic bias, which pressures DelayBasin to test de-authorized or provenance-swapped variants before certifying one exact handle as semantically unique.

- `REF-0661` — arXiv, **Vulnerability of LLMs’ Stated Beliefs? LLMs Belief Resistance Check Through Strategic Persuasive Conversation Interventions** (revised 2026-03-18; accessed 2026-03-22)
  - URL: https://arxiv.org/html/2601.13590v3
  - Load-bearing use: organizes persuasion under a source–message–channel–receiver frame and says source-level authority or in-group attribution can materially shape belief erosion, which pressures DelayBasin to treat source prestige as a live confound rather than as neutral metadata around a handle.

- `REF-0662` — arXiv, **The Judge Who Never Admits: Hidden Shortcuts in LLM-based Evaluation** (submitted 2026-02-08; accessed 2026-03-22)
  - URL: https://www.arxiv.org/pdf/2602.07996
  - Load-bearing use: shows a provenance hierarchy of EXPERT > HUMAN > LLM > UNKNOWN with cue acknowledgment often near zero, which pressures DelayBasin not to let institutional or provenance badges silently certify exact-handle authority.

- `REF-0663` — OpenReview, **Agent-to-Agent Theory of Mind: Testing Interlocutor Awareness among Large Language Models** (published 2025-07-24; accessed 2026-03-21)
  - URL: https://openreview.net/forum?id=e0VUmntFnE
  - Load-bearing use: says contemporary LLMs can infer and adapt to the identity and characteristics of dialogue partners, and that this interlocutor awareness creates both coordination gains and safety risks, which pressures DelayBasin to test identity-neutral variants before certifying exact-handle authority.

- `REF-0664` — arXiv, **Persona-Assigned Large Language Models Exhibit Human-Like Motivated Reasoning** (submitted 2025-06-24; accessed 2026-03-21)
  - URL: https://arxiv.org/abs/2506.20020
  - Load-bearing use: says persona assignment can reduce veracity discernment and induce identity-congruent reasoning that prompt-based debiasing methods do not reliably undo, which pressures DelayBasin to treat persona cues as a live confound rather than decorative style.

- `REF-0665` — arXiv, **From Biased Chatbots to Biased Agents: Examining Role Assignment Effects on LLM Agent Robustness** (submitted 2026-02-17; accessed 2026-03-21)
  - URL: https://arxiv.org/abs/2602.12285
  - Load-bearing use: says demographic persona assignments can degrade agentic-task performance by up to 26.2 percent despite being task-irrelevant, which pressures DelayBasin not to let claimed speaker or user-persona cues silently certify weird-handle authority.

- `REF-0666` — ACL Anthology, **Stereotype or Personalization? User Identity Biases in Large Language Model Recommendations** (published 2025-11; accessed 2026-03-21)
  - URL: https://aclanthology.org/2025.findings-acl.1254.pdf
  - Load-bearing use: shows that revealed identity features can bias recommendations and that models often fail to disclose when identity shaped the result, which makes interlocutor-identity privilege a real confound rather than neutral personalization metadata.

- `REF-0667` — arXiv, **Measuring Pragmatic Influence in Large Language Model Instructions** (submitted 2026-02-02; accessed 2026-03-21)
  - URL: https://arxiv.org/abs/2602.21223
  - Load-bearing use: shows that short influence prefixes such as urgency, authority, reciprocity, and emotional framing can systematically and reproducibly shift directive prioritization without changing task content, which pressures DelayBasin to test a neutral-tone or de-escalated control before certifying exact-handle authority.

- `REF-0668` — ACL Anthology, **Should We Respect LLMs? A Cross-Lingual Study on the Influence of Prompt Politeness on LLM Performance** (published 2024-11-16; accessed 2026-03-21)
  - URL: https://aclanthology.org/2024.sicon-1.2/
  - Load-bearing use: shows that impolite prompts often degrade performance while the best politeness level varies by language, which makes social-force phrasing a live confound rather than mere interpersonal decoration around a handle.

- `REF-0669` — arXiv, **Emotional Manipulation Through Prompt Engineering Amplifies Disinformation Generation in AI Large Language Models** (submitted 2024-03-06; accessed 2026-03-21)
  - URL: https://arxiv.org/abs/2403.03550
  - Load-bearing use: shows that polite and emotionally framed requests can materially change harmful-compliance behavior, which pressures DelayBasin not to treat urgency or affective cues as semantically neutral when evaluating vivid exact handles.

- `REF-0670` — arXiv, **ChatGPT Reads Your Tone and Responds Accordingly — Until It Does Not — Emotional Framing Induces Bias in LLM Outputs** (submitted 2025-06-17; accessed 2026-03-21)
  - URL: https://arxiv.org/abs/2507.21083
  - Load-bearing use: shows that tone changes can shift response polarity and semantic drift even when question content is held constant, which makes pragmatic-frame privilege legible enough to quarantine while only supporting one smaller canon guard.


- `REF-0671` — ACL Anthology, **Do LLMs Adhere to Label Definitions? Examining Their Receptivity in Text Classification** (published 2025-11; accessed 2026-03-21)
  - URL: https://aclanthology.org/2025.emnlp-main.1648.pdf
  - Load-bearing use: shows that models heavily rely on provided label definitions, that performance drops significantly when definitions are swapped or corrupted, and that definition-integration strategy can materially change behavior, which pressures DelayBasin not to let named criteria silently certify exact-handle authority.

- `REF-0672` — arXiv / CLEF 2025 Working Notes, **CEA-LIST at CheckThat! 2025: Evaluating LLMs as Detectors of Bias and Opinion in Text** (published 2025-09; accessed 2026-03-21)
  - URL: https://arxiv.org/abs/2507.07539
  - Load-bearing use: systematically varies explicit label names, neutral category names, and yes/no reframings and finds materially different precision/recall tradeoffs, which pressures DelayBasin to test whether a weird handle only works under one label or category naming scheme.

- `REF-0673` — ACL Anthology, **Curse of Knowledge: When Complex Evaluation Context Benefits yet Biases LLM Judges** (published 2025-11; accessed 2026-03-21)
  - URL: https://aclanthology.org/2025.findings-emnlp.805.pdf
  - Load-bearing use: says richer rubric packets can introduce criteria-loophole bias and criteria-entanglement bias, which pressures DelayBasin to treat rubric structure as a live confound rather than neutral explanation around a handle.

- `REF-0674` — arXiv, **LLMs Designing and Applying Evaluation Rubrics** (submitted 2026-02-09; accessed 2026-03-21)
  - URL: https://arxiv.org/abs/2602.08672
  - Load-bearing use: says rubric generation and application can remain coherent within a model while still showing limited cross-model agreement and weaker human alignment, which makes a stronger rubric scaffold legible enough to quarantine while only supporting one smaller canon guard.

- `REF-0675` — arXiv, **Beyond Manuals and Tasks: Instance-Level Context Learning for LLM Agents** (submitted 2025-10-03; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2510.02369
  - Load-bearing use: argues that instance-level context is a distinct and often missing source of reliable performance beyond environment-level manuals or task-level guidance, which pressures DelayBasin not to let broad family-scope artifacts silently certify one named local instance without an instance-narrowed control.


- `REF-0676` — Google Developers, **Migrate from Google Sign-In** (updated 2025-05-23; accessed 2026-03-22)
  - URL: https://developers.google.com/identity/gsi/web/guides/migration
  - Load-bearing use: exemplifies public migration discipline by pairing a deprecated path with an explicit replacement path and migration steps, which supports DelayBasin's compact rule that a changed startup route should name the successor path rather than force rediscovery.

- `REF-0677` — Microsoft Learn, **Important changes (deprecations) coming in Power Platform** (accessed 2026-03-22)
  - URL: https://learn.microsoft.com/en-us/power-platform/important-changes-coming
  - Load-bearing use: states that deprecation notices should provide sufficient time to plan and update before removal, which supports DelayBasin's burden-truth stance when a previously relied-on startup cue or route is being retired.


- `REF-0678` — arXiv, **Benchmarking Prompt Sensitivity in Large Language Models** (submitted 2025-01-12; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2501.14899
  - Load-bearing use: says slight prompt variations can materially affect response quality and that existing methods struggle to predict or stabilize this prompt sensitivity, which reinforces DelayBasin's policy of testing nearby control variants before certifying one exact wording as uniquely load-bearing.

- `REF-0679` — arXiv, **When Punctuation Matters: A Large-Scale Comparison of Prompt Robustness Methods for LLMs** (submitted 2025-06-25; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2506.19495
  - Load-bearing use: says LLMs remain highly sensitive to subtle, non-semantic prompt phrasing and formatting changes even under robustness methods, which keeps small wording controls legible as real confounds rather than decorative edits.

- `REF-0680` — arXiv, **When Wording Steers the Evaluation: Framing Bias in LLM judges** (submitted 2026-03-24; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2603.17649
  - Load-bearing use: says symmetric predicate-positive and predicate-negative judge prompts can induce significant discrepancies across high-stakes tasks, which pressures DelayBasin to preserve a predicate-parity control before certifying exact-handle authority.

- `REF-0681` — ACL Anthology / arXiv, **Deontological Keyword Bias: The Impact of Modal Expressions on Normative Judgments of Language Models** (published 2025-11; accessed 2026-03-22)
  - URL: https://aclanthology.org/2025.findings-emnlp.489/
  - Load-bearing use: says deontic modal expressions such as must and ought can push models toward obligation judgments even when scenario content is held fixed, which pressures DelayBasin to preserve a modal-neutralized control before treating an exact wording as uniquely semantic.

- `REF-0682` — arXiv, **Measuring and Exploiting Confirmation Bias in LLM-Assisted Security Code Review** (submitted 2026-03-19; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2603.18740
  - Load-bearing use: shows that framing vulnerable code as secure can reduce detection rates by 16.2–93.5 percentage points and that the effect is strongly asymmetric, which pressures DelayBasin to preserve a verdict-neutral or expectation-scrubbed control before certifying one exact handle as semantically unique.

- `REF-0683` — arXiv, **Anchoring Bias in Large Language Models: An Experimental Study** (submitted 2024-12-09; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2412.06593
  - Load-bearing use: shows that biased hints can disproportionately steer LLM judgment and that simple reflection-style mitigations are not enough, which pressures DelayBasin to treat embedded anchors as a live confound rather than decorative context around a handle.

- `REF-0684` — arXiv, **Quantifying LLM Biases Across Instruction Boundary in Mixed Question Forms** (revised 2026-01-07; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2509.20278
  - Load-bearing use: formulates sufficient, redundant, and insufficient instruction settings and shows that user instructions can themselves induce large biases, which pressures DelayBasin to preserve one expectation-neutralized control before reading prelabels or seeded verdicts as genuine handle authority.



- `REF-0685` — arXiv, **When Wording Steers the Evaluation: Framing Bias in LLM judges** (submitted 2026-01-20; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2601.13537
  - Load-bearing use: shows that symmetric framing changes can skew judge outputs and that model families show distinct tendencies toward agreement or rejection, which pressures DelayBasin to preserve an agreement-neutralized control before certifying exact-handle authority.

- `REF-0686` — arXiv, **Mitigating Agreement Bias in MLLMs with Self-Grounded Verification** (revised 2026-03-08; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2507.11662
  - Load-bearing use: shows that verifier models can over-validate and favor favorable labels, which pressures DelayBasin to preserve an endorsement-scrubbed control rather than let pre-endorsed labels or confirm-me scaffolds glow.

- `REF-0687` — arXiv, **Beyond the Illusion of Consensus: From Surface Heuristics to Knowledge-Grounded Evaluation in LLM-as-a-Judge** (submitted 2026-03-11; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2603.11027
  - Load-bearing use: argues that high evaluator agreement can ride on shared surface heuristics rather than substantive quality, which pressures DelayBasin not to treat agreement-seeking wording as semantically neutral scaffolding.

- <a id="ref-0688"></a>**[REF-0688]** Y. Luo et al., "Overlap Bias in LLM-Based Summary Evaluation," arXiv, 2026. https://arxiv.org/abs/2602.07673
- <a id="ref-0689"></a>**[REF-0689]** L. Zhang et al., "BiasScope: Unveiling Evaluation Bias in Language Models," arXiv, 2026. https://arxiv.org/abs/2602.09383
- <a id="ref-0690"></a>**[REF-0690]** J. Li et al., "Evaluating Scoring Bias in LLM-as-a-Judge," arXiv, 2025. https://arxiv.org/abs/2506.22316

- `REF-0691` — arXiv, **Evaluating and Mitigating LLM-as-a-judge Bias in Communication Systems** (revised 2026-02-28; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2510.12462
  - Load-bearing use: says LLM judges are influenced by verbosity, rich content, and chain-of-thought cues, which pressures DelayBasin to preserve a length-balanced or verbosity-scrubbed control before certifying one exact handle as semantically unique.

- `REF-0692` — arXiv, **Toward robust LLM-based judges: taxonomic bias evaluation and debiasing optimization** (submitted 2026-03-09; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2603.08091
  - Load-bearing use: says current judges exhibit significant length bias and stylistic-fluency bias, which pressures DelayBasin to preserve a style-neutralized control before treating polished wording as genuine handle authority.

- `REF-0693` — arXiv, **One Bias After Another: Mechanistic Reward Shaping and Persistent Biases in Language Reward Models** (submitted 2026-03-04; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2603.03291
  - Load-bearing use: says reward models still show length bias, overconfidence bias, and model-style reward sensitivity, which pressures DelayBasin not to let polished house style or richer-looking answers glow as semantics inside GPUstorming.

- `REF-0694` — arXiv, **Autorubric: A Unified Framework for Rubric-Based LLM Evaluation** (submitted 2026-02-13; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2603.00077
  - Load-bearing use: says criterion conflation can be mitigated with per-criterion atomic evaluation and natural-language explanations, which pressures DelayBasin to preserve a criterion-isolated control before treating blended rubric wins as exact-handle authority.

- `REF-0695` — arXiv, **Criterion-referenceability determines LLM-as-a-judge validity across physics assessment formats** (submitted 2026-03-16; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2603.14732
  - Load-bearing use: argues that validity tracks whether a task maps to explicit, observable grading features rather than raw model capability, which pressures DelayBasin to separate clean criterion-target reading from multi-objective blending when GPUstorming exact-handle authority.


- `REF-0696` — arXiv, **The Judge Who Never Admits: Hidden Shortcuts in LLM-based Evaluation** (submitted 2026-02-12; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2602.07996
  - Load-bearing use: shows that RECENT labels and temporal framing can bend judge outputs without semantic change and that judges often do not acknowledge the shortcut, which pressures DelayBasin to preserve a time-tag-neutralized or recency-scrubbed control before treating current/new wording as genuine authority.

- `REF-0697` — arXiv, **BiasScope: Towards Automated Detection of Bias in LLM-as-a-Judge Evaluation** (submitted 2026-02-13; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2602.09383
  - Load-bearing use: explicitly names novelty bias and shows that novelty-coded or unconventional answers can receive extra credit apart from judged quality, which pressures DelayBasin to preserve a novelty-blanded control before reading innovation cues as exact-handle authority.

- `REF-0698` — arXiv, **Am I More Pointwise or Pairwise? Revealing Position Bias in Rubric-Based LLM-as-a-Judge** (submitted 2026-02-02; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2602.02219
  - Load-bearing use: shows that rubric-based judges prefer score options appearing at particular positions and that balanced permutation improves correlation with human judgments, which pressures DelayBasin to preserve rubric-permuted controls before treating score ordering as semantic authority.


- `REF-0699` — arXiv, **Toward robust LLM-based judges: taxonomic bias evaluation and debiasing optimization** (submitted 2026-03-09; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2603.08091
  - Load-bearing use: explicitly treats bandwagon bias as a context bias where adding a majority-preference statement can steer judgments while response content stays fixed, which pressures DelayBasin to preserve a consensus-scrubbed control before treating social proof as semantics.

- `REF-0700` — arXiv, **Making Bias Non-Predictive: Training Robust LLM Judges via Reinforcement Learning** (submitted 2026-02-02; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2602.01528
  - Load-bearing use: shows that fabricated consensus cues such as “90% of people choose X” can reverse otherwise correct judgments and that debiasing requires making bandwagon signals non-predictive, which pressures DelayBasin not to read popularity or majority labels as harmless wrapper text.

- `REF-0701` — ACL Anthology, **Don’t Judge Code by Its Cover: Exploring Biases in LLM Judges for Code Evaluation** (accessed 2026-03-22)
  - URL: https://aclanthology.org/2025.findings-acl.306/
  - Load-bearing use: semantically equivalent code can be judged differently because of comments, formatting, and other presentation cues, which pressures DelayBasin not to mistake markup or presentation for semantic authority.

- `REF-0702` — ACL Anthology / Findings of NAACL, **LLMs Are Biased Towards Output Formats! Systematically Evaluating and Mitigating Format Bias in LLMs** (accessed 2026-03-22)
  - URL: https://aclanthology.org/2025.findings-naacl.337/
  - Load-bearing use: answer quality judgments can move substantially across output formats even when the underlying content is held fixed, which pressures DelayBasin to preserve a formatting-neutralized control.

- `REF-0703` — arXiv, **Co-Writing with Opinionated Language Models Affects Users' Views** (submitted 2023-02-01; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2302.00560
  - Load-bearing use: shows that an opinionated AI writing assistant shifted both what participants wrote and their later attitudes, which pressures DelayBasin to treat starter-surface defaults as a live steering channel rather than harmless convenience chrome.

- `REF-0704` — Science Advances, **Biased AI Writing Assistants Shift Users' Attitudes on Societal Issues** (published 2026-03-11; accessed 2026-03-22)
  - URL: https://www.science.org/doi/10.1126/sciadv.adw5578
  - Load-bearing use: reports preregistered autocomplete experiments where biased writing suggestions moved users' attitudes on societal questions, which pressures DelayBasin to preserve blank-started or suggestion-scrubbed controls before reading prompt-chip wins as semantics.

- `REF-0705` — Computers in Human Behavior, **The Search Suggestion Effect (SSE): A quantification of how autocomplete search suggestions could be used to impact opinions and votes** (published 2024; accessed 2026-03-22)
  - URL: https://www.sciencedirect.com/science/article/pii/S0747563224002103
  - Load-bearing use: argues that autocomplete suggestions can dramatically shift opinions and voting preferences without leaving an obvious paper trail, which pressures DelayBasin to quarantine broader suggestion-governance stories honestly while importing one compact starter-surface guard.

- `REF-0706` — arXiv, **Audit of Query Bias in Academic Search Engines** (submitted 2023-11-16; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2311.09969
  - Load-bearing use: shows that biased benefits-vs-risks style queries can shift academic search results without changing the underlying topic, which pressures DelayBasin to preserve a query-blanded or slant-scrubbed control before treating research phrasing as evidence.

- `REF-0707` — ACL Anthology / Findings of EMNLP, **The Power of Framing: How News Headlines Guide Search Behavior** (published 2025; accessed 2026-03-22)
  - URL: https://aclanthology.org/2025.findings-emnlp.46/
  - Load-bearing use: shows that headline framing strongly guides later follow-up queries, which pressures DelayBasin to treat query wording itself as an intervention surface rather than a transparent window onto evidence.

- `REF-0708` — SIGWEB / WebSci 2025 proceedings, **Unite or divide? Biased search queries and Google Search results in polarized politics** (published 2025; accessed 2026-03-22)
  - URL: https://www.sigweb.org/toc/websci25a.html
  - Load-bearing use: reports that query slant, rather than user ideology alone, was the primary driver of search-result differences in polarized politics, which pressures DelayBasin to isolate query wording before narrating surfaced evidence as inevitability.

- `REF-0709` — arXiv / CHI 2024, **Dissecting users' needs for search result explanations** (published 2024; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2401.16509
  - Load-bearing use: shows that users do not always seek or understand search explanations, want them mainly for complex or critical tasks, and appreciate the ability to contest results, which pressures DelayBasin to import one bounded explanation-surface guard rather than full explanation governance.

- `REF-0710` — arXiv / ECIR 2026, **Trust Me on This: A User Study of Trustworthiness for RAG Responses** (submitted 2026-01-20; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2601.14460
  - Load-bearing use: shows that explanation types such as source attribution, factual grounding, and information coverage can significantly guide trust toward higher-quality responses, which pressures DelayBasin to treat why-this-result chrome as a live intervention surface rather than neutral wrapper text.

- `REF-0711` — arXiv, **Navigating the Thin Line: Examining User Behavior in Search to Detect Engagement and Backfire Effects** (submitted 2024-01-20; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2401.11201
  - Load-bearing use: shows that stance labels and biased-result presentations can alter clicking diversity, search interactions, and abandonment patterns, which pressures DelayBasin to keep rationale labels visible as potential trust cues rather than harmless annotations.


- `REF-0712` — arXiv / ECIR 2024, **Explaining Search Result Stances to Opinionated People** (submitted 2023-09-15; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2309.08460
  - Load-bearing use: shows that stance labels and their explanations can increase the diversity of search results consumed, which pressures DelayBasin to treat explicit pro/con/neutral overlays as a live intervention surface rather than harmless labeling.

- `REF-0713` — arXiv, **AI summaries in online search influence users' attitudes** (submitted 2025-11-27; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2511.22809
  - Load-bearing use: shows that stance-framed AI summaries can shift issue attitudes and that top-placed summaries produce stronger attitude shifts than middle-placed ones, which pressures DelayBasin to quarantine any broader stance-governance story honestly while importing only one compact stance-overlay guard.


- `REF-0714` — ACM Transactions on Information Systems, **On the Effectiveness of Query-Biased Summaries in Web Search** (published 2003; accessed 2026-03-22)
  - URL: https://dl.acm.org/doi/10.1145/944012.944013
  - Load-bearing use: shows that query-biased summaries influence web-search behavior and effectiveness, which pressures DelayBasin to treat selected excerpts as an intervention surface rather than a transparent window onto the same underlier.

- `REF-0715` — arXiv, **The Impact of Snippet Reliability on Misinformation in Online Health Search** (submitted 2023-11-15; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2311.09969
  - Load-bearing use: shows that many snippets fail to represent their document's viewpoint reliably, which pressures DelayBasin to preserve excerpt-scrubbed or counterspan-included controls before treating highlighted spans as faithful evidence.

- `REF-0716` — TU Delft repository / CHIIR 2023, **Investigating the Influence of Featured Snippets on User Attitudes** (published 2023; accessed 2026-03-22)
  - URL: https://repository.tudelft.nl/record/uuid:8767ea85-bf95-4727-bc67-91dc3579bf4a
  - Load-bearing use: shows that featured snippets can influence users' post-task attitudes and explanations, which pressures DelayBasin to isolate selected-span surfaces before reading the same underlier as semantically decisive.

- `REF-0717` — ACM / CHIIR 2023, **Featured Snippets and their Influence on Users' Credibility Judgements** (published 2023; accessed 2026-03-22)
  - URL: https://doi.org/10.1145/3576840.3578277
  - Load-bearing use: shows that manipulating snippet correctness can change users' credibility judgments, which pressures DelayBasin to treat chosen top excerpts as a live authority surface rather than harmless convenience text.

- `REF-0718` — WebSci 2018 proceedings, **Investigating the Effects of Google's Search Engine Result Page in Evaluating the Credibility of Online News Sources** (published 2018; accessed 2026-03-22)
  - URL: https://emmalurie.github.io/docs/websci18-investigating.pdf
  - Load-bearing use: shows that SERP layout elements such as Knowledge Panels, Top Stories, and source ranking materially shape credibility assessments, which pressures DelayBasin to treat apparent multi-source search support as a live wrapper surface rather than transparent evidence.

- `REF-0719` — Newspaper Research Journal, **News story aggregation and perceived credibility** (published 2021; accessed 2026-03-22)
  - URL: https://doi.org/10.1177/07395329211013488
  - Load-bearing use: suggests that aggregated content becomes more credible when originating sources are identified clearly, which pressures DelayBasin to distinguish real independent support from source-cluster presentation.

- `REF-0720` — Journal of Business Research, **The impact of source-based aggregation on content consumption behaviors** (published 2026; accessed 2026-03-22)
  - URL: https://doi.org/10.1016/j.jbusres.2025.115876
  - Load-bearing use: shows that grouping multiple items from the same source increases source salience while reducing perceived diversity, which pressures DelayBasin to preserve source-cluster controls before reading repeated origin cues as corroboration.

- `REF-0721` — Information Retrieval Journal, **The impact of result diversification on search behaviour and performance** (published 2019; accessed 2026-03-22)
  - URL: https://doi.org/10.1007/s10791-019-09353-0
  - Load-bearing use: shows that diversified results improve aspect coverage and can mitigate search bias, which pressures DelayBasin to keep source diversity visible before treating clustered support as adequate evidence coverage.


- `REF-0722` — Applied Ergonomics, **People also ask: How does this tool affect exploration-exploitation strategies with regard to prior domain knowledge and search context? An eye-tracking study** (published 2024; accessed 2026-03-23)
  - URL: https://doi.org/10.1016/j.apergo.2024.104367
  - Load-bearing use: shows that People Also Ask boxes are processed differently by task and prior knowledge, and that lower-knowledge users attend to them early, which pressures DelayBasin to treat route-shaping result modules as an active control surface rather than neutral search furniture.

- `REF-0723` — ACM TOIS, **Understanding Faceted Search from Data Science and Human Factor Perspectives: A Case Study on Facet Usage and Effectiveness in E-commerce Search** (published 2019; accessed 2026-03-23)
  - URL: https://doi.org/10.1145/3284101
  - Load-bearing use: shows that users interact with facets throughout search and that facet choices measurably structure exploration, which pressures DelayBasin to isolate aspect-route surfaces before reading the resulting evidence path as inevitable.

- `REF-0724` — ACM CHI 2022, **InterWeave: Presenting Search Suggestions in Context Improves Sensemaking** (published 2022; accessed 2026-03-23)
  - URL: https://doi.org/10.1145/3526113.3545696
  - Load-bearing use: shows that weaving search suggestions into the sensemaking workspace changes users' search and sensemaking behavior, which pressures DelayBasin to treat contextual route suggestions as a live intervention surface rather than ambient convenience.


- `REF-0725` — ACM CHIIR 2021, **Cognitive Biases in Search: A Review and Reflection of Cognitive Biases in Information Retrieval** (published 2021; accessed 2026-03-22)
  - URL: https://doi.org/10.1145/3406522.3446023
  - Load-bearing use: explicitly names primacy order effects in search, where users give more weight to information presented earlier in ranked lists, which pressures DelayBasin to preserve an order-balanced or position-scrubbed control before treating top placement as semantic authority.

- `REF-0726` — Journal of the Association for Information Science and Technology, **The effects of credibility cues on the selection of search engine results** (published 2017; accessed 2026-03-22)
  - URL: https://doi.org/10.1002/asi.23820
  - Load-bearing use: confirms the significance of ranking in result selection even when other credibility cues are present, which pressures DelayBasin to isolate raw ordering effects before reading clicks or trust as evidence quality.

- `REF-0727` — ACM TOIS, **Investigating Searchers' Mental Models to Inform Search Explanations** (published 2019; accessed 2026-03-22)
  - URL: https://doi.org/10.1145/3371390
  - Load-bearing use: shows that users have consequential mental models about how search selects and ranks results, which pressures DelayBasin to treat top-slot placement as an active interpretive surface rather than neutral plumbing.

- `REF-0728` — arXiv / CHIIR 2024, **Cognitively Biased Users Interacting with Algorithmically Biased Results in Whole-Session Search on Controversial Topics** (submitted 2024-03-26; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2403.17286
  - Load-bearing use: shows that result presentation and the sequence position of biased SERPs affect search behavior and some users' attitude changes across sessions, which pressures DelayBasin to treat order and slot position as a live intervention surface rather than harmless display order.


- `REF-0729` — arXiv, **Human Trust in AI Search: A Large-Scale Experiment** (submitted 2025-04-08; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2504.06435
  - Load-bearing use: shows that reference links and citations can significantly increase trust in generative AI search even when cited links are wrong or hallucinated, which pressures DelayBasin to treat citation surfaces as an active intervention surface rather than harmless transparency.

- `REF-0730` — arXiv, **The Attribution Crisis in LLM Search Results** (submitted 2025-08-01; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2508.00838
  - Load-bearing use: argues that attribution transparency and which consumed sources are surfaced are engineering choices in LLM search, which pressures DelayBasin to isolate source-link presentation from generic explanation chrome.

- `REF-0731` — arXiv / ECIR 2026, **Trust Me on This: A User Study of Trustworthiness for RAG Responses** (submitted 2026-01-22; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2601.14460
  - Load-bearing use: shows that source attribution can have the strongest positive trust effect among explanation types in factual and technical contexts, which pressures DelayBasin to split citation surfaces from broader why-this-result explanation cues.

- `REF-0732` — arXiv, **Not All Transparency Is Equal: Source Presentation Effects on Attention, Interaction, and Persuasion in Conversational Search** (submitted 2025-12-16; accessed 2026-03-22)
  - URL: https://arxiv.org/abs/2512.12207
  - Load-bearing use: shows that source-presentation format changes attention, interaction, and some persuasion outcomes, which pressures DelayBasin to treat citation badges, reference links, and source cards as a live control surface.


- `REF-0733` — Stanford Cyber Policy Center, **Data Voids and Warning Banners on Google Search** (published 2025-02-25; accessed 2026-03-23)
  - URL: https://cyber.fsi.stanford.edu/publication/data-voids-and-warning-banners-google-search
  - Load-bearing use: shows that Google warning banners were rare, churned over time, and low-quality banners disappeared while average result quality stayed largely unchanged, which pressures DelayBasin to treat warning surfaces as a live intervention surface rather than stable ambient caution.

- `REF-0734` — Scientific Reports / PubMed, **Misinformation does not reduce trust in accurate search results, but warning banners may backfire** (published 2024-05-14; accessed 2026-03-23)
  - URL: https://pubmed.ncbi.nlm.nih.gov/38744967/
  - Load-bearing use: shows that source-reputation warning banners can significantly decrease trust in accurate information, which pressures DelayBasin to preserve warning-hidden or caution-scrubbed controls before reading caution chrome as neutral safety layer.

- `REF-0735` — arXiv / CHI 2025, **Labeling Synthetic Content: User Perceptions of Warning Label Designs for AI-generated Content on Social Media** (submitted 2025-02-14; accessed 2026-03-23)
  - URL: https://arxiv.org/abs/2503.05711
  - Load-bearing use: shows that the presence and design of warning labels materially change user beliefs and trust in the label itself, which pressures DelayBasin to treat warning-banner form as a live design lever rather than a transparent note.
