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
