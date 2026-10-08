# Research notes — 2026-03-21

## Current source-anchor findings

- Grok now has a direct first-party web surface at `https://grok.com/`, which is a tighter product anchor for the browser surface than the broader xAI corporate home.
- Kimi now has a direct first-party web/product surface at `https://www.kimi.com/`, which is tighter than relying on the broader Moonshot corporate home.
- Z.ai currently exposes a direct browser/product route at `https://z.ai/chat`, which is a better chat-surface anchor than older `chat.z.ai` assumptions.
- ChatGPT still has a stable first-party product overview, and OpenAI's current help surfaces now also give useful direct browser-route and feature-mode anchors for home route, capabilities, canvas, file uploads, projects, search, and GPT builder.
- Claude and Google AI Studio still have stable first-party product surfaces appropriate for source-lock authority.

## Product consequence

The approved-source lock should not only pin authority classes; it should also admit that source authority decays. A named source with no freshness budget eventually becomes another hidden assumption.

## Implementation consequence

rev0132 added review-age policy and stale-review detection so the repo can distinguish:

1. approved source exists
2. bundle cites that approved source
3. approved source review is still current enough for stronger publication language

rev0134 extends that idea for ChatGPT specifically: the repo now distinguishes the plain browser route from richer mode branches and names current first-party help anchors for those branches.

## Second-adapter research notes

- ChatGPT's current overview surface still presents a broad browser-native workflow with typing, search, canvas, file analysis, image conversation, and a direct try path.
- OpenAI's current ChatGPT home-page help article anchors the plain browser route at `chatgpt.com`, which is a better first baseline target than jumping straight into richer modes.
- OpenAI's current capabilities, canvas, file-upload, and projects help surfaces make the mode branching risk more concrete: ChatGPT is strategically the best second adapter, but the first proof should stay on the generic chat lane rather than trying to prove every feature mode at once.
- Google AI Studio remains a direct signed-in browser surface, but its official framing is still more developer/workspace-centric: Gemini API entry, prompt gallery, API key, and “Try it out” flows.
- Kimi's current web surface exposes a much richer workspace from the first screen (`Websites`, `Docs`, `Slides`, `Sheets`, `Deep Research`, `Agent Swarm Beta`), which is strategically attractive but likely more complex for the very next adapter than a general chat lane.
- Z.ai's current web/chat surface exposes `Chat`, `API`, and product/agent navigation, suggesting a plausible general browser lane but not an obviously stronger second-adapter case than ChatGPT.
- xAI and Grok's official surfaces now clearly establish Grok on the web, but Grok's product velocity and broader search/X posture still look riskier for the first post-Claude proof than ChatGPT.
- Playwright's current best-practices and locator docs continue to support accessible, user-facing locators over brittle DOM structure, which fits the repo's current ChatGPT selector discipline.

## Decision consequence

The repo should stop treating the second-adapter choice as merely a recommendation buried in prose. The current best explicit choice remains ChatGPT, with AI Studio as the next-wave follow-on once the generic second-adapter proof lands.

The repo should also stop treating “do the ChatGPT baseline” as one vague sentence. rev0134 turns it into a named execution brief with ordered phases, artifact targets, selector principles, and promotion criteria. rev0136 adds a posture matrix so future runs can classify whether the landed shell is still baseline-safe or has drifted into a richer branch before attempting proof actions.

## Additional ChatGPT execution findings

- OpenAI's current ChatGPT search help article says ChatGPT search is available at `chatgpt.com` and can also be available to logged-out users; that means search can appear inside the normal home lane and should be recorded as a caution variant rather than being mistaken for a different route.
- OpenAI's current GPT builder help article says GPT creation/editing is a web-only workspace reached from the GPTs area or `https://chatgpt.com/gpts`; that makes the builder a distinct branch shell instead of part of the first generic chat-lane proof.
- OpenAI's current ChatGPT home-page article explicitly says ChatGPT can be accessed before creating an account at `chatgpt.com`, that you can simply enter a prompt in the text box to get started, and that logged-out use is limited to one conversation at a time.
- OpenAI's current Projects help article says Projects are logged-in workspaces that group chats, files, and instructions, so they should stay out of the first generic route-first proof.
- OpenAI's current Canvas help article says Canvas can open automatically for larger writing/coding responses, from `use canvas` prompts, from a blank-canvas request, from a composer shortcut, or via `/canvas`; that confirms Canvas is a mode-branching hazard for selector work rather than part of the first baseline.
- OpenAI's current GPT-5.3/GPT-5.4-in-ChatGPT help article says the web composer can show a thinking-time toggle for GPT-5.4 Thinking and that the most recent response exposes retry or branch actions; that makes it important to anchor selectors to the active composer and main conversation region rather than a fixed local button cluster.

## Implementation consequence after rev0135

The repo should stop treating the first ChatGPT proof as only an ordered checklist. It now has enough current first-party product detail to freeze:

1. a selector contract
2. a low-ambiguity benign probe
3. a branch-hazard inventory
4. a failure taxonomy
5. a candidate support bundle manifest

That combination is a better bridge between “we studied the product” and “we can now run a disciplined first proof.”

## Additional route-witness findings after rev0136

- OpenAI's current chat-history search help article makes it clear that authenticated users can search prior chats from the sidebar, so that cue should stay separate from web-search-in-the-main-lane during the first ChatGPT baseline.
- Playwright's current best-practices guidance keeps reinforcing user-facing locators over brittle DOM shape, which supports storing route/title/text witnesses instead of trying to classify the shell from CSS details.
- Playwright's current actionability guidance reinforces that visibility, enabledness, and editability checks should stay separate from route classification; the branch guard should decide whether to proceed before the proof kit spends time on composer actionability.

## Implementation consequence after rev0137

The repo now has enough current product and tooling detail to separate three decisions that were previously too entangled:

1. what posture family the landed shell seems to be in
2. whether the concrete witness is strong enough to continue, continue-with-caution, or stop
3. whether the chosen composer/submit candidate is actionable once the shell is accepted

That is a more durable boundary between route truth, branch truth, and actionability truth than rev0136 alone.

## Additional bundle-promotion findings after rev0141

- OpenAI's current home-page guidance still makes the plain route, prompt box, and single logged-out conversation the cleanest baseline, which keeps bundle promotion anchored to one minimal lane rather than a richer workspace.
- OpenAI's current Projects, Canvas, GPT builder, and search docs keep reinforcing that several distinct branches can still appear inside ChatGPT's product family; that makes one whole proof-window receipt more honest than pretending separate step receipts automatically imply one coherent baseline run.
- Playwright's current best-practices, actionability, input, and assertion guidance still favors user-visible locators, actionability-aware interactions, and durable readback checks, which supports preserving screenshot, receiver posture, submit evidence, and latest-turn artifacts together when a bundle is promoted.

## Implementation consequence after rev0141

The repo now has enough current product and tooling detail to separate five decisions that were previously too easy to blur:

1. what posture family the landed shell seems to be in
2. whether the route witness is strong enough to continue honestly
3. whether the composer witness proves a writable prompt lane
4. whether the submit/result witness proves a completed turn with stable latest-turn readback
5. whether one whole proof window is coherent enough to attach to a stronger held bundle without overclaiming from isolated receipts


## Additional repeatability findings after rev0142

- OpenAI's current home-page and feature docs keep reinforcing that ChatGPT can present meaningfully different shells across logged-out home, search-capable home, Projects, Canvas, and GPT-builder branches, so a single clean proof window should not be mistaken for stable surface-wide support.
- Playwright's current best-practices, locators, and assertions guidance keeps emphasizing resilient user-facing locators, codegen-assisted locator review, and web-first assertions, which supports preserving locator strategy and stable exact readback across repeated proof windows rather than only preserving one pass.
- Playwright's current debugging and trace guidance also supports keeping replay materials with repeated windows so later drift review can distinguish a resilient lane from a one-off lucky interaction.

## Implementation consequence after rev0142

The repo now has enough current product and tooling detail to separate six decisions that were previously too easy to blur:

1. what posture family the landed shell seems to be in
2. whether the route witness is strong enough to continue honestly
3. whether the composer witness proves a writable prompt lane
4. whether the submit/result witness proves a completed turn with stable latest-turn readback
5. whether one whole proof window is coherent enough to attach to a stronger held bundle without overclaiming from isolated receipts
6. whether repeated proof windows are stable enough to strengthen ChatGPT support language beyond one held bundle

## Browser-envelope grounding

- OpenAI's current ChatGPT troubleshooting guidance says browser extensions, cache/cookies, private windows, VPNs, and trying a different browser can all materially change whether ChatGPT behaves cleanly, so a single captured browser lane should not silently become cross-browser support.
- Playwright's current browser and projects docs keep reinforcing that Chromium, Firefox, WebKit, and branded-browser configurations are separate project targets, which makes browser/project scope a real support boundary instead of just metadata.
