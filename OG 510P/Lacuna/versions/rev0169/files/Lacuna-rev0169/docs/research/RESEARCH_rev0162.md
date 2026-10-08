# Research — rev0162

## Question 1: is this a useful gift to Gwern?

Yes, if the gift is framed as a falsifiable instrument rather than a flattering implementation of the thesis.

The central value of Lacuna is not that it can produce a clever retrospective explanation. A large prompt can already attempt that. The useful claim is narrower: explicit custody of unknowns, candidate worlds, commitments, consequences, role-separated comparison, and bounded compression may reduce rubber reality and seam visibility without sacrificing agency or costing more than it helps.

A serious instrument must be able to report that this claim is wrong. The four conditions do that:

- `forward-only` tests continuation without retrospective hidden-state revision;
- `prompt-only-retcon` tests the general retcon idea without Lacuna's machinery;
- `lacuna-serial` tests the structured protocol in one context; and
- `lacuna-role-separated` tests whether manufactured context boundaries add value.

Rev0161 made one block runnable. Rev0162 targets the next real objection: an experiment owner could otherwise decide which stories to run, create later assignments after seeing earlier outcomes, stop after a pleasing block, unblind early, or report only successful cells. A bundle fixes every child and assignment up front, executes in one private order, includes terminal failures, and withholds every mapping until all blocks are sealed.

That directly addresses concerns implicit in retcon arguments:

- **cheap commitment:** the hidden explanation or experiment design can move after evidence;
- **rubber reality:** later needs make earlier details suspiciously convenient;
- **selection overfitting:** search chooses a satisfying payoff but hides discarded failures;
- **path dependence:** early outcomes influence later search and reporting;
- **cost without benefit:** extra roles and tools may add latency/cost but no visible gain; and
- **unfalsifiable demonstrations:** one curated success is offered as mechanism evidence.

The external commitment/witness gate is especially Gwern-relevant. It applies anti-retcon custody to the evaluation itself. An independent holder can retain the exact preregistration and hidden-assignment commitments before execution. This still cannot prove that no earlier unwitnessed bundle was discarded, but it makes the surviving study harder to rewrite after seeing results.

The strongest gift package would therefore contain the software, a very short reproducible protocol, several preregistered blocks, exact retained failures, blind rater-level data, and a result that is publishable even when Lacuna loses.

## Question 2: can a 20-year-old player just ask ChatGPT to DM?

Yes. The player entrance should remain this simple:

> Will you DM?

An ordinary ChatGPT conversation can immediately interpret that as a request to run a role-playing scene, ask only the minimum fiction-setting questions when needed, preserve player agency, and begin. The player does not need to know about cubes, checkpoints, assignments, raters, subagents, or a CLI.

There are three honest operating levels:

### Chat-only play

ChatGPT can DM in the current conversation. It should treat session-control language as session control, not fictional dialogue, and state once that the campaign is not durably committed to a Lacuna cube. The conversation itself is the memory boundary.

### Human bridge

A person runs `lacuna play start`, copies the emitted complete handoff into ChatGPT, saves the one JSON return, and runs the exact printed accept/commit command. This gives durable cube custody without requiring ChatGPT to have a shell or custom integration.

### Connected host

A ChatGPT Project, Action/App/MCP-like adapter, Codex workspace, or other tool-capable parent can call the narrow Lacuna commands itself. The parent follows `NEXT.md`, delegates only complete cards, and presents narration only from an accepted receipt.

The important design rule is that the model should never have to infer the whole workflow. The cube compiles the next local context and says:

- who owns the next step;
- what exact artifact is input;
- what schema must be returned;
- whether the handoff is blind;
- what the worker may not do; and
- what exact command the parent runs next.

That is why a less capable model can still operate Lacuna. It can “jump in” at the player surface, while a durable host can guide it one bounded transition at a time backstage.

A scenario bundle is not part of this play path. It is how an experiment owner compares ways of DMing. Keeping it separate protects both usability and blinding.

## Question 3: how should different frontier LLM configurations enter?

The stable object should be the semantic handoff, not vendor syntax. Provider-specific configuration maps one complete Lacuna role card to the available product surface.

### Codex or another shell-capable coding agent

Use one parent workspace with filesystem/CLI authority. The parent reads only the current pointer, invokes Lacuna, starts fresh subagents for role-separated work when available, and records their exact returns. Workers receive no commit or unblind authority.

### Claude Code or Gemini-oriented coding agents

Use the same parent/worker split. Native subagents or delegated tasks are convenient, but the exact Lacuna dispatch remains the source of role, input, forbidden context, and return schema. If the product cannot provide clean contexts, declare the downgrade and use the serial treatment rather than pretending separation.

### ChatGPT with connected tools

The parent can call narrow commands and use separate chats, tasks, or subagent-like contexts where the product exposes them. Ordinary ChatGPT without those tools uses a human bridge. The game still starts from the one sentence.

### API or custom host

Create a fresh provider context for each declared role, preserve request/response IDs where available, and return one exact object. The bundle rejects declared context or invocation-ID reuse across blocks, while recognizing that strings alone do not prove real isolation.

### A model that is less inferentially capable

Do not give it the repository and ask it to “run the experiment.” Give it exactly the emitted current dispatch. The handoff should be self-contained, redundant at the authority boundary, and explicit about output shape. The parent—not the worker—handles filesystem state, recovery, acceptance, sealing, and unblinding.

## Can the cube make a frontier model use subagents correctly?

It can make the desired action much more likely and make contradictory declarations detectable.

The cube can emit an instruction such as:

```text
You are the parent coordinator. Do not solve this role yourself.
Create one fresh worker context for the named role.
Give it exactly input_document and no private sibling artifacts.
Require exactly one JSON object matching expected_return_schema.
Do not let the worker run accept, commit, seal, recover, or unblind.
Record the provider context and invocation identifiers honestly.
Return authority to the parent after the object is saved.
```

It can then bind the worker's declared role, context, invocation, input digest, output digest, ordering, and parent command. It can refuse reuse or a topology that contradicts the treatment.

It cannot force a product to instantiate a genuine subagent, erase shared memory, hide provider system prompts, prevent collusion through tools, or prove that two context IDs represent independent cognition. Subagent separation is therefore both an operational technique and an experimental variable.

## Why two agents may matter

Two agents are valuable only when they hold different information or authority. Merely asking the same context twice can add samples without reducing bias.

For retcon planning, useful separations are:

- generator sees the source-bound problem but not provenance-sensitive judgment;
- judge sees candidate content but not authorship or privileged rationale;
- compressor sees only the selected candidate and a least-authority state-update contract;
- verifier checks the proposed update without participating in composition; and
- parent alone can accept, commit, seal, recover, or unblind.

The `lacuna-serial` versus `lacuna-role-separated` contrast asks whether these manufactured boundaries matter beyond schemas and fixed workflow. A replicated bundle makes that contrast observable across stories and models.

## Datacube as an exact context walk

The datacube can be understood as an executable curriculum over a large hidden state space:

```text
verified world boundary
  -> one source-bound request
  -> one complete role card
  -> one schema-conforming return
  -> one audited transition
  -> one newly compiled local context
  -> ...
  -> blind packet
  -> fixed ratings
  -> sealed block
  -> all-block report
```

A model never needs the whole cube in one context. Repeated CLI invocations can reveal exactly the cells, projections, cards, and authority boundaries required for the current step. That is useful not only for fiction but for science, where private hypotheses, blinded critique, minimal state updates, and public reporting should remain distinct.

## Scientific configuration

A scientific adaptation could map the same roles to:

- hypothesis generator;
- provenance-blind evaluator;
- selected-hypothesis compressor into a typed research state;
- independent method/data verifier; and
- public-report compiler.

A bundle could preregister datasets/tasks, model/tool strata, role topology, failure inclusion, and primary endpoints. It would not make the resulting science true. It would make proposal, selection, update, and reporting custody more inspectable and give negative results somewhere durable to live.

The strongest next scientific work is not a more autonomous agent. It is external provider attestations where available, contamination canaries, masking checks, rater disagreement, a declared analysis plan, and public redaction that preserves verification without releasing private candidate hypotheses.

## What rev0162 still does not answer

- Whether Lacuna actually scores better across a representative task population.
- How many blocks or raters are adequately powered.
- Which ordinal/statistical model should be primary.
- Whether native subagents are genuinely more independent than separate API contexts.
- Whether structured blinding survives semantic style leakage.
- Whether extra governance is worth its latency and operator cost.
- Whether a witness service's claims are valid.

Those are now experiment questions rather than reasons the instrument cannot be run.

## Recommended evaluation sequence

1. Choose multiple seeds and off-script actions before execution.
2. Fix one comparable rating contract and explicit model/story strata.
3. Build and inspect one complete bundle plan.
4. Publish every child and assignment.
5. Retain the commitment externally before execution.
6. Operate blocks only through the current pointer and preserve failures.
7. Seal every fully rated block without unblinding.
8. Unblind all at once and export rater-level JSON.
9. Analyze under a separately declared ordinal/hierarchical model.
10. Publish the null or negative result with the same care as a win.

That sequence is the clearest current answer to the three serious questions: the gift targets real objections, the player can still start with one sentence, and heterogeneous frontier models receive a hyperlegible exact walk rather than a request to intuit the whole system.
