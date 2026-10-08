# Official voter-information post-submit redirect surface checklist

Use this checklist when an election office operates **public submit routes whose next browser-visible state may depend on redirects, refresh behavior, or generic repost prompts**.

## Scope and route classification review

- [ ] Record which public submit routes can end in a confirmation page, a status page, a same-document durable result state, or a residual browser repost-risk state.
- [ ] Distinguish this surface from general confirmation-copy review, local-versus-office state truthfulness, same-document history mutation, or leave-page warning posture.
- [ ] Keep cross-origin or third-party handoffs bounded separately from same-origin post-submit browser-state review.

## Redirect and method-semantics review

- [ ] Review whether routes that promise a confirmation or status page actually land on a refresh-safe retrieval destination.
- [ ] Review redirect semantics after submit explicitly; do not treat `302`, `303`, `307`, and `308` as interchangeable when public retry/reload safety is at stake.
- [ ] Review whether long-running actions redirect to a truthful status/help page rather than leaving the voter on a fragile residual submit shell.
- [ ] Do not quietly rely on browser-dependent redirect behavior to decide whether ordinary refresh will replay the original submit.

## Confirmation / retry safety review

- [ ] Review whether the voter can tell if refreshing the visible next page is safe, duplicative, or uncertain.
- [ ] Keep already-received, safe-to-retry, duplicate-risk, and unknown-outcome states visibly distinct.
- [ ] Keep a bounded confirmation/status/help recovery path when replay safety cannot be guaranteed.
- [ ] Do not let a durable-looking success block on the same document masquerade as a refresh-safe confirmation state if reload still risks replay.

## Browser repost-prompt humility review

- [ ] Treat any generic browser repost or resubmit prompt as residual browser behavior, not as the office’s confirmation surface.
- [ ] Do not describe a browser repost prompt as proof that the office received the request.
- [ ] Do not describe a browser repost prompt as duplicate protection, safe retry guidance, or a reliable keep-a-record artifact.
- [ ] Review revisit paths such as refresh, Back/Forward, reopen, and copied revisit links for residual repost ambiguity.

## Evidence and minimization review

- [ ] Preserve a small public digest of reviewed routes, post-submit destination classes, refresh-safe posture, duplicate-risk posture, and last review time.
- [ ] Do not preserve raw request bodies, individualized retry histories, or full access logs merely to prove that post-submit redirect posture was reviewed.
