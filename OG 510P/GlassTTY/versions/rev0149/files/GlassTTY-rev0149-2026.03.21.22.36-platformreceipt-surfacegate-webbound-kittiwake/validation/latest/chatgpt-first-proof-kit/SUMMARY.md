# ChatGPT first proof kit

- generated_at: `2026-03-21T22:05:01Z`
- primary route hint: `https://help.openai.com/en/articles/9125172-the-chatgpt-home-page`
- probe prompt: `Reply with exactly this text and nothing else: GLASSTTY-CHECKPOINT`
- candidate bundle path: `docs/support-bundles/candidate/chatgpt-routefirst-chromium-live-candidate.json`

## Priority rules

- Prefer route-first proof on chatgpt.com before Projects, Canvas, GPT builder, or other richer workspaces.
- Prefer user-facing, accessible locators and main-region scoping before CSS or DOM-shape fallbacks.
- Preserve one failed candidate and one successful candidate for the composer and submit affordance so drift is reviewable.
- Treat submit proof, generation proof, and latest-turn proof as separate evidence moments even when one run provides all three.
- Require a composer witness receipt before submit proof so a merely discovered textbox cannot masquerade as a proved write path.
- Require a submit witness receipt before treating submit, generation, or latest-turn extraction as a proved workflow slice.
- Require a proof-bundle receipt before claiming a whole proof window is fit for held-bundle promotion.
- Require a promotion-stability receipt before using repeated proof windows to strengthen ChatGPT support language beyond one held bundle.
- Require a support-claim receipt before phrasing support language so repeated Chromium proof does not silently imply broader browser or workspace coverage.
- Require a capability-profile receipt before phrasing support language so a plain text-only baseline does not silently imply Search, uploads, data analysis, voice, image, or other tool modes.
- Require an auth-workspace receipt before phrasing support language so guest, personal, Business, Enterprise, or Edu session stories do not silently blur together.
- Require a plan-envelope receipt before phrasing support language so guest, Free, Plus, Pro, Business, Enterprise, or Edu subscription stories do not silently blur together.
- Require a browser-envelope receipt before phrasing support language so one explicit Chromium lane does not silently become broader browser support.
- Require a retention-envelope receipt before phrasing support language so standard saved-history chats, Temporary Chats, memory-off runs, and reused storage-state sessions do not silently blur together.
- Require a platform-envelope receipt before phrasing support language so desktop web proof does not silently become Windows app, macOS app, iOS, Android, or mobile-web support.

## UI branching hazards

- logged-out single-thread posture: The current home-page article says logged-out use is available at chatgpt.com but limits you to one conversation and cannot preserve history after logout.
- projects require login and introduce a richer workspace shell: Projects are a logged-in workspace with chats, files, instructions, and sharing, so they should stay out of the first generic chat-lane proof.
- canvas can open from prompts, slash command, composer toolbox, or longer generated content: Canvas is useful but it changes the UI shape and should be treated as a branch, not the baseline lane.
- web-only composer controls can appear for selected models: The web composer can expose model and thinking-time controls, so selector scope should stay anchored to the active composer rather than assume a fixed button neighborhood.
- built-in tools can change the same route without changing the host: Search, uploads, data analysis, images, voice, and other tools can all live on the same ChatGPT surface, so the first proof should preserve a capability profile instead of silently treating one text-only pass as tool-general support.
